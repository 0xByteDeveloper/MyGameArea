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
//  v1.8 "PLUSMAXGOD" (oturum 13 - kullanici raporu: HEPSI CALISTI):
//    Kullanici talebi: (1) giris sonrasi oyun-ici komutlar (envanter, chat,
//    hareket/pozisyon), (2) oyuna ait tum python dosyalarini cekme+inceleme,
//    (3) fonksiyon katalogu PLUSQuest. pylib v4.0 = PLUSMAXGOD_PyScript.py
//    (kanit havuzu: nighttown koleksiyonu 4000+ kullanim + cycu.py).
//    FIX-32: BootImport surum-ongoer oldu - eski maxlib (v3.x) yuklu ise
//            diskteki PLUSMAXGOD_PyScript.py ile YERINDE exec edilir
//            (yukseiltme); o yoksa eski pylib.py yedek yolu. Surum guard'i
//            majou 4 ister. std::string uretim (FIX-23 dersi korunur).
//    FIX-33: PLUSMAXGOD komut ailesi - oyun-ici: stat pos inv equip skill
//            near chat whisper ride revive logout back zoom use pickup drop
//            goto tp key attack | kesif: pyfiles pydump pydumpall pyscan
//            plusquest. Hepsinin pylib karsiligi kanitli API'ler.
//    FIX-34: C:\MaxExec\dump klasoru (py dump + PLUSQuest_live.txt);
//            basedir.txt ile tasinabilir (BASE_DIR\dump).
//    FIX-35: SyncEmbeddedPylib yeni dosya adini yazar (PLUSMAXGOD_PyScript.py),
//            eskisini PLUSMAXGOD_eski_v<surum>.py olarak yedekler.
//  v2.6 (saha testi 16 raporu, pylib v5.0 cifti): DLL kodu ayni (150ms
//         nabiz + kuyruk zaten v2.5'te saglam) - sadece el-sikisma/banner
//         dizgileri v5.0'a gecti. TUM davranis degisiklikleri pylib v5.0'da:
//         slots cok-hucreli esya (GetItemSize), sell/drop kara liste +
//         120sn siniri + flicker korumasi, sellall bitince dukkan otomatik
//         kapanir, autopot otomatik acilis (autopot.txt).
//  v2.5 "PLUSMAXGOD" (saha testi 15 dev raporu, pylib v4.9 cifti):
//     150MS HIZLI NABIZ: DLL artik her 150ms'de maxlib._tick() cagirir
//     (kuyruk taramasi ~1.5sn'de kalir) - autopot/sell/drop/otp donguleri
//     ui penceresi + DLL timer CIFT kalple yurur (dongulerin '1 is sonrasi
//     durma' sorununun kok cozumu). sellall/selljunk/dropall BURST gonderim
//     (45 slot/nabiz - m2k DropAllItems/Taubuyer NightTown kaniti; v4.8'in
//     0.4-0.45sn beklemeleri kaldirildi). autopot KRITIK mod (%50 alti
//     0.15sn) + format-bug fix ('TypeError: not enough arguments').
//     otp2 ISINLANA-ISINLANA + ADIM (SetPixelPosition + MoveToDestPosition
//     + 1-kare UP + SendCharacterPositionPacket - darealfreak kaniti).
//     otp delay/step/stop alt-komutlari ('otp delay 1' ValueError fix).
//  v2.4 "PLUSMAXGOD" (saha testi 14 dev raporu, pylib v4.8 cifti):
//     (1) LIVE tailer acilista eski live.txt'yi konsola geri oynatiyordu
//         -> ilk okuma artik dosya sonundan baslar (sadece yeni satirlar).
//     (2) KALDIRILDI: speed/aspeed (sunucu tanimiyor) + chchange/relogin
//         (karakteri degistirmisti; sonra detayli yeniden yapilacak).
//     (3) YENI: slots/selljunk/sellall/dropall (envanter yonetimi),
//         autopot hp/mp + autopot_item (oto-pot esyasi), otp1/otp2,
//         warp = Legendy yolu (background.WarpTest - sahne yeniden yuklenir).
//  v2.2 "PLUSMAXGOD" (saha testi 12 dev raporu, pylib v4.6 cifti):
//     9 yeni komut: warp (otp adim + SendCharacterPositionPacket),
//     antistun, antislow (AFFECT temizleme donguleri), autopot
//     (27001-3/27004-6 vnum kanitli), combo (surekli vurus),
//     statdown (/stat-), skillupui/statupui (oyunun kendi UI
//     fonksiyonlari), efsun (bonus efsun okuma).
//     pylib v4.6: near tip-filtresi kalkti (METIN tasi tip=2
//     artik bulunur - kagb-multihack kaniti), speed/aspeed 0.5sn
//     dongu (Crap_Levelbot), antifly saldirisiz modlar, chchange
//     stream.SetLoginPhase (networkModule oyun yolu).
//  v2.1 "PLUSMAXGOD" (saha testi 11 - kok-neden onarimi, pylib v4.5 cifti):
//     (1) KOK NEDEN: v4.4 pylib ICINDE sinif tabani (ui_WindowBase)
//         tanimindan ONCE kullanildigi icin import aninda NameError
//         yiyip HIC yuklenemiyordu -> BootImport sessizce eski
//         pylib.py v3.2'ye dusuyordu -> itemscanall/morph/otp/speed/
//         morphtarget/fakemount AttributeError + serverlist eski
//         mesaji + near _my_vid hatasi. pylib v4.5'te tanim yukari
//         tasindi; C++ tarafinda yukseltme denemesi oturum basina 1
//         kez + basarisizlik last_pylib_fail.txt'e traceback yazar.
//     (2) komut seti v2.0 ile ayni (91 maxlib cagrisi, tam kapli).
//  v2.0 "PLUSMAXGOD" (saha testi 10 - GOD MOD paketi v3, pylib v4.4 cifti):
//  v1.9 "PLUSMAXGOD" (saha testi 9 - GOD MOD paketi v2, pylib v4.2 cifti):
//    FIX-36: CANLI CIKTI IZLEYICISI - C:\MaxExec\live.txt'yi 700ms'de bir
//            okuyan ayri thread; yeni satirlar [LIVE] onekiyle konsola akar.
//            fish dongusu + chchange + autotake durumlari boyle canli akar.
//    FIX-37: GOD MOD komut ailesi v2 - ekipman: unequip unequipall |
//            baglanti: chchange relogin (otomatik yeniden giris akisi) |
//            yer esyasi: ground groundtake autotake (textTail.Pick ekran
//            taramasi - pickupstealer kaniti) | gorev: quest |
//            hayalet: fakeitem fakeclear (itemcreator kaniti) |
//            sahte instance: clone unclone spawn morph unmorph setarmor
//            setweapon (introselect MakeCharacter kanit sirasi) |
//            simya: simya ds itemscan (DS envanter + item tablosu) |
//            BALIK: fish fishstop fishdelay fishkeep fishswap fishspot
//            fishstat fishtest (LegendySF fishing.cpp mekanigine gore
//            adaptif gecikme ogrenici + canli oran ekrani)
//    FIX-38: serverlist v2 sonuc dosyasi ayrildi (last_serverlist.txt) -
//            selserver uzeyine basmiyor; ListBar2 textDict okuma yolu.
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
static char DUMP_DIR[MAX_PATH]   = "C:\\MaxExec\\dump";      // FIX-34 (v1.8)
static char ALIVE_FILE[MAX_PATH] = "C:\\MaxExec\\alive.txt";
static char EXEC_LOG[MAX_PATH]   = "C:\\MaxExec\\maxexec.log";
static char PYERR_LOG[MAX_PATH]  = "C:\\MaxExec\\pyerr.log";
static const int     MAX_CMDS_PER_DRAIN = 4;              // tek mesajda maks. komut (render'i sisirmemek icin)

// ---------------------------------------------------------------------------
// v2.0: KONSOL CIKIS KILIDI (saha testi 10: 'konsolda saçma karisik yazi')
// 3 ayri yazar vardi: worker thread (help/prompt), oyun ana thread'i
// (PyRun icinde python print), LiveMonitorThread ([LIVE]) - hepsi kilitsiz
// printf -> help metninin ORTASINA [LIVE]/python satirlari giriyordu.
// COZUM: tum C++ cikislari tek kritik bolumde; python print'leri de
// DrainQueue'da ayni kilitle korunur.
// ---------------------------------------------------------------------------
static CRITICAL_SECTION g_csOut;
static volatile LONG g_csOutInit = 0;

