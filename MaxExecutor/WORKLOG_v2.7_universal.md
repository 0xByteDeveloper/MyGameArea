# WORKLOG — Oturum 22 (30 Ekim 2026): UNIVERSAL LOGIN/SELSERVER
**MaxExecutor v2.7 + pylib v5.2 — 28-client GitHub araştırmasına dayalı evrensel güncelleme**

> Kullanıcı talebi: *"githubda Metin2 PVP filesleri tara, metin2.dev ve forumlarda tara, sonra tarananları detaylı incele + bilgi sahibi olduktan sonra bu maxexecdeki scripti global evrensel uyumlu yapabiliriz"* — login 2/3 parametre, server listbox/OK-buton/bölge varyasyonları dahil.

---

## 1. SÜREÇ (nasıl yapıldı)

| Aşama | Ne yapıldı | Sonuç |
|---|---|---|
| 1. Bundle analizi | Mevcut v2.6/v5.1 mimarisi: DLL→`maxlib.login(id,pwd)`→pylib UI/paket yolu; login yalnız `idEditLine+pwdEditLine+loginButton` attr'larına bakıyordu | Bağımlılık haritası çıkarıldı |
| 2. Araştırma girişimi | WebSearch/WebFetch kotaları, GitHub API anonim 60/saat limiti, arama motorları (DDG/Bing/Mojeek/SearXNG) bot-duvarı → 2 Task ajanı zaman aşımı | Araştırma bloklandı |
| 3. **Token çözümü** | Kullanıcı GitHub fine-grained PAT verdi (0xByteDeveloper) → core 5000/h + code search 10/dk + WebFetch yenilendi | **Araştırma açıldı** |
| 4. Code Search (token'lı) | `filename:intrologin.py idEditLine` (28 sonuç) + `serverSelectButton` (14) + `REGION_DICT` (16) + `loginwindow.py` (509) + `introselect.py` (33 — bunun karakter-seçimi olduğu netleşti) | Repo aday havuzu |
| 5. Raw indirme | 28 client dump `raw.githubusercontent.com/HEAD/...` ile indirildi (UTF-8 errors=replace) | Tam kanıt seti |
| 6. Otomatik satır analizi | Her dosya: editline/buton/listbox envanteri + def listesi + SetLoginInfo/Connect akışları + 3. alan tespiti | 5 mimari + matris |
| 7. Forum doğrulaması | metin2.dev konu 20529 (Multiple Login Saver System) — 3-parametreli (k.adı:şifre:ID/slot) kayıt yapısı doğrulandı | 3. parametre kanıtı |
| 8. Uygulama | pylib v5.2 universal bloklar + DLL v2.7 komut genişletmesi + pylib_embedded.h yeniden üretim | Bu commit |
| 9. Doğrulama | lib2to3 py2 parse OK (7848 satır) + 11 yeni fonksiyon var + cpp parantez dengesi 262/262 + embed v5.2 boyut | TÜM KONTROLLER GEÇTİ |
| 10. Paketleme | `MaxExecutor_bundle_v2.7_universal.zip` (328 KB, 8 dosya) | download/ + bu repo |

Araştırma sırasındaki araç engelleri ve çözümleri (süreç kanıtı): anonim GitHub API 60/saat → token'la 5000/h; r.jina.ai proxy + Sourcegraph stream → kodlanamadı; **çözüm: GitHub Code Search API + raw fetch (token'lı)** — en verimli yol bu çıktı.

## 2. BULGULAR — 5 LOGIN MİMARİSİ (detay: RESEARCH.md)

| # | Mimari | Kanıt (dump) | Karakteristik |
|---|---|---|---|
| M1 | **Resmi 2014 standart** | 14/28: m2dev-client, Baseline, Lead, battal34(TR), TurkMMO-MS5.8(TR), zaxerrrr 2009... | `idEditLine+pwdEditLine` + `serverList/channelList` listbox + `serverSelectButton` (OK) + `stream.SetLoginInfo/Connect` |
| M2 | **Marty gömülü** | AdmKojuro/Metin2Marty5.3 | Server listesi YOK (g_ip sabit), CH butonları `channelButton` dict, OK YOK, login+CH BİRLEŞİK ekran, F1-F4 slot giriş, guard-code |
| M3 | **Eski/kendi katman** | 0xenia/N2Play-Client | `authSocket.SetLoginInfo`, `info["channel"]`, Türkçe karakter desteği, bot-control yerleşik |
| M4 | **Çoklu-hesap container** | werednnbs/reign2 + merlis | `id_editline_s`/`pwd_editlines` container'lar, `autoLogin(index)`, registry base64 hesaplar |
| M5 | **PIN 3. alan** | TheFara97/proyecto-metin | `pin_edit_line` — login ekranında 3 editline |

