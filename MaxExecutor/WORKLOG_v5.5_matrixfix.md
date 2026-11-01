# WORKLOG — MaxExecutor v2.9.1 + pylib v5.5 "MATRIS-FIX" (oturum 26)

Tarih: 2026-11-01/02 | Tetik: kullanici saha raporu (NightTown serveri)

## KULLANICI RAPORU (birebir)
"diyo fakat suan denedigim server ayni ekranda degil? hatta auto ile komut
verdim k.adi sifre dogru olmasina ragmen sv secmedigi icin giremedi, ve
tespit ettigin matris hatali. once server ve ch seciyom ok a basiyom sonra
diger ekrana geciriyor. diger ekranda da k.adi sifre ve giris butonu var
sana bunlari dedim diye kopya cekme hatayi bul. bu ilk sv secme ekrani
dedigim falan filan dedigim files [NightTownFullpack.rar]
matris algilama mantigini tamamen detaylica kontrol et bu MVP GOD Tier
urun olacagi icin hataya yer yok."

## KANIT ZINCIRI
1. MaxExec_sonuc.rar (kullanicinin C:\MaxExec'i) acildi:
   - last_matrix.txt : TIP=TIP2a, vis_editline=2, vis_serverList=1,
     vis_okButton=1  <-- yanlis TIP2a karari buradan
   - last_serverlist.txt : server adedi=1 "01. Romania", CH1..CH4, ListBox2
   - last_auto.txt : "selserver(0, 0, ok=False) [TIP2: sadece SEC]" ->
     OK hic basilmadi -> login ekranina gecis yok -> giris olmadi
   - last_error.txt : LOGIN_FAILURE: NOID (eski deneme; 'admin' o sw'de yok)
2. Kullanici tanimi ile saha baglasti: once server+CH+OK ekrani, SONRA
   login ekrani = TIP1.
3. Google Drive NightTownFullpack.rar (1.19GB) indirildi; client intrologin
   kaynagi pakette YOK (bot/lib fullpack) -> teshis kod+kanit uzerinden.

## KOK NEDENLER (2 TASARIM HATASI)
### H1 — _is_shown yalnizca KENDI IsShow bayragini okuyordu
Hide() yalnizca board'un kendi bayragini kapatir; cocuk editline'larin
bayragi True kalir -> gizli login board'unun cocuklari "gorunur" olculdu ->
vis_editline=2 -> TIP2a. AYNI hata resmi M1 akisinda da TIP2a uretir.
### H2 — auto() OK sonrasi time.sleep ile bekliyordu
Komut ana thread'de: uyku sirasinda oyun dongusu durur; OK -> baglanti ->
login-ekrani gecisi ISLENMEZ. TIP1'te senkron bekleme matematiksel olarak
calisamaz. (v5.4'te TIP1 yolu hic sahada dogru dusmedi.)

## FIXLER (pylib v5.5 — DLL v2.9.1 DEGISMEDI)
- _eff_visible: EFEKTIF gorunurluk (kendi + tum atalar; parentWindow ->
  GetParent zinciri) | _is_shown geriye-uyumlu sarmalayici oldu
- _offscreen: GetGlobalPosition ekrandisi = gizli board hilesi kaniti
- _parent_chain + _board_relation: LCA analizi — ortak ata KOK ise AYRI
  ekran (TIP1 kaniti), ortak ata BOARD ise AYNI ekran (TIP2 kaniti)
- _detect_matrix karar agaci yeniden yazildi: "EKRANDA NE AKTIFSE O EKRAN"
  (server_aktif x login_aktif x el_gizli x ayri_board matrisi);
  sig'e server_aktif/login_aktif/eff_idEditLine/offscreen_els/ayri_board
- auto(): TIP1 ARTIK DURUM MAKINESI — selserver(ok) -> _AUTO faz=1 ->
  _auto_tick (DLL 150ms nabzi) her karede login ekrani EFEKTIF gorunur mu
  olcer, dustugu an login atar (max 25sn + asim raporu, [AUTO] canli)
- TIP2x iki-fazli adaptif: TIP2 yolu (ok=0+login) -> 10sn ilerleme yoksa
  TIP1 yolu (ok=1 -> bekle -> login); LOGIN_FAILURE geldi ise akis dogru
  sayilir (kimlik hatasi), yol degistirilmez (_LOGIN_FAIL_T isareti)
- relogin step-4: login ekrani EFEKTIF gorunmesini bekler (6sn yedek)
- matrix() raporu: TIP1 tavsiyesi "auto tek komut - elle bisey yapma" +
  v5.5 not satiri; TIP2x aciklamasi iki-fazli olarak guncellendi
- pylib_load raporuna v5.5 kok-neden blogu

## DOGRULAMA
- lib2to3 PY2 parse + py3 transpile compile: OK (scripts/check_py2.py)
- scripts/test_matrix_v55.py: 24/24 GECTI
  T1 kullanici serveri TIP1(ayri_board=1) + auto: ok=1 -> bekle -> login
  T2 TIP2a KORUNDU | T3 resmi M1 artik DOGRU | T4 ekrandisi kaniti TIP1
  T5 TIP2x iki-fazli akis | T6 board_relation birim
- Surum kilidi: DLL ReadPylibVersion atoi>=4 -> v5.5 UYUMLU, derleme yok

## PAKET
MaxExecutor_bundle_v2.9.1_matrixfix.zip:
MaxExecutor.dll (v2.9.1, ayni binary) + MaxInject.exe + PLUSMAXGOD_PyScript.py
(v5.5) + MaxExecutor.cpp + MaxInject.cpp + shim_ucrt.c + README.md +
KULLANIM.md + RESEARCH.md + PLUSQuest.md + FIX-NOTU_v2.9.1.txt +
FIX-NOTU_v5.5.txt + WORKLOG_v2.9.1_detectfix.md + WORKLOG_v5.5_matrixfix.md
(pylib_embedded.h YOK — tek kaynak PLUSMAXGOD_PyScript.py)

## SONRAKI ADIMLAR (saha)
1. v5.5 pylib'i C:\MaxExec\ icine kopyala -> banner "v5.5 (uyumlu)"
2. detect -> TIP1 + [v5.5 kanit: ...] etiketi beklenir
3. auto <hesap> <sifre> -> [AUTO] satirlarindan otomatik girisi izle
4. Ikinci bir TIP2 (birlesik) serverda da detect+auto testi (regresyon)
