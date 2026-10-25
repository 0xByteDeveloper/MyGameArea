// ============================================================================
//  MaxExecutor.cpp — Metin2 Ana-Thread Güvenli Python Executor  (v1.1)
// ============================================================================
//  v1.1 DUZELTMELER (konsol bos / yazi yok sorunu):
//    FIX-1: GUI surecinde CRT stdout tablosu gecersiz handle ile baslar;
//           AllocConsole() sonrasi freopen(CONIN$/CONOUT$) ile CRT yeniden
//           baglanmaliydi — eksikti. Bu yuzden printf cikisi gorunmuyordu.
//    FIX-2: setvbuf(_IONBF) — cikis buffer'siz, crash olsa bile yazar.
//    FIX-3: Konsol kurulumu DllMain'den worker thread'e tasindi
//           (loader-lock hijyeni; AllocConsole DllMain icinde riskli).
//    FIX-4: Konsol penceresi HWND_TOPMOST yapildi (oyun arkasinda kalmaz).
//    FIX-5: Otomatik dreneaj thread'i (2 sn): konsol olmasa bile kuyruk
//           islenir — .cmd dosyasini elle birak, 2 sn icinde calisir.
//    FIX-6: Her adim maxexec.log'a yaziliyor (konsolsuz debug kanali).
//  v1.2 DUZELTMELER (kuyruk yaziliyor ama hicbir sey calismiyor sorunu):
//    FIX-8:  SetTimer TABANLI DRENAJ — TimerProc oyunun kendi mesaj pompasinda
//            ana thread'de calisir; WndProc subclass'a HICBIR bagimlilik yok.
//            Subclass geri alinirsa/emilirse bile kuyruk islenir.
//    FIX-9:  SAYACLAR + alive.txt zenginlesti:
//            tick=<ms> drain=<n> exec=<n> timer=<n> msg=<n> py=<0/1>
//            tek dosya okumasi tum zincirin nerede kirildigini soyler.
//    FIX-10: PROBE — python27 bulununca kuyruga otomatik probe komutu konur;
//            results\py_probe.txt olusursa zincir UST-UCE KANITLANMIS olur.
//    FIX-11: Py_IsInitialized artik loglanir.
//    FIX-12: basedir.txt destegi (C:\MaxExec\basedir.txt icine "D:\MaxExec"
//            yazarsan tum dosyalar oraya tasinir; C:\ sorunu yasayanlar icin).
//    FIX-13: 30 sn'de bir maxexec.log'a sayaç ozeti yazilir.
// ============================================================================
//  xgodmod4 gereksinimleri:
//    * Python fonksiyon hook'u  YOK  (monkey-patch yok)
//    * Shared memory            YOK  (dosya kuyrugu kullanir)
//    * Oyun ana thread'ini siken desen YOK (arka plan PyRun yok)
//
//  MIMARI:
//    - DLL yuklenince oyunun ana gorunur penceresini bulunur ve WndProc'u
//      subclass edilir (SetWindowLongPtr / GWLP_WNDPROC).
//    - Konsol (worker thread) komutlari DOSYA kuyruguna yazar:
//          C:\MaxExec\queue\*.cmd   (atomik: .tmp yaz -> MoveFile)
//      ve ana thread'e PostMessage(WM_APP_MAXEXEC) atar. Worker thread
//      HICBIR ZAMAN Python C-API cagirmaz.
//    - WndProc OYUNUN ANA THREAD'INDE calisir. Metin2 client ana thread'de
//      Python'u calistirir ve GIL'i birakmaz; dolayisiyla WndProc icinden
//      yapilan PyRun_SimpleString cagrisi GIL zaten bizim elimizde oldugu
//      icin dogal olarak guvenlidir (yaris yok, deadlock yok).
//    - Her drain sonunda C:\MaxExec\alive.txt heartbeati yazilir; `status`
//      komutu bu dosyanin yasiyla ana-thread sagligini raporlar.
//
//  DERLEME: Visual Studio, x86 (metin2client 32bit ise), DLL projesi.
//           Ek baglama gereksinimi: user32.lib (varsayilan acik).
//
//  KULLANIM (oyun ici konsol):
//    help | status | load <py-dosya> | login <id> <pwd> | charlist
//    empire <1-3> | create <slot> <ad> <race> <shape> | enter <slot>
//    raw <python kodu> | waitfor <SceneAdi> <saniye> | log | exit
//
//  Python tarafini bir kez yukleyin:
//    load C:\MaxExec\pylib.py
// ============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <stdio.h>
#include <stdarg.h>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// Sabitler
// ---------------------------------------------------------------------------
static const UINT    WM_APP_MAXEXEC   = WM_APP + 0x7A1;   // 0x87A1
static const UINT_PTR TIMER_ID_MAXEXEC = 0x7A1;          // SetTimer kimligi
// v1.2: yollar artik calisma-zamani — basedir.txt ile tasinabilir (FIX-12)
static char BASE_DIR[MAX_PATH]   = "C:\\MaxExec";
static char QUEUE_DIR[MAX_PATH]  = "C:\\MaxExec\\queue";
static char RESULT_DIR[MAX_PATH] = "C:\\MaxExec\\results";
static char ALIVE_FILE[MAX_PATH] = "C:\\MaxExec\\alive.txt";
static char EXEC_LOG[MAX_PATH]   = "C:\\MaxExec\\maxexec.log";
static char PYERR_LOG[MAX_PATH]  = "C:\\MaxExec\\pyerr.log";
static const int     MAX_CMDS_PER_DRAIN = 4;              // tek mesajda maks. komut (render'i sisirmemek icin)

