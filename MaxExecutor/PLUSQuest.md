# PLUSQuest — Metin2 İstemci Python Fonksiyon Kataloğu
### (PLUSMAXGOD Edition · v4.0 · Oturum 13)

> **Bu dosya nedir?** MaxExecutor'un oyunun Python'undan erişebildiği **tüm bilinen modül ve
> fonksiyonların** kataloğudur: ne işe yararlar, hangileri bu istemcide **kanıtlı** (saha
> kanıtlı kullanım), ne yapmak için **birlikte** kullanılabilirler. Artı "eski AI sohbetindeki"
> doğruların/yanlışların GOD MOD hükmüyle kesinleştirilmiş hali.
>
> **Kanıt işaretleri:**
> - **[K]** = KANITLI — nighttown koleksiyonunda (4000+ kullanım, kullanıcının ekosistemi)
>   veya cycu.py'de birebir bu istemcide çağrılmış. Riski sıfıra yakın.
> - **[S]** = STANDART — resmî Metin2 istemci Python API'sinde var, bu istemcide büyük
>   olasılıkla çalışır; ilk kullanımda tek seferlik doğrula.
> - **[?]** = BELİRSİZ — sunucu/istemciye bağlı; `pyscan <modul>` ile istemcinde var mı bak.
>
> **Canlı güncelleme döngüsü:** oyun içinde `plusquest` yaz → `C:\MaxExec\dump\PLUSQuest_live.txt`
> oluşur (istemcinin ŞU AN yüklü modülleri + fonksiyonları) → o dosyayı AI'ya gönder → bu
> katalog senin istemcinin gerçek envanteriyle zenginleşir. `pydumpall` ile pack'in içindeki
> tüm .py kaynakları da `C:\MaxExec\dump`'a dökülür (INDEX.txt ile) — aynı şekilde gönderilir.

---

## 0. HIZLI ERİŞİM TABLOSU (hangi komut hangi fonksiyonu kullanıyor?)

| MaxExecutor komutu | Kullandığı çekirdek fonksiyon(lar) | Kanıt |
|---|---|---|
| `stat` | `player.GetStatus(LEVEL/HP/MAX_HP/SP/MAX_SP/EXP/NEXT_EXP/MOVING_SPEED)`, `net.GetMainActorRace`, `net.GetMainActorSkillGroup`, `net.GetEmpireID`, `player.GetName`, `player.IsMountingHorse` | [K] cycu |
| `pos` | `chr.GetPixelPosition(vid)`, `net.GetMainActorVID`, `background.GetCurrentMapName`, `player.GetMainCharacterPosition` (yedek) | [K] cycu + 34 kullanım |
| `inv` / `equip` | `player.GetItemIndex`, `player.GetItemCount`, `player.INVENTORY_PAGE_SIZE`, `player.EQUIPMENT_BASE_INDEX`, `item.SelectItem`, `item.GetItemName` | [K] 267/100/147/300/171 |
| `skill` | `player.GetSkillIndex?`, `player.GetSkillLevel`, `player.GetSkillGrade`, `player.IsSkillCoolTime`, `skill.GetSkillName` | [K] 24/24/19/15 |
| `near` | VID sweep `chr.GetPixelPosition(vid)` ×2000, `chr.GetInstanceType`, `chr.GetNameByVID`, `nonplayer.GetLevelByVID` | [K] 57/52/6 |
| `chat` / `cmd` | `net.SendChatPacket` | [K] cycu + 117 |
| `whisper` | `net.SendWhisperPacket` | [K] 9 |
| `ride` | `net.SendChatPacket('/ride')` | [K] cycu |
| `revive` | `chr.Revive()` | [K] cycu + 22 |
| `logout` / `back` | `net.SendChatPacket('/logout' / '/phase_select')` | [K] cycu |
| `zoom` | `app.SetCameraMaxDistance` | [K] cycu + 13 |
| `use` | `net.SendItemUsePacket(slot)` | [K] 218 (!) |
| `pickup` | `player.PickCloseItem` | [K] 15 |
| `drop` | `net.SendItemDropPacketNew(slot, adet)` | [K] cycu + 19 |
| `goto` | `chr.MoveToDestPosition(vid, x, y)` | [K] 36 |
| `tp` | `chr.SetPixelPosition(x, y)` | [K] 211 (!) |
| `key` | `player.SetSingleDIKKeyState(app.DIK_x, TRUE/FALSE)` | [K] 368 (!) |
| `attack` | `player.SetAttackKeyState(TRUE/FALSE)` | [K] 100 |
| `pyfiles` | `app.GetFileList` [?] + `sys.modules` + `pkgutil` + `os.listdir` + import-probe | karışık |
| `pydump` / `pydumpall` | `app.OpenTextFile` + `app.GetTextFileLineCount` + `app.GetTextFileLine` | [K] cycu + 24 |
| `pyscan` / `plusquest` | `sys.modules` + `dir()` + `func_code.co_varnames` | [S] py2 çekirdeği |

