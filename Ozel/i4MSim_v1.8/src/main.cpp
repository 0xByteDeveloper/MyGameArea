// ============================================================================
//  i4MSim v1.8 - DLL yuklu-hal (process-dinamik) SIMULASYONU + HOOK TARAMASI
//  Motor: i4MConsoleLoader / PEManualMapper.h (Windows loader emulasyonu)
//  EK   : [9/9] TLS callback + DllMain CALISTIRMA -> packer unpack tetiklenir
//  v1.8 : semantik siniflandirma (HPTR-ASLR/T2-STAT/CNT/PATH/PKS) + KOMUT 4
//         (canli-kendi-gurultusu) + KOMUT 8 (hook tarama: EXEC-diff + pointer-
//         hedef denetimi + modul-disi EXEC bolge taramasi + modul listesi)
//
//  Komutlar:
//    1 <dll yolu>  -> SIMULE ET: DLL'i bir feda-i process icinde GERCEK Windows
//                     loader ile yukle (LoadLibraryEx), packer unpack'ini
//                     calistir, base..base+SizeOfImage TUM byte'lari
//                     C:\simule_memory.txt olarak kaydet
//    2 <pid>       -> CANLI DUMP: hedef process'te python27.dll bul (base..end),
//                     tum byte'lari C:\dinamik_memory.txt olarak kaydet
//    3             -> iki dosyayi byte-byte karsilastir (0 fark = %100 simule)
//    4 <pid>       -> canlinin KENDI gurultusu: iki canli dump (1 sn arayla)
//                     karsilastirilir -> sim'siz taban-gurultu kaniti
//    5 <dll yolu>  -> zorla MANUAL-MAP modu (PEManualMapper + TLS + DllMain)
//    6 <dll yolu>  -> zorla GERCEK-LOADER modu (LoadLibraryEx)
//    8 <pid>       -> HOOK TARAMA: (a) EXEC/kod bolgelerinde sim-vs-canli
//                     byte diff (inline hook), (b) fark bolgelerindeki
//                     pointer'larin canli hedef-denetimi (trampoline avı),
//                     (c) modul-disi EXEC bellek taramasi, (d) modul listesi
//
//  Gizli cocuk modlari (kendi kendine spawn): --simlib <yol> / --simmap <yol>
//  Feda-i process: arac kendini %TEMP%\i4MHost\metin2client.exe olarak kopya-
//  layip oradan calistirir (pack'in host-exe-adi kontrolune karsi).
// ============================================================================

#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#define _CRT_SECURE_NO_WARNINGS
#include <windows.h>
#include <tlhelp32.h>
#include "PEManualMapper.h"
#include <string>
#include <vector>
#include <map>
#include <cstdio>
#include <cstring>
#include <cctype>
#include <cstdint>
#include <ctime>

using u8  = unsigned char;
using u16 = unsigned short;
using u32 = unsigned int;
using u64 = unsigned long long;
using ADR = uintptr_t;

#ifdef _WIN64
#define FMTA "%016llX"
#define A(x) ((unsigned long long)(x))
#else
#define FMTA "%08X"
#define A(x) ((unsigned)(x))
#endif

// ---------------------------------------------------------------------------
// sabitler
// ---------------------------------------------------------------------------
static const char* TOOL_VER  = "i4MSim v1.8";
static const char* SIM_TXT   = "C:\\simule_memory.txt";
static const char* LIVE_TXT  = "C:\\dinamik_memory.txt";
static const char* LIVE2_TXT = "C:\\dinamik_memory_2.txt";
static const char* SIM_LOG   = "C:\\simule_log.txt";
static const char* TARGET_DLL = "python27.dll";

// diff raporu disaridan analiz icin ek cikti (v1.8)
static const char* HOOK_TXT  = "C:\\i4msim_hookscan.txt";

// ---------------------------------------------------------------------------
// yardimcilar
// ---------------------------------------------------------------------------
static u64 Fnv64(const u8* p, size_t n) {
    u64 h = 0xCBF29CE484222325ULL;
    for (size_t i = 0; i < n; i++) { h ^= p[i]; h *= 0x100000001B3ULL; }
    return h;
}

static void NowStamp(char* out, size_t cap) {
    SYSTEMTIME st; GetLocalTime(&st);
    snprintf(out, cap, "%04u-%02u-%02u %02u:%02u:%02u",
             st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond);
}

static std::string Trim(const std::string& s) {
    size_t a = 0, b = s.size();
    while (a < b && (s[a]==' '||s[a]=='\t'||s[a]=='\r'||s[a]=='\n'||s[a]=='\"')) a++;
    while (b > a && (s[b-1]==' '||s[b-1]=='\t'||s[b-1]=='\r'||s[b-1]=='\n'||s[b-1]=='\"')) b--;
    return s.substr(a, b - a);
}

static std::string Lower(std::string s) {
    for (auto& c : s) c = (char)tolower((unsigned char)c);
    return s;
}

static bool Ieq(const std::string& a, const std::string& b) { return Lower(a) == Lower(b); }

static void HumanSize(u64 n, char* out, size_t cap) {
    if (n >= 1024ull*1024ull) snprintf(out, cap, "%.2f MB", (double)n / (1024.0*1024.0));
    else snprintf(out, cap, "%.1f KB", (double)n / 1024.0);
}

static bool ReadableProtect(DWORD p) {
    if (p & PAGE_GUARD) return false;
    switch (p & 0xFF) {
        case PAGE_NOACCESS: return false;
        default: return true;
    }
}

// ---------------------------------------------------------------------------
// v1.8: pointer/bolge yardimcileri (hook taramasi + semantik siniflandirma)
// ---------------------------------------------------------------------------
// ileri bildirimler (asagida tanimlilar)
static bool RpmX(HANDLE h, ADR addr, void* buf, size_t n);
static bool FindRemoteModule(DWORD pid, const char* modName, ADR* base, u32* size,
                             std::string& how, std::string& err);
static bool ResolveDumpPath(const char* cPath, const char* tempName, std::string& out);

static bool ExecProtect(DWORD p) {
    switch (p & 0xFF) {
        case PAGE_EXECUTE:
        case PAGE_EXECUTE_READ:
        case PAGE_EXECUTE_READWRITE:
        case PAGE_EXECUTE_WRITECOPY: return true;
        default: return false;
    }
}

static bool WriteProtect(DWORD p) {
    switch (p & 0xFF) {
        case PAGE_READWRITE:
        case PAGE_WRITECOPY:
        case PAGE_EXECUTE_READWRITE:
        case PAGE_EXECUTE_WRITECOPY: return true;
        default: return false;
    }
}

// pointer-benzeri mi? (32-bit user alani, NULL degil, ucucta degil)
static bool PtrLike(u32 v) {
    return v >= 0x00010000 && v < 0x7FFE0000;
}

// canli process'in modul listesi + bellek bolge haritasi
struct ModEntry { ADR base; u32 size; std::string name; std::string path; };
struct RegionInfo { ADR base; SIZE_T size; DWORD state, protect, type; };
struct RemoteMaps {
    std::vector<ModEntry> mods;
    std::vector<RegionInfo> regions;
    bool ok = false;
};

static bool BuildRemoteMaps(HANDLE h, DWORD pid, RemoteMaps& rm) {
    rm.mods.clear(); rm.regions.clear(); rm.ok = false;
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid);
    if (snap == INVALID_HANDLE_VALUE) return false;
    MODULEENTRY32W me{}; me.dwSize = sizeof(me);
    if (Module32FirstW(snap, &me)) {
        do {
            ModEntry m;
            m.base = (ADR)(uintptr_t)me.modBaseAddr;
            m.size = me.modBaseSize;
            for (int q = 0; q < 63 && me.szModule[q]; q++) m.name.push_back((char)(me.szModule[q] < 128 ? me.szModule[q] : '?'));
            wchar_t* wp = me.szExePath;
            char path[MAX_PATH*2] = {}; int pi = 0;
            for (; *wp && pi < MAX_PATH*2-1; wp++) path[pi++] = (char)(*wp < 128 ? *wp : '?');
            m.path = path;
            rm.mods.push_back(m);
        } while (Module32NextW(snap, &me));
    }
    CloseHandle(snap);
    if (rm.mods.empty()) return false;

    SYSTEM_INFO si{}; GetSystemInfo(&si);
    uintptr_t addr = (uintptr_t)si.lpMinimumApplicationAddress;
    uintptr_t maxa = (uintptr_t)si.lpMaximumApplicationAddress;
    int guard = 0;
    while (addr < maxa && guard++ < 300000) {
        MEMORY_BASIC_INFORMATION mbi{};
        if (!VirtualQueryEx(h, (LPCVOID)addr, &mbi, sizeof(mbi))) break;
        RegionInfo r;
        r.base   = (ADR)(uintptr_t)mbi.BaseAddress;
        r.size   = mbi.RegionSize;
        r.state  = mbi.State;
        r.protect= mbi.Protect;
        r.type   = mbi.Type;
        rm.regions.push_back(r);
        addr = (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
    }
    rm.ok = true;
    return true;
}

static const ModEntry* ModOf(const RemoteMaps& rm, ADR a) {
    for (auto& m : rm.mods)
        if (a >= m.base && a < m.base + m.size) return &m;
    return nullptr;
}

// hedef adresin turu: MODUL / HEAP-VERI / EXEC-ANONIM(supheli) / OKUNMAZ
static void ClassifyTarget(const RemoteMaps& rm, u32 v, char* out, size_t cap) {
    ADR a = (ADR)v;
    const ModEntry* m = ModOf(rm, a);
    if (m) { snprintf(out, cap, "MODUL(%s)", m->name.c_str()); return; }
    for (auto& r : rm.regions) {
        if (a >= r.base && a < r.base + r.size) {
            if (r.state != MEM_COMMIT) { snprintf(out, cap, "RESERVED"); return; }
            if (ExecProtect(r.protect)) {
                const char* t = (r.type == MEM_IMAGE) ? "EXEC-IMAGE(mapli,modul-listesi-disi!)"
                              : (r.type == MEM_MAPPED) ? "EXEC-MAPPED"
                                                       : "EXEC-ANONIM(supheli!)";
                snprintf(out, cap, "%s", t);
            } else {
                snprintf(out, cap, "%s", (r.type == MEM_PRIVATE) ? "HEAP/VERI" : "MAPPED-VERI");
            }
            return;
        }
    }
    snprintf(out, cap, "HARITA-DISI");
}

// canli python27 goruntusunu hafizaya oku (komut 2/4/8 ortak)
static bool ReadLiveImage(DWORD pid, std::vector<u8>& img, ADR& base, u32& size,
                          std::string& how, std::string& err) {
    HANDLE h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    if (!h) { err = "OpenProcess hata " + std::to_string(GetLastError()); return false; }
    std::string e2;
    if (!FindRemoteModule(pid, TARGET_DLL, &base, &size, how, e2)) {
        err = TARGET_DLL + std::string(" bulunamadi: ") + e2;
        CloseHandle(h); return false;
    }
    img.assign(size, 0);
    SIZE_T got = 0;
    if (ReadProcessMemory(h, (LPCVOID)base, img.data(), size, &got) && got == size) {
        CloseHandle(h); return true;
    }
    u32 skipped = 0;
    const u32 PG = 0x1000;
    for (u32 off = 0; off < size; off += PG) {
        u32 n = (size - off < PG) ? (size - off) : PG;
        MEMORY_BASIC_INFORMATION mbi{};
        LPCVOID a = (LPCVOID)(base + off);
        if (!VirtualQueryEx(h, a, &mbi, sizeof(mbi)) || !ReadableProtect(mbi.Protect) ||
            !RpmX(h, base + off, img.data() + off, n)) skipped++;
    }
    CloseHandle(h);
    if (skipped) err = "(uyari: " + std::to_string(skipped) + " sayfa okunamadi, 0 dolduruldu)";
    return true;
}

// fark bolgelerini birlestir (<=8 bosluk) - ortak yardimci
static void MergeDiffRegions(const u8* a, const u8* b, size_t n,
                             std::vector<std::pair<u32,u32>>& regs) {
    for (size_t i = 0; i < n; i++) {
        if (a[i] != b[i]) {
            if (!regs.empty() && (u32)i - (regs.back().first + regs.back().second) <= 8)
                regs.back().second = (u32)(i + 1 - regs.back().first);
            else regs.push_back({ (u32)i, 1 });
        }
    }
}

