# WORKLOG — Oturum 24 (2 Kasım 2026): TIP1/TIP2 MATRİS + detect + pylib_embedded.h KALDIRILDI
**MaxExecutor v2.9 + pylib v5.4 — "bi komut ver bize algılasın bilgi versin — matris olasılıklarının hepsini versin"**

> Kullanıcı mesajları: *"bi komut ver bize algılasın bilgi versin, tip1 sw'de önce server seçme ekranı var ve ok butonu var, tip2 server'de önce server seçme ekranı + k.adı + şifre girebileceğin alan var veya k.adı + şifre + id girebileceğin alan var. bilgisi versin. yani matris olasılıklarının hepsini versin ona yönelik komut ta ekle sisteme"* · *"kodladığın python script ve pylib_embedded.h içinde de mi yoksa PLUSMAXGOD_PyScript.py da mı? pylib_embedded.h'yi kaldır gereksiz yere klasöre eski py pushlanmasın."*

---

## 1. CEVAP — PYTHON SCRIPT HANGİ DOSYADA?

| Dosya | Ne işe yarar | v2.9 durumu |
|---|---|---|
| `PLUSMAXGOD_PyScript.py` | **GERÇEK KAYNAK** — kodlanan Python burada (`maxlib` kütüphanesi, 8266 satır) | v5.4'e yükseltildi (TIP matris) |
| `pylib_embedded.h` | Otomatik üretilmiş C byte-dizisi kopyası — DLL içine gömülü yedekti (FIX-22): diskteki .py eksik/eskiyse DLL açılışta bu kopyayı diske yazardı | **KALDIRILDI** (kullanıcı isteği) |

KALDIRMA GEREKÇESİ + SONUÇ: header ~1.7 MB'dı ve her pylib güncellemesinde yeniden üretilmesi gerekiyordu; bayat kopya klasöre/repoya girme riski taşıyordu. Artık **tek kaynak = diskteki `PLUSMAXGOD_PyScript.py`**, DLL SADECE oradan yükler. `C:\MaxExec\PLUSMAXGOD_PyScript.py` dosyası ZORUNLU hale geldi (bundle'dan kopyala). cpp'den çıkarılanlar: `#include "pylib_embedded.h"` + `EMBEDDED_PYLIB_*` referansları + `SyncEmbeddedPylib()` fonksiyonu + açılış çağrısı. `ReadPylibVersion` sürüm el-sıkışması (FIX-19) için korundu. Repodan ayrıca eski `pylib.py` (v3.2 yedek kopya) da silindi.

## 2. TIP MATRİS TANIMI (kullanıcının sözlü tanımı → kod)

```
TIP1  : server seçme ekranı AYRI + OK butonu VAR (k.adı/şifre ekranı ayrı gelir)
TIP1n : server seçme ekranı AYRI, OK YOK (otomatik geçiş / CH butonları)
TIP2a : server seçme + k.adı + şifre AYNI ekranda (2 alan)
TIP2b : server seçme + k.adı + şifre + id AYNI ekranda (3 alan)
TIP2x : birleşik MUHTEMEL (IsShow ölçülemedi — teyit için board görünürken tekrar)
M1    : resmi 2014 — login ÖNCE ayrı ekranda, serverboard SONRA (gizli katman)
M2    : Marty gömülü — server listesi yok, CH butonları, OK yok
M3    : özel/eski — sadece login alanları, listbox yok
M4    : çoklu-hesap container (id_editline_s + autoLogin(index))
+M5   : PIN/guard 3. alan bayrağı (her matrisle birleşebilir)
BÖLGE : çoklu bölge (regionList>1, Romania vb.) bayrağı
'?'   : bilinmiyor → uiprobe
```

