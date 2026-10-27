# WORKLOG — Append-Only Oturum Günlüğü

> KURAL: Her oturum / her büyük adım buraya EKLENİR (asla üstüne yazılmaz). En yeni en altta.

---

## Oturum 1-2 (özet — önceki sandbox'lardan)

- HyperBot-Nerwia2 indirildi, tarandı → FULL_System.json → push (commit 72acae2)
- C4USMultiHack-Metin2 indirildi, tarandı → FULL_System_A1.json → push (commit 6392709)
- DEV_MVP_WEB.json üretildi (1.34 MB, 1350 fonksiyon) → push edildi
- Kullanıcı geri bildirimi: "basit yapmışsın, ben senden hardcode istedim" → JSON iptal, BÜYÜK MD formatına geçildi
- LegendySF-V2 klonlandı, LegendySF index kuruldu (15.312 def, 1.232 typedef, 59 server handler)

---

## Oturum 3 — GOD MOD (2026-10-25)

### Adım 3.1 — Bağ yeniden kurulumu
- Sandbox yeniden kurulmuş: LegendySF-V2 yeniden klonlandı (73.679 dosya), MyGameArea pull'landı.
- Rar'lar açıldı → /home/z/my-project/extracted/ (win32apiMetin2Py, cppcmpr, MaximumPyScript1 = 77 dosya)
- Oyun indirimi başlatıldı (Google Drive 1.20 GB → metin2_game.bin)

### Adım 3.2 — Paralel derin araştırma (2 agent)
- **Agent A (script/GIL):** 77 script kronolojik dizildi, 17 kök neden (RC1-RC17) dosya:satır kanıtlı bulundu. Kritik: RC12 çift-giriş (StartGame+DirectEnter) = NPC yüklenmeme; RC1 background-thread API çağrıları = GIL.
- **Agent B (LegendySF login):** login→select→empire→create→enter zinciri uçtan uca dosya:satır+packet struct+server handler ile çözüldü. 5 slot, MAIN_RACE 0-8, hata kodları, 30sn cooldown, versiyon kontrolü, CRC yalnız PHASE_SELECT'te kurulur (login'e etkisiz).

### Adım 3.3 — Hafıza yapısı kuruldu
- MEMORY/GOD_MOD_MAP.md + uploads/ (5 orijinal dosya) repoya eklendi, push edildi.