// bolgenin semantik etiketi (v1.8 siniflandirmasi)
//   HPTR-ASLR : iki taraf da heap-benzeri pointer (ASLR -> eslesemez)
//   T2-STAT   : bir taraf image-statik ptr, digeri heap/kucuk (init turu)
//   CNT       : kucuk sayac/refcnt/bayragi degerleri
//   PATH      : ascii yol/string icerigi
//   PKS       : packer-kosmetik section-header alani (rawsize=0 bolum)
//   VERI      : diger
static const char* SemanticTag(const u8* x1, const u8* x2, size_t imgSize, u32 rva, u32 len,
                               u32 img1Lo, u32 img1Hi, u32 img2Lo, u32 img2Hi,
                               bool isPackerHdrField) {
    if (isPackerHdrField) return "PKS";
    bool ascii = true, anyPrint = false;
    for (u32 k = 0; k < len; k++) {
        u8 c = x1[rva+k], d = x2[rva+k];
        if (!((c >= 32 && c < 127) || c == 0) || !((d >= 32 && d < 127) || d == 0)) { ascii = false; break; }
        if (c >= 32 && c < 127) anyPrint = true;
    }
    bool sawHeap = false, sawT2 = false, sawCnt = false;
    u32 w0 = rva & ~3u, w1 = (rva + len - 1) & ~3u;
    for (u32 off = w0; off <= w1; off += 4) {
        if (off + 4 > imgSize) break;
        u32 v1, v2;
        memcpy(&v1, x1 + off, 4);
        memcpy(&v2, x2 + off, 4);
        if (v1 == v2) continue;
        bool h1 = PtrLike(v1), h2 = PtrLike(v2);
        bool i1 = (v1 >= img1Lo && v1 < img1Hi);
        bool i2 = (v2 >= img2Lo && v2 < img2Hi);
        if (h1 && h2 && !i1 && !i2) sawHeap = true;
        if ((i1 && h2 && !i2) || (i2 && h1 && !i1)) sawT2 = true;
        if (i2 && !h2 && v1 < 0x10000) sawT2 = true;
        if (i1 && !h1 && v2 < 0x10000) sawT2 = true;
        if (!h1 && !h2 && !i1 && !i2) sawCnt = true;
    }
    if (ascii && anyPrint && len >= 3) return "PATH";
    if (sawHeap) return sawT2 ? "HPTR-ASLR+T2" : "HPTR-ASLR";
    if (sawT2)   return "T2-STAT";
    if (sawCnt)  return "CNT";
    return "VERI";
}

// ---------------------------------------------------------------------------
// SEH sarmalayicilar
//   MSVC   : gercek __try/__except (istisnada bile yasamaya devam)
//   zig/clang x86: lld-link i686 SEH tablolarini baglayamiyor ->
//   fallback : VirtualQuery on-kontrolu + kok-RPM; istisna olursa cocuk
//              process duser, parent raporlar (process izolasyonu zaten var)
// ---------------------------------------------------------------------------
typedef BOOL  (WINAPI *DllMainT)(HINSTANCE, DWORD, LPVOID);
typedef VOID  (WINAPI *TlsCbT)(LPVOID, DWORD, LPVOID);

static bool PageBlocked(const void* p) {
    MEMORY_BASIC_INFORMATION mbi{};
    if (!VirtualQuery(p, &mbi, sizeof(mbi))) return true;
    if (mbi.Protect & PAGE_GUARD) return true;
    if ((mbi.Protect & 0xFF) == PAGE_NOACCESS) return true;
    return false;
}

#if defined(_MSC_VER)
static bool SafeCallEntry(void* fn, HINSTANCE h, DWORD r, LPVOID rv, BOOL* out) {
    __try { *out = ((DllMainT)fn)(h, r, rv); return true; }
    __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}
static bool SafeCallTls(void* fn, HINSTANCE h, DWORD r, LPVOID rv) {
    __try { ((TlsCbT)fn)(h, r, rv); return true; }
    __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}
static bool SafeTouch(const void* p) {
    __try { *(volatile const u8*)p; return true; }
    __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}
static bool SafeCopyPage(void* dst, const void* src, size_t n) {
    __try { memcpy(dst, src, n); return true; }
    __except (EXCEPTION_EXECUTE_HANDLER) { return false; }
}
#else
static bool SafeCallEntry(void* fn, HINSTANCE h, DWORD r, LPVOID rv, BOOL* out) {
    *out = ((DllMainT)fn)(h, r, rv);
    return true;
}
static bool SafeCallTls(void* fn, HINSTANCE h, DWORD r, LPVOID rv) {
    ((TlsCbT)fn)(h, r, rv);
    return true;
}
static bool SafeTouch(const void* p) {
    if (PageBlocked(p)) {
        u8 b = 0; SIZE_T got = 0;
        return ReadProcessMemory(GetCurrentProcess(), p, &b, 1, &got) && got == 1;
    }
    *(volatile const u8*)p;
    return true;
}
static bool SafeCopyPage(void* dst, const void* src, size_t n) {
    if (PageBlocked(src)) {
        SIZE_T got = 0;
        return ReadProcessMemory(GetCurrentProcess(), src, dst, n, &got) && got == n;
    }
    memcpy(dst, src, n);
    return true;
}
#endif

// ---------------------------------------------------------------------------
// Cikti yolu secimi: C:\ yazilamiyorsa %TEMP% altina duser
// ---------------------------------------------------------------------------
static bool PickOutPath(const char* cPath, const char* tempName, std::string& out, bool& usedTemp) {
    out = cPath; usedTemp = false;
    FILE* t = fopen(cPath, "ab");
    if (t) { fclose(t); return true; }
    char tp[MAX_PATH] = {};
    if (GetTempPathA(MAX_PATH, tp)) {
        out = std::string(tp) + tempName; usedTemp = true;
        FILE* t2 = fopen(out.c_str(), "ab");
        if (t2) { fclose(t2); return true; }
    }
    return false;
}

// ---------------------------------------------------------------------------
// DUMP TXT YAZICI  (meta baslik + hexdump govde)
// ---------------------------------------------------------------------------
struct DumpInfo {
    std::string kind;      // sim | live
    std::string mode;      // simlib | simmap | rpm
    std::string module;
    std::string srcPath;
    DWORD       pid = 0;
    ADR         base = 0;
    u32         size = 0;
    u32         ep = 0;
    const u8*   data = nullptr;
    std::string note;
    u32         skippedPages = 0;
};

static bool WriteDumpTxt(const std::string& path, const DumpInfo& di, std::string& err) {
    FILE* f = fopen(path.c_str(), "wb");
    if (!f) { err = "cikti dosyasi acilamadi: " + path + " (hata " + std::to_string(GetLastError()) + ")"; return false; }

    char stamp[64]; NowStamp(stamp, sizeof(stamp));
    char fnv[32];  snprintf(fnv, sizeof(fnv), "%016llX", (unsigned long long)Fnv64(di.data, di.size));

    fprintf(f, "I4MDUMP1\n");
    fprintf(f, "kind=%s\n", di.kind.c_str());
    fprintf(f, "mode=%s\n", di.mode.c_str());
    fprintf(f, "module=%s\n", di.module.c_str());
    fprintf(f, "path=%s\n", di.srcPath.c_str());
    fprintf(f, "pid=%lu\n", (unsigned long)di.pid);
    fprintf(f, "base=" FMTA "\n", A(di.base));
    fprintf(f, "end=" FMTA "\n", A(di.base + (di.size ? di.size - 1 : 0)));
    fprintf(f, "size=%X\n", di.size);
    fprintf(f, "ep=%X\n", di.ep);
#ifdef _WIN64
    fprintf(f, "machine=x64\n");
#else
    fprintf(f, "machine=x86\n");
#endif
    fprintf(f, "fnv64=%s\n", fnv);
    fprintf(f, "skippedpages=%u\n", di.skippedPages);
    fprintf(f, "saved=%s\n", stamp);
    fprintf(f, "tool=%s\n", TOOL_VER);
    fprintf(f, "note=%s\n", di.note.c_str());
    fprintf(f, "--------------------------------------------------\n");

    std::vector<char> line;
    line.reserve(256);
    char hdr[32];
    for (u32 off = 0; off < di.size; off += 32) {
        line.clear();
        snprintf(hdr, sizeof(hdr), "%08X  ", off);
        line.insert(line.end(), hdr, hdr + strlen(hdr));
        u32 chunk = (di.size - off < 32) ? (di.size - off) : 32;
        for (u32 i = 0; i < chunk; i++) {
            static const char* HEX = "0123456789ABCDEF";
            u8 b = di.data[off + i];
            line.push_back(HEX[b >> 4]); line.push_back(HEX[b & 0xF]);
            line.push_back(i + 1 < chunk ? ' ' : '\n');
        }
        fwrite(line.data(), 1, line.size(), f);
    }
    fclose(f);
    return true;
}

// ---------------------------------------------------------------------------
// DUMP TXT OKUYUCU
// ---------------------------------------------------------------------------
struct ParsedDump {
    std::vector<std::pair<std::string, std::string>> meta;
    std::vector<u8> bytes;
    bool ok = false;
    std::string err;

    std::string Get(const char* k, const char* def = "") const {
        for (auto& kv : meta) if (kv.first == k) return kv.second;
        return def;
    }
    u32 GetHex(const char* k, u32 def = 0) const {
        std::string v = Get(k);
        if (v.empty()) return def;
        return (u32)strtoull(v.c_str(), nullptr, 16);
    }
    u64 GetHex64(const char* k, u64 def = 0) const {
        std::string v = Get(k);
        if (v.empty()) return def;
        return strtoull(v.c_str(), nullptr, 16);
    }
};

static inline int H2(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    return -1;
}

static bool IsHex8(const char* l) {
    for (int i = 0; i < 8; i++) if (H2(l[i]) < 0) return false;
    return (l[8] == ' ');
}

static bool ReadDumpTxt(const std::string& path, ParsedDump& d, std::string& err) {
    FILE* f = fopen(path.c_str(), "rb");
    if (!f) { err = "dosya acilamadi: " + path; return false; }
    fseek(f, 0, SEEK_END);
    long fsz = ftell(f);
    fseek(f, 0, SEEK_SET);
    if (fsz <= 0) { fclose(f); err = "dosya bos: " + path; return false; }
    std::string txt; txt.resize((size_t)fsz);
    size_t got = fread(&txt[0], 1, (size_t)fsz, f);
    fclose(f);
    txt.resize(got);

    size_t pos = 0, lineNo = 0;
    while (pos <= txt.size()) {
        size_t e = txt.find('\n', pos);
        std::string line = txt.substr(pos, (e == std::string::npos ? txt.size() : e) - pos);
        pos = (e == std::string::npos) ? txt.size() + 1 : e + 1;
        lineNo++;
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) continue;
        if (line[0] == '-') continue;

        if (line.size() > 9 && IsHex8(line.c_str())) {
            u32 off = (u32)strtoul(line.substr(0, 8).c_str(), nullptr, 16);
            if (off != d.bytes.size()) {
                char b[128]; snprintf(b, sizeof(b), "satir %zu: offset atlama (beklenen %zu, dosyada %08X)",
                                      lineNo, d.bytes.size(), off);
                err = b; return false;
            }
            const char* p = line.c_str() + 9;
            while (*p == ' ') p++;
            while (*p) {
                int h1 = H2(p[0]), h2 = H2(p[1]);
                if (h1 < 0 || h2 < 0) break;
                d.bytes.push_back((u8)((h1 << 4) | h2));
                p += 2;
                while (*p == ' ') p++;
            }
        } else if (line.size() > 2 && line.find('=') != std::string::npos) {
            size_t eq = line.find('=');
            d.meta.push_back({ Trim(line.substr(0, eq)), line.substr(eq + 1) });
        }
        if (e == std::string::npos) break;
    }
    d.ok = true;
    return true;
}

// ---------------------------------------------------------------------------
// PE section ayristirma (dump byte'larinin icinden; offset == RVA)
// ---------------------------------------------------------------------------
struct SecInfo {
    char name[9];
    u32  rva, vsize, rawsize, chars;
};

