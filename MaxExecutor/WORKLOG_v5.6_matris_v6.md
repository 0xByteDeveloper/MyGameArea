# WORKLOG — pylib v5.6 MATRIS v6 (KANIT-TABANLI)

**Tarih:** 2026-11-02 · **Çift:** MaxExecutor v2.9.1 (DLL değişmedi) + pylib **v5.6**
**Tetik:** Kullanıcının 2. saha raporu — *"aynı ekranda değil maalesef"* — v5.5 yaması yüklü
olmasına rağmen `detect` **yine TIP2a** dedi; gerçek akış TIP1 (önce server+CH+OK,
sonra ayrı login ekranı) ve `auto` OK'a basmadığı için şifre doğru olduğu halde giriş olmadı.

---

## 1. SAHA KANITI (2. rapor — v5.5 yüklüyken)

```
[MAXLIB] pylib v5.5 aktif
--- SINYALLER (varlik + gorunurluk) ---
  ayri_board      : -1      <-- v5.5'in LCA/parent-zinciri kaniti KURULAMADI
  eff_idEditLine  : 1       <-- editline "EFEKTIF gorunur" sanildi (YANLIS)
  offscreen_els   : 0       <-- GetGlobalPosition olcumu HIC CALISMADI
  vis_editline    : 2       <-- editline'larin KENDI bayragi 1 (board gizli olsa bile)
  server_aktif    : 1, login_aktif : 1
TIP: TIP2a  <-- HATALI KARAR (gercek: TIP1)
```

## 2. KÖK NEDEN (kör yama değil — kanıtlı teşhis)

v5.5'in **üç kanıt yolu da client C++ API'sine bağımlıydı** ve kullanıcının client'ında
bu API'ler YOK. Sinyal tablosu üç yolu da çökmüş olarak raporluyor:

1. **Parent zinciri kurulamıyor** (`_parent_of` → `parentWindow` attr / `GetParent()`):
   kullanıcının client'ında ikisi de çözümlemiyor → `ayri_board = -1`, LCA kanıtı hiç
   kurulamadı. v5.5'in ana fikri (zincirde gizli ata ara) bu client'ta çalışamaz.
2. **`GetGlobalPosition` yok** → `offscreen_els` ölçümü her elemanda `-1` (okunamadı)
   döndürdü; "ekrandışı" kanıtı hiç üretilemedi.
