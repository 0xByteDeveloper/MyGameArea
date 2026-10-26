# MaxExecutor PAKETİ — TAM KULLANIM KILAVUZU (Türkçe)

> Paket içeriği, kurulum, komutlar, giriş akışı, sorun giderme — hepsi bu dosyada.
> Mimari gerekçe için: `reports/DEV_REAL_BINARY_TEST.md` (RC18/RC19) + `reports/DEV_GIL_ANALYSIS.md` (RC1-RC17).
> Son güncelleme: **Oturum 8 — v1.3** (oto pylib yükleme, kendini onaran komutlar, `pyerr` komutu, load dosya kontrolü)
>
> **v1.3 ÖZET — saha testi 26.10 dersi:** kuyruk/drenaj/ana-thread zinciri ÇALIŞIYORDU (kanıt: `results\py_probe.txt` oluştu, `alive.txt` aktti) ama makinede **`C:\MaxExec\pylib.py` dosyası yoktu**. `load` sessiz IOError yedi, `maxlib` hiç kurulmadı; her `status`/`login`/`waitfor` komutu pyerr.log'a "ImportError: No module named maxlib" yazdı (100+ kez). **v1.3 pylib.py'yi otomatik yükler** — dosya yoksa baştan uyarır.

---

## 1. PAKET İÇİĞİNDE NE VAR?