static bool ParseImageSections(const u8* img, size_t size, u32& hdrSize,
                               std::vector<SecInfo>& secs, std::string& err) {
    if (size < 0x200 || img[0] != 'M' || img[1] != 'Z') { err = "MZ imzasi yok"; return false; }
    u32 e = *(const u32*)(img + 0x3C);
    if (e + 248 > size || *(const u32*)(img + e) != 0x00004550u) { err = "PE imzasi yok"; return false; }
    u16 magic = *(const u16*)(img + e + 24);
    if (magic != 0x10B && magic != 0x20B) { err = "PE32/PE32+ bekleniyordu"; return false; }
    hdrSize = *(const u32*)(img + e + 24 + 60);          // SizeOfHeaders
    u16 nsec = *(const u16*)(img + e + 6);               // NumberOfSections
    u32 optSize = *(const u16*)(img + e + 20);
    u32 secOff = e + 24 + optSize;
    if (secOff + (u32)nsec * 40 > size) { err = "section tablosu tasma"; return false; }
    for (u16 i = 0; i < nsec; i++) {
        const u8* sh = img + secOff + i * 40;
        SecInfo s{};
        memcpy(s.name, sh, 8); s.name[8] = 0;
        s.vsize   = *(const u32*)(sh + 8);
        s.rva     = *(const u32*)(sh + 12);
        s.rawsize = *(const u32*)(sh + 16);
        s.chars   = *(const u32*)(sh + 36);
        secs.push_back(s);
    }
    return true;
}

// ---------------------------------------------------------------------------
// image byte'larini guvenli topla (sayfa sayfa; guard/NOACCESS -> 0)
// ---------------------------------------------------------------------------
static u32 CollectImageBytes(ADR base, u32 size, std::vector<u8>& out) {
    out.assign(size, 0);
    u32 skipped = 0;
    const u32 PG = 0x1000;
    for (u32 off = 0; off < size; off += PG) {
        u32 n = (size - off < PG) ? (size - off) : PG;
        const void* src = (const void*)(base + off);
        MEMORY_BASIC_INFORMATION mbi{};
        if (VirtualQuery(src, &mbi, sizeof(mbi)) && !ReadableProtect(mbi.Protect)) {
            skipped++;
            continue;
        }
        if (!SafeCopyPage(out.data() + off, src, n)) skipped++;
    }
    return skipped;
}

// ---------------------------------------------------------------------------
// COCUK MODU 1: --simlib (GERCEK Windows loader: LoadLibraryEx)
//   loader header map + section + reloc + IAT + TLS + DllMain HEPSINI yapar;
//   packer unpack'i DllMain icinde gercelleisir. En yuksek sadakat.
// ---------------------------------------------------------------------------
static int RunSimChildLib(const std::string& dllPath) {
    FILE* lf = fopen(SIM_LOG, "w");
    auto L = [&](const char* fmt, ...) {
        char buf[1024];
        va_list a; va_start(a, fmt);
        vsnprintf(buf, sizeof(buf), fmt, a);
        va_end(a);
        printf("[cocuk-simlib] %s\n", buf);
        if (lf) { fprintf(lf, "%s\n", buf); fflush(lf); }
    };

    L("mod=simlib (gercek Windows loader)");
    // DLL'in kendi klasorune gec (bagimliliklar oradan bulunsun)
    size_t p = dllPath.find_last_of("\\/");
    if (p != std::string::npos) SetCurrentDirectoryA(dllPath.substr(0, p).c_str());

    HMODULE h = LoadLibraryExA(dllPath.c_str(), NULL, LOAD_WITH_ALTERED_SEARCH_PATH);
    if (!h) {
        L("[!!] LoadLibraryEx basarisiz (hata %lu) - ImageBase dolu olabilir", GetLastError());
        if (lf) fclose(lf);
        return 2;
    }
    ADR base = (ADR)h;
    L("[+] yuklendi: base=" FMTA, A(base));

    {
        char real[MAX_PATH] = {};
        GetModuleFileNameA(h, real, MAX_PATH);
        L("[i] GetModuleFileName: %s", real);
        HMODULE dup = GetModuleHandleA("python27.dll");
        L("[i] GetModuleHandle(python27.dll) = %p", (void*)dup);
        // cocugun kendi modul listesi (ilk 12)
        HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE, GetCurrentProcessId());
        if (snap != INVALID_HANDLE_VALUE) {
            MODULEENTRY32W me{}; me.dwSize = sizeof(me);
            int k = 0;
            if (Module32FirstW(snap, &me)) {
                do {
                    char nm[64] = {};
                    for (int q = 0; q < 63 && me.szModule[q]; q++) nm[q] = (char)me.szModule[q];
                    L("    modul[%d] %-20s base=%p size=%X", k, nm, (void*)me.modBaseAddr, me.modBaseSize);
                    k++;
                } while (Module32NextW(snap, &me) && k < 14);
            }
            CloseHandle(snap);
        }
        u8 probe[16];
        memcpy(probe, (const void*)(base + 0x1000), 16);
        L("[i] base+0x1000 ilk16: %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X",
          probe[0],probe[1],probe[2],probe[3],probe[4],probe[5],probe[6],probe[7],
          probe[8],probe[9],probe[10],probe[11],probe[12],probe[13],probe[14],probe[15]);
    }

    u8 hdr[0x1000];
    if (!SafeCopyPage(hdr, (const void*)base, sizeof(hdr))) { L("[!!] header okunamadi"); if (lf) fclose(lf); return 3; }
    u32 e = *(const u32*)(hdr + 0x3C);
    if (*(const u32*)(hdr + e) != 0x00004550u) { L("[!!] PE imzasi yok"); if (lf) fclose(lf); return 3; }
    u32 size = *(const u32*)(hdr + e + 24 + 56);   // SizeOfImage
    u32 ep   = *(const u32*)(hdr + e + 24 + 16);   // AddressOfEntryPoint
    L("[+] SizeOfImage=%X  EntryPoint RVA=%X", size, ep);

#ifndef _WIN64
    if (base != 0x1E000000)
        L("[i] ImageBase tercihi 1E000000 DEGIL (" FMTA ") -> reloc uygulanmis olur", A(base));
#endif

    // packer unpack DllMain icinde tamamlandi (LoadLibrary senkron doner)
    // guard/lazy sayfalar varsa tetikle:
    u32 touched = 0, failed = 0;
    for (u32 off = 0; off < size; off += 0x1000) {
        if (SafeTouch((const void*)(base + off))) touched++; else failed++;
    }
    L("[i] sayfa dokunma: %u tetiklendi, %u atlandi", touched, failed);
    FlushInstructionCache(GetCurrentProcess(), (LPCVOID)base, size);
    Sleep(200);

    std::vector<u8> img;
    u32 skipped = CollectImageBytes(base, size, img);
    L("[i] goruntu toplandi: %u byte, %u sayfa okunamadi(0 dolduruldu)", (unsigned)img.size(), skipped);

    // unpack kontrolu: rawsize=0 + EXEC bolum hala tumu sifir ise pack unpack etmedi
    u32 hs = 0; std::vector<SecInfo> secs; std::string serr;
    if (ParseImageSections(img.data(), img.size(), hs, secs, serr)) {
        for (auto& s : secs) {
            if (s.rawsize == 0 && (s.chars & IMAGE_SCN_MEM_EXECUTE) && s.vsize >= 0x1000) {
                bool allZero = true;
                for (u32 i = 0; i < 0x1000; i++)
                    if (img[s.rva + i]) { allZero = false; break; }
                if (allZero) {
                    L("[!!] %s hala BOŞ -> packer unpack YAPMADI (host kontrolu olabilir)", s.name);
                    L("     cozum: '5 <yol>' ile manual-map modunu dene");
                    if (lf) fclose(lf);
                    return 6;
                }
            }
        }
    }

    DumpInfo di;
    di.kind = "sim"; di.mode = "simlib";
    di.module = TARGET_DLL; di.srcPath = dllPath;
    di.pid = GetCurrentProcessId(); di.base = base; di.size = size; di.ep = ep;
    di.data = img.data(); di.skippedPages = skipped;
    di.note = "gercek Windows loader (LoadLibraryEx) + packer unpack + sayfa tetikleme";
    std::string outPath; bool usedTemp = false;
    if (!PickOutPath(SIM_TXT, "simule_memory.txt", outPath, usedTemp)) {
        L("[!!] cikti yazilamiyor"); if (lf) fclose(lf); return 4;
    }
    std::string werr;
    if (!WriteDumpTxt(outPath, di, werr)) { L("[!!] %s", werr.c_str()); if (lf) fclose(lf); return 4; }
    L("[+] dump yazildi: %s%s", outPath.c_str(), usedTemp ? " (C:\\ yazilamadi, TEMP kullanildi)" : "");
    if (lf) fclose(lf);
    return 0;
}

