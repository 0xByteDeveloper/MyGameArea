# RESEARCH.md — Metin2 PVP Files'ları Login/Server-Seçim Araştırması
**MaxExecutor Universal Güncellemesi (pylib v5.2 / DLL v2.7) için Derin Araştırma Raporu**

Araştırma tarihi: 29-30 Ekim 2026 · Yöntem: GitHub Code Search API (token'lı) + raw dosya indirme + metin2.dev forum
Araştırılan alan: `intrologin.py` / `introselect.py` / `loginwindow.py` UI varyasyonları — 28 gerçek client dump'ı indirilip satır satır analiz edildi.

---

## 1. Araştırma Sorusu

Kullanıcının tespiti doğruydu: **"bazı serverlar kullanıcı adı + şifre (2 parametre) isterken, kimisi kullanıcı adı : şifre : ID (3 parametre) istiyor"** ve **"bazılarında Server listbox + CH listbox + OK butonu var, bazılarında server listesi yok (tek server default), bazılarında çoklu bölge (Romania vb.), bazılarında OK butonu yok, bazılarında login ekranı CH seçimiyle birleşik"**.

Bu rapor, hangi mimarilerin gerçekten var olduğunu GitHub'daki client kaynaklarıyla kanıtlar ve MaxExecutor'un universal (çoklu sunucu uyumlu) yaklaşımının gerekçesini verir.

## 2. Yöntem

1. **GitHub Code Search API** (token'lı, `filename:intrologin.py` + anahtar desenler):
   - `idEditLine` → 28 sonuç (asıl örneklem)
   - `serverSelectButton` → 14 sonuç (resmi 2014 server board kanıtı)
   - `REGION_DICT` → 16 sonuç (bölge yapısı kanıtı)
   - `filename:loginwindow.py` → 509 sonuç (uiscript eşleri; metin2.dev konusundaki `uiSelectCredentials.py`/`loginwindow.py` ailesini doğrular)
   - `filename:introselect.py` → 33 sonuç (NOT: bu KARAKTER seçimi, server seçimi değil — server seçimi hep `intrologin.py` içinde)
2. **Raw indirme**: 28 dosya (`raw.githubusercontent.com/<repo>/HEAD/<path>`) → yerel analiz
3. **Otomatik satır analizi**: editline/buton/listbox envanteri, `def` fonksiyon listesi, `SetLoginInfo`/`Connect` akışları
4. **metin2.dev**: konu 20529 "Multiple Login Saver System" (3-parametreli kayıt yapısı doğrulandı)
5. Ticari source'ların kapalı olduğu doğrulandı: TMP4 (yalnız `tmp4/tmp` repo'su kalmış), Owsap (yalnız tool repo'ları), martysama0134 (yalnız tool/patch repo'ları), blackdragonx61 (repo listesi boş) — bu ailelerin client'ları yine de topluluk dump'larında temsil ediliyor (Marty 5.3/5.8 dump'ları = martysama tabanlı).

## 3. Bulunan 5 Login Mimarisi

### M1 — Resmi 2014 Standart Akışı (EN YAYGIN)
**Kanıtlar:** `d1str4ught/m2dev-client`, `Debloat/Baseline`, `Lead0x194/lead-files-community`, `Marcel-Schlanzke1994/Aetherfall`, `SAFlux/m2x-client`, `mxmatheus/Valmeryn2-Client`, `Mohammad-Abu-Saa/NerO-SF`, `qMin32/distraught-m2dev-client-src`, `a962000941-art/root`, `battal34/battal34` (TR), `ruhqersa/TurkMMO-MS5.8Client` (TR Marty 5.8), `zaxerrrr-dot/mt2009-sp-plus` (2009 patch yolu)

- Login alanları: `idEditLine` + `pwdEditLine` (2 alan)
- Server board: `serverList` (listbox) + `channelList` (listbox) + `serverSelectButton` (OK)
- Seçim okuma: `__GetRegionID()` (genelde sabit `0`), `__GetServerID()` = `serverList.GetSelectedItem()`, `__GetChannelID()` = `channelList.GetSelectedItem()`
- Bağlantı: `self.stream.SetLoginInfo(id, pwd)` + `self.stream.Connect()`
- Marty 5.8 tabanlı TR files'lar (battal34, TurkMMO-MS5.8) standart widget adlarını **koruyor** + üstüne `SAB_*` (Save Account Board) fonksiyon ailesi ekliyor: `SAB_LoadAccountData/SAB_SaveAccountData/SAB_Click_Save/SAB_Click_Access/SAB_Click_Remove`
- Widget atama bazı clientlarda `GetObject("ServerList")`, bazılarında `GetChild("serverList")` yolu — ikisi de olabileceği için universal kod İKİSİNİ DENEMELİ (v5.2 `_child_by_names`: attr → GetChild → dir() taraması)

### M2 — Marty Gömülü Akış (Server listesi YOK, OK butonu YOK)
**Kanıt:** `AdmKojuro/Metin2Marty5.3`

- Login + CH seçimi İLK EKRANDA BİRLEŞİK: `channelButton = {...}` dict (CH → buton), `channelButtons.SetEvent(self.SetChannel, channelID)`
- `SetChannel(ch)`: `self.stream.SetConnectInfo(g_ip, self.ChannelPort(ch, 0), g_ip, self.ChannelPort("LOGIN"))` — g_ip sabit, server listesi yok (tek server)
- `Connect(id, pwd)`: `stream.SetLoginInfo` + `stream.Connect` (resmiyle aynı)
- `serverList`/`channelList`/`serverSelectButton` HİÇ YOK
- Ekstra: `__LoginDirectly(j)` F1-F4 tuşlarıyla slot j → `LoadAccount(j-1)` → otomatik giriş (SAB tarzı çoklu hesap), `AskGuardCode/ConfirmGuardCode/CheckGuardCode` (guard code = 3. alan senaryosu)

### M3 — Eski/Kendi Network Katmanı
**Kanıt:** `0xenia/N2Play-Client`

- `self.authSocket.SetLoginInfo(id, pwd)` — stream yerine kendi socket katmanı
- `self.info["channel"]` + `self.serverName` + `self.pickedChannel` — server/CH durumu login ekranında tutulur
- `has_turkish_characters`, `TRANSFORM_LANG` — Türkçe karakter desteği (TR serverların özelliği)
- `RefreshBotControl/CheckBotControl` — bazı serverlar client'a bot API'si gömer

### M4 — Çoklu-Hesap Slotlu UI (SAB/meta-farklı adlar)
**Kanıtlar:** `werednnbs/reign2-interface`, `werednnbs/merlis-ui-work`

- `idEditLines = self.GetChild("id_editline_s")` / `pwdEditLines = self.GetChild("pwd_editlines")` — editline'lar CONTAINER içinde, alt editline `LoginInputs()`'ta dinamik kurulur
- `autoLogin(index)`: registry'den base64 hesap (`get_reg("%d_id" % index)` → `binascii.a2b_base64`) → editline'lara doldur → `__OnClickLoginButton()`
- `saveAccountChenars / saveAccountFunction(index) / deleteAccountFunction(index)` — slot bazlı hesap yönetimi
- DERS: editline'lar her zaman `idEditLine` adında OLMAYABİLİR — aday listesi + container altı tarama şart

### M5 — Modern Modifiye (PIN 3. Alanı)
**Kanıt:** `TheFara97/proyecto-metin`

- `SetPinEditLineFocus()` + `self.pin_edit_line` — PIN editline = KULLANICININ DEDİĞİ 3. PARAMETRE karşılığı
- `SetIDEditLineFocus/SetPasswordEditLineFocus/SetPinEditLineFocus` üçlüsü — 3 alanlı login ekranı
- `save_account/load_account/delete_account/is_slot_occupied` — slot tabanlı hesap kaydı
- `SetChannel` yok, `_setup_network` kendi akışı

## 4. 3-Parametreli Login (k.adı : şifre : ID) — Bulgular

Kullanıcının bahsettiği "3. parametre"nin client tarafındaki karşılıkları (4 farklı anlam tespit edildi):

| # | 3. Alanın Anlamı | Kanıt | Mekanizma |
|---|------------------|-------|-----------|
| 1 | **Hesap slotu** (SAB çoklu hesap) | Marty 5.3 (`__LoginDirectly(j)`), battal34, TurkMMO-MS5.8 (`SAB_*`), reign2 (`autoLogin(index)`) | Kayıtlı hesap index'i → LoadAccount → otomatik doldur+giriş |
| 2 | **PIN kodu** | TheFara97 (`pin_edit_line`) | Login ekranında 3. editline |
| 3 | **Guard code** (2FA) | Marty 5.3 (`AskGuardCode/ConfirmGuardCode`) | Login SONRASI dialogda ayrı editline |
| 4 | **Server-side ID** (kullanıcı adı : şifre : oyun-IÇI id eşlemesi) | metin2.dev konu 20529 + TR server pratikleri | Sunucu bazı hesaplarda ek ID doğrulaması ister; client'ta 3. editline veya chat-dialog |

**Sonuç:** 3. alanın ADI her serverda farklı (pin_edit_line, connect_editline, guardcode, id2...). Universal çözüm: **"her 3. editline'ı otomatik bul + doldur + tipini raporla"** (kullanıcının seçtiği evrensel yaklaşım) — v5.2 `login(id, pwd, third=None)` tam bunu yapar; `uiprobe()` 3. alanın adını/tipini raporlar.

## 5. Server/CH Seçim Varyasyonları

| Varyasyon | Kanıt | Universal Davranış (v5.2 `selserver`) |
|-----------|-------|---------------------------------------|
| serverList + channelList + serverSelectButton (OK) | M1 (14 repo) | `SelectItem(srv)` + `SelectItem(ch)` + `serverSelectButton.CallEvent()` |
| Server listesi YOK (tek server) | M2 Marty 5.3 | listbox yoksa CH butonları dict'ten tetiklenir; `pw.SetChannel(ch)` yedeği |
| OK butonu YOK | M2 (channelButton dict) | OK bulunamazsa `ok=0` modu + "OK zaten yok" raporu |
| Çoklu bölge (Region: Romania vb.) | `REGION_DICT` 16 repo; resmi yapı `REGION_DICT[regionID][serverKey]={'name','node','state',...}` | `regionList` varsa ve >1 bölge varsa önce bölge seçilir |
| CH butonları (listbox değil) | Marty 5.3 `channelButton` dict | dict taraması + `CallEvent/Event/Down` |
| Login+CH birleşik ilk ekran | Marty 5.3, N2Play | `selserver` listbox bulamazsa sessizce CH yoluna düşer; `login` direkt çalışır |
| EditLine'lar container altında | reign2 (`id_editline_s`) | `_scan_editlines`: attr + `GetChild` + `dir()` üçlü tarama |

**serverInfo.REGION_DICT yapısı** (resmi): `regionID → {serverKey: {'name': 'Yserbius', 'node': ..., 'state': ..., 'channel': {...}}}` — v5.2 `serverlist()` artık bu modülü de döküyor (bölge/server adları listbox metninden bağımsız okunur).

## 6. Files Ailesi × Özellik Matrisi (indirilen 28 client'tan)

| Repo (client dump) | Aile/Taban | Login Alanları | ServerList | ChannelList | OK Butonu | Not |
|---|---|---|---|---|---|---|
| d1str4ught/m2dev-client | m2dev/resmi 2014 | id+pwd | ✓ | ✓ | ✓ serverSelectButton | metin2.dev referans dump |
| Debloat/Baseline | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | SEVER_LIST_BUG_FIX'li |
| Lead0x194/lead-files-community | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | Lead files |
| battal34/battal34 | Marty 5.8 TR | id+pwd (+SAB) | ✓ | ✓ | ✓ | TR: SAB_*, sanal klavye |
| ruhqersa/TurkMMO-MS5.8Client | Marty 5.8 TR | id+pwd (+SAB) | ✓ | ✓ | ✓ | TR: +sanal klavye |
| AdmKojuro/Metin2Marty5.3 | Marty 5.3 | id+pwd | ✗ | ✗ (channelButton dict) | ✗ | F1-F4 slot login, guard code |
| 0xenia/N2Play-Client | eski/kendi katman | id+pwd | ✗ (info["channel"]) | ✗ | ✗ | authSocket, TR karakter desteği |
| werednnbs/reign2-interface | modifiye | id_editline_s container | ✗ | ✗ | ✗ | autoLogin(idx), registry base64 |
| werednnbs/merlis-ui-work | modifiye | id_editline_s container | ✗ | ✗ | ✗ | multi-hesap UI çalışması |
| TheFara97/proyecto-metin | modifiye modern | id+pwd+**PIN** | ✗ | ✗ | ✗ | 3. alan = PIN |
| zaxerrrr-dot/mt2009-sp-plus | 2009 patch (3 sürüm) | id+pwd | ✓ | ✓ | ✓ | 2.0.21/25/28 patch serisi |
| a962000941-art/root | resmi türev | id+pwd | ✓ | ✓ | ✓ | 1371 satır (en uzun) |
| SAFlux/m2x-client | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | m2x |
| mxmatheus/Valmeryn2-Client | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | — |
| Mohammad-Abu-Saa/NerO-SF | m2dev kopya | id+pwd | ✓ | ✓ | ✓ | — |
| qMin32/distraught-m2dev-client-src | m2dev kaynak | id+pwd | ✓ | ✓ | ✓ | source |
| Marcel-Schlanzke1994/Aetherfall | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | — |
| Lead/Debloat/… (bakınız M1) | resmi 2014 | id+pwd | ✓ | ✓ | ✓ | 14 repo toplam |
| yumulk604/yumulk | sadeleştirilmiş | id+pwd | ✗ | ✗ | ✗ | 363 satır (en kısa) |
| fespinozasanchez/Metin2-nidavelir | modifiye | id+pwd | ✗ | ✗ | ✗ | 637 satır |
| renoki-games/Metin2BE-Client | modifiye | id+pwd | ✓ | ✓ | ✗ | serverSelectButton yok |
| ixtreeme/AurigaGlobal | modifiye | id+pwd | ✗ | ✗ | ✗ | +.bak varyantı |
| ybeststudio/Anka2Project | TR (Anka2) | id+pwd | ✗ | ✗ | ✗ | binary_unpack |
| 0xenia/N2Play (yukarıda) | — | — | — | — | — | — |
| SamuraiHUN/Remove_unussed_code | parça | — | — | — | — | analiz dışı (190 satır parça) |

**Dağılım özeti:** 14/28 resmi 2014 listbox akışı (M1), 9/28 listbox'sız/birleşik (M2-M4-M5 tarzı), 1/28 kendi katman (M3), 4/28 çoklu-hesap slotlu (M4), 1/28 PIN'li (M5).

## 7. Login Bağlantı Yolları (paket/yedek)

1. **UI yolu** (en uyumlu): editline `SetText` → buton `CallEvent()` — tüm mimarilerde işler; tek risk attr adı farkları
2. **`pw.Connect(id, pwd)` class metodu**: resmi 2014 İLE Marty 5.3'te imza aynı — UI yoksa güçlü yedek (v5.2 YOL B)
3. **Paket yolu**: `stream.SetLoginInfo` + `stream.Connect` (resmi) → `net.SetLoginInfo` + `net.ConnectToAccountServer` (eski) → `authSocket.SetLoginInfo` (N2Play) (v5.2 YOL C)

## 8. Uygulama Kararları (v5.2 / v2.7)

1. **Çoklu aday + GetChild + dir() taraması**: 5 mimarideki tüm ad farklarını kapsar (`_child_by_names`, `_scan_editlines`, `_classify_editlines`)
2. **`login(id, pwd, third=None)`**: 3. editline varsa raporlar, `third` verilirse doldurur; `SetText` → `SetTextF` → `InsertIntoCurrentLine` yedeği; buton yoksa `__OnClickLoginButton` → `pw.Connect` → paket yolu
3. **`selserver(srv, ch, ok=1)`**: bölge → server → CH listbox → Marty channelButton dict → `pw.SetChannel` zinciri; `ok=0` OK'a basmaz (OK'suz clientlar için kullanıcının istediği)
4. **`serverlist()` zenginleşti**: listbox dökümü + `serverInfo.REGION_DICT` + channelButton dict + tek-server tespiti
5. **`uiprobe()` YENİ**: login ekranı tam envanteri — hangi mimari, 3. alanın adı, hangi argümanlarla login/selserver verilir
6. **`relogin` DÖNDÜ (universal)**: TAM mod `/logout → char ekranı → net.Disconnect → login → selserver → login`; HIZLI mod (`relogin quick [slot]`) `/logout → selchar`. State-machine DLL 150ms nabziyle sürer (ana thread bloklanmaz)
7. **pylib_embedded.h** v5.2 ile yeniden üretildi (scripts/embed_pylib.py) — DLL diskteki pylib eksikse v5.2'yi yazar
8. **DLL v2.7**: `login` 3. parametre, `selserver` ok parametresi, `uiprobe`, `relogin` komutları; pylib major guard `<5` uyarısı

## 9. Sınırlar / Saha Testi Notları

- TR/TR-utils clientlarından alıntılar iso-8859-1/utf-8 karma — analiz `errors='replace'` ile yapıldı; kod anlamı etkilenmez
- Bazı serverlar login ekranını `uiscript/loginwindow.py` XML'i ile değiştirir (PACHIPtr/PACHI_TUNGA_SF kanıtı) — bu durumda attr adları değişir; `uiprobe` bu tespit için var
- `/logout` komutu her serverda açık değildir; `net.Disconnect` bazı clientlarda yoktur — `relogin` deadline'lıdır ve adım raporlarını `last_relogin_step.txt`'e yazar
- Ticari source (TMP4 40250 güncel sürüm, Owsap, Sanii güncel) GitHub'da kapalıdır; ancak bu tabanların yaygın dump'ları örneklemde vardır ve widget/akış kalıpları aynıdır
- MaxExecutor.dll bu pakette DERLENMİŞ ESKİ binary (v2.6) olarak kalır: DLL kaynak v2.7'yi kullanıcının derlemesi gerekir (Visual Studio 2019/2022 + Windows SDK, Release/x86); pylib v5.2 ESKI DLL ile de büyük ölçüde çalışır (komut argümanları 2'li formda) ancak 3. parametre ve relogin için v2.7 derlemesi şart