**3-parametre (k.adı:şifre:ID) bulgusu:** 3. alanın 4 farklı anlamı var — (1) SAB hesap slotu (Marty: `__LoginDirectly(j)`, TR files'lar: `SAB_*`), (2) PIN (M5), (3) guard-code 2FA (M2), (4) sunucu-ID (metin2.dev 20529). Universal karar (kullanıcı seçimi): **her 3. editline'ı otomatik bul+raporla, verilirse doldur.**

**Server/CH varyasyonları:** listbox'lı (M1) / tek-server (M2) / çoklu-bölge `REGION_DICT[regionID][serverKey]` (16 repo'da) / OK'suz (M2) / butonlu-CH (M2) / birleşik ekran (M2,M3) / container editline (M4) — **HEPSİ v5.2'de destekleniyor.**

**Kritik yan-bulgu:** Ticari source'lar (TMP4/Owsap/martysama/blackdragonx61) GitHub'da kapalı — ama TR files'ların dump'ları (battal34, TurkMMO-MS5.8) resmi 2014 widget adlarını KORUYOR (+SAB ekliyor), yani MaxExecutor'un mevcut attr'ları bu ailelerde de çalışıyor.

## 3. UYGULAMA — pylib v5.2 (PLUSMAXGOD_PyScript.py, 7848 satır)

### Yeni universal yardımcılar
- `_child_by_names(pw, names)` — 3 yollu widget bulma: attr → `GetChild` (uiscript adı) → `dir()` gevsek tarama
- `_scan_editlines(pw)` — TÜM editline'lar (attr + GetChild aday adları: EditLine_ID/EditLine_PWD/pin_editline/guardcode...)
- `_classify_editlines(pw)` — id/pwd/3.alan rol ayrımı (kesin ad → gevsek ad → kalanlar)
- `_set_editline(el, text)` — `SetText` → `SetTextF` → `InsertIntoCurrentLine` yedeği
- `_press_button(btn)` — `CallEvent` → `Event` → `Down` yedeği
- Aday adı sabitleri: `_LOGIN_ID_NAMES/_LOGIN_PWD_NAMES/_LOGIN_BTN_NAMES/_SERVERLIST_NAMES/_CHLIST_NAMES/_REGIONLIST_NAMES/_OKBTN_NAMES`