static void OutP(const char* fmt, ...)
{
    char buf[4096];
    va_list ap;
    va_start(ap, fmt);
    _vsnprintf(buf, sizeof(buf) - 1, fmt, ap);
    buf[sizeof(buf) - 1] = 0;
    va_end(ap);
    if (g_csOutInit) EnterCriticalSection(&g_csOut);
    fputs(buf, stdout);
    fflush(stdout);
    if (g_csOutInit) LeaveCriticalSection(&g_csOut);
}

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
static volatile LONG g_nFastTick = 0; // v2.5: maxlib._tick() cagrilari

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
    _snprintf(DUMP_DIR,   MAX_PATH, "%s\\dump",      BASE_DIR);  DUMP_DIR[MAX_PATH-1]=0;
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
            // v2.0: python print'leri cikis kilidinde (diger thread'lerin
            // help/[LIVE] ciktilariyla karismasin); uzun komutta [LIVE] biraz
            // bekler - sadece siralama garanti edilir
            if (g_csOutInit) EnterCriticalSection(&g_csOut);
            int rc = pfn_PyRun_SimpleString(code.c_str());
            if (g_csOutInit) LeaveCriticalSection(&g_csOut);
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
                    "En sik neden: ESKI pylib - PLUSMAXGOD v5.0 ile degistir (bundle zip / GitHub)!\n");
                OutP("[MAXEXEC] !! PYTHON HATASI (%s) - detay icin: pyerr\n", fd.cFileName);
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
// v2.5 HIZLI NABIZ (saha testi 15 kok-onarimi): DLL 150ms'de bir
// maxlib._tick() cagirir - autopot/sell/drop/otp donguleri artik sadece ui
// penceresine degil DLL timer'ina da bagli (cift kalp). hasattr korumasi:
// eski pylib'de _tick yok -> sessiz gecilir (pyfail sayilmaz).
// ---------------------------------------------------------------------------
static void FastTick(void)
{
    if (!pfn_PyRun_SimpleString) return;
    InterlockedIncrement(&g_nFastTick);
    const char* code =
        "try:\n"
        "    import maxlib\n"
        "    if hasattr(maxlib, '_tick'):\n"
        "        maxlib._tick()\n"
        "except Exception:\n"
        "    pass\n";
    if (g_csOutInit) EnterCriticalSection(&g_csOut);
    pfn_PyRun_SimpleString(code);
    if (g_csOutInit) LeaveCriticalSection(&g_csOut);
}

// ---------------------------------------------------------------------------
// TIMER YOLU (FIX-8) — WM_TIMER oyunun kendi mesaj pompasiyla TimerProc'a
// ulasir; WndProc subclass'i geri alinsa bile CALISIR. Ana thread garanti
// (pencerenin sahibi thread = oyun ana thread'i).
// v2.5: 150ms hizli nabiz. Kuyruk tarayici (disk FindFirstFile) her 10.
// nabizda (~1.5sn - eski davranis korunur); aradaki nabizlar pylib._tick.
// ---------------------------------------------------------------------------
static VOID CALLBACK MaxExecTimerProc(HWND hwnd, UINT, UINT_PTR, DWORD)
{
    InterlockedIncrement(&g_nTimer);
    if ((g_nTimer % 10) == 1)
        DrainQueue();   // her ~1.5sn: komut kuyrugu + alive.txt nabzi
    else
        FastTick();     // aradaki ~150ms nabizlar: dongu surusu (v2.5)
}

static void InstallTimer(void)
{
    if (!g_hGameWnd) return;
    UINT_PTR id = SetTimer(g_hGameWnd, TIMER_ID_MAXEXEC, 150, MaxExecTimerProc);
    LogLine("SetTimer: %s (id=%lu, 150ms hizli nabiz - v2.5)", id ? "KURULDU" : "BASARISIZ", (unsigned long)id);
    OutP("ana-thread timer: %s (150ms hizli nabiz + 1.5sn kuyruk - v2.6)\n", id ? "KURULDU" : "BASARISIZ");
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
    if (EnqueueCommand(code, f)) OutP("[MAXEXEC] kuyruga yazildi: %s\n", f.c_str());
    else OutP("[MAXEXEC] HATA: kuyruga yazilamadi\n");
    if (g_hGameWnd) PostMessage(g_hGameWnd, WM_APP_MAXEXEC, 0, 0);
}

// ---------------------------------------------------------------------------
// FIX-15: kendini onaran import + FIX-32 (v1.8): SURUM-ONGOER bootstrap.
// Eski maxlib (v3.x) yuklu ise diskteki PLUSMAXGOD_PyScript.py ile YERINDE
// exec edilir (yukseiltme - kullanici hicbir sey yapmaz); o dosya yoksa
// eski pylib.py denenir (yine de calisir ama guard KOSKOCA uyari basar).
// NOT (FIX-23 dersi): metin std::string ile uretilir - tampon kesmesi
// imkansiz. Cagiranlar: QRaw(BootImport() + "maxlib.xxx(...)")
// ---------------------------------------------------------------------------
static std::string BootImport(void)
{
    // v2.1 (saha testi 11 kok-neden onarimi):
    //  (a) yukseltme denemesi OTURUM BASINA 1 KEZ - v2.0'ta her komutta
    //      yeniden deniyordu; kirik pylib durumunda her komutta banner
    //      tekrari + konsol karisikligi oluyordu.
    //  (b) yukseltme BASARISIZSA artik results\last_pylib_fail.txt'e TAM
    //      TRACEBACK yazilir - v4.4'teki sessiz dusus (ui_WindowBase sira
    //      hatasi -> pylib.py v3.2'ye dusus) tespit edilemiyordu.
    //  (c) son care pylib.py v3.2 yedek yolu korunur.
    std::string s;
    s += "try:\n"
         "    import maxlib\n"
         "    _mxv = int(str(getattr(maxlib, 'PYLIB_VERSION', '0')).split('.')[0])\n"
         "except Exception:\n"
         "    _mxv = 0\n";
    s += "if _mxv < 4 and not globals().get('_MX_UPGRADE_TRIED', False):\n"
         "    globals()['_MX_UPGRADE_TRIED'] = True\n"
         "    try:\n"
         "        exec(open(r'" + std::string(BASE_DIR) + "\\\\PLUSMAXGOD_PyScript.py').read())\n"
         "    except Exception:\n"
         "        try:\n"
         "            import traceback\n"
         "            _f = open(r'" + std::string(RESULT_DIR) + "\\\\last_pylib_fail.txt', 'w')\n"
         "            _f.write('PLUSMAXGOD_PyScript.py YUKLENEMEDI (DLL v2.6 / pylib v5.0) - TRACEBACK:\\n' + traceback.format_exc())\n"
         "            _f.close()\n"
         "        except Exception:\n"
         "            pass\n"
         "        try:\n"
         "            exec(open(r'" + std::string(BASE_DIR) + "\\\\pylib.py').read())\n"
         "        except Exception:\n"
         "            pass\n";
    s += "import maxlib\n"
         "try:\n"
         "    _mxv = int(str(getattr(maxlib, 'PYLIB_VERSION', '0')).split('.')[0])\n"
         "except Exception:\n"
         "    _mxv = 0\n"
         "if _mxv < 4 and not getattr(maxlib, '_MX_OLD_WARNED', False):\n"
         "    maxlib._MX_OLD_WARNED = True\n"
         "    try:\n"
         "        import sys\n"
         "        sys.stderr.write('!!! PYLIB ESKI v' + str(getattr(maxlib, 'PYLIB_VERSION', '?')) + ' - DLL v2.6 PLUSMAXGOD v5.0 ister! "
         "C:\\\\MaxExec\\\\PLUSMAXGOD_PyScript.py dosyasini yenisiyle degistir (bundle zip / GitHub) !!!\\\\n')\n"
         "    except Exception:\n"
         "        pass\n";
    return s;
}

// FIX-33 (v1.8): guvenli python dizgi-literal uretici (chat/whisper/pyscan
// icin - kullanici girdisinde tirnak/backslash/newline olabilir). Raw string
// DEGIL normal tek-tirnak literal: kacis kurallari tam uygulanir.
static std::string PyStr(const std::string& in)
{
    std::string o = "'";
    for (size_t i = 0; i < in.size(); ++i)
    {
        unsigned char c = (unsigned char)in[i];
        switch (c)
        {
            case '\\': o += "\\\\"; break;
            case '\'': o += "\\'";  break;
            case '\n': o += "\\n";  break;
            case '\r': o += "\\r";  break;
            case '\t': o += "\\t";  break;
            default:   o += (char)c; break;
        }
    }
    o += "'";
    return o;
}

static std::string JoinArgs(const std::vector<std::string>& a, size_t from)
{
    std::string o;
    for (size_t i = from; i < a.size(); ++i)
    {
        if (i > from) o += " ";
        o += a[i];
    }
    return o;
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
        OutP("[MAXEXEC] HATA: dosya YOK: %s\n", path.c_str());
        OutP("    pylib.py'yi su klasore kopyala: %s\n", BASE_DIR);
        OutP("    (bundle zip icinde var; v1.3 otomatik yukler)\n");
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
    OutP("[MAXEXEC] pylib yukleme komutu kuyruga alindi (kurulum ana thread'de olur)\n");
    OutP("[MAXEXEC] Python hatalari icin: %s\n", PYERR_LOG);
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
        OutP("[LASTERR] oyun hatalari (sonlar en altta):\n");
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
            OutP("  %s\n", lines[i].c_str());
        if (lines.empty()) OutP("  (bos - henuz oyun hatasi yaklanmadi)\n");
    }
    else
        OutP("[LASTERR] last_error.txt yok - henuz oyun hatasi yaklanmadi\n");
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

