// ============================================================================
//  MaxExecutor.cpp — Metin2 Ana-Thread Güvenli Python Executor  (v1.0)
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
static const char*   BASE_DIR         = "C:\\MaxExec";
static const char*   QUEUE_DIR        = "C:\\MaxExec\\queue";
static const char*   RESULT_DIR       = "C:\\MaxExec\\results";
static const char*   ALIVE_FILE       = "C:\\MaxExec\\alive.txt";
static const char*   EXEC_LOG         = "C:\\MaxExec\\maxexec.log";
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
    sprintf(tmp, "%s\\c_%u_%04u.tmp", QUEUE_DIR, GetTickCount(), seq);
    sprintf(fin, "%s\\c_%u_%04u.cmd", QUEUE_DIR, GetTickCount(), seq);
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

static void Heartbeat(void)
{
    char buf[64];
    sprintf(buf, "%lu", GetTickCount());
    WriteFileAll(ALIVE_FILE, buf);
}

static void DrainQueue(void)
{
    if (!pfn_PyRun_SimpleString) return;

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
        DrainQueue();
        return 0;
    }
    return CallWindowProc(g_oldWndProc, hwnd, msg, wp, lp);
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
    char buf[512];
    // Dosyayi ANA THREAD'de exec et — tum kurulum GIL-guvenli olur (RC4 caresi)
    _snprintf(buf, sizeof(buf), "exec(open(r'%s').read())", path.c_str());
    buf[sizeof(buf)-1] = 0;
    QRaw(buf);
    printf("[MAXEXEC] pylib yukleme komutu kuyruga alindi (kurulum ana thread'de olur)\n");
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
    printf("\n=== MaxExecutor v1.0 (ana-thread WndProc + dosya kuyruk) ===\n");
    printf("  help                        : bu yardim\n");
    printf("  status                      : anlik sahne/baglanti snapshot\n");
    printf("  load <py-dosya>             : pylib.py'yi ANA THREAD'de yukle (ILK KOMUT BU OLSUN)\n");
    printf("  login <id> <pwd>            : auth'a baglan + giris (paket yolu)\n");
    printf("  charlist                    : 5 slot tablosunu doken rapor\n");
    printf("  empire <1-3>                : bayrak/imparatorluk secimi\n");
    printf("  create <slot> <ad> <race> <shape> : karakter olustur (race 0-8, shape 0/1)\n");
    printf("  enter <slot>                : oyuna giris — TEK DirectEnter (cift giris yok!)\n");
    printf("  raw <python kodu>           : serbest Python (ana thread'de)\n");
    printf("  waitfor <Scene> <sn>        : orn. waitfor GameWindow 60\n");
    printf("  log                         : maxexec.log son satirlar\n");
    printf("  exit                        : cikis\n");
    printf("Kurulum sirasi: status -> load C:/MaxExec/pylib.py -> login <id> <pwd>\n");
    printf("  -> waitfor SelectCharacterWindow 30 -> charlist -> (empire/create)\n");
    printf("  -> enter 0 -> waitfor GameWindow 60\n\n");
}

static DWORD WINAPI WorkerThread(LPVOID)
{
    printf("\n=============================================\n");
    printf("  MaxExecutor v1.0 — ana-thread executor\n");
    printf("  hook yok | SHM yok | arka-plan PyRun yok\n");
    printf("=============================================\n");
    for (int i = 0; i < 40 && !ResolvePython(); ++i) Sleep(500);
    printf("python27.dll : %s\n", pfn_PyRun_SimpleString ? "BULUNDU" : "YOK (oyun python'u daha baslamamis olabilir)");
    for (int i = 0; i < 40 && !HookGameWindow(); ++i) Sleep(500);
    printf("oyun penceresi: %s (hwnd=%p)\n", g_hGameWnd ? "SUBCLASS EDILDI" : "BULUNAMADI",
           (void*)g_hGameWnd);
    printf("kuyruk: %s | sonuc: %s\n", QUEUE_DIR, RESULT_DIR);
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
        DisableThreadLibraryCalls(hMod);
        EnsureDirs();
        AllocConsole();
        SetConsoleTitleA("MaxExecutor v1.0 — ana-thread executor");
        CreateThread(NULL, 0, WorkerThread, NULL, 0, NULL);
        LogLine("MaxExecutor yuklendi (pid=%lu)", GetCurrentProcessId());
    }
    return TRUE;
}
