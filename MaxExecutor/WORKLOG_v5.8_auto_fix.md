# WORKLOG v5.8 — AUTO GİRİŞ SAHA-FİX (oturum 27c)

**Tarih:** 2026-11-02 · **pylib:** 5.7 → **5.8** · **DLL:** v2.9.1 (ikili DEĞİŞMEDİ)
**Tetik (saha çıktısı):** `auto admin 1` → TIP1/TIP1-A doğru algılandı, selserver OK bastı
(`serverSelectButton.CallEvent()` → "server board onaylandı") ama faz-1
`ZAMAN ASIMI (faz 1)` + `t+128.0` ile durdu. İkinci `auto` çalıştırmasında
login board aktif bulundu (KANIT: `serverBoard=0 | connectBoard=1, loginBoard=1`)
ve `loginButton.CallEvent()` basıldı; `[STATUS] CONN=0` sonrası rapor yoktu.

## 1. Kanıt zinciri → kök neden

| Kanıt (kullanıcı çıktısından) | Sonuç |
| --- | --- |
| 2. çalıştırmada `connectBoard=1, loginBoard=1, serverBoard=0` | OK gerçekte işledi; ekran sunucudan login'e döndü |
| Zaman aşımı `t+128.0` (sozde max 25sn) | DLL 150ms nabzi ~100sn işleyemedi → auth bağlantısı ana-thread'i meşgul etti; tick ilk fırsatta deadline aşımı gördü |
| faz-1 penceresi 25sn | Bu client'ın auth süresine göre kısaydı |
| Timeout satırı sinyal içermiyordu | Teşhis imkânsızdı ("neden beklendiği" yazmıyordu) |
| faz-9'da LOGIN_FAILURE kontrolü yoktu | Şifre reddi sessizce 30sn bekleyip zaman aşımına düşerdi |
| selserver "onaylandı" diyor, doğrulama yok | CallEvent sonrası geçiş işlenmediyse erken uyarı yok |

## 2. Değişiklikler (yalnızca pylib; TIP/ALT-TIP mantığı ve token'lar aynen)

1. **`_auto_board_snapshot()` (YENİ)** — tek satır ekran görüntüsü:
   `board:server=<adlar|-> login=<adlar|-> CONN=<0/1/-1>` (KATMAN A bayrakları + `net.IsConnect()`).
2. **faz-1 deadline 25→60sn**; TIP2x 2.faz 20→45sn, M1 faz-4 25→45sn, faz-9 30/25→45sn.
3. **OK-etki izleme (faz-1)** — `srv_on0`/`srv_kapandi` durum anahtarları: server board
   1→0 geçişinde `OK isledi: server board KAPANDI - auth baglantisi / login ekrani bekleniyor`.
4. **Zaman aşımı tanısı** — satır artık `[board:...]` taşır + server board hâlâ açıksa
   `tani: server board HALA ACIK -> OK etkisiz olabilir veya auth baglantisi kurulamadi`.
5. **faz-9 LOGIN_FAILURE raporu** — `_LOGIN_FAIL_T` (OnLoginFailure hook'u) tetiklendiyse
   `LOGIN HATA: LOGIN_FAILURE: <kod>` + öneri yazıp durur; aksi hâlde CONN'lu bekleme satırı.
6. **selserver OK doğrulaması** — CallEvent +1.0sn'de board durumu okunur:
   `UYARI: OK sonrasi server board HALA ACIK` / `OK: login board acildi (...) - gecis tamam`.
7. **`auto()` durum anahtarları** — `srv_on0/srv_kapandi/lf_rapor/lf9` resetlendi.
8. Banner + `matrix` NOT bölümüne v5.8 satırları; `PYLIB_VERSION='5.8'`.

## 3. Kullanıcı sorularının yanıtla bağlantısı

- **"3. parametrenin olmadığını ne ile kontrol ettin?"** → TIP1-A kanıtı 5 kaynaktır:
  (1) `_scan_editlines` dir(pw)+GetChild taraması → toplam **editline=2** (idEditLine,
  pwdEditLine); `Hide()` çocuklara yayılmadığından gizli login board'un alanları da bu
  sayımdadır (ekran hangi board'da olursa olsun sayı geçerlidir). (2) kalan editline
  yok → `3.alan=0`. (3) KATMAN B: `intrologin.py` Open() + `LoginWindow.py` topolojisi —
  kaynakta 3. editline oluşturma kanıtı yok. (4) ALANLAR bölümü rol adlandırması
  (ID/PWD). (5) Saha: `login` komutu tam olarak bu iki alanı doldurup loginButton'a bastı.
  Kalan sınır: 3. alan bir alt-container'ın içine attr'sız gömülüyse dir(pw) kaçırabilir →
  login ekranı açıldığında `_auto_tick` `_login_param_yapisi`'nı YENİDEN ölçer
  (`login-yapisi: ... (ALT-TIP: TIP1-x)` kesinleştirme satırı) + `uiprobe` tam tarama.
- **"detect liste içeriklerini kontrol ediyor mu?"** → detect VARLIK+ADET verir
  (`serverList_adet:1, channelList_adet:4` saha çıktısında mevcut); İÇERİK dökümü
  `serverlist` komutunun işidir (bölünme bilinçli).
- **"tipi neye göre belirliyor?"** → karar ağacı: KATMAN A board ham bayrağı →
  KATMAN B kaynak/topoloji kanıtı → KATMAN C efektif görünürlük (yalnız yardımcı,
  kurulamazsa -1). TIP2a/b yalnız ayni-board kanıtıyla; TIP1/TIP1n/M1 board bayrağı
  veya kaynak Open() kanıtıyla; kanıt yoksa TIP2x (iki-fazlı adaptif auto).

## 4. Doğrulama

- `scripts/check_py2.py`: lib2to3 PY2 parse + PY3 transpile OK (8 yeni v5.8 işareti).
- `scripts/test_matrix_v58.py` **22/22**: F1-F4 saha vakası (40sn tick-durgunluğu →
  erken zaman aşımı YOK → board dönüşünde login ATILDI), F5 faz-9 başarı, F6
  `LOGIN HATA: LOGIN_FAILURE: WRONGPWD`, F7 timeout board+CONN tanısı, F8 OK-etki
  raporu, F9 selserver doğrulama (pozitif/negatif), F10 TIP1/TIP1-A regresyonu.
- `scripts/test_matrix_v56.py` 18/18, `scripts/test_matrix_v57.py` TAMAM (regresyon).
- `test_tips.py`'nin `_eff_visible` NameError'ı v5.7'de de vardı (eski düzeneğin
  çekim listesi eksik; v5.8'e bağlı DEĞİL).

## 5. Paket

`MaxExecutor_bundle_v2.9.1_matris_v6.2.zip` (20 dosya: v6.1 + FIX-NOTU_v5.8 +
WORKLOG_v5.8). Kurulum: `C:\MaxExec\PLUSMAXGOD_PyScript.py` değiştir (oyun
yeniden açmak en temizi; DLL major-5 kontrolü v5.8'i uyumlu okur).