// ---------------------------------------------------------------------------
// FIX-33 (v1.8): PLUSMAXGOD komut ailesi ureticileri - oyun-ici + kesif.
// Her biri BootImport() + tek satir maxlib cagrisi (FIX-23 std::string).
// ---------------------------------------------------------------------------
static void CmdStat(void)   { QRaw(BootImport() + "maxlib.stat()\n"); }
static void CmdPos(void)    { QRaw(BootImport() + "maxlib.pos()\n"); }
static void CmdEquip(void)  { QRaw(BootImport() + "maxlib.equip()\n"); }
static void CmdSkill(void)  { QRaw(BootImport() + "maxlib.skill()\n"); }
static void CmdNear(const std::string& q) { QRaw(BootImport() + "maxlib.near(" + PyStr(q) + ")\n"); }
static void CmdRide(void)   { QRaw(BootImport() + "maxlib.ride()\n"); }
static void CmdRevive(void) { QRaw(BootImport() + "maxlib.revive()\n"); }
static void CmdLogout(void) { QRaw(BootImport() + "maxlib.logout()\n"); }
static void CmdBack(void)   { QRaw(BootImport() + "maxlib.back()\n"); }
static void CmdPickup(void) { QRaw(BootImport() + "maxlib.pickup()\n"); }
static void CmdPyFiles(void)   { QRaw(BootImport() + "maxlib.pyfiles()\n"); }
static void CmdPyDumpAll(void) { QRaw(BootImport() + "maxlib.pydumpall()\n"); }
static void CmdPlusQuest(void) { QRaw(BootImport() + "maxlib.plusquest()\n"); }

static void CmdChat(const std::string& msg)
{
    QRaw(BootImport() + "maxlib.chat(" + PyStr(msg) + ")\n");
}

static void CmdWhisper(const std::string& who, const std::string& msg)
{
    QRaw(BootImport() + "maxlib.whisper(" + PyStr(who) + ", " + PyStr(msg) + ")\n");
}

