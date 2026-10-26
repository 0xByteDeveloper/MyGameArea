# MaxExecutor PAKETİ — TAM KULLANIM KILAVUZU (Türkçe)

> Paket içeriği, kurulum, komutlar, giriş akışı, sorun giderme — hepsi bu dosyada.
> Mimari gerekçe için: `reports/DEV_REAL_BINARY_TEST.md` (RC18/RC19) + `reports/DEV_GIL_ANALYSIS.md` (RC1-RC17).
> Son güncelleme: **Oturum 12 — v1.7 / pylib v3.2** (UI giriş yolu + temiz karakter oluşturma)
>
> **v1.7 ÖZET — saha testi 7 dersi (oturum 12):** v1.6'nın 30 komutu da temiz çalıştı (pyfail=0) ve iki gerçek oyun-düzeyi bulgu çıktı. **(1) `enter` oyuna sokmuyor:** `net.DirectEnter` YENİ oluşturulan karakterde sunucu tarafından reddediliyor (loading penceresi açılıp login ekranına geri atıyor); eski karakterlerde (raynare) çalışıyor. Oyunun kendi START butonu ise çalışıyor — kullanıcı doğrulaması + MaximumPyScript_Merged_calisan kanıtı. **v1.7 `enter`: önce SelectSlot + StartGame/startButton (UI yolu); DirectEnter sadece UI yolu bulunamazsa YEDEK.** Çift-giriş yasağı (RC12) korunur: UI yolu seçilince DirectEnter hiç çağrılmaz. **(2) mkchar'dan sahte CREATE_FAILURE:** çift paket gidiyordu — UI OLUSTUR butonu paketi kendisi yolluyor + pylib bir de direkt SendCreateCharacterPacket yolluyordu → 1. paket başarı, 2. paket `CREATE_FAILURE: 0 (0 karakter yaratılamaz)`. Karakter zaten oluşmuştu; sahte hataydı. **v1.7 mkchar: paket yolu SADECE buton bulunamazsa.**
>
> **v1.3 ÖZET — saha testi 26.10 dersi:** kuyruk/drenaj/ana-thread zinciri ÇALIŞIYORDU (kanıt: `results\py_probe.txt` oluştu, `alive.txt` aktti) ama makinede **`C:\MaxExec\pylib.py` dosyası yoktu**. `load` sessiz IOError yedi, `maxlib` hiç kurulmadı; her `status`/`login`/`waitfor` komutu pyerr.log'a "ImportError: No module named maxlib" yazdı (100+ kez). **v1.3 pylib.py'yi otomatik yükler** — dosya yoksa baştan uyarır.

