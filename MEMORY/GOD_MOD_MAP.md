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

## X3 — OYUN İNDİRME (AKTİF)

- Kaynak: `https://drive.google.com/file/d/1JaxWFkMID_7e9929_--yk20a7PqJ-aZE/view` (1.20 GB)
- İçerik: `metin2client.exe` (test için gerekli oyun)
- Durum: İndirme başlatıldı → `metin2_game.bin` (bitince adı değiştirilir, içinden metin2client.exe çıkarılır)
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

## XGODMOD4 — YENİ EXECUTOR (HOOK YOK, SHM YOK, ANA THREAD DOSTU)

Yöntem: **WndProc subclass + dosya-kuyruk + ana-thread PyRun.**
- C++ DLL oyun penceresini subclass eder (`SetWindowLongPtr(GWLP_WNDPROC)`); komutlar DOSYA kuyruğuna yazılır (`C:\MaxExec\queue\`), worker thread sadece `PostMessage(WM_APP+0x7A1)` atar.
- WndProc ANA THREAD'de çalışır → orada `PyRun_SimpleString` GIL'i zaten ana thread'in tuttuğu için %100 güvenli.
- Python fonksiyon hook'u YOK, shared memory YOK, background Python thread YOK.
- Çıktı: `MaxExecutor/MaxExecutor.cpp` + `MaxExecutor/pylib.py` + README.
- Komut seti xGODMOD2 akışını birebir uygular: login, status, charlist, empire, create, enter, raw.

---

## BEKLEYEN / SONRAKİ ADIMLAR

- [ ] Oyun indirilince `metin2client.exe` çıkarılıp kontrol (paket yapısı, python27.dll sürümü)
- [ ] MaxExecutor derleme talimatları + gerçek client'ta test yönergesi (kullanıcı tarafında)
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
