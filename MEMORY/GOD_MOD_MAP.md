# GOD MOD GÖREV HARİTASI — Proje Beyni

> **BU DOSYA KALICI HAFIZADIR.** Sandbox sıfırlansa, memory kaybolsa, önce BU DOSYA ve MEMORY/WORKLOG.md okunur.
> Repo: https://github.com/0xByteDeveloper/MyGameArea
> Son güncelleme: Oturum 3 (2026-10-25)

---

## X1 — TEMEL TAŞLAR (TAMAMLANDI)

| Ürün | İçerik | Durum |
|------|--------|-------|
| `FULL_System.json` | HyperBot-Nerwia2 tam analiz (596 fonksiyon, hook haritası) | ✅ Repo'da (commit 72acae2) |
| `FULL_System_A1.json` | C4USMultiHack-Metin2 tam analiz (34 özellik, 754 fonksiyon, SendAttackPacket zinciri) | ✅ Repo'da (commit 6392709) |
| `DEV_MVP_WEB.json` | İlk cross-research denemesi | ⚠️ Kullanıcı "basit yapmışsın" dedi → JSON formatı iptal. Artık BÜYÜK MD raporlar üretiliyor (`reports/`) |

Not: `FULL_MEGA_System` birleştirmesi ertelendi — kullanıcı yönü DEV araştırmaya kaydı.

## X2 — GITHUB HAFIZA PROTOKOLÜ (AKTİF KURAL)

- Repo: `https://github.com/0xByteDeveloper/MyGameArea`
- Token: SADECE push URL'sinde kullanılır (`https://<TOKEN>@github.com/...`), asla dosyaya yazılmaz.
- **KURAL:** Kullanıcının yazdığı her istek, verilen her yanıt, atılan her dosya, yapılan her değişiklik bu repoya push edilir. Sandbox/workspace/memory sıfırlansa bile iş buradan devam eder.
- Yapı:
  - `MEMORY/GOD_MOD_MAP.md` ← bu dosya (görev haritası)
  - `MEMORY/WORKLOG.md` ← append-only oturum günlüğü (her adım buraya)
  - `uploads/` ← kullanıcının yüklediği orijinal dosyalar (rar + MD sohbet dökümleri)
  - `reports/` ← üretilen BÜYÜK MD dev raporları
  - `MaxExecutor/` ← xgodmod4 çıktısı (yeni executor)
  - `FULL_System.json`, `FULL_System_A1.json` ← temel taşlar

## X3 — OYUN İNDİRME (✅ TAMAMLANDI — Oturum 4)

