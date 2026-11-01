# WORKLOG — pylib v5.7 "ALT-TIP" (login parametre yapisinin harfi)

**Tarih:** 2026-11-02 · **Sürüm:** pylib v5.7 (DLL v2.9.1 değişmedi) · **Motor:** MATRIS v6.1 (v6 + ALT-TIP)
**Tetikleyici:** Saha oturumu 27 — v5.6 saha testi DOĞRULANDI (TIP1 + GUVEN: YUKSEK). Kullanıcı talebi:

> "tip1 tamamda k.adı + şifre bilgisi mi var yoksa k.adı + şifre + pid bilgisi mi var? yani 3 parametreli mi, 2 parametreli mi bunu da belirtmeli. tip1 A / tip2 B gibisinden"

## 1. Tasarım kararı

TIP1 ekran yapısını söylüyor (server seçme ayrı + OK), ama **login ekranının kaç alan
istediğini** taşımıyordu. Ayrı bir harf katmanı (ALT-TIP) eklendi — TIP kararına DOKUNULMADI
(v5.6 kazananı bozmamak için):

| ALT-TIP | Anlam | Ölçüt (kanıt) |
|---|---|---|
| **TIP1-A** | 2-param (k.adı + şifre) | editline=2 |
| **TIP1-B** | 3-param (+PIN/PID/guard) | editline>=3 |
| **TIP1-S** | tek-alan (sadece id) | editline=1 |
| **TIP1-X** | belirsiz | editline=0 (login alanı agaçta yok) → login ekranı açılınca `_auto_tick` gerçek harfi yazar |
| TIP2-A / TIP2-B / TIP2-X | TIP2a/b/x'in düzenli gösterimi | iç token'lar DEĞİŞMEDİ (auto/relogin %100 uyumlu) |

**Kanıt felsefesi:** editline SAYISI birincil kanıttır (isimlendirme karışıksa bile sayı
yertutucu). `wndMgr Hide()` çocuklara yayılmaz kuralı burada LEHİMİZE işler: login board
gizliyken bile editline'lar agaçtaysa sayı doğrudur — NightTown saha çıktısı
(`editline=2, third=0, id=idEditLine, pwd=pwdEditLine`) → **TIP1-A**.
Kanit satırı alan adlarını gösterir (falsifikasyon açık): `[editline=2, 3.alan=0, id=..., pwd=...]`.

## 2. Kod değişiklikleri (PLUSMAXGOD_PyScript.py)

1. **`_login_param_yapisi(pw)` YENİ** — `(n, desc, harf, kanit)` döner; `_classify_editlines`
   sonuçundan sayı + rol + 3.alan adı çıkarır (satır ~1547).
2. **`_detect_matrix`** — `sig['param'/'login_yapisi'/'param_kanit']`, dönüşe
   `'alt'/'param'/'param_desc'` alanları; KANIT zincirine `PARAM login-yapisi: ...` satırı.
3. **`matrix()`/`detect`** — `ALT-TIP:` ve `PARAM:` satırları; olasılık tablosunda harf notları;
   `[X] ALT-TIP: ...` işaret satırı; ONERILEN AKIS'a yapı bilgisi; v5.7 dipnotu.
4. **`auto()`** — log'a `ALT-TIP:` satırı; `_MATRIX['alt'/'param']` kaydı.
5. **`_auto_tick` (faz 1/3, st==1)** — login ekranı açıldığı AN param yapısı YENİDEN ölçülür:
   `[AUTO] login-yapisi: 2-param: k.adı + şifre (ALT-TIP: TIP1-A) [...]` — **TIP1-X burada
   kesinleşir**, `_MATRIX['alt']` güncellenir.
6. `PYLIB_VERSION = '5.7'`; başlık dokümanı + pylib_load geçmişi v5.7 bloğu.

## 3. DLL (v2.9.1) — kaynak banner güncellendi, İKİLİ DEĞİŞMEDİ

`MaxExecutor.cpp`: bootstrap uyarı dizgileri + `help` banner v5.7; help'e ALT-TIP harf
açıklaması (2 satır). DLL major-5 kontrolü v5.7'yi sorunsuz okur → derleme GEREKMEZ.

## 4. Doğrulama

- `scripts/check_py2.py`: lib2to3 PY2 parse **OK** + py3 transpile derlemesi **OK** + 29 işaret OK.
- `scripts/test_matrix_v57.py` (YENİ, mock UI): **27/27 GEÇTİ**
  (S1 NightTown→TIP1-A/2, S1p+pin→TIP1-B/3, S1z→TIP1-X, S1s→TIP1-S/1,
  S2→TIP2-A/2, S2b→TIP2-B/3, S3 M1+param, S4→TIP2-X, S7 auto-vis 0/1/2,
  S8 auto akış + tick kesinleştirme `_MATRIX[alt]=TIP1-A` + live satır,
  S9 matrix rapor metni ALT-TIP/PARAM/KANIT).
- `scripts/test_matrix_v56.py` (regresyon): **TAMAM** — v5.6 davranışı korunuyor.

## 5. Dosyalar

- `PLUSMAXGOD_PyScript.py` v5.7 (canonical: `download/`, senkron: `mx29/`, repo)
- `MaxExecutor.cpp` (banner v5.7), `FIX-NOTU_v5.7.txt`, `WORKLOG_v5.7_alttip.md`, `README.md` (v2.9.1-P4 bloğu)
- `MaxExecutor_bundle_v2.9.1_matris_v6.1.zip` (18 dosya)
- `scripts/test_matrix_v57.py`, `scripts/check_py2.py` (v5.7 işaretleri)

## 6. Bilinen sınırlar (şeffaf)

- TIP1-X yalnızca login alanları ağaçta hiç yoksa verilir (lazy-UI client'ları) — auto
  login ekranını bekleyip harfi kesinleştirir; akış değişmez.
- Server board'unda VIP/anahtar tipi editline olan client'larda 3. alan sayılabilir (B);
  kanıt satırı 3.alan ADINI gösterdiği için sahada ayırt edilir.
- KATMAN B pack okuması kullanıcı client'ında `None` (önceki oturumdan bilinen); ALT-TIP
  KATMAN A tarzı canlı ölçümle çalıştığı için etkilenmez.
