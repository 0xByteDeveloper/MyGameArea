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