### Adım 3.4 — Raporlar ve kod (BU OTURUMDA ÜRETİLENLER)
- reports/DEV_LOGIN_FLOW.md (xGODMOD2 büyük rapor)
- reports/DEV_GIL_ANALYSIS.md (xgodmod3 büyük rapor)
- MaxExecutor/MaxExecutor.cpp (xgodmod4 — WndProc ana-thread executor, hook yok SHM yok)
- MaxExecutor/pylib.py (komut kütüphanesi, hook yok)
- MaxExecutor/README.md
- MaxExecutor/MaximumPyScript_STABLE.py (v17 cerrahi stabilize: çift-giriş kaldırıldı, recovery gate'lendi)

### Durum
- Oyun indirmesi devam ediyor (arka plan)
- Push'lar: her büyük adımda bir commit

### Adım 3.5 — Üretilen teslimatlar (devam)
- reports/DEV_LOGIN_FLOW.md push (commit 72ddff7): 691 satır, §0-§11 — faz sistemi, handshake, auth+game login, slot tablosu API, empire, create hata dalları, enter-game, anti-cheat, durum makinesi, e2e diyagram, fonksiyon indeksi
- reports/DEV_GIL_ANALYSIS.md push (commit 8b4c27b): 23 sürüm kronolojisi, RC1-RC17 kök nedenler (satır kanıtlı), C++ injection mekanizmaları, log kanıtları
- MaxExecutor/MaxExecutor.cpp: WndProc subclass + dosya kuyruk + ana-thread PyRun_SimpleString; worker Python'a hiç dokunmaz; drain'de max 4 komut + heartbeat
- MaxExecutor/pylib.py: maxlib modülü (login/charlist/empire/create/enter/status) — hooksuz, gc'siz, mainStream yalnız yükleme anında yakalanır
- MaxExecutor/README.md: derleme + kurulum + xGODMOD2 akış komut eşlemesi
- MaxExecutor/MaximumPyScript_STABLE.py: v17 + 3 cerrahi yama (RC12 tek-giriş, RC13 recovery kilidi, RC14 GameWindow kanıtı) — scripts/patch_stable.py anchor-doğrulamalı uyguladı, tüm kontroller OK
- Google Drive indirme: rate-limit; yavaş retry döngüsü arka planda (scripts/download_retry_slow.sh)

---

## Oturum 4 — NightTownFullpack İndirildi + Repo'ya alındı (2026-10-25)

### Adım 4.1 — Kullanıcının verdiği doğrudan URL ile indirme (x3 TAMAMLANDI)
- Kullanıcı URL verdi: `https://drive.usercontent.google.com/download?id=1JaxWFkMID_7e9929_--yk20a7PqJ-aZE&export=download`
- gdown yolunu terk ettik: virus-scan HTML'inden `confirm=t&uuid=...` form parametreleri çekildi
- `curl -C -` resume ile HTTP 206 → kalan 371MB 13.5 sn'de tamamlandı
- **NightTownFullpack.rar = 1,198,166,225 byte, RAR5 imza doğrulandı** → /home/z/my-project/game/
- İlk script'li arka plan denemesi 826MB'da sandbox tarafından öldürüldü → foreground curl ile çözüldü (ders: büyük indirmeler foreground yapılmalı)

### Adım 4.2 — Açma + envanter
- unrar x → 2908 öğe, 1.57GB → /home/z/my-project/game/NightTownFullpack/
- Kritik: metin2client.exe (5,216,256) = yeniden_olusturulan_MemoryGenislet.exe ile aynı boyut (yamalı rebuild)
- python27.dll (845,868) → client Python 2.7 gömülü (bilgi teyit edildi)
- **ErrorLog.txt: denemeoutput.exe 0xc0000005, stack'te 13 exe + 6 python27.dll frame** → RC1 GIL hipotezini güçlendiren GERÇEK crash kanıtı
- logs/console.txt: HookHunter anti-cheat aktif; pyDetour/ = Python detour kütüphanesi
- 73 root script + Modules/ + HyperBot/ + OpenBot/ + m2kmod/ + lib/ + accounts.save

### Adım 4.3 — Repo'ya alma (persistence protokolü)
- nighttown/ oluşturuldu: exes/ + scripts_root/ (73 py) + Modules/ + HyperBot/ + pyDetour/ + m2kmod/ + lib/ + logs/ + ErrorLog.txt + config/
- nighttown/README.md = tam envanter + GIL kanıt analizi + klasör boyut tablosu
- 1.1GB tam rar GitHub 100MB limiti nedeniyle repoya konulamadı (yerelde duruyor) — README'de belirtildi
- GOD_MOD_MAP.md X3 bölümü TAMAMLANDI olarak güncellendi

---

## Oturum 5 — Gerçek Client Binary Testi (2026-10-25)

### Adım 5.1 — Ortam + araç
- Disk %100 dolmuştu: pack/BGM/screenshot/dmg silindi (~1.45GB), LegendySF .git silindi (1.5GB, kaynak ağacı kaldı) → 2.4GB boşaltıldı
- pefile + capstone + uncompyle6 kuruldu (TMPDIR=/home/z/my-project/tmp)

### Adım 5.2 — FAZ 1/1b/1c binary analizi
- PE karşılaştırma: metin2client vs MemoryGenislet (aynı boyut, MD5 farklı) vs denemeoutput (+0x1000 .maze)
- ErrorLog crash stack TAM çözüldü: python27 eval → client API → CInstanceBase → Bolge_1 → helper → crash
- python27 export-nearest: PyObject_Call/EvalCodeEx/EvalFrameEx çerçeveleri
- String tarama: 18,187 string; API ground truth tablosu; m2g alias'ları YOK; PHASE_WINDOW_* bulundu

### Adım 5.3 — FAZ 2/3 script ekosistemi
- 142 script (root73+Modules25+bot44) API/thread taraması
- spambot.py:77-83 = thread'den SendChatPacket ÇALIŞIYOR → teori inceltildi
- pyDetour = Python-seviyesi detour (L5 hatası), OpenBot=eXLib, HookHunter logu

### Adım 5.4 — FAZ 4 MazeProtector + Generated DLL
- .maze section + MazeMap.txt çözümü: MZI5 blob, RVA 0xD7610 = SendAttackPacket ("Send Battle Attack Packet Error" 0x8033BC)
- byte-diff: yalnız 2 bölge (0xD7610-0xD766F) farklı = koruma bölgesi
- 11/main.cpp+globals.h okundu: RC19 sahte tuple + GIL yok + worker thread; 5 kusur tablosu

### Çıktılar
- reports/DEV_REAL_BINARY_TEST.md (büyük rapor)
- nighttown/11/ + MazeMap repoya; nighttown/README güncellendi
- scripts/realtest_faz1.py, faz1b.py, faz1c.py, faz23.py, faz4_maze.py (workspace'te)

---

## Oturum 6 — Derleme + Dağıtım (2026-10-25)

### Adım 6.1 — Derleyici kurulumu (root yok, apt kapalı)
- llvm-mingw 20250319 portable indirildi (clang 20.1.1, i686-w64-mingw32, ~90MB)
- Kullanıcı kararı: Maze önemli değil — odak metin2client.exe (maze'siz)

### Adım 6.2 — MaxExecutor derlemesi
- MaxExecutor.cpp'de EKSIK FONKSIYON BULUNDU ve duzeltildi: HookGameWindow()
  (WorkerThread cagiriyordu ama tanim yoktu — EnumWndProc + SetWindowLongPtrA subclass)
- EnqueueCommand %u/%lu format uyarilari duzeltildi
- bin/MaxExecutor.dll: 618KB, i386 DLL, -static (libc++/unwind gomulu; USER32/KERNEL32 + UCRT)
- MaxInject.cpp YAZILDI (LoadLibrary enjektoru: isim/PID hedefleme, PROCESSENTRY32W fix)
- bin/MaxInject.exe: 81KB, i386 console
- UCRT notu: Win10/11 yerlesik; Win7/8 icin VC++ 2015-2022 x86 redistributable

### Adım 6.3 — Kilavuz + paket
- MaxExecutor/KULLANIM.md: 8 bolum — kurulum (5 adim), login akisi (8 komut birebir),
  create/empire, race tablosu, hata takibi, eski SHM yolu (STABLE), sorun giderme tablosu,
  yeniden derleme, test kontrol listesi
- MaxExecutor_bundle_v1.zip (278KB): dll + exe + pylib + STABLE + kilavuz + kaynaklar

---

## Oturum 7 — Saha Testi + v1.1 Konsol Fix (2026-10-26)

### Adım 7.1 — Kullanici saha testi (gercek Windows 10 1909)
- Test 1: `MaxInject.exe` -> `VirtualAllocEx basarisiz: 8` (NOT_ENOUGH_MEMORY)
  (32-bit oyun adres alani dolu/parcali; tekrar denemede gecti — sorun giderme tablosuna eklendi)
- Test 2: enjeksiyon BASARILI (module=0x7A8C0000) AMA konsola hic yazi yazilmiyordu

### Adım 7.2 — Kök neden analizi (konsol bos)
- NEDEN: metin2client.exe GUI-subsystem process. CRT baslangicinda stdio FILE tablosu
  GetStdHandle ile GECERSIZ handle'i one baglar. AllocConsole() Windows tarafinda yeni
  konsol acar ama CRT'nin cache'ledigi stdout handle'ini GUNCELLEMEZ -> printf sessizce
  olen handle'a yazar. v1.0'da freopen(CONIN$/CONOUT$) EKSIKTII.
- Ikincil: konsol kurulumu DllMain icindeydi (loader-lock riski), cikis buffer'liydi,
  konsol oyun arkasinda kaliyordu, hatalar gorunmezdi.

### Adım 7.3 — MaxExecutor v1.1 (7 fix)
- FIX-1: freopen CONIN$/CONOUT$ (stdin/stdout/stderr) — konsol cikisinin asil fix'i
- FIX-2: setvbuf _IONBF (buffer'siz; crash olsa bile yazar)
- FIX-3: konsol kurulumu DllMain -> WorkerThread (loader-lock hijyeni)
- FIX-4: konsol HWND_TOPMOST + SetForegroundWindow (oyun arkasında kalmaz)
- FIX-5: AutoDrainThread — 2 sn'de bir PostMessage(WM_APP_MAXEXEC): konsol olmasa bile
  kuyruk islenir (headless mod: queue/*.cmd dosyasini elle birak, 2 sn'de calisir)
- FIX-6: maxexec.log tam iz (worker baslangici, AllocConsole sonucu, python27, pencere)
- FIX-7: load komutu sys.stderr -> C:\MaxExec\pyerr.log ('a',1) — Python traceback gorunur
- MaxInject: ASCII banner (CP857 bozulmasi "ÔÇ" fix), 3 ipucu satiri (Alt+Tab/maxexec.log/pyerr.log)
- DrainQueue: python27 yokken de heartbeat yazar

### Adım 7.4 — Derleme (GCC 14.2 mingw-w64, root'suz kurulum)
- sudo YOK -> apt-get download (5 deb: g++/gcc-win32, base, binutils, i686-dev, common)
  + dpkg -x /tools/mingw altina; dikkat: windows.h mingw-w64-common'daki symlink'le gelir
  (i686-dev tek basina BROKEN SYMLINK verir — common'suz "windows.h not found")
- bin/MaxExecutor.dll 579KB + bin/MaxInject.exe 235KB — objdump: pei-i386 (dogrulandi)
- strings dogrulamasi: CONIN$/CONOUT$/v1.1 stringleri DLL'de mevcut

### Adım 7.5 — Dokuman + dagitim
- KULLANIM.md: sorun giderme tablosuna 5 yeni satir (bos konsol / err8 / TOPMOST /
  headless mod / pyerr.log), derleme bolumu GCC 14'e guncellendi
- MaxExecutor_bundle_v1.zip yenilendi (337KB)
- commit b080176 -> main push OK

---

## Oturum 7b — Saha Testi 2: Kuyruk Islenmiyor + Serverlist Ekrani (2026-10-26)

### Adım 7b.1 — Kullanici saha testi 2
- v1.1 konsol fix CALISTI (banner + subclass EDILDI hwnd=001b14ec)
- AMA: kuyruk dosyalari yaziliyor (c_*.cmd seq 1-135) -> hicbir sonuc dosyasi yok,
  pyerr.log yok, pylib load görünmüyor -> ANA THREAD DRENAJI HIC CALISMAMIS
- Kullanici notu: client'ta login'den ONCE server listesi ekrani VAR
  (server isimleri listbox + CH listesi + OK butonu) — pylib v1.0 bunu bilmiyordu
- Kullanici sorusu: "C:\ korumali alan mi?" -> HAYIR: oyun süreci zaten queue'ya yazdi

### Adım 7b.2 — Kullanici yükledigi materyal analizi (uploads/)
- MaximumPyScript1.rar extract (76 dosya): MaximumPyScript_Merged_calisan.py
  (KANITLANMIS çalışan script) + SceneTracker_GILSafe + recorder_v20 + ui_scan serisi
- KRITIK BULGULAR (calisan script'ten):
  * mainStream __main__'den ERISILEMIYOR -> sys._current_frames() frame yürüyüşü
  * Sahne: type(curPhaseWindow).__name__ + LoginWindow.serverBoard -> ServerList
  * Server seçim: lw.serverList.SelectItem + lw.channelList.SelectItem +
    lw.serverSelectButton.CallEvent
  * Login: lw.idEditLine/pwdEditLine.SetText + lw.loginButton.CallEvent
  * Enter: sw.SelectSlot + sw.slot=s + TEK net.DirectEnter (RC12 uyumlu)
- Prestige Silver doc: atilma azaltma varyasyonlari (bot davranis ayari — sonra)
- Hooking doc (49k satir): SetTimer(hWnd, id, 300, NULL) polling deseni — v1.2 fikri

### Adım 7b.3 — v1.2 (drenaj mimarisi degisti)
- FIX-8 SETTIMER YOLU: SetTimer(hwnd, 0x7A1, 1500, TimerProc) — WM_TIMER oyunun kendi
  mesaj pompasiyla TimerProc'a gider; WndProc subclass'a bagimlilik SIFIR.
  Subclass koruma tarafindan geri alinirsa/emilirse bile kuyruk islenir.
- FIX-9 sayaclar: alive.txt = tick/drain/exec/timer/msg/py — zincir nerede koptu tek bakista
- FIX-10 probe: python27 bulununca otomatik probe komutu -> results/py_probe.txt
  olusursa ana-thread Python calismasi UST-UCE KANIT
- FIX-11 Py_IsInitialized logu, FIX-13 30sn'lik maxexec.log ozetleri
- FIX-12 basedir.txt: C:\MaxExec\basedir.txt -> "D:\MaxExec" yazilirsa tum yollar tasinir
- MaxInject dokunulmadi (235KB), DLL 585KB pei-i386 dogrulandi

### Adım 7b.4 — pylib v2.0 (serverlist akisi)
- _find_ms_from_frames() port (mainStream/stream/main_stream/appStream, curPhaseWindow attr)
- _scene_name(): LoginWindow+serverBoard/serverList -> 'LoginWindow+ServerList'
- serverlist(): listbox icerigi raporu (GetItemCount/GetItemText + aday attr taramasi)
- selserver(srv,ch): SelectItem x2 + serverSelectButton.CallEvent (aday buton taramasi dahil)
- login(): UI yolu ONCELIKLI (idEditLine/pwdEditLine/loginButton), paket yolu yedek
- enter(): SelectSlot/slot senkron + TEK DirectEnter
- py2 sozdizimi lib2to3 python_grammar ile DOGRULANDI

### Adım 7b.5 — Dagitim
- KULLANIM.md: akis yeniden yazildi (selserver baslangicli, 10 adim) + ZINCIR KOPTU MU
  tablosu (probe/alive.txt alanlari) + 5 yeni sorun giderme satiri
- bundle yenilendi (341KB); commit 4f38865 push OK

## Oturum 8 — v1.3: "bi bok yazilmadi" kok nedeni bulundu + oto-yukleme

### Saha testi 3 analizi (v1.2, kullanici konsol ciktisi + 3 log dosyasi)
- ZINCIR KANITLANDI: results/py_probe.txt OLUSTU ("PYOK t=03:00:46 ver=2.7.6"),
  alive.txt akti (tick/drain/exec/timer/msg hepsi artiyordu) — SetTimer drenaji,
  ana-thread PyRun ve C:\ yazma yolu CALISIYOR. C:\ korumali degil, VirtualStore yok
  (kanit: oyun surecinin yazdigi dosyalar kullaniciya gorundu).
- KOK NEDEN (pyerr.log): "IOError: [Errno 2] No such file or directory:
  'C:/MaxExec/pylib.py'" — makinede pylib.py YOKTU (v1.2'nin bundle'inda var ama
  kullanici sadece yeni DLL'i kopyalamis). load sessizce IOError yedi ->
  maxlib hic kurulmadi -> her status/login/waitfor pollu "ImportError: No module
  named maxlib" yedi (~100 traceback = v1.1'in 134 komutuyla tam örtüşüyor:
  waitfor 700ms poll x 30sn/60sn). Sonuc dosyasi hic olusmadi, waitfor'lar TIMEOUT.
- Ucuncu goz: queue klasoru bos = komutlar tuketildi (normal); hata calistirma
  degil YUKLEME katmanindaydi.

### v1.3 (FIX-14..18)
- FIX-14 AUTO-LOAD: pylib.py BASE_DIR'de varsa startup'ta kuyruga otomatik konur;
  yoksa konsolda "pylib.py : YOK!!" + last_load.txt'ye cozum yazilir.
  `load` komutu artik ZORUNLU DEGIL.
- FIX-15 KENDINI ONARAN SNIPPET: her komut try:import maxlib / except:exec(pylib.py)
  bootstrap'i ile gider — maxlib dusse bile ilk komut geri getirir.
- FIX-16 load dosya varlik kontrolu C++ tarafinda (GetFileAttributes) — sessiz
  IOError devri kapandi; hata konsolda+log'da+results'ta net soylenir.
- FIX-17 pyerr komutu: pyerr.log son 30 satiri konsola doker.
- FIX-18 probe sys.stderr'i pyerr.log'a baglar (ilk andan itibaren traceback'ler
  dosyada).
- Referans dogrulama: MaximumPyScript_Merged_calisan.py'nin do_select_server
  bloğu (serverList.SelectItem -> channelList.SelectItem -> serverSelectButton.
  CallEvent) pylib v2.0 selserver ile birebir ortusuyor — calisan yol zaten dogru,
  dosya eksikti. pylib degismedi; py2 gramer yeniden dogrulandi.

### Dagitim
- DLL 596KB / EXE 235KB (pei-i386 dogrulandi), bundle 348KB (pylib.py icinde!)
- KULLANIM.md: Oturum 8 ozeti + v1.3 kurulum satirlari + akista load kalkti +
  4 yeni sorun-giderme satiri (ImportError maxlib satiri en ustte)
- Test checklist guncellendi: last_pylib_load.txt oto-yukleme kaniti

## Oturum 9 — v1.4 + pylib v3.0: karakter islemleri + oyun hatasi izleme

### Saha durumu
- GIRIS BASARILI (MaxExecTamRapor.rar): selserver -> login -> charlist calisti.
  Hesap: 2 karakter (raynare Ninja-K slot2, 111111111111 Shaman-K slot3), 3 bos slot.
- Kullanici istekleri: yanlis sifre loglama, slot secme, olustur butonu, bayrak
  listesi+secme+ilerle, sinif/cinsiyet/isim+enter, hata mesaji komutu, karakter
  silme + silme kodu dialogu.

### Kaynak arastirma (uploads/MaximumPyScript1.rar arsivi)
- ui_scan.txt: LoginWindow tam attr (serverList=ListBox2, channelList, OK butonu)
- ui_scan_select.txt: SelectCharacterWindow 84 metot (SelectSlot, MakeCharacter,
  CreateCharacter, DeleteCharacter, PopupDeleteQuestion, InputPrivateCode,
  AcceptInputPrivateCode, OnCreateFailure, OnDeleteFailure/Success, btnCreate=None!)
- ui_scan_empire2_result.txt: ReselectEmpireWindow (empireID=3, ClickSelectButton)
- chardeleter.txt + chardeleter_result.txt: KANITLANMIS silme akisi (5 adim,
  inputValue EditLine, kod="1111111" gerceklesmis)
- maximum_log.txt: KANITLANMIS server secim akisi (11.08.2026, birebir ayni komutlar)
- MaximumPyScript_Merged_calisan.py: do_select_empire (OnSelectEmpire+EmpireButton.
  CallEvent+ClickSelectButton) + do_create_character (__IncreaseSlotIndex gezme,
  __SelectGender, editCharacterName.SetText, btnCreate.CallEvent + paket yedegi)
- LoginEventTracker_GILSafe.py: OnLoginFailure hook deseni + LOGIN_FAILURE_CODES

### pylib v3.0 (yeni)
- OTO HATA IZLEME: _install_error_hooks() — OnLoginFailure /
  OnCreateFailure / OnDeleteFailure / OnDeleteSuccess -> last_error.txt
  (idempotent _mx_hooked; status() lazy tekrar dener)
- YENI: selchar, newchar, joblist, mkchar(ad,race), empirelist, empireui(n),
  delchar(slot), delcode(kod), lasterr, serverlist
- Tablolar: EMPIRE_NAMES, RACE_TO_SLOT, RACE_TO_GENDER, LOGIN_FAILURE_CODES,
  CREATE_FAIL_CODES — hepsi kanitlanmis scriptlerden
- py2 gramer lib2to3 ile DOGRULANDI

### DLL v1.4 (yeni)
- 10 yeni komut dispatch'i: selchar/newchar/joblist/mkchar/empirelist/empireui/
  delchar/delcode/serverlist/lasterr (CmdLastErr son 25 satiri konsola doker)
- PrintHelp v1.4 tablosu (giris/olusturma/silme akislari)
- DLL 604KB pei-i386, uyarisiz derleme

---

## Oturum 10 — Saha Testi 5: "yeni komutlar calismiyor" (v1.5)

**Kullanicidan:** MaxExec_calismayanlar.rar — v1.4 konsol ciktisi: selchar/newchar/
mkchar/delchar/delcode/empirelist/empireui/joblist kuyruga yaziliyor ama hicbir
sonuc dosyasi olusmuyor; lasterr "henuz oyun hatasi yaklanmadi" diyor.

**Kok neden (RAR analizi):**
- pyerr.log kuyrugu: `AttributeError: 'module' object has no attribute 'selchar'`
  (x5), newchar/mkchar/lasterr/delchar ayni sekilde — DLL v1.4 NEW, pylib.py DISKTE
  v2.0 (eski bundle'dan; 427 satir, yeni fonksiyonlar yok)
- last_pylib_load.txt: "pylib **v2.0** yuklendi" — oto-yukleme ESKI dosyayi yuklemis
- DLL v1.4 dispatch saglamdi; Python tarafi eskiydi. Zincir sorunu YOK.
- Yanlis sifre yakalanamamasi da ayni neden: OnLoginFailure hook'unu pylib v3.0
  kurar — v2.0 yukluyken hook hic kurulmadi (last_error.txt hic olusmadi)

**v1.5 duzeltmeleri:**
- FIX-19 SURUM EL SIKISMASI: acilista C++ pylib.py'yi okur, PYLIB_VERSION isareti
  <3 ise KOSKOCA konsol uyarisi + results\last_warning.txt + log kaydi
- FIX-20 PyRun rc KONTROL: rc!=0 -> konsol "!! PYTHON HATASI - detay: pyerr" +
  last_pyfail.txt + alive.txt'ye pyfail= sayaci. Sessiz Python hatasi devri KAPANDI
- FIX-21 BootImport guard: her komut oncesi surum <3 ise pyerr.log'a aciklamali
  uyari (AttributeError yaninda "PYLIB ESKI" satiri gorunur, dedup'lu)
- FIX-22 GOMULU PYLIB: pylib v3.0 (44858 bayt) DLL icine gomuldu
  (scripts/embed_pylib.py -> pylib_embedded.h; SHA1 roundtrip dogrulandi).
  Diskteki pylib eksik/eskiyse DLL otomatik yazar (eskisi pylib_eski_vX.py
  yedegi) — artik SADECE DLL guncellemek yeterli
- probe versiyon dilimi [:12] -> [:24] (kafa karistirici kesilme giderildi)
- pylib.py: PYLIB_VERSION='3.0' isareti eklendi (maxlib kaydi globals'i kopyalar,
  isaret modulde de gorunur — DLL guard'i calisir)

**Teslimat:** DLL 657KB pei-i386 + bundle 399KB; KULLANIM.md oturum-10 guncel.

---

## Oturum 11 — Saha Testi 6: "her komutta PYTHON HATASI" (v1.6, 2026-10-26)

**Kullanici raporu (MaxExec_x.rar):** v1.5 banner aciliyor, infra yesil
(python27 BULUNDU, pylib v3.0 uyumlu, SUBCLASS OK, timer OK) — ama
selserver/login/status/selchar/mkchar/delchar/delcode HEP
"!! PYTHON HATASI" veriyor. Calisanlar: newchar, joblist, lasterr (+ OnLoginFailure
hook CALISTI: "[04:39:07] LOGIN_FAILURE: NOID (Boyle bir hesap yok)" yakalandi).

**Kok neden (RAR analizi — uc bagimsiz kanit birlesiyor):**
1. maxexec.log EXEC satirlarinda .cmd boyutlari: 255 byte (selserver/status/
   selchar/delchar) ve 511 byte (login/mkchar/delcode) = PYFAIL; 674 byte
   (newchar/joblist/lasterr) = CALISTI. Boyutlar KOMUT ICERIGINE bagLI DEGIL,
   ureticiye bagli — truncate kaniti.
2. pyerr.log kuyrugunda SyntaxError: "EOL while scanning string literal":
   satir 10 `if _mxv < 3 and not getattr(maxlib, '_MX_` (255 kesimi),
   satir 14 `...joblist/delcode/la` (511 kesimi) — bootstrap satir ortasinda
   KOPUYOR.
3. Kaynak kod: v1.5 BootImport (FIX-21 guard eklenince) ~660 karakter; ama 12
   eski komut ureticisi hala `char buf[256]/[512]` + `_snprintf ile
   BootImport().c_str()` yaziyordu → _snprintf sessizce kesti. std::string
   birlesimi kullanan 3 yeni komut (newchar/joblist/lasterr) bu yuzden calisti.

Lab dogrulamasi (scripts/verify_fix23.py): bootstrap'i 255/511'de kesince
SAHA HATASI BIREBIR yeniden uretildi (ayni satir, ayni kesme noktasi);
v1.6 uretimi 675-694 byte, lib2to3 (py2.7 gramatigi) ile hepsi GECERLI.

Ek bulgular ayni RAR'dan:
- [STATUS] satiri iki kez t=04:00:27 gosterdi → status komutu hic calismadi,
  C++ CmdStatus 400ms sonra BAYAT last_status.txt'yi basilardi (FIX-27)
- "delchar" argumansiz → "bilinmeyen komut (help)" — arguman kontrolu yuzeysel (FIX-24)
- maxexec.log "v1.4 yuklendi" + konsol basligi "v1.4" — bayat dizgi (FIX-25)
- konsol mojibake "OCo" — UTF-8 uzun cizgi, CP857 konsol (FIX-26)
- oyunda Python print'leri konsola HIC dusmuyordu (sahit: pylib yuklenme
  banner'lari hic gorunmedi) → probe sys.stdout'u CONOUT$'a bagladi (FIX-28),
  pylib v3.1 _write echo ile charlist/joblist/mkchar raporlari artik CANLI

**v1.6 duzeltmeleri:**
- FIX-23: 12 komut ureticisi (login/selserver/selchar/mkchar/empireui/delchar/
  delcode/empire/create/enter/status/waitfor) std::string birlesimine cevrildi;
  sadece kisa cagri satiri snprintf ile uretiliyor. Truncate yapisal olarak
  bitti. BootImport'a "buf[256/512]'ye snprintf YASAK" notu dustu.
- FIX-24: eksik arguman → "kullanim: ..." mesajlari (dispatcher yeniden
  yapilandi; yaniltici "bilinmeyen komut" kalkti)
- FIX-25: bayat surum dizgileri (DllMain logu, konsol basligi, banner, help)
  v1.6 yapildi
- FIX-26: konsol printf dizgileri ASCII (mojibake onlendi)
- FIX-27: CmdStatus'un bayat dosya echo'su kaldirildi (cikisi pylib canli yazar)
- FIX-28: probe sys.stdout = open('CONOUT$','w',0) + py_probe.txt'ye
  'stdout: CONOUT$' kanit satiri
- pylib v3.1: _write(name, text, echo=True) — raporlar [ETIKET] ile konsola
  yansir; _log_game_error canli [OYUN HATASI] satiri basar; status(echo)
  parametresi (waitfor → status(0), spam yok); lasterr echo'suz (DLL
  pretty-print ediyor); em-dash temizligi (53 adet); PYLIB_VERSION='3.1'
- SyncEmbeddedPylib minor-farkinda: disk 3.0 < gomulu 3.1 → artik senkron
  tetiklenir (eskiden 3>=3 geciyordu)

**Teslimat:** DLL 661KB + EXE 235KB (GCC 14 mingw-w64 i686 -static, pei-i386,
uyarisiz; bayat v1.4/v1.5 string izi 0); bundle MaxExecutor_bundle_v1.6.zip
(391KB, pylib v3.1 dogrulamali); KULLANIM.md oturum-11 guncel (v1.6 OZET +
2 yeni sorun giderme satiri).

---

## Oturum 12 — v1.7 / pylib v3.2: UI giris yolu + temiz karakter olusturma

**Kullanici saha raporu (saha testi 7):** "calisanlar var calismayanlar var" ->
buyuk sonuc arsivi (MaxExec_buyuk_sonuc.rar) analizi: v1.6 TEMIZ — 30 EXEC,
pyfail=0, alive.txt saglikli (tick=151M, drain=1079). Python seviyesinde hicbir
hata YOK; kalan iki sorun OYUN seviyesindeydi:

1) **enter oyuna sokmuyor:** net.DirectEnter YENI olusan karakterde (YeniIsm,
   slot 0) 2 kez reddedildi (loading aciliyor -> login ekranina geri atiyor,
   CONN=0); eski karakterde (raynare, slot 2) CALISTI (tam oyun yuklemesi,
   2 kez). Kullanicinin oyun-ici START butonu ile girisi calisiyordu
   (EXEC kaydi olmayan 2. tam yukleme = manuel UI giris). Referans kanit:
   MaximumPyScript_Merged_calisan.py do_enter_game: SelectSlot + sw.slot +
   **sw.StartGame()** ONCELIKLI, DirectEnter yedek.

2) **mkchar sonrasi sahte CREATE_FAILURE: 0 ("0 karakter yaratilamaz"):**
   karakter olusmustu (charlist dogruladi). Kok neden: CIFT PAKET — UI
   OLUSTUR butonu paketi KENDISI yolluyor + pylib ek 1 sn sonra direkt
   SendCreateCharacterPacket yolluyordu. 1. paket basari, 2. paket reddi
   (isim/slot dolu) -> sahte hata. Matematik: cift paket + 1 basari +
   1 CREATE_FAILURE + UI butonunun paket yolladiginin kesin kaniti.

**Cozum (v1.7 / pylib v3.2):**
- FIX-29 pylib v3.2 enter(): UI START yolu ONCELIKLI — SelectSlot(slot) +
  sw.slot + [a] sw.StartGame() metodu, [b] startButton/btnStart/btn_start/
  StartButton attr taramasi, [c] ElementDictionary yedegi; hepsi yoksa
  [d] DirectEnter YEDEK (eski davranis). UI yolu secilince DirectEnter
  HIC CAGRILMAZ (RC12 cift-giris yasagi korunur).
- FIX-30 pylib v3.2 mkchar(): paket yolu SADECE OLUSTUR butonu bulunamazsa;
  buton basildiysa paket atlanir ("paket yolu atlandi" raporu).
- FIX-31 v1.7 surum dizgileri (konsol basligi, banner, help, DllMain logu,
  BootImport guard metni, last_warning metni); enter help'i: "UI START yolu
  (DirectEnter yedek)".
- pylib_embedded.h v3.2 olarak yeniden uretildi (scripts/embed_pylib.py;
  lib2to3 sozdizim dogrulamali).
- syserr.txt (kullanici ekledi): sadece efekt dosyasi log'lari (.mse yok) —
  zararsiz, oyunun kendi kaydi; aksiyon gerektirmez.

**Araclar:** workspace resetlendi -> repo GitHub'dan klonlandi (c955174);
mingw yerine **zig 0.11.0** indirildi (tools/zig, root-less);
`zig c++ -target x86-windows-gnu -shared -O2 -Wall` → PE32 i386 DLL, kendi
kaynak kodunda 0 uyarı.

**Teslimat:** bin/MaxExecutor.dll 553KB + bin/MaxInject.exe 222KB (PE32 i386);
bundle MaxExecutor_bundle_v1.7.zip (434KB, pylib v3.2 dogrulamali); KULLANIM.md
oturum-12 guncel (v1.7 OZET + enter/mkchar aciklamalari + mimari tablo).

### Oturum 12 devam — saha dogrulama: v1.7 HEPSI CALISTI (kullanici raporu)

Kullanici testi (yeni oturum logu) — tum komutlar dogrulandi:
- enter 0 (UI START yolu) -> StartGame() cagrildi, DirectEnter CAGRILMADI,
  YENI karakter (Isim, race 5) tam oyun yuklemesi ile girdi (2 kez). v1.7'nin
  ana fix'i saha dogrulandi.
- mkchar Isim 5 -> "OK: paket yolu atlandi (buton kendisi yollar...)" raporu
  gorundu, SAHTE CREATE_FAILURE YOK. FIX-30 dogrulandi.
- delchar 0 + delcode 111111/1111111 -> silme tamalandi (0 karakter ->
  sonraki newchar BAYRAK ekranini acti).
- newchar -> NEW EMPIRE WINDOW; empirelist -> SCENE=ReselectEmpireWindow
  (bu sunucunun bayrak ekran sahnesi); empireui 2 -> OnSelectEmpire(2) +
  ClickSelectButton + yedek paket -> CreateCharacterWindow acildi.
- Bilinen tek sikinti: kullanici 3 kez "chardel" yazdi (dogrusu delchar) -
  dokumante edildi.

KULLANIM.md'ye "SAHA DOGRULAMALI SENARYOLAR" bolumu eklendi:
Senaryo A (bayrak secmeli, waitfor'lu), Senaryo B (bayrak secsiz, waitfor'lu),
Silme akisi. waitfor'in substring eslestirmesi ve ReselectEmpireWindow
sahne adi notu dokumante edildi. Kod degisikligi YOK, rebuild YOK.

---

## Oturum 13 — v1.8 "PLUSMAXGOD" (2026-10-26): oyun-ici komutlar + py kesif + PLUSQuest katalogu

### Giris
- Kullanici raporu: oturum 12'deki v1.7 akisinin HEPSI calisti (enter UI yolu 2 kez yeni
  karakterle girdi, mkchar sahte CREATE_FAILURE yok, delchar/delcode temiz).
- Istekler: (1) kullanilan komutlarin listesi (oturum 12 sonunda verilip KULLANIM.md'ye
  Senaryo A/B/Silme olarak islendi - commit 8dca033), (2) giris sonrasi oyun-ici komutlar
  (envanter/chat/hareket-pozisyon), (3) oyuna ait BUTUN python dosyalarini cekip inceleme,
  (4) tum fonksiyonlarin PLUSQuest adli dosyada katalogu + kombinasyonlari,
  (5) pylib dosyasinin adi PLUSMAXGOD_PyScript.py olsun (MaximumPyScript_STABLE degil),
  (6) nighttown workspace'te / temp-tmp'te (kesif taramasi icin not).

### Kanit havuzu (yenisi - GOD MOD taramasi)
- nighttown koleksiyonu (kullanici yukledi, repo icinde): Modules/ m2kmod/ pyDetour/
  scripts_root/ - 4000+ API kullanimi sayildi (grep -c | sort).
- Kritik bulgular: chr.SetPixelPosition 211 (tp), player.SetSingleDIKKeyState 368 (key),
  net.SendItemUsePacket 218 (use), player.SetAttackKeyState 100 (attack),
  chr.MoveToDestPosition 36 (goto), background.GetCurrentMapName 34 (pos),
  chr.GetNameByVID 52 + chr.GetInstanceType 57 (near), app.OpenTextFile 24 (pydump),
  **app.GetFileList 0 kullanim** (eski AI'nin "en iyi yontem" iddiasini curttu),
  **chr.GetInstanceList 0** (near = VID sweep yapildi).
- cycu.py zaten cycu-kanitlari veriyordu (GetStatus/GetMainActorVID/Revive/ClickSkillSlot...).

### pylib v4.0 = PLUSMAXGOD_PyScript.py (2280 satir, 94KB, py2 sozdizimi dogrulandi)
- v3.2'nin TAMAMI korundu (kanitli menu komutlari hic degismeden).
- A) OYUN-ICI (hepsi _ingame() guard'li - cycu GetPixelPosition!='None' deseni):
  stat pos inv(page) equip skill near chat whisper ride revive logout back zoom use pickup
  drop goto tp key attack.
- B) KESIF: pyfiles (5 yontem raporu) pydump(ad) pydumpall (dump\ + INDEX.txt, cap 800)
  pyscan(modul) plusquest (PLUSQuest_live.txt; pyscanall takma ad).
- Tum raporlar results\last_<ad>.txt + konsol canli yanki (v3.1 deseni).

### MaxExecutor v1.8 (DLL 614KB + EXE 222KB, PE32 i386, kendi kaynakta 0 uyari)
- FIX-32 BootImport surum-ongoer: eski maxlib (v3.x) yuklu ise PLUSMAXGOD_PyScript.py ile
  YERINDE exec (kullanici hicbir sey yapmaz); o yoksa eski pylib.py yedek yolu; guard majer 4.
- FIX-33 25 yeni Cmd ureticisi + dispatch + help (oyun-ici + KESIF bolumleri); PyStr() guvenli
  python literal ureticisi (chat/whisper tirnak/kacis guvenli), JoinArgs().
- FIX-34 dump klasoru (BASE_DIR\dump - basedir.txt ile tasinabilir).
- FIX-35 SyncEmbeddedPylib yeni adla yazar, PLUSMAXGOD_eski_v<surum>.py yedekler.
- Ders: "zig c++ ... | head" pipeline'i zig'i SIGPIPE ile olduruyor, rc=head'in rc'si oluyor ->
  DLL eski kaldi (v3.2 gomulu). 2. derlemede stderr dosyaya yakalandi -> dogru DLL 614KB.

### Dokuman + katalog
- PLUSQuest.md (repo kokunde, 364 satir): 0. hizli erisim tablosu (komut -> fonksiyon -> kanit),
  1. kesif yontemleri + eski AI hukumleri, 2. modul katalogu (app/net/player/chr/item/
  nonplayer/background/skill/chat/ui + K/S/? kanit isaretleri), 3. 10 kombinasyon tarifi
  (T1 giris zinciri, T2 envanter, T3 av dongusu, T4 HP koruma, T5 ghost/relogin,
  T6 pozisyon takip, T7 skill rotasyonu, T8 kesif dongusu, T9 esya yoneticisi,
  T10 registry->dosya koprusu), 4. risk tablosu.
- KULLANIM.md: v1.8 ozeti + paket tablosu + kurulum metinleri + yeni "3c OYUN-ICI" ve
  "3d KESIF" bolumleri + derleme (zig yolu) + test listesi.
- README.md: PLUSMAXGOD_PyScript.py tablo/girisleri + dump\ klasoru.

### Cikis
- Commit: MaxExecutor v1.8 + pylib v4.0 (PLUSMAXGOD_PyScript.py) + PLUSQuest.md + dokumanlar.
- Beklenen saha dogrulama: stat/pos/inv/equip/skill raporlari, goto/tp hareket,
  chat/use paketleri, pyfiles->pydumpall->plusquest kesif zinciri (dump klasoru -> AI'ya).

## OTURUM 14 (2026-10-27) — SAHA TESTI 8: v4.0 pydumpall analizi -> v1.8.1 + pylib v4.1 (pack.Get zinciri)

### Saha raporu (kullanici: MaxExec_plus_sonuc.rar)
- OYUN-ICI KOMUTLAR TEMIZ: stat (Lv100 Ninja-E Jinno, HP/SP 100%), pos (vid 26977,
  x38421/y39017 z18093, metin2_map_c1), skill (9 slot, Rumence isimler), near (0 buldu -
  bos alan, kod calisti), tp (SetPixelPosition 2-arg OK), goto (MoveToDestPosition OK),
  attack 1/0, chat /ride, revive. lasterr: NOID + WRONGPWD + CREATE_FAILURE:0 (gercek
  oyun hatalari, dogru yakalandi). alive.txt: pyfail=0, exec=29.
- KULLANICI YANLIS YAZANLAR: "player.ClickSkillSlot(15)" tek basina komut degil (bilinmeyen
  komut) -> "raw player.ClickSkillSlot(15)" olmali. "client koordinat /100" ayni sekilde.
  serverlist oyundayken HATA: LoginWindow sahnesinde degil (davranis dogru).
- KESIF BULGUSU (kullanicinin gozlemi DOGRU): diskteki bot dosyalari tam dumplandi
  (pasha37-levelbot.py 178KB) AMA oyunun KENDI 59 modulu (app/chr/player/game/ui/
  introLogin...) 2 BAYT bos cikti. Oyun bunlari kullanmiyor - kullanici sonradan atmada
  (root/epx'te yok).

### Kok neden (INDEX.txt + pyfiles raporu kanitlari)
- app.GetFileList("*.py") BU ISTEMCIDE CALISIYOR ama SADECE DISK listeliyor: 73 dosya =
  73 kullanici botu. Eski AI'nin "en iyi yontem" iddiasi yine yalandi (disk icin faydali,
  pack icin yararsiz).
- app.OpenTextFile pack dosyalarinda handle verip 0 SATIR donduruyor (59x "OK 0 satir").
  cycu.py GetTextFileTuple(mode=0) zaten bos liste dondurur (kendi bug'i).
- Oyunun kendi 130 modulu root PACK icinde (sys.modules kaniti).

### GOD MOD kanit taramasi (dump'lanan CALISAN botlarin kendi kodunda)
- pack.Exist + pack.Get: FileExtractor.py (ScriptStealer!) ExtractScript + New_Levelbot.py:363
  pack.Get("playersettingmodule.py") = ROOT PACK'TEN KAYNAK STRING OKUYOR.
- pack_open(ad,"r").readlines(): edithack.py:888/911/939 + itemcreator.py:418/441/469
  (pack icindeki locale/de/item_list.txt - diskte DEGIL).
- Root pack = duz .py kaynak (compiled pyc degil - New_Levelbot'un find() karsilastirmasi
  kaynak metinde calisiyor).

### pylib v4.1 (PLUSMAXGOD_PyScript.py, 108KB)
- _pack_read(ad): 4-katmanli zincir pack.Get -> pack_open(r/rb) -> app.OpenTextFile -> disk.
- _name_variants(ad): buyuk-kucuk harf + root//locale/ro/ui//UIScript//uiscript/ yollari.
- _UI_SCRIPT_PATHS: oyun log'unda gorulen 39 UI script yolu (saha kanitli).
- _STDLIB_SKIP: C-stdlib modullerine Exist denemesi ziyan etmez; KAYNAKSIZ(C) etiketi.
- pydump v2: zincir + varyant taramasi + yontem raporu.
- pydumpall v2: hedefler CANLI sys.modules'ten + probe + disk/GetFileList + UI yollari;
  INDEX.txt'de yontem + byte kolonu; 0 byte = BOS isaretli (sahte OK yok); UI hit'leri
  ayri bolumde ui__*.py olarak dokulur.
- pyfiles v2: [6] pack API kesfi (dir(pack) + hasattr Exist/Get/GetList/Open/pack_open/
  IsExist) + [7] modul __file__ raporu + GetFileList=disk-only saha notu.
- plusquest/pyscan dokunulmadi (439KB PLUSQuest_live mukemmel calisti).

### MaxExecutor v1.8.1
- Sadece surum dizgileri (banner "v1.8.1" + "v4.1 ister"); BootImport guard majer 4 ->
  yerinde yukseltme calisir. DLL 628KB + EXE 222KB (zig x86-windows-gnu, kaynakta 0 uyari).
- pylib_embedded.h v4.1 (567KB) scripts/embed_pylib.py ile uretildi.

### Dokuman
- PLUSQuest.md: baslik v4.1/oturum-14; kesif yontemleri tablosu SAHA TESTI 8 hukumleriyle
  yeniden yazildi (GetFileList=[K-disk], OpenTextFile=[K-disk/X-pack YEDEK], pack.Get=[K]
  GERCEK YOL, pack_open=[K], pkgutil=[X]); hizli erisim tablosu pydump satirlari zincire
  guncellendi; bolum 5'e calisanlar listesi + komut yazim notu eklendi.
- KULLANIM.md: v4.1 ozeti (bastaki blok) + 3d kesif bolumu v4.1 akisi + SAHA TESTI 8 HUKMU
  notu; paket tablosu + banner metinleri + test listesi v4.1'e cekildi.
- README.md: v1.8.1/pylib v4.1.


---

## Oturum 16 — v1.9 / pylib v4.3 "BALIK-FIX + OTP" (2026-10-27)

### Giris
- Kullanici saha raporu (MaxExec_sonuc_x.rar): fishspot uzaktan tutma MANTIGI dogrulandi (isinla+space = tutuyor) AMA dongu 32 atis / 0 isirtma / 14 kacan. Istekler: 400-birim su degistirebilme, fishtp tek-atis, oltayla mob/player tutma, clone sac, clonemod, spawn 20016 gorunmez, morph 20016 gorunmez, itemscan tam kayit + otomatik bulma, fishswap calismiyor gibi, OptimizeTP (tp sonrasi yuruyus geri atmasi).

### Kaynak kanit zamani (LegendySF-V2 sparse klon: DrLegendy/LegendySF-V2, Legendy.Source)
- **Isirtma gorunmezligi KOK NEDENI:** GameSource fishing.cpp event: bite 10-40sn (number(10,40)), REACT paketi; Take penceresi step==1 (6sn, PASSES_PER_SEC(6)); kacista rod->SetSocket(2,0) (YEM SIFIRLANIR). Client (ClientSource PythonNetworkStreamPhaseGame.cpp GC_FISHING): REACT dalinda python callback YOK (sadece C++ SetFishEmoticon+ReactFishing); OnFishingNotify SADECE FISH paketi ile ve PredictFish TRUE ise. PredictFish (fishing.cpp:374) = AFFECT_FISH_MIND_PILL || PREMIUM_FISH_MIND || UNIQUE_GROUP_FISH_MIND. Hapi vnumu: fishing.h FISH_MIND_PILL_VNUM=27610 (char_item.cpp:3053 20dk affect). -> v4.2 dongusunun 0 isirtma + alterne yemsiz atis deseni TAM aciklandi.
- **Sunucu su kontrolu YOK** (char.cpp CHARACTER::fishing -> sadece ATTR_BLOCK + rod + socket2). Client 400 birim = compiled c_fFishingDistance (GetFishingRot 10'ar derece su taramasi) -> PYTHON DEGISKENI YOK (binary patch gerekir, gereksiz: fishspot bypass).
- **Geri atma mekanizmasi:** input_main.cpp CG_MOVE: FUNC_MOVE -> Goto (yurur); ENABLE_TP_SPEED_CHECK aktifken mesafe>25m (binmede 60m) -> ch->Show(eski konum) = kullanicinin raporu birebir. FUNC_ATTACK/SKILL -> Move (aninda). Cozum: otp = 240px adim + MoveToDestPosition + 1300ms.
- **Mob-fishing IMKANSIZ:** fishing.cpp'de GetVictim/GetTarget YOK; fish secimi DetermineFish(map-prob). Baska sunucularin custom ozelligi - kaynakla kanitli red.
- **spawnscan probu:** client PythonNonPlayerModule.cpp:70 nonplayer.GetMonsterName(vnum) -> mob_proto aramasi (instance yaratmadan gecerli race taramasi).

### Kod (v1.9 DLL + pylib v4.3)
- scripts/make_v43.py: 20 anchor'li patcher (saha-deployed v4.2 uzerine) -> PLUSMAXGOD_PyScript.py v4.3 (4758 satir, lib2to3 py2 parse OK).
- Fish: hapi otomatik-kullanim (boot), fail/WRONGPLACE -> aninda pre, baitwait (soket2>0), baloncuk 2-vid (-1 + GetMainActorVID), timeout 50s, oneshot (fishtp), fishswap vnum filtre + fishswapnow.
- Yeni: fishtp, otp/optimizetp/otpstop/otpstep/otpdelay (_OtpWnd), clonemod swap/takip (_CloneFollowWnd), spawnscan (spawnscan_full.txt), itemscan tam-dosya (itemscan_full.txt) + itemscanall; clone sac probe; spawn/morph mob_proto on-kontrol.
- DLL v1.9: 9 Cmd uretici + dispatch + help; zig derleme PE32 i386 749KB (kaynak 0 uyari); pylib_embedded.h v4.3 (1.01MB) embed_pylib.py ile.

### Teslimat + durum
- download: MaxExecutor_bundle_v1.9.zip (DLL+EXE+py v4.3+KULLANIM+README+PLUSQuest), PLUSMAXGOD_PyScript_v4.3.py
- KULLANIM.md: v4.3 ozet bolumu (kok-neden + komut tablosu); README v1.9/v4.3.
- Beklenen saha dogrulama: /i 27610 sonrasi fish -> [LIVE] ISIRTMA + balik adi; fishtp tek dongu; otp yuruyus serbestligi; spawnscan listesi; fishswapnow.

---

## Oturum 17 — DEEP SCAN: dump.rar Python katmanı + adım animasyonu mekanizması (2026-10-28)

### Giris
- Kullanici gorevi: LegendySF-V2 indir + dump.rar Python fonksiyonlarini cikar + C++ vs Python karsilastirma + "tek ayak havada adim animasyonu" arastirmasi (kod + web + GitHub).

### Kaynak kurulumu
- MyGameArea pull; LegendySF-V2 full klon (4.8 GB, 73.679 dosya, main dal); dump.rar unrar (156 dosya, 3.3 MB; INDEX.txt = PLUSMAXGOD pydumpall v4.1 ciktisi).

### Kok-neden bulgusu (dosya:satir kanitli)
- **Tek ayak havada yurume = FUNC_WAIT teleport-step deseni:**
  - Darealfreakbot.py:688-697: SetPixelPosition + Debug() = DIK_UP 1-kare basma; elitepvpers Auto Hunt 2025 ayni desen.
  - Transform() (InstanceBase.cpp:1994-2015): hareket vektoru >1 -> OnMoving (FUNC_MOVE @300ms); yoksa OnWaiting (FUNC_WAIT @100ms + >1px). Isinlama vektor ~0 -> hep FUNC_WAIT.
  - Sunucu (input_main.cpp:1530-1700): FUNC_MOVE -> Goto (yol sim.); FUNC_WAIT -> Move(x,y)+Stop() = ANINDA kabul; dwDuration=0; ENABLE_TP_SPEED_CHECK yorumda (1557) = mesafe kontrolu yok.
  - Izleyici (InstanceBase.cpp:1434-1490): FUNC_WAIT + >1px -> StartWalking -> aninda varis -> EndWalking; her 100 ms kare-0 restart -> yuruyus dongusu (0.5-1.0s) asla tamamlanmaz = TEK AYAK HAVADA.
  - Animasyon motoru: SetLoopMotion -> __ClearMotion kare-0 (ActorInstanceMotion.cpp:307,627-637); SetMoveSpeed restart (ActorInstance.cpp:190).
- SendCharacterStatePacket (PhaseGame.cpp:1152) Python'a ACIK DEGIL (net method tablosunda yok); istemci handler'lari otomatik gonderiyor -> teorinin dogru/yanlis parciralari netlesti.
- C++/Python matrisi: Kategori A (saf Python: MoveToDestPosition, SetPixelPosition, SetAttackKeyState, item/chat/shop...), B (ozel DLL: ham CG_ATTACK - m2BotLib), C (imkansiz: sniff, inject, bellek).
- Sunucu tespit seti: 6 onlem (TP_SPEED_CHECK ac, FUNC_WAIT mesafe butcesi, frekans sayaci, tutarlilik istatistigi, dwTime geri-ileri, Goto-celiski denetimi).

### Teslimatlar
- reports/DEV_DUMP_WALK_ANALYSIS.md (bu raporun MD versiyonu)
- reports/LegendySF-Dump_Derin_Analiz_Raporu.pdf (19 sayfa; TOC + 2 grafik + 1 diyagram + 11 tablo + 3 kod kaniti)
- reports/assets/: diagram_flow.png, chart_dump_kategoriler.png, chart_cpp_bindings.png, cover_kaynak.html
- analysis/dump_inventory.json (154 dosyanin fonksiyon/API envanteri)

## Oturum 19 (2026-10-28) — v2.4 / pylib v4.8: saha testi 14 DEV RAPORU

**Rapor:** autopot 1 kere basip susuyor (karakter oldu) | otp2 bas-cek gibi | slots sayim yanlis (2x45=90 dogru, kod 168 diyordu, her sekmede 5 eksik) | selljunk/sellall satmiyor | surekli NPC aciyor + kapatamiyor | dropall atmiyor.

**KANIT TARAMASI (dump.rar gercek client kaynaklari + nighttown kendi botlari):**
- m2k Inventorymanager.py (NightTown'da calismis): `shop.IsOpen()` + **1-arg `net.SendShopSellPacket(slot)`** + **1-arg `net.SendItemDropPacket(slot)`** (xrange(0,90))
- Taubuyer.py: ayni 1-arg satis yolu (NightTown kaniti)
- uiShop.py OnSellItem: `net.SendShopSellPacketNew(slotPos, count)` (client UI'un kendisi; YENI paket)
- game.py:326+ MoveUp: `player.SetSingleDIKKeyState(app.DIK_UP, True)` — W->MoveUp->DIK_UP zinciri
- darealfreakbot/pasha37-levelbot GetDegree: `chr.SetRotation(deg(acos(dy/d))+180; px>=mx ise 360-rada)` = **S=0, B=90, K=180, D=270** (rot = deg(atan2(dx,dy))+180 mod 360)
- teleport4.py: SetPixelPosition + DIK_UP press/release = sunucu hareket senkron hilesi (otp1'in yolu)

**KOK NEDENLER:** (1) autopot TEK buyuk except — ilk exception'da dongu SESSIZ oluyor; (2) sell/drop ONCE 2-arg 'New' paket deniyordu — bu sunucu isletmiyor (1-arg kanitli), exception da olmadigi icin 1-arg'a hic dusmuyordu; (3) IsOpen flicker + waitnpc reset = NPCye surekli tiklama firtinasi; (4) slots INVENTORY_SLOT_COUNT(168) tercih ediyordu.

**v4.8 DUZELTMELER:** autopot blok-blok try/except + ilk 3 hata [LIVE] + 30sn kalp atisi + 0.4sn dongu + olum/pot-yok mesajlari. otp2: sicrama YOK, SetRotation hedefe (100ms tik), W+UP her tik BASILI, varince/otpstop bırakır, uzaklik-artiyor tani uyarisi. slots: TOPLAM=pc*ps + 9 kolonlu harita (#=esya .=bos E=efsunlu ?=hata) + hata sayaci + GetGold yedegi + 90-usti alan taramasi. selljunk/sellall: faz makinesi (bekle/sat/dogrula), NPCye 1 tik + 8sn sessiz bekleme (acilir acilmaz satis; elle tiklama da kabul), 1-arg ONCE, `selljunk 0`/`sellall 0` DUR. dropall: 1-arg ONCE, `dropall 0` DUR, 0-atilan teshisi.

**cpp v2.4:** CmdDropAll(sub) arg gecisi (dropall 0 kuyruga gecer) + help + surum dizgileri. **Dogrulama:** lib2to3 parse + module-exec simulasyonu (305 global) + dispatch capraz-kontrol (103 fonksiyon) + ikili denetim (eski spam formati YOK). DLL 876KB + EXE 222KB (zig, kaynakta 0 uyari). Commit **d5dc646**.

**Sahada beklenecek:** autopot surekli basis + kalp atisi; otp2 donerek yurume (kamera-bagli hareket cikarsa SetRotation etkisiz — uzaklik-artiyor uyarisi tani); selljunk dukkan-acilinca otomatik satis + yontem=eski-1arg logu; dropall 1-arg atma; 3 stop komutu; slots haritasi eslesmesi.