// ---------------------------------------------------------------------------
// COCUK MODU 2: --simmap (i4MConsoleLoader PEManualMapper + TLS + DllMain)
// ---------------------------------------------------------------------------
static int RunSimChildMap(const std::string& dllPath) {
    FILE* lf = fopen(SIM_LOG, "w");
    auto L = [&](const char* fmt, ...) {
        char buf[1024];
        va_list a; va_start(a, fmt);
        vsnprintf(buf, sizeof(buf), fmt, a);
        va_end(a);
        printf("[cocuk-simmap] %s\n", buf);
        if (lf) { fprintf(lf, "%s\n", buf); fflush(lf); }
    };

    L("mod=simmap (PEManualMapper + TLS + DllMain calistirma)");

    std::vector<u8> file;
    {
        HANDLE hF = CreateFileA(dllPath.c_str(), GENERIC_READ, FILE_SHARE_READ, NULL,
                                OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
        if (hF == INVALID_HANDLE_VALUE) { L("[!!] dosya acilamadi (hata %lu)", GetLastError()); if (lf) fclose(lf); return 2; }
        LARGE_INTEGER fsz{};
        if (!GetFileSizeEx(hF, &fsz)) { CloseHandle(hF); L("[!!] boyut alinamadi"); if (lf) fclose(lf); return 2; }
        file.resize((size_t)fsz.QuadPart);
        DWORD rd = 0;
        if (!ReadFile(hF, file.data(), (DWORD)file.size(), &rd, nullptr) || rd != file.size()) {
            CloseHandle(hF); L("[!!] dosya okunamadi"); if (lf) fclose(lf); return 2;
        }
        CloseHandle(hF);
    }
    L("[i] disk dosyasi okundu: %u byte", (unsigned)file.size());

    PEManualMapper mapper;
    mapper.options.tryPreferredBase        = true;
    mapper.options.applyRelocations        = true;
    mapper.options.resolveImports          = true;
    mapper.options.setSectionProtections   = false;  // unpack yazacak: hepsi RW kalsin
    mapper.options.continueOnMissingImport = true;

    auto res = mapper.MapMemory(file);
    for (auto& l : res.log) L("  | %s", l.c_str());
    if (!res.success) { L("[!!] map basarisiz: %s", res.error.c_str()); if (lf) fclose(lf); return 2; }

    if ((u32)(uintptr_t)res.base != (u32)res.preferredBase) {
        L("[!!] ImageBase %llX dolu, base=%p -> tekrar denenecek", (unsigned long long)res.preferredBase, (void*)res.base);
        PEManualMapper::Unmap(res);
        if (lf) fclose(lf);
        return 5;   // parent yeni process acar (ASLR zarini yeniden atar)
    }

    // ---- [0/9] goruntuyu RWX yap (DEP fix) ----
    // packer unpack .text'e YAZACAK, sonra EP calistirilacak; korumalar atlandigi
    // icin sayfalar PAGE_READWRITE kaldi -> DEP execute'a izin vermez.
    {
        DWORD oldp = 0;
        if (VirtualProtect((LPVOID)(uintptr_t)res.base, (SIZE_T)res.imageSize,
                           PAGE_EXECUTE_READWRITE, &oldp))
            L("[0/9] goruntu RWX yapildi (unpack yazma + calistirma icin)");
        else
            L("[!] RWX basarisiz (hata %lu) - DEP'de EP cagrisi cokebilir", GetLastError());
    }

    // ---- [9/9a] TLS VERI KURULUMU (LdrpHandleTlsData emulasyonu) ----
    // gercek loader TLS callback'lerden ONCE TEB->ThreadLocalStoragePointer[idx]
    // vektorunu kurar ve raw data'yi kopyalar; kurmazsak callback NULL'a duser.
    if (res.hasTLS) {
        u32 e2  = *(const u32*)((u8*)(uintptr_t)res.base + 0x3C);
        u32 opt2 = e2 + 24;
        u16 magic2 = *(const u16*)((u8*)(uintptr_t)res.base + opt2);
        u32 ddOff2 = (magic2 == 0x20B) ? opt2 + 112 : opt2 + 96;   // DataDirectory[9] = TLS
        u32 tlsRva = *(const u32*)((u8*)(uintptr_t)res.base + ddOff2 + 9 * 8);
        if (tlsRva) {
            u64 start, end, idxAddr, cbAddr; u32 zeroFill;
            if (magic2 == 0x20B) {
                auto t = (IMAGE_TLS_DIRECTORY64*)((u8*)(uintptr_t)res.base + tlsRva);
                start = t->StartAddressOfRawData; end = t->EndAddressOfRawData;
                idxAddr = t->AddressOfIndex;      cbAddr = t->AddressOfCallBacks;
                zeroFill = t->SizeOfZeroFill;
            } else {
                auto t = (IMAGE_TLS_DIRECTORY32*)((u8*)(uintptr_t)res.base + tlsRva);
                start = t->StartAddressOfRawData; end = t->EndAddressOfRawData;
                idxAddr = t->AddressOfIndex;      cbAddr = t->AddressOfCallBacks;
                zeroFill = t->SizeOfZeroFill;
            }
            u64 rawSz = (end > start) ? (end - start) : 0;
            u32 blockSz = (u32)(rawSz + zeroFill);
            void* block = calloc(1, blockSz ? blockSz : 1);
            if (block && rawSz)
                memcpy(block, (const void*)(uintptr_t)start, (size_t)rawSz);
            DWORD idx = TlsAlloc();
            if (idx == TLS_OUT_OF_INDEXES) idx = 0;
            if (idxAddr)
                *(volatile u32*)(uintptr_t)idxAddr = (u32)idx;   // loader index'i buraya yazar
            void** vec = NULL;
#ifdef _WIN64
            vec = (void**)__readgsqword(0x58);                    // TEB.ThreadLocalStoragePointer
            if (!vec) { vec = (void**)calloc(64, sizeof(void*)); __writegsqword(0x58, (u64)vec); }
#else
            vec = (void**)__readfsdword(0x2C);
            if (!vec) { vec = (void**)calloc(64, sizeof(void*)); __writefsdword(0x2C, (u32)(uintptr_t)vec); }
#endif
            if (vec) vec[idx] = block;
            L("[9/9a] TLS veri kuruldu: idx=%lu block=%p (%u byte, raw %llu + zero %u)",
              (unsigned long)idx, block, blockSz, (unsigned long long)rawSz, zeroFill);
        } else {
            L("[9/9a] TLS dizini okunamadi (rva=0)");
        }
    }

    // ---- [9/9b] TLS callback'ler (loader sirasi: TLS veri -> callback -> EP) ----
    if (res.hasTLS && res.tlsCallbacksVA) {
#ifdef _WIN64
        u64* cb = (u64*)(uintptr_t)res.tlsCallbacksVA;
#else
        u32* cb = (u32*)(uintptr_t)res.tlsCallbacksVA;
#endif
        int n = 0;
        while (*cb && n < 64) {
            ADR va = (ADR)*cb;
            L("[9/9b] TLS callback[%d] @ " FMTA " cagiriliyor...", n, A(va));
            if (va >= (ADR)(uintptr_t)res.base && va < (ADR)(uintptr_t)res.base + res.imageSize) {
                if (SafeCallTls((void*)va, (HINSTANCE)res.base, DLL_PROCESS_ATTACH, NULL))
                    L("[9/9b] TLS callback[%d] dondu (OK)", n);
                else
                    L("[!]  TLS callback[%d] EXCEPTION: " FMTA, n, A(va));
            } else {
                L("[!]  TLS callback[%d] goruntu disinda (" FMTA ") - atlandi", n, A(va));
            }
            cb++; n++;
        }
        L("[9/9b] TLS turu bitti (%d callback)", n);
    } else {
        L("[9/9b] TLS callback yok");
    }

    // ---- DllMain (EP) CALISTIR -> packer unpack burada gercelleisir ----
    BOOL ret = FALSE;
    if (!SafeCallEntry((void*)(uintptr_t)res.entryPointVA, (HINSTANCE)res.base, DLL_PROCESS_ATTACH, NULL, &ret)) {
        L("[!!] EntryPoint EXCEPTION (SEH kodu kaydi yok) - unpack tamamlanmadi");
        if (lf) fclose(lf);
        return 3;
    }
    L("[+] DllMain(PROCESS_ATTACH) dondu: %d  (packer unpack tamamlandi)", (int)ret);

    FlushInstructionCache(GetCurrentProcess(), (LPCVOID)(uintptr_t)res.base, (size_t)res.imageSize);
    Sleep(200);

    u32 touched = 0, failed = 0;
    for (u32 off = 0; off < (u32)res.imageSize; off += 0x1000) {
        if (SafeTouch((const void*)((ADR)(uintptr_t)res.base + off))) touched++; else failed++;
    }
    L("[i] sayfa dokunma: %u tetiklendi, %u atlandi", touched, failed);

    std::vector<u8> img;
    u32 skipped = CollectImageBytes((ADR)(uintptr_t)res.base, (u32)res.imageSize, img);
    L("[i] goruntu toplandi: %u byte, %u sayfa okunamadi(0 dolduruldu)", (unsigned)img.size(), skipped);

    u32 hs = 0; std::vector<SecInfo> secs; std::string serr;
    if (ParseImageSections(img.data(), img.size(), hs, secs, serr)) {
        for (auto& s : secs) {
            if (s.rawsize == 0 && (s.chars & IMAGE_SCN_MEM_EXECUTE) && s.vsize >= 0x1000) {
                bool allZero = true;
                for (u32 i = 0; i < 0x1000; i++)
                    if (img[s.rva + i]) { allZero = false; break; }
                if (allZero) {
                    L("[!!] %s hala BOŞ -> packer unpack YAPMADI", s.name);
                    if (lf) fclose(lf);
                    return 6;
                }
            }
        }
    }

    DumpInfo di;
    di.kind = "sim"; di.mode = "simmap";
    di.module = TARGET_DLL; di.srcPath = dllPath;
    di.pid = GetCurrentProcessId();
    di.base = (ADR)(uintptr_t)res.base; di.size = (u32)res.imageSize;
    di.ep = (u32)(res.entryPointVA - (u64)(uintptr_t)res.base);
    di.data = img.data(); di.skippedPages = skipped;
    di.note = "PEManualMapper manuel map + TLS + DllMain calistirma (i4MConsoleLoader motoru)";
    std::string outPath; bool usedTemp = false;
    if (!PickOutPath(SIM_TXT, "simule_memory.txt", outPath, usedTemp)) {
        L("[!!] cikti yazilamiyor"); if (lf) fclose(lf); return 4;
    }
    std::string werr;
    if (!WriteDumpTxt(outPath, di, werr)) { L("[!!] %s", werr.c_str()); if (lf) fclose(lf); return 4; }
    L("[+] dump yazildi: %s%s", outPath.c_str(), usedTemp ? " (C:\\ yazilamadi, TEMP kullanildi)" : "");
    if (lf) fclose(lf);
    return 0;
}

// ---------------------------------------------------------------------------
// KOMUT 1 (parent): feda-i process baslat, bekle, raporla
// ---------------------------------------------------------------------------
static void PrintChildLog() {
    FILE* f = fopen(SIM_LOG, "rb");
    if (!f) return;
    printf("\n---- cocuk log (%s) ----\n", SIM_LOG);
    char buf[1024];
    while (fgets(buf, sizeof(buf), f)) printf("%s", buf);
    fclose(f);
    printf("---- log sonu ----\n");
}

static bool RunSimChild(const std::string& mode, const std::string& dllPath,
                        const char* hostExe, DWORD* exitCode) {
    std::string cmd = "\"" + std::string(hostExe) + "\" --" + mode + " \"" + dllPath + "\"";
    STARTUPINFOA si{}; si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    if (!CreateProcessA(NULL, (LPSTR)cmd.c_str(), NULL, NULL, FALSE,
                        0, NULL, NULL, &si, &pi)) {
        printf("[!] feda-i process baslatilamadi (hata %lu)\n", GetLastError());
        return false;
    }
    DWORD w = WaitForSingleObject(pi.hProcess, 180000);
    if (w == WAIT_TIMEOUT) {
        printf("[!] cocuk 180 sn icinde bitmedi -> sonlandiriliyor\n");
        TerminateProcess(pi.hProcess, 99);
        WaitForSingleObject(pi.hProcess, 5000);
    }
    DWORD rc = 99;
    GetExitCodeProcess(pi.hProcess, &rc);
    CloseHandle(pi.hThread); CloseHandle(pi.hProcess);
    *exitCode = rc;
    return (rc == 0);
}

static void DoSimulate(const std::string& dllPath, bool forceMap) {
    char self[MAX_PATH] = {};
    GetModuleFileNameA(NULL, self, MAX_PATH);

    char tp[MAX_PATH] = {};
    GetTempPathA(MAX_PATH, tp);
    std::string hostDir = std::string(tp) + "i4MHost";
    CreateDirectoryA(hostDir.c_str(), NULL);
    std::string hostExe = hostDir + "\\metin2client.exe";
    if (!CopyFileA(self, hostExe.c_str(), FALSE))
        printf("[i] kopya host olusturulamadi (hata %lu) - kendi adimla devam\n", GetLastError());

    std::string path = Trim(dllPath);
    printf("\n================================================================\n");
    printf(" SIMULASYON: %s\n", path.c_str());
    printf(" yontem    : %s\n", forceMap ? "MANUAL-MAP (PEManualMapper + TLS + DllMain)"
                                              : "GERCEK LOADER (LoadLibraryEx) -> gerekirse manual-map");
    printf(" host      : %s (feda-i process)\n", hostExe.c_str());
    printf("================================================================\n");

    DWORD rc = 99;
    bool ok = false;
    if (!forceMap) {
        for (int t = 1; t <= 2 && !ok; t++) {
            printf("[*] gercek-loader denemesi %d...\n", t);
            ok = RunSimChild("simlib", path, hostExe.c_str(), &rc);
            if (ok) break;
            if (rc == 2) { printf("[i] LoadLibrary basarisiz -> manual-map moduna geciliyor\n"); break; }
            if (rc == 6) { printf("[i] pack unpack yapmadi -> manual-map moduna geciliyor\n"); break; }
            if (rc == 99) break;   // timeout
        }
    }
    for (int t = 1; t <= 3 && !ok; t++) {
        printf("[*] manual-map denemesi %d (base=1E000000 garantilenir)...\n", t);
        ok = RunSimChild("simmap", path, hostExe.c_str(), &rc);
        if (rc == 5) { printf("[i] ImageBase dolu -> yeni process ile tekrar\n"); continue; }
        break;
    }

    if (!ok) {
        printf("\n[!] SIMULASYON BASARISIZ (cocuk rc=%lu)\n", (unsigned long)rc);
        PrintChildLog();
        return;
    }

    // ozet
    ParsedDump d; std::string err;
    std::string outPath; bool usedTemp = false;
    PickOutPath(SIM_TXT, "simule_memory.txt", outPath, usedTemp);
    if (ReadDumpTxt(outPath, d, err)) {
        u64 bb = d.GetHex64("base"); u32 s = d.GetHex("size");
        char hs[32]; HumanSize(s, hs, sizeof(hs));
        printf("\n[+] SIMULASYON TAMAM: %s%s\n", outPath.c_str(), usedTemp ? " (TEMP)" : "");
        printf("    modul    : %s (%s modu)\n", d.Get("module").c_str(), d.Get("mode").c_str());
        printf("    base     : " FMTA "\n", A(bb));
        printf("    end      : " FMTA "  (son byte)\n", A(bb + (s ? s - 1 : 0)));
        printf("    boyut    : %X byte (%s)\n", s, hs);
        printf("    fnv64    : %s\n", d.Get("fnv64").c_str());
        printf("    kayit    : %s\n", d.Get("saved").c_str());
        printf("    su an '2 <pid>' ile canli dump, sonra '3' ile karsilastir.\n");
    } else {
        printf("[!] dump yazildi ama okunamadi: %s\n", err.c_str());
    }
}

// ---------------------------------------------------------------------------
// UZAK PROCESS YARDIMCILARI (komut 2)
// ---------------------------------------------------------------------------
static bool Rpm(HANDLE h, u32 addr, void* buf, size_t n) {
    SIZE_T got = 0;
    return ReadProcessMemory(h, (LPCVOID)(uintptr_t)addr, buf, n, &got) && got == n;
}
static bool RpmX(HANDLE h, ADR addr, void* buf, size_t n) {
    SIZE_T got = 0;
    return ReadProcessMemory(h, (LPCVOID)addr, buf, n, &got) && got == n;
}

static bool ScanRemotePE(HANDLE h, const char* want, ADR* base, u32* size) {
    SYSTEM_INFO si{}; GetSystemInfo(&si);
    uintptr_t addr = (uintptr_t)si.lpMinimumApplicationAddress;
    uintptr_t maxa = (uintptr_t)si.lpMaximumApplicationAddress;
    int guardIter = 0;
    while (addr < maxa && guardIter++ < 200000) {
        MEMORY_BASIC_INFORMATION mbi{};
        if (!VirtualQueryEx(h, (LPCVOID)addr, &mbi, sizeof(mbi))) break;
        if (mbi.State == MEM_COMMIT && mbi.RegionSize >= 0x1000 && ReadableProtect(mbi.Protect)) {
            u8 hdr[0x1000];
            ADR b0 = (ADR)(uintptr_t)mbi.BaseAddress;
            if (Rpm(h, (u32)(uintptr_t)b0, hdr, sizeof(hdr)) ||
                (RpmX(h, b0, hdr, sizeof(hdr)))) {
                if (hdr[0] == 'M' && hdr[1] == 'Z') {
                    u32 e = *(const u32*)(hdr + 0x3C);
                    if (e >= 0x40 && e <= 0xF00 && e + 248 <= 0x1000 &&
                        *(const u32*)(hdr + e) == 0x00004550u) {
                        u16 mach  = *(const u16*)(hdr + e + 4);
                        u16 magic = *(const u16*)(hdr + e + 24);
                        u32 ddOff = (magic == 0x20B) ? 24 + 112 : 24 + 96;
                        u32 soi = *(const u32*)(hdr + e + 24 + 56);
                        u32 expRva = *(const u32*)(hdr + e + ddOff);
                        if ((mach == 0x014C || mach == 0x8664) &&
                            soi > 0x1000 && soi < 0x10000000 && expRva) {
                            IMAGE_EXPORT_DIRECTORY ed{};
                            if (RpmX(h, b0 + expRva, &ed, sizeof(ed)) && ed.Name) {
                                char nm[64] = {};
                                if (RpmX(h, b0 + ed.Name, nm, sizeof(nm) - 1) && Ieq(nm, want)) {
                                    *base = b0; *size = soi;
                                    return true;
                                }
                            }
                        }
                    }
                }
            }
        }
        addr = (uintptr_t)mbi.BaseAddress + mbi.RegionSize;
    }
    return false;
}

static bool FindRemoteModule(DWORD pid, const char* modName, ADR* base, u32* size,
                             std::string& how, std::string& err) {
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid);
    if (snap != INVALID_HANDLE_VALUE) {
        MODULEENTRY32W me{}; me.dwSize = sizeof(me);
        if (Module32FirstW(snap, &me)) {
            do {
                std::wstring mn = me.szModule;
                std::string s; s.reserve(mn.size());
                for (wchar_t w : mn) s.push_back((char)(w < 128 ? w : '?'));
                if (Ieq(s, modName)) {
                    *base = (ADR)(uintptr_t)me.modBaseAddr;
                    *size = me.modBaseSize;
                    how = "module-snapshot";
                    CloseHandle(snap);
                    return true;
                }
            } while (Module32NextW(snap, &me));
        }
        CloseHandle(snap);
    }
    HANDLE h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    if (!h) { err = "OpenProcess hata " + std::to_string(GetLastError()); return false; }
    bool f = ScanRemotePE(h, modName, base, size);
    CloseHandle(h);
    if (f) how = "bellek-PE-taramasi";
    else err = "snapshot + bellek taramasi ikisi de bulamadi";
    return f;
}