3. **Kritik fallback hatası:** `_eff_visible` zincir kuramazsa **1 (GÖRÜNÜR)** döndürüyordu
   (`return 1  # atasi yok (kok pencere) veya atalar okunamadi`). Zincir kurulamayan
   TÜM editline'lar "kesin görünür" sanıldı → `vis_els=True` → `server_aktif and vis_els`
   → **TIP2a**. (v5.4'ün hatasını fallback seviyesinde kopyalamıştı.)

**Ek UI gerçek** (düzeltmenin temeli): Metin2 wndMgr'de `Hide()` **çocuklara yayılmaz** —
board'un KENDİ bayrağı 0 olur, çocuk editline'ların bayrağı 1 kalır. Bu yüzden
editline bayrağını okumak (v5.4) ve zincirden efektif görünürlük hesaplamak (v5.5)
her ikisi de yanlış yertutucu. **Doğru yer: BOARD seviyesindeki attr'ların ham bayrağı.**

**Ground-truth doğrulama** (araştırma havuzu, 28 gerçek intrologin.py): MS5.8/Türk
files sınıfı akış `Open()` → cold-start `else` dalı → `__OpenServerBoard()` →
`serverBoard.Show()` + `connectBoard.Hide()` + `loginBoard.Hide()`. Yani kullanıcı
sunucusunda login board **gerçekten gizleniyor** — board ham bayrağı (0) okunabilse
karar kesin TIP1'di.

## 3. ÇÖZÜM — v5.6 KANIT-TABANLI MATRİS v6

Kanıt sırası **C++ API'siz ground truth önce**:

| Katman | Yöntem | Neden sağlam |
|---|---|---|
| **A** | `_scan_boards` + `_board_verdict`: `dir(pw)` içindeki board-vari attr'ların KENDİ ham `IsShow` bayrağı (`serverBoard=1, connectBoard=0` → TIP1 kanıti) | Parent zinciri GEREKMEZ; Hide board'un kendi bayrağını kapattığı için doğru yertutucu. `main/save/pin` notr, `server*` server-, `login/connect*` login-board. |
| **B-1** | `_source_evidence` → `_pack_read` (v4.7 kanıtlı pack.Get yolu) ile `root/intrologin.py` okunur → `_src_first_screen`: TÜM `def Open` blokları taranır; server-acici/login-acici desenleri; iki acici de varsa **SON acici** soğuk-başlangıç dalıdır (`rfind` — `find` ilk geçişi verdiği için USE_OPENID gibi erken ikinci çağrılar sonucu ters çeviriyordu; saha kalibrasyonunda yakalandı) | Client'in KENDİ durum makinesi — UI API'sinden tamamen bağımsız gerçek. |
| **B-2** | `__LoadScript` adından UIScript dict'i okunur → `_eval_uiscript` (py2 eval, tanımsız sabitlere 1024 retry) → `_topo_from_tree`: editline ve serverList'in **en yakın board atası** karşılaştırılır. AYNI board = TIP2 kesin kanıtı; FARKLI = TIP1/M1 kesin kanıtı. Eval olmazsa `_topo_from_text` (ZAYIF kanıt) | UI'ın gerçek kurulma topolojisi — görsellik/katman hilelerinden etkilenmez. |
| **C** | v5.5 kalır: `_eff_visible` + `_offscreen` + `_board_relation` — **yalnızca yardımcı kanıt** | Zincir kurulamazsa artık **-1 (bilinmiyor)** döner; asla 1 dönmez. |

**Yeni karar ağacı (saha hatasını kapatan kural):**

```
1) UIScript topolojisi AYNI board  -> TIP2a/b  (kesin kanıt — tek TIP2 yolu)
2) UIScript FARKLI board           -> SIRALI ekranlar:
      board bayrağı 'server'/'l-off'  -> TIP1 (OK var) / TIP1n
      board bayrağı 'login'/'s-off'   -> M1 / M3
      bayrak yoksa kaynak Open()      -> server: TIP1 | login: M1
3) Topoloji yok                    -> board bayrağı karar verir
      'both' (katmanlı kapak deseni)  -> kaynak Open(); o da yoksa TIP2x
4) HİÇBİR kanıt yok                -> TIP2x (iki-fazlı adaptif auto — GÜVENLİ)
      "ikisi de görünüyor" ARTIK ASLA kesin TIP2a demez
```

`detect` çıktısına **GUVEN (YÜKSEK/ORTA/DÜŞÜK) + KANIT** satırları eklendi (hangi
katman ne dedi); `auto`/`last_auto.txt`'a da aynı kanıt yazılır.

**Auto/relogin bekleme düzeltmeleri:** `_auto_login_board_visible` artık ÖNCE board
bayrağına bakar: `1` = login board açık (+ server kapalı), `0` = kesin kapalı,
`2` = **kapak deseni** (iki board da açık → 8 sn yedek sonra yine de login atılır —
SetText/CallEvent gizli arkadaki alanlara da güvenle uygulanır), `-1` = bilinmiyor →
eski eff yolu. `_auto_tick` faz-4 (M1 serverboard bekleme) de `ekran_bayragi=='server'`
kanıtını kullanır. `relogin` st-4 aynı yardımcıyı kullanır.

**Ek tespit:** `_OKBTN_NAMES`'e resmi client adı **`okButton`** eklendi
(`selectConnectButton` varyantı bulunamayan clientlarda OK butonu hiç bulunamıyordu).

## 4. DOĞRULAMA (statik + mantık + gerçek kaynak kalibrasyonu)

- `scripts/check_py2.py`: lib2to3 **PY2 parse OK** + py3 transpile compile OK + 20 içerik işareti OK (v5.6).
- `scripts/test_matrix_v56.py`: **18/18 GECTI** —
  S1 NightTown (kullanıcı senaryosu: zincir kurulamaz + board bayrağı + kaynak) → **TIP1, GÜVEN=YÜKSEK**;
  S1b yalnız kaynak kanıtı → TIP1; S2 gerçek birleşik (aynı-board kanıtı) → TIP2a (korundu);
  S3 M1; S4 kanıt yok → **TIP2x** (güvenli); S5 kapak+Open()=server → TIP1; S6 kapak+kaynak yok → TIP2x;
  `_auto_login_board_visible` 0/1/2 durumları; auto(TIP1) → `selserver(0,0,ok=1)` + faz=1 +
  tick login attı; `_src_first_screen` MS5.8 deseni; `_topo_from_tree` farklı/aynı board.
- **30 gerçek intrologin.py kalibrasyonu**: MS5.8 (TR) + m2dev baseline + Lead + battal34 +
  Anka2 → `server` (PVP ailesi, kullanıcının sınıfı); N2Play/Auriga/yumulk → `login` (resmi akış);
  Marty/reign2 → `?` (farklı mimari — dürüst belirsiz). 15 server / 6 login / 7 ? — hiçbiri yanlış kesin karar vermedi.
- KATMAN B gerçek-kaynak hataları kalibrasyonda yakalandı ve düzeltildi:
  (a) ilk `def Open` başka sınıfa ait olabiliyor → TÜM Open blokları taranıyor;
  (b) `find` ilk geçişi veriyordu → `rfind` (son acici = soğuk-başlangıç);
  (c) metin-yedeği tırnak mantığı çöp döndürüyordu → `"name" : "X"` çifti gezicisi.
- Not: Kullanıcının NightTownFullpack.rar (1.19 GB) yine indirildi; içinde EterPack
  (root.pak) yok — intrologin kaynağı pack'te. Bu yüzden KATMAN B, `detect` anında
  **kullanıcının kendi client'ında** pack.Get ile okuyacak (v4.7'de kanıtlanmış yol).

