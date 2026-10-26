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
//  v1.3 DUZELTMELER (saha testi 26.10 — "bi bok yazilmadi" kökü bulundu):
//    KOK NEDEN: makinede C:\MaxExec\pylib.py YOKTU. load komutu sessiz
//    IOError yedi (pyerr.log'a dustu), maxlib hic kurulmadi; sonraki her
//    status/login/waitfor "ImportError: No module named maxlib" yedi.
//    Zincir kendisi SAGLAMDI: py_probe.txt olustu (kanit), alive.txt kostu.
//    FIX-14: AUTO-LOAD — pylib.py BASE_DIR icindeyse startup'ta otomatik
//            kuyruga konur; `load` yazmak ARTIK ZORUNLU DEGIL. Dosya yoksa
//            konsol + log + results\last_load.txt uzerinden NET uyarı.
//    FIX-15: KENDINI ONARAN SNIPPET — butun komutlar
//            try:import maxlib / except:exec(pylib.py) bootstrap ile gider;
//            maxlib bir kere dusse bile ilk komut geri getirir.
//    FIX-16: load <dosya> C++ tarafinda varlik kontrolu yapar; yanlis yazi
//            sahibine acikca soylenir (sessiz IOError devri kapandi).
//    FIX-17: pyerr komutu — pyerr.log son satirlarini konsola doker.
//    FIX-18: PROBE sys.stderr'i pyerr.log'a baglar; ilk andan itibaren
//            butun traceback'ler dosyaya duser.
//  v1.4 (oturum 9 — giris sonrasi karakter islemleri):
//    + selchar/newchar/joblist/mkchar/empirelist/empireui/delchar/delcode
//      /lasterr/serverlist komutlari (pylib v3.0 cifti)
//    + lasterr: oyun hatalarini (yanlis sifre vb.) konsola doker —
//      pylib'in OnLoginFailure/OnCreateFailure/OnDelete* hooklari
//      results\last_error.txt'ye yazar.
//  v1.5 (oturum 10 - saha testi 5: "yeni komutlar calismiyor" kok nedeni):
//    KOK NEDEN: makinede DLL v1.4 vardi ama pylib.py hala v2.0 idi (eski
//    bundle'dan kopyalanmisti). selchar/newchar/mkchar/delchar -> sessiz
//    AttributeError: pyerr.log'a duser, konsol SUSAR, kimse fark etmez.
//    Bu durum artik IMKANSIZ hale getirildi:
//    FIX-19: SURUM EL SIKISMASI - acilista C++ pylib.py'yi okuyup
//            PYLIB_VERSION isaretini cikarir; <3 ise konsolda KOSKOCA
//            uyar + results\last_warning.txt + maxexec.log'a kayit.
//    FIX-20: PyRun_SimpleString DONUS DEGERI KONTROL - rc!=0 ise konsola
//            "!! PYTHON HATASI - detay: pyerr" basilir + last_pyfail.txt
//            yazilir + alive.txt'ye pyfail sayaci eklenir. Sessiz Python
//            hatasi devri kapandi.
//    FIX-21: BootImport surum guard'i - diskteki pylib eskiyse her komut
//            oncesi pyerr.log'a ACIKLAMALI uyari satiri (AttributeError
//            yaninda "PYLIB ESKI - yeni pylib.py kopyala" yazar).
//    FIX-22: GOMULU PYLIB - pylib v3.0 DLL ICINE gomulu (pylib_embedded.h,
//            scripts/embed_pylib.py uretir). Diskteki pylib eksik/eskiyse
//            DLL otomatik yazar (eskisi yedeklenir) - artik SADECE DLL
//            guncellemek yeterli, pylib.py'yi elle tasimak zorunlu degil.
//  v1.6 (oturum 11 - saha testi 6: "her komutta PYTHON HATASI" kok nedeni):
//    KOK NEDEN: v1.5, BootImport'a FIX-21 surum guard'ini ekleyince bootstrap
//            ~630 karaktere buyudu; ama ESKI komut ureticileri hala
//            char buf[256]/[512] + _snprintf ile kod uretiyordu. _snprintf
//            sessizce kesti -> 255/511 byte'lik .cmd dosyalari SATIR
//            ORTASINDA kopuk Python kodu iceriyordu -> SyntaxError
//            ("EOL while scanning string literal") -> selserver/login/
//            status/selchar/mkchar/delchar/delcode PYFAIL. Kanit:
//            maxexec.log'ta 255/511 byte = PATLADI; 674 byte (std::string
//            ile uretilen newchar/joblist/lasterr) = CALISTI.
//    FIX-23: Butun komut ureticileri std::string birlestirmeye cevrildi;
//            sabit tampon + _snprintf devri kapandi (truncate imkansiz).
//    FIX-24: Eksik argumanli komutlara "kullanim: ..." mesaji (eskiden
//            yaniltici "bilinmeyen komut" dustu).
//    FIX-25: Bayat surum dizgileri (konsol basligi + DllMain logu hala
//            "v1.4" diyordu - saha logunda sikici karisiklik yaratıyordu).
//    FIX-26: Konsol printf dizgileri ASCII'ye cekildi (CP857'de uzun cizgi
//            karakteri mojibake olarak gorunuyordu).
//    FIX-27: status artik bayat last_status.txt'yi gostermiyor (eski kod
//            400ms sonra dosyayi okuyup basiyordu; komut fail olsa bile
//            39 dk onceki sonuc gorunuyordu - saha kanitli).
//    FIX-28: PROBE sys.stdout'u CONOUT$'a baglar - oyun Python'inin print
//            cikisi artik konsola duser; pylib v3.1 rapor yankisi (charlist/
//            joblist/mkchar canli cikisi) bunun uzerinden calisir.
//  v1.7 (oturum 12 - saha testi 7: "enter takiliyor + sahte CREATE_FAILURE"):
//    Saha kaniti 1: enter/DirectEnter YENI olusan karakterde server
//            tarafindan reddediliyor (loading acilip login ekranina geri
//            atiyor), eski karakterde calisiyor. Kullanici dogrulamasi:
//            oyunun kendi START butonu (UI yolu) calisiyor.
//    Saha kaniti 2: mkchar sonrasi CREATE_FAILURE: 0 "0 karakter
//            yaratilamaz" - ama karakter olusuyordu. Kok neden: cift paket
//            (UI OLUSTUR butonu + pylib'in direkt SendCreateCharacterPacket
//            cagrisi). 1. paket basarili, 2. paket reddedildi -> sahte hata.
//    FIX-29 (pylib v3.2): enter() UI START yolu ONCELIKLI (SelectSlot +
//            StartGame/startButton - MaximumPyScript_Merged_calisan yolu);
//            DirectEnter sadece UI yolu bulunamazsa YEDEK. RC12 cift-giris
//            yasagi korunur.
//    FIX-30 (pylib v3.2): mkchar() paket yolu SADECE buton bulunamazsa;
//            buton bastiysa paket atlanir (cift paket = sahte CREATE_FAILURE).
//    FIX-31: surum dizgileri + help metni v1.7'ye cekildi; enter help'i
//            yeni yolu anlatir.
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
#include "pylib_embedded.h"   // FIX-22: gomulu pylib (v3.2, otomatik uretilir)

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
static volatile LONG g_nPyFail = 0;  // FIX-20: PyRun'in -1 dondurdugu komutlar

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
    char buf[192];
    sprintf(buf, "tick=%lu drain=%ld exec=%ld timer=%ld msg=%ld py=%d pyfail=%ld",
            (unsigned long)GetTickCount(),
            (long)g_nDrain, (long)g_nExec, (long)g_nTimer, (long)g_nMsg,
            pfn_PyRun_SimpleString ? 1 : 0, (long)g_nPyFail);   // FIX-20
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
            int rc = pfn_PyRun_SimpleString(code.c_str());
            InterlockedIncrement(&g_nExec);
            ++done;
            // FIX-20: traceback pyerr.log'da olur ama sahibi KONSOLDA da
            // gormek zorunda - sessiz Python hatasi devri kapandi.
            if (rc != 0)
            {
                InterlockedIncrement(&g_nPyFail);
                LogLine("PYFAIL %s (rc=%d)", fd.cFileName, rc);
                char fp[MAX_PATH];
                _snprintf(fp, MAX_PATH, "%s\\last_pyfail.txt", RESULT_DIR); fp[MAX_PATH-1]=0;
                WriteFileAll(fp, std::string("PYTHON HATASI: ") + fd.cFileName +
                    "\nDetay: pyerr komutunu yaz (pyerr.log son satirlari).\n"
                    "En sik neden: ESKI pylib.py - v3.0 ile degistir (bundle zip)!\n");
                printf("[MAXEXEC] !! PYTHON HATASI (%s) - detay icin: pyerr\n", fd.cFileName);
                fflush(stdout);
            }
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