static void DoLiveDump(DWORD pid) {
    printf("\n================================================================\n");
    printf(" CANLI DUMP: pid=%lu  modul=%s\n", (unsigned long)pid, TARGET_DLL);
    printf("================================================================\n");

    HANDLE h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    if (!h) {
        printf("[!] OpenProcess basarisiz (hata %lu) - pid dogru mu? Yonetici olarak dene.\n", GetLastError());
        return;
    }

    ADR base = 0;
    u32 size = 0;
    std::string how, err;
    if (!FindRemoteModule(pid, TARGET_DLL, &base, &size, how, err)) {
        printf("[!] %s hedef process'te bulunamadi: %s\n", TARGET_DLL, err.c_str());
        CloseHandle(h);
        return;
    }
    printf("[+] %s bulundu (%s): base=" FMTA " end=" FMTA " boyut=%X\n",
           TARGET_DLL, how.c_str(), A(base), A(base + (size ? size - 1 : 0)), size);

    std::vector<u8> img(size, 0);
    SIZE_T got = 0;
    u32 skipped = 0;
    if (ReadProcessMemory(h, (LPCVOID)base, img.data(), size, &got) && got == size) {
        printf("[i] toplu okuma OK (%u byte)\n", (unsigned)size);
    } else {
        printf("[i] toplu okuma eksik -> sayfa sayfa okunuyor...\n");
        const u32 PG = 0x1000;
        for (u32 off = 0; off < size; off += PG) {
            u32 n = (size - off < PG) ? (size - off) : PG;
            MEMORY_BASIC_INFORMATION mbi{};
            LPCVOID a = (LPCVOID)(base + off);
            if (!VirtualQueryEx(h, a, &mbi, sizeof(mbi)) || !ReadableProtect(mbi.Protect) ||
                !RpmX(h, base + off, img.data() + off, n)) {
                skipped++;
            }
        }
        if (skipped) printf("[!] %u sayfa okunamadi (NOACCESS/guard) - 0 ile dolduruldu\n", skipped);
    }
    CloseHandle(h);

    DumpInfo di;
    di.kind = "live"; di.mode = "rpm";
    di.module = TARGET_DLL; di.srcPath = "";
    di.pid = pid; di.base = base; di.size = size;
    di.data = img.data(); di.skippedPages = skipped;
    di.note = "ReadProcessMemory (disaridan canli okuma)";
    std::string outPath; bool usedTemp = false;
    if (!PickOutPath(LIVE_TXT, "dinamik_memory.txt", outPath, usedTemp)) {
        printf("[!] cikti dosyasi acilamiyor (C:\\ ve TEMP)\n");
        return;
    }
    std::string werr;
    if (!WriteDumpTxt(outPath, di, werr)) { printf("[!] %s\n", werr.c_str()); return; }

    char hs[32]; HumanSize(size, hs, sizeof(hs));
    printf("\n[+] CANLI DUMP TAMAM: %s%s\n", outPath.c_str(), usedTemp ? " (TEMP)" : "");
    printf("    base     : " FMTA "\n", A(base));
    printf("    end      : " FMTA "  (son byte)\n", A(base + (size ? size - 1 : 0)));
    printf("    boyut    : %X byte (%s)\n", size, hs);
    printf("    fnv64    : %016llX\n", (unsigned long long)Fnv64(img.data(), img.size()));
    printf("    su an '3' yazarak simuleMemory.txt ile karsilastir.\n");
}

// bolum arama (rva -> SecInfo; header icindeyse NULL)
static const SecInfo* FindSectionRVA(const std::vector<SecInfo>& secs, bool haveSecs,
                                     u32 rva, u32 hdrSize) {
    if (haveSecs && rva < hdrSize) return nullptr;
    for (auto& s : secs)
        if (rva >= s.rva && rva < s.rva + ((s.vsize) ? s.vsize : s.rawsize)) return &s;
    return nullptr;
}

// ---------------------------------------------------------------------------
// KOMUT 4: CANLI KENDI-GURULTUSU (iki canli dump, 1 sn arayla)
//   amac: sim'e HIC dokunmadan, canli goruntunun kendi icinde ne kadar
//   degistigini olcer. Iki canli dump arasinda da fark cikiyorsa, sim-vs-canli
//   farklarinin bir kismi "yakalanamaz taban-gurultu"dir (kanit olarak kullanilir).
// ---------------------------------------------------------------------------
static void DoLiveSelfNoise(DWORD pid) {
    printf("\n================================================================\n");
    printf(" CANLI KENDI-GURULTUSU: pid=%lu  modul=%s (iki dump, 1 sn arayla)\n", (unsigned long)pid, TARGET_DLL);
    printf("================================================================\n");

    ADR b1 = 0, b2 = 0; u32 s1 = 0, s2 = 0;
    std::vector<u8> img1, img2;
    std::string how1, how2, e1, e2;
    if (!ReadLiveImage(pid, img1, b1, s1, how1, e1)) { printf("[!] %s\n", e1.c_str()); return; }
    printf("[+] 1. dump OK (base=" FMTA " boyut=%X %s)\n", A(b1), s1, e1.c_str());
    Sleep(1000);
    if (!ReadLiveImage(pid, img2, b2, s2, how2, e2)) { printf("[!] %s\n", e2.c_str()); return; }
    printf("[+] 2. dump OK (base=" FMTA " boyut=%X %s)\n", A(b2), s2, e2.c_str());
    if (b1 != b2 || s1 != s2) { printf("[!] iki dump arasinda base/boyut degisti\n"); return; }

    size_t n = (img1.size() < img2.size()) ? img1.size() : img2.size();
    std::vector<std::pair<u32,u32>> regs;
    MergeDiffRegions(img1.data(), img2.data(), n, regs);
    size_t diffBytes = 0; for (auto& r : regs) diffBytes += r.second;

    // semantik: iki taraf da canli -> image araligi ayni
    u32 imgLo = (u32)b1, imgHi = (u32)(b1 + s1);
    std::map<std::string, std::pair<size_t,size_t>> sem;   // tag -> (byte, bolge)
    for (auto& r : regs) {
        const char* tag = SemanticTag(img1.data(), img2.data(), n, r.first, r.second,
                                      imgLo, imgHi, imgLo, imgHi, false);
        sem[tag].first  += r.second;
        sem[tag].second += 1;
    }

    printf("\n  iki canli dump arasi fark: %zu byte / %zu bolge (alan %.4f%%)\n",
           diffBytes, regs.size(), n ? 100.0 * (double)diffBytes / (double)n : 0.0);
    printf("  SEMANTIK:\n");
    for (auto& kv : sem)
        printf("    %-14s : %zu byte / %zu bolge\n", kv.first.c_str(), kv.second.first, kv.second.second);

    // 2. dump'i kanit olarak kaydet
    DumpInfo di;
    di.kind = "live"; di.mode = "rpm-2nd";
    di.module = TARGET_DLL; di.pid = pid; di.base = b2; di.size = s2;
    di.data = img2.data();
    di.note = "canli kendi-gurultusu kanit dump (1 sn sonra)";
    std::string outPath; bool usedTemp = false;
    if (PickOutPath(LIVE2_TXT, "dinamik_memory_2.txt", outPath, usedTemp)) {
        std::string werr;
        if (WriteDumpTxt(outPath, di, werr))
            printf("\n[i] 2. dump kaniti: %s%s\n", outPath.c_str(), usedTemp ? " (TEMP)" : "");
        else printf("[!] kanit dump yazilamadi: %s\n", werr.c_str());
    }

    printf("\n  YORUM:\n");
    if (diffBytes == 0)
        printf("    [i] iki canli dump birebir ayni -> bu process su an hareketli degil.\n");
    else {
        printf("    [i] canli goruntu 1 saniyede bile kendisiyle degisiyor (%zu byte).\n", diffBytes);
        printf("    -> sim-vs-canli diff'inde bu tur farklarin bir kismi GERCEK runtime gurultusudur;\n");
        printf("       100%% byte-eslesmesi iki CANLI dump arasinda bile mumkun degil.\n");
        printf("    -> hook avinda bunlar false-positive DEGILDIR: kod (EXEC) bolgelerine bak (komut 8).\n");
    }
}

