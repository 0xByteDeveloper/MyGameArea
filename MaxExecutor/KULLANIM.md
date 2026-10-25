# MaxExecutor PAKETİ — TAM KULLANIM KILAVUZU (Türkçe)

> Paket içeriği, kurulum, komutlar, giriş akışı, sorun giderme — hepsi bu dosyada.
> Mimari gerekçe için: `reports/DEV_REAL_BINARY_TEST.md` (RC18/RC19) + `reports/DEV_GIL_ANALYSIS.md` (RC1-RC17).
> Son güncelleme: Oturum 6 (derlenen exe'ler bu pakette: `bin/`)

---

## 1. PAKET İÇİĞİNDE NE VAR?

| Dosya | Ne işe yarar | Nereden geldi |
|---|---|---|
| `bin/MaxExecutor.dll` | **Ana proje.** Oyun içine enjekte edilen 32-bit DLL. Ana thread'de (WndProc) Python çalıştırır. Hook YOK, SHM YOK, arka-plan PyRun YOK. | Bu repo — derlendi (clang-mingw i686) |
| `bin/MaxInject.exe` | DLL enjektörü. `metin2client.exe` sürecini bulur, DLL'i LoadLibrary ile yükler. | Bu repo — derlendi |
| `pylib.py` | DLL içine yüklenen Python komut kütüphanesi (maxlib): login/charlist/empire/create/enter/status | Bu repo |
| `MaximumPyScript_STABLE.py` | Eski mimarinin (SHM'li v17) RC12/RC13/RC14 yamalı hali. Alternatif yol. | Bu repo |
| `MaxExecutor.cpp` / `MaxInject.cpp` | Kaynak kodlar (değişiklik yaparsan yeniden derlersin) | Bu repo |
| `README.md` | Mimari açıklama (İngilizce başlıklı ama içerik Türkçe) | Bu repo |

**Derleme ortamı:** llvm-mingw 20250319 (clang 20.1.1), i686-w64-mingw32, `-static` (618KB DLL, bağımlılığı yalnız USER32/KERNEL32 + UCRT).

---

## 2. KURULUM (5 ADIM, ~2 DAKİKA)

1. **Klasörü hazırla** — oyunun kurulu olduğu bilgisayarda:
   ```
   C:\MaxExec\
       MaxExecutor.dll
       MaxInject.exe
       pylib.py
   ```
2. **Oyunu aç** → login ekranı görünene kadar bekle (pencere oluşsun).
3. **Enjekte et** — Komut İstemi'ni (cmd) **Yönetici olarak** aç:
   ```
   cd C:\MaxExec
   MaxInject.exe
   ```
   - Otomatik: `metin2client.exe` sürecini arar.
   - Başka isimli client: `MaxInject.exe metin2.exe`
   - PID ile: `MaxInject.exe 12345`
   - Farklı DLL yolu: `MaxInject.exe metin2client.exe D:\yer\MaxExecutor.dll`
4. **Konsol açılır** — "MaxExecutor v1.0 — ana-thread executor" başlıklı siyah pencere.
   İlk satırlarda şunları görmelisin:
   ```
   python27.dll : BULUNDU
   oyun penceresi: SUBCLASS EDILDI (hwnd=0x...)
   ```
   > `python27.dll : YOK` ise oyunun Python'u henüz başlamamıştır → konsolda bekle,
   > oyun login ekranına gelince `status` yazarak tekrar dene (DLL her 0.5 sn'de yeniden dener, 20 sn boyunca).
5. **Hazır.** §3'teki akışa geç.

> ⚠️ **Win7/Win8'de "api-ms-win-crt-*.dll eksik" hatası alırsan:** Visual C++ 2015-2022 Redistributable (x86) kur → UCRT'yi getirir. Win10/11'de gerekmez.

---

## 3. İLK GİRİŞ AKIŞI (komut sırası birebir)

MaxExecutor konsolunda sırayla:

```
status                                  (1) ana thread nabzı + sahne — "SCENE=..." dönmeli
load C:/MaxExec/pylib.py                (2) maxlib'i ANA THREAD'de yükle
login kullaniciadim sifrem              (3) auth'a bağlan + giriş
waitfor SelectCharacterWindow 30        (4) karakter seçme ekranına düşene kadar bekle
charlist                                (5) 5 slot tablosunu yazdır
enter 0                                 (6) 1. slottaki karakterle oyuna gir (slot = 0-4)
waitfor GameWindow 60                   (7) oyun ekranı + NPC spawn tamamlanması
status                                  (8) son durum
```

Sonuç dosyaları `C:\MaxExec\results\` altında yazılır: `last_status.txt`, `last_charlist.txt`, `last_login.txt`, `last_enter.txt`, `last_error.txt`.

### create ile yeni karakter (karakter yoksa)
```
charlist                                önce bak: hangi slotlar boş?
empire 1                                gerekliyse bayrak/imparatorluk seç (1=Shinsoo 2=Chunjo 3=Jinno)
create 0 MaxAdi 2 0                     slot0, isim, race=2 (Sura-E), shape=0
enter 0
```
**race tablosu (LegendySF MAIN_RACE):** 0=Savaşçı-E, 1=Ninja-K, 2=Sura-E, 3=Şaman-K, 4=Savaşçı-K, 5=Ninja-E, 6=Sura-K, 7=Şaman-E, 8=Wolfman-E.
**Hata takibi:** `results/last_error.txt` — `isim mevcut (bType=1)` / `karakter yaratılamaz (bType=0)` / 30 sn create cooldown bilgisi buraya düşer.

### serbest komut
```
raw import net; net.SendChatPacket("merhaba", 0)
raw print(net.GetMainActorVID())     → çıktı C:\MaxExec\results\last_error.txt değil; stdout oyun loguna gider.
```
> Not: `raw` ile `print` çıktısı MaxExec konsoluna DEĞİL, oyunun kendi debug çıkışına gider.
> Değer almak için maxlib desenini kullan (dosyaya yazar).

---

## 4. NEDEN BU MİMARİ GÜVENLİ? (kısa hatırlatma)

| Eski yöntem (cppcmpr / Generated v9.2.0) | MaxExecutor |
|---|---|
| Worker thread'den Python C-API → **GIL crash** (RC1/RC3) | Yalnız ana thread (WndProc) → GIL zaten bizde |
| C++ stack'inde sahte PyInt/TupleObject (RC19) | Sahte obje YOK — gerçek PyRun_SimpleString |
| SendAttackPacket'a prolog hook → MazeProtector/decrypt çakışması (RC18) | Fonksiyon hook'u YOK |
| SHM bayt dilimi komutlar | Atomik dosya kuyruğu (`.tmp` → `MoveFile`) |
| `gc.get_objects()` heap taraması (RC2) | Yok |
| Çift giriş StartGame+DirectEnter → NPC yok (RC12) | Tek giriş (`maxlib.enter` = tek DirectEnter) |

Worker thread yalnız **dosya yazar + PostMessage** atar; Python'a hiç dokunmaz. Drain her mesajda
en fazla **4 komut** işler ve render'a nefes verir (`MAX_CMDS_PER_DRAIN`).

---

## 5. ESKİ YOL — MaximumPyScript_STABLE.py (alternatif)

Bu, eski SHM mimarisinin yamalı hali (v18-STABLE). **MaxExecutor'u tercih et;** bunu yalnız
eski Controller (win32apiMetin2Py / cppcmpr) zincirini kullanacaksan çalıştır:

1. Eski DLL'in (Kaynak.cpp v6 GILGuard'lı derlemesi) yüklü ve `Control_<PID>` SHM'si açık olmalı.
2. Oyun içi Python'a gir:
   ```
   py exec(open('C:/MaximumPyScript_STABLE.py').read())
   ```
3. Yamalar otomatik uygulanır: tek giriş (NPC fix), loading-recovery kilidi, GameWindow kanıtı.
4. SHM komutları eski MaximumController v4 GUI'siyle aynı.

---

## 6. SORUN GİDERME

| Belirti | Sebep | Çözüm |
|---|---|---|
| `MaxInject.exe` "sureci bulunamadi" | Oyun kapalı ya da exe adı farklı | Oyunu aç; `MaxInject.exe <gercek-exe-adı>` |
| "OpenProcess basarisiz (5)" | Yönetici değil | cmd'yi Yönetici olarak aç |
| `python27.dll : YOK` | Oyun Python'u başlatmamış | Login ekranına kadar bekle; DLL 20 sn boyunca otomatik tekrar dener; o da yetmezse oyunu login ekranına getirip DLL'i TEKRAR enjekte et |
| `oyun penceresi: BULUNAMADI` | Pencere henüz yok | DLL 20 sn yeniden dener; hâlâ yoksa `status` yaz (komut Pencere yoksa da kuyruğa gider, pencere gelince işlenir) |
| `status` → "sonuc dosyasi yok" | pylib yüklü değil | `load C:/MaxExec/pylib.py` çalıştırmayı unutma |
| `login` sonrası hiçbir şey olmuyor | Hatalı ID/şifre veya sunucu seçilmemiş | `results/last_error.txt` + oyun penceresinde hata popup'ına bak (`OnLoginFailure` kodları: NOID/WRONGPWD/ALREADY...) |
| NPC'ler gelmiyor | Eski script alışkanlığı: çift giriş | `enter` komutunu TEK SEFER kullan; tekrar denemeden önce `waitfor GameWindow 60` ile bekle |
| Oyunda lag/kasma | Çok sık komut | Drain zaten 4 komut/mesaj sınırlı; arka arkaya `raw` spamı yapma |
| GIL hatası hâlâ geliyor | Başka bir eski DLL de enjekte (Kaynak.cpp v1/v2/pythonSenderv1) | O DLL'leri KALDIRIR — MaxExecutor tek başına yeterli |
| DLL iki kez enjekte edildi | çift konsol | İkinci konsolu kapat; oyunu yeniden başlatıp tek enjeksiyon yap |

---

## 7. YENİDEN DERLEME (kaynağı değiştirirsen)

```bash
# llvm-mingw (linux) ile:
i686-w64-mingw32-g++ -shared -static -O2 -std=c++17 \
    -o bin/MaxExecutor.dll MaxExecutor.cpp -luser32 -lkernel32 -lgdi32

i686-w64-mingw32-g++ -static -O2 -std=c++17 \
    -o bin/MaxInject.exe MaxInject.cpp -luser32 -lkernel32
```
Visual Studio kullanacaksan: x86 platform, DLL projesi, `/MT` (statik CRT), ek include yok.

---

## 8. TEST KONTROL LİSTESİ (kullanıcı tarafında)

- [ ] `MaxInject.exe` → konsol açıldı, `python27.dll : BULUNDU`
- [ ] `status` → `SCENE=LoginWindow` + `GIL=MAIN` benzeri çıktı
- [ ] `load C:/MaxExec/pylib.py` → hata yok
- [ ] `login id pwd` → `waitfor SelectCharacterWindow 30` ile ekran geçişi
- [ ] `charlist` → `results/last_charlist.txt` dolu (5 slot, race/level/isim)
- [ ] (yeni karakter) `empire` + `create` + hata takibi
- [ ] `enter 0` → `waitfor GameWindow 60` → **NPC'ler görünüyor mu?**
- [ ] `raw` ile `player.SetAttackKeyState` denemeleri (SendAttackPacket'a elle dokunma!)