// ---------------------------------------------------------------------------
// Python27 sembolleri (yalniz ANA THREAD'den kullanilir!)
// ---------------------------------------------------------------------------
typedef int  (*PFN_PyRun_SimpleString)(const char*);
typedef int  (*PFN_PyIsInitialized)(void);

static PFN_PyRun_SimpleString  pfn_PyRun_SimpleString = 0;
static PFN_PyIsInitialized     pfn_PyIsInitialized    = 0;
static HMODULE                 hPython27              = 0;

static bool ResolvePython(void)
{
    if (pfn_PyRun_SimpleString) return true;
    hPython27 = GetModuleHandleA("python27.dll");
    if (!hPython27) return false;
    pfn_PyRun_SimpleString = (PFN_PyRun_SimpleString)GetProcAddress(hPython27, "PyRun_SimpleString");
    pfn_PyIsInitialized    = (PFN_PyIsInitialized)GetProcAddress(hPython27, "Py_IsInitialized");
    return (pfn_PyRun_SimpleString != 0);
}

// ---------------------------------------------------------------------------
// Kucuk yardimcilar (dosya)
// ---------------------------------------------------------------------------
static void MkDirp(const char* path) { CreateDirectoryA(path, NULL); }
static void EnsureDirs(void);   // fwd decl: WorkerThread kullanir, tanim DllMain bolgesinde

static void LogLine(const char* fmt, ...)
{
    SYSTEMTIME st; GetLocalTime(&st);
    FILE* f = fopen(EXEC_LOG, "a");
    if (!f) return;
    fprintf(f, "[%02d:%02d:%02d] ", st.wHour, st.wMinute, st.wSecond);
    va_list ap; va_start(ap, fmt);
    vfprintf(f, fmt, ap);
    va_end(ap);
    fprintf(f, "\n");
    fclose(f);
}