// ---------------------------------------------------------------------------
// KOMUT 8: HOOK TARAMA
//   (a) EXEC/kod bolgelerinde sim-vs-canli byte diff  -> inline hook
//   (b) diff bolgelerindeki pointer'larin canli hedef-denetimi -> trampoline
//   (c) modul-disi EXEC bellek taramasi -> injected shellcode/manual-map
//   (d) modul listesi -> bilinmeyen DLL
// ---------------------------------------------------------------------------
static void DoHookScan(DWORD pid) {
    printf("\n================================================================\n");
    printf(" HOOK TARAMA: pid=%lu  modul=%s\n", (unsigned long)pid, TARGET_DLL);
    printf("================================================================\n");

    // 0) sim referansi
    std::string p1;
    if (!ResolveDumpPath(SIM_TXT, "simule_memory.txt", p1)) {
        printf("[!] %s yok -> once '1 <dll yolu>' ile simulasyon uret\n", SIM_TXT);
        return;
    }
    ParsedDump a; std::string rerr;
    if (!ReadDumpTxt(p1, a, rerr)) { printf("[!] sim dump bozuk: %s\n", rerr.c_str()); return; }

    // 1) canli goruntu
    ADR lbase = 0; u32 lsize = 0;
    std::vector<u8> live;
    std::string how, lerr;
    if (!ReadLiveImage(pid, live, lbase, lsize, how, lerr)) { printf("[!] %s\n", lerr.c_str()); return; }
    printf("[+] canli %s bulundu (%s): base=" FMTA " boyut=%X %s\n",
           TARGET_DLL, how.c_str(), A(lbase), lsize, lerr.c_str());

    u64 sbase = a.GetHex64("base");
    u32 ssize = a.GetHex("size");
    if (sbase != (u64)lbase || ssize != lsize)
        printf("[!] UYARI: sim(base=%s size=%X) != canli(base=" FMTA " size=%X) -> pointer farklari guvenilmez\n",
               a.Get("base").c_str(), ssize, A(lbase), lsize);

    size_t n = (a.bytes.size() < live.size()) ? a.bytes.size() : live.size();

    // 2) bolge haritasi (modul + exec taramasi icin) - handle acik kalsin
    HANDLE h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pid);
    RemoteMaps rm;
    bool haveMaps = false;
    if (h) haveMaps = BuildRemoteMaps(h, pid, rm);
    if (!haveMaps) printf("[!] modul/bolge haritasi alinamadi -> pointer denetimi sinirli\n");

    // ---- (a) EXEC/KOD bolgelerinde byte diff ----
    u32 hdrSize = 0;
    std::vector<SecInfo> secs; std::string serr;
    bool haveSecs = ParseImageSections(a.bytes.data(), a.bytes.size(), hdrSize, secs, serr);
    struct ExecDiff { char name[9]; u32 rva, vsize, diffs; };
    std::vector<ExecDiff> execDiffs;
    size_t execTotal = 0;
    if (haveSecs) {
        for (auto& s : secs) {
            if (!(s.chars & IMAGE_SCN_MEM_EXECUTE)) continue;
            u32 lo = s.rva, hi = s.rva + s.vsize;
            if (hi > n) hi = (u32)n;
            if (lo >= hi) continue;
            u32 d = 0;
            for (u32 i = lo; i < hi; i++) if (a.bytes[i] != live[i]) d++;
            ExecDiff ed{}; memcpy(ed.name, s.name, 8); ed.name[8] = 0;
            ed.rva = lo; ed.vsize = hi - lo; ed.diffs = d;
            execDiffs.push_back(ed);
            execTotal += d;
        }
    }
    printf("\n  (a) EXEC/KOD bolgeleri (sim vs canli, inline-hook avı):\n");
    if (!haveSecs) printf("      [!] bolum haritasi yok: %s\n", serr.c_str());
    for (auto& ed : execDiffs)
        printf("      %-8.8s RVA %06X +%06X : %u byte fark%s\n",
               ed.name, ed.rva, ed.vsize, ed.diffs, ed.diffs ? "   <<< INLINE-HOOK SUPHELISI" : "  (temiz)");
    if (execTotal == 0 && haveSecs)
        printf("      -> KOD KATMANI TEMIZ: python27.dll icinde byte-level inline-hook YOK (0 gurultu).\n");

    // ---- (b) tum diff bolgeleri + pointer hedef-denetimi ----
    std::vector<std::pair<u32,u32>> regs;
    MergeDiffRegions(a.bytes.data(), live.data(), n, regs);
    size_t diffBytes = 0; for (auto& r : regs) diffBytes += r.second;

    u32 e_pe = *(const u32*)(a.bytes.data() + 0x3C);
    u32 optOff = e_pe + 24;
    u16 optSize16 = *(const u16*)(a.bytes.data() + e_pe + 20);
    u32 secTable = optOff + optSize16;
    u32 secTableEnd = secTable + (u32)secs.size() * 40;
    u32 ddImpRva = *(const u32*)(a.bytes.data() + optOff + 96 + 1*8);
    u32 ddImpSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 1*8 + 4);
    u32 ddIatRva = *(const u32*)(a.bytes.data() + optOff + 96 + 12*8);
    u32 ddIatSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 12*8 + 4);
    u32 ddRelRva = *(const u32*)(a.bytes.data() + optOff + 96 + 5*8);
    u32 ddRelSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 5*8 + 4);

    auto InDD = [](u32 rva, u32 lo, u32 sz) { return sz && rva >= lo && rva < lo + sz; };
    auto IsPkHdrRegion = [&](u32 rva, u32 len) -> bool {
        for (u32 q = 0; q < len; q++) {
            u32 rr = rva + q;
            if (rr < secTable || rr >= secTableEnd) return false;
            u32 idx = (rr - secTable) / 40, off = (rr - secTable) % 40;
            if (idx >= secs.size()) return false;
            if (!(off >= 16 && off < 24)) return false;   // SizeOfRawData + PointerToRawData
            if (secs[idx].rawsize != 0) return false;     // sadece packer (rawsize=0) bolumu
        }
        return true;
    };

    u32 img1Lo = (u32)sbase, img1Hi = (u32)(sbase + ssize);
    u32 img2Lo = (u32)lbase, img2Hi = (u32)(lbase + lsize);
    std::map<std::string, std::pair<size_t,size_t>> sem;   // tag -> (byte, bolge)
    std::map<std::string, int> tgtCnt;                     // hedef turu sayaci
    std::map<std::string, int> crossMod;                   // baska modulu gosteren ptr'ler (bilgi)
    struct Suspect { u32 rva; u32 from, to; char tgt[80]; };
    std::vector<Suspect> suspects;
    size_t iatDiffB = 0, relDiffB = 0, pksB = 0;

    for (auto& r : regs) {
        bool pk = haveSecs && IsPkHdrRegion(r.first, r.second);
        if (pk) pksB += r.second;
        if (InDD(r.first, ddImpRva, ddImpSz) || InDD(r.first, ddIatRva, ddIatSz)) iatDiffB += r.second;
        if (InDD(r.first, ddRelRva, ddRelSz)) relDiffB += r.second;

        const char* tag = SemanticTag(a.bytes.data(), live.data(), n, r.first, r.second,
                                      img1Lo, img1Hi, img2Lo, img2Hi, pk);
        sem[tag].first  += r.second;
        sem[tag].second += 1;

        if (haveMaps) {
            u32 w0 = r.first & ~3u, w1 = (r.first + r.second - 1) & ~3u;
            for (u32 off = w0; off <= w1 && off + 4 <= n; off += 4) {
                u32 v1, v2;
                memcpy(&v1, a.bytes.data() + off, 4);
                memcpy(&v2, live.data() + off, 4);
                if (v1 == v2) continue;
                if (!PtrLike(v2)) continue;
                char tg[80];
                ClassifyTarget(rm, v2, tg, sizeof(tg));
                tgtCnt[tg]++;
                if (strstr(tg, "supheli") || strstr(tg, "modul-listesi-disi")) {
                    // hook hedefi: modul-disi calistirilabilir bellek
                    Suspect sp{};
                    sp.rva = off; sp.from = v1; sp.to = v2;
                    snprintf(sp.tgt, sizeof(sp.tgt), "%s", tg);
                    suspects.push_back(sp);
                } else if (!strncmp(tg, "MODUL(", 6)) {
                    std::string mn(tg + 6);
                    size_t rb = mn.find(')');
                    if (rb != std::string::npos) mn = mn.substr(0, rb);
                    if (!Ieq(mn, TARGET_DLL)) crossMod[mn]++;   // baska modulu gosteren ptr (bilgi)
                }
            }
        }
    }

    printf("\n  (b) fark bolgeleri semantigi (canli taraf pointer-hedef denetimiyle):\n");
    printf("      toplam fark: %zu byte / %zu bolge\n", diffBytes, regs.size());
    for (auto& kv : sem)
        printf("      %-14s : %zu byte / %zu bolge\n", kv.first.c_str(), kv.second.first, kv.second.second);
    printf("      loader-yapisal: IAT/IMPORT fark=%zu byte, BASERELOC fark=%zu byte, packer-header(PKS)=%zu byte\n",
           iatDiffB, relDiffB, pksB);
    if (haveMaps) {
        printf("      canli pointer hedef dagilimi:\n");
        for (auto& kv : tgtCnt) printf("        %-36s : %d word\n", kv.first.c_str(), kv.second);
    }

    printf("\n  (b2) SUPHELI pointer hedefleri:\n");
    if (suspects.empty()) {
        printf("      YOK -> diff bolgelerindeki hicbir canli pointer modul-disi\n");
        printf("           calistirilabilir bellege isaret etmiyor (trampoline yok).\n");
    } else {
        int shown = 0;
        for (auto& sp : suspects) {
            if (shown++ >= 32) { printf("      ... ve %d supheli daha (raporda)\n", (int)suspects.size() - 32); break; }
            printf("      RVA %08X: sim=%08X -> canli=%08X  hedef=%s\n", sp.rva, sp.from, sp.to, sp.tgt);
        }
    }
    if (!crossMod.empty()) {
        printf("      [i] python27-disi MODULLERE isaret eden fark pointer'lari (bilgi - genelde).");
        printf("\n          statik fonksiyon ptr'leri; hook arastirilacaksa isimlere bak):\n");
        for (auto& kv : crossMod) printf("        MODUL %-24s : %d word\n", kv.first.c_str(), kv.second);
    }

    // ---- (c) modul-disi EXEC bolgeler ----
    printf("\n  (c) MODUL-DISI calistirilabilir bellek bolgeleri (shellcode/manual-map avi):\n");
    int execAnon = 0, execMapped = 0, execImageGhost = 0;
    if (haveMaps) {
        for (auto& r : rm.regions) {
            if (r.state != MEM_COMMIT || !ExecProtect(r.protect)) continue;
            if (ModOf(rm, r.base)) continue;   // bilinen modul icinde
            u8 head[16] = {};
            SIZE_T got = 0;
            bool readable = h && ReadProcessMemory(h, (LPCVOID)r.base, head, sizeof(head), &got) && got == sizeof(head);
            if (r.type == MEM_PRIVATE) {
                execAnon++;
                printf("      [!] ANONIM-EXEC base=" FMTA " boyut=%llu protect=%08X ilk16: ", A(r.base), (unsigned long long)r.size, r.protect);
                for (int q = 0; q < 16; q++) printf("%02X ", head[q]);
                printf("%s\n", readable ? "" : "(okunamadi)");
            } else if (r.type == MEM_MAPPED) {
                execMapped++;
                printf("      [i] MAPPED-EXEC base=" FMTA " boyut=%llu protect=%08X\n", A(r.base), (unsigned long long)r.size, r.protect);
            } else if (r.type == MEM_IMAGE) {
                execImageGhost++;
                printf("      [!] IMAGE-EXEC ama modul listesi DISINDA base=" FMTA " boyut=%llu (manuel-map?)\n", A(r.base), (unsigned long long)r.size);
            }
        }
        if (!execAnon && !execImageGhost && !execMapped)
            printf("      YOK -> tum EXEC bolgeler bilinen modullerin icinde.\n");
    }

    // ---- (d) modul listesi ----
    printf("\n  (d) MODUL LISTESI (%d adet):\n", (int)rm.mods.size());
    for (auto& m : rm.mods)
        printf("      %-24s base=" FMTA " size=%X  %s\n", m.name.c_str(), A(m.base), m.size, m.path.c_str());

    // ---- rapor + verdict ----
    {
        std::string rp; bool ut = false;
        PickOutPath(HOOK_TXT, "i4msim_hookscan.txt", rp, ut);
        FILE* f = fopen(rp.c_str(), "wb");
        if (f) {
            fprintf(f, "i4MSim v1.8 hook-tarama raporu  pid=%lu  %s\n", (unsigned long)pid, TARGET_DLL);
            fprintf(f, "sim=%s fnv=%s\n", p1.c_str(), a.Get("fnv64").c_str());
            fprintf(f, "canli base=" FMTA " boyut=%X\n\n", A(lbase), lsize);
            fprintf(f, "[a] EXEC/KOD diff:\n");
            for (auto& ed : execDiffs)
                fprintf(f, "  %-8.8s RVA %06X +%06X : %u byte fark\n", ed.name, ed.rva, ed.vsize, ed.diffs);
            fprintf(f, "\n[b] diff bolgeleri (%zu byte / %zu bolge):\n", diffBytes, regs.size());
            for (auto& kv : sem) fprintf(f, "  %-14s : %zu byte / %zu bolge\n", kv.first.c_str(), kv.second.first, kv.second.second);
            fprintf(f, "\n[b2] supheli pointer hedefleri: %d\n", (int)suspects.size());
            for (auto& sp : suspects)
                fprintf(f, "  RVA %08X: sim=%08X -> canli=%08X  hedef=%s\n", sp.rva, sp.from, sp.to, sp.tgt);
            for (auto& kv : crossMod)
                fprintf(f, "  [i] cross-modul ptr: MODUL %s x%d\n", kv.first.c_str(), kv.second);
            fprintf(f, "\n[c] modul-disi EXEC: anonim=%d mapped=%d image-ghost=%d\n", execAnon, execMapped, execImageGhost);
            fprintf(f, "\n[d] moduller: %d\n", (int)rm.mods.size());
            for (auto& m : rm.mods) fprintf(f, "  %-24s base=" FMTA " size=%X %s\n", m.name.c_str(), A(m.base), m.size, m.path.c_str());
            fclose(f);
            printf("\n[i] rapor: %s\n", rp.c_str());
        }
    }

    printf("\n  HOOK-VERDICT:\n");
    bool codeClean = (execTotal == 0);
    bool iatClean  = (iatDiffB == 0);
    bool ptrClean  = suspects.empty();
    bool memClean  = (execAnon == 0 && execImageGhost == 0);
    if (codeClean && iatClean && ptrClean && memClean) {
        printf("    [OK] python27.dll KOD bolgeleri sim ile BIREBIR (inline-hook YOK).\n");
        printf("    [OK] IAT/IMPORT farki YOK (IAT-hook YOK).\n");
        printf("    [OK] diff pointer'larinin hicbiri modul-disi EXEC bellege isaret etmiyor (trampoline YOK).\n");
        printf("    [OK] modul-disi anonim/ghost EXEC bolge YOK (enjekte kod yok).\n");
        printf("    -> kalan fark tamami VERI bolgesinde runtime gurultusu (HPTR-ASLR/CNT/PATH).\n");
    } else {
        if (!codeClean) printf("    [!!] KOD bolgesinde %zu byte fark -> inline hook veya unpack eksigi! (raporu incele)\n", execTotal);
        if (!iatClean)  printf("    [!!] IAT/IMPORT bolgesinde fark -> IAT-hook olasiligi!\n");
        if (!ptrClean)  printf("    [!!] %d pointer supheli hedefe isaret ediyor -> trampoline/yondlendirme incelenmeli\n", (int)suspects.size());
        if (!memClean)  printf("    [!!] modul-disi EXEC bellek VAR -> enjekte kod/manual-map incelenmeli\n");
        printf("    -> %s raporunu incele (bolum: b2 ve c).\n", HOOK_TXT);
    }
    if (h) CloseHandle(h);
}
static bool ResolveDumpPath(const char* cPath, const char* tempName, std::string& out) {
    FILE* t = fopen(cPath, "rb");
    if (t) { fclose(t); out = cPath; return true; }
    char tp[MAX_PATH] = {};
    if (GetTempPathA(MAX_PATH, tp)) {
        std::string alt = std::string(tp) + tempName;
        FILE* t2 = fopen(alt.c_str(), "rb");
        if (t2) { fclose(t2); out = alt; return true; }
    }
    return false;
}