// ---------------------------------------------------------------------------
// FIX-15: kendini onaran import bootstrap — maxlib sys.modules'te yoksa
// pylib.py'yi exec edip tekrar dener. load atlandiysa ya da modul dustuysa
// ilk komut kendini iyilestirir. (Pyerr.log'a dusen "No module named maxlib"
// saldirisinin panzehiri.)
// ---------------------------------------------------------------------------
static std::string BootImport(void)
{
    // FIX-15: kendini onaran import + FIX-21: surum guard'i.
    // Diskteki pylib eskiyse (v2.x) pyerr.log'a ACIKLAMALI uyari duser;
    // yeni komutlarin AttributeError'leri boylece kendini aciklar.
    // NOT (FIX-23): bu metin ~630 karakterdir; ASLA char buf[256/512]
    // icine _snprintf ile yazma - v1.5 tam bunu yapip 255/511 byte'lik
    // kopuk .cmd'ler uretti. Kullananlar std::string birlestirsin:
    //   QRaw(BootImport() + "maxlib.xxx(...)")
    char buf[1024];
    _snprintf(buf, sizeof(buf),
        "try:\n"
        "    import maxlib\n"
        "except Exception:\n"
        "    exec(open(r'%s\\pylib.py').read())\n"
        "    import maxlib\n"
        "try:\n"
        "    _mxv = int(str(getattr(maxlib, 'PYLIB_VERSION', '0')).split('.')[0])\n"
        "except Exception:\n"
        "    _mxv = 0\n"
        "if _mxv < 3 and not getattr(maxlib, '_MX_OLD_WARNED', False):\n"
        "    maxlib._MX_OLD_WARNED = True\n"
        "    try:\n"
        "        import sys\n"
        "        sys.stderr.write('!!! PYLIB ESKI v' + str(getattr(maxlib, 'PYLIB_VERSION', '?')) + ' - DLL v1.7: selchar/newchar/mkchar/delchar/empirelist/empireui/joblist/delcode/lasterr komutlari pylib v3.0 ister! C:\\MaxExec\\pylib.py dosyasini yenisiyle degistir (bundle zip icinde) !!!\\n')\n"
        "    except Exception:\n"
        "        pass\n", BASE_DIR);
    buf[sizeof(buf)-1] = 0;
    return std::string(buf);
}