static bool ReadFileAll(const std::string& path, std::string& out)
{
    HANDLE h = CreateFileA(path.c_str(), GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return false;
    DWORD size = GetFileSize(h, NULL);
    out.resize(size);
    DWORD rd = 0;
    ReadFile(h, &out[0], size, &rd, NULL);
    CloseHandle(h);
    return true;
}

static bool WriteFileAll(const std::string& path, const std::string& data)
{
    HANDLE h = CreateFileA(path.c_str(), GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL);
    if (h == INVALID_HANDLE_VALUE) return false;
    DWORD wr = 0;
    WriteFile(h, data.c_str(), (DWORD)data.size(), &wr, NULL);
    CloseHandle(h);
    return true;
}

// Kuyruga atomik komut yazimi: once .tmp, sonra MoveFile -> .cmd
static bool EnqueueCommand(const std::string& code, std::string& outFile)
{
    static unsigned seq = 0;
    ++seq;
    char tmp[MAX_PATH], fin[MAX_PATH];
    sprintf(tmp, "%s\\c_%lu_%04lu.tmp", QUEUE_DIR, (unsigned long)GetTickCount(), (unsigned long)seq);
    sprintf(fin, "%s\\c_%lu_%04lu.cmd", QUEUE_DIR, (unsigned long)GetTickCount(), (unsigned long)seq);
    if (!WriteFileAll(tmp, code)) return false;
    if (!MoveFileA(tmp, fin)) { DeleteFileA(tmp); return false; }
    outFile = fin;
    return true;
}

// ---------------------------------------------------------------------------
// WndProc subclass — ANA THREAD'de calisir
// ---------------------------------------------------------------------------
static WNDPROC g_oldWndProc = 0;
static HWND    g_hGameWnd   = 0;

// ---------------------------------------------------------------------------
// Sayaclar (FIX-9) — zincirin nerede kirildigini tek bakista soyler
// ---------------------------------------------------------------------------
static volatile LONG g_nMsg = 0;     // WndProc'un aldigi WM_APP_MAXEXEC sayisi
static volatile LONG g_nTimer = 0;   // TimerProc cagrilari (oyun pompasi kaniti)
static volatile LONG g_nDrain = 0;   // DrainQueue cagrilari
static volatile LONG g_nExec = 0;    // gercekten PyRun edilen komutlar

static void InitPaths(void)
{
    // FIX-12: C:\MaxExec\basedir.txt ilk satiri = yeni ana klasor (orn: D:\MaxExec)
    std::string bd;
    if (ReadFileAll("C:\\MaxExec\\basedir.txt", bd))
    {
        while (!bd.empty() && (bd[bd.size()-1]=='\n' || bd[bd.size()-1]=='\r' || bd[bd.size()-1]==' ' || bd[bd.size()-1]=='\t'))
            bd.erase(bd.size()-1);
        if (bd.size() >= 3 && bd[1]==':' && (bd[2]=='\\' || bd[2]=='/'))
        {
            for (size_t i = 0; i < bd.size(); ++i) if (bd[i] == '/') bd[i] = '\\';
            _snprintf(BASE_DIR, MAX_PATH, "%s", bd.c_str());
            BASE_DIR[MAX_PATH-1] = 0;
        }
    }
    _snprintf(QUEUE_DIR,  MAX_PATH, "%s\\queue",     BASE_DIR);  QUEUE_DIR[MAX_PATH-1]=0;
    _snprintf(RESULT_DIR, MAX_PATH, "%s\\results",   BASE_DIR);  RESULT_DIR[MAX_PATH-1]=0;
    _snprintf(ALIVE_FILE, MAX_PATH, "%s\\alive.txt", BASE_DIR);  ALIVE_FILE[MAX_PATH-1]=0;
    _snprintf(EXEC_LOG,   MAX_PATH, "%s\\maxexec.log", BASE_DIR); EXEC_LOG[MAX_PATH-1]=0;
    _snprintf(PYERR_LOG,  MAX_PATH, "%s\\pyerr.log",  BASE_DIR);  PYERR_LOG[MAX_PATH-1]=0;
}

static void Heartbeat(void)
{
    char buf[160];
    sprintf(buf, "tick=%lu drain=%ld exec=%ld timer=%ld msg=%ld py=%d",
            (unsigned long)GetTickCount(),
            (long)g_nDrain, (long)g_nExec, (long)g_nTimer, (long)g_nMsg,
            pfn_PyRun_SimpleString ? 1 : 0);
    WriteFileAll(ALIVE_FILE, buf);
}

static void DrainQueue(void)
{
    InterlockedIncrement(&g_nDrain);
    if (!pfn_PyRun_SimpleString) { Heartbeat(); return; }  // python27 yoksa da nabiz yaz

    WIN32_FIND_DATAA fd;
    char pattern[MAX_PATH];
    sprintf(pattern, "%s\\*.cmd", QUEUE_DIR);
    HANDLE h = FindFirstFileA(pattern, &fd);
    if (h == INVALID_HANDLE_VALUE) { Heartbeat(); return; }

    int done = 0;
    do
    {
        if (done >= MAX_CMDS_PER_DRAIN)
        {
            // Kalan komutlar var -> yeniden tetikle (render'a nefes payi)
            FindClose(h);
            PostMessage(g_hGameWnd, WM_APP_MAXEXEC, 0, 0);
            return;
        }
        std::string full = std::string(QUEUE_DIR) + "\\" + fd.cFileName;
        std::string code;
        if (ReadFileAll(full, code))
        {
            LogLine("EXEC %s (%u byte)", fd.cFileName, (unsigned)code.size());
            // >>> ANA THREAD'DE PYTHON CALISTIRMA (GIL zaten ana thread'de) <<<
            pfn_PyRun_SimpleString(code.c_str());
            InterlockedIncrement(&g_nExec);
            ++done;
        }
        DeleteFileA(full.c_str());
    } while (FindNextFileA(h, &fd));
    FindClose(h);

    Heartbeat();
}

static LRESULT CALLBACK MaxExecWndProc(HWND hwnd, UINT msg, WPARAM wp, LPARAM lp)
{
    if (msg == WM_APP_MAXEXEC)
    {
        InterlockedIncrement(&g_nMsg);
        DrainQueue();
        return 0;
    }
    return CallWindowProc(g_oldWndProc, hwnd, msg, wp, lp);
}

// ---------------------------------------------------------------------------
// TIMER YOLU (FIX-8) — WM_TIMER oyunun kendi mesaj pompasiyla TimerProc'a
// ulasir; WndProc subclass'i geri alinsa bile CALISIR. Ana thread garanti
// (pencerenin sahibi thread = oyun ana thread'i).
// ---------------------------------------------------------------------------
static VOID CALLBACK MaxExecTimerProc(HWND hwnd, UINT, UINT_PTR, DWORD)
{
    InterlockedIncrement(&g_nTimer);
    DrainQueue();
}

static void InstallTimer(void)
{
    if (!g_hGameWnd) return;
    UINT_PTR id = SetTimer(g_hGameWnd, TIMER_ID_MAXEXEC, 1500, MaxExecTimerProc);
    LogLine("SetTimer: %s (id=%lu, 1500ms)", id ? "KURULDU" : "BASARISIZ", (unsigned long)id);
    printf("ana-thread timer: %s\n", id ? "KURULDU (WndProc'tan bagimsiz drenaj)" : "BASARISIZ");
}

// Oyunun ana gorunur penceresini bul (bu surece ait, sahibi olmayan, en buyuk)
struct FindCtx { HWND best; DWORD bestArea; DWORD pid; };
static BOOL CALLBACK EnumWndProc(HWND hwnd, LPARAM lp)
{
    FindCtx* ctx = (FindCtx*)lp;
    DWORD pid = 0;
    GetWindowThreadProcessId(hwnd, &pid);
    if (pid != ctx->pid) return TRUE;
    if (!IsWindowVisible(hwnd)) return TRUE;
    if (GetWindow(hwnd, GW_OWNER) != 0) return TRUE;
    RECT rc; if (!GetWindowRect(hwnd, &rc)) return TRUE;
    DWORD area = (rc.right - rc.left) * (rc.bottom - rc.top);
    if (area > ctx->bestArea) { ctx->bestArea = area; ctx->best = hwnd; }
    return TRUE;
}

// Ana pencereyi bul ve WndProc'u subclass et. WorkerThread yeniden dener
// (oyun penceresi DLL yuklemesinden sonra birkac saniye gec olusabilir).
static bool HookGameWindow(void)
{
    if (g_hGameWnd) return true;
    FindCtx ctx; ctx.best = 0; ctx.bestArea = 0; ctx.pid = GetCurrentProcessId();
    EnumWindows(EnumWndProc, (LPARAM)&ctx);
    if (!ctx.best) return false;
    WNDPROC old = (WNDPROC)SetWindowLongPtrA(ctx.best, GWLP_WNDPROC, (LONG_PTR)MaxExecWndProc);
    if (!old) return false;
    g_oldWndProc = old;
    g_hGameWnd   = ctx.best;
    LogLine("oyun penceresi subclass edildi: hwnd=%p oldWndProc=%p",
            (unsigned long)(uintptr_t)ctx.best, (unsigned long)(uintptr_t)old);
    return true;
}

// ---------------------------------------------------------------------------
// Komut -> Python snippet ureticileri
// ---------------------------------------------------------------------------
static void QRaw(const std::string& code)
{
    std::string f;
    if (EnqueueCommand(code, f)) printf("[MAXEXEC] kuyruga yazildi: %s\n", f.c_str());
    else printf("[MAXEXEC] HATA: kuyruga yazilamadi\n");
    if (g_hGameWnd) PostMessage(g_hGameWnd, WM_APP_MAXEXEC, 0, 0);
}

static void CmdLoad(const std::string& path)
{
    char buf[1024];
    // Dosyayi ANA THREAD'de exec et — tum kurulum GIL-guvenli olur (RC4 caresi)
    // Ek: sys.stderr -> pyerr.log (Python hatalari artik dosyada gorunur, FIX-7)
    _snprintf(buf, sizeof(buf),
        "import sys\n"
        "try:\n"
        "    sys.stderr = open(r'%s', 'a', 1)\n"
        "except:\n"
        "    pass\n"
        "exec(open(r'%s').read())\n", PYERR_LOG, path.c_str());
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
    printf("[MAXEXEC] pylib yukleme komutu kuyruga alindi (kurulum ana thread'de olur)\n");
    printf("[MAXEXEC] Python hatalari icin: %s\n", PYERR_LOG);
}

static void CmdLogin(const std::string& id, const std::string& pwd)
{
    char buf[512];
    _snprintf(buf, sizeof(buf),
        "import maxlib\n"
        "maxlib.login(r'%s', r'%s')\n", id.c_str(), pwd.c_str());
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
}

static void CmdSelServer(int srv, int ch)
{
    char buf[256];
    _snprintf(buf, sizeof(buf), "import maxlib\nmaxlib.selserver(%d, %d)\n", srv, ch);
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
}

static void CmdCharlist(void)
{
    QRaw("import maxlib\nmaxlib.charlist()\n");
}

static void CmdEmpire(int e)
{
    char buf[256];
    _snprintf(buf, sizeof(buf), "import maxlib\nmaxlib.empire(%d)\n", e);
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
}

static void CmdCreate(int slot, const std::string& name, int race, int shape)
{
    char buf[512];
    _snprintf(buf, sizeof(buf),
        "import maxlib\n"
        "maxlib.create(%d, r'%s', %d, %d)\n", slot, name.c_str(), race, shape);
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
}

static void CmdEnter(int slot)
{
    char buf[256];
    _snprintf(buf, sizeof(buf), "import maxlib\nmaxlib.enter(%d)\n", slot);
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
}

static void CmdStatus(void)
{
    char buf[256];
    _snprintf(buf, sizeof(buf), "import maxlib\nmaxlib.status()\n");
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
    Sleep(400);  // ana thread'in islemesine sure ver
    std::string s;
    if (ReadFileAll(std::string(RESULT_DIR) + "\\last_status.txt", s))
        printf("[STATUS] %s", s.c_str());
    else
        printf("[STATUS] sonuc dosyasi yok (pylib yuklu mu? ana thread nabzi var mi?)\n");
}

// C++ TARAFINDA bekler; Python'u kisa patlamalarda calistirir (ana thread dostu)
static void CmdWaitFor(const std::string& sceneName, int seconds)
{
    if (!g_hGameWnd) { printf("[MAXEXEC] oyun penceresi yok\n"); return; }
    printf("[MAXEXEC] %s bekleniyor (%d sn)...\n", sceneName.c_str(), seconds);
    DWORD start = GetTickCount();
    while ((GetTickCount() - start) < (DWORD)seconds * 1000)
    {
        char buf[256];
        _snprintf(buf, sizeof(buf), "import maxlib\nmaxlib.status()\n");
        buf[sizeof(buf)-1] = 0;
        std::string f;
        EnqueueCommand(buf, f);
        PostMessage(g_hGameWnd, WM_APP_MAXEXEC, 0, 0);

        Sleep(700);
        std::string s;
        if (ReadFileAll(std::string(RESULT_DIR) + "\\last_status.txt", s))
        {
            if (s.find("SCENE=" + sceneName) != std::string::npos)
            {
                printf("[MAXEXEC] ULASILDI: %s\n", sceneName.c_str());
                printf("%s", s.c_str());
                return;
            }
        }
    }
    printf("[MAXEXEC] TIMEOUT: %s\n", sceneName.c_str());
}

// ---------------------------------------------------------------------------
// Konsol kurulumu — WORKER THREAD icinde (DllMain'de DEGIL!)
// GUI surecinde CRT stdout'u gecersiz handle ile baslar; AllocConsole
// sonrasi CRT'yi CONIN$/CONOUT$ cihazlarina yeniden baglamak SART.
// ---------------------------------------------------------------------------
static bool InitConsole(void)
{
    if (!AllocConsole())
    {
        LogLine("AllocConsole BASARISIZ gle=%lu (headless mod: kuyruk dosyalari ile kullan)",
                (unsigned long)GetLastError());
        return false;
    }
    if (!freopen("CONIN$",  "rb", stdin))
        LogLine("CONIN$ yeniden acilamadi (stdin klavye gelmeyecek)");
    if (!freopen("CONOUT$", "wb", stdout))
        LogLine("CONOUT$ yeniden acilamadi (stdout konsola yazmayacak!)");
    if (!freopen("CONOUT$", "wb", stderr))
        LogLine("CONOUT$ (stderr) yeniden acilamadi");
    setvbuf(stdout, NULL, _IONBF, 0);   // buffer'siz: crash olsa bile yazar
    setvbuf(stderr, NULL, _IONBF, 0);
    SetConsoleTitleA("MaxExecutor v1.2");
    HWND cw = GetConsoleWindow();
    if (cw)
    {
        // Oyun tam ekran/ustte olsa bile konsol gorunur kalsin (Alt+Tab'a gerek yok)
        SetWindowPos(cw, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
        SetForegroundWindow(cw);
    }
    LogLine("konsol hazir (CONIN/CONOUT yeniden baglandi, unbuffered)");
    return true;
}

// ---------------------------------------------------------------------------
// Otomatik dreneaj — konsol kapali/headless olsa bile kuyruk 2 sn'de islenir
// (yalnizca PostMessage; Python'a dokunmaz)
// ---------------------------------------------------------------------------
static DWORD WINAPI AutoDrainThread(LPVOID)
{
    while (!g_hGameWnd) Sleep(500);
    LogLine("otomatik dreneaj aktif (2 sn periyot)");
    int ticks = 0;
    while (true)
    {
        PostMessage(g_hGameWnd, WM_APP_MAXEXEC, 1, 0);
        Sleep(2000);
        // FIX-13: 30 sn'de bir sayaç ozeti (zincir izi)
        if ((++ticks % 15) == 0)
            LogLine("ozet30s: timer=%ld msg=%ld drain=%ld exec=%ld",
                    (long)g_nTimer, (long)g_nMsg, (long)g_nDrain, (long)g_nExec);
    }
    return 0;
}

// ---------------------------------------------------------------------------
// Konsol worker thread  (Python'a HIC dokunmaz — sadece dosya + PostMessage)
// ---------------------------------------------------------------------------
static std::vector<std::string> SplitArgs(const std::string& line)
{
    std::vector<std::string> out;
    bool q = false; std::string cur;
    for (size_t i = 0; i < line.size(); ++i)
    {
        char c = line[i];
        if (c == '"') { q = !q; continue; }
        if (!q && (c == ' ' || c == '\t')) { if (!cur.empty()) { out.push_back(cur); cur.clear(); } }
        else cur += c;
    }
    if (!cur.empty()) out.push_back(cur);
    return out;
}

static void PrintHelp(void)
{
    printf("\n=== MaxExecutor v1.2 (timer+wndproc ana-thread drenaj) ===\n");
    printf("  help                        : bu yardim\n");
    printf("  status                      : anlik sahne/baglanti snapshot\n");
    printf("  load <py-dosya>             : pylib.py'yi ANA THREAD'de yukle (ILK KOMUT BU OLSUN)\n");
    printf("  selserver <srv> <ch>        : SERVER LISTESI ekraninda sunucu+CH sec (OK'a basar)\n");
    printf("  login <id> <pwd>            : login ekraninda UI doldurur + giris\n");
    printf("  charlist                    : 5 slot tablosunu doken rapor\n");
    printf("  empire <1-3>                : bayrak/imparatorluk secimi\n");
    printf("  create <slot> <ad> <race> <shape> : karakter olustur (race 0-8, shape 0/1)\n");
    printf("  enter <slot>                : oyuna giris - TEK DirectEnter (cift giris yok!)\n");
    printf("  raw <python kodu>           : serbest Python (ana thread'de)\n");
    printf("  waitfor <Scene> <sn>        : orn. waitfor GameWindow 60\n");
    printf("  log                         : maxexec.log son satirlar\n");
    printf("  exit                        : cikis\n");
    printf("Akis: status -> load C:/MaxExec/pylib.py -> selserver 0 0 ->\n");
    printf("  waitfor LoginWindow 15 -> login <id> <pwd> -> waitfor SelectCharacterWindow 30\n");
    printf("  -> charlist -> enter 0 -> waitfor GameWindow 60\n");
    printf("Saglik: %s (tick/drain/exec/timer/msg/py) | zincir kaniti: results\\py_probe.txt\n\n", ALIVE_FILE);
}

static DWORD WINAPI WorkerThread(LPVOID)
{
    InitPaths();                                  // FIX-12: basedir.txt (D:\ destegi)
    LogLine("worker thread basladi (base=%s)", BASE_DIR);
    EnsureDirs();
    const bool con = InitConsole();

    printf("\n=============================================\n");
    printf("  MaxExecutor v1.2 - ana-thread executor\n");
    printf("  hook yok | SHM yok | arka-plan PyRun yok\n");
    printf("=============================================\n");
    if (!con)
        printf("[!] KONSOL ACILAMADI (headless). Komutlari %s\\queue klasorune\n"
               "    elle .cmd dosyasi olarak birak - 2 sn icinde otomatik islenir.\n", BASE_DIR);
    for (int i = 0; i < 40 && !ResolvePython(); ++i) Sleep(500);
    LogLine("python27: %s (Py_IsInitialized=%d)",
            pfn_PyRun_SimpleString ? "BULUNDU" : "YOK",
            pfn_PyIsInitialized ? pfn_PyIsInitialized() : -1);   // FIX-11
    printf("python27.dll : %s%s\n", pfn_PyRun_SimpleString ? "BULUNDU" : "YOK (oyun python'u daha baslamamis olabilir)",
           (pfn_PyIsInitialized && pfn_PyIsInitialized()) ? " [initialized]" : "");
    if (pfn_PyRun_SimpleString)
    {
        // FIX-10: PROBE - ilk drenajda ana thread'in gercekten calistigini kanitlar
        char probe[512];
        _snprintf(probe, sizeof(probe),
            "import sys, time\n"
            "_pf = open(r'%s\\py_probe.txt', 'w')\n"
            "_pf.write('PYOK t=' + time.strftime('%%H:%%M:%%S') + ' ver=' + str(sys.version)[:12] + '\\n')\n"
            "_pf.close()\n", RESULT_DIR);
        probe[sizeof(probe)-1] = 0;
        std::string pf;
        if (EnqueueCommand(probe, pf)) LogLine("probe kuyruga yazildi: %s", pf.c_str());
    }
    for (int i = 0; i < 40 && !HookGameWindow(); ++i) Sleep(500);
    if (!g_hGameWnd) LogLine("oyun penceresi 20 sn icinde bulunamadi");
    printf("oyun penceresi: %s (hwnd=%p)\n", g_hGameWnd ? "SUBCLASS EDILDI" : "BULUNAMADI",
           (void*)g_hGameWnd);
    printf("kuyruk: %s | sonuc: %s\n", QUEUE_DIR, RESULT_DIR);
    InstallTimer();                               // FIX-8: WndProc'tan bagimsiz ana yol
    CreateThread(NULL, 0, AutoDrainThread, NULL, 0, NULL);
    PrintHelp();

    char line[4096];
    while (true)
    {
        printf("maxexec> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;
        std::string ln(line);
        while (!ln.empty() && (ln[ln.size()-1] == '\n' || ln[ln.size()-1] == '\r')) ln.erase(ln.size()-1);
        if (ln.empty()) continue;

        std::vector<std::string> a = SplitArgs(ln);
        const std::string& cmd = a[0];

        if      (cmd == "help")  PrintHelp();
        else if (cmd == "exit")  break;
        else if (cmd == "status") CmdStatus();
        else if (cmd == "charlist") CmdCharlist();
        else if (cmd == "login" && a.size() >= 3) CmdLogin(a[1], a[2]);
        else if (cmd == "selserver" && a.size() >= 3) CmdSelServer(atoi(a[1].c_str()), atoi(a[2].c_str()));
        else if (cmd == "empire" && a.size() >= 2) CmdEmpire(atoi(a[1].c_str()));
        else if (cmd == "create" && a.size() >= 5) CmdCreate(atoi(a[1].c_str()), a[2], atoi(a[3].c_str()), atoi(a[4].c_str()));
        else if (cmd == "enter" && a.size() >= 2) CmdEnter(atoi(a[1].c_str()));
        else if (cmd == "load" && a.size() >= 2) CmdLoad(a[1]);
        else if (cmd == "raw" && ln.size() > 4) QRaw(ln.substr(4));
        else if (cmd == "waitfor" && a.size() >= 3) CmdWaitFor(a[1], atoi(a[2].c_str()));
        else if (cmd == "log")
        {
            FILE* f = fopen(EXEC_LOG, "r");
            if (!f) { printf("log yok\n"); continue; }
            char buf[512]; std::vector<std::string> lines;
            while (fgets(buf, sizeof(buf), f)) lines.push_back(buf);
            fclose(f);
            for (size_t i = lines.size() > 25 ? lines.size()-25 : 0; i < lines.size(); ++i)
                printf("%s", lines[i].c_str());
        }
        else printf("bilinmeyen komut (help)\n");
    }
    return 0;
}

// ---------------------------------------------------------------------------
// DllMain
// ---------------------------------------------------------------------------
static void EnsureDirs(void)
{
    MkDirp(BASE_DIR); MkDirp(QUEUE_DIR); MkDirp(RESULT_DIR);
}

BOOL APIENTRY DllMain(HMODULE hMod, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        // Loader-lock guvenli minimal init: konsol kurulumu worker'a tasindi (FIX-3)
        DisableThreadLibraryCalls(hMod);
        EnsureDirs();
        CreateThread(NULL, 0, WorkerThread, NULL, 0, NULL);
        LogLine("MaxExecutor v1.2 yuklendi (pid=%lu) — worker baslatiliyor",
                GetCurrentProcessId());
    }
    return TRUE;
}