static void DoCompare() {
    std::string p1, p2;
    bool have1 = ResolveDumpPath(SIM_TXT,  "simule_memory.txt",  p1);
    bool have2 = ResolveDumpPath(LIVE_TXT, "dinamik_memory.txt", p2);

    printf("\n================================================================\n");
    printf(" KARSILASTIRMA (simule x1 vs canli x2): %s\n", TARGET_DLL);
    printf("================================================================\n");
    if (!have1) { printf("[!] %s yok -> once '1 <dll yolu>' calistir\n", SIM_TXT); return; }
    if (!have2) { printf("[!] %s yok -> once '2 <pid>' calistir\n", LIVE_TXT); return; }

    ParsedDump a, b;
    std::string e1, e2;
    if (!ReadDumpTxt(p1, a, e1)) { printf("[!] simule dump bozuk: %s\n", e1.c_str()); return; }
    if (!ReadDumpTxt(p2, b, e2)) { printf("[!] canli dump bozuk: %s\n", e2.c_str()); return; }

    // dosya butunlugu
    u64 f1 = Fnv64(a.bytes.data(), a.bytes.size());
    u64 f2 = Fnv64(b.bytes.data(), b.bytes.size());
    u64 m1 = strtoull(a.Get("fnv64", "0").c_str(), nullptr, 16);
    u64 m2 = strtoull(b.Get("fnv64", "0").c_str(), nullptr, 16);
    printf("  simule (x1) : %s\n", p1.c_str());
    printf("                %s modu | pid=%s | base=" FMTA " | boyut=%X | kayit=%s\n",
           a.Get("mode").c_str(), a.Get("pid").c_str(), A(a.GetHex64("base")), a.GetHex("size"), a.Get("saved").c_str());
    printf("  canli  (x2) : %s\n", p2.c_str());
    printf("                pid=%s | base=" FMTA " | boyut=%X | kayit=%s\n",
           b.Get("pid").c_str(), A(b.GetHex64("base")), b.GetHex("size"), b.Get("saved").c_str());
    printf("  fnv x1      : %016llX %s\n", (unsigned long long)f1,
           f1 == m1 ? "(dosya dogrulandi)" : "[!!] META ILE UYUSMUYOR - dosya bozuk/eski");
    printf("  fnv x2      : %016llX %s\n", (unsigned long long)f2,
           f2 == m2 ? "(dosya dogrulandi)" : "[!!] META ILE UYUSMUYOR - dosya bozuk/eski");

    u64 b1 = a.GetHex64("base"), b2 = b.GetHex64("base");
    size_t s1 = a.bytes.size(), s2 = b.bytes.size();
    printf("  base        : %s (x1=" FMTA " x2=" FMTA ")\n", b1 == b2 ? "AYNI" : "FARKLI", A(b1), A(b2));
    printf("  boyut       : %s (x1=%zu x2=%zu)\n", s1 == s2 ? "AYNI" : "FARKLI", s1, s2);
    if (b1 != b2)
        printf("  [!] base farkli: x2 tarafinda relocation uygulanmis -> pointer byte'lari farkli cikar (beklenen)\n");
    size_t n = (s1 < s2) ? s1 : s2;
    if (s1 != s2) printf("  [i] ortak alanda karsilastiriliyor: %zu byte\n", n);
    if (n == 0) { printf("[!] karsilastirilacak byte yok\n"); return; }

    // fark bolgelerini topla (8 byte'a kadar komsulari birlestir)
    struct Reg { u32 rva; u32 len; u32 exact; const char* tag; };
    std::vector<Reg> regs;
    for (size_t i = 0; i < n; i++) {
        if (a.bytes[i] != b.bytes[i]) {
            if (!regs.empty() && (u32)i - (regs.back().rva + regs.back().len) <= 8) {
                regs.back().len = (u32)(i + 1 - regs.back().rva);
                regs.back().exact++;
            } else regs.push_back({ (u32)i, 1, 1, "VERI" });
        }
    }
    size_t diffBytes = 0, spanBytes = 0;
    for (auto& r : regs) { diffBytes += r.exact; spanBytes += r.len; }
    double pct = 100.0 * (double)diffBytes / (double)n;
    double match = 100.0 - pct;

    printf("\n  KARSILASTIRMA [base .. base+boyut):\n");
    printf("    karsilastirilan : %zu byte\n", n);
    printf("    farkli byte     : %zu / %zu (%.4f%%)\n", diffBytes, n, pct);
    printf("    farkli bolge    : %zu (bitisik birlesik kaplama: %zu byte)\n", regs.size(), spanBytes);

    // bolum haritasi (x1 header'indan)
    u32 hdrSize = 0;
    std::vector<SecInfo> secs;
    std::string serr;
    bool haveSecs = ParseImageSections(a.bytes.data(), a.bytes.size(), hdrSize, secs, serr);
    if (haveSecs) {
        printf("\n  bolumler (x1 header'indan):\n");
        for (auto& s : secs)
            printf("    %-8.8s RVA %06X vsize %06X raw %06X %s\n",
                   s.name, s.rva, s.vsize, s.rawsize,
                   (s.rawsize == 0 && (s.chars & IMAGE_SCN_MEM_EXECUTE)) ? "[PK] packer-unpacked KOD"
                   : (s.rawsize == 0)                                    ? "[PK] packer-unpacked"
                                                                         : "[DS] diskten gelen");
    }

    // bolum bazli dagilim
    auto FindSec = [&](u32 rva) -> const SecInfo* {
        if (haveSecs && rva < hdrSize) return nullptr;   // header
        for (auto& s : secs)
            if (rva >= s.rva && rva < s.rva + ((s.vsize) ? s.vsize : s.rawsize)) return &s;
        return nullptr;
    };
    size_t pkB = 0, pkR = 0, dsB = 0, dsR = 0, hdB = 0, hdR = 0, ooB = 0, ooR = 0;
    for (auto& r : regs) {
        const SecInfo* s = FindSec(r.rva);
        if (!haveSecs)                    { ooB += r.exact; ooR++; }
        else if (!s)                      { hdB += r.exact; hdR++; }
        else if (s->rawsize == 0)         { pkB += r.exact; pkR++; }
        else                              { dsB += r.exact; dsR++; }
    }
    printf("\n  SINIFLANDIRMA:\n");
    printf("    [HDR] header               : %zu byte / %zu bolge\n", hdB, hdR);
    printf("    [PK]  packer-unpacked KOD  : %zu byte / %zu bolge\n", pkB, pkR);
    printf("    [DS]  diskten-gelen VERI   : %zu byte / %zu bolge\n", dsB, dsR);
    if (!haveSecs) printf("    [??]  bolum haritasi yok   : %zu byte / %zu bolge\n", ooB, ooR);

    // ---- v1.8: SEMANTIK siniflandirma + loader-yapisal toplamlar ----
    u32 e_pe = *(const u32*)(a.bytes.data() + 0x3C);
    u32 optOff = e_pe + 24;
    u16 optSize16 = *(const u16*)(a.bytes.data() + e_pe + 20);
    u32 secTable = optOff + optSize16;
    u32 secTableEnd = secTable + (u32)secs.size() * 40;
    u32 ddImpRva = *(const u32*)(a.bytes.data() + optOff + 96 + 1*8);
    u32 ddImpSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 1*8 + 4);
    u32 ddIatRva = *(const u32*)(a.bytes.data() + optOff + 96 + 12*8);
    u32 ddIatSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 12*8 + 4);
    u32 ddRelRva = *(const u32*)(a.bytes.data() + optOff + 96 + 5*8);
    u32 ddRelSz  = *(const u32*)(a.bytes.data() + optOff + 96 + 5*8 + 4);
    auto InDD = [](u32 rva, u32 lo, u32 sz) { return sz && rva >= lo && rva < lo + sz; };
    auto IsPkHdrRegion = [&](u32 rva, u32 len) -> bool {
        for (u32 q = 0; q < len; q++) {
            u32 rr = rva + q;
            if (rr < secTable || rr >= secTableEnd) return false;
            u32 idx = (rr - secTable) / 40, off2 = (rr - secTable) % 40;
            if (idx >= secs.size()) return false;
            if (!(off2 >= 16 && off2 < 24)) return false;   // SizeOfRawData + PointerToRawData
            if (secs[idx].rawsize != 0) return false;       // sadece packer (rawsize=0) bolumu
        }
        return true;
    };
    u32 img1Lo = (u32)b1, img1Hi = (u32)(b1 + a.bytes.size());
    u32 img2Lo = (u32)b2, img2Hi = (u32)(b2 + b.bytes.size());
    std::map<std::string, std::pair<size_t,size_t>> sem;   // tag -> (byte, bolge)
    size_t execB2 = 0, iatB2 = 0, relB2 = 0, pksB2 = 0;
    for (auto& r : regs) {
        bool pk = haveSecs && IsPkHdrRegion(r.rva, r.len);
        if (pk) pksB2 += r.exact;
        const SecInfo* sec2 = FindSec(r.rva);
        if (sec2 && (sec2->chars & IMAGE_SCN_MEM_EXECUTE)) execB2 += r.exact;
        if (InDD(r.rva, ddImpRva, ddImpSz) || InDD(r.rva, ddIatRva, ddIatSz)) iatB2 += r.exact;
        if (InDD(r.rva, ddRelRva, ddRelSz)) relB2 += r.exact;
        const char* tg = SemanticTag(a.bytes.data(), b.bytes.data(), n, r.rva, r.len,
                                     img1Lo, img1Hi, img2Lo, img2Hi, pk);
        sem[tg].first += r.exact; sem[tg].second++;
        r.tag = tg;
    }
    printf("\n  SEMANTIK (v1.8; calisma-zamani dolum turleri):\n");
    for (auto& kv : sem)
        printf("    %-14s : %zu byte / %zu bolge\n", kv.first.c_str(), kv.second.first, kv.second.second);
    printf("  LOADER-YAPISAL: EXEC-KOD fark=%zu, IAT/IMPORT fark=%zu, BASERELOC fark=%zu, packer-header(PKS)=%zu\n",
           execB2, iatB2, relB2, pksB2);

    // detay (ilk 24)
    size_t show = regs.size() < 24 ? regs.size() : 24;
    if (show) {
        printf("\n  DETAY (ilk %zu bolge):\n", show);
        for (size_t i = 0; i < show; i++) {
            const Reg& r = regs[i];
            const SecInfo* s = FindSec(r.rva);
            const char* nm = (!haveSecs) ? "??" : (!s ? "header" : s->name);
            const char* tag = (!haveSecs) ? "[??]" : (!s ? "[HDR]" : (s->rawsize == 0 ? "[PK]" : "[DS]"));
            printf("    RVA %08X len=%-3u (fark %u) %-8.8s %s [%s]\n", r.rva, r.len, r.exact, nm, tag, r.tag);
            printf("      x1(sim): ");
            for (u32 k = 0; k < r.len && k < 16; k++) printf("%02X ", a.bytes[r.rva + k]);
            printf("\n      x2(can): ");
            for (u32 k = 0; k < r.len && k < 16; k++) printf("%02X ", b.bytes[r.rva + k]);
            printf("\n");
        }
        if (regs.size() > show)
            printf("    ... ve %zu bolge daha (tum farklar rapor dosyasinda)\n", regs.size() - show);
    }

    // tam rapor dosyasi
    {
        std::string rp; bool ut = false;
        PickOutPath("C:\\i4msim_diff.txt", "i4msim_diff.txt", rp, ut);
        FILE* f = fopen(rp.c_str(), "wb");
        if (f) {
            fprintf(f, "i4MSim diff raporu (x1 simule vs x2 canli)\n");
            fprintf(f, "x1=%s fnv=%016llX\nx2=%s fnv=%016llX\n", p1.c_str(), (unsigned long long)f1, p2.c_str(), (unsigned long long)f2);
            fprintf(f, "fark=%zu byte / %zu bolge (eslesme %.4f%%)\n\n", diffBytes, regs.size(), match);
            for (auto& r : regs) {
                const SecInfo* s = FindSec(r.rva);
                fprintf(f, "RVA %08X len=%u fark=%u %s %s [%s]\n", r.rva, r.len, r.exact,
                        (!haveSecs) ? "??" : (!s ? "header" : s->name),
                        (!haveSecs) ? "" : (!s ? "[HDR]" : (s->rawsize == 0 ? "[PK]" : "[DS]")),
                        r.tag);
                fprintf(f, "  x1:");
                for (u32 k = 0; k < r.len && k < 32; k++) fprintf(f, " %02X", a.bytes[r.rva + k]);
                fprintf(f, "\n  x2:");
                for (u32 k = 0; k < r.len && k < 32; k++) fprintf(f, " %02X", b.bytes[r.rva + k]);
                fprintf(f, "\n\n");
            }
            fclose(f);
            printf("\n[i] tum farklar: %s\n", rp.c_str());
        }
    }

    // VERDICT (v1.8: yapisal-vs-gurultu ayrimi)
    size_t hdrBadB = hdB > pksB2 ? (hdB - pksB2) : 0;   // PKS disi header farki
    printf("\n  VERDICT:\n");
    if (diffBytes == 0) {
        printf("    [OK] 0 FARK - SIMULASYON %%100 BIREBIR\n");
        printf("    diskteki dosya, hedef process'te yuklu halinin aynisi.\n");
    } else if (!haveSecs) {
        printf("    [??] bolum haritasi cozumlenemedi (%s) - siniflandirma yapilamadi.\n", serr.c_str());
        printf("    raporu incele: C:\\i4msim_diff.txt\n");
    } else if (execB2 == 0 && iatB2 == 0 && relB2 == 0 && hdrBadB == 0) {
        printf("    [OK] LOADER-YAPISAL 0 FARK: KOD(EXEC)+IAT+RELOC+HEADER temiz ->\n");
        printf("         python27.dll icinde inline-hook / IAT-hook YOK (kod katmani %%100 uretildi).\n");
        if (pksB2)
            printf("    [i]  %zu byte packer-kosmetik header farki (rawsize=0 bolumun disk-alani bilgisi; zararsiz).\n", pksB2);
        printf("    [i]  kalan fark canli process'in KENDI calisma-zamani dolumu:\n");
        for (auto& kv : sem)
            printf("           %-14s : %zu byte\n", kv.first.c_str(), kv.second.first);
        printf("         -> HPTR-ASLR: iki process'te heap adresleri farkli (yapisal olarak eslesemez);\n");
        printf("            iki CANLI dump arasinda bile fark cikar -> '4 <pid>' ile kanitla.\n");
        printf("    [i]  hook avina gecis: '8 <pid>' (EXEC-diff + trampoline + modul-disi EXEC + modul listesi).\n");
    } else {
        printf("    [!!] YAPISAL fark VAR: EXEC-KOD=%zu IAT=%zu RELOC=%zu HDR(yapisal)=%zu byte.\n",
               execB2, iatB2, relB2, hdrBadB);
        printf("    ya simulasyon tarafinda unpack tamamlanmadi, ya canli tarafta mudahale (hook) var.\n");
        printf("    -> '8 <pid>' ile hook taramasi yap, sonra C:\\i4msim_diff.txt raporunu gonder.\n");
    }
    printf("    eslesme: %.4f%%\n", match);
}

