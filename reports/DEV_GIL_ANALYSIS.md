# DEV_GIL_ANALYSIS — MaximumPyScript1 Tüm Sürümlerin Analizi + GIL/RENDER/NPC Hata Kökenleri

> **Kaynaklar:** `/home/z/my-project/extracted/MaximumPyScript1/` (77 dosya), `/home/z/my-project/extracted/cppcmpr/cppcmpr/`, `/home/z/my-project/extracted/win32apiMetin2Py/win32apiMetin2Py/`
> **Hedef:** "Script oyuna girince GIL hatası veriyor, NPC'ler yüklenmiyor" sorununun kaynağını satır satır göstermek ve stabilize yolunu çizmek.
> **Referans sohbetler:** `uploads/Prestige Silver Atılma Azaltma.md`, `uploads/Hooking Breakpoints & Redirecting Commands.md`

---

## 1. KRONOLOJİ TABLOSU (sürüm sırası kanıtlarıyla)

| # | Dosya | Sürüm kanıtı | Mimari | Hüküm |
|---|---|---|---|---|
| 1 | `Script2..Script4.txt` | "Auto Login Script v3/v4", tek-seferlik `gc.get_objects()` taramaları | Ana thread'de tek-seferlik `py exec(...)`, SHM yok, thread yok | Teşhis aracı, eskimiş |
| 2 | `recorderbase.txt` | "Dialog Recorder v3" | Tüm görünür nesnelerin agresif taraması + `TextLine.SetText` hook + `Interface`/`PopupDialog` hook'ları | Bozuk (crash'li hook'lar) |
| 3 | `recorder.txt` | "Recorder v10" | gc-temelli `LoginWindow` bulma, event hook'ları, 20ms dinleyici | Kararsız |
| 4 | `recorder_.txt` | "Recorder v11 – Login Attempt Aware" | `net.SendLoginPacket` hook, sınıf-seviyesi LoginWindow hook | Kararsız |
| 5 | `recorder_v11.txt`, `recorder_v12.txt` | "v11/v12 – Coalesce Fix" | **20ms dinleyici döngüsü İÇİNDE `gc.get_objects()`** (v11:1119, v12:1146) | BOZUK (render crash) |
| 6 | `recorder_v13.txt` | "v14 – CRASH FIX + CHAT HOOK" (dosya adı v13) | gc taraması / app.Update / popup-poll **kaldırıldı**; chat hook eklendi | Kısmi düzeltme |
| 7 | `recorder_v14.txt` | "v14 – Crash Fix + Refine Capture" | Popup yoklaması 0.5sn'de bir **gc ile** (1186, 1232); TextLine hook kaldırıldı ("crash sebebi!" başlık 13-16) | Kararsız |
| 8 | `recorder_v15.txt`, `recorder_v20.txt` | "v15 – Render Fix" (v20 dosyası = ikinci v15) | gc yoklamadan çıkarıldı, weakref'ler, sleep 20→50ms ("render bozma sebebi" v20:10) | STABİLE-YAKIN |
| 9 | `recorder_v16.txt`, `recorder_v17.txt` | "v16 WeakRef" / "v17 No Polling, Hooks Only" | v17: yalnız hook, gc yalnız init'te | Stabile-yakın |
| 10 | `recorder_v18.txt`, `recorder_v19.txt`, `recorder_v19_.txt` | "Ultimate String Recorder v18/v19 – TOTAL CAPTURE", "BEYAZ LİSTE" | `chat`, diyaloglar, `GameWindow.BINARY_ServerCommand_Run`, `net.Send*`, `__import__`, lazy 2sn modül taraması hook'ları | Kararsız (spam, aşırı yük) |
| 11 | `MaximumScript.txt` | **"v1.0"**, SHM `Control_{PID}` 64KB, magic `0x4D543243`, JSON status/komut @+32768 (8-14. satırlar) | Background thread main_loop (1528), JSON SHM, gc find_obj | Bozuk/kararsız |
| 12 | `MaximumPyScript__.txt` | **"v1.2 – TAM DÜZELTİLMİŞ"** | Blokalamayan durum makinesi, Python thread'den `app.Pump/ProcessMessage/Update` çağıran `pump_game()` (307-316) | BOZUK (re-entrancy) |
| 13 | `MaximumPyScript_.txt` | "Tüm Otomasyon Tek Script" (v1-öncesi, POLL_INTERVAL 0.05, satır 39) | 13-bölümlü monolit, thread `ipc_main_loop` (1482), recorder entegre | Bozuk |
| 14 | `MaximumPyScriptX.txt` | `VERSION = 1` (satır 72), "MaximumController.exe" ifadesi | Binary SHM geçişi, chat+login hook'lu Recorder, thread (2048) | Kararsız |
| 15 | `MaximumPyScript.txt` | **"v3"** (`VERSION = 3` satır 73) | 16KB binary SHM magic `0x4D415831`, COMMAND_POLL 0.15, `app.Pump` gitti, tam otomatik akış | Kararsız |
| 16 | `MaximumPyScript1.txt` | **"v3.1"** (v3 başlığı + `IN_GAME_POLL = 2.0` satır 33, `CHAR_AUTO_REFRESH = 2.0` satır 32) | v3 + oyun-içi pasif mod, karakter otomatik tazeleme | Kararsız |
| 17 | `MaximumPyScriptv2.txt` | **"v4"** (`VERSION = 4` satır 80), CMD_COMPLETE_ALL, stratejiler | v3.1 + complete-all durum makinesi | Kararsız |
| 18 | `MaximumPyScript3.txt` | **"v5 – GIL/Render Fix"** (başlık 7-11) | gc taraması bir kez cache'lendi (`_gc_scan_once` 740-758), oyun-içi pasif (IN_GAME_POLL 5.0) | Yarı-stabil |
| 19 | `MaximumPyScript4.txt` | **"v7 – FINAL (Hook-Safe + GIL-Safe + Input-Safe)"** (başlık 6-10) | chat hook yalnız menüde, oyuna girmeden önce kaldırılıyor (647-650), gc cache'li, poll 0.3 | **STABİLE-YAKIN** (`maximum_log.txt` ile kanıtlı) |
| 20 | `MaximumPyScript_Merged_calisan.py` | **"v14 – GIL-SAFE: Hooks + Scene Track + SHM Cmd"** (başlık 4-13) | SetPhaseWindow hook, gc hiç yok, `_le_mod` loginevent proxy, thread start (1877) | **EN YENİ #1 (stabile yakın)** |
| 21 | `MaximumPyScript_Merged.py` | **"v17 – FOCUS FIX v2 + GIL-SAFE"** (başlık 4-17) | v14 + SetFocus yönetimi, `_get_scene_safe()`, `if False` ile karakter oluşturma devre dışı (1690) | **EN YENİ #2 (stabile yakın)** |
| 22 | `SceneTracker_GILSafe.py` | "SceneTracker GIL-Safe v2.0" (başlık 4) | Frame-yürüyüş + SetPhaseWindow hook + `_winreg`, gc yok | Stabile-yakın (salt-okur) |
| 23 | `LoginEventTracker_GILSafe.py` | "LoginEventTracker GIL-Safe v1.0" (başlık 4) | Salt event-güdümlü, sınıf hook'ları, registry, `sys.modules['loginevent']` | Stabile-yakın |
| yardımcı | `script1.txt`, `helperScript.txt`, `scenechanger*.txt`, `chardeleter.txt`, `Script5/6/6x.txt`, `Script_scan*`, `ui_scan*`, `m2_explore.txt`, `m2_dump_py.txt`, `locale_probe*` | tek-seferlik araçlar | Ana-thread tek-seferlik exec | Teşhis |