### Güncellenen komutlar
- **`login(id, pwd, third=None)`** — 3 yol: (A) UI editline+buton (+3.alan doldur) → (B) `pw.Connect(id,pwd)` class metodu (resmi 2014 İLE Marty 5.3'te aynı imza!) → (C) paket: `stream/net.SetLoginInfo` + `ms.Connect()` + `net.ConnectToAccountServer` + 4-arg imza yedeği
- **`selserver(srv, ch, ok=1)`** — (0) regionList çoklu-bölge → (1) serverList+channelList `SelectItem` → (2) Marty `channelButton` dict (ch=0 → ilk buton) + `pw.SetChannel` → (3) OK `CallEvent` (ok=0: basmaz)
- **`serverlist()`** — mevcut listbox dökümüne EK: `serverInfo.REGION_DICT` (bölge/server adları), `channelButton` dict taraması, tek-server tespiti
- **`uiprobe()` YENİ** — login ekranı TAM envanter: class/modül, TÜM editline'lar (rol etiketli + GetText/SetText yetenek), butonlar, listbox'lar (adet+seçili), channelButton dict, LoginWindow metotları, REGION_DICT, **önerilen komut sırası** → `results\last_uiprobe.txt`
- **`relogin(id,pwd,srv,ch,third,ok)` + `reloginquick(slot)` YENİ** — state-machine `_RELOGIN`, `_tick()` (DLL 150ms nabzı) ile sürer: TAM mod `/logout → char ekranı → net.Disconnect → login ekranı → selserver+login`; HIZLI mod `/logout → selchar`. Deadline'lı (15-40sn adım limitleri), `last_relogin_step.txt`/`last_relogin.txt` raporlu
- `_SAVE` login.dat 6. alan: `third` (3. alan kalıcı kayıt)
- Yükleme raporu v5.2 notları

## 4. UYGULAMA — DLL v2.7 (MaxExecutor.cpp, 1927 satır)

- `CmdLogin(id, pwd, third)` — third doluysa `maxlib.login(r'%s', r'%s', r'%s')`
- `CmdSelServer(srv, ch, ok)` — `maxlib.selserver(%d,%d,%d)`
- `CmdUiProbe()` — `maxlib.uiprobe()` YENİ
- `CmdRelogin(nArg, args)` — `relogin` / `relogin <id> <pwd> [srv] [ch]` / `relogin quick [slot]` YENİ
- Dispatch: 4 komut güncel/yeni + kullanım mesajları
- Help: giris akışı bölümü güncel + `GIRIS: status -> uiprobe -> selserver -> login [3.alan] -> ...` + HIZLI YENIDEN GIRIS satırı
- Sürüm dizgileri v2.7/v5.2 (banner, pylib-fail raporu, major guard `_mxv < 5`, ESI uyarısı)
- `pylib_embedded.h` v5.2 (322111 byte) — `scripts/embed_pylib.py` ile üretildi

## 5. DOĞRULAMA (statik — saha testi kullanıcıda)

```
1) pylib v5.2 PY2 PARSE OK (7848 satır, lib2to3)      ✓
2) 11 universal fonksiyon mevcut                       ✓
3) _tick -> _relogin_tick bağlantısı                   ✓
4) cpp v2.7 sembolleri (CmdLogin 3-arg, CmdUiProbe...) ✓
5) cpp parantez dengesi {262/262} ({2050/2050})        ✓
6) pylib_embedded.h v5.2 + boyut 322111                ✓
7) maxlib modül kaydı (globals taraması)               ✓
8) bozuk string kontrolü (apostrof kalıntısı yok)      ✓
```

Saha testi beklentileri (kullanıcı): (1) resmi-listbox sunucuda `selserver 0 0` + `login id pwd` eskisi gibi; (2) tek-server sunucuda `selserver 0 0 0` + `login`; (3) 3-alanlı sunucuda `uiprobe` → alan adını gör → `login id pwd pin`; (4) `relogin` (TAM) ve `relogin quick 0` (HIZLI). Uyarı: paketteki **MaxExecutor.dll v2.6 derlemesi** — 3. parametre/relogin/reloginquick komutları için v2.7 kaynak kodu derlenmeli (Visual Studio, Release/x86); pylib v5.2 eski DLL ile de 2-arg login/selserver çalıştırır (3. argüman yoksayılır).

## 6. BU COMMITTE KOPYALANAN DOSYALAR

```
MaxExecutor/
  PLUSMAXGOD_PyScript.py        <- v5.2 UNIVERSAL (322111 byte)
  MaxExecutor.cpp               <- v2.7 (94220 byte)
  pylib_embedded.h              <- v5.2 embed (1682955 byte)
  RESEARCH.md                   <- YENİ: 28-client araştırma raporu (kaynak linkli)
  KULLANIM.md                   <- v5.2: UNIVERSAL NOT + uiprobe/relogin akışları + sorun giderme
  README.md                     <- v2.7/v5.2 üst özet + DOSYALAR + KULLANIM güncel
  PLUSQuest.md                  <- güncel
  MaxExecutor_bundle_v2.7_universal.zip  <- 328 KB paket (8 dosya)
  research/intrologin/          <- YENİ: 28 client dump kanıtı (araştırma ham verisi)
  research/cs_*.json            <- YENİ: GitHub Code Search API sonuçları (kanıtlar)
  WORKLOG_v2.7_universal.md     <- BU dosya
```

Derlenen binary'ler (MaxExecutor.dll v2.6 / MaxInject.exe) eski sürümdeki haliyle kalır — v2.7 derlemesi kullanıcıda yapılınca güncellenecek.

## 7. SONRAKİ ADIMLAR

1. **DLL v2.7 derlemesi** (kullanıcı): Visual Studio → Release/x86 → MaxExecutor.cpp (pylib_embedded.h projede)
2. **Saha testi 17**: 4 senaryo (§5) — özellikle 3-alanlı sunucu bulup `uiprobe` çıktısı paylaşımı
3. `relogin` davranışı `/logout`'u tanımayan sunucularda deadline'la durur — `last_relogin_step.txt` ile teşhis
4. Sonraki oturumda öneri: `chchange` komutunun universal dönüşü (pylib v5.2 yardımcıları artık faz değişimlerini de güvenle yapabilir)