---

## 1. KEŞİF YÖNTEMLERİ — eski AI'nin doğruları / yanlışları (GOD MOD hükmü)

Eski sohbetteki AI 5 yöntem saymıştı. İşte kesin hükümler:

| Yöntem | Hüküm | Açıklama |
|---|---|---|
| `app.GetFileList("*.py")` | **[?] YANLIŞ vaat** — eski AI "en iyi yöntem" dedi ama nighttown koleksiyonunda **0 kullanım** → bu istemcide büyük olasılıkla YOK. `pyfiles` komutu yine de dener; yoksa not düşer. | Varsa bedava dosya listesi verir. |
| `app.OpenTextFile` + `GetTextFileLineCount` + `GetTextFileLine` | **[K] GERÇEK OKUMA YOLU** — cycu.py bu üçlüyle `intrologin.py`'i okuyor; sen `serverinfo.py` okumayı doğruladın; nighttown'da 24 kullanım. **Şifreli pack'ten bile okur** (oyun pack'i kendi çözer). `pydump`/`pydumpall` tam buna kurulu. | Asıl yöntem bu. |
| `sys.modules` | **[K] DOĞRU** — yüklü tüm modüllerin adlarını verir. Bedava, risksiz. `plusquest` bunun üstüne `dir()` ile fonksiyonları da çıkarır. | Menüde az, oyunda çok modül görünür → `plusquest`'i **oyundayken** çalıştır. |
| `pkgutil.iter_modules()` | **[?] ZAYIF** — gömülü interpreter'ın importer'ı desteklemeyebilir. Denemesi bedava; sonuç raporda not olarak düşer. | Beklenti düşük tut. |
| `os.listdir()` | **[K-koşullu] DOĞRU ama farklı amaçla** — root pack şifrelis DISKTE .py yoksa pack dosyalarını bulamaz; AMA **client klasörünü** (senin deyiminle: nighttown workspace'te, değilse temp/tmp'te) tarayarak script/modül koleksiyonlarını (m2kmod, Modules/, scripts_root/...) yakalar. `pyfiles` cwd + sys.path + TEMP/TMP tarar. | Koleksiyon taraması için altın. |

**Özet yargı:** dosya *listesi* için `sys.modules` + disk taraması + import-probe; dosya *içeriği*
için her durumda `app.OpenTextFile` üçlüsü. `pyfiles` hepsini tek raporda birleştirir.

---

## 2. MODÜL KATALOĞU

### 2.1 `app` — istemci çekirdeği (uygulama, kamera, dosya, tuş sabitleri)

| Fonksiyon | Ne yapar | Kanıt |
|---|---|---|
| `app.OpenTextFile(ad)` | Pack'ten (şifreli olsa bile) metin dosyası açar, handle döner. | [K] |
| `app.GetTextFileLineCount(h)` | Açık dosyanın satır sayısı. | [K] |
| `app.GetTextFileLine(h, i)` | i. satırı string olarak verir. | [K] |
| `app.GetFileList("*.py")` | (Varsa) pack içi dosya listesi. | [?] |
| `app.SetCameraMaxDistance(n)` | Kamera menzili (cycu: 12000). | [K] |
| `app.GetCameraRotation()` / `app.RotateCamera(a)` | Kamera açısı oku / döndür. | [K] |
| `app.IsPressed(DIK_x)` | Tuş basılı mı? (bot döngülerinde şart kontrolü) | [K] 28 |
| `app.DIK_UP/DOWN/LEFT/RIGHT/SPACE/LSHIFT/F5/W/A/S/D/B` | DirectInput tuş sabitleri (`key` komutu bunları çözer). | [K] |
| `app.GetTime()` / `app.GetGlobalTimeStamp()` | Oyun içi zaman (döngü zamanlayıcıları için). | [K] 141 |
| `app.GetRandom(a, b)` | Rastgele sayı (rastgele hedef/karar için). | [K] 30 |
| `app.SetMinFog(...)` | Sis ayarı (nofog görünürlük hilesi). | [K] 11 |
| `app.GetLocalePath()` | Dil/locale yolu (dosya yolları için). | [K] 13 |
| `app.Abort()` / `app.Exit()` | İstemciyi kapatır. **Tehlikeli** — bot döngüsünde yanlışlıkla çağırma. | [K] |
| `app.Shop(...)` | Shop açma çağrısı (pencere katmanı). | [K] 14 |

