# PLUSQuest — Metin2 İstemci Python Fonksiyon Kataloğu
### (PLUSMAXGOD Edition · v4.8 · Oturum 19 — SAHA TESTİ 14: otp2 W-basılı yürüyüş + satma/atma 1-arg paket düzeltmesi + stop komutları; envanter yönetimi kanıtları: m2k Inventorymanager shop.IsOpen/SendShopSellPacket(1-arg)/SendItemDropPacket(1-arg) + uiShop.py SendShopSellPacketNew + game.py MoveUp DIK_UP + GetDegree dönüş konvansiyonu S=0 B=90 K=180 D=270)

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
| `pyfiles` | `app.GetFileList` [K-disk] + `sys.modules` + `pkgutil` + `os.listdir` + import-probe + **pack API keşfi (v4.1)** | karışık |
| `pydump` / `pydumpall` | **v4.1 zinciri:** `pack.Exist`+`pack.Get` → `pack_open` → `app.OpenTextFile` → disk | [K] FileExtractor:407, New_Levelbot:363, edithack:888, itemcreator:418 |
| `pyscan` / `plusquest` | `sys.modules` + `dir()` + `func_code.co_varnames` | [S] py2 çekirdeği |
| `unequip` / `unequipall` | takılı slota `net.SendItemUsePacket(slot)` (tak=use, çıkar=aynı paket) | [K] kullanıcı saha testi 9 |
| `chchange` / `relogin` | `net.Disconnect` + UI akış otomasyonu (`_pw_by_type` + `selserver/login/enter`) — farmbot deseni | [K] UI yolları saha-9 |
| `ground` / `groundtake` / `autotake` | **`textTail.Pick(x, y)`** ekran taraması + `net.SendItemPickUpPacket(vid)` | [K] pickupstealer.py + Itemstealer.py |
| `quest` | **`quest.GetQuestCount` + `quest.GetQuestData`(4'lü) + `quest.GetQuestLastTime`(2'li) + `quest.GetQuestIndex`** | [K] uicharacter.py:812-876 |
| `fakeitem` / `fakeclear` | **`player.SetItemData(slot, vnum, adet)`** + `SetItemAttribute` + `SetItemMetinSocket` (hayalet) | [K] itemcreator.py CreateItem |
| `clone` / `spawn` / `morph` | **`chr.CreateInstance(vid)` → `SelectInstance` → `SetVirtualID` → `SetNameString` → `SetRace` → `SetArmor` → `SetHair` → `SetMotionMode` → `SetLoopMotion` → `SetRotation` → `Show`** (1-arg setterlar SEÇİLİ instance'a gider!) | [K] introselect.py MakeCharacter |
| `simya` / `ds` | `player.GetItemIndex(player.DRAGON_SOUL_INVENTORY, slot)` (2-arg form) + `item.ITEM_TYPE_DS` | [K] PythonPlayerModule.cpp:788 + canlı katalog |
| `itemscan` | `item.SelectItem(vnum)` + `GetItemName/GetItemType` taraması | [K] itemcreator/EQChanger |
| `fish` ailesi | `player.SetAttackKeyState` (at/çek) + `chrmgr.IsPossibleEmoticon(-1)` (ısırtma/baloncuk) + `game.GameWindow.OnFishingNotify/Success/Failure` hook + `player.GetItemMetinSocket(eb+4, 2)` (olta-skill) | [K] fishbot1.0.py + client kaynak |
| `canli` | `C:\MaxExec\live.txt` yaz → DLL [LIVE] akışı (FIX-36) | [K] v1.9 |

---

## 1. KEŞİF YÖNTEMLERİ — eski AI'nin doğruları / yanlışları (GOD MOD hükmü + SAHA TESTİ 8)

Eski sohbetteki AI 5 yöntem saymıştı. İşte kesin hükümler — artık **saha testi 8** (v4.0'ın
144 hedeflik ilk pydumpall'ı + 439KB PLUSQuest_live) ile birebir doğrulanmış hali:

| Yöntem | Hüküm | Saha testi 8 kanıtı |
|---|---|---|
| `app.GetFileList("*.py")` | **[K-disk] ÇALIŞTI ama VAADİ YANLIŞ** — eski AI "en iyi yöntem" dedi. Gerçek: VAR ve çalışıyor **ama SADECE DISK dosyalarını** listeliyor. 73 dosya döndü — **73'ü de kullanıcının kendi eklediği botlar** (pasha37-levelbot vb., oyunun kullanmadığı, root/epx'te olmayan dosyalar). Oyunun kendi modülleri listede YOK. | INDEX.txt: `app.GetFileList=73 disk=73` — aynı 73 dosya iki kez. |
| `app.OpenTextFile` + `GetTextFileLineCount` + `GetTextFileLine` | **[K-disk / X-pack] YEDEK** — disk dosyalarında çalışır (73 bot tam döküldü). AMA pack içi dosyalarda handle verip **0 SATIR** döndürüyor: oyunun kendi 59 modülü (app/chr/player/game/ui/introLogin...) **2 bayt boş** çıktı. cycu.py'nin `GetTextFileTuple`'u da (mode=0'da zaten boş liste döndürür — kendi bug'ı) bu yolda. | INDEX: 59× `OK 0 satir` → 2 bayt dosyalar. |
| `pack.Exist(ad)` + `pack.Get(ad)` | **[K] GERÇEK PACK OKUMA YOLU (v4.1)** — dump edilen **çalışan botların kendi kodunda** kanıtlı: `FileExtractor.py` (ScriptStealer!) `pack.Exist` + `pack_open` zinciriyle pack'ten extract ediyor; `New_Levelbot.py:363` = `pack.Get("playersettingmodule.py")` ile **root pack'ten kaynak metni string olarak okuyor**. | Bot ekosistemi birebir kanıt. |
| `pack_open(ad, mod)` | **[K] DOSYA-OBJESİ YOLU (v4.1)** — `edithack.py:888/911/939` + `itemcreator.py:418/441/469`: `pack_open("locale/de/item_list.txt", "r").readlines()` — item_list **pack içindedir, diskte değil** → pack okuma ispatlı. Bare global (istemci injected) ya da `pack.pack_open`. | 6 ayrı satır, çalışan botlarda. |
| `sys.modules` | **[K] DOĞRU** — yüklü **130 modül** sayıldı (app, chr, player, game, ui*, introLogin..., cpsm, maxlib...). v4.1 `pydumpall` hedef listesi ARTIK buradan canlı üretilir. | pyfiles raporu [2]: 130. |
| `pkgutil.iter_modules()` | **[X] ÇALIŞMIYOR** — `ImportError: No module named pkgutil` (gömülü importer taşımiyor). Beklenen buydu; not olarak raporlanır. | pyfiles raporu [3]. |
| `os.listdir()` | **[K-koşullu] DOĞRU** — disk açık: 73 bot dosyası + client klasörü (`C:\Users\Admin\Desktop\NightTownFullpack`) yakalandı. Pack içini göremez (onun işi `pack.Get`). | pyfiles raporu [4]. |

**Özet yargı (v4.1):** dosya *listesi* için `sys.modules` (canlı 130 modül) + disk taraması;
dosya *içeriği* için **`pack.Get` → `pack_open` → `app.OpenTextFile` → disk** zinciri
(`_pack_read`). `pyfiles` artık `[6] pack API keşfi` (dir(pack) + Exist/Get/pack_open
hasattr tablosu) ve `[7] modül __file__ raporu` da basar.

**Not (kullanıcı gözlemi, doğru):** dump'a karışan `pasha37-levelbot.py`, `darealfreakbot.py`
gibi dosyalar **oyunun kullanmadığı, sonradan klasöre atılmış** botlar (root/epx modüllerinde
yok) — oyun onları import etmez. Oyunun **kendi** dosyaları pack içindedir ve v4.1 ile
`pack.Get` zinciriyle dökülecektir.

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

### 2.8 v4.2 — BALIKÇILIK MEKANİĞİ + SAHTE INSTANCE KAYNAK HÜKÜMLERİ (LegendySF-V2 kaynak okuması)

**Sunucu balık akışı** (`fishing.cpp` — klasik mainline, NightTown aynı aile):
| Aşama | Sunucu kodu | İstemci etkisi |
|---|---|---|
| Atış (`CG_FISHING`) | `CHARACTER::fishing()`: yalnız **ATTR_BLOCK** kontrol (SU KONTROLÜ YOK!) + olta takılı mı + yem (`soket2>0`) | İstemcide `GetFishingRot` 400 birim içinde su ister — 10'ar derece tarar; su yoksa paket bile gönderilmez |
| Bekleme | `CreateFishingEvent`: `number(10, 40)` **saniye** | — |
| Isırtma | `FishingReact` → `GC_REACT` → `SetFishEmoticon` (baloncuk) + `hang_time` kaydı | `chrmgr.IsPossibleEmoticon(-1)==0` = baloncuk aktif |
| Çekiş | `Compute(fish, ms, level)`: `ms>6000→FAIL`; `kova=(ms+99)/200`; `number(1,100) <= aFishingTime[tip][kova]`; sonra `number(1, zorluk) <= olta-skill` | tepki ms'si = başarının tekill belirleyicisi (istemci tarafı) |
| Kaçırma | 6 sn asımı: `rod->SetSocket(2, 0)` — **olta-skilli SIFIR** | — |
| Balık seçimi | `DetermineFish`: harita→prob_idx (1/21/41=0, 3/23/43=1); **Fish Mind → prob_idx 2** (daha iyi tablo) | istemci SEÇEMEZ |
| Sonuç | `GC_SUCCESS/FAIL` + `GC_FISH(vnum)` → `OnFishingSuccess(isFish, fishName)` / `OnFishingFailure()` | `game.GameWindow` metotları hook'lanabilir (v4.2 fish yapar) |

**aFishingTime tablosu** (%; kova=(ms+99)/200; MAX_FISHING_TIME_COUNT=31):
tip0: `0,0,0,0,0,2,4,8,12,16,20,22,25,30,50,80,50,30,25,...` — **anında tepki %0**, 2.6-3.2sn'de %30-80
tip1: `0 ×16, sonra 4,8,12,16,20,22,25,30,50,80,50,...` — 3.2-6 sn arası
tip2: `20,22,25,30,50,80,50,30,...` — anında en iyi (%80, kova 5)
tip3: **hepsi %100**
tip4: `20,20,20,20,20,22,24,28,32,36,40,42,45,50,70,100,70,...` — 3sn'de %100

**Sahte instance kanıt sırası** (`introselect.py MakeCharacter` — bu motor ailesinin kendi kodu):
```python
chr.CreateInstance(slot)          # RegisterInstance (boş instance)
chr.SelectInstance(slot)         # SEÇİM ŞART — 1-arg setterlar seçiliye gider
chr.SetVirtualID(slot)
chr.SetNameString(name)
chr.SetRace(race)                # CInstanceBase::SetRace aktörü yeniden kurar (InstanceBase.cpp:996)
chr.SetArmor(form)               # + RegisterBoundingSphere
chr.SetHair(hair)
chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
chr.SetLoopMotion(chr.MOTION_INTRO_WAIT)
chr.SetRotation(0.0)
chr.Hide() / chr.Show()
```
> Kritik hüküm (PythonCharacterModule.cpp): **TÜM 1-arg setter'lar `GetSelectedInstancePtr()`'a gider** —
> `chr.SetPixelPosition(x, y)`'nin tp olarak çalışmasının nedeni bu. Morph/klon sonrası `SelectInstance(ben)`
> ile seçimi geri al (v4.2 otomatik yapar). Demirci = race **20016** (npclist.txt: `20016 blacksmith`).

**Hayalet eşya** (itemcreator.py `CreateItem`): `player.SetItemData(slot, vnum, adet)` — boş slot bulma + 2-tall
üst kontrolü dahil; bonuslar `SetItemAttribute(slot, i, tip, deger)`, metinler `SetItemMetinSocket(slot, i, vnum)`.
İstemci göstergesidir; sunucu `SetItemData`'yı görmez.

**Yer eşyası tarama** (pickupstealer.py/Itemstealer.py): `textTail.Pick(x, y)` ekran-koordinat seçici — grid
tarama (X 300-825, Y 125-600) → VID listesi → `net.SendItemPickUpPacket(vid)`. Yer eşyaları chr instance
DEĞİLDİR (INSTANCE_TYPE'da ITEM yok) — bu yüzden ad/vnum okunamaz, yalnız VID.

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

- Katalog tabanı: **v1.8.1 PLUSMAXGOD / pylib v4.1** (oturum 14) — kanıt havuzu:
  nighttown koleksiyonu (Modules/, m2kmod/, pyDetour/, scripts_root/ — 4000+ kullanım)
  + cycu.py + oturum 9-13 saha testleri + **saha testi 8** (v4.0'ın ilk pydumpall'ı:
  73 disk dosyası tam döküldü; oyun modüllerinin pack'te olduğu + OpenTextFile'ın
  pack'te 0 satır verdiği tespit edildi; çalışan botların KENDİ kodundan `pack.Get` /
  `pack.Exist` / `pack_open` kanıtı çıkarıldı).
- **Saha testi 8'de birebir ÇALIŞANLAR** (kullanıcı log'u): `stat` (Lv100 Ninja-E Jinno
  tam rapor), `pos` (vid/x/y/z + metin2_map_c1), `skill` (9 slot + Rumence isimler),
  `near`, `tp` (SetPixelPosition 2-arg), `goto` (MoveToDestPosition), `attack`,
  `chat /ride`, `revive`, `pyfiles` (5 yöntem + 130 modül), `pyscan`, `plusquest`
  (439KB canlı katalog), `pydumpall` (disk dosyaları). Hatalı yazılanlar:
  `player.ClickSkillSlot(15)` komut değil → `raw player.ClickSkillSlot(15)` yaz;
  `serverlist` menü sahnesinde çalışır (oyundayken `HATA: LoginWindow sahnesinde
  degil` — doğru davranış).
- **Canlı zenginleştirme:** oyunda `plusquest` → `PLUSQuest_live.txt` → AI'ya gönder.
  - Menüde az modül, oyunda çok modül yüklü → **oyundayken** çalıştır.
  - **v4.1 `pydumpall`** ile pack içi kaynaklar (sys.modules canlı hedefler + UI
    script yolları, pack.Get zinciri) → `C:\MaxExec\dump\` + INDEX.txt (yöntem + byte
    kolonlu; 0 byte = BOS işaretli) → gönder → bu katalog dosya-dosya doğrulanır
    ve yeni bölümler eklenir.
- Bu dosyadaki her [K] işareti, kullanıcının kendi istemcisinden gelen saha kanıtıdır;
  [S] işaretleri resmî API bilgi birikimidir; [?] işaretleri `pyscan`/`pyfiles` ile
  tek seferlik doğrulanabilir.