static void CmdZoom(int dist)
{
    char call[64];
    _snprintf(call, sizeof(call), "maxlib.zoom(%d)\n", dist);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdUse(int slot)
{
    char call[64];
    _snprintf(call, sizeof(call), "maxlib.use(%d)\n", slot);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdDrop(int slot, int count)
{
    char call[80];
    _snprintf(call, sizeof(call), "maxlib.drop(%d, %d)\n", slot, count);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdGoto(int x, int y)
{
    char call[80];
    _snprintf(call, sizeof(call), "maxlib.goto(%d, %d)\n", x, y);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdTp(int x, int y)
{
    char call[80];
    _snprintf(call, sizeof(call), "maxlib.tp(%d, %d)\n", x, y);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdKey(const std::string& dik, const std::string& down)
{
    QRaw(BootImport() + "maxlib.key(" + PyStr(dik) + ", " + PyStr(down) + ")\n");
}

static void CmdAttack(const std::string& mode)
{
    QRaw(BootImport() + "maxlib.attack(" + PyStr(mode) + ")\n");
}

// ---------------------------------------------------------------------------
// FIX-37 (v1.9): GOD MOD komut ailesi v2 (pylib v4.2 karsiliklari)
// ---------------------------------------------------------------------------
static void CmdUnequip(const std::string& part)
{
    QRaw(BootImport() + "maxlib.unequip(" + PyStr(part) + ")\n");
}
static void CmdUnequipAll(void) { QRaw(BootImport() + "maxlib.unequipall()\n"); }
// (v2.4) chchange/relogin KALDIRILDI - kullanici istegi (karakteri
// degistirmisti; sonra detaylica yeniden yapilacak)
static void CmdGround(void)  { QRaw(BootImport() + "maxlib.ground()\n"); }
static void CmdGroundTake(const std::string& mode)
{
    QRaw(BootImport() + "maxlib.groundtake(" + PyStr(mode) + ")\n");
}
static void CmdAutoTake(const std::string& flag)
{
    QRaw(BootImport() + "maxlib.autotake(" + PyStr(flag) + ")\n");
}
static void CmdQuest(void)   { QRaw(BootImport() + "maxlib.quest()\n"); }
static void CmdFakeItem(const std::string& vnum, const std::string& count)
{
    QRaw(BootImport() + "maxlib.fakeitem(" + PyStr(vnum) + ", " + PyStr(count) + ")\n");
}
static void CmdFakeClear(const std::string& mode)
{
    QRaw(BootImport() + "maxlib.fakeclear(" + PyStr(mode) + ")\n");
}
static void CmdClone(const std::string& off, const std::string& hair)
{
    QRaw(BootImport() + "maxlib.clone(" + PyStr(off) + ", " + PyStr(hair) + ")\n");
}
static void CmdUnClone(const std::string& mode)
{
    QRaw(BootImport() + "maxlib.unclone(" + PyStr(mode) + ")\n");
}
static void CmdSpawn(const std::string& race, const std::string& name)
{
    QRaw(BootImport() + "maxlib.spawn(" + PyStr(race) + ", " + PyStr(name) + ")\n");
}
static void CmdMorph(const std::string& race)
{
    QRaw(BootImport() + "maxlib.morph(" + PyStr(race) + ")\n");
}
static void CmdUnMorph(void) { QRaw(BootImport() + "maxlib.unmorph()\n"); }
static void CmdSetArmor(const std::string& vnum)
{
    QRaw(BootImport() + "maxlib.setarmor(" + PyStr(vnum) + ")\n");
}
static void CmdSetWeapon(const std::string& vnum)
{
    QRaw(BootImport() + "maxlib.setweapon(" + PyStr(vnum) + ")\n");
}
static void CmdSimya(void)   { QRaw(BootImport() + "maxlib.simya()\n"); }
static void CmdItemScan(const std::string& mn, const std::string& mx)
{
    QRaw(BootImport() + "maxlib.itemscan(" + PyStr(mn) + ", " + PyStr(mx) + ")\n");
}
static void CmdFish(void)        { QRaw(BootImport() + "maxlib.fish()\n"); }
static void CmdFishStop(void)    { QRaw(BootImport() + "maxlib.fishstop()\n"); }
static void CmdFishKeep(const std::string& v)  { QRaw(BootImport() + "maxlib.fishkeep(" + PyStr(v) + ")\n"); }
static void CmdFishSpot(const std::string& x, const std::string& y)
{
    QRaw(BootImport() + "maxlib.fishspot(" + PyStr(x) + ", " + PyStr(y) + ")\n");
}
static void CmdFishStat(void)    { QRaw(BootImport() + "maxlib.fishstat()\n"); }
static void CmdFishTest(void)    { QRaw(BootImport() + "maxlib.fishtest()\n"); }
// --- v2.0 (pylib v4.4): yeni komut ureticileri ---
static void CmdMorphTarget(void)   { QRaw(BootImport() + "maxlib.morphtarget()\n"); }
static void CmdClonePlayer(void)   { QRaw(BootImport() + "maxlib.cloneplayer()\n"); }
static void CmdFakeMount(const std::string& m) { QRaw(BootImport() + "maxlib.fakemount(" + PyStr(m) + ")\n"); }
// (v2.4) speed/aspeed KALDIRILDI - sunucu chr.SetMoveSpeed/
// SetAttackSpeed tanimiyordu (kullanici istegiyle silindi)
static void CmdStatUp(const std::string& p, const std::string& n)  { QRaw(BootImport() + "maxlib.statup(" + PyStr(p) + ", " + PyStr(n) + ")\n"); }
static void CmdSkillUp(const std::string& i, const std::string& n) { QRaw(BootImport() + "maxlib.skillup(" + PyStr(i) + ", " + PyStr(n) + ")\n"); }
static void CmdAntiFly(const std::string& m)   { QRaw(BootImport() + "maxlib.antifly(" + PyStr(m) + ")\n"); }
static void CmdAntiFlyEffect(const std::string& m) { QRaw(BootImport() + "maxlib.antiflyeffect(" + PyStr(m) + ")\n"); }
// --- v2.2 (pylib v4.6): saha testi 12 komutlari ---
static void CmdWarp(const std::string& x, const std::string& y) { QRaw(BootImport() + "maxlib.warp(" + PyStr(x) + ", " + PyStr(y) + ")\n"); }
static void CmdAntiStun(const std::string& m)   { QRaw(BootImport() + "maxlib.antistun(" + PyStr(m) + ")\n"); }
static void CmdAntiSlow(const std::string& m)   { QRaw(BootImport() + "maxlib.antislow(" + PyStr(m) + ")\n"); }
// --- v2.4 (pylib v4.8): saha testi 13+14 komutlari ---
static void CmdSlots(void)                       { QRaw(BootImport() + "maxlib.slots()\n"); }
static void CmdSellJunk(const std::string& sub)  { QRaw(BootImport() + "maxlib.selljunk(" + PyStr(sub) + ")\n"); }
static void CmdSellAll(const std::string& f)     { QRaw(BootImport() + "maxlib.sellall(" + PyStr(f) + ")\n"); }
static void CmdDropAll(const std::string& sub)   { QRaw(BootImport() + "maxlib.dropall(" + PyStr(sub) + ")\n"); }
static void CmdAutoPot(const std::string& arg, const std::string& pct)
                                                { QRaw(BootImport() + "maxlib.autopot(" + PyStr(arg) + ", " + PyStr(pct) + ")\n"); }
static void CmdAutoPotItem(const std::string& k) { QRaw(BootImport() + "maxlib.autopot_item(" + PyStr(k) + ")\n"); }
static void CmdCombo(const std::string& n)      { QRaw(BootImport() + "maxlib.combo(" + PyStr(n) + ")\n"); }
static void CmdStatDown(const std::string& p, const std::string& n)  { QRaw(BootImport() + "maxlib.statdown(" + PyStr(p) + ", " + PyStr(n) + ")\n"); }
static void CmdSkillUpUI(const std::string& s) { QRaw(BootImport() + "maxlib.skillupui(" + PyStr(s) + ")\n"); }
static void CmdStatUpUI(const std::string& p)  { QRaw(BootImport() + "maxlib.statupui(" + PyStr(p) + ")\n"); }
static void CmdEfsun(const std::string& s)     { QRaw(BootImport() + "maxlib.efsun(" + PyStr(s) + ")\n"); }
static void CmdItemFind(const std::string& w)  { QRaw(BootImport() + "maxlib.itemfind(" + PyStr(w) + ")\n"); }
static void CmdItemInfo(const std::string& v)  { QRaw(BootImport() + "maxlib.iteminfo(" + PyStr(v) + ")\n"); }
static void CmdAttr(const std::string& s)      { QRaw(BootImport() + "maxlib.attr(" + PyStr(s) + ")\n"); }
static void CmdAttrAll(void)     { QRaw(BootImport() + "maxlib.attrall()\n"); }
static void CmdUseOn(const std::string& s, const std::string& d) { QRaw(BootImport() + "maxlib.useon(" + PyStr(s) + ", " + PyStr(d) + ")\n"); }
static void CmdEfsunSw(const std::string& d)   { QRaw(BootImport() + "maxlib.efsunsw(" + PyStr(d) + ")\n"); }
static void CmdGoTake(const std::string& m)    { QRaw(BootImport() + "maxlib.gotake(" + PyStr(m) + ")\n"); }
static void CmdCanli(const std::string& msg)
{
    QRaw(BootImport() + "maxlib.canli(" + PyStr(msg) + ")\n");
}
// ---- v1.9 (pylib v4.3): fishtp + fishswapnow + OTP + clonemod + spawnscan + itemscanall ----
static void CmdOTP1(const std::string& x, const std::string& y)
{
    QRaw(BootImport() + "maxlib.otp1(" + PyStr(x) + ", " + PyStr(y) + ")\n");
}
static void CmdOTP2(const std::string& x, const std::string& y)
{
    QRaw(BootImport() + "maxlib.otp2(" + PyStr(x) + ", " + PyStr(y) + ")\n");
}
static void CmdOTPStop(void)     { QRaw(BootImport() + "maxlib.otpstop()\n"); }
static void CmdOTPStep(const std::string& v)  { QRaw(BootImport() + "maxlib.otpstep(" + PyStr(v) + ")\n"); }
static void CmdOTPDelay(const std::string& v) { QRaw(BootImport() + "maxlib.otpdelay(" + PyStr(v) + ")\n"); }
static void CmdCloneMod(const std::string& mode) { QRaw(BootImport() + "maxlib.clonemod(" + PyStr(mode) + ")\n"); }
static void CmdSpawnScan(const std::string& a, const std::string& b)
{
    QRaw(BootImport() + "maxlib.spawnscan(" + PyStr(a) + ", " + PyStr(b) + ")\n");
}
static void CmdItemScanAll(void) { QRaw(BootImport() + "maxlib.itemscanall()\n"); }

static void CmdInv(int page)
{
    char call[64];
    _snprintf(call, sizeof(call), "maxlib.inv(%d)\n", page);
    call[sizeof(call)-1] = 0;
    QRaw(BootImport() + call);
}

static void CmdPyDump(const std::string& name)
{
    QRaw(BootImport() + "maxlib.pydump(" + PyStr(name) + ")\n");
}

static void CmdPyScan(const std::string& mod)
{
    QRaw(BootImport() + "maxlib.pyscan(" + PyStr(mod) + ")\n");
}

// C++ TARAFINDA bekler; Python'u kisa patlamalarda calistirir (ana thread dostu)
static void CmdWaitFor(const std::string& sceneName, int seconds)
{
    if (!g_hGameWnd) { OutP("[MAXEXEC] oyun penceresi yok\n"); return; }
    OutP("[MAXEXEC] %s bekleniyor (%d sn)...\n", sceneName.c_str(), seconds);
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
                OutP("[MAXEXEC] ULASILDI: %s\n", sceneName.c_str());
                OutP("%s", s.c_str());
                return;
            }
        }
    }
    OutP("[MAXEXEC] TIMEOUT: %s (ipucu: status + pyerr komutlarina bak)\n", sceneName.c_str());
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
    SetConsoleTitleA("MaxExecutor v2.6 PLUSMAXGOD");
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
// FIX-36 (v1.9): CANLI CIKTI IZLEYICISI - pylib v4.2 durum akislari (fish/
// chchange/autotake) C:\MaxExec\live.txt'ye yazar; bu thread yeni satirlari
// [LIVE] onekiyle konsola basar. Dosya kuculurse (truncate) bastan okur.
// ---------------------------------------------------------------------------
static DWORD g_liveOffset = 0;
static bool  g_liveFirst  = true;   // v2.3: acilistaki eski icerigi atla
static DWORD WINAPI LiveMonitorThread(LPVOID)
{
    std::string path = std::string(BASE_DIR) + "\\live.txt";
    Sleep(3000);
    while (true)
    {
        HANDLE h = CreateFileA(path.c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE,
                               NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (h != INVALID_HANDLE_VALUE)
        {
            DWORD size = GetFileSize(h, NULL);
            if (size == INVALID_FILE_SIZE) size = 0;
            if (g_liveFirst && size > 0)             // v2.3 FIX: DLL her
            {                                        // acilisinda eski [LIVE]
                g_liveFirst = false;                 // satirlar konsola geri
                g_liveOffset = size;                 // OYNANIYORDU - artik
            }                                        // sadece yeniler akar
            if (size < g_liveOffset)
                g_liveOffset = 0;                    // truncate: bastan oku
            if (size > g_liveOffset)
            {
                DWORD want = size - g_liveOffset;
                if (want > 16384) { g_liveOffset = size - 16384; want = 16384; }
                static char buf[16386];
                DWORD got = 0;
                LONG hi = 0;
                SetFilePointer(h, (LONG)g_liveOffset, &hi, FILE_BEGIN);
                if (ReadFile(h, buf, want, &got, NULL) && got > 0)
                {
                    buf[got] = 0;
                    DWORD consumed = 0;
                    char* p = buf;
                    while (true)
                    {
                        char* nl = strchr(p, '\n');
                        if (!nl) break;
                        *nl = 0;
                        if (nl > p && nl[-1] == '\r') nl[-1] = 0;
                        OutP("[LIVE] %s\n", p);
                        // \r satir icinde 0'landi ama byte olarak tuketildi
                        consumed += (DWORD)(nl - p) + 1;
                        p = nl + 1;
                        if (p >= buf + got) break;
                    }
                    g_liveOffset += consumed;
                }
            }
            CloseHandle(h);
        }
        else
        {
            g_liveOffset = 0;
        }
        Sleep(700);
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
    OutP("\n=== MaxExecutor v2.6 PLUSMAXGOD (oyun-ici + GOD MOD pylib v5.0) ===\n");
    OutP("  help                        : bu yardim\n");
    OutP("  status                      : anlik sahne/baglanti snapshot\n");
    OutP("  -- giris akisi (menu) --\n");
    OutP("  serverlist                  : server/CH listbox icerigi\n");
    OutP("  selserver <srv> <ch>        : server+CH sec, OK'a bas\n");
    OutP("  login <id> <pwd>            : login ekraninda UI doldurur + giris\n");
    OutP("  charlist                    : 5 slot tablosunu doken rapor\n");
    OutP("  selchar <slot>              : karakter slotu SEC (0-4)\n");
    OutP("  enter <slot>                : oyuna giris - UI START yolu (DirectEnter yedek)\n");
    OutP("  newchar | empirelist | empireui <1-3> | joblist | mkchar <ad> <race>\n");
    OutP("  delchar <slot> | delcode <kod>\n");
    OutP("  -- OYUN-ICI --\n");
    OutP("  stat | pos | inv <sayfa> | equip | skill : raporlar\n");
    OutP("  near [vid-siniri]           : GENIS varlik taramasi (v4.4: anlik 1..50000\n");
    OutP("                                + arka plan 4M tarama -> near_full.txt)\n");
    OutP("  chat <mesaj> | cmd <slash> | whisper <kim> <mesaj> : sohbet\n");
    OutP("  ride | revive | logout | back | pickup : hizli eylemler\n");
    OutP("  zoom <mesafe> | use <slot> | drop <slot> <adet> | goto <x> <y> | tp <x> <y>\n");
    OutP("  key <DIK> <0/1> | attack <0/1>\n");
    OutP("  -- v5.0: SAHA TESTI 16 DUZELTMELERI --\n");
    OutP("  slots                      : v5.0 COK-HUCRELI esya sayimi (kilic 1x3, zirh 2x3 -\n");
    OutP("                                oyunun gostergesiyle AYNI bos slot; harita 5 kolon)\n");
    OutP("  selljunk/sellall           : v5.0 kara liste (2 turda satilmayan bir daha\n");
    OutP("                                denenmez, isim listesi raporlanir) + 120sn siniri\n");
    OutP("                                + flicker korumasi + bitince dukkan KAPANIR\n");
    OutP("  dropall                    : v5.0 ayni tedavi + ATILAMAYAN esya isim listesi\n");
    OutP("                                (sunucu yavaysa esyalar sonra tek tek duser)\n");
    OutP("  autopot                    : v5.0 OTOMATIK ACILIR - C:\\MaxExec\\autopot.txt\n");
    OutP("                                (varsayilan hp 80; kapatmak: dosyaya off / autopot 0)\n");
    OutP("  -- v4.9: SAHA TESTI 15 DUZELTMELERI --\n");
    OutP("  sellall/selljunk/dropall      : BURST gonderim (45 slot/nabiz - m2k kaniti)\n");
    OutP("  autopot hp/mp <pct>           : KRITIK mod - %50 alti 0.15sn arayla pot\n");
    OutP("  otp2 <x> <y>                  : ISINLANA-ISINLANA + ADIM (sendcharacterstate)\n");
    OutP("  otp delay <ms> | otp step <px> | otp stop : alt-komutlar (v2.5)\n");
    OutP("  DLL 150ms hizli nabiz: maxlib._tick() - donguler cift kalple yurur\n");
    OutP("  slots                       : envanter ozeti + SLOT HARITASI (#=esya .=bos E=efsunlu)\n");
    OutP("  selljunk                    : v4.9 BURST - COP esyalari NPC'ye sat (efsunlu ASLA satilmaz)\n");
    OutP("       dukkan acilir acilmaz otomatik satar (acilmazsa NPCye kendin tikla)\n");
    OutP("       selljunk 0 = DURDUR | selljunk add <vnum> | del <vnum> | list | name <isim>\n");
    OutP("  sellall [force]             : v4.9 BURST - TUM envanteri sat (force: efsunlu dahil!) | DUR: sellall 0\n");
    OutP("  warp <x> <y>                : v4.7 - LEGENDY warp (sahne YENIDEN yuklenir!)\n");
    OutP("                                x,y = pos/100 (orn 38421 39017 -> warp 384 390)\n");
    OutP("  autopot hp 80 | autopot mp 80 | autopot (durum) | autopot 0\n");
    OutP("       SUREKLI izleme: esik altindayken 0.4sn'de bir pot, esige dek\n");
    OutP("       KRITIK mod: %50 altinda 0.15sn arayla | 30sn kalp atisi | DUR: autopot 0\n");
    OutP("  autopot_item hp | autopot_item mp | autopot_item 0\n");
    OutP("       oto-pot ESYASI (72723-6/72727-30): pasifse basar, bitince yeniler\n");
    OutP("  otp1 <x> <y>                : v4.9 - saldiri tusu adim-adim (kanitli)\n");
    OutP("  otp2 <x> <y>                : v4.9 - ISINLANA-ISINLANA + ADIM (geri atma yok)\n");
    OutP("  dropall                     : v4.9 BURST - tum envanteri YERE AT (45 slot/nabiz) | DUR: dropall 0\n");
    OutP("  -- v4.4: PUAN + HIZ + BINIS + ANTIFLY --\n");
    OutP("  statup <ht|iq|st|dx> [adet] : stat puani ver (orn: statup st 10)\n");
    OutP("  skillup <skill-idx> [adet]  : skill puani ver (idx: skill raporundan)\n");
    OutP("  fakemount <0/1>             : SAHTE at binisi - at ustunde gorunursun ama\n");
    OutP("                                sunucu binmemis sayar: skill SERBEST\n");
    OutP("  antifly <0/1/2/3>           : itilme engeli (1=kilit, 2=+Guclu Beden, 3=orijinal)\n");
    OutP("  antiflyeffect <id>          : efekt yontemi (chrmgr.SetAffect)\n");
    OutP("  -- GOD MOD v2: EKIPMAN + BAGLANTI --\n");
    OutP("  unequip <parca|slot> | unequipall\n");
    OutP("  -- GOD MOD v2: YER ESYASI + GOREV --\n");
    OutP("  ground | groundtake [all|vid] | autotake <0/1> | quest\n");
    OutP("  gotake <vid|all>            : v4.4 - esyaya YURU + TOPLA (yakinlasip alir)\n");
    OutP("  -- GOD MOD v2: HAYALET + SAHTE INSTANCE (istemci tarafi!) --\n");
    OutP("  fakeitem <vnum> [adet] | fakeclear [slot|all]\n");
    OutP("  clone [offset] [sac]        : klon (v4.4: Z-fix + SAC otomatik okunur)\n");
    OutP("  unclone [all|vid]\n");
    OutP("  spawn <race> [ad]           : sahte NPC (v4.4: z-fix + konum dogrulama + gorsel tazeleme)\n");
    OutP("  morph <race> | unmorph      : gorunum (v4.4: gorsel tazeleme - zirh takip cikma YOK)\n");
    OutP("  morphtarget                 : v4.4 - HEDEF NPC/mob/OYUNCU'ya donus (once tikla)\n");
    OutP("  cloneplayer                 : v4.4 - hedef OYUNCUYA donus (irk+ad)\n");
    OutP("  setarmor <vnum> | setweapon <vnum> | clonemod <swap|1|0>\n");
    OutP("  spawnscan [min] [max]       : mob_proto race taramasi\n");
    OutP("  -- GOD MOD v2: SIMYA + ESYA KESIF + EFSUN --\n");
    OutP("  simya | ds                  : DS envanter raporu\n");
    OutP("  itemscan <min> <max>        : item tablo taramasi\n");
    OutP("  itemscanall                 : TUM item taramasi 1-99999 (v4.4: 50k parcasi FIX)\n");
    OutP("  itemfind <kelime>           : v4.4 - isimle ara (itemfind simya | itemfind kostum)\n");
    OutP("  iteminfo <vnum>             : v4.4 - esyanin TAM proto bilgisi\n");
    OutP("  attr <slot> | attrall       : v4.4 - EFSUNLARI oku (efsunlu mu, ne efsunlu)\n");
    OutP("  useon <src> <dst>           : v4.4 - esyayi esya uzerinde kullan\n");
    OutP("                                (efsun ekle/degistir/5.attr/kostum efsunu)\n");
    OutP("  efsunsw <esya-slot>         : v4.4 - efsun kagidini bul + uygula\n");
    OutP("  -- GOD MOD v2: BALIK --\n");
    OutP("  fish | fishstop             : otomatik balik dongusu / durdur\n");
    OutP("  fishkeep <vnum|0>           : sadece hedef baligi tut\n");
    OutP("  fishspot <x> <y>|0          : su-noktasi modu (atis aninda suya, sonra geri)\n");
    OutP("  fishstat | fishtest | canli <mesaj>\n");
    OutP("  (v4.4 not: fishdelay/fishswap/fishswapnow/fishtp KALDIRILDI;\n"
         "   v4.5 not: pylib yukleme sira hatasi duzeltildi;\n"
         "   v4.6 not: near artik METIN taslarini bulur | antifly saldirisiz;\n"
         "   v4.7 not: speed/aspeed/chchange/relogin KALDIRILDI | warp Legendy\n"
         "            yolu | dump: C modul API stub + pack.Get sysmodules;\n"
         "   v4.8 not: autopot surekli | otp2 W-basili | slots sayim fix |\n"
         "            selljunk/sellall/dropall 1-arg paket + stop (selljunk 0);\n"
         "   v5.0 not: slots cok-hucreli | sell/drop kara liste + 120sn + dukkan kapanir |\n"
         "   autopot otomatik (autopot.txt) | v4.9: sell/drop BURST | otp2 isinlana+adim |\n"
         "            DLL 150ms nabiz | otp delay/step alt-komut)\n");
    OutP("  -- KESIF --\n");
    OutP("  pyfiles | pydump <ad> | pydumpall | pyscan <modul> | plusquest\n");
    OutP("  -- hata takibi --\n");
    OutP("  lasterr | pyerr | log | load <py> | raw <kod> | waitfor <Scene> <sn> | exit\n");
    OutP("GIRIS: status -> selserver 0 0 -> login <id> <pwd> -> charlist -> selchar 0 -> enter 0\n");
    OutP("BALIK: fishtest -> /i 27400 (olta) + /i 27801 200 (solucan) -> fish -> [LIVE] izle\n");
    OutP("  uzaktan: goto <su kenari> -> fishspot <x> <y> -> fish\n");
    OutP("ENVANTER: slots -> selljunk (cop sat) -> sellall (hepsi) -> dropall (yere at)\n");
    OutP("OTPOT: autopot hp 80 + autopot mp 80 + autopot_item hp (oto-pot esyasi 72724)\n");
    OutP("Saglik: %s | oyun hatalari: results\\last_error.txt\n", ALIVE_FILE);
    OutP("dump klasoru: %s | plusquest cikti: %s\\PLUSQuest_live.txt\n\n", DUMP_DIR, DUMP_DIR);
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
    _snprintf(pylibPath, MAX_PATH, "%s\\PLUSMAXGOD_PyScript.py", BASE_DIR); pylibPath[MAX_PATH-1]=0;
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
        _snprintf(bak, MAX_PATH, "%s\\PLUSMAXGOD_eski_v%s.py", BASE_DIR,
                  diskVer[0] ? diskVer : "2x"); bak[MAX_PATH-1]=0;
        if (CopyFileA(pylibPath, bak, FALSE))
            LogLine("pylib sync: eski dosya yedeklendi -> %s", bak);
    }
    std::string emb((const char*)EMBEDDED_PYLIB_DATA, EMBEDDED_PYLIB_SIZE);
    if (WriteFileAll(pylibPath, emb))
    {
        LogLine("pylib sync: gomulu PLUSMAXGOD v%s diske yazildi (eskisi: %s)",
                EMBEDDED_PYLIB_VERSION, hasDisk ? diskVer : "yok");
        OutP("PLUSMAXGOD_PyScript.py : GUNCELLENDI -> v%s (DLL icinden yazildi%s)\n",
               EMBEDDED_PYLIB_VERSION,
               hasDisk ? ", eski dosya PLUSMAXGOD_eski_*.py olarak yedeklendi" : "");
    }
    else
    {
        LogLine("pylib sync HATA: %s yazilamadi", pylibPath);
        OutP("PLUSMAXGOD_PyScript.py : GUNCELLENEMEDI (yazma hatasi!) - elle kopyala\n");
    }
}

static DWORD WINAPI WorkerThread(LPVOID)
{
    InitializeCriticalSection(&g_csOut);          // v2.0: cikis kilidi
    InterlockedExchange(&g_csOutInit, 1);
    InitPaths();                                  // FIX-12: basedir.txt (D:\ destegi)
    LogLine("worker thread basladi (base=%s)", BASE_DIR);
    EnsureDirs();
    const bool con = InitConsole();

    OutP("\n=============================================\n");
    OutP("  MaxExecutor v2.6 PLUSMAXGOD - ana-thread executor\n");
    OutP("  oyun-ici + kesif + GOD MOD v2 (pylib v5.0 cifti)\n");
    OutP("  canli cikti: C:\\MaxExec\\live.txt izlenir -> [LIVE] akar\n");
    OutP("=============================================\n");
    if (!con)
        OutP("[!] KONSOL ACILAMADI (headless). Komutlari %s\\queue klasorune\n"
               "    elle .cmd dosyasi olarak birak - 2 sn icinde otomatik islenir.\n", BASE_DIR);
    for (int i = 0; i < 40 && !ResolvePython(); ++i) Sleep(500);
    LogLine("python27: %s (Py_IsInitialized=%d)",
            pfn_PyRun_SimpleString ? "BULUNDU" : "YOK",
            pfn_PyIsInitialized ? pfn_PyIsInitialized() : -1);   // FIX-11
    OutP("python27.dll : %s%s\n", pfn_PyRun_SimpleString ? "BULUNDU" : "YOK (oyun python'u daha baslamamis olabilir)",
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
        _snprintf(pylibPath, MAX_PATH, "%s\\PLUSMAXGOD_PyScript.py", BASE_DIR); pylibPath[MAX_PATH-1]=0;
        DWORD pa = GetFileAttributesA(pylibPath);
        if (pa != INVALID_FILE_ATTRIBUTES && !(pa & FILE_ATTRIBUTE_DIRECTORY))
        {
            char ver[32];
            bool okVer = ReadPylibVersion(pylibPath, ver) && atoi(ver) >= 4;
            std::string ld;
            if (EnqueueCommand(BootImport(), ld))
                LogLine("AUTO-LOAD: PLUSMAXGOD_PyScript.py kuyruga kondu (%s)", pylibPath);
            if (okVer)
            {
                OutP("PLUSMAXGOD_PyScript.py : v%s (uyumlu) - otomatik yuklenecek\n", ver);
                OutP("                        oyun-ici: stat pos inv equip skill near chat goto tp |\n");
                OutP("                        kesif: pyfiles pydumpall pyscan plusquest\n");
            }
            else
            {
                const char* vShow = ver[0] ? ver : "2.x/3.x (isaret yok/eski)";
                char rp[MAX_PATH];
                _snprintf(rp, MAX_PATH, "%s\\last_warning.txt", RESULT_DIR); rp[MAX_PATH-1]=0;
                WriteFileAll(rp, std::string("! PYLIB ESI SURUM: v") + vShow +
                    "  (DLL v2.6 PLUSMAXGOD v5.0 ister)\n"
                    "Yeni PLUSMAXGOD_PyScript.py'yi " + std::string(BASE_DIR) + " icine kopyala (bundle zip / GitHub).\n"
                    "ESKI pylib ILE: stat/pos/inv/equip/skill/near/chat/goto/tp/pyfiles/pydumpall/plusquest CALISMAZ.\n");
                LogLine("UYARI: pylib ESI v%s - PLUSMAXGOD v5.0 gerekli! (%s)", vShow, pylibPath);
                OutP("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
                OutP("!! PYLIB ESI: diskteki PLUSMAXGOD_PyScript.py = v%s  (gereken: v5.0)\n", vShow);
                OutP("!! Yeni PLUSMAXGOD_PyScript.py'yi %s icine kopyala (bundle zip)\n", BASE_DIR);
                OutP("!! Eski pylib ile v4.0 komutlari CALISMAZ (stat/inv/tp/pyfiles..)\n");
                OutP("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n");
            }
        }
        else
        {
            char rp[MAX_PATH];
            _snprintf(rp, MAX_PATH, "%s\\last_load.txt", RESULT_DIR); rp[MAX_PATH-1]=0;
            WriteFileAll(rp, "HATA: " + std::string(pylibPath) + " YOK!\n"
                             "bundle zip icindeki PLUSMAXGOD_PyScript.py'yi " + std::string(BASE_DIR) +
                             " klasorune kopyala.\n");
            LogLine("UYARI: PLUSMAXGOD_PyScript.py YOK — komutlar calismaz! (%s)", pylibPath);
            OutP("PLUSMAXGOD_PyScript.py : YOK!! (%s)\n", pylibPath);
            OutP("                bundle zip'ten PLUSMAXGOD_PyScript.py'yi %s icine kopyala.\n", BASE_DIR);
            OutP("                Kopyalamadan komut yazarsan: ImportError maxlib.\n");
        }
    }
    for (int i = 0; i < 40 && !HookGameWindow(); ++i) Sleep(500);
    if (!g_hGameWnd) LogLine("oyun penceresi 20 sn icinde bulunamadi");
    OutP("oyun penceresi: %s (hwnd=%p)\n", g_hGameWnd ? "SUBCLASS EDILDI" : "BULUNAMADI",
           (void*)g_hGameWnd);
    OutP("kuyruk: %s | sonuc: %s\n", QUEUE_DIR, RESULT_DIR);
    InstallTimer();                               // FIX-8: WndProc'tan bagimsiz ana yol
    CreateThread(NULL, 0, AutoDrainThread, NULL, 0, NULL);
    CreateThread(NULL, 0, LiveMonitorThread, NULL, 0, NULL);   // FIX-36
    PrintHelp();

    char line[4096];
    while (true)
    {
        OutP("maxexec> ");
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
            else OutP("kullanim: login <id> <sifre>\n");
        }
        else if (cmd == "selserver")
        {
            if (a.size() >= 3) CmdSelServer(atoi(a[1].c_str()), atoi(a[2].c_str()));
            else OutP("kullanim: selserver <server> <kanal>   (orn. selserver 0 0)\n");
        }
        else if (cmd == "empire")
        {
            if (a.size() >= 2) CmdEmpire(atoi(a[1].c_str()));
            else OutP("kullanim: empire <1-3>   (1=Shinsoo 2=Chunjo 3=Jinno)\n");
        }
        else if (cmd == "create")
        {
            if (a.size() >= 5) CmdCreate(atoi(a[1].c_str()), a[2], atoi(a[3].c_str()), atoi(a[4].c_str()));
            else OutP("kullanim: create <slot> <ad> <race> <shape>\n");
        }
        else if (cmd == "enter")
        {
            if (a.size() >= 2) CmdEnter(atoi(a[1].c_str()));
            else OutP("kullanim: enter <slot>\n");
        }
        else if (cmd == "selchar")
        {
            if (a.size() >= 2) CmdSelChar(atoi(a[1].c_str()));
            else OutP("kullanim: selchar <slot 0-4>\n");
        }
        else if (cmd == "newchar") CmdNewChar();
        else if (cmd == "joblist") CmdJobList();
        else if (cmd == "mkchar")
        {
            if (a.size() >= 3) CmdMkChar(a[1], atoi(a[2].c_str()));
            else OutP("kullanim: mkchar <isim> <race 0-8>   (orn. mkchar Isim 3 = Shaman(K))\n");
        }
        else if (cmd == "empirelist") CmdEmpireList();
        else if (cmd == "empireui")
        {
            if (a.size() >= 2) CmdEmpireUI(atoi(a[1].c_str()));
            else OutP("kullanim: empireui <1-3>   (1=Shinsoo 2=Chunjo 3=Jinno)\n");
        }
        else if (cmd == "delchar")
        {
            if (a.size() >= 2) CmdDelChar(atoi(a[1].c_str()));
            else OutP("kullanim: delchar <slot 0-4>   (sonra delcode <silme-kodu>)\n");
        }
        else if (cmd == "delcode")
        {
            if (a.size() >= 2) CmdDelCode(a[1]);
            else OutP("kullanim: delcode <silme-kodu>   (once delchar <slot>)\n");
        }
        // ---- FIX-33 (v1.8): PLUSMAXGOD komut ailesi ----
        else if (cmd == "stat") CmdStat();
        else if (cmd == "pos") CmdPos();
        else if (cmd == "equip") CmdEquip();
        else if (cmd == "skill") CmdSkill();
        else if (cmd == "near") CmdNear(a.size() >= 2 ? a[1] : "0");
        else if (cmd == "ride") CmdRide();
        else if (cmd == "revive") CmdRevive();
        else if (cmd == "logout") CmdLogout();
        else if (cmd == "back") CmdBack();
        else if (cmd == "pickup") CmdPickup();
        else if (cmd == "pyfiles") CmdPyFiles();
        else if (cmd == "pydumpall") CmdPyDumpAll();
        else if (cmd == "plusquest" || cmd == "pyscanall") CmdPlusQuest();
        else if (cmd == "inv")
        {
            CmdInv(a.size() >= 2 ? atoi(a[1].c_str()) : 0);
        }
        else if (cmd == "chat")
        {
            if (a.size() >= 2) CmdChat(JoinArgs(a, 1));
            else OutP("kullanim: chat <mesaj>   (orn. chat merhaba | chat /ride)\n");
        }
        else if (cmd == "cmd")
        {
            if (a.size() >= 2)
            {
                std::string j = JoinArgs(a, 1);
                if (j[0] != '/') j = "/" + j;
                CmdChat(j);
            }
            else OutP("kullanim: cmd <slash-komut>   (orn. cmd /ride | cmd /logout)\n");
        }
        else if (cmd == "whisper")
        {
            if (a.size() >= 3) CmdWhisper(a[1], JoinArgs(a, 2));
            else OutP("kullanim: whisper <kim> <mesaj>\n");
        }
        else if (cmd == "zoom")
        {
            if (a.size() >= 2) CmdZoom(atoi(a[1].c_str()));
            else OutP("kullanim: zoom <mesafe>   (orn. zoom 12000)\n");
        }
        else if (cmd == "use")
        {
            if (a.size() >= 2) CmdUse(atoi(a[1].c_str()));
            else OutP("kullanim: use <slot>   (slot: inv raporundan)\n");
        }
        else if (cmd == "drop")
        {
            if (a.size() >= 3) CmdDrop(atoi(a[1].c_str()), atoi(a[2].c_str()));
            else OutP("kullanim: drop <slot> <adet>   (DESTRUKTIF - dikkat!)\n");
        }
        else if (cmd == "goto")
        {
            if (a.size() >= 3) CmdGoto(atoi(a[1].c_str()), atoi(a[2].c_str()));
            else OutP("kullanim: goto <x> <y>   (once pos yaz)\n");
        }
        else if (cmd == "tp")
        {
            if (a.size() >= 3) CmdTp(atoi(a[1].c_str()), atoi(a[2].c_str()));
            else OutP("kullanim: tp <x> <y>   (once pos yaz)\n");
        }
        else if (cmd == "key")
        {
            if (a.size() >= 2) CmdKey(a[1], a.size() >= 3 ? a[2] : "1");
            else OutP("kullanim: key <DIK> <0/1>   (orn. key UP 1, key LEFT 0)\n");
        }
        else if (cmd == "attack")
        {
            CmdAttack(a.size() >= 2 ? a[1] : "1");
        }
        else if (cmd == "pydump")
        {
            if (a.size() >= 2) CmdPyDump(a[1]);
            else OutP("kullanim: pydump <dosya-ad>   (orn. pydump intrologin | adaylar: pyfiles)\n");
        }
        else if (cmd == "pyscan")
        {
            if (a.size() >= 2) CmdPyScan(a[1]);
            else OutP("kullanim: pyscan <modul>   (orn. pyscan player | pyscan net)\n");
        }
        // --- FIX-37 (v1.9): GOD MOD komutlari ---
        else if (cmd == "unequip")
        {
            if (a.size() >= 2) CmdUnequip(a[1]);
            else OutP("kullanim: unequip <parca|slot>   (body/head/shoes/wrist/weapon/neck/ear/unique/arrow/costume | 90-109)\n");
        }
        else if (cmd == "unequipall") CmdUnequipAll();
        else if (cmd == "ground") CmdGround();
        else if (cmd == "groundtake")
        {
            CmdGroundTake(a.size() >= 2 ? a[1] : "all");
        }
        else if (cmd == "autotake")
        {
            CmdAutoTake(a.size() >= 2 ? a[1] : "1");
        }
        else if (cmd == "quest") CmdQuest();
        else if (cmd == "fakeitem")
        {
            if (a.size() >= 2) CmdFakeItem(a[1], a.size() >= 3 ? a[2] : "1");
            else OutP("kullanim: fakeitem <vnum> [adet]   (HAYALET esya - istemci gorunumu)\n");
        }
        else if (cmd == "fakeclear")
        {
            CmdFakeClear(a.size() >= 2 ? a[1] : "all");
        }
        else if (cmd == "clone")
        {
            CmdClone(a.size() >= 2 ? a[1] : "80", a.size() >= 3 ? a[2] : "-1");
        }
        else if (cmd == "unclone")
        {
            CmdUnClone(a.size() >= 2 ? a[1] : "all");
        }
        else if (cmd == "spawn")
        {
            if (a.size() >= 2) CmdSpawn(a[1], a.size() >= 3 ? a[2] : "NPC");
            else OutP("kullanim: spawn <race> [ad]   (demirci=20016, satici=20010, simyaci=20001; race ogrenme: near)\n");
        }
        else if (cmd == "morph")
        {
            if (a.size() >= 2) CmdMorph(a[1]);
            else OutP("kullanim: morph <race>   (demirci gorunumu: morph 20016; geri: unmorph)\n");
        }
        else if (cmd == "unmorph") CmdUnMorph();
        else if (cmd == "setarmor")
        {
            if (a.size() >= 2) CmdSetArmor(a[1]);
            else OutP("kullanim: setarmor <vnum>   (gorunum zirhi - istemci tarafi)\n");
        }
        else if (cmd == "setweapon")
        {
            if (a.size() >= 2) CmdSetWeapon(a[1]);
            else OutP("kullanim: setweapon <vnum>   (gorunum silahi - istemci tarafi)\n");
        }
        else if (cmd == "simya" || cmd == "ds") CmdSimya();
        else if (cmd == "itemscan")
        {
            if (a.size() >= 3) CmdItemScan(a[1], a[2]);
            else OutP("kullanim: itemscan <min> <max>   (orn. itemscan 55000 55999 - simya vnum kesfi)\n");
        }
        else if (cmd == "fish") CmdFish();
        else if (cmd == "fishstop") CmdFishStop();
        else if (cmd == "fishkeep")
        {
            CmdFishKeep(a.size() >= 2 ? a[1] : "0");
        }
        else if (cmd == "fishspot")
        {
            if (a.size() >= 3) CmdFishSpot(a[1], a[2]);
            else CmdFishSpot("0", "0");
        }
        else if (cmd == "fishstat") CmdFishStat();
        else if (cmd == "fishtest") CmdFishTest();
        // --- v2.0 (pylib v4.4) komutlari ---
        else if (cmd == "morphtarget") CmdMorphTarget();
        else if (cmd == "cloneplayer") CmdClonePlayer();
        else if (cmd == "fakemount" || cmd == "ridefake")
        {
            CmdFakeMount(a.size() >= 2 ? a[1] : "1");
        }
        else if (cmd == "statup")
        {
            if (a.size() >= 2) CmdStatUp(a[1], a.size() >= 3 ? a[2] : "1");
            else OutP("kullanim: statup <ht|iq|st|dx> [adet]   (orn: statup st 10)\n");
        }
        else if (cmd == "skillup")
        {
            if (a.size() >= 2) CmdSkillUp(a[1], a.size() >= 3 ? a[2] : "1");
            else OutP("kullanim: skillup <skill-idx> [adet]   (idx: skill raporundan)\n");
        }
        else if (cmd == "antifly")
        {
            CmdAntiFly(a.size() >= 2 ? a[1] : "1");
        }
        else if (cmd == "antiflyeffect")
        {
            CmdAntiFlyEffect(a.size() >= 2 ? a[1] : "1");
        }
        else if (cmd == "warp")
        {
            if (a.size() >= 3) CmdWarp(a[1], a[2]);
            else OutP("kullanim: warp <x> <y>   (otp adimlama + konum paketi - ayni harita)\n");
        }
        else if (cmd == "antistun") CmdAntiStun(a.size() >= 2 ? a[1] : "1");
        else if (cmd == "antislow") CmdAntiSlow(a.size() >= 2 ? a[1] : "1");
        else if (cmd == "autopot")
        {
            // v2.3 yeni sema: autopot hp 80 | autopot mp 80 | autopot (durum) | autopot 0
            if (a.size() >= 2) CmdAutoPot(a[1], a.size() >= 3 ? a[2] : "80");
            else CmdAutoPot("durum", "0");
        }
        else if (cmd == "autopot_item")
        {
            CmdAutoPotItem(a.size() >= 2 ? a[1] : "?");
        }
        else if (cmd == "slots") CmdSlots();
        else if (cmd == "selljunk")
        {
            CmdSellJunk(a.size() >= 2 ? JoinArgs(a, 1) : "");
        }
        else if (cmd == "sellall")
        {
            CmdSellAll(a.size() >= 2 ? a[1] : "");
        }
        else if (cmd == "dropall")
        {
            std::string sub = JoinArgs(a, 1);
            CmdDropAll(sub);
        }
        else if (cmd == "combo") CmdCombo(a.size() >= 2 ? a[1] : "0");
        else if (cmd == "statdown")
        {
            if (a.size() >= 2) CmdStatDown(a[1], a.size() >= 3 ? a[2] : "1");
            else OutP("kullanim: statdown <ht|iq|st|dx> [adet]   (stat puani geri al)\n");
        }
        else if (cmd == "skillupui")
        {
            if (a.size() >= 2) CmdSkillUpUI(a[1]);
            else OutP("kullanim: skillupui <slot>   (oyunun kendi skill+ dugme fonksiyonu)\n");
        }
        else if (cmd == "statupui")
        {
            if (a.size() >= 2) CmdStatUpUI(a[1]);
            else OutP("kullanim: statupui <ht|iq|st|dx>   (oyunun kendi stat+ dugme fonksiyonu)\n");
        }
        else if (cmd == "efsun")
        {
            CmdEfsun(a.size() >= 2 ? a[1] : "all");
        }
        else if (cmd == "itemfind")
        {
            if (a.size() >= 2) CmdItemFind(JoinArgs(a, 1));
            else OutP("kullanim: itemfind <kelime>   (orn: itemfind simya | itemfind kostum)\n");
        }
        else if (cmd == "iteminfo")
        {
            if (a.size() >= 2) CmdItemInfo(a[1]);
            else OutP("kullanim: iteminfo <vnum>\n");
        }
        else if (cmd == "attr")
        {
            if (a.size() >= 2) CmdAttr(a[1]);
            else OutP("kullanim: attr <slot>   (envanter 0-89, ekipman 90+)\n");
        }
        else if (cmd == "attrall") CmdAttrAll();
        else if (cmd == "useon")
        {
            if (a.size() >= 3) CmdUseOn(a[1], a[2]);
            else OutP("kullanim: useon <kagit-slot> <esya-slot>\n");
        }
        else if (cmd == "efsunsw")
        {
            if (a.size() >= 2) CmdEfsunSw(a[1]);
            else OutP("kullanim: efsunsw <esya-slot>\n");
        }
        else if (cmd == "gotake")
        {
            CmdGoTake(a.size() >= 2 ? a[1] : "all");
        }
        else if (cmd == "otp" || cmd == "otp1" || cmd == "optimizetp" || cmd == "otp2")
        {
            // v2.5 (saha testi 15): 'otp delay 1' -> ValueError yiyordu.
            // Artik alt-komutlar BURADA yakalanir (pylib yedek yonlendirme de var).
            bool m2 = (cmd == "otp2");
            if (a.size() >= 2)
            {
                const std::string& s1 = a[1];
                if (s1 == "stop" || s1 == "dur" || s1 == "kapat" || s1 == "0")
                    CmdOTPStop();
                else if (s1 == "delay" || s1 == "bekle")
                {
                    if (a.size() >= 3) CmdOTPDelay(a[2]);
                    else OutP("kullanim: otp delay <ms>   (orn: otp delay 1300 - beklemeyi ayarlar)\n");
                }
                else if (s1 == "step" || s1 == "adim")
                {
                    if (a.size() >= 3) CmdOTPStep(a[2]);
                    else OutP("kullanim: otp step <px>   (240 oneri - 25m TP-kontrol alti)\n");
                }
                else if (a.size() >= 3)
                {
                    if (m2) CmdOTP2(a[1], a[2]);
                    else    CmdOTP1(a[1], a[2]);
                }
                else
                    OutP("kullanim: otp <x> <y> | otp2 <x> <y> | otp delay <ms> | otp step <px> | dur: otpstop\n");
            }
            else
                OutP("kullanim: otp <x> <y> | otp2 <x> <y> | otp delay <ms> | otp step <px> | dur: otpstop\n");
        }
        else if (cmd == "otpstop")  CmdOTPStop();
        else if (cmd == "otpstep")  { if (a.size() >= 2) CmdOTPStep(a[1]); else OutP("kullanim: otpstep <px> (240 oneri)\n"); }
        else if (cmd == "otpdelay") { if (a.size() >= 2) CmdOTPDelay(a[1]); else OutP("kullanim: otpdelay <ms> (1300 oneri)\n"); }
        else if (cmd == "clonemod") { if (a.size() >= 2) CmdCloneMod(a[1]); else OutP("kullanim: clonemod <swap|1|0>\n"); }
        else if (cmd == "spawnscan")
        {
            if (a.size() >= 3) CmdSpawnScan(a[1], a[2]);
            else CmdSpawnScan("1", "30000");
        }
        else if (cmd == "itemscanall") CmdItemScanAll();
        else if (cmd == "canli")
        {
            std::string m;
            for (size_t i = 1; i < a.size(); ++i) { if (i > 1) m += " "; m += a[i]; }
            CmdCanli(m);
        }
        else if (cmd == "serverlist") CmdServerList();
        else if (cmd == "lasterr") CmdLastErr();
        else if (cmd == "load")
        {
            if (a.size() >= 2) CmdLoad(a[1]);
            else OutP("kullanim: load <py-dosyasi>   (v1.3+ zaten otomatik)\n");
        }
        else if (cmd == "raw")
        {
            if (ln.size() > 4) QRaw(ln.substr(4));
            else OutP("kullanim: raw <python kodu>   (orn. raw import sys)\n");
        }
        else if (cmd == "waitfor")
        {
            if (a.size() >= 3) CmdWaitFor(a[1], atoi(a[2].c_str()));
            else OutP("kullanim: waitfor <SahneAdi> <saniye>   (orn. waitfor GameWindow 60)\n");
        }
        else if (cmd == "pyerr")   // FIX-17: Python hatalarini konsolda gor
        {
            FILE* f = fopen(PYERR_LOG, "r");
            if (!f) { OutP("pyerr.log yok (henuz Python hatasi olusmadi)\n"); continue; }
            char buf[512]; std::vector<std::string> lines;
            while (fgets(buf, sizeof(buf), f)) lines.push_back(buf);
            fclose(f);
            OutP("--- pyerr.log son %d satir ---\n", (int)(lines.size() > 30 ? 30 : lines.size()));
            for (size_t i = lines.size() > 30 ? lines.size()-30 : 0; i < lines.size(); ++i)
                OutP("%s", lines[i].c_str());
        }
        else if (cmd == "log")
        {
            FILE* f = fopen(EXEC_LOG, "r");
            if (!f) { OutP("log yok\n"); continue; }
            char buf[512]; std::vector<std::string> lines;
            while (fgets(buf, sizeof(buf), f)) lines.push_back(buf);
            fclose(f);
            for (size_t i = lines.size() > 25 ? lines.size()-25 : 0; i < lines.size(); ++i)
                OutP("%s", lines[i].c_str());
        }
        else OutP("bilinmeyen komut (help)\n");
    }
    return 0;
}

// ---------------------------------------------------------------------------
// DllMain
// ---------------------------------------------------------------------------
static void EnsureDirs(void)
{
    MkDirp(BASE_DIR); MkDirp(QUEUE_DIR); MkDirp(RESULT_DIR);
    MkDirp(DUMP_DIR);                    // FIX-34: py dump + PLUSQuest_live
}

BOOL APIENTRY DllMain(HMODULE hMod, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        // Loader-lock guvenli minimal init: konsol kurulumu worker'a tasindi (FIX-3)
        DisableThreadLibraryCalls(hMod);
        EnsureDirs();
        CreateThread(NULL, 0, WorkerThread, NULL, 0, NULL);
        LogLine("MaxExecutor v2.5 PLUSMAXGOD yuklendi (pid=%lu) — worker baslatiliyor",
                GetCurrentProcessId());
    }
    return TRUE;
}