**Birlikte:** `key UP 1` + `app.IsPressed(app.DIK_LSHIFT)` + `attack 1` → koşarak-toplu saldırı;
`app.OpenTextFile` üçlüsü + `pydump` → pack okuma motoru.

---

### 2.2 `net` — ağ/oturum katmanı (paket göndericiler)

| Fonksiyon | Ne yapar | Kanıt |
|---|---|---|
| `net.SendChatPacket(s)` | Sohbet paketi. `"/"` ile başlarsa OYUN KOMUTU'dur (`/ride`, `/logout`, `/phase_select`, `/stat`...). Tüm slash komutları kapısı. | [K] 117 + cycu |
| `net.SendWhisperPacket(kim, mesaj)` | Özel mesaj. | [K] 9 |
| `net.SendItemUsePacket(slot)` | Envanter slotundaki eşyayı kullanır (potion/kiyafet/taş...). **218 kullanım — en çok kullanılan paket.** | [K] |
| `net.SendItemDropPacketNew(slot, adet)` | Eşyayı yere bırakır. **DESTRÜKTİF.** | [K] cycu + 19 |
| `net.SendItemPickUpPacket(vid)` | Yerdeki eşyayı alır. | [K] 12 |
| `net.SendItemUseToItemPacket(...)` | Eşyayı eşyaya kullan (taş ekleme vb.). | [K] 19 |
| `net.SendShopBuyPacket` / `SendShopSellPacket` / `SendShopEndPacket` | NPC dükkân al/sat/kapat. | [K] 58/16/7 |
| `net.SendRefinePacket(slot, tip)` | Geliştirme (up) paketi. **Riskli + malzeme yer.** | [K] 36 |
| `net.SendGoldDropPacketNew(...)` | Yang bırakma. | [K] 5 |
| `net.SendGiveItemPacket(...)` | Eşya verme (pazar/oyuncu). | [K] 7 |
| `net.SendSelectCharacterPacket(slot)` | Karakter seçim paketi (paket yolu giriş). | [K] 5 |
| `net.SendEnterGamePacket()` | Oyuna gir paketi (SelectSlot sonrası zincirin son halkası). | [K] 4 |
| `net.DirectEnter(slot)` | Doğrudan giriş — **YENİ karakterde sunucu reddediyor (saha kanıtı oturum 12)**; UI START yolu önce. | [K] ama kısıtlı |
| `net.SetLoginInfo(id, pwd)` + `net.SetPacketSequenceMode()` + `net.ConnectToAccountServer(...)` | Paket-yolu giriş üçlüsü (cycu DirectConnect deseni). | [K] 6/3/6 |
| `net.SendSelectEmpirePacket(n)` | Bayrak seçim paketi (empireui'nin YEDEK yolu). | [K] |
| `net.SendCreateCharacterPacket(slot, ad, race, shape, ...)` | Karakter oluşturma paketi — **yalnız buton bulunamazsa** (çift paket = sahte CREATE_FAILURE, oturum 12 kanıtı). | [K] |
| `net.SendOnClickPacket(vid)` | NPC'ye tıkla paketi (dialog açma). | [K] 5 |
| `net.SendQuestInputStringPacket(s)` | Quest giriş kutusuna string gönderir (otomasyon için değerli!). | [K] 5 |
| `net.SendGuildOfferPacket(...)` | Lonca işlemleri. | [K] 5 |
| `net.GetMainActorVID()` | Kendi karakterinin VID'si. | [K] cycu |
| `net.GetMainActorRace()` / `net.GetMainActorSkillGroup()` | Irak / beceri grubu. | [K] cycu 13/13 |
| `net.GetEmpireID()` | Hesabın bayrağı (1/2/3). | [K] |
| `net.IsConnect()` | Bağlantı durumu (`status` bunu raporlar). | [K] |
| `net.SetServerInfo(ad)` | Sunucu adı etiketi (görsel). | [K] 8 |
| `net.LogOutGame()` | Oyun oturumunu kapatır. | [K] 6 |

**Birlikte:** `near` → hedef vid → `net.SendOnClickPacket(vid)` → NPC dialog; `inv` → slot →
`net.SendItemUsePacket(slot)`; quest botu: quest giriş kutusu → `SendQuestInputStringPacket`.

---

### 2.3 `player` — oyuncu durumu ve eylemleri (EN ZENGİN modül)

| Fonksiyon / sabit | Ne yapar | Kanıt |
|---|---|---|
| `player.GetStatus(player.X)` | `X ∈ LEVEL, HP, MAX_HP, SP, MAX_SP, EXP, NEXT_EXP, MOVING_SPEED` (cycu: HP%/SP%/EXP% hesapları bu üçlüyle). | [K] 187 |
| `player.GetName()` | Karakter adı. | [K] cycu |
| `player.GetMainCharacterIndex()` | Ana karakterin instance index'i (= VID'si; `goto` bunu kullanır). | [K] 73 |
| `player.GetMainCharacterPosition()` | Ana karakter pozisyonu (`pos` yedeği). | [K] 168 |
| `player.GetItemIndex(slot)` | Slottaki eşya vnum'u (0 = boş). Envanter okumanın çekirdeği. | [K] 267 |
| `player.GetItemCount(slot)` / `GetItemCountByVnum(vnum)` | Slottaki adet / vnum'un toplam adedi. | [K] 44/46 |
| `player.GetItemAttribute(slot, i)` / `SetItemAttribute` | Eşya bonuslarını oku/yaz (efsun botu ham maddesi). | [K] 34/16 |
| `player.GetItemMetinSocket(slot, i)` | Taş yuvalarını okur. | [K] 19 |
| `player.INVENTORY_PAGE_SIZE` | Sayfa boyutu (45) — `inv` komutu bundan okur. | [K] 147 |
| `player.EQUIPMENT_BASE_INDEX` | Ekipman slotlarının başlangıcı (≈90) — `equip` bunu kullanır. | [S] |
| `player.SetSingleDIKKeyState(DIK, 1/0)` | **Sanal tuş basışı** — 368 kullanım! Gerçek klavye simülasyonu (kayak, dialog seçimleri). | [K] |
| `player.SetAttackKeyState(1/0)` | Saldırı tuşunu basılı tut/bırak — 100 kullanım. | [K] |
| `player.ClickSkillSlot(slot)` | Skill bar slotuna tıkla (cycu saldırı rotasyonu). | [K] 68 |
| `player.IsSkillCoolTime(slot)` | Slot beklemede mi (cycu: rotasyon şartı). | [K] 19 |
| `player.GetSkillLevel(idx)` / `GetSkillGrade(idx)` | Beceri seviyesi/grad (oyun 0 dönerse öğrenilmemiş — `skill` komutunun tarama şartı). | [K] 24/24 |
| `player.SetTarget(vid)` / `player.GetTargetVID()` | Hedefle / hedefi oku (otomatik avın kalbi). | [K] 17/26 |
| `player.GetCharacterDistance(a, b)` | İki instance arası mesafe (yaklaşma şartı). | [K] 37 |
| `player.IsMountingHorse()` | Atlı mı (cycu: skill atmadan inme/çık deseni). | [K] 42 |
| `player.PickCloseItem()` | En yakın yerdeki eşyayı al. | [K] 15 |
| `player.RequestUseLocalQuickSlot(idx)` | Quickslot kullan. | [K] 16 |
| `player.SetItemAttribute(...)` | Bonus yaz (istemci tarafı görüş + paket yolları ayrı — dikkat). | [K] 16 |