- Kaynak: `https://drive.google.com/file/d/1JaxWFkMID_7e9929_--yk20a7PqJ-aZE/view` (1.1 GB)
- **İndirme yöntemi (Oturum 4, kullanıcı doğrudan URL verdi):**
  - gdown rate-limit'e takılıyordu (199MB'da kesiliyordu)
  - Çözüm: `drive.usercontent.google.com/download?id=...&export=download` → virus-scan HTML sayfasından `confirm=t&uuid=...` parametreleri çekildi
  - `curl -C -` resume + HTTP 206 → 1,198,166,225 byte TAM indirildi (13.5 sn'de kalan 371MB)
  - RAR5 imzası (`Rar!\x1a\x07`) doğrulandı → **NightTownFullpack.rar**
- İçerik: **2908 öğe** — metin2client.exe (5.2MB) + 73 root Python script + Modules/HyperBot/OpenBot/pyDetour/m2kmod + lib (py27 stdlib + accounts) + pack (1.3GB oyun kaynakları)
- İlk bulgular → `nighttown/README.md` (repoda):
  - `yeniden_olusturulan_MemoryGenislet.exe` = metin2client.exe ile BİREBİR boyut (5,216,256) → yamalı client rebuild
  - **ErrorLog.txt: denemeoutput.exe 0xc0000005 crash, stack'te 6 python27.dll frame** → RC1 (arka-plan thread GIL) kanıtını GÜÇLENDİRİYOR
  - logs/console.txt: HookHunter anti-cheat taraması aktif
  - pyDetour/ = Python-side detour kütüphanesi
- Repoya alınanlar: `nighttown/` (exes + scripts_root + Modules + HyperBot + pyDetour + m2kmod + lib + logs, 303 dosya ~16MB). 1.1GB tam rar repoya GİREMEZ (GitHub 100MB limit).
- Yardımcı paketler (kullanıcı yükledi, `uploads/` içinde):
  - `win32apiMetin2Py.rar` → Dış GUI kontrolcüsü (MaximumController v4, SHM tüketici tarafı)
  - `cppcmpr.rar` → Enjekte DLL ailesi (Kaynak.cpp v6 FINAL GILGuard'lı, Controller.h SHM komutcusu, v1/v2/pythonSenderv1/pythonfnctuple eski GIL'siz denemeler)
  - `MaximumPyScript1.rar` → 77 dosya: tüm script sürümleri + çıktı/log kayıtları

## XGODMOD — GIL HATASI (KÖKENİ BULUNDU)

Belirti: Script oyuna girince GIL hatası, NPC'ler yüklenmiyor, sohbette bahsediliyor.
Referans sohbet: `uploads/Prestige Silver Atılma Azaltma.md`

**Kök nedenler (`reports/DEV_GIL_ANALYSIS.md` detaylı):**
1. **RC12 (NPC yüklenmeme — KRİTİK):** Her sürümde `do_enter_game()` çift giriş yapıyor: önce `sw.StartGame()` (UI yolu), 0.1 sn sonra `net.DirectEnter(sl)` (paket yolu). İkinci giriş, ilk girişin spawn/phase geçişini iptal ediyor → NPC yok.
2. **RC1 (GIL — KRİTİK):** Tüm oyun API çağrıları (`net.*`, UI `CallEvent`, `SetText`) arka plan Python thread'inden yapılıyor; oyunun ana thread'i ile senkron yok.
3. **RC2 (GIL):** `gc.get_objects()` tam-heap taramaları 200-500ms GIL bloğu (recorder v11/v12 20ms döngüde yapıyordu).
4. **RC3 (GIL):** Eski C++ tarafı (v1.cpp, v2.cpp, pythonSenderv1.cpp, pythonfnctuple.cpp) `PyGILState_Ensure` OLMADAN Python C-API çağırıyor → heap bozulması.
5. **RC13 (NPC):** Scene yanlış algılanınca background thread'den `SetSelectCharacterPhase()` recovery → LOADING fazı iptal.
6. **RC14:** "Oyuna girildi" tespiti yanlış (`game` modülü eski import'tan var olabiliyor) → spawn patlaması ortasına komut düşüyor.

## XGODMOD2 — LOGIN AKIŞI C++ KARŞILIKLARI (TAMAMLANDI)

Kaynak: LegendySF-V2 (oyunun gerçek client+server kaynağı) → `reports/DEV_LOGIN_FLOW.md`

Zincir: Handshake → Auth login (TPacketCGLogin3, key) → Game login (TPacketCGLogin2) → LoginSuccess4 (5 slot karakter tablosu) → Empire seçimi (TPacketCGEmpire 1-3, sadece 0 karakter varsa) → Create (TPacketCGCreateCharacter, hata: bType 0=genel, 1=isim alınmış) → DirectEnter → SendSelectCharacterPacket → LoadData → EnterGame → PHASE_GAME.

Tüm fonksiyonlar dosya:satır + parametre + packet struct + server handler + hata dalları ile rapora yazıldı.

## XGODMOD3 — SCRIPT ANALİZİ + STABİLİZASYON

- 77 dosya kronolojik dizildi (23 ana sürüm). En yeni 2: `MaximumPyScript_Merged_calisan.py` (v14) + `MaximumPyScript_Merged.py` (v17); son kanıtlanmış çalışan: `MaximumPyScript4.txt` (v7, `maximum_log.txt`).
- Analiz → `reports/DEV_GIL_ANALYSIS.md`
- Stabilize çıktı → `MaxExecutor/MaximumPyScript_STABLE.py` (v17 üzerinden cerrahi düzeltmeler)

## XGODMOD4 — YENİ EXECUTOR (TAMAMLANDI)

Üretildi: `MaxExecutor/MaxExecutor.cpp` + `MaxExecutor/pylib.py` + `MaxExecutor/README.md` + `MaxExecutor/MaximumPyScript_STABLE.py`

Yöntem: **WndProc subclass + dosya-kuyruk + ana-thread PyRun.**
- C++ DLL oyun penceresini subclass eder (`SetWindowLongPtr(GWLP_WNDPROC)`); komutlar DOSYA kuyruğuna yazılır (`C:\MaxExec\queue\`), worker thread sadece `PostMessage(WM_APP+0x7A1)` atar.
- WndProc ANA THREAD'de çalışır → orada `PyRun_SimpleString` GIL'i zaten ana thread'in tuttuğu için %100 güvenli.
- Python fonksiyon hook'u YOK, shared memory YOK, background Python thread YOK.
- Çıktı: `MaxExecutor/MaxExecutor.cpp` + `MaxExecutor/pylib.py` + README.
- Komut seti xGODMOD2 akışını birebir uygular: login, status, charlist, empire, create, enter, raw.

---

## BEKLEYEN / SONRAKİ ADIMLAR

- [x] Oyun indirildi + açıldı + envanter çıkarıldı → `nighttown/` (Oturum 4). metin2client.exe ✅ python27.dll ✅ (Python 2.7). ErrorLog 0xc0000005 + python27.dll stack bulundu.
- [ ] MaxExecutor derleme talimatları + gerçek client'ta test yönergesi (kullanıcı tarafında)
- [x] xgodmod3 stabilize: `MaxExecutor/MaximumPyScript_STABLE.py` (v17 + RC12/RC13/RC14 cerrahi yamalar — patch_stable.py ile, anchor doğrulamalı)
- [ ] FULL_MEGA_System birleştirmesi (kullanıcı isterse)
- [ ] Sohbet dökümü MD'lerinin (Hooking/Prestige) içinden ek talepler varsa çıkarılacak

## KRİTİK TEKNİK BİLGİLER (hafıza güvencesi)

- Metin2 client Python: **2.7**, embedded; ana thread interpreter'ı çalıştırır, GIL'i bırakmaz.
- Injection: `GetModuleHandleA("python27.dll")` + ~40 GetProcAddress + `AllocConsole` + worker thread; `py <code>` = `ACQUIRE_GIL + PyRun_SimpleString` (Kaynak.cpp v6, GILGuard RAII satır 331-349).
- SHM: `Control_<PID>` 16384 byte, magic `0x4D415831` ("MAX1"), komut u32 + 4 param + string offsetleri.
- LegendySF: 5 slot (`ENABLE_PLAYER_PER_ACCOUNT5`), MAIN_RACE 0-8 (0=erkek savaşçı, 1=kadın ninja, 2=erkek sura, 3=kadın şaman, 4=kadın savaşçı, 5=erkek ninja, 6=kadın sura, 7=erkek şaman, 8=wolfman), `RaceToJob = race % 4`.
- Hata kodları login: NOID, WRONGPWD, ALREADY, FULL, SHUTDOWN, BLOCK, BESAMEKEY... (`intrologin.py:179-198`)
- Create hata: `TPacketGCCreateFailure{9, bType}` → bType 0 = genel/karakter yaratamazsın, 1 = isim mevcut. 30 sn create cooldown (DB core).
- `app.Pump/app.Update/app.ProcessMessage` bu client'ta YOK (`scenechanger_result.txt` kanıtı).

---

## OTURUM 5 — GERÇEK BINARY TESTİ (2026-10-25) — RC18/RC19 BULUNDU

Kullanıcı: "metin2client.exe üstünde test et, gerçek zamanlı debug, gereken tüm testleri yap."
Yöntem: Linux sandbox'ta statik derin analiz (pefile + capstone x86-32 + byte-diff + string tarama + 142 script analizi).

### Yeni Kök Nedenler
- **RC18 (MazeProtector):** denemeoutput.exe'de "i4M MazeProtector V4.3-IP" — SendAttackPacket (RVA 0xD7610,
  95B gövde) şifreli, .maze section'da 661B "MZI5" blob, ilk çağrıda in-place decrypt.
  ErrorLog crash çerçeveleri (0x4D769C/0x4D7647) TAM bu fonksiyonda. Kimlik: hata string'i
  "Send Battle Attack Packet Error" (0x8033BC) + HEADER_CG_ATTACK=2 (packet.h:13).
  Sequence üreteci: 0x482840 (sayaç 0x8BF835, tablolar 0x7F6748/0x8BF838).
- **RC19 (Sahte PyTuple):** 11/main.cpp+globals.h "Generated v9.2.0" DLL — sahte PyInt/TupleObject
  (refcnt=9999, statik C dizisi) ile Python C-fonksiyon çağrısı, PyGILState_ensure=0, worker thread.
- **Crash stack çözüldü:** PyObject_Call(+0x4C) → PyEval_EvalCodeEx(+0x65A) → PyEval_EvalFrameEx(+0x21AE) = eval-loop içi.

### Düzeltilen Teori
- Thread'den basit paket çağrısı (SendChatPacket) bu client'ta ÇALIŞIYOR (spambot.py:77-83 kanıt).
  Ölümcül olan: sahte tuple (RC19), phase fonksiyonları (RC12/13), korumalı bölge (RC18), yüksek frekans spam.

### Doğrulamalar
- MaxExecutor/pylib komut seti binary isimleriyle BİREBİR teyit (rapor §6 tablo: StartGame 0x401A95,
  DirectEnter 0x401CD3, SendSelectCharacterPacket 0x401D81 ...).
- m2netm2g/playerm2g2 bu client'ta YOK → net/player/chat kullan.
- pyDetour (Python-seviyesi hook, güvenli yöntem) L5 yazım hatası var.
- HookHunter anti-cheat: WndProc subclass güvenli, global hook tehlikeli.

### Rapor
- reports/DEV_REAL_BINARY_TEST.md (10 bölüm, adres+satır kanıtlı)
- nighttown/11/ + nighttown/denemeoutput.exe_MazeMap.txt repoya eklendi