static void CmdLoad(const std::string& path)
{
    // FIX-16: once C++ tarafinda varlik kontrolu — sessiz IOError'a son
    DWORD attr = GetFileAttributesA(path.c_str());
    if (attr == INVALID_FILE_ATTRIBUTES || (attr & FILE_ATTRIBUTE_DIRECTORY))
    {
        char rp[MAX_PATH];
        _snprintf(rp, MAX_PATH, "%s\\last_load.txt", RESULT_DIR); rp[MAX_PATH-1]=0;
        std::string msg = "HATA: pylib dosyasi YOK: " + path + "\n"
                          "Cozum: bundle zip icindeki pylib.py'yi su klasore kopyala:\n  " +
                          std::string(BASE_DIR) +
                          "\n(v1.3: dosya oradaysa otomatik yuklenir)\n";
        WriteFileAll(rp, msg);
        printf("[MAXEXEC] HATA: dosya YOK: %s\n", path.c_str());
        printf("    pylib.py'yi su klasore kopyala: %s\n", BASE_DIR);
        printf("    (bundle zip icinde var; v1.3 otomatik yukler)\n");
        LogLine("load HATA: dosya yok: %s", path.c_str());
        return;
    }
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
    // FIX-23: cagri satiri kisa tamponda uretilir, bootstrap std::string
    // ile birlestirilir - _snprintf'un BootImport'i kesmesi artik imkansiz.
    char call[512];
    _snprintf(call, sizeof(call), "maxlib.login(r'%s', r'%s')\n", id.c_str(), pwd.c_str());
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdSelServer(int srv, int ch)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.selserver(%d, %d)\n", srv, ch);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdServerList(void)
{
    QRaw(BootImport() + "maxlib.serverlist()\n");
}

static void CmdSelChar(int slot)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.selchar(%d)\n", slot);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdNewChar(void)
{
    QRaw(BootImport() + "maxlib.newchar()\n");
}

static void CmdJobList(void)
{
    QRaw(BootImport() + "maxlib.joblist()\n");
}

static void CmdMkChar(const std::string& name, int race)
{
    char call[128];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.mkchar(r'%s', %d)\n", name.c_str(), race);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdEmpireList(void)
{
    QRaw(BootImport() + "maxlib.empirelist()\n");
}

static void CmdEmpireUI(int n)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.empireui(%d)\n", n);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdDelChar(int slot)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.delchar(%d)\n", slot);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdDelCode(const std::string& code)
{
    char call[128];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.delcode(r'%s')\n", code.c_str());
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdLastErr(void)
{
    QRaw(BootImport() + "maxlib.lasterr()\n");
    Sleep(400);
    std::string s;
    if (ReadFileAll(std::string(RESULT_DIR) + "\\last_error.txt", s))
    {
        printf("[LASTERR] oyun hatalari (sonlar en altta):\n");
        // son 25 satir
        std::vector<std::string> lines;
        size_t p = 0;
        while (p < s.size())
        {
            size_t q = s.find('\n', p);
            if (q == std::string::npos) q = s.size();
            if (q > p) lines.push_back(s.substr(p, q - p));
            p = q + 1;
        }
        for (size_t i = lines.size() > 25 ? lines.size()-25 : 0; i < lines.size(); ++i)
            printf("  %s\n", lines[i].c_str());
        if (lines.empty()) printf("  (bos - henuz oyun hatasi yaklanmadi)\n");
    }
    else
        printf("[LASTERR] last_error.txt yok - henuz oyun hatasi yaklanmadi\n");
}

static void CmdCharlist(void)
{
    QRaw(BootImport() + "maxlib.charlist()\n");
}

static void CmdEmpire(int e)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.empire(%d)\n", e);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdCreate(int slot, const std::string& name, int race, int shape)
{
    char call[160];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.create(%d, r'%s', %d, %d)\n", slot, name.c_str(), race, shape);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdEnter(int slot)
{
    char call[64];   // FIX-23
    _snprintf(call, sizeof(call), "maxlib.enter(%d)\n", slot);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdStatus(void)
{
    // FIX-23 + FIX-27: eskiden komut 256 byte'lik tampona sigmayip PATLIYORDU
    // (SyntaxError); ustelik 400 ms sonra last_status.txt okunup basilirdi ki
    // o BAYAT icerikti (saha testinde 39 dk onceki sonuc iki kez gorundu).
    // Artik cikisi pylib v3.1 canli yaziyor (FIX-28 konsol stdout baglanti).
    QRaw(BootImport() + "maxlib.status()\n");
}

// C++ TARAFINDA bekler; Python'u kisa patlamalarda calistirir (ana thread dostu)
static void CmdWaitFor(const std::string& sceneName, int seconds)
{
    if (!g_hGameWnd) { printf("[MAXEXEC] oyun penceresi yok\n"); return; }
    printf("[MAXEXEC] %s bekleniyor (%d sn)...\n", sceneName.c_str(), seconds);
    DWORD start = GetTickCount();
    while ((GetTickCount() - start) < (DWORD)seconds * 1000)
    {
        std::string f;
        EnqueueCommand(BootImport() + "maxlib.status(0)\n", f);   // FIX-23 (status(0): konsol yankisi kapali, spam yok)
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
    printf("[MAXEXEC] TIMEOUT: %s (ipucu: status + pyerr komutlarina bak)\n", sceneName.c_str());
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
    SetConsoleTitleA("MaxExecutor v1.7");
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
    printf("\n=== MaxExecutor v1.7 (UI giris yolu + temiz karakter olusturma) ===\n");
    printf("  help                        : bu yardim\n");
    printf("  status                      : anlik sahne/baglanti snapshot\n");
    printf("  serverlist                  : server/CH listbox icerigi\n");
    printf("  selserver <srv> <ch>        : server+CH sec, OK'a bas\n");
    printf("  login <id> <pwd>            : login ekraninda UI doldurur + giris\n");
    printf("  charlist                    : 5 slot tablosunu doken rapor\n");
    printf("  selchar <slot>              : karakter slotu SEC (0-4)\n");
    printf("  enter <slot>                : oyuna giris - UI START yolu (DirectEnter yedek)\n");
    printf("  -- karakter olusturma --\n");
    printf("  newchar                     : olustur butonuna bas (bayrak/olusturma acar)\n");
    printf("  empirelist                  : bayrak listesi + mevcut empire\n");
    printf("  empireui <1-3>              : bayrak sec + ILERLE (1=Shinsoo 2=Chunjo 3=Jinno)\n");
    printf("  joblist                     : sinif/cinsiyet tablosu (race 0-8)\n");
    printf("  mkchar <ad> <race>          : UI akisiyla OLUSTUR (sinif+cinsiyet+isim+enter)\n");
    printf("  -- karakter silme --\n");
    printf("  delchar <slot>              : slotu sec + silme sorusu + kod dialogu ACAR\n");
    printf("  delcode <kod>               : silme kodunu yazar + ONAYLAR\n");
    printf("  -- hata takibi --\n");
    printf("  lasterr                     : OYUN hatalari (yanlis sifre vb.)\n");
    printf("  pyerr                       : PYTHON hatalari (traceback)\n");
    printf("  log                         : maxexec.log son satirlari\n");
    printf("  load <py-dosya>             : pylib yukle (v1.3+ zaten otomatik)\n");
    printf("  raw <python kodu>           : serbest Python (ana thread'de)\n");
    printf("  waitfor <Scene> <sn>        : orn. waitfor GameWindow 60\n");
    printf("  exit                        : cikis\n");
    printf("GIRIS AKISI: status -> selserver 0 0 -> waitfor LoginWindow 15 ->\n");
    printf("  login <id> <pwd> -> waitfor SelectCharacterWindow 30 -> charlist\n");
    printf("YENI KARAKTER: newchar -> status -> (bayrak geldiyse empirelist ->\n");
    printf("  empireui 1 -> waitfor CreateCharacterWindow 10) -> joblist ->\n");
    printf("  mkchar Isim 3 -> waitfor SelectCharacterWindow 15 -> charlist\n");
    printf("SILME: charlist -> delchar <slot> -> delcode <silme-kodu> -> lasterr\n");
    printf("Saglik: %s | oyun hatalari: results\\last_error.txt\n\n", ALIVE_FILE);
}

// ---------------------------------------------------------------------------
// FIX-19: pylib surum okuyucu - diskteki pylib.py'den PYLIB_VERSION isaretini
// ceker. Isaret yoksa (v2.0 ve oncesi) yanlis doner -> eski kabul edilir.
// ---------------------------------------------------------------------------
static bool ReadPylibVersion(const char* path, char outVer[32])
{
    outVer[0] = 0;
    FILE* f = fopen(path, "rb");
    if (!f) return false;
    char buf[16384];
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);
    buf[n] = 0;
    const char* p = strstr(buf, "PYLIB_VERSION");
    if (!p) return false;
    p = strstr(p, "=");
    if (!p) return false;
    ++p;
    while (*p == ' ' || *p == '\t') ++p;
    if (*p == '\'' || *p == '"')
    {
        char q = *p; ++p;
        int i = 0;
        while (*p && *p != q && *p != '\n' && i < 30) outVer[i++] = *p++;
        outVer[i] = 0;
    }
    else
    {
        int i = 0;
        while (((*p >= '0' && *p <= '9') || *p == '.') && i < 30) outVer[i++] = *p++;
        outVer[i] = 0;
    }
    return outVer[0] != 0;
}

// ---------------------------------------------------------------------------
// FIX-22: GOMULU PYLIB SENKRONU — DLL icinde tasiyan pylib kopyasini diske
// yazar. Diskteki pylib eksikse olusturur, eskiyse gunceller (eskisini
// pylib_eski_vX.py olarak yedekler). 'DLL yeni ama pylib eski' hatasi
// artik otomatik iyilesir — elle dosya kopyalama zorunlulugu kalkti.
// ---------------------------------------------------------------------------
static void SyncEmbeddedPylib(void)
{
    char pylibPath[MAX_PATH];
    _snprintf(pylibPath, MAX_PATH, "%s\\pylib.py", BASE_DIR); pylibPath[MAX_PATH-1]=0;
    char diskVer[32];
    bool hasDisk = ReadPylibVersion(pylibPath, diskVer);
    int diskMaj  = hasDisk ? atoi(diskVer) : 0;
    int diskMin  = 0;
    if (hasDisk) { const char* d = strchr(diskVer, '.'); if (d) diskMin = atoi(d+1); }
    const char* edot = strchr(EMBEDDED_PYLIB_VERSION, '.');
    int embMaj = atoi(EMBEDDED_PYLIB_VERSION);
    int embMin = edot ? atoi(edot+1) : 0;
    // v1.6: minor-farkinda karsilastirma - disk v3.0 / gomulu v3.1 ise
    // senkron TETIKLENIR (eskiden 3>=3 geciyordu, eski dosya kalabiliyordu)
    if (hasDisk && (diskMaj > embMaj || (diskMaj == embMaj && diskMin >= embMin)))
        return;   // disk zaten yeni/esit - dokunma
    if (hasDisk)
    {
        char bak[MAX_PATH];
        _snprintf(bak, MAX_PATH, "%s\\pylib_eski_v%s.py", BASE_DIR,
                  diskVer[0] ? diskVer : "2x"); bak[MAX_PATH-1]=0;
        if (CopyFileA(pylibPath, bak, FALSE))
            LogLine("pylib sync: eski dosya yedeklendi -> %s", bak);
    }
    std::string emb((const char*)EMBEDDED_PYLIB_DATA, EMBEDDED_PYLIB_SIZE);
    if (WriteFileAll(pylibPath, emb))
    {
        LogLine("pylib sync: gomulu pylib v%s diske yazildi (eskisi: %s)",
                EMBEDDED_PYLIB_VERSION, hasDisk ? diskVer : "yok");
        printf("pylib.py      : GUNCELLENDI -> v%s (DLL icinden yazildi%s)\n",
               EMBEDDED_PYLIB_VERSION,
               hasDisk ? ", eski dosya pylib_eski_*.py olarak yedeklendi" : "");
    }
    else
    {
        LogLine("pylib sync HATA: %s yazilamadi", pylibPath);
        printf("pylib.py      : GUNCELLENEMEDI (yazma hatasi!) - elle kopyala\n");
    }
}

static DWORD WINAPI WorkerThread(LPVOID)
{
    InitPaths();                                  // FIX-12: basedir.txt (D:\ destegi)
    LogLine("worker thread basladi (base=%s)", BASE_DIR);
    EnsureDirs();
    const bool con = InitConsole();

    printf("\n=============================================\n");
    printf("  MaxExecutor v1.7 - ana-thread executor (UI giris yolu + temiz olusturma)\n");
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
        // FIX-18: probe ayrica sys.stderr'i pyerr.log'a baglar — butun
        //         traceback'ler ilk andan itibaren dosyaya duser.
        char probe[896];
        _snprintf(probe, sizeof(probe),
            "import sys, time\n"
            "try:\n"
            "    sys.stderr = open(r'%s', 'a', 1)\n"
            "except:\n"
            "    pass\n"
            "try:\n"
            "    sys.stdout = open(r'CONOUT$', 'w', 0)\n"
            "except:\n"
            "    pass\n"
            "_pf = open(r'%s\\py_probe.txt', 'w')\n"
            "_pf.write('PYOK t=' + time.strftime('%%H:%%M:%%S') + ' ver=' + str(sys.version)[:24] + '\\n')\n"
            "_pf.write('stdout: ' + str(getattr(sys.stdout, 'name', '?')) + '\\n')\n"
            "_pf.close()\n", PYERR_LOG, RESULT_DIR);
        probe[sizeof(probe)-1] = 0;
        std::string pf;
        if (EnqueueCommand(probe, pf)) LogLine("probe kuyruga yazildi: %s", pf.c_str());

        // FIX-14: AUTO-LOAD + FIX-19: SURUM EL SIKISMASI + FIX-22: GOMULU SENKRON
        // (Saha testi 5 dersi: DLL yeni ama pylib eski olabiliyordu - v1.5
        //  artik gomulu kopyayi diske yazar, el sikismasi da dogrular.)
        SyncEmbeddedPylib();
        char pylibPath[MAX_PATH];
        _snprintf(pylibPath, MAX_PATH, "%s\\pylib.py", BASE_DIR); pylibPath[MAX_PATH-1]=0;
        DWORD pa = GetFileAttributesA(pylibPath);
        if (pa != INVALID_FILE_ATTRIBUTES && !(pa & FILE_ATTRIBUTE_DIRECTORY))
        {
            char ver[32];
            bool okVer = ReadPylibVersion(pylibPath, ver) && atoi(ver) >= 3;
            std::string ld;
            if (EnqueueCommand(BootImport(), ld))
                LogLine("AUTO-LOAD: pylib.py kuyruga kondu (%s)", pylibPath);
            if (okVer)
            {
                printf("pylib.py      : v%s (uyumlu) - otomatik yuklenecek, load yazmana gerek yok\n", ver);
                printf("                kanit dosyasi: %s\\last_pylib_load.txt\n", RESULT_DIR);
            }
            else
            {
                const char* vShow = ver[0] ? ver : "2.x (isaret yok)";
                char rp[MAX_PATH];
                _snprintf(rp, MAX_PATH, "%s\\last_warning.txt", RESULT_DIR); rp[MAX_PATH-1]=0;
                WriteFileAll(rp, std::string("! PYLIB ESI SURUM: v") + vShow +
                    "  (DLL v1.7 pylib v3.0 ister)\n"
                    "Yeni pylib.py'yi " + std::string(BASE_DIR) + " icine kopyala (bundle zip / GitHub).\n"
                    "ESKI pylib ILE: selchar/newchar/mkchar/delchar/empirelist/empireui/"
                    "joblist/delcode/lasterr CALISMAZ (AttributeError).\n");
                LogLine("UYARI: pylib ESI v%s - v3.0 gerekli! (%s)", vShow, pylibPath);
                printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
                printf("!! PYLIB ESI: diskteki pylib.py = v%s  (gereken: v3.0)\n", vShow);
                printf("!! Yeni pylib.py'yi %s icine kopyala (bundle zip icinde var)\n", BASE_DIR);
                printf("!! Eski pylib ile yeni komutlar CALISMAZ (selchar/mkchar/delchar..)\n");
                printf("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
            }
        }
        else
        {
            char rp[MAX_PATH];
            _snprintf(rp, MAX_PATH, "%s\\last_load.txt", RESULT_DIR); rp[MAX_PATH-1]=0;
            WriteFileAll(rp, "HATA: " + std::string(pylibPath) + " YOK!\n"
                             "bundle zip icindeki pylib.py'yi " + std::string(BASE_DIR) +
                             " klasorune kopyala.\n");
            LogLine("UYARI: pylib.py YOK — komutlar calismaz! (%s)", pylibPath);
            printf("pylib.py      : YOK!! (%s)\n", pylibPath);
            printf("                bundle zip'ten pylib.py'yi %s icine kopyala.\n", BASE_DIR);
            printf("                Kopyalamadan komut yazarsan: ImportError maxlib.\n");
        }
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

        // FIX-24: eksik arguman -> yaniltici "bilinmeyen komut" yerine kullanim mesaji
        if      (cmd == "help")  PrintHelp();
        else if (cmd == "exit")  break;
        else if (cmd == "status") CmdStatus();
        else if (cmd == "charlist") CmdCharlist();
        else if (cmd == "login")
        {
            if (a.size() >= 3) CmdLogin(a[1], a[2]);
            else printf("kullanim: login <id> <sifre>\n");
        }
        else if (cmd == "selserver")
        {
            if (a.size() >= 3) CmdSelServer(atoi(a[1].c_str()), atoi(a[2].c_str()));
            else printf("kullanim: selserver <server> <kanal>   (orn. selserver 0 0)\n");
        }
        else if (cmd == "empire")
        {
            if (a.size() >= 2) CmdEmpire(atoi(a[1].c_str()));
            else printf("kullanim: empire <1-3>   (1=Shinsoo 2=Chunjo 3=Jinno)\n");
        }
        else if (cmd == "create")
        {
            if (a.size() >= 5) CmdCreate(atoi(a[1].c_str()), a[2], atoi(a[3].c_str()), atoi(a[4].c_str()));
            else printf("kullanim: create <slot> <ad> <race> <shape>\n");
        }
        else if (cmd == "enter")
        {
            if (a.size() >= 2) CmdEnter(atoi(a[1].c_str()));
            else printf("kullanim: enter <slot>\n");
        }
        else if (cmd == "selchar")
        {
            if (a.size() >= 2) CmdSelChar(atoi(a[1].c_str()));
            else printf("kullanim: selchar <slot 0-4>\n");
        }
        else if (cmd == "newchar") CmdNewChar();
        else if (cmd == "joblist") CmdJobList();
        else if (cmd == "mkchar")
        {
            if (a.size() >= 3) CmdMkChar(a[1], atoi(a[2].c_str()));
            else printf("kullanim: mkchar <isim> <race 0-8>   (orn. mkchar Isim 3 = Shaman(K))\n");
        }
        else if (cmd == "empirelist") CmdEmpireList();
        else if (cmd == "empireui")
        {
            if (a.size() >= 2) CmdEmpireUI(atoi(a[1].c_str()));
            else printf("kullanim: empireui <1-3>   (1=Shinsoo 2=Chunjo 3=Jinno)\n");
        }
        else if (cmd == "delchar")
        {
            if (a.size() >= 2) CmdDelChar(atoi(a[1].c_str()));
            else printf("kullanim: delchar <slot 0-4>   (sonra delcode <silme-kodu>)\n");
        }
        else if (cmd == "delcode")
        {
            if (a.size() >= 2) CmdDelCode(a[1]);
            else printf("kullanim: delcode <silme-kodu>   (once delchar <slot>)\n");
        }
        else if (cmd == "serverlist") CmdServerList();
        else if (cmd == "lasterr") CmdLastErr();
        else if (cmd == "load")
        {
            if (a.size() >= 2) CmdLoad(a[1]);
            else printf("kullanim: load <py-dosyasi>   (v1.3+ zaten otomatik)\n");
        }
        else if (cmd == "raw")
        {
            if (ln.size() > 4) QRaw(ln.substr(4));
            else printf("kullanim: raw <python kodu>   (orn. raw import sys)\n");
        }
        else if (cmd == "waitfor")
        {
            if (a.size() >= 3) CmdWaitFor(a[1], atoi(a[2].c_str()));
            else printf("kullanim: waitfor <SahneAdi> <saniye>   (orn. waitfor GameWindow 60)\n");
        }
        else if (cmd == "pyerr")   // FIX-17: Python hatalarini konsolda gor
        {
            FILE* f = fopen(PYERR_LOG, "r");
            if (!f) { printf("pyerr.log yok (henuz Python hatasi olusmadi)\n"); continue; }
            char buf[512]; std::vector<std::string> lines;
            while (fgets(buf, sizeof(buf), f)) lines.push_back(buf);
            fclose(f);
            printf("--- pyerr.log son %d satir ---\n", (int)(lines.size() > 30 ? 30 : lines.size()));
            for (size_t i = lines.size() > 30 ? lines.size()-30 : 0; i < lines.size(); ++i)
                printf("%s", lines[i].c_str());
        }
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
        LogLine("MaxExecutor v1.7 yuklendi (pid=%lu) — worker baslatiliyor",
                GetCurrentProcessId());
    }
    return TRUE;
}