**Birlikte:** `stat` + `use <potion_slot>` → otomatik potion; `near` + `SetTarget` + `attack` +
`goto` → av döngüsü (§3 T3); `ClickSkillSlot` + `IsSkillCoolTime` + `IsMountingHorse` → cycu
rotasyon deseni (§3 T7).

---

### 2.4 `chr` — karakter/instance görsel katmanı (hareket + dünyadaki varlıklar)

| Fonksiyon / sabit | Ne yapar | Kanıt |
|---|---|---|
| `chr.SetPixelPosition(x, y)` | **IŞINLAMA** — 211 kullanım (2-arg desen). `tp` komutu. | [K] |
| `chr.MoveToDestPosition(vid, x, y)` | **YÜRÜYÜŞ** — hedefe yol boyunca yürütür. `goto` komutu. | [K] 36 |
| `chr.GetPixelPosition(vid)` | Instansecin pozisyonu (cycu online kontrolü + `near` sweep). | [K] 50 + cycu |
| `chr.GetNameByVID(vid)` | VID → isim (`near` raporu). | [K] 52 |
| `chr.GetInstanceType(vid)` | VID → tip (PLAYER/NPC/ENEMY... — `near` tip etiketi). | [K] 57 |
| `chr.INSTANCE_TYPE_PLAYER/NPC/ENEMY` | Tip sabitleri. | [K] |
| `chr.SelectInstance(vid)` | Instanseci seç (kendi vid'ini seçmek dialog/hedef işlemleri için). | [K] 90 |
| `chr.SetMoveSpeed(f)` / `chr.SetAttackSpeed(f)` | Hız çarpanları (hız hack temeli — **dikkat: sunucu doğrulaması ve ban riski**). | [K] 30/18 |
| `chr.Revive()` | Ölümden dirilt (cycu ghost/relogin deseni). | [K] cycu + 22 |
| `chr.SetDirection(a)` / `chr.SetRotation(a)` | Dönüş/direction ayarı (kamera-karakter senkron). | [K] 14/4 |
| `chr.SetLoopMotion(MOTION_WAIT)` / `chr.PushOnceMotion(...)` / `chr.SetMotionMode(...)` | Animasyon kontrolü (koşma animasyonu tuşla beraber — nighttown hareket deseni). | [K] |
| `chr.MOTION_WAIT`, `chr.MOTION_MODE_ONEHAND_SWORD` | Animasyon sabitleri. | [K] |
| `chr.GetRace(vid)` | Instansecin irk/vnum verisi. | [K] 11 |
| `chr.IsGameMaster()` | GM mi (güvenli hedefleme — GM'e saldırma!). | [K] 9 |
| `chr.IsEnemy(vid)` / `chr.IsPartyMember(vid)` | Düşman/party kontrolü (hedef filtreleme). | [K] 4/3 |
| `chr.HasInstance(vid)` | VID hâlâ canlı mı (ölmüş hedefi tekrar vurmama). | [K] 6 |

**Birlikte:** `near` → `HasInstance` + `IsEnemy` filtre → `MoveToDestPosition` + `attack` → tam
av döngüsü; `SetPixelPosition` + `background.GetCurrentMapName` → harita-bazlı ışınlanma listesi.

---

### 2.5 `item` — eşya tanımları (vnum → bilgi)

| Fonksiyon / sabit | Ne yapar | Kanıt |
|---|---|---|
| `item.SelectItem(vnum)` + `item.GetItemName()` | vnum → isim (300/171 kullanım — `inv`/`equip` raporu böyle isim basar). | [K] |
| `item.GetIconImageFileName()` | vnum → ikon yolu (GUI raporları). | [K] 131 |
| `item.GetItemType()` / `GetItemSubType()` | Tip/alt-tip (ITEM_TYPE_WEAPON/ARMOR...) — potion mu silah mı filtresi. | [K] 84 |
| `item.GetItemSize()` | Envanterde kaç slot yer (1-3). | [K] 16 |
| `item.GetLimit(i)` + `item.LIMIT_LEVEL` | Kullanım sınırı (min seviye vb.). | [K] 7/7 |
| `item.IsAntiFlag(ITEM_ANTIFLAG_GIVE/MYSHOP)` | Eşya verilebilir mi/pazara konur mu (atma/hazırlık kontrolü). | [K] |
| `item.GetAffect(i)` | Eşyanın verdiği etki/bonus tanımı. | [K] 4 |
| `item.ITEM_APPLY_MAX_NUM` | Bonus slot sayısı sabiti. | [K] |

**Birlikte:** `inv` → vnum listesi → `SelectItem`+`GetItemType` → "potionları bul, sırayla `use`"
(§3 T4); `IsAntiFlag(GIVE)` → atılacak eşya filtresi.

---

### 2.6 `nonplayer` / `background` / `skill` / `chat` — dünya modülleri

| Modül · Fonksiyon | Ne yapar | Kanıt |
|---|---|---|
| `nonplayer.GetLevelByVID(vid)` | Mob/NPC seviyesi (`near` raporu). | [K] 6 |
| `nonplayer.GetGradeByVID(vid)` | Mob sınıfı (boss/normal). | [K] 4 |
| `background.GetCurrentMapName()` | **Mevcut harita adı** (`pos` raporu; 34 kullanım). | [K] |
| `background.GlobalPositionToMapInfo(x, y)` | Global koordinat → harita bilgisi (haritalar arası tp hesabı). | [K] 5 |
| `background.GlobalPositionToLocalPosition(x, y, mapIdx)` | Global → yerel koordinat dönüşümü. | [K] 4 |
| `background.LoadMap` / `RegisterEnvironmentData` / `SetEnvironmentData` / `EnableSnow` | Harita/ortam yükleyicileri (istemci tarafı görsel — oyuncu taşımadan görünüm değişir, sunucu etkisiz). | [K] |
| `skill.GetSkillName(idx)` | idx → isim (`skill` raporu). | [K] 15 |
| `skill.CanUseSkill(idx)` | Beceri ŞU AN kullanılabilir mi (mana/mesafe/CD toplu kontrol). | [K] 13 |
| `skill.GetSkillCoolTime(idx)` / `GetDuration(idx)` / `IsToggleSkill(idx)` | CD saniyesi/süre/anahtar beceri kontrolü. | [K] |
| `chat.AppendChat(chat.CHAT_TYPE_INFO, s)` | Sohbet penceresine satır bas (bot GUI'si olmayan tek "ekran çıkışı"). | [K] 990 (!) |
| `chat.CHAT_TYPE_INFO/NOTICE/SHOUT/TALKING/PARTY/GUILD` | Sohbet kanal sabitleri. | [K] |
| `event.SelectAnswer(idx)` | Quest dialog seçeneğini tıklar (quest botu için altın!). | [K] 39 |

---

### 2.7 `ui` / `wndMgr` / diğer — arayüz katmanı (özet)

| Modül · Fonksiyon | Ne yapar | Kanıt |
|---|---|---|
| `ui.Window / ScriptWindow / Board / EditLine / Button / TextLine...` | Arayüz çerçevesi — MaxExecutor'ın tüm menü komutları (selserver/login/mkchar/delchar) bu sınıfların `CallEvent()`/`SetText()`/`GetText()` yollarını kullanıyor. | [K] 3688 |
| `ui.__mem_func(fn)` | Metot bağlayıcı (cycu WaitingDialog `SAFE_SetTimeOverEvent` deseni — zamanlayıcı botları). | [K] 602 |
| `wndMgr.GetScreenWidth/Height`, `wndMgr.GetMousePosition` | Ekran/ faresi okuma (tık noktası hesapları). | [K] 103/85/20 |
| `ime.clock` / `ime.sleep` | py2 zamanlayıcı (nighttown döngü bekleme deseni — **oyun thread'inde uzun sleep YOK**, maxlib komutları kısa çalışır). | [K] 93 |
| `grp.GenerateColor` / `snd.PlaySound` / `dbg.LogBox` | Renk/ses/hata kutusu (bilgi çıkışı; `dbg.LogBox` eski sohbet'te serverinfo gösterimi için kullanılmıştı — çalışıyor). | [K] |

---

## 3. BİRLİKTE KULLANIM — KOMBİNASYON TARİFLERİ (cookbook)

> Hepsi MaxExecutor konsol komutlarıyla (elle) veya `raw`/pylib deseniyle (otomatik) kurulabilir.
> Konsol komutlarıyla başla; stabil çalışınca aynı adımları `raw` ile tek Python bloğuna dönüştür.

### T1 — Tam giriş zinciri (menü → oyun)
```
status → selserver 0 0 → waitfor LoginWindow 15 → login <id> <pwd>
→ waitfor SelectCharacterWindow 30 → charlist → selchar 0 → enter 0
→ waitfor GameWindow 60 → stat → pos
```
`login` UI yolu (idEditLine/pwdEditLine/loginButton.CallEvent) + `enter` UI START yolu
(StartGame) — oturum 12 saha doğrulaması. Oyun İÇİ komutlar bundan sonra geçerli.

### T2 — Envanter değerleme + potion bulucu
```
inv 0  →  inv 1  →  equip
```
Rapordaki `vnum`'lar `item.SelectItem(vnum)+GetItemName()` ile isimleşir. Potion slotlarını
bul; sonra: `use <slot>` (HP/SP potu). `stat` ile HP% düşünce tekrar `use`. Otomatikleşmesi:
`stat`'ın HP alanı + `use`'u 5 sn arayla çağıran bir `raw` bloğu (ana thread'de kısa).

### T3 — Otomatik av döngüsü (kavramsal; konsol adımları)
```
near                          → ENEMY listesi (vid + dist + Lv + isim)
goto <x> <y>                  → hedefe yürü (dist > 2000 ise)
attack 1                      → saldırıyı başlat (SetAttackKeyState)
skill                         → CD durumu; boşsa cmd /ride ile at kullan (cycu deseni)
attack 0                      → hedef ölünce bırak
near                          → yeni hedef...
```
Döngü otomasyonu için `near`'ın ENEMY satırlarını dosyadan okuyan bir `raw` bloğu kur:
`chr.HasInstance(vid)` + `chr.IsEnemy(vid)` + `player.GetCharacterDistance` şartları +
`player.SetTarget(vid)` + `attack` — nighttown Levelbot.py deseninin birebir mantığı.

### T4 — HP koruma / potion botu
```
stat                          → HP% = GetStatus(HP)/GetStatus(MAX_HP)
use <pot_slot>                → HP < %50 iken
```
`item.SelectItem(vnum)` + `GetItemType()` ile potion slotlarını baştan belirle ( Tip sabitleri
§2.5). SP için ayrı slot. **`drop` KULLANMA** — yanlış slot = eşya gider.

### T5 — Ghost / relogin botu (cycu.py'nin birebir deseni)
```
stat → (ölünce) revive       → chr.Revive() [K]
logout → waitfor SelectCharacterWindow → selchar 0 → enter 0 → waitfor GameWindow 60
```
cycu `kickfinish` döngüsü: `chr.GetPixelPosition(net.GetMainActorVID()) == 'None'` ise online
değil → DirectEnter tekrar dene. MaxExecutor'da bunun yerine `waitfor` + `enter` UI yolu
kullan (DirectEnter yeni karakterde reddediliyor — oturum 12 kanıtı).

### T6 — Pozisyon takipçisi + harita kaydı
```
pos                           → x/y/z + harita adı + metre karşılığı
tp <x> <y>                    → ışınlan; sonra tekrar pos ile doğrula
```
Düzenli kayıt için `raw` bloğu: her çağrıda `chr.GetPixelPosition` +
`background.GetCurrentMapName()` sonucunu `C:\MaxExec\results\last_pos.txt`'e append et
(`_write` deseni). Harita değişimini yakalamak için `GetMapName()` önceki değerle kıyasla.

### T7 — Skill rotasyonu (cycu'nun kanıtlanmış deseni)
```
skill                                   → slot/idx/Lv/CD tablosu
key UP 1 / key UP 0                     → hedefe koş/paralel
attack 1                                → temel saldırı
(cycu: ClickSkillSlot(1..6) + IsSkillCoolTime(1..6) + IsMountingHorse → /ride)
```
Döngü: `IsSkillCoolTime(slot) == 0` ise `ClickSkillSlot(slot)`; atlıysa önce `cmd /ride` in,
skill bas, sonra tekrar bin. Bu birebir cycu `skillc1..6b` blokları.

### T8 — KESİF zinciri (bu repo'nun geleceği)
```
pyfiles                       → 5 yöntem raporu
pydump intrologin             → tek dosya testi (ilk 40 satır konsolda)
pydumpall                     → TÜM py'ler → C:\MaxExec\dump\ + INDEX.txt
plusquest                     → yüklü modüllerin canlı kataloğu → PLUSQuest_live.txt
pyscan player                 → tek modül detayı (argüman adlarıyla)
```
Sonra: dump klasörünü ZIP'le → AI'ya gönder → PLUSQuest.md bu katalog senin istemcinin
gerçek içeriğiyle güncellenir → yeni komutlar (örn. switchbot, shop botu) kanıtlı yazılır.
**Bu döngü "eski AI'nin kestirdiği" değil, SAHADAN doğrulanmış API listesi üretir.**

### T9 — Eşya yöneticisi (topla/bırak/tak)
```
pickup                        → yerdeki en yakın eşya (PickCloseItem)
near                          → yerdeki eşya VID'leri → net.SendItemPickUpPacket(vid)
inv 0 / inv 1                 → dolu slotlar
use <slot>                    → giyin/kullan (zırh/potion)
drop <slot> <n>               → çöpe at (DESTRÜKTİF — IsAntiFlag(GIVE) kontrolü yap!)
```
Taslak mantık: `inv`'de vnum X'in hepsi doluysa → `GetItemCountByVnum` ile toplamı say →
`GetItemAttribute` ile bonus karşılaştır → kötüsünü `drop`.

### T10 — Dış dünya köprüsü (cycu BinDir deseni → dosya tabanlı)
cycu.py oyuncu durumunu **registry**'ye yazıyordu (HKCU\SOFTWARE\BinDir: onln/mplynm/mplylv/
orthp/ortmp/ortexp/mjob/mrace) ve dış program okuyordu. MaxExecutor'da bunun modern hali:
her rapor zaten `C:\MaxExec\results\last_*.txt`'e yazılıyor — dış bot/panel bu dosyaları okur,
komutları `C:\MaxExec\queue\*.cmd`'e bırakır (headless mod). Registry yerine dosya: daha
hızlı, taşınabilir, basedir.txt ile D:\'ye taşınabilir.

---

## 4. GÜVENLİK VE RİSK NOTLARI (dürüst hükümler)

| Eylem | Risk | Not |
|---|---|---|
| `stat/pos/inv/equip/skill/near/pyfiles/pyscan/plusquest/pydump` | **Düşük** — okuma yönünde, sunucuya paket gitmiyor (pydump disk yazımı hariç). | En güvenli grup. |
| `chat/whisper/cmd` | **Orta** — sunucuya paket gider; spam = chat-mute/rapor. | İnsan temposunda kullan. |
| `use/ride/attack/goto/key` | **Orta** — oyun içi eylem; anti-bot desenleri (aralıklar) insan gibi kullan. | Aralıklarla (2-5 sn) kullan; saniyede onlarca komut = desen. |
| `tp` | **Yüksek** — bazı sunucularda koordinat doğrulaması ister; geri atma/ban olabilir. | Önce kendi riskini test et (küçük mesafe). |
| `drop` | **Veri kaybı** + sunucu izi. | Slot numarasını iki kez doğrula. |
| `chr.SetMoveSpeed/SetAttackSpeed`, `SendRefinePacket` | **En yüksek** — hız hack / geliştirme spam'ı sunucu tarafında loglanır. | Bilinçli, tek seferlik denemeler. |
| Genel | Konsol komutları **ana thread'de** çalışır: uzun `raw sleep` döngüleri oyunu dondurur. | Döngüleri kısa tut; bekleme için `waitfor` kullan. |

---

## 5. SÜRÜM DURUMU VE CANLI GÜNCELLEME

- Katalog tabanı: **v1.8 PLUSMAXGOD / pylib v4.0** (oturum 13) — kanıt havuzu:
  nighttown koleksiyonu (Modules/, m2kmod/, pyDetour/, scripts_root/ — 4000+ kullanım)
  + cycu.py + oturum 9-12 saha testleri.
- **Canlı zenginleştirme:** oyunda `plusquest` → `PLUSQuest_live.txt` → AI'ya gönder.
  - Menüde az modül, oyunda çok modül yüklü → **oyundayken** çalıştır.
  - `pydumpall` ile pack içi kaynaklar → `C:\MaxExec\dump\` → gönder → bu katalog
    dosya-dosya doğrulanır ve yeni bölümler eklenir.
- Bu dosyadaki her [K] işareti, kullanıcının kendi istemcisinden gelen saha kanıtıdır;
  [S] işaretleri resmî API bilgi birikimidir; [?] işaretleri `pyscan`/`pyfiles` ile
  tek seferlik doğrulanabilir.