**AYIRT ETME TEKNİĞİ (v5.4'ün yeniliği): GÖRÜNÜRLÜK.** Resmi 2014 intrologin'de serverboard **gizli katmandır** (login'den SONRA açılır) — `serverList` eleman sözlüğünde VARDIR ama `IsShow()=False`. TIP2 birleşik ekranda listbox **AÇIK** görünür. TIP1'de editline ya yoktur ya da gizlidir. Böylece M1 (login önce) ile TIP2 (birleşik) güvenilir ayrılır:

```
vis_editline ≥ 1 VE vis_serverList==1  → TIP2a/TIP2b (birleşik, editline sayısına göre)
vis_serverList==1 VE editline gizli/yok → TIP1 (OK görünür/var) | TIP1n (OK yok)
editline görünür VE serverList gizli katman → M1 resmi (login önce)
```

## 3. UYGULAMA

### pylib v5.4 (PLUSMAXGOD_PyScript.py, 8266 satır)
- `_is_shown(obj)` — YENİ: 1=gorunur, 0=gizli, -1=bilinmiyor (IsShow patlarsa)
- `_detect_matrix(pw)` — YENİDEN: sinyallere `vis_serverList/vis_regionList/vis_channelList/vis_okButton/vis_editline` görünürlük alanları eklendi; dönen dict artık `{'tip', 'code', 'label', 'flags', 'sig'}`. Sıra kuralı: TIP2/TIP1 branch'leri M3'ten ÖNCE (regionList-only clientlar code=M3'e düşse bile ekran birleşikse TIP2a — saha testinde yakalanan kenar durumu)
- `matrix()` — rapora **MATRIS OLASILIKLARI** tablosu: 9 satır (TIP1..M4) + +M5 + BÖLGE, eşleşen `[X]` işaretli; başlıkta `TIP:` + `MATRIS:` satırları; TIP'e göre önerilen akış; "tespit SU ANKI ekrana göre" uyarısı
- `detect = matrix` — takma ad (DLL `detect` komutu + raw kullanıcılar)
- `auto()` — akış TIP'E GÖRE SIRALANIR: TIP1/TIP1n `selserver(ok)` → 1.2sn → login; TIP2a/b/x `selserver(ok=0 sadece seç)` → login (connect login butonunda; TIP2x için 2sn sonra board-takip); M1 `login` → 2.5sn → `_auto_board_followup` (board açıldıysa seç+OK, açılmadıysa atla+lasterr yönlendir); M2 Marty ch>0 → CH butonu → login; M3/M4/? eski sıra
- `_auto_board_followup(log, srv, ch, ok)` — YENİ: login sonrası board açıldı mı kontrolü (vis_serverList==1 veya tip TIP1) + selserver
- `uiprobe` çıktısına `TIP ETIKETI:` satırı eklendi
- `PYLIB_VERSION = '5.4'` + banner güncellemesi + docstring v5.4 bloğu

### DLL v2.9 (MaxExecutor.cpp, ~2000 satır)
- **GOMULU PYLIB KALDIRILDI**: include satırı, `SyncEmbeddedPylib()` (yerine 5 satırlık açıklama yorumu), `WorkerThread` içindeki çağrı — `pylib_embedded.h` artık DERLEMEDE GEREKMEZ
- `detect` komutu: dispatch `cmd == "matrix" || cmd == "detect"` → `CmdMatrix()` (kullanıcı istediği "bi komut ver bize algılasın bilgi versin" = **detect**)
- Help: `matrix | detect` satırı (TUM olasılık tablosu notu) + auto satırı TIP akışı anlatır
- Sürüm dizgileri: konsol başlığı, banner ×2, ESI uyarıları ×3, BootImport guard → v2.9/v5.4; başlık yorum bloğuna v2.9 bölümü
- `ReadPylibVersion` korundu (disk pylib sürüm el-sıkışması hâlâ aktif)

## 4. DOĞRULAMA (statik + sahte-UI simülasyon — saha testi kullanıcıda)

```
verify_tips.py:
1) pylib v5.4 PY2 PARSE OK (lib2to3, 8266 satır)           ✓
2) 13 sembol mevcut (_is_shown/_detect_matrix/matrix/...)   ✓
3) TÜM matris olasılıkları tabloda (TIP1..M4/+M5/BOLGE)     ✓
4) auto() TIP akışı (TIP1/TIP2x/M1 followup fragmanları)    ✓
5) cpp parantez dengesi {261/261} (2090/2090)               ✓
6) pylib_embedded.h kod referansı YOK (yorumlar hariç)      ✓
7) cpp v2.9 sembolleri (detect dispatch + v2.9/v5.4)        ✓

test_tips.py (SAHTE-UI, 10 senaryo):
TIP1 → TIP1 ✓ | TIP1n → TIP1n ✓ | TIP1-gizli-editline → TIP1 ✓
TIP2a → TIP2a ✓ | TIP2b → TIP2b ✓ | M1-resmi(gizli katman) → M1 ✓
M2-marty → M2 ✓ | M4-coklu → M4 ✓ | TIP2x(IsShow-yok) → TIP2x ✓
BÖLGE+TIP2(regionList 2 + 2 alan) → TIP2a + coklu-bolge(2) ✓
SONUÇ: 10/10 OK
```

Kenar durumu düzeltmesi: ilk koşuda `regionList + k.adı/şifre` (çoklu-bölge birleşik ekran — kullanıcının Romania senaryosu) M3'e düşüyordu; TIP2 branch'i M3'ten öne alındı → TIP2a+`coklu-bolge(2)` doğru etiket.

## 5. SAHA KULLANIMI (beklentiler)

```
detect                            -> "TIP: TIP1 | MATRIS: M1 - ..." + TÜM olasılıklar [X]
matrix                            -> aynısı (takma ad)
detect yazmadan önce:             -> komutu acilista ILK ekranda calistir
                                     (tespit su anki ekrana gore; login ekranindayken
                                     board gizli katman oldugundan M1/TIP2 dogru ayrilir)
auto hesabim sifrem               -> TIP1: sec+OK -> login | TIP2: sec(ok=0) -> login
                                     | M1: login -> board acilinca sec+OK
auto hesabim sifrem pinim         -> 3. alanli (TIP2b/+M5)
```
- Sonuç dosyaları: `last_matrix.txt` (TIP + olasılık tablosu), `last_auto.txt` (sıralı adımlar), `last_login.txt`, `lasterr`
- **MaxExecutor.dll v2.9 derlemesi BUNDLE'DA HAZIR** (PE32 i386, zig cc ile derlendi) — `MaxInject.exe` de dahil; derleme gerekmez: DLL'i `C:\MaxExec\` içine kopyala + `MaxInject.exe` ile enjekte et. Kendi Visual Studio'nla derlemek istersen §3 (artık SADECE MaxExecutor.cpp — header yok!)
- Eski DLL (v2.6 binary) kullanıyorsan: `detect`/`matrix`/`auto` DLL komutları YOK — bundle'daki v2.9 DLL'i kullan
- **KRİTİK kurulum notu:** pylib_embedded.h kaldırıldığı için v2.9 DLL derleyen kullanıcının `C:\MaxExec\PLUSMAXGOD_PyScript.py` dosyasını elle kopyalaması ZORUNLU (bundle'da var)

## 6. BU COMMITTE DEĞİŞEN DOSYALAR

```
MaxExecutor/
  PLUSMAXGOD_PyScript.py        <- v5.4 (~333KB): TIP matris + detect + TIP sıralı auto
  MaxExecutor.cpp               <- v2.9 (~96KB): embed KALDIRILDI + detect dispatch + v2.9 dizgileri
  pylib_embedded.h              <- SILINDI (git rm — 1.7MB eski py kopyası)
  pylib.py                      <- SILINDI (git rm — eski v3.2 yedek kopya)
  KULLANIM.md                   <- v5.4: TIP1/TIP2 bölümü + detect + kurulum zorunluluğu
  README.md                     <- v2.9 üst özet + DOSYALAR (~~pylib_embedded.h~~) + detect
  MaxExecutor_bundle_v2.9_universal.zip  <- 9 dosya (header'sız + MaxExecutor.dll + MaxInject.exe)
  WORKLOG_v2.9_tips_matrix.md   <- BU dosya
```

NOT: MaxExecutor.dll v2.9 DERLENDI ve bundle'a kondu (PE32 i386, 589824 byte; MaxInject.exe 222208 byte ile birlikte) — kullanici Visual Studio derlemesi OZELLIKLE istege bagli; pylib_embedded.h artık projeye EKLENMEZ — sadece MaxExecutor.cpp.

## 6.5 DERLEME (oturum 24 tamamlayıcı istek: ".exe ve dll i de derle zipin içine at")

```
zig c++ -target x86-windows-gnu -shared -O2 -std=c++14 \
      -o MaxExecutor.dll MaxExecutor.cpp -luser32 -lkernel32 -lgdi32
   -> PE32 executable for MS Windows 6.00 (DLL), Intel i386, 12 sections, 589824 byte
zig c++ -target x86-windows-gnu -O2 -std=c++14 \
      -o MaxInject.exe MaxInject.cpp -luser32 -lkernel32 -ladvapi32
   -> PE32 executable for MS Windows 6.00 (console), Intel i386, 6 sections, 222208 byte
```
- Binary string kanıtı: 'MaxExecutor v2.9 PLUSMAXGOD' + 'TIP1/TIP2 matris' + 9× v5.4 referansı; eski 'v2.8' banner KALMADI (0)
- MaxInject.exe 222208 byte = önceki v2.6 dönemi derlemeyle BİREBİR aynı boyut (kaynak değişmedi — tutarlılık kanıtı)
- Bundle v2.9 9 dosyaya genişletildi: 7 kaynak/dok + MaxExecutor.dll + MaxInject.exe

## 7. SONRAKİ ADIMLAR

1. ~~DLL v2.9 derlemesi~~ TAMAM — bundle'da HAZIR derlenmiş binary var (MaxExecutor.dll + MaxInject.exe); Visual Studio derlemesi isteyen için §3 (SADECE MaxExecutor.cpp — header yok!)
2. `C:\MaxExec\PLUSMAXGOD_PyScript.py`'yi bundle'dan güncelle (v5.4)
3. **Saha testi 18**: 2-3 farklı sunucuda `detect` çıktısını paylaş (TIP etiketi + [X] tablosu) — sınıflandırma oranını ölçelim
4. TIP2x çıkan serverlarda: board görünürken `detect`'i tekrar çalıştır (teyit)
5. Öneri (sonraki oturum): `relogin`'in `_MATRIX` globalini kullanarak TIP-farkındalı hale getirilmesi (TIP1'de selserver adımını login'den ÖNCE yapması)
