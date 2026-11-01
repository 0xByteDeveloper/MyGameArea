# WORKLOG — Oturum 23 (2 Kasım 2026): MATRIX ALGILAMA + TEK KOMUT OTO-GİRİŞ
**MaxExecutor v2.8 + pylib v5.3 — "serverın hangi matrisde olduğunu algıla ve ona göre davran"**

> Kullanıcı sorusu: *"MaxExecutor_bundle_v2.7_universal bu bana serverin hangi yapı matrisinde olduğunu algılayıp söyleyebilir mi? hem hangi matriste olduğunu algılayıp hem de ona göre komut gönderebilir mi?"*

---

## 1. CEVAP — ÖNCE NE VARDI, NE EKLENDİ

| Soru | v2.7'deki durum | v2.8'deki durum |
|---|---|---|
| "Matrisi algılayıp söyleyebilir mi?" | Kısmen: `uiprobe` ham envanter çıkarır (etiket yok, M1–M5'i kullanıcı çıkarmalıydı) | **`matrix`** — M1/M1v/M2/M3/M4 etiketi + **+M5** PIN bayrağı, sinyal tablosu, önerilen akış → `last_matrix.txt` |
| "Algılayıp ona göre komut gönderebilir mi?" | Kısmen: `login`/`selserver` zaten uyarlamalıydı (3 yol / 4 yol sıralar) ama akışı kullanıcı kurmalıydı | **`auto <id> <pwd> [3.alan] [srv] [ch]`** — TEK KOMUT: matrisi algılar → listbox'lıysa `selserver` (OK varsa basar/yoksa basmaz — otomatik) → `login`; Marty ise direkt `login` → `last_auto.txt` |

## 2. SINIFLANDIRMA KURALLARI (`_detect_matrix`, RESEARCH.md'deki 5 mimariyle birebir)

```
M4  : pw.autoLogin metodu VEYA id_editline_s/pwd_editlines container (reign2/merlis)
M2  : serverList YOK + (channelButton dict VEYA pw.SetChannel)   (Marty 5.3)
M1  : serverList + (channelList VEYA OK butonu)                  (resmi 2014)
M1v : serverList var, CH listesi/OK farklı                       (varyant)
M3  : UI editline var ama listbox yok                            (özel/eski katman)
+M5 : pin içeren 3. editline (her matrisle birleşebilir)          (proyecto-metin)
+coklu-bolge(n) : regionList n>1 (Romania vb.) + guard-code-2FA bayrağı
'?' : LoginWindow yok / sinyalsiz → uiprobe önerilir, login 3 yolu yine denenir
```

Sinyaller raporda satır satır gösterilir: `serverList, channelList, regionList, okButton, channelButton, SetChannel, pw.Connect, autoLogin, container, editline, third`.

## 3. UYGULAMA

### pylib v5.3 (PLUSMAXGOD_PyScript.py, 8054 satır)
- `_detect_matrix(pw)` — sinyal toplama + yukarıdaki kurallar; dict döner `{code, label, flags, sig}`
- `matrix()` — rapor üretir (`last_matrix.txt`), sonucu `_MATRIX` globalinde saklar
- `auto(user, pwd, third=None, srv=0, ch=0, ok=None)` —
  - ADIM 1: M1/M1v/M3 + serverList varsa `selserver(srv, ch, ok)` — `ok=None` ise OK butonu VARSA 1, YOKSA 0 (otomatik karar)
  - M2 + ch>0: `selserver(0, ch, 0)` (CH butonu); M2 ch=0: adım atlanır (server gömülü)
  - ADIM 2: `login(user, pwd, third)` (kendisi uyarlamalı: UI → pw.Connect → paket)
  - M2/M4/PIN/guard durumlarında third verilmediyse UYARI satırı
  - Kimlik `login.dat`'a kaydedilir (relogin bunu kullanır) → `last_auto.txt`
- `uiprobe` çıktısına "TEK KOMUT: auto ..." + "ETIKET: matrix" satırları eklendi
- Yükleme banner'ına v5.3 bloğu eklendi; `PYLIB_VERSION = '5.3'`

### DLL v2.8 (MaxExecutor.cpp, 2036 satır)
- `CmdMatrix()` → `maxlib.matrix()`
- `CmdAuto(id, pwd, third)` → `maxlib.auto(r'%s', r'%s'[, r'%s'])`
- Dispatch: `matrix` / `auto` + eksik-argüman kullanım mesajları (FIX-24 dersi)
- Help: matrix + auto satırları giris akışı bölümünde
- Sürüm dizgileri: konsol başlığı, banner, ESI uyarıları → v2.8/v5.3; başlık yorum bloğuna v2.8 notu
- `pylib_embedded.h` v5.3 yeniden üretildi (scripts/embed_pylib.py, 332367 byte kaynak)

## 4. DOĞRULAMA (statik — saha testi kullanıcıda)

```
1) pylib v5.3 PY2 PARSE OK (lib2to3, 8054 satır)      ✓
2) 10 sembol mevcut (matrix/auto/_detect_matrix/...)   ✓
3) auto() akışı: detect -> selserver(ok-otomatik) -> login ✓
4) cpp parantez dengesi {266/266} (2097/2097)          ✓
5) cpp v2.8 sembolleri (CmdMatrix/CmdAuto/dispatch/help) ✓
6) pylib_embedded.h v5.3 (332367 byte)                 ✓
```

Doğrulama scripti: `scripts/verify_matrix.py` (bu depoda değil, geliştirme ortamında).

## 5. SAHA KULLANIMI (beklentiler)

```
matrix                          -> "MATRIS: M1 - Resmi 2014 standart ..." + sinyaller + akış
auto hesabim sifrem             -> M1 ise: selserver(0,0,ok=1) + login; M2 ise: direkt login
auto hesabim sifrem 1234        -> PIN/guard/slot'lu serverlarda 3. alanla
auto hesabim sifrem abc 1 2     -> server=1 ch=2 elle
```
- `last_matrix.txt` / `last_auto.txt` / `last_login.txt` / `last_status.txt` takip için
- Eski DLL (v2.6 binary) ile: `matrix`/`auto` DLL komutları YOK (v2.8 kaynak derlenmeli) — ama pylib v5.3 diskteyken `raw maxlib.matrix()` / `exec` ile de çağrılabilir; `login`/`selserver` v5.2 davranışıyla çalışır
- v2.8 DLL derlenince 4 komut tek yerden: `uiprobe` (ham envanter) → `matrix` (etiketli teşhis) → `auto` (algıla+uygula) → `relogin` (tekrar giriş)

## 6. BU COMMITTE DEĞİŞEN DOSYALAR

```
MaxExecutor/
  PLUSMAXGOD_PyScript.py        <- v5.3 (332367 byte): _detect_matrix + matrix + auto
  MaxExecutor.cpp               <- v2.8 (96382 byte): CmdMatrix + CmdAuto + dispatch/help/banner
  pylib_embedded.h              <- v5.3 embed (1736511 byte)
  KULLANIM.md                   <- v5.3: MATRIX+AUTO bölümü + akışlar + sorun giderme satırları
  README.md                     <- v2.8/v5.3 üst özet + DOSYALAR + komut listesi
  MaxExecutor_bundle_v2.8_universal.zip  <- 8 dosya, 2.2 MB paket
  WORKLOG_v2.8_matrix_auto.md   <- BU dosya
```

NOT: Önceki oturumun commit'i (307f8ba, v2.7 universal) pushlanmadan kalmıştı — bu push ile birlikte gidiyor. MaxExecutor.dll binary'si hâlen v2.6 derlemesi (kullanıcı v2.8 kaynağını Visual Studio Release/x86 derleyecek).

## 7. SONRAKİ ADIMLAR

1. **DLL v2.8 derlemesi** (kullanıcı): Visual Studio → Release/x86 → MaxExecutor.cpp + pylib_embedded.h
2. **Saha testi 17**: `matrix` çıktısını 2-3 farklı sunucuda paylaş (matris etiketi + sinyaller) — sınıflandırma oranını ölçeceğiz
3. `auto` akışında takılırsa: `last_auto.txt` + `last_matrix.txt` ikilisi teşhis için yeterli kanıt
4. Öneri (sonraki oturum): `matrix` sonucuna göre `relogin`'in de matris-farkındalı hale getirilmesi (M2'de selserver adımını atlamak) — `_MATRIX` globali zaten hazır