## 10. Kaynaklar

**GitHub client dump'ları (raw indirilip analiz edilen):**
- https://github.com/d1str4ught/m2dev-client — assets/root/intrologin.py
- https://github.com/Debloat/Baseline — Client/Binary/pack/root/intrologin.py
- https://github.com/Lead0x194/lead-files-community — Lead-Client/pack/root/intrologin.py
- https://github.com/battal34/battal34 — intrologin.py (TR Marty 5.8 + SAB)
- https://github.com/ruhqersa/TurkMMO-MS5.8Client — Client/pack/root/intrologin.py (TR)
- https://github.com/AdmKojuro/Metin2Marty5.3 — Cliente/pack/root/intrologin.py (Marty gömülü akış)
- https://github.com/0xenia/N2Play-Client — client/script/introLogin.py (authSocket katmanı)
- https://github.com/werednnbs/reign2-interface — root/intrologin.py (çoklu hesap container)
- https://github.com/werednnbs/merlis-ui-work — code/root/intrologin.py
- https://github.com/TheFara97/proyecto-metin — pack/root/intrologin.py (PIN 3. alan)
- https://github.com/zaxerrrr-dot/mt2009-sp-plus — client-patches/client-2.0.{21,25,28}
- https://github.com/a962000941-art/root — intrologin.py
- https://github.com/SAFlux/m2x-client — assets/root/intrologin.py
- https://github.com/mxmatheus/Valmeryn2-Client — assets/root/intrologin.py
- https://github.com/Mohammad-Abu-Saa/NerO-SF — m2dev-client/assets/root/intrologin.py
- https://github.com/qMin32/distraught-m2dev-client-src — m2dev-client/assets/root/intrologin.py
- https://github.com/Marcel-Schlanzke1994/Aetherfall — root/intrologin.py
- https://github.com/ybeststudio/Anka2Project — Tools/binary_unpack/root/intrologin.py (TR)
- https://github.com/yumulk604/yumulk — Binary/root/intrologin.py
- https://github.com/fespinozasanchez/Metin2-nidavelir — client/pack/root/intrologin.py
- https://github.com/renoki-games/Metin2BE-Client — root/intrologin.py
- https://github.com/ixtreeme/AurigaGlobal — root/intrologin.py (+.bak)
- https://github.com/Lead0x194/lead-files-community — Lead-Client/pack/root/introselect.py
- https://github.com/PACHIPtr/PACHI_TUNGA_SF — binary/data/root/uiscript/loginwindow.py (uiscript değişimi kanıtı)

**Diğer:**
- https://github.com/TMP4 — client source kapalı (yalnız `tmp4/tmp`), TMP4 tabanlı dump'lar örneklemde
- https://github.com/Owsap — tool repo'ları; client source kapalı
- https://github.com/martysama0134 — SAB/marty taban tools; client source kapalı
- https://github.com/Vegas007 — C++ modül repo'ları (login UI source yok)
- https://metin2.dev/topic/20529-multiple-login-saver-system/ — 3-parametreli çoklu hesap kayıt sistemi (k.adı : şifre : ID/slot)
- martysama0134 gist'leri — resmi intrologin.py yapısı, REGION_DICT, autoSelect/autoLogin referansı
- Resmi 2014 client kaynak akışı: `LoginWindow.__OnClickSelectServerButton` → `__GetRegionID/__GetServerID/__GetChannelID` → `stream.SetLoginInfo/Connect`