## 5. PAKET

- `PLUSMAXGOD_PyScript.py` **v5.6** — tek pylib kaynağı (pylib_embedded.h yok).
- `MaxExecutor.cpp` — banner/help/bootstrap dizgileri v5.6 (DLL ikili değişmedi;
  v2.9.1 DLL major-5 kontrolüyle v5.6'yı "uyumlu" okur, C:\MaxExec'ten yükler).
- `MaxExecutor_bundle_v2.9.1_matris_v6.zip` — 14 dosya (dll+exe+py+cpp+shim+README+
  KULLANIM+RESEARCH+PLUSQuest+2 FIX-NOTU+3 WORKLOG).
- `FIX-NOTU_v5.6.txt` — kurulum + saha test formülü.

## 6. SONRAKİ ADIMLAR (saha)

1. `PLUSMAXGOD_PyScript.py` (v5.6) → `C:\MaxExec\` (DLL'e dokunma).
2. Oyunu aç, server seçme ekranında BEKLE → `detect` çalıştır.
   Beklenen: `TIP1`, `GUVEN: YUKSEK`, KANIT satırlarında
   `KATMAN A board-bayragi: ekran=server [server: serverBoard=1 | login: ...=0]`
   ve/veya `KATMAN B kaynak: root/intrologin.py -> Open() ilk-ekran=server` +
   `KATMAN B topoloji: ... -> farkli-board`.
3. `auto admin 1` — beklenen: ADIM 1 `selserver(0,0,ok=1)` → OK'a basılır →
   `[AUTO] login ekrani acildi (login board ACIK + server board KAPALI)` → login atılır.
4. `detect` çıktısı (last_matrix.txt) ve `last_auto.txt` her sonuçla paylaşılmalı —
   kanıt satırları bir sonraki iyileştirmenin girdisi.
```