> **v1.5 ÖZET — saha testi 5 dersi (oturum 10):** makinede DLL v1.4 vardı ama `pylib.py` hâlâ **v2.0** idi (eski bundle'dan). Yeni komutlar (selchar/mkchar/delchar...) sessiz `AttributeError` yedi — konsol hiçbir şey söylemedi, hatalar yalnız pyerr.log'daydı. v1.5 bunu kökten bitirir: **pylib v3.0 artık DLL'İN İÇİNE GÖMÜLÜ** — diskteki pylib eksik/eskiyse DLL otomatik yazar (eskisini pylib_eski_vX.py olarak yedekler), sürüm uyumsuzluğu varsa açılışta KOSKOCA uyarı basar, Python hatası olursa konsol artık `!! PYTHON HATASI — detay: pyerr` diye BAĞIRIR (sessiz hata devri kapandı).

> **v1.6 ÖZET — saha testi 6 dersi (oturum 11):** v1.5'in hata görünürlüğü asıl problemi ortaya çıkardı: **neredeyse her komut `PYTHON HATASI` veriyordu.** Kök neden: v1.5, komutların import-bootstrap'ına sürüm-koruması ekleyince metin ~660 karaktere büyüdü; ama eski komut üreticileri hâlâ `char buf[256]/[512]` + `_snprintf` ile kod üretiyordu → kuyruktaki .cmd dosyaları **satır ortasında kopuk Python kodu** içeriyordu (255/511 byte) → `SyntaxError: EOL while scanning string literal` → komut hiç çalışmıyordu. Kanıt zinciri: maxexec.log'ta 674 byte'lık komutlar (newchar/joblist/lasterr — std::string ile üretilenler) ÇALIŞTI; 255/511 byte'lıklar PATLADI; pyerr.log'daki kesik satırlar birebir bu kesime noktasına denk geliyor. **v1.6: tüm üreticiler std::string'e çevrildi (FIX-23) — kesilme yapısal olarak imkânsız.** Bonuslar: Python `print`'leri konsola düşüyor (FIX-28), `charlist`/`joblist`/`mkchar`/`selchar` raporları CANLI görünüyor (pylib v3.1 yankısı), oyun hataları (yanlış şifre vb.) olduğu AN konsola `[OYUN HATASI]` satırı düşüyor, eksik argümanlı komutlar `kullanim:` mesajı veriyor, `status` bayat dosya göstermiyor (FIX-27).

---

## 1. PAKET İÇİNDE NE VAR?

| Dosya | Ne işe yarar | Nereden geldi |
|---|---|---|
| `bin/MaxExecutor.dll` | **Ana proje.** Oyun içine enjekte edilen 32-bit DLL. Ana thread'de (WndProc + SetTimer) Python çalıştırır. Hook YOK, SHM YOK, arka-plan PyRun YOK. **v1.2: SetTimer drenajı + sayaçlar + probe. v1.3: pylib.py otomatik yükleme + kendini onaran komut bootstrap'i + `pyerr` komutu.** | Bu repo — derlendi (32-bit PE, `-O2 -static`; mingw-w64 i686 veya zig cc `x86-windows-gnu`) |
| `bin/MaxInject.exe` | DLL enjektörü. `metin2client.exe` sürecini bulur, DLL'i LoadLibrary ile yükler. | Bu repo — derlendi |
| `pylib.py` | DLL içine yüklenen Python komut kütüphanesi (maxlib): login/charlist/selchar/newchar/mkchar/delchar/delcode/lasterr... **v3.2: enter UI START yolu + mkchar tek paket** | Bu repo |
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
   ```
   (pylib.py artık ZORUNLU DEĞİL — v1.5 DLL'in içinde gömülü; diskte eski/eksikse otomatik yazar. Yine de yanına koymak istersen bundle'daki pylib.py'yi kopyala.)
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
4. **Konsol açılır** — "MaxExecutor v1.7" başlıklı siyah pencere (oyunun ÜSTÜNDE kalır, TOPMOST).
   İlk satırlarda şunları görmelisin:
   ```
   python27.dll : BULUNDU [initialized]
   pylib.py      : v3.2 (uyumlu) - otomatik yuklenecek, load yazmana gerek yok
   oyun penceresi: SUBCLASS EDILDI (hwnd=0x...)
   ana-thread timer: KURULDU
   ```
   > `pylib.py : GUNCELLENDI -> v3.2 (DLL icinden yazildi)` görürsen: diskteki pylib eskiymiş, v1.7 gömülü kopyayı yazdı — ekstra bir şey yapmana gerek yok.
   > `!! PYLIB ESI` uyarısı görürsen: pylib yazılamadı demektir (yazma hatası) — o zaman elle kopyala.
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
enter 0                                 (7) 1. slotla oyuna gir (UI START yolu)
waitfor GameWindow 60                   (8) oyun + NPC spawn
status                                  (9) son durum
pyerr                                   (*)  Python hatası olduysa son 30 satırı konsola döker
```

Sonuç dosyaları `C:\MaxExec\results\` altında: `py_probe.txt` (zincir kanıtı), `last_status.txt`, `last_server.txt`, `last_login.txt`, `last_charlist.txt`, `last_enter.txt`, `last_error.txt`, `last_pylib_load.txt`.

### SAHA DOĞRULAMALI SENARYOLAR (v1.7, oturum 12 testi: HEPSİ ÇALIŞTI ✓)

> Bu iki akış gerçek sunucuda uçtan uca test edildi (giriş → bayrak → oluşturma → oyuna giriş → silme).
> `waitfor` sahne adını `SCENE=` çıktısıyla eşleştirir (substring). Bu sunucuda bayrak ekranının
> sahne adı **ReselectEmpireWindow**'dur (SelectEmpireWindow.py yüklenir ama sahne adı böyle raporlanır).

**SENARYO A — BAYRAK SEÇMELİ** (hesapta 0 karakter / ilk karakter; testte tam olarak bu akış çalıştı):
```
status
selserver 0 0
waitfor LoginWindow 15
login <id> <sifre>
waitfor SelectCharacterWindow 30
charlist
newchar                        bayrak ekranı açılır (ilk karakter)
waitfor ReselectEmpireWindow 10
empirelist                     mevcut empire + bayrak tablosu
empireui 2                     1=Shinsoo 2=Chunjo 3=Jinno -> OLUSTURMA ekranı açılır
waitfor CreateCharacterWindow 10
joblist                        sinif/cinsiyet tablosu + ekran durumu
mkchar Isim 5                  sinif gez + cinsiyet + isim + OLUSTUR (tek paket)
waitfor SelectCharacterWindow 15
charlist                       yeni karakter slotta mi?
selchar 0
enter 0                        UI START yolu (StartGame) -> oyun yüklenir
waitfor GameWindow 60
status
```

**SENARYO B — BAYRAK SEÇMESİZ** (empire kayıtlı; `newchar` direkt olusturma ekranını açar):
```
status
selserver 0 0
waitfor LoginWindow 15
login <id> <sifre>
waitfor SelectCharacterWindow 30
charlist
newchar                        bayrak atlanir, direkt CreateCharacterWindow
waitfor CreateCharacterWindow 10
joblist
mkchar YeniIsim 5
waitfor SelectCharacterWindow 15
charlist
selchar 0
enter 0
waitfor GameWindow 60
status
```

**SİLME AKIŞI** (test edildi: delchar → delcode → 0 karakter → sonraki newchar bayrak ekranını açtı):
```
charlist
delchar <slot>                 silme sorusu + kod dialogu ACAR
delcode <kod>                  kodu yazar + ONAYLAR
waitfor SelectCharacterWindow 10
charlist                       slot BOS mu?
lasterr                        DELETE_SUCCESS/DELETE_FAILURE kaydi
```
> Not: `chardel` diye bir komut YOK — doğrusu `delchar` (saha testinde 3 kez karıştırıldı).

### ZİNCİR KOPTU MU? (bir şey olmuyorsa 30 sn bekle, sonra bak)

| Kontrol | Ne demek |
|---|---|
| `results\py_probe.txt` VAR | Ana thread Python'u çalışıyor — zincir TAMAM. Sorun Python/pylib tarafında → `pyerr.log` |
| `results\py_probe.txt` YOK + `alive.txt`'de `exec=0` | Komutlar kuyruğa giriyor ama çalıştırılmıyor |
| `alive.txt`'de `timer>0` artıyor | Oyun mesaj pompası TimerProc'u çağırıyor — drenaj yaşıyor (v1.2 ana yol) |
| `alive.txt`'de `msg>0` artıyor | WndProc subclass da yaşıyor |
| `alive.txt` HİÇ yok / 2 sn'de bir güncellenmiyor | Drain hiç çağrılmıyor — `maxexec.log`'a bak (SetTimer satırı var mı?) |
| `alive.txt` içeriği örnek: `tick=110017796 drain=412 exec=8 timer=409 msg=3 py=1` | `drain` akıyor ama `exec` 0 ise python27 çözülememiş → `maxexec.log` |


---

## 3b. KARAKTER İŞLEMLERİ (v1.4 — giriş yaptıktan sonra)

> pylib v3.0 **otomatik hata izleme** kurar: `LoginWindow.OnLoginFailure` +
> `SelectCharacterWindow.OnCreateFailure/OnDeleteFailure/OnDeleteSuccess` hook'ları
> (Python-seviye, kanıtlanmış desen). Yanlış şifre, isim çakışması, silme sonucu →
> `results\last_error.txt`'ye düşer. Konsolda görmek için: **`lasterr`**

### a) Slot seçme / girme
```
charlist              tabloya bak (hangi slotlar dolu/bos)
selchar 4             4. slotu SEÇ (isaretler; girmez)
enter 2               2. slotla OYUNA GİR (UI START yolu - StartGame butonu)
```

### b) Yeni karakter oluşturma (2 ekran: bayrak → sınıf/cinsiyet/isim)
```
newchar               "karakter olustur" butonuna basar
status                hangi ekran geldigine bak
  SCENE=SelectEmpireWindow   -> bayrak ekrani (ilk karakter)
  SCENE=CreateCharacterWindow -> direkt olusturma (bayrak kayitliysa)

bayrak ekrani geldiyse:
empirelist            bayrak listesi + mevcut empire (1=Shinsoo 2=Chunjo 3=Jinno)
empireui 1            bayrak sec + ILERLE butonu (paket yolu yedekli)
waitfor CreateCharacterWindow 10

olusturma ekraninda:
joblist               sinif/cinsiyet tablosu (race 0-8) + ekran durumu
mkchar YeniIsim 3     sinif gez + cinsiyet + isim + OLUSTUR'a bas
                      (v3.2: paket yolu SADECE buton bulunamazsa - cift paket
                       sahte CREATE_FAILURE: 0 uretiyordu, artik yok)
                      race=3 -> Shaman(K); race=7 -> Shaman(E); 0=Warrior(E)...
waitfor SelectCharacterWindow 15
charlist              yeni karakter slotta mi? (30 sn create cooldown olabilir)
lasterr               hata varsa (isim mevcut = CREATE_FAILURE: 1)
```

### c) Karakter silme (2 adım: soru+kod dialogu → kodu gir)
```
charlist              once bak
delchar 3             3. slotu sec + "karakteri sil" sorusu + kod dialogunu ACAR
delcode 1111111       silme kodunu yazar + ONAYLAR
lasterr               sonuc: DELETE_SUCCESS / DELETE_FAILURE
charlist              slot bosaldi mi?
```
> Bazı serverlar silme kodu istemez (`NOT_NEED_DELETE_CODE`) — delchar çıktısında belirtilir.

### d) Hata komutları özeti
| Komut | Ne gösterir | Kaynak dosya |
|---|---|---|
| `lasterr` | **OYUN hataları** (yanlış şifre=LOGIN_FAILURE: WRONGPWD, isim mevcut, silme sonucu...) | `results\last_error.txt` |
| `pyerr` | **PYTHON hataları** (traceback — kod hatası) | `pyerr.log` |
| `log` | **DLL izi** (EXEC satırları, sayaçlar) | `maxexec.log` |

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
| Çift giriş StartGame+DirectEnter → NPC yok (RC12) | Tek giriş: UI yolu seçilince DirectEnter ÇAĞRILMAZ (v3.2); DirectEnter yalnız UI bulunamazsa tek başına |

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
| **HER KOMUTA `!! PYTHON HATASI`** (v1.5 saha bulgusu 6) | v1.5 hatası: bootstrap ~660 karaktere büyüdü ama eski üreticiler `char buf[256/512]` + `_snprintf` kullanıyordu → .cmd dosyaları satır ortasında kopuk Python kodu (255/511 byte) → SyntaxError. Kanıt: maxexec.log'taki byte boyutları + pyerr.log'daki kesik satırlar | **v1.6 kullan** — tüm üreticiler std::string (FIX-23). Ayrıca pyerr.log'da `EOL while scanning string literal` görüyorsan ve maxexec.log'ta EXEC satırı 255/511 byte diyorsa → kesinlikle v1.5'tesin, v1.6 DLL'i kopyala |
| **newchar/joblist çalışıyor ama selchar/mkchar/delchar HATASI** (v1.5 saha bulgusu) | Aynı kök neden: çalışanlar std::string üreticili, patlayanlar sabit tamponluydu | v1.6 (FIX-23) — yukarıdaki satır |
| **`AttributeError: 'module' object has no attribute 'selchar'`** (ya da herhangi bir yeni komut sessiz kalıyor) | **Diskteki pylib.py eski (v2.0) — DLL yeni** (saha testi 5: DLL v1.4 + pylib v2.0). Yeni komutlar pylib v3.0 ister | **v1.5 kullan: gömülü pylib otomatik yazar** (pylib_eski_*.py yedeği alınır). v1.4'te isen: bundle'daki yeni pylib.py'yi elle kopyala. v1.5'te bu durum ASLA sessiz kalamaz: açılışta `!! PYLIB ESI` uyarısı + komut hatasında `!! PYTHON HATASI — detay: pyerr` konsol satırı + `results\last_warning.txt` / `last_pyfail.txt` |
| **`ImportError: No module named maxlib`** (pyerr.log'da tekrar tekrar; status → "sonuc dosyasi yok") | **`C:\MaxExec\pylib.py` makinede yok** — v1.2 saha bulgusu: `load` sessiz IOError yedi, maxlib kurulmadı, her komut import hatası yedi. Zincir kendisi sağlamdı (py_probe.txt oluştu) | bundle zip'teki `pylib.py`'yi `C:\MaxExec` içine kopyala. **v1.3 otomatik yükler + dosya yoksa konsolda "pylib.py : YOK!!" der; komutlar kendini onarır** |
| **`load` komutu "dosya YOK" diyor** | Yanlış/eksik yol | `load C:/MaxExec/pylib.py` — ya da hiç yazma; v1.3 otomatik yükler |
| **C:\ yazma izni şüphesi** | — | **KANIT: py_probe.txt + alive.txt oyun süreci tarafından yazıldı ve göründü → C:\ sağlıklı, VirtualStore sorunu YOK.** Yine de istersen: `basedir.txt` içine `D:\MaxExec` yaz → tüm dosyalar oraya taşınır (pylib.py'yi de oraya koy!) |
| Python hatasını konsolda görmek | — | **`pyerr`** komutu — pyerr.log'un son 30 satırını döker. **v1.5: hata anında konsol da `!! PYTHON HATASI (dosya) — detay: pyerr` diye uyarır** + `results\last_pyfail.txt` + alive.txt'de `pyfail=` sayacı |
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
# ONCELIKLI: pylib.py degistirdiysen gomulu kopyayi yeniden uret (FIX-22):
python3 scripts/embed_pylib.py        # pylib_embedded.h yenilenir
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
- [ ] `pylib.py : v3.0 (uyumlu)` ya da `GUNCELLENDI -> v3.0` satırı göründü
- [ ] 30 sn sonra `results\last_pylib_load.txt` VAR (oto-yükleme kanıtı)
- [ ] `status` → `SCENE=LoginWindow+ServerList` benzeri çıktı
- [ ] `login id pwd` → `waitfor SelectCharacterWindow 30` ile ekran geçişi
- [ ] `charlist` → `results/last_charlist.txt` dolu (5 slot, race/level/isim)
- [ ] (yeni karakter) `empire` + `create` + hata takibi
- [ ] `enter 0` → `waitfor GameWindow 60` → **NPC'ler görünüyor mu?**
- [ ] `raw` ile `player.SetAttackKeyState` denemeleri (SendAttackPacket'a elle dokunma!)