// ---------------------------------------------------------------------------
// banner + menu
// ---------------------------------------------------------------------------
static void Banner() {
    printf("============================================================\n");
    printf(" %s - DLL yuklu-hal SIMULASYONU + HOOK TARAMASI\n", TOOL_VER);
    printf(" motor: i4MConsoleLoader/PEManualMapper + GERCEK loader calistirma\n");
    printf(" amac : herhangi bir DLL disk -> process-dinamik hali (packer unpack DAHIL)\n");
    printf("============================================================\n");
    printf(" 1 <dll yolu>   -> C:\\simule_memory.txt   (simule dinamik goruntu)\n");
    printf(" 2 <pid>        -> C:\\dinamik_memory.txt  (canli goruntu, base..end)\n");
    printf(" 3              -> byte-byte + SEMANTIK siniflandirma (v1.8)\n");
    printf(" 4 <pid>        -> canlinin KENDI gurultusu (iki canli dump, 1 sn arayla)\n");
    printf(" 5 <dll yolu>   -> zorla MANUAL-MAP modu (PEManualMapper + TLS + DllMain)\n");
    printf(" 6 <dll yolu>   -> zorla GERCEK-LOADER modu (LoadLibraryEx)\n");
    printf(" 8 <pid>        -> HOOK TARAMA (EXEC-diff + trampoline + modul-disi EXEC)\n");
    printf(" help | quit\n");
    printf("============================================================\n");
}

static void Usage() {
    printf("Ornek:\n");
    printf("  1 C:\\Users\\Admin\\Desktop\\NightTownFullpack\\python27.dll\n");
    printf("  2 1234\n");
    printf("  3\n");
    printf("  8 1234      (hook tarama: sim referansi gerekir, once '1')\n");
    printf("Akis: once 1 (simulasyon), sonra 2 (canli), sonra 3 (karsilastirma).\n");
    printf("Hook avina: 8 (kod+trampoline+enjeksiyon) -> rapor: C:\\i4msim_hookscan.txt\n");
    printf("cmd1 feda-i process kullanir: arac kendini %%TEMP%%\\i4MHost\\metin2client.exe\n");
    printf("olarak kopyalayip oradan yukler (pack host-adi kontrolune karsi).\n");
}

int main(int argc, char** argv) {
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);

    // cocuk modlari
    if (argc >= 3 && !strcmp(argv[1], "--simlib")) return RunSimChildLib(argv[2]);
    if (argc >= 3 && !strcmp(argv[1], "--simmap")) return RunSimChildMap(argv[2]);

    // tek atimlik modlar
    if (argc >= 3 && !strcmp(argv[1], "1")) { DoSimulate(argv[2], false); return 0; }
    if (argc >= 3 && !strcmp(argv[1], "5")) { DoSimulate(argv[2], true);  return 0; }
    if (argc >= 3 && !strcmp(argv[1], "6")) { DoSimulate(argv[2], false); return 0; }
    if (argc >= 3 && !strcmp(argv[1], "2")) { DoLiveDump((DWORD)strtoul(argv[2], NULL, 0)); return 0; }
    if (argc >= 2 && !strcmp(argv[1], "3")) { DoCompare(); return 0; }
    if (argc >= 3 && !strcmp(argv[1], "4")) { DoLiveSelfNoise((DWORD)strtoul(argv[2], NULL, 0)); return 0; }
    if (argc >= 3 && !strcmp(argv[1], "8")) { DoHookScan((DWORD)strtoul(argv[2], NULL, 0)); return 0; }

    Banner();
    char line[2048];
    for (;;) {
        printf("\ni4MSim> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) break;
        std::string s = Trim(line);
        if (s.empty()) continue;

        size_t sp = s.find_first_of(" \t");
        std::string cmd = (sp == std::string::npos) ? s : s.substr(0, sp);
        std::string arg = (sp == std::string::npos) ? "" : Trim(s.substr(sp + 1));
        cmd = Lower(cmd);

        if (cmd == "1" || cmd == "sim") {
            if (arg.empty()) printf("[!] kullanim: 1 <dll yolu>\n");
            else DoSimulate(arg, false);
        } else if (cmd == "5") {
            if (arg.empty()) printf("[!] kullanim: 5 <dll yolu>\n");
            else DoSimulate(arg, true);
        } else if (cmd == "6") {
            if (arg.empty()) printf("[!] kullanim: 6 <dll yolu>\n");
            else DoSimulate(arg, false);
        } else if (cmd == "2" || cmd == "dump") {
            if (arg.empty()) printf("[!] kullanim: 2 <pid>\n");
            else DoLiveDump((DWORD)strtoul(arg.c_str(), NULL, 0));
        } else if (cmd == "3" || cmd == "cmp") {
            DoCompare();
        } else if (cmd == "4" || cmd == "noise") {
            if (arg.empty()) printf("[!] kullanim: 4 <pid>\n");
            else DoLiveSelfNoise((DWORD)strtoul(arg.c_str(), NULL, 0));
        } else if (cmd == "8" || cmd == "hook") {
            if (arg.empty()) printf("[!] kullanim: 8 <pid>\n");
            else DoHookScan((DWORD)strtoul(arg.c_str(), NULL, 0));
        } else if (cmd == "help" || cmd == "?") {
            Usage();
        } else if (cmd == "quit" || cmd == "exit" || cmd == "q") {
            break;
        } else {
            printf("[?] bilinmeyen komut: %s  (help yaz)\n", cmd.c_str());
        }
    }
    return 0;
}