| Dosya | Ne işe yarar | Nereden geldi |
|---|---|---|
| `bin/MaxExecutor.dll` | **Ana proje.** Oyun içine enjekte edilen 32-bit DLL. Ana thread'de (WndProc + SetTimer) Python çalıştırır. Hook YOK, SHM YOK, arka-plan PyRun YOK. **v1.2: SetTimer drenajı + sayaçlar + probe. v1.3: pylib.py otomatik yükleme + kendini onaran komut bootstrap'i + `pyerr` komutu.** | Bu repo — derlendi (GCC 14 mingw-w64 i686, `-static`) |
| `bin/MaxInject.exe` | DLL enjektörü. `metin2client.exe` sürecini bulur, DLL'i LoadLibrary ile yükler. | Bu repo — derlendi |
| `pylib.py` | DLL içine yüklenen Python komut kütüphanesi (maxlib): login/charlist/empire/create/enter/status | Bu repo |
| `MaximumPyScript_STABLE.py` | Eski mimarinin (SHM'li v17) RC12/RC13/RC14 yamalı hali. Alternatif yol. | Bu repo |
| `MaxExecutor.cpp` / `MaxInject.cpp` | Kaynak kodlar (değişiklik yaparsan yeniden derlersin) | Bu repo |
| `README.md` | Mimari açıklama (İngilizce başlıklı ama içerik Türkçe) | Bu repo |

**Derleme ortamı (v1.1):** Debian GCC 14.2 mingw-w64 (win32 threads), i686-w64-mingw32, `-static` (579KB DLL, bağımlılık: yalnız USER32/KERNEL32 + UCRT).

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
4. **Konsol açılır** — "MaxExecutor v1.3" başlıklı siyah pencere (oyunun ÜSTÜNDE kalır, TOPMOST).
   İlk satırlarda şunları görmelisin:
   ```
   python27.dll : BULUNDU [initialized]
   pylib.py      : OTOMATIK yuklenecek (v1.3 — load yazmana gerek yok)
   oyun penceresi: SUBCLASS EDILDI (hwnd=0x...)
   ana-thread timer: KURULDU
   ```
   > `pylib.py : YOK!!` satırı görürsen: pylib.py'yi `C:\MaxExec` içine kopyalamamışsın demektir —
   > bundle zip'ten kopyala. v1.3 olmadan da komutlar kendini onarır ama dosya ŞART.
   > `python27.dll : YOK` ise oyunun Python'u henüz başlamamıştır → konsolda bekle,
   > oyun login ekranına gelince `status` yazarak tekrar dene (DLL her 0.5 sn'de yeniden dener, 20 sn boyunca).
   > Konsol bir sebeple hiç açılmazsa: `C:\MaxExec\maxexec.log` dosyasına bak (her adım oraya yazılır)
   > ve §6'daki "headless mod" başlığına geç.
5. **Hazır.** §3'teki akışa geç.

> ⚠️ **Win7/Win8'de "api-ms-win-crt-*.dll eksik" hatası alırsan:** Visual C++ 2015-2022 Redistributable (x86) kur → UCRT'yi getirir. Win10/11'de gerekmez.

---

## 3. İLK GİRİŞ AKIŞI (komut sırası birebir)

> ⚠️ **Bu client'ta login'den ÖNCE server listesi ekranı var** (server isimleri + CH listbox + OK butonu).
> O yüzden akış `selserver` ile başlar.

MaxExecutor konsolunda sırayla:

```
status                                  (0) SCENE= ne diyor bak (LoginWindow+ServerList ise dogru ekrandasin)
                                        (1) load ARTIK YOK — v1.3 pylib.py'yi otomatik yükler
                                           (kanıt: results\last_pylib_load.txt, 2 sn içinde oluşur)
selserver 0 0                           (2) listedeki 0. sunucu + 0. CH'yi seç, OK'a bas
serverlist                              (*)  isimleri/listbox içeriğini görmek istersen
waitfor LoginWindow 15                  (3) login (id/şifre) ekranına düşünceye kadar
login kullaniciadim sifrem              (4) id+şifre doldur + giriş
waitfor SelectCharacterWindow 30        (5) karakter seçme ekranı
charlist                                (6) 5 slot tablosu
enter 0                                 (7) 1. slotla oyuna gir (TEK DirectEnter)
waitfor GameWindow 60                   (8) oyun + NPC spawn
status                                  (9) son durum
pyerr                                   (*)  Python hatası olduysa son 30 satırı konsola döker
```

Sonuç dosyaları `C:\MaxExec\results\` altında: `py_probe.txt` (zincir kanıtı), `last_status.txt`, `last_server.txt`, `last_login.txt`, `last_charlist.txt`, `last_enter.txt`, `last_error.txt`, `last_pylib_load.txt`.

### ZİNCİR KOPTU MU? (bir şey olmuyorsa 30 sn bekle, sonra bak)

| Kontrol | Ne demek |
|---|---|
| `results\py_probe.txt` VAR | Ana thread Python'u çalışıyor — zincir TAMAM. Sorun Python/pylib tarafında → `pyerr.log` |
| `results\py_probe.txt` YOK + `alive.txt`'de `exec=0` | Komutlar kuyruğa giriyor ama çalıştırılmıyor |
| `alive.txt`'de `timer>0` artıyor | Oyun mesaj pompası TimerProc'u çağırıyor — drenaj yaşıyor (v1.2 ana yol) |
| `alive.txt`'de `msg>0` artıyor | WndProc subclass da yaşıyor |
| `alive.txt` HİÇ yok / 2 sn'de bir güncellenmiyor | Drain hiç çağrılmıyor — `maxexec.log`'a bak (SetTimer satırı var mı?) |
| `alive.txt` içeriği örnek: `tick=110017796 drain=412 exec=8 timer=409 msg=3 py=1` | `drain` akıyor ama `exec` 0 ise python27 çözülememiş → `maxexec.log` |

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
| **`ImportError: No module named maxlib`** (pyerr.log'da tekrar tekrar; status → "sonuc dosyasi yok") | **`C:\MaxExec\pylib.py` makinede yok** — v1.2 saha bulgusu: `load` sessiz IOError yedi, maxlib kurulmadı, her komut import hatası yedi. Zincir kendisi sağlamdı (py_probe.txt oluştu) | bundle zip'teki `pylib.py`'yi `C:\MaxExec` içine kopyala. **v1.3 otomatik yükler + dosya yoksa konsolda "pylib.py : YOK!!" der; komutlar kendini onarır** |
| **`load` komutu "dosya YOK" diyor** | Yanlış/eksik yol | `load C:/MaxExec/pylib.py` — ya da hiç yazma; v1.3 otomatik yükler |
| **C:\ yazma izni şüphesi** | — | **KANIT: py_probe.txt + alive.txt oyun süreci tarafından yazıldı ve göründü → C:\ sağlıklı, VirtualStore sorunu YOK.** Yine de istersen: `basedir.txt` içine `D:\MaxExec` yaz → tüm dosyalar oraya taşınır (pylib.py'yi de oraya koy!) |
| Python hatasını konsolda görmek | — | **`pyerr`** komutu — pyerr.log'un son 30 satırını döker |
| **Komutlar kuyruğa yazılıyor ama hiçbir sonuç dosyası oluşmuyor** (v1.1 saha bulgusu) | v1.1 drenajı yalnız WndProc subclass + PostMessage'a dayanıyordu; subclass etkisizse zincir ölür | **v1.2+ kullan** — SetTimer yolu WndProc'tan bağımsız. Test: `results\py_probe.txt` oluşmalı (30 sn bekle) |
| `SCENE=?` dönüyor | mainStream frame-walk ile bulunamadı | `status` tekrar dene (frame yürüyüşü her çağrıda çalışır); oyunun intro ekranı değişmişse `raw` ile `import sys; print(sys.modules.keys())` incele |
| `selserver` "serverList.SelectItem YOK" | Bu ekranda değil ya da attr adı farklı | Önce `serverlist` yaz — aday attr'ları raporlar |
| **Konsol açılıyor AMA hiç yazı yazmıyor** (v1.0 hatası) | GUI process'in CRT stdout'u geçersiz handle ile başlar; `AllocConsole` sonrası CRT konsola yeniden bağlanmamıştı | **v1.2'ye güncelle** (freopen CONIN$/CONOUT$ + unbuffered fix). Her adım ayrıca `maxexec.log`'a yazılır |
| `VirtualAllocEx basarisiz: 8` (NOT_ENOUGH_MEMORY) | Oyun 32-bit adres alanı (2GB) pack dosyalarıyla dolu/parçalı | Oyunu ilk açtığın anda (login ekranı çıkınca hemen) inject et; cmd'yi Yönetici yap; olmazsa oyunu yeniden başlat |
| Konsol penceresi görünmüyor | Oyun tam ekran, konsol arkada | v1.1+ konsolu TOPMOST yapar. Alt+Tab ile "MaxExecutor" penceresini ara |
| **Konsol hiç açılmadı (headless mod)** | AllocConsole bazı koruma/ortamlarda başarısız olur | Sorun değil: `C:\MaxExec\queue\` klasörüne komutu elle `.cmd` dosyası olarak bırak — otomatik drenaj işler |
| Python kodum hata verdi, nerede göreceğim? | Python traceback'leri oyun içine gider | `load` sonrası tüm Python hataları `C:\MaxExec\pyerr.log`'da |
| `MaxInject.exe` "sureci bulunamadi" | Oyun kapalı ya da exe adı farklı | Oyunu aç; `MaxInject.exe <gercek-exe-adı>` |
| "OpenProcess basarisiz (5)" | Yönetici değil | cmd'yi Yönetici olarak aç |
| `python27.dll : YOK` | Oyun Python'u başlatmamış | Login ekranına kadar bekle; DLL 20 sn boyunca otomatik tekrar dener |
| `oyun penceresi: BULUNAMADI` | Pencere henüz yok | DLL 20 sn yeniden dener |
| `status` → "sonuc dosyasi yok" | pylib yüklü değil ya da hata yedi | `pyerr` komutuna bak; pylib.py dosyası yerinde mi? (v1.3 otomatik yükler) |
| `login` sonrası hiçbir şey olmuyor | Hatalı ID/şifre veya serverlist ekranı atlanmış | Önce `selserver` yap; sonra `last_login.txt` + `pyerr.log` + oyun popup'ı (OnLoginFailure: NOID/WRONGPWD/ALREADY...) |
| NPC'ler gelmiyor | Eski script alışkanlığı: çift giriş | `enter` TEK SEFER; `waitfor GameWindow 60` ile bekle |
| Oyunda lag/kasma | Çok sık komut | Drain 4 komut/mesaj sınırlı; `raw` spamı yapma |
| GIL hatası hâlâ geliyor | Başka eski DLL enjekte (Kaynak.cpp v1/v2/pythonSenderv1) | O DLL'leri KALDIRIR — MaxExecutor tek başına yeterli |

---

## 7. YENİDEN DERLEME (kaynağı değiştirirsen)

```bash
# Debian/Ubuntu'da: sudo apt install g++-mingw-w64-i686 (root yoksa: apt-get download + dpkg -x)
i686-w64-mingw32-g++ -shared -static -static-libgcc -static-libstdc++ -O2 \
    -o bin/MaxExecutor.dll MaxExecutor.cpp -luser32 -lkernel32 -lgdi32

i686-w64-mingw32-g++ -static -static-libgcc -O2 \
    -o bin/MaxInject.exe MaxInject.cpp -luser32 -lkernel32

# dogrulama (ikisi de pei-i386 / i386 cikmali):
i686-w64-mingw32-objdump -f bin/MaxExecutor.dll | grep architecture
```
Visual Studio kullanacaksan: x86 platform, DLL projesi, `/MT` (statik CRT), ek include yok.

---

## 8. TEST KONTROL LİSTESİ (kullanıcı tarafında)

- [ ] `MaxInject.exe` → konsol açıldı, `python27.dll : BULUNDU`
- [ ] `pylib.py : OTOMATIK yuklenecek` satırı göründü (YOK!! ise dosyayı kopyala)
- [ ] 30 sn sonra `results\last_pylib_load.txt` VAR (oto-yükleme kanıtı)
- [ ] `status` → `SCENE=LoginWindow+ServerList` benzeri çıktı
- [ ] `login id pwd` → `waitfor SelectCharacterWindow 30` ile ekran geçişi
- [ ] `charlist` → `results/last_charlist.txt` dolu (5 slot, race/level/isim)
- [ ] (yeni karakter) `empire` + `create` + hata takibi
- [ ] `enter 0` → `waitfor GameWindow 60` → **NPC'ler görünüyor mu?**
- [ ] `raw` ile `player.SetAttackKeyState` denemeleri (SendAttackPacket'a elle dokunma!)