**En yeni ikili = `MaximumPyScript_Merged_calisan.py` (v14) ve `MaximumPyScript_Merged.py` (v17)** (v17, v14'ün birebir üst kümesi yaması — diff ile doğrulandı). Ayrıca GILSafe ikilisi en yeni salt-okur eklemeler. `MaximumPyScript4.txt` (v7) son tam kanıtlanmış koşu (`maximum_log.txt`).

---

## 2. SON İKİ SCRIPT'İN MİMARİSİ (ayrıntı)

v14 ve v17 odak/GIL yamaları dışında bayt-bayt aynıdır (diff ile doğrulandı).

### Taşıma (transport)
- **SHM `Control_<PID>`**, 16384 bayt, Python tarafı oluşturur (`SharedMemoryManager.create()` — v14:351-395) `mmap.mmap(-1, SHM_SIZE, name)` ya da ctypes `CreateFileMappingA`+`MapViewOfFile` ile.
- Binary kayıt düzeni, magic `0x4D415831` ("MAX1"), `VERSION = 14` (v14:78-79): offsetler `OFF_MAGIC=0 … OFF_LOG_RPOS=2852` (v14:40-76). Komutlar tek u32 (`OFF_COMMAND`), parametreler `OFF_PARAM1..4`, stringler sabit offsetlerde (`OFF_USERNAME=608`, `OFF_PASSWORD=672`, …).
- SHM ring-buffer loglama **kapatıldı** — `write_log()` ve `append_log()` "GIL bloke eder" gerekçesiyle **NO-OP** (v14:284-286, 470-472).

### Enjeksiyon girişi
- DLL konsolu (`py <code>` komutu, cppcmpr `Kaynak.cpp:2858-2860`) şunu çalıştırır:
  `py exec(open('C:/MaximumPyScript_Merged.py').read())` — kullanım satırı v14:5.
- `exec`, **DLL worker thread'inde** (oyun için yabancı thread) koşar: hook'ları kurar + SHM oluşturur, sonra işi bir Python thread'ine devreder.

### Thread modeli
- `_thread.start_new_thread(_ctrl.start, ())` (v14:1876-1877, v17:1970-1971) → **kontrol döngüsü bir arka plan Python thread'inde**, oyunun ana thread'i her frame Python çalıştırmaya devam ederken.
- v17 satır 1976-1984: `threading.Thread(daemon=True)` yedeği.
- `LoginEventTracker`-tarzı hook'lar (`OnLoginFailure`, `OnHandShake`, `SetPhaseWindow`) **oyun ana thread'inde**, oyunun kendi callback'leri içinde koşar.

### Ana döngü (v14 `_loop`, 1695-1757; v17 1780-1840)
1. Sahneyi `SetPhaseWindow` hook'unun `_tracked_phase_window` globalinden oku (yalnız Python özniteliği, ~0ms).
2. Sahne/durumu SHM'ye yaz (mmap int yazımları).
3. `OFF_COMMAND` yokla; `_cmd()` dağıt (1778-1837) — komutlar **döngü thread'inde senkron** çalışır, dakikalarca bloklayabilir (do_complete_all).
4. Sahneye göre uyku: CHAR_SEL 5sn / GAME 10sn / LOGIN 2sn / değilse 2sn ("GIL tamamen serbest").
- v17 ekleri: `prev_scene` takibi + GAME→menü geçişinde `SetFocus()` (v17:1802-1814), slot döngüsünde `time.sleep(0)` GIL teslimi (v17:941-942).

### Hangi oyun modülü NEREDEN çağrılıyor (hepsi **arka plan kontrol thread'inden**)
| Çağrı | Yer (v14) | Thread |
|---|---|---|
| `net.GetAccountCharacterSlotDataInteger/String` | `cm.refresh` 936-957 | arka plan |
| `net.GetEmpireID`, `net.SendSelectEmpirePacket`, `net.SendCreateCharacterPacket` | 1330, 1288, 1394, 1422 | arka plan |
| `net.DirectEnter(sl)` | 1465 | arka plan |
| `net.IsConnect()` | 765, 800, 1480 | arka plan |
| UI: `lw.serverList.SelectItem`, `serverSelectButton.CallEvent`, `idEditLine/pwdEditLine.SetText`, `loginButton.CallEvent` | 1106-1178 | arka plan |
| UI: `sw.SelectSlot`, **`sw.StartGame()`**, `sw.slot = sl` | 1454-1460 | arka plan |
| UI: `ccw.__IncreaseSlotIndex/__SelectGender/editCharacterName.SetText/btnCreate.CallEvent` | 1352-1386 | arka plan |
| UI: `ew.OnSelectEmpire`, `EmpireButton.IsShow()/CallEvent()`, `ClickSelectButton` | 1236-1281 | arka plan |
| Faz makinesi: `stm.SetSelectCharacterPhase/SetLoginPhase/...` | 1403, 1505, 1519 | arka plan |
| Sınıf monkey-patch `MainStream.SetPhaseWindow` | 656 kurulum (arka plan), koşum (ana) | karışık |

### Ana-thread tarafındaki hook seti
- `Recorder v9` (v14:499-614): örnek-seviyesi `lw.OnLoginFailure/OnConnectFailure/OnHandShake/PopupNotifyMessage` sarmalayıcıları — saf dict/global güncellemeleri, dosya I/O yok, chat hook yok.
- `install_phase_window_hook()` (v14:619-659): `MainStreamClass.SetPhaseWindow = _hooked_set_phase` — iki global'e yazar, sonra orig'i çağırır.
- `SceneDetector v8` (702-825): hook önce, `sys._current_frames()` frame-yürüyüşü yedeği (664-697), `net.IsConnect()` son yedek — v17 her yerde `detect()`'i bypass edip `_get_scene_safe()` kullanıyor (v17:1053-1063).
- C++ konsoluna sahte modül: `sys.modules['loginevent']` (v14:1842-1869).

### GILSafe ikilisinin yaklaşımı (görev F)
**`SceneTracker_GILSafe.py` (v2.0)** — salt-okur sahne izleyici:
- Arka plan thread (`start_scene_tracker` → `thread.start_new_thread(tracker.start, ())` 630-651) — "GIL-Safe" adına rağmen hâlâ ikinci bir Python thread'i.
- MainStream'i 3 yolla bulur: `sys._current_frames()` frame-yürüyüşüyle **oyun ana thread'inin canlı yığınından** `f.f_locals['mainStream']` okuma (219-270); sınıf monkey-patch `MainStream.SetPhaseWindow` (273-320); `__main__` globali (323-337).
- Hiç `gc.get_objects()` yok; algılama = `type(pw).__name__` bakışları (388-431) + opsiyonel `sb.IsShow()` (406).
- Çıktı `_winreg.SetValueEx` ile `HKCU\Software\MG\SceneTracker` (127-159) 0.5sn/1sn/2sn aralıkla; `time.sleep` GIL bırakır (613-619).
- **Kalan ana-thread ihlalleri:** izleyici thread'den `net.IsConnect()` (459) — C++ çağrısı net thread/ana thread ile yarışıyor; frame-yürüyüş çalışan ana döngünün canlı frame'ine dokunuyor (f_locals okuması CPython'da zararsız ama GIL'e bağımlı hareketli hedef okuması); arka plan thread'den `print`.

**`LoginEventTracker_GILSafe.py` (v1.0)** — gerçekten event-güdümlü (başlık 22 "Thread YOK" — doğru, thread kurmaz):
- Sınıf-seviyesi yamalar: `LoginWindow.OnLoginFailure` (411-423), `OnConnectFailure` (444-455), `OnHandShake` (476-487), `PopupNotifyMessage` (508-523), ayrıca `MainStream.SetPhaseWindow` (366-390).
- Tüm hook'lar **oyun ana thread'inde**; her event `_log_event` → `time.strftime`, history append ve **6 `_winreg.SetValueEx` registry yazımı** (137-160) + frame-yürüyüşü ya da `net.IsConnect()` gerektirebilen `_get_current_scene_name()` (253-290) yapar.
- C++ konsolun sorgulaması için `sys.modules['loginevent']` arayüzü: `GetLastEvent/GetLastErrorCode/GetHistory/GetScene...` (528-606) (`call loginevent.GetLastEvent()`).
- **Kalan ihlaller:** ana-thread paket-işleme yolunun içinde registry I/O ve olası `net.IsConnect()` — her faz değişimi (`LoadingWindow`'a girme dahil) yükleme sırasında registry yazımı tetikler.

---

## 3. KÖK NEDENLER (numaralı, kanıt satırlı)

### GIL kökenleri

**RC1 — KRİTİK — Tasarımla arka plan Python thread'i vs oyun ana thread'i.**
Her sürüm `_thread.start_new_thread(controller.start)` ile bitiyor — v1.0 `MaximumScript.txt:1528`, v1.2 `MaximumPyScript__.txt:1424`, v7 `MaximumPyScript4.txt:1741`, **v14 `MaximumPyScript_Merged_calisan.py:1877`, v17 `MaximumPyScript_Merged.py:1971`**, recorder'lar (`recorder.txt:1032` … `recorder_v19_.txt:1427`), SceneTracker `SceneTracker_GILSafe.py:636`. Kontrol thread'i `net.*`, UI `CallEvent/SetText/IsShow` ve faz metotlarını oyunun ana thread'i Python çalıştırırken EŞZAMANLI çağırıyor. Client'ta bunu koordine eden hiçbir şey yok: scriptlerde `PyGILState` farkındalığı yok, senkron yok. Sonuç tam raporlanan belirti: komut yanlış anda çalışınca çıkan aralıklı "GIL" hataları, ve yalnız "hiçbir şey olmuyorken" stabilite (o yüzden oyun-içi pasif mod — v7:1602-1630 — işleri iyileştirdi).

**RC2 — KRİTİK — Arka plan thread'de `gc.get_objects()` tam-heap taramaları = yüzlerce-ms GIL blokları.**
- recorder v11/v12 bunu **her dinleyici tığında (20ms döngü)** yapıyor: `recorder_v11.txt:1119`, `recorder_v12.txt:1146`.
- v3 sahne-tespiti başına yapıyordu (`MaximumPyScript3.txt` başlık 7-11 "gc.get_objects() TEK SEFER… cache").
- v7 hâlâ `do_select_empire` içinde tam tarama yapıyor: `MaximumPyScript4.txt:1157` (kendi "Fix 2" iddiasına rağmen, satır 9).
- Tek-seferlik araçlar da tarıyor (`MaximumPyScript__.txt:295`, `Script5.txt:~380`, `ui_scan*`).
Geliştiricilerin kendi yorumları mekanizmayı kanıtlıyor: `recorder_v13.txt:7-9` "[CRASH FIX] gc.get_objects() taramasi KALDIRILDI", `recorder_v15.txt:10` "(render crash sebebi)", `recorder_v20.txt:10` "gc.get_objects() KALDIRILDI (render bozma sebebi!)", `SceneTracker_GILSafe.py:27` "TOPLAM GIL hold ~0.05ms (vs gc.get_objects: 200-500ms!)". Ana thread frame Python'unu çalıştırmak isterken 200-500ms'lik GIL bloğu = donma → render watchdog/sıfırlama → "render hataları".

**RC3 — KRİTİK — C++ DLL'lerin GIL'SİZ Python C-API çağırması.**
`cppcmpr/cppcmpr/v1.cpp`, `v2.cpp`, `pythonSenderv1.cpp`, `pythonfnctuple.cpp` içinde **sıfır** `PyGILState_Ensure` (grep ile doğrulandı). Worker thread'leri (`v1.cpp:571-629`, DllMain 631-651; `pythonSenderv1.cpp` DllMain 1260-1265) doğrudan `PyTuple_New/PyObject_Call/PyDict_Next…` çağırıyor (`v1.cpp` `CallModuleFunctionInt0/Int1`, `DumpModuleAttributes`). Ana thread Python çalıştırırken bunların herhangi biri koşarsa senkronsuz GIL erişimi → heap bozulması, "Fatal Python error", rastgele access violation. `Kaynak.cpp` (v6 FINAL) bunu `GILGuard` (331-349) + her komutta `ACQUIRE_GIL()` (2806, 2858…) ile çözdü; `Controller.h` patlama başına `PyGILState_Ensure` kullanıyor (230-234, 244, 281).

**RC4 — YÜKSEK — Yabancı thread'den tüm-script `PyRun_SimpleString` saniyelerce GIL tutuyor.**
`Kaynak.cpp:2858-2860` `py exec(open('C:/MaximumPyScript_Merged.py').read())` komutunu tek `ACQUIRE_GIL()` altında çalıştırıyor; bu exec SHM kurulumu + locale ters-harita inşası (eski sürümlerde 700+ girdi — `maximum_log.txt:3` "Recorder v7 kuruldu: 724 locale") + hook kurulumları + ilk gc taraması yapıyor. Bu tek hold süresince oyun ana thread'i hiçbir Python çalıştıramaz → enjeksiyon anında toplam input/render durgunluğu. Sonraki "NO-OP loglama" değişiklikleri (`Merged_calisan.py:285, 471, 518, 522`) ve v17'nin `if False` debug kapatmaları (1690) hep bunun hafifletme girişimleri.

**RC5 — YÜKSEK — `app.Pump()/app.Process()/app.Update()` ile Python thread'inden oyun döngüsüne re-entrant giriş.**
`MaximumPyScript__.txt:12` "app.Pump/Update cagriliyor (oyun donmasin)" diyor; `pump_game()` (307-316) her eylemden sonra çağrılıyor (591, 626, 639, 652…); `Script5.txt:363-372` her 0.3sn'de `app.Update()` döngüsü kuruyor. Bu, gerçek ana döngü frame'in ortasındayken oyunun kendi mesaj/update döngüsünü ana-thread-olmayan bir thread'den sürmek = GIL ve render/mesaj pompası üzerinde re-entrancy. `scenechanger_result.txt` bulgusu neden terk edildiğini kanıtlıyor: `app.Pump: YOK / app.Update: YOK / app.ProcessMessage: YOK` (satır 4-6) — bu client build'inde fonksiyonlar zaten yok, yalnız `app.IsPressed` çalışıyor (satır 4, 14).

**RC6 — ORTA — Sıkı dinleyici döngüleri ve mesaj-başına dosya I/O.**
Recorder dinleyicisi `time.sleep(0.02)` (recorder v10-v17: `recorder.txt:1015`, `recorder_v12.txt:1189`, `recorder_v19_.txt:1402`) = saniyede 50 GIL yarışı; her kaydedilen mesaj **ana-thread hook'ları içinde** `open/write/close` yapıyor (`recorder_v19_.txt:163-181`) (RC7).

### RENDER kökenleri

**RC8 — KRİTİK — Frame-başına UI fonksiyonlarının monkey-patch'i.**
`recorderbase.txt` ve recorder ≤v12 `ui.TextLine.SetText/Show` hook'luyordu — geliştiricinin kendi notuna göre "her frame'de binlerce kez" çağrılıyor (`recorder_v14.txt:13-16`: "TextLine.SetText/Show hook KALDIRILDI (crash sebebi!) 80 TextLine instansi var, her frame'de binlerce kez cagrilir ve GetParent() gibi C++ metodlari crash verebiliyordu"). v18/v19 `Window.Show`'u jenerik hook'ladı → `recorder_result_.txt` kuyruğu dakikalar içinde **1570+ `Window.Show` event'i** gösteriyor (satır ~2940-2962). Sarmalayıcı gövdeleri render frame'inin İÇİNDE, render thread'i aynı pencere nesnelerine sahipken C++ çağırıyor (`GetParent`).

**RC9 — YÜKSEK — Arka plan thread'den render döngüsüyle yarışan C++ UI metot çağrıları.**
v7 `SceneDetector.detect` kontrol thread'inden `sb.IsShow()`, `ccw.IsShow()`, `ew.IsShow()`, `sw.IsShow()` çağırıyor (`MaximumPyScript4.txt:724, 744, 761, 769`) — ana thread o pencereleri render ederken. v14 bunu açıkça kaldırdı: "_resolve_scene_from_window(): IsShow() cagrisi KALDIRILDI - C++ metodu GIL bloke ediyordu" (`Merged_calisan.py:721-723`, 1696-1705). "GIL" diye etiketlense de mekanizma aynı: senkronsuz eşzamanlı C++ UI erişimi — render bozulmalarının klasik kaynağı.

**RC10 — YÜKSEK — Zorlanmış GC geçişleri vs client'ın elinde tuttuğu ham `PyObject*`.**
`gc.get_objects()` (RC2) + dinleyicinin tahsis hızı rastgele anlarda jenerasyonel collection tetikler. Eski Metin2 client kodu C++ yapilarında ödünç/ham `PyObject*` tutar (UI pencereleri, callback'ler); frame ortasında bu nesneleri untrack/serbest bırakan bir collection → sonraki Draw'da use-after-free = takip edilen "render bozma".

**RC11 — ORTA — Enjekte koddan odak manipülasyonu.**
v16 `loginButton.CallEvent()` sonrası `KillFocus()` ekledi; v17 kaldırdı: "KillFocus() KALDIRILDI (login response'u engelliyordu)" (`MaximumPyScript_Merged.py:11, 1224-1226`), `SetText` öncesi ve GAME→menü geçişlerinde `SetFocus()` ekledi (1187-1195, 1802-1814). Enjekte UI çağrılarının pencere yöneticisini bozup client'ın event/login işlemesini durgunlaştırabildiğinin kanıtı.

### NPC-yüklenmeme kökenleri

**RC12 — KRİTİK — ÇİFT enter-game dizisi.**
Her kontrol sürümünde `do_enter_game()`:
- `sw.SelectSlot(sl)` → `sw.StartGame()` (UI yolu: select+enter paketleri), SONRA
- `time.sleep(0.1)` → `net.DirectEnter(sl)` (paket yolu: select+enter TEKRAR).

Kanıt: v3 `MaximumPyScript1.txt:1664-1673`, v7 `MaximumPyScript4.txt:1356-1363`, v14 `Merged_calisan.py:1454-1466`, v17 `Merged.py:1538-1548`, X `MaximumPyScriptX.txt:1517-1526`. Koşu logu ikisinin de aynı saniyede art arda başarılı olduğunu gösteriyor: `maximum_log.txt:24-25` "StartGame OK" / "DirectEnter(0) OK". Client böylece 0.1 sn arayla İKİ select+enter dizisi alıyor; PHASE_WINDOW_SELECT(2)→LOAD(4) geçişinde ikinci giriş geçişi söker/yeniden başlatır ve ilk geçişe ait entity-spawn server komutları sıfırlanan faza karşı işlenir → iptal edilen geçişin NPC/monster'ları hiçbir zaman gelmez. "Oyuna girildi ama NPC'ler yüklenmedi"nin en doğrudan kod-seviyesi nedeni budur.

**RC13 — KRİTİK — Arka plan thread'den faz-makinesi müdahalesi (`SetXxxPhase()` recovery).**
`do_recovery()` `stm.SetSelectCharacterPhase()` / `SetLoginPhase()` çağırıyor (v14:1510-1530; v17:1616-1636) ve sahne "doğru değilmiş" gibi göründüğünde tetikleniyor: create hatalarından sonra (1638-1641), başarısız girişten sonra (1647), `_cmd(CMD_CREATE_CHAR)` içinde (1807-1810), `do_scene_change` (1495-1508). Sahne algısı hook-tabanlı; hook bir geçişi kaçırdıysa (ya da client aslında `LoadingWindow`/`GameWindow`'dayken eski `SelectCharacterWindow` bildiriyorsa) arka plan thread'i **dünya yüklenirken** `SetSelectCharacterPhase()` çağırır → yükleme iptal → NPC yok/takılı ekran. `helper_result.txt` akışı (satır 44-50) ekibin bu recovery'ye zaten güvendiğini gösteriyor ("BUG TESPIT EDILDI! CreateCharacterWindow da takildi! SetSelectCharacterPhase ile geri donuluyor") — güçlü ama yüklenme sırasında tetiklenirse felaket.

**RC14 — YÜKSEK — Yanlış "oyundayım" tespiti.**
`do_enter_game`, `net.IsConnect() and (sys.modules.get('game') or sys.modules.get('introGame'))` olduğunda başarı ilan ediyor (v14:1477-1487; v7:1374-1384). Her iki koşul da **yükleme ekranı hâlâ dayanıkken** doğru (bağlantı select fazında kuruldu; `game`/`introGame` önceki oturumdan import edilmiş olabiliyor). Kontrol böylece `ST_IN_GAME` raporluyor, `AUTO_COMPLETE` (`maximum_log.txt:29-30` StartGame'den 7sn sonra "OYUNA GIRILDI! === TAMAMLA BASARILI ===") — faz izlemeyi bırakıyor ve sonraki her komut/tazeleme (`cm.refresh`, `net.GetAccountCharacterSlotData*`) spawn patlamasının ortasına düşüyor.

**RC15 — YÜKSEK — Yükleme kritik yolundaki recorder hook'ları.**
recorder v18/v19 `GameWindow.BINARY_ServerCommand_Run` hook'luyor (`recorder_v19_.txt:1015-1030`; yakalanan `recorder_result.txt:101`) — **her** server komutu, yani dünya yüklemesi sırasındaki her entity/item spawn'ı artık dict bakışı, birleştirme, `time.strftime` ve **senkron dosya open/write/close** yapan bir Python sarmalayıcıdan geçiyor (`append_line`, `recorder_v19_.txt:163-181`) — hepsi ana thread'de, tam NPC-spawn patlaması sırasında. Yükleme hattını yavaşlatır/boğar ve client'ın kendi entity işlemesinin exception yoluna düşme şansını artırır.

**RC16 — ORTA — Doğrudan öznitelik yazımlarıyla select penceresini desenkronize etmek.**
`SelectSlot(sl)` sonrası `sw.slot = sl` (v3:1660, v7:1353, v14:1456, v17:1538) pencerenin slot-değişikliği yan etkilerini atlatır; `StartGame()` hiç doğrulanmamış bir slot durumu için paket yollar (`ew.empireID = empire_id` v14:1239 aynı).

**RC17 — ORTA — Geçişler sırasında agresif karakter-veri yoklaması.**
v3.1/v7 seçim ekranında her 2-3sn'de `net.GetAccountCharacterSlotDataInteger/String` otomatik tazeliyor (v7:1638-1643); v14 kaldırdı ("CHAR_AUTO_REFRESH: KALDIRILDI - … auto-refresh GIL bloke eder", `Merged_calisan.py:29`), v17 oluşturma sayımını bile `if False:` ile kapattı (v17:1690) — bu okuma döngülerinin seçim ekranındaki GIL/donma belirtileriyle birlikte geldiğinin kanıtı.

---

## 4. C++ ENJEKSİYON MEKANİZMASI (iki proje)

### `cppcmpr/cppcmpr/` — işlem-içi enjekte DLL ailesi ("Python27 DLL Injector")
- Kaynakların hiçbirinde `OpenProcess/WriteProcessMemory/CreateRemoteThread/SetWindowsHookEx` **yok** — DLL'i harici bir loader yüklüyor (o loader burada değil); her varyant `metin2client.exe` içinde zaten koşuyor varsayar.
- Giriş: `DllMain` → `DLL_PROCESS_ATTACH` → `AllocConsole()` + `CreateThread(WorkerThread)` (`Kaynak.cpp:2901-2911`; aynı desen `v1.cpp:633-651`, `v2.cpp:891-908`, `pythonSenderv1.cpp:1260-1265`, `pythonfnctuple.cpp:1961`).
- Sembol çözümü: `GetModuleHandleA("python27.dll")` + ~40 CPython 2.7 exportu için `GetProcAddress` (`Kaynak.cpp:188-241`); thread'ler başlatılmamışsa `PyEval_InitThreads()` (302-313).
- Konsol komutları: `list/ls`, `call <mod>.<fn>(args)`, `get`, `info`, `all`, **`py <code>` → `ACQUIRE_GIL(); PyRun_SimpleString(code)`** (`Kaynak.cpp:2844-2865`), `sniff on/off` (`PyRun_SimpleString` ile Python monkey-patch, 1668-1784), `hook add redirect|monitor|capture` (monkey-patch motoru, 2024-2629).
- Nesil farkları:
  - `v1.cpp`, `v2.cpp` — prototipler; modül sayım + doğrudan çağrı, **GIL yönetimi hiç yok** (RC3).
  - `pythonSenderv1.cpp` — "Unified Python Caller with Cache + FncInfo", registry cache `Software\MG\ScanCache`, AES-gizli `RESULTX` master key (20-36); **GIL yönetimi yok**.
  - `pythonfnctuple.cpp` — FncInfo + Capstone x86 otomatik-arg-analizi çağırıcı (497); **GIL yönetimi yok**.
  - `Kaynak.cpp` — **v6 FINAL**, `GILGuard` RAII (331-349), sniff/hook motorları, güvenli modül erişimi.
  - `Controller.h` — "MaximumController Injector v5": Python kontrolcünün **C++ ikizi**. SHM `Control_<PID>`'yi kendi oluşturuyor (436-466), birebir 16KB offset tablosu (22-59), komutları 100ms'de **GIL'SİZ** yoklar ve kısa `PyGILState_Ensure → PyRun_SimpleString → Release` "GIL patlamaları" ile çalıştırıyor (CTRL_GIL_MAX_MS=50, 220-306), adımlar arası uyku "GIL tamamen serbest! Oyun yüklenebilir!" (1220). `CtrlDoEnterGame` **yalnız `net.DirectEnter`** yolluyor (1199-1212) — çift giriş yok; Python sürümlerinden kayda değer sapma.

### `win32apiMetin2Py/win32apiMetin2Py/Kaynak.cpp` — harici kontrol GUI'si ("MaximumController v4")
- Saf Win32 dialog uygulaması (709 satır), **enjekte değil, DLL yok, süreç belleği yazımı yok**.
- İsimle bağlanır: `OpenFileMappingA("Control_%u", pid)` + `MapViewOfFile` + magic kontrolü (`Kaynak.cpp:366-379`).
- Komut kayıtları yazar (`SendCommand`, 197-202), sahne/durum/karakter tablolarını ve SHM **ring-buffer log**unu okur (`ReadShmLogs`, 216-238), `SetTimer` 100ms ile UI yoklaması (594, 597-598). `DoCompleteAll` (383-448) tüm SHM alanlarını doldurup `CMD_COMPLETE_ALL` atar.
- Tam zincir: *loader DLL'i yükler → DLL konsolu `py exec(open('C:/MaximumPyScript_Merged.py').read())` → Python SHM `Control_<PID>` oluşturur → harici GUI (ya da DLL'in kendi Controller.h'si) SHM'ye komut yazar → Python kontrol thread'i eylemleri oyunda yapar.*

---

## 5. SONUÇ/LOG KANITLARI (alıntı)

- `maximum_log.txt` (v7 tam otomatik koşu — **başarı** + çift-giriş kanıtı):
  - L4-5: `=== MaximumPyScript v7 (Hook-Safe + GIL-Safe + Input-Safe) ===` / `PID: 1380 | SHM: Control_1380 | Scene: 2 | Locale: 724`
  - L17: `LoginWindow hook kuruldu (id=87417232)`
  - L20: `LOGIN OK -> scene=3`
  - **L24-25: `StartGame OK` / `DirectEnter(0) OK`** (çift giriş, aynı saniye)
  - L27: `OYUN MODU: Hooklar kaldirildi, GIL serbest`
  - L29-30: `OYUNA GIRILDI!` / `=== TAMAMLA BASARILI ===`
- `maximum_result.txt`: tam zaman çizelgesi `[SERVER_SELECT] → [LOGIN_ATTEMPT:admin] → [HANDSHAKE:OK] → [LOGIN_SUCCESS:OK] → [ENTER_GAME:slot=0 name=staple]`.
- `login_result.txt` (Script4/5/6 dönemi, v9 yöntem 2): **L7 `Olusturma TIMEOUT`, L14 `Olusturma TIMEOUT`** — UI-yolu karakter oluşturma iki kez zaman aşımına uğradı, yeni isimlerle yeniden denendi.
- `scenechanger_result.txt`: `app.Pump: YOK`, `app.Update: YOK`, `app.ProcessMessage: YOK`, `stream: YOK`, `use_thread: False` (L2-15); **L18-20: `SelectEmpire OK` / `SelectEmpire OK` / `TIMEOUT 30s`** — UI event'leri ateşleniyor ama sahne hiç geçmiyor → enjekte edilmiş `CallEvent` tek başına client'ı sürmüyor (odak/pump eksikliği), v16/v17 SetFocus/KillFocus serisiyle sonra ele alındı.
- `helper_result.txt`: L46 `BUG TESPIT EDILDI! CreateCharacterWindow da takildi!` → L48-50 `SetSelectCharacterPhase() -> OK … BASARILI! Phase degisti!` (faz-kurtarma mekanizması çalışıyor).
- `chardeleter_result.txt` / `chardeleter_result - Copy (2).txt`: tam silme akışı `SelectSlot → PopupDeleteQuestion → InputPrivateCode → SetText("1111111") → AcceptInputPrivateCode` → `Karakter SILINDI!`.
- `recorder_result.txt` (v19): L43 `Ana thread baslatildi`; **L101 `GameWindow HOOK: BINARY_ServerCommand_Run, OpenQuestWindow, PopupMessage`** (yükleme kritik yolunda hook); L71-72 lazy `Interface`/`SelectWindow` hook'ları; L145 `[NET_SEND:SendChatPacket] (#1) merhaba, 0`.
- `recorder_result_.txt` (v18 TOTAL CAPTURE): L13 `net: 0` (net-hook kurulumu başarısız), L41 `Ana thread`; kuyruk = **`[Window:Window.Show] (#1557)…(#1570)`** — yüzlerce frame-başına hook event'i (spam → GIL/render baskısı).
- `recorder_result - Copy.txt` (v17): L36 `gc.get_objects: SADECE baslangicta 1 kere`; L41-43 dinleyici start + KAYIT BASLADI; L101 `GameWindow HOOK: BINARY_ServerCommand_Run…`.
- `locale_probe_result.txt`: `LOCALE MODULE NOT FOUND: locale_game / locale_game_text / localeInfo_game` (kuyruk), sonra `GC dict scanned: 780`, `FOUND: gc_dict_484 | key='LOGIN_FAILURE_WRONG_PASSWORD'…` — locale stringlerine yalnız gc-dict taramasıyla ulaşılabiliyor (gc'nin neden başta kullanıldığını ve kaldırılınca hook/registry alternatiflerine geçildiğini açıklıyor).
- `Script4_check.txt`, `Script3_check.txt`, `ui_scan*.txt`: başarılı tek-seferlik UI durum dökümleri (`serverBoard show: 1`, `net.PHASE_WINDOW_GAME = 5 …` `ui_scan5.txt`).
- Hiçbir `*_result.txt` içinde Python traceback ya da kelimesi kelimesine "GIL" hatası YOK — GIL/render başarısızlıkları client tarafı donma/crash olarak tezahür ediyor, sürüm başlıkları bunları belgeliyor ("crash sebebi", "render bozma sebebi", "GIL bloke eder").

---

## 6. KANITLANMIŞ ÇALIŞANLAR (tekrar kullanılacaklar)

1. **SHM komut taşıması** — binary düzen `MAX1` uçtan uca: GUI → SHM → kontrolcü tam `CMD_COMPLETE_ALL` çalıştırdı (`maximum_log.txt`).
2. **Sunucu/CH seçimi + login otomasyonu** — `serverList.SelectItem`, `serverSelectButton.CallEvent`, `idEditLine/pwdEditLine.SetText`, `loginButton.CallEvent` + `OnLoginFailure/OnHandShake` hook geri-besleme döngüsü (`maximum_log.txt:12-20`, `maximum_result.txt`).
3. **Karakter listesi tazeleme** `net.GetAccountCharacterSlotData*` — doğru ad/level/sınıf (`maximum_log.txt:23`, `chardeleter_result.txt:3-6`).
4. **Karakter silme** — tam sosyal-kod diyalog otomasyonu (`chardeleter_result.txt`, `- Copy (2).txt`).
5. **Karakter oluşturma (UI yolu)** — sınıf/cinsiyet dolaşımı + takılan pencere kurtarma (`helper_result.txt:20-50`).
6. **Recorder yakalama** — login hata kodları (`WRONGPWD`), popup/locale stringleri ters locale key ile, `net.Send*` izleri.
7. **`MainStream.SetPhaseWindow` monkey-patch ile sahne takibi** — kanıtlı (`maximum_log.txt` "Scene: 2", `scenechanger_result.txt` "curPhaseWindow: LoginWindow") ve iki GILSafe script'in temeli.
8. **GIL-güvenli salt-okur desen** — `sys.modules['loginevent']` sorgu arayüzü + registry dışa aktarım, C++ konsolu tüketiyor.
9. **Client içgözlemi** — modül sayımı, kaynak dökümü (`m2_dump_py.txt`), UI taramaları, locale sorgulama.

---

## 7. GENEL SONUÇ VE ÇÖZÜM YOLU

Üç belirtinin (GIL, RENDER, NPC) ortak mimari-seviye nedeni: **oyunla ilgili TÜM iş, client'ın ana thread'i DIŞINDAKI thread'lerde** koşuyor (Python kontrol thread'i, recorder dinleyicisi, DLL worker) ve senkron yalnız umutla sağlanıyor.

En yeni v14/v17, *boşta*ken GIL baskısını sıfıra yakın indirmeyi başardı (hook-tabanlı sahne okuması, mmap yazımları, uzun uykular, no-op loglama) — bu yüzden "stabile yakın"lar. Ama her **eylem** (RC1/RC5/RC9), her oyuna-giriş (RC12 çift giriş) ve yükleme sırasında yanlış tetiklenen kurtarma (RC13) hâlâ yanlış thread'den oyun kodu çalıştırıyor.

C++ tarafındaki `Controller.h` doğru şekli zaten bulmuş durumda: tek worker, `PyGILState_Ensure` patlamaları, tek `DirectEnter`. Bunu Python tarafına geri taşımak yerine **xgodmod4'ün istediği mimariye geçmek**:

> **MaxExecutor: hook yok, SHM yok, ana thread'i sıkmayan yöntem.**
> C++ DLL oyun penceresini subclass eder (`SetWindowLongPtr(GWLP_WNDPROC)`); komutlar DOSYA kuyruğuna yazılır (`C:\MaxExec\queue\`), worker thread yalnız `PostMessage(WM_APP+0x7A1)` atar. WndProc **ana thread'de** çalışır; oradan `PyRun_SimpleString` çağrısı GIL ana thread'in elinde olduğu için doğal olarak güvenlidir. Python fonksiyon monkey-patch yok, paylaşılan bellek yok, arka plan Python thread'i yok.
> Detaylı tasarım: `MaxExecutor/README.md` — kod: `MaxExecutor/MaxExecutor.cpp` + `MaxExecutor/pylib.py`.

### STABİLLEŞTİRME PAKETİ (v17 üzerinden cerrahi yamalar → `MaxExecutor/MaximumPyScript_STABLE.py`)
1. **RC12:** `do_enter_game`'den UI yolu (`sw.SelectSlot`+`sw.slot`+`sw.StartGame()`) ve `time.sleep(0.1)` KALDIRILIR; yalnız `net.DirectEnter(sl)` kalır.
2. **RC14:** "oyundayım" tespiti `sys.modules.get('game')` yerine `_get_scene_safe() == SCENE_GAME` (GameWindow kanıtı) olur.
3. **RC13:** `do_recovery`'e kapı: mevcut sahne `LOADING`/`GAME` ise `SetXxxPhase()` çağrısı REDDEDİLİR.
4. **RC17:** oyun-içi hiçbir otomatik yoklama yok; IN_GAME_POLL pasif kalır.
5. Uzun vade: tüm eylemler MaxExecutor ana-thread modeline taşınır (bu paket geçici güvenlik ağıdır).
