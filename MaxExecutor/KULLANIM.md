# MaxExecutor PAKETİ — TAM KULLANIM KILAVUZU (Türkçe)

> Paket içeriği, kurulum, komutlar, giriş akışı, sorun giderme — hepsi bu dosyada.
> Mimari gerekçe için: `reports/DEV_REAL_BINARY_TEST.md` (RC18/RC19) + `reports/DEV_GIL_ANALYSIS.md` (RC1-RC17).
> Son güncelleme: **Oturum 19 — MaxExecutor v2.4 PLUSMAXGOD / pylib v4.8 (saha testi 14 dev raporu — sürekli oto-pot + W-basılı yürüyüş + satma/atma paket düzeltmesi + durdurma komutları)**
>
> **v2.4/v4.8 ÖZET — saha testi 14 (tümü kanıtlı):**
> **`autopot` SÜREKLİ İZLEME:** saha raporu '1 kere bastı bir daha basmadı ve karakter öldü' — kök neden: döngü tek büyük `except`'in içindeydi, ilk exception'dan sonra SESSİZCE ölüyordu. Artık her blok ayrı try/except'te + **ilk 3 hata [LIVE]'a yazılır** + **30 saniyede bir kalp atısı** (`[LIVE] AUTOPOT: izleme AKTIF (basilan kirmizi=N mavi=M)`). Eşik altındayken **0.4sn'de bir** pot basar, eşik ÜSTÜNE çıkınca işaretir. Karakter ölüyken pot basmaz (uyarı yazar), pot yoksa 5sn'de bir hatırlatır.
> **`otp2` SÜREKLİ BASILI:** saha raporu 'bas çek değil, konuma gidilene kadar sürekli basılı tutsun' — v4.7'deki adım-sıçramalar (SetPixelPosition) KALDIRILDI. Artık karakter her 100ms'de **hedefe döndürülür** (`chr.SetRotation` — darealfreakbot/pasha37-levelbot GetDegree kanıtı: S=0, B=90, K=180, D=270) ve **W+UP tuşu BASILI KALIR** (`SetSingleDIKKeyState` her tik yenilenir — game.py MoveUp DIK_UP kanıtı), varınca/`otpstop`'ta tuşlar MUTLAKA bırakılır. Uzaklık artarsa 'engel var olabilir' uyarısı verir. `otp1` aynen korundu (kanıtlanmış adım-adım).
> **`slots` SAYIM DÜZELTMESI:** saha raporu '45 45 toplam 90 slot var' ama kod 168 diyordu — TOPLAM artık **sekme x sekme-boyu** (2x45=90); `INVENTORY_SLOT_COUNT` farklıysa bilgi satırı. Her sekme için **9 kolonlu slot HARİTASI** (`#`=esya, `.`=boş, `E`=efsunlu, `?`=okuma-hatasi) + okuma-hata sayacı + `GetElk`/`GetGold` yang yedeği — hangi slot boş görünüyor direkt görünür.
> **`selljunk`/`sellall` YENİ AKIŞ:** saha raporu 'satmıyo' + 'kapatamıyom sürekli npc açıyo'. (1) **PAKET ÖNCELİĞİ DÜZELTİLDİ:** artık ÖNCE kanıtlı 1-arg `net.SendShopSellPacket(slot)` (m2k Inventorymanager + Taubuyer — NightTown'da ÇALIŞMIŞ bot kodu; v4.7 yanlışlıkla önce yeni 2-arg `SendShopSellPacketNew(slot,adet)` paketini yolluyordu ve bu sunucu onu işletmiyordu); (2) **SPAM YOK:** NPC'ye 1 tik + 8sn SESSIZ bekleme (eski 'NPC dukkani aciliyor' fırtınası bitti); dükkan açılmazsa en fazla 1 tekrar, sonra durur — sen NPC'ye KENDİN tıkla, **dükkan açılır açılmaz satma otomatik başlar** (bekleme sırasında `shop.IsOpen()` izlenir); (3) **DURDUR:** `selljunk 0` / `sellall 0` (veya `stop`).
> **`dropall` DÜZELTMESI:** saha raporu 'drop all da atmıyo' — v4.7 2-arg `SendItemDropPacketNew` ile başlıyordu (bu sunucuda işlevsiz). Artık ÖNCE kanıtlı 1-arg `net.SendItemDropPacket(slot)` (m2k DropAllItems kanıtı). 0.45sn arayla tek tek + 2 doğrulama turu + **DURDUR: `dropall 0`** + hiçbir şey atılamazsa 'sunucu atmayı engelliyor olabilir' teşhisi.
> **[LIVE] SPAM BİTTİ:** sell/drop döngüleri artık her 3 saniyede bir özet satırı yazar (slot+yöntem bilgisiyle) — saniyede 2 satır fırtınası yok.
>> **v2.3/v4.7 ÖZET — saha testi 13 (tümü kanıtlı):**
> **KALDIRILDI (kullanıcı isteği):** `speed`/`aspeed` (sunucu `chr.SetMoveSpeed/SetAttackSpeed` tanımıyordu) + `chchange`/`relogin` (karakteri değiştiriyordu — CH değil; sonra detaylı yeniden yapılacak).
> **`warp` TAMAMEN YENİ — LEGENDY YOLU:** `warp <x> <y>` artık **sahneyi YENİDEN yükler** (kullanıcının anlattığı net.directenter tarzı). Kanıt: LegendySF-V2 `consolemodule.py` warp konsol komutu = `background.Destroy()` + `background.Initialize()` + **`background.WarpTest(x,y)`** (+ çevre/gölge kurulumu) — bu istemcinin background modülünde WarpTest VAR (canlı katalog). Koordinat = **pos/100** (örn pos 38421 39017 → `warp 384 390`; büyük yazarsan otomatik /100). Harita sınırı YOK — atlas koordinatıyla başka haritaya da geçer. Sonrasında karakter hedefe yerleştirilir + konum paketi gönderilir.
> **`otp1`/`otp2` (OTP yöntem ayrımı):** mevcut kanıtlı yöntem = **`otp1`** (saldiri tuşu basılı). **`otp2` YENİ:** atak YERİNE **W TUŞU** basılı gider (`player.SetSingleDIKKeyState(app.DIK_W, 1)` — game.py DIK_W + Crap_Levelbot kanıtları; kullanıcının 'dik_key_w' tarifi). `otp` = `otp1` eş anlamlı.
> **`autopot` YENİ DÜZEN (kullanıcı isteği):** `autopot hp 80` = can **%80 altına düşünce NORMAL kırmızı pot** (27001-3, oto-pot eşyası HARİÇ, sürekli basar) · `autopot mp 80` = mana %80 altında NORMAL mavi pot (27004-6) · `autopot` = durum raporu · `autopot 0` = hepsi kapalı.
> **`autopot_item` YENİ:** `autopot_item hp` = **otomatik pot basan eşya** (72723-72726 + 76021-2 + 79012; kullanıcı örneği **72724**) **pasifse basar, aktifse dokunmaz** (gerek yok — metinSocket[0] aktiflik kontrolü, uiInventory.py kanıtı); eşya bitince yenisini 3sn içinde otomatik basar. `autopot_item mp` = mana tarafı (72727-30 + 76004-5 + 79013). `autopot_item 0` = izleme kapalı.
> **ENVANTER YÖNETİMİ YENİ:** `slots` (kaç sekme/slot, dolu mu, kaç slot kaldı, **% kaç dolu**, yang) · `selljunk` (çöp eşyaları **yakındaki NPC'ye sat** — dükkan otomatik açılmaya çalışılır: yakın NPC'ye `net.SendOnClickPacket`; **efsunlu olanlar ASLA satılmaz**; çöp listesi = balıklar + `selljunk add <vnum>` / `selljunk name <isim>` ile genişletilir — junklist.txt'ye kalıcı kaydedilir) · `sellall [force]` (tüm envanteri sat; efsunlular korunur — `force` ile dahil, DİKKAT!) · `dropall` (tüm envanteri **tek tek yere at** — bazı sunucular toplu atmayı reddediyor; 3 tur doğrulama ile reddedilenler tekrar denenir). Kanıtlar: m2k Inventorymanager (shop.IsOpen + SendShopSellPacket) + uiShop.py:231 (SendShopSellPacketNew) + ItemUse.py (SendOnClickPacket).
> **attackkeystate BUG DÜZELTİLDİ:** `otpstop` artık saldırı VE W tuşlarını **mutlaka bırakır** — saha raporu: 'fonksiyon kullanmasan bile attackkeystate aktif' — nedeni otp'nin yol ortasında durdurulunca tuşu BASILI bırakmasıydı. Tüm durdurma/hata yollarında tuş bırakma eklendi.
> **KONSOL [LIVE] TEMİZLİĞİ:** DLL her açılışında konsol ESKİ oturumun [LIVE] balık satırlarını geri oynatıyordu (live.txt append modunda birikiyordu). Düzeltme: C++ izleyici açılışta dosyanın SONUNA atlar (sadece yeni satırlar akar) + pylib oturum başında live.txt'yi temizler.
> **DUMP DÜZELTİLMELERİ:** (1) `_pack_read` artık `sys.modules['pack']` üzerinden **DİREKT** erişir (import zinciri hiç işlemez — gömülü pylib'de serverinfo.py dumplanmama sorunu için) + `__main__` globals'ten `pack_open` yedeği. (2) **C modülleri (player.py/chr.py/net.py...) artık API-STUB olarak dump edilir** — kaynak .py yok ama gerçek `dir()` içeriği (sabitler + fonksiyon listesi) yazılır; `pydump player` da aynı şekilde çalışır.
>
> **v2.2/v4.6 ÖZET — saha testi 12 (tümü NightTown dump kanıtlı):**
> **DÜZELTMELER:** (1) **`near` artık METİN TAŞLARINI bulur** — tip filtresi kaldırıldı; kagb-multihack kanıtı: **0=MOB, 2=METİN, 6=OYUNCU** (v4.5 filtresi tip-2'yi atıyordu!). (2) **`speed`/`aspeed` artık 0.5sn DÖNGÜ** — Crap_Levelbot kanıtı: sunucu hızı sürekli gerçek değere sıfırlar, tek atış etkisizdi; her döngü gerçek→hack hızı dansı. (3) **`antifly` saldırı tuşu artık varsayılan DEĞİL** — 1=animasyon kilidi, 2=+Güçlü Beden (AFFECT_CHEONGEON — zihinsel savaşçı devrilmeme efezgi), 3=orijinal (saldırılı). (4) **`chchange`/`relogin` karakter ekranında takılma bitti** — select ekranından oyunun KENDİ `stream.SetLoginPhase()` yolu (networkModule.py: Disconnect + faz takası). (5) **`attr` etiketleri** — efsun 1-5 + **6./7. BONUS** (rare) ayrımı (efsunbotu.py index kanıtı: 0-4 normal, 5-6 rare).
> **YENİ KOMUTLAR:** `warp <x> <y>` (otp adımlama + **net.SendCharacterPositionPacket** — CG_POSITION 'konuma istek' paketi; kullanıcının tarif ettiği teknik) · `antistun 1` (sersemleme anında çözme döngüsü — AFFECT_STUN temizleme) · `antislow 1` (yavaşlatma çözme — AFFECT_SLOW+KWAESOK; speed ile birlikte kullan) · `autopot 1 [hp%] [sp%]` (**otomatik kırmızı/mavi pot**: 27001-3=Licoare Rosie, 27004-6=Licoare Albastra — New_Levelbot + itemscan kanıtı) · `combo <0-3>` (**sürekli vuruş** — chr.testSetComboType, 123klo-multihack kanıtı: 'render animasyonunu damage animasyonuyla değiştirme' tekniği) · `statdown <ht|iq|st|dx> [n]` (stat puanı GERİ AL — `/stat-`, uiCharacter minus kanıtı) · `skillupui <slot>` / `statupui <part>` (oyunun KENDİ UI fonksiyonları: OnPressedSlotButton / __OnClickStatusPlusButton — **başka py-paketi yok, oyunun kendisi de chat paketi kullanıyor** [uiCharacter.py:947 kanıtı]) · `efsun <slot>|all` (envanter+ekipman BONUS efsun raporu — attr'nin yeni adı).
> **MAPOlarak ışınlanma notu:** map-arası geçiş SUNUCU kontrolünde (harita kapıları/yüzük paketi sunucuda işler). `warp` aynı haritada garantilidir; map değiştirmek için `goto` ile harita kapısına yürü.
>
> **v2.1/v4.5 — saha testi 11 kök-neden onarımı:**
>
> **v2.1/v4.5 ÖZET — SAHA TESTİ 11 KÖK NEDENİ (önceki v2.0 neden hiçbir şey çalışmadı):**
> v4.4 pylib **HİÇ yüklenemiyordu**: yeni eklenen `_NearScanWnd`/`_GoTakeWnd`/`_AntiFlyWnd` sınıfları, `ui_WindowBase` tabanının tanımından (dosyanın ilerisinde, v4.2 bölümündeydi) **ÖNCE** kullanılıyordu → import anında `NameError` → pylib exec'i çöktü → BootImport **sessizce** eski `pylib.py v3.2`'ye düştü → `itemscanall`/`morph`/`otp`/`speed`/`morphtarget`/`fakemount` = AttributeError ("PYTHON HATASI"), `serverlist` eski mesaj, `near` = `_my_vid` hatası, her komutta "pylib v3.2 yüklendi" banner tekrarı. **v4.5 çözümü:** taban tanımı sınıfların ÜSTÜNE taşındı + `import ui` korumalı (ui yüklenmemişse yedek taban — dongu pencereleri zaten komut anında kurulur). **DLL v2.1 çözümleri:** (1) BootImport yükseltme denemesi **oturum başına 1 kez** (v2.0'ta her komutta yeniden deniyordu = banner spam + konsol karışıklığı); (2) yükleme başarısızsa **tam traceback `results\last_pylib_fail.txt`'ye yazılır** — sessiz düşüş artık imkansız; (3) ölü `fishtp` kalıntısı ("tek atış bitti") tamamen temizlendi. **Komut seti v2.0 ile aynı (91 komut, hepsi pylib'te var — otomatik çapraz-kontrol edildi).** Kurulum: DLL'i değiştir → yeniden enjekte → `C:\MaxExec\PLUSMAXGOD_PyScript.py` otomatik v4.5'e yükseltilir (elle kopyalama GEREKMEZ; bundle'daki .py dosyası manuel yedek için).
>
> **v2.0/v4.4 ÖZET — saha testi 10 (kullanıcı raporları):**
> **KALDIRILDI:** `fishdelay` `fishswap` `fishswapnow` `fishtp` (çalışmıyordu/istenmedi; fishdelay'in auto-öğrenici mantığı dahili olarak yaşıyor).
> **YENİ KOMUTLAR:** `morphtarget` (hedef NPC/mob/oyuncuya dönüş — önce TIKLA) · `cloneplayer` (hedef oyuncuya dönüş: ırk+ad) · `fakemount 0/1` (sahte at binisi — chr.MountHorse kanıtı: saf istemci görünümdür, sunucu binmemiş sayar → **skill serbest!**) · `speed <0-1100>` / `aspeed <0-1100>` (chr.SetMoveSpeed/SetAttackSpeed; 100=normal, 0=geri yükle; **1100 üstü client'ta sıfırlanır!**) · `statup <ht|iq|st|dx> [adet]` + `skillup <idx> [adet]` (uiCharacter.py kanıtı: `/stat ht`, `/skillup idx`) · `antifly 0/1/2` (kanıtlı yöntem AntiFly.py: WAIT animasyonu + saldırı tuşu) + `antiflyeffect <id>` (chrmgr.SetAffect) · `itemfind <kelime>` (isimle arama: `itemfind simya` / `itemfind kostüm` / `itemfind efsun`) · `iteminfo <vnum>` (tam proto: tip/efsun/limit/flag) · `attr <slot>` + `attrall` (**efsun okuma** — efsunlu mu, hangi efsunlar) · `useon <kagit-slot> <esya-slot>` (**efsun ekleme/değiştirme/5.attr/kostüm efsunu** — net.SendItemUseToItemPacket kanıtı efsunbotu.py) · `efsunsw <slot>` (efsun kâğıdını bul+uygula) · `gotake <vid|all>` (eşyaya yürü + topla).
> **FIX:** `clone` Z (GetPixelPosition artık (x,y,z) üçlü + sac **otomatik** okunur: hesap karakter tablosu kanıtı) · `spawn`/`morph` **görsel tazeleme** (_visual_kick: Update/Deform + Hide/Show + WAIT — "zırh tak-çıkar" bitti; spawn konumu geri-okunup rapora yazılır) · `near` **GENİŞ tarama** (eski 1..2000 → anlık 1..50000 + arka plan 0..4M pencere taraması → `near_full.txt`; bu sunucuda VID 20000+ olduğu için eski tarama hiçbir şey bulamıyordu) · `otp` (yol boyunca **saldırı tuşu BASILI**, varışta bırakılır — kullanıcının "attackkeystate true ile git" düzeltmesi; varsayılan bekleme **50ms**) · `relogin`/`chchange` (kök neden: net.Disconnect soketi kesiyor ama python faz penceresi GameWindow'da kalıyordu → npc/karakterler kayboluyor sahne değişmiyordu. Yeni yol: **net.ExitGame()/net.LogOutGame()** — uiSystem.py'daki "Karakter Değiştir/Oturum Kapat" butonlarının kullandığı sunucu-driven faz paketleri; relogin artık select ekranından direkt girer, login gerekmez) · **konsol karışıklığı** (3 yazarsız printf kilitli tek kanala alındı + pylib yükleme raporu artık dosyaya yazılıp konsola tek kısa satır basıyor — "oyuna girer girmez balık tutma yazıları" bitti) · `itemscanall` 50k kesme hatası.
> **Simya/eşya bulma:** `itemfind simya` (Dragon Soul taşları isimle çıkar) → `iteminfo <vnum>` (tip/efsun kontrol) → `/i <vnum>`. Kostüm bonusu: `itemfind kostüm` + `useon` (sunucu destekliyorsa).
>
> **v4.1 ÖZET — saha testi 8 dersi (kullanıcı: "oyunun kendi kullandıklarını 1kb dumpladı, tam dumplayamamış"):** v4.0 `pydumpall` 144 hedef buldu; diskteki 73 bot dosyasını TAM döktü (pasha37-levelbot.py = 178KB ✓) AMA oyunun kendi 59 modülü (app/chr/player/game/ui/introLogin...) **2 bayt BOŞ** çıktı. Kök neden 3 katman: (1) `app.GetFileList` bu istemcede **SADECE DISK** listeliyor — 73 dosyanın hepsi senin sonradan attığın botlar (oyun onları kullanmıyor; root/epx'te yok — senin gözlemin doğruydu); (2) oyunun kendi modülleri root **PACK** içinde; (3) `app.OpenTextFile` pack dosyalarında handle verip **0 satır** döndürüyor. **v4.1 çözümü — KANITLI OKUMA ZİNCİRİ** (dump edilen ÇALIŞAN botların kendi kodundan çıkarıldı): `pack.Exist`+`pack.Get` (FileExtractor.py "ScriptStealer" + New_Levelbot.py:363 `pack.Get("playersettingmodule.py")` root pack'ten KAYNAK okuyor!) → `pack_open(ad,"r")` (edithack.py:888 + itemcreator.py:418) → `app.OpenTextFile` (artık YEDEK) → disk. `pydumpall` hedefleri artık **canlı sys.modules'ten** (130 modül) + UI script yollarından (locale/ro/ui + UIScript, oyun log kanıtlı) üretilir; INDEX.txt'e **yöntem + byte kolonu** geldi; 0 byte = `BOS` işaretli (sahte OK yok). `pyfiles`'a `[6] pack API keşfi` + `[7] modül __file__` raporu geldi. **Saha testi 8'de ÇALIŞANLAR:** stat/pos/skill/near/tp/goto/attack/chat/revive/pyfiles/pyscan/plusquest (439KB canlı katalog) — hepsi temiz. Komut yazım hatası notu: `player.ClickSkillSlot(15)` tek başına komut DEĞİL → `raw player.ClickSkillSlot(15)` yaz.
>
> **v4.1 ÖZET — saha testi 8 dersi (kullanıcı: "oyunun kendi kullandıklarını 1kb dumpladı, tam dumplayamamış"):** v4.0 `pydumpall` 144 hedef buldu; diskteki 73 bot dosyasını TAM döktü (pasha37-levelbot.py = 178KB ✓) AMA oyunun kendi 59 modülü (app/chr/player/game/ui/introLogin...) **2 bayt BOŞ** çıktı. Kök neden 3 katman: (1) `app.GetFileList` bu istemcede **SADECE DISK** listeliyor — 73 dosyanın hepsi senin sonradan attığın botlar (oyun onları kullanmıyor; root/epx'te yok — senin gözlemin doğruydu); (2) oyunun kendi modülleri root **PACK** içinde; (3) `app.OpenTextFile` pack dosyalarında handle verip **0 satır** döndürüyor. **v4.1 çözümü — KANITLI OKUMA ZİNCİRİ** (dump edilen ÇALIŞAN botların kendi kodundan çıkarıldı): `pack.Exist`+`pack.Get` (FileExtractor.py "ScriptStealer" + New_Levelbot.py:363 `pack.Get("playersettingmodule.py")` root pack'ten KAYNAK okuyor!) → `pack_open(ad,"r")` (edithack.py:888 + itemcreator.py:418) → `app.OpenTextFile` (artık YEDEK) → disk. `pydumpall` hedefleri artık **canlı sys.modules'ten** (130 modül) + UI script yollarından (locale/ro/ui + UIScript, oyun log kanıtlı) üretilir; INDEX.txt'e **yöntem + byte kolonu** geldi; 0 byte = `BOS` işaretli (sahte OK yok). `pyfiles`'a `[6] pack API keşfi` + `[7] modül __file__` raporu geldi. **Saha testi 8'de ÇALIŞANLAR:** stat/pos/skill/near/tp/goto/attack/chat/revive/pyfiles/pyscan/plusquest (439KB canlı katalog) — hepsi temiz. Komut yazım hatası notu: `player.ClickSkillSlot(15)` tek başına komut DEĞİL → `raw player.ClickSkillSlot(15)` yaz.
>
> **v1.8 ÖZET — oturum 13 (kullanıcı raporu: v1.7 HEPSİ ÇALIŞTI ✓):** Saha doğrulaması sonrası iki yeni yetenek ailesi eklendi. **(A) OYUN-İÇİ KOMUTLAR:** `stat` (seviye/HP/SP/EXP), `pos` (x/y/z + harita), `inv <sayfa>` (envanter), `equip` (ekipman), `skill` (beceriler), `near` (yakın varlıklar), `chat <mesaj>` / `cmd /komut` (sohbet), `whisper`, `ride/revive/logout/back/pickup`, `zoom <mesafe>`, `use <slot>`, `drop <slot> <adet>` (DİKKAT), `goto <x> <y>` (yürü), `tp <x> <y>` (ışınla), `key <DIK> <0/1>`, `attack <0/1>`. Hepsi kanıtlı API'ler — nighttown koleksiyonu 4000+ kullanım + cycu.py. **(B) KESİF KOMUTLARI:** `pyfiles`, `pydump <ad>`, `pydumpall` (HEPSİNİ `C:\MaxExec\dump`'a + INDEX.txt), `pyscan <modul>`, `plusquest` (tüm modülleri tara → PLUSQuest_live.txt). **(C) YENİ ADLANDIRMA:** pylib artık diskte **PLUSMAXGOD_PyScript.py** olarak yaşar (DLL v1.8 otomatik yazar/yükseltir; eski pylib.py hâlâ yedek yol olarak kabul edilir — BootImport yerinde yükseltir). Katalog: **PLUSQuest.md** (MaxExecutor klasöründe).
>
> **v1.7 ÖZET — saha testi 7 dersi (oturum 12):** v1.6'nın 30 komutu da temiz çalıştı (pyfail=0) ve iki gerçek oyun-düzeyi bulgu çıktı. **(1) `enter` oyuna sokmuyor:** `net.DirectEnter` YENİ oluşturulan karakterde sunucu tarafından reddediliyor (loading penceresi açılıp login ekranına geri atıyor); eski karakterlerde (raynare) çalışıyor. Oyunun kendi START butonu ise çalışıyor — kullanıcı doğrulaması + MaximumPyScript_Merged_calisan kanıtı. **v1.7 `enter`: önce SelectSlot + StartGame/startButton (UI yolu); DirectEnter sadece UI yolu bulunamazsa YEDEK.** Çift-giriş yasağı (RC12) korunur: UI yolu seçilince DirectEnter hiç çağrılmaz. **(2) mkchar'dan sahte CREATE_FAILURE:** çift paket gidiyordu — UI OLUSTUR butonu paketi kendisi yolluyor + pylib bir de direkt SendCreateCharacterPacket yolluyordu → 1. paket başarı, 2. paket `CREATE_FAILURE: 0 (0 karakter yaratılamaz)`. Karakter zaten oluşmuştu; sahte hataydı. **v1.7 mkchar: paket yolu SADECE buton bulunamazsa.**
>
> **v1.3 ÖZET — saha testi 26.10 dersi:** kuyruk/drenaj/ana-thread zinciri ÇALIŞIYORDU (kanıt: `results\py_probe.txt` oluştu, `alive.txt` aktti) ama makinede **`C:\MaxExec\pylib.py` dosyası yoktu**. `load` sessiz IOError yedi, `maxlib` hiç kurulmadı; her `status`/`login`/`waitfor` komutu pyerr.log'a "ImportError: No module named maxlib" yazdı (100+ kez). **v1.3 pylib.py'yi otomatik yükler** — dosya yoksa baştan uyarır.

> **v1.5 ÖZET — saha testi 5 dersi (oturum 10):** makinede DLL v1.4 vardı ama `pylib.py` hâlâ **v2.0** idi (eski bundle'dan). Yeni komutlar (selchar/mkchar/delchar...) sessiz `AttributeError` yedi — konsol hiçbir şey söylemedi, hatalar yalnız pyerr.log'daydı. v1.5 bunu kökten bitirir: **pylib v3.0 artık DLL'İN İÇİNE GÖMÜLÜ** — diskteki pylib eksik/eskiyse DLL otomatik yazar (eskisini pylib_eski_vX.py olarak yedekler), sürüm uyumsuzluğu varsa açılışta KOSKOCA uyarı basar, Python hatası olursa konsol artık `!! PYTHON HATASI — detay: pyerr` diye BAĞIRIR (sessiz hata devri kapandı).

> **v1.6 ÖZET — saha testi 6 dersi (oturum 11):** v1.5'in hata görünürlüğü asıl problemi ortaya çıkardı: **neredeyse her komut `PYTHON HATASI` veriyordu.** Kök neden: v1.5, komutların import-bootstrap'ına sürüm-koruması ekleyince metin ~660 karaktere büyüdü; ama eski komut üreticileri hâlâ `char buf[256]/[512]` + `_snprintf` ile kod üretiyordu → kuyruktaki .cmd dosyaları **satır ortasında kopuk Python kodu** içeriyordu (255/511 byte) → `SyntaxError: EOL while scanning string literal` → komut hiç çalışmıyordu. Kanıt zinciri: maxexec.log'ta 674 byte'lık komutlar (newchar/joblist/lasterr — std::string ile üretilenler) ÇALIŞTI; 255/511 byte'lıklar PATLADI; pyerr.log'daki kesik satırlar birebir bu kesime noktasına denk geliyor. **v1.6: tüm üreticiler std::string'e çevrildi (FIX-23) — kesilme yapısal olarak imkânsız.** Bonuslar: Python `print`'leri konsola düşüyor (FIX-28), `charlist`/`joblist`/`mkchar`/`selchar` raporları CANLI görünüyor (pylib v3.1 yankısı), oyun hataları (yanlış şifre vb.) olduğu AN konsola `[OYUN HATASI]` satırı düşüyor, eksik argümanlı komutlar `kullanim:` mesajı veriyor, `status` bayat dosya göstermiyor (FIX-27).

---

## 1. PAKET İÇİNDE NE VAR?

| Dosya | Ne işe yarar | Nereden geldi |
|---|---|---|
| `bin/MaxExecutor.dll` | **Ana proje.** Oyun içine enjekte edilen 32-bit DLL. Ana thread'de (WndProc + SetTimer) Python çalıştırır. Hook YOK, SHM YOK, arka-plan PyRun YOK. **v1.8: PLUSMAXGOD komut ailesi (oyun-ici + kesif) + surum-ongoer BootImport + dump klasoru.** | Bu repo — derlendi (32-bit PE, `-O2`; zig cc `x86-windows-gnu`) |
| `bin/MaxInject.exe` | DLL enjektörü. `metin2client.exe` sürecini bulur, DLL'i LoadLibrary ile yükler. | Bu repo — derlendi |
| `PLUSMAXGOD_PyScript.py` | **pylib v4.6 (maxlib).** DLL içine gömülü; diskte eksik/eskiyse otomatik yazılır. Tüm komutlar: menü (login/charlist/mkchar...) + oyun-ici (stat/inv/tp...) + kesif (pyfiles/pydumpall/plusquest). | Bu repo |
| `pylib.py` | Eski v3.2 adı — YEDEK yolu olarak kabul edilir (BootImport önce PLUSMAXGOD'u dener). Silinebilir; DLL yeniden yazmaz. | Bu repo |
| `MaximumPyScript_STABLE.py` | Eski mimarinin (SHM'li v17) RC12/RC13/RC14 yamalı hali. Alternatif yol. | Bu repo |
| `MaxExecutor.cpp` / `MaxInject.cpp` | Kaynak kodlar (değişiklik yaparsan yeniden derlersin) | Bu repo |
| `README.md` | Mimari açıklama (İngilizce başlıklı ama içerik Türkçe) | Bu repo |

**Derleme ortamı (v1.1):** Debian GCC 14.2 mingw-w64 (win32 threads), i686-w64-mingw32, `-static` (579KB DLL, bağımlılık: yalnız USER32/KERNEL32 + UCRT). **v1.8: zig 0.11.0 (root-less) — 614KB DLL.**

---

## 2. KURULUM (5 ADIM, ~2 DAKİKA)

1. **Klasörü hazırla** — oyunun kurulu olduğu bilgisayarda:
   ```
   C:\MaxExec\
       MaxExecutor.dll
       MaxInject.exe
   ```
   (pylib.py artık ZORUNLU DEĞİL — v1.5 DLL'in içinde gömülü; diskte eski/eksikse otomatik yazar. Yine de yanına koymak istersen bundle'daki pylib.py'yi kopyala.)
2. **Oyunu aç** → login ekranı görünene kadar bekle (pencere oluşsun).
3. **Enjekte et** — Komut İstemi'ni (cmd) **Yönetici olarak** aç:
   ```
   cd C:\MaxExec
   MaxInject.exe
   ```
   - Otomatik: `metin2client.exe` sürecini arar.
   - Başka isimli client: `MaxInject.exe metin2.exe`
   - PID ile: `MaxInject.exe 12345`
   - Farklı DLL yolu: `MaxInject.exe metin2client.exe D:\yer\MaxExecutor.dll`
4. **Konsol açılır** — "MaxExecutor v1.8 PLUSMAXGOD" başlıklı siyah pencere (oyunun ÜSTÜNDE kalır, TOPMOST).
   İlk satırlarda şunları görmelisin:
   ```
   python27.dll : BULUNDU [initialized]
   PLUSMAXGOD_PyScript.py : v4.1 (uyumlu) - otomatik yuklenecek
   oyun penceresi: SUBCLASS EDILDI (hwnd=0x...)
   ana-thread timer: KURULDU
   ```
   > `PLUSMAXGOD_PyScript.py : GUNCELLENDI -> v4.1 (DLL icinden yazildi)` görürsen: diskteki pylib eskiymiş (veya v3.2 idi), v1.8 gömülü kopyayı yazdı — ekstra bir şey yapmana gerek yok. Eski dosya `PLUSMAXGOD_eski_*.py` olarak yedeklenir.
   > Eski `pylib.py` v3.2 yerinde duruyorsa bile sorun yok: BootImport sürümü okur, v4'ten küçükse PLUSMAXGOD_PyScript.py ile YERİNDE yükseltir (FIX-32).
   > `!! PYLIB ESI` uyarısı görürsen: pylib yazılamadı demektir (yazma hatası) — o zaman elle kopyala.
   > `python27.dll : YOK` ise oyunun Python'u henüz başlamamıştır → konsolda bekle,
   > oyun login ekranına gelince `status` yazarak tekrar dene (DLL her 0.5 sn'de yeniden dener, 20 sn boyunca).
   > Konsol bir sebeple hiç açılmazsa: `C:\MaxExec\maxexec.log` dosyasına bak (her adım oraya yazılır)
   > ve §6'daki "headless mod" başlığına geç.
5. **Hazır.** §3'teki akışa geç.

> ⚠️ **Win7/Win8'de "api-ms-win-crt-*.dll eksik" hatası alırsan:** Visual C++ 2015-2022 Redistributable (x86) kur → UCRT'yi getirir. Win10/11'de gerekmez.

---

## 3. İLK GİRİŞ AKIŞI (komut sırası birebir)

> ⚠️ **Bu client'ta login'den ÖNCE server listesi ekranı var** (server isimleri + CH listbox + OK butonu).
> O yüzden akış `selserver` ile başlar.

MaxExecutor konsolunda sırayla:

```
status                                  (0) SCENE= ne diyor bak (LoginWindow+ServerList ise dogru ekrandasin)
                                        (1) load ARTIK YOK — v1.3 pylib.py'yi otomatik yükler
                                           (kanıt: results\last_pylib_load.txt, 2 sn içinde oluşur)
selserver 0 0                           (2) listedeki 0. sunucu + 0. CH'yi seç, OK'a bas
serverlist                              (*)  isimleri/listbox içeriğini görmek istersen
waitfor LoginWindow 15                  (3) login (id/şifre) ekranına düşünceye kadar
login kullaniciadim sifrem              (4) id+şifre doldur + giriş
waitfor SelectCharacterWindow 30        (5) karakter seçme ekranı
charlist                                (6) 5 slot tablosu
enter 0                                 (7) 1. slotla oyuna gir (UI START yolu)
waitfor GameWindow 60                   (8) oyun + NPC spawn
status                                  (9) son durum
pyerr                                   (*)  Python hatası olduysa son 30 satırı konsola döker
```

Sonuç dosyaları `C:\MaxExec\results\` altında: `py_probe.txt` (zincir kanıtı), `last_status.txt`, `last_server.txt`, `last_login.txt`, `last_charlist.txt`, `last_enter.txt`, `last_error.txt`, `last_pylib_load.txt`.

### SAHA DOĞRULAMALI SENARYOLAR (v1.7, oturum 12 testi: HEPSİ ÇALIŞTI ✓)

> Bu iki akış gerçek sunucuda uçtan uca test edildi (giriş → bayrak → oluşturma → oyuna giriş → silme).
> `waitfor` sahne adını `SCENE=` çıktısıyla eşleştirir (substring). Bu sunucuda bayrak ekranının
> sahne adı **ReselectEmpireWindow**'dur (SelectEmpireWindow.py yüklenir ama sahne adı böyle raporlanır).

**SENARYO A — BAYRAK SEÇMELİ** (hesapta 0 karakter / ilk karakter; testte tam olarak bu akış çalıştı):
```
status
selserver 0 0
waitfor LoginWindow 15
login <id> <sifre>
waitfor SelectCharacterWindow 30
charlist
newchar                        bayrak ekranı açılır (ilk karakter)
waitfor ReselectEmpireWindow 10
empirelist                     mevcut empire + bayrak tablosu
empireui 2                     1=Shinsoo 2=Chunjo 3=Jinno -> OLUSTURMA ekranı açılır
waitfor CreateCharacterWindow 10
joblist                        sinif/cinsiyet tablosu + ekran durumu
mkchar Isim 5                  sinif gez + cinsiyet + isim + OLUSTUR (tek paket)
waitfor SelectCharacterWindow 15
charlist                       yeni karakter slotta mi?
selchar 0
enter 0                        UI START yolu (StartGame) -> oyun yüklenir
waitfor GameWindow 60
status
```

**SENARYO B — BAYRAK SEÇMESİZ** (empire kayıtlı; `newchar` direkt olusturma ekranını açar):
```
status
selserver 0 0
waitfor LoginWindow 15
login <id> <sifre>
waitfor SelectCharacterWindow 30
charlist
newchar                        bayrak atlanir, direkt CreateCharacterWindow
waitfor CreateCharacterWindow 10
joblist
mkchar YeniIsim 5
waitfor SelectCharacterWindow 15
charlist
selchar 0
enter 0
waitfor GameWindow 60
status
```

**SİLME AKIŞI** (test edildi: delchar → delcode → 0 karakter → sonraki newchar bayrak ekranını açtı):
```
charlist
delchar <slot>                 silme sorusu + kod dialogu ACAR
delcode <kod>                  kodu yazar + ONAYLAR
waitfor SelectCharacterWindow 10
charlist                       slot BOS mu?
lasterr                        DELETE_SUCCESS/DELETE_FAILURE kaydi
```
> Not: `chardel` diye bir komut YOK — doğrusu `delchar` (saha testinde 3 kez karıştırıldı).

### ZİNCİR KOPTU MU? (bir şey olmuyorsa 30 sn bekle, sonra bak)

| Kontrol | Ne demek |
|---|---|
| `results\py_probe.txt` VAR | Ana thread Python'u çalışıyor — zincir TAMAM. Sorun Python/pylib tarafında → `pyerr.log` |
| `results\py_probe.txt` YOK + `alive.txt`'de `exec=0` | Komutlar kuyruğa giriyor ama çalıştırılmıyor |
| `alive.txt`'de `timer>0` artıyor | Oyun mesaj pompası TimerProc'u çağırıyor — drenaj yaşıyor (v1.2 ana yol) |
| `alive.txt`'de `msg>0` artıyor | WndProc subclass da yaşıyor |
| `alive.txt` HİÇ yok / 2 sn'de bir güncellenmiyor | Drain hiç çağrılmıyor — `maxexec.log`'a bak (SetTimer satırı var mı?) |
| `alive.txt` içeriği örnek: `tick=110017796 drain=412 exec=8 timer=409 msg=3 py=1` | `drain` akıyor ama `exec` 0 ise python27 çözülememiş → `maxexec.log` |


---

## 3b. KARAKTER İŞLEMLERİ (v1.4 — giriş yaptıktan sonra)

> pylib v3.0 **otomatik hata izleme** kurar: `LoginWindow.OnLoginFailure` +
> `SelectCharacterWindow.OnCreateFailure/OnDeleteFailure/OnDeleteSuccess` hook'ları
> (Python-seviye, kanıtlanmış desen). Yanlış şifre, isim çakışması, silme sonucu →
> `results\last_error.txt`'ye düşer. Konsolda görmek için: **`lasterr`**

### a) Slot seçme / girme
```
charlist              tabloya bak (hangi slotlar dolu/bos)
selchar 4             4. slotu SEÇ (isaretler; girmez)
enter 2               2. slotla OYUNA GİR (UI START yolu - StartGame butonu)
```

### b) Yeni karakter oluşturma (2 ekran: bayrak → sınıf/cinsiyet/isim)
```
newchar               "karakter olustur" butonuna basar
status                hangi ekran geldigine bak
  SCENE=SelectEmpireWindow   -> bayrak ekrani (ilk karakter)
  SCENE=CreateCharacterWindow -> direkt olusturma (bayrak kayitliysa)

bayrak ekrani geldiyse:
empirelist            bayrak listesi + mevcut empire (1=Shinsoo 2=Chunjo 3=Jinno)
empireui 1            bayrak sec + ILERLE butonu (paket yolu yedekli)
waitfor CreateCharacterWindow 10

olusturma ekraninda:
joblist               sinif/cinsiyet tablosu (race 0-8) + ekran durumu
mkchar YeniIsim 3     sinif gez + cinsiyet + isim + OLUSTUR'a bas
                      (v3.2: paket yolu SADECE buton bulunamazsa - cift paket
                       sahte CREATE_FAILURE: 0 uretiyordu, artik yok)
                      race=3 -> Shaman(K); race=7 -> Shaman(E); 0=Warrior(E)...
waitfor SelectCharacterWindow 15
charlist              yeni karakter slotta mi? (30 sn create cooldown olabilir)
lasterr               hata varsa (isim mevcut = CREATE_FAILURE: 1)
```

### c) Karakter silme (2 adım: soru+kod dialogu → kodu gir)
```
charlist              once bak
delchar 3             3. slotu sec + "karakteri sil" sorusu + kod dialogunu ACAR
delcode 1111111       silme kodunu yazar + ONAYLAR
lasterr               sonuc: DELETE_SUCCESS / DELETE_FAILURE
charlist              slot bosaldi mi?
```
> Bazı serverlar silme kodu istemez (`NOT_NEED_DELETE_CODE`) — delchar çıktısında belirtilir.

### d) Hata komutları özeti
| Komut | Ne gösterir | Kaynak dosya |
|---|---|---|
| `lasterr` | **OYUN hataları** (yanlış şifre=LOGIN_FAILURE: WRONGPWD, isim mevcut, silme sonucu...) | `results\last_error.txt` |
| `pyerr` | **PYTHON hataları** (traceback — kod hatası) | `pyerr.log` |
| `log` | **DLL izi** (EXEC satırları, sayaçlar) | `maxexec.log` |

### create ile yeni karakter (karakter yoksa)
```
charlist                                önce bak: hangi slotlar boş?
empire 1                                gerekliyse bayrak/imparatorluk seç (1=Shinsoo 2=Chunjo 3=Jinno)
create 0 MaxAdi 2 0                     slot0, isim, race=2 (Sura-E), shape=0
enter 0
```
**race tablosu (LegendySF MAIN_RACE):** 0=Savaşçı-E, 1=Ninja-K, 2=Sura-E, 3=Şaman-K, 4=Savaşçı-K, 5=Ninja-E, 6=Sura-K, 7=Şaman-E, 8=Wolfman-E.
**Hata takibi:** `results/last_error.txt` — `isim mevcut (bType=1)` / `karakter yaratılamaz (bType=0)` / 30 sn create cooldown bilgisi buraya düşer.

### serbest komut
```
raw import net; net.SendChatPacket("merhaba", 0)
raw print(net.GetMainActorVID())     → çıktı C:\MaxExec\results\last_error.txt değil; stdout oyun loguna gider.
```
> Not: `raw` ile `print` çıktısı MaxExec konsoluna DEĞİL, oyunun kendi debug çıkışına gider.
> Değer almak için maxlib desenini kullan (dosyaya yazar).

---

## 3c. OYUN-İÇİ KOMUTLAR (v1.8 PLUSMAXGOD — `waitfor GameWindow 60` SONRASI)

> Tümü oyunun KENDİ kanıtlı API'lerini kullanır (nighttown koleksiyonu 4000+ kullanım +
> cycu.py — kullanıcının ekosistemi). Her komut önce "oyunda mıyız?" kontrolü yapar;
> menü ekranındaysa `HATA: oyunda degilsin (once waitfor GameWindow 60)` der.
> Raporlar `results\last_<komut>.txt`'e yazılır + konsola canlı basılır.

### a) Durum raporları
```
stat       ad/seviye/HP%/SP%/EXP%/race/skill grubu/empire/hız/biniş durumu
pos        vid + x/y/z + metre (x/100) + HARİTA ADI (background.GetCurrentMapName)
           + hazır tp/goto önerisi
inv 0      envanter 1. sayfa (45 slot): slot/vnum/isim/adet — INVENTORY_PAGE_SIZE'dan okunur
inv 1      2. sayfa (45..89)
equip      ekipman slotları (EQUIPMENT_BASE_INDEX=90+: silah/zırh/kolye...)
skill      beceriler: slot/idx/isim/Lv/Grade/CD (GetSkillIndex yoksa öğretilmiş tarama)
near       10000 birim yarıçaptaki varlıklar: vid/tip/dist/isim/Lv (VID sweep 1..2000,
           chr.GetInstanceType + GetNameByVID + nonplayer.GetLevelByVID — kanıtlı)
```

### b) Sohbet + eylemler
```
chat merhaba            genel sohbet paketi (net.SendChatPacket)
cmd /ride               slash komut (aynı yol — /ride /logout /phase_select ...)
whisper Oyuncu selam    özel mesaj (net.SendWhisperPacket)
ride | revive | logout | back | pickup   hızlı eylemler (cycu.py kanıtları)
zoom 12000              kamera menzili (app.SetCameraMaxDistance)
use 5                   5. slottaki eşyayı KULLAN (net.SendItemUsePacket — 218 kanıt)
drop 5 1                5. slottan 1 adet YERE BIRAK — DESTRUKTİF, geri alınamaz!
```

### c) Hareket
```
pos                     önce konumu oku (x/y + harita)
goto 95900 269000        KONUMA YÜRÜ (chr.MoveToDestPosition(vid,x,y) — yol izler)
tp 95900 269000          KONUMA IŞINLAN (chr.SetPixelPosition(x,y) — 211 kanıt;
                         server koordinat doğrulaması yoksa anlık ışınlanma)
key UP 1 / key UP 0      tuş simülasyonu (player.SetSingleDIKKeyState — 368 kanıt!)
attack 1 / attack 0      saldırı basılı tut / bırak (player.SetAttackKeyState — 100 kanıt)
```
> `goto` yürümedir (animasyonlu, mesafe kademeli), `tp` anlıktır. Bazı sunucular tp'yi
> sunucu tarafında doğrular — ışınlanma sonrası `pos` ile doğrula, geri atarsan `goto` kullan.

### d) Kesif akışı (oyunun python dosyalarını çek + incele) — v4.1
```
pyfiles                 6 rapor: app.GetFileList (SADECE DISK - saha testi 8) +
                        sys.modules (canli 130 modul) + pkgutil (yok - beklenen) +
                        disk taramasi + import-probe + [6] pack API kesfi (dir(pack),
                        Exist/Get/pack_open var mi) + [7] modul __file__ raporu
pydump introLogin       TEK dosyayi KANITLI ZINCIRLE oku → C:\MaxExec\dump\ + ilk 40 satir
                        (zincir: pack.Get → pack_open → app.OpenTextFile → disk;
                        buyuk-kucuk harf varyantlari otomatik denenir)
pydumpall               HEPSINI dok → C:\MaxExec\dump\*.py + INDEX.txt
                        hedefler: sys.modules canlisi (oyunun KENDI modulleri!) +
                        probe + disk + UI script yollari (locale/ro/ui + UIScript);
                        INDEX'te yontem + byte kolonu; 0 byte = BOS isaretli
pyscan player           yüklü modülün fonksiyonları + argüman adları (py2 func_code)
plusquest               TÜM yüklü modülleri tara → C:\MaxExec\dump\PLUSQuest_live.txt
                        (oyundayken çalıştır — daha fazla modül yüklü olur)
```
> **SONRAKI ADIM:** `C:\MaxExec\dump` klasörünü ZIP'le → AI'ya gönder → PLUSQuest.md kataloğu
> senin istemcinin gerçek dosyalarıyla zenginleştirilir.
>
> **SAHA TESTİ 8 HÜKMÜ (v4.1'in nedeni):** v4.0 `pydumpall` 144 hedef buldu; diskteki 73
> bot dosyasını TAM döktü AMA oyunun kendi 59 modülü (app/chr/player/game/ui...) **2 bayt
> boş** çıktı. Nedenler: (1) `app.GetFileList` bu istemcede SADECE DISK listeliyor — 73
> dosyanın hepsi senin sonradan attığın botlar (oyun onları kullanmıyor, root/epx'te yok);
> (2) oyunun kendi modülleri root **PACK** içinde; (3) `app.OpenTextFile` pack dosyalarında
> handle verip **0 satır** döndürüyor. **GERÇEK pack okuma yolu** (çalışan botların kendi
> kodundan çıkarıldı): `pack.Exist(ad)` + `pack.Get(ad)` (FileExtractor.py + New_Levelbot.py:363
> `pack.Get("playersettingmodule.py")` = root pack'ten kaynak okuyor!) ve `pack_open(ad,"r")`
> (edithack.py:888 + itemcreator.py:418, pack içindeki item_list.txt'yi okuyor). v4.1
> `pydump`/`pydumpall` tam bu zincirle çalışır.

---

## 3e. v2.4 / pylib v4.8 — ENVANTER + WARP + OTOPOT (saha testi 14 günceli)

```
slots                        envanter ozeti + SLOT HARITASI (#=esya .=bos E=efsunlu ?=hata)
                             TOPLAM = sekme x sekme-boyu (2x45=90)
selljunk                     cop esyalari yakindaki NPC'ye sat (efsunlu ASLA satilmaz)
                             NPCye 1 tik; dukkan ACILIR ACILMAZ satis baslar
  selljunk 0 | stop          DURDUR ('kapatamiyom' fix - spam yok)
  selljunk add 27803         cop listesine vnum ekle (kalici: junklist.txt)
  selljunk name fier         isminde 'fier' gecen esyalari cop say
  selljunk list              listeyi goster | selljunk del <vnum> cikar
sellall [force]              tum envanteri sat (force: efsunlu dahil - DIKKAT)
  sellall 0 | stop           DURDUR
dropall                      tum envanteri YERE AT (1-arg kanitli paket, tek tek)
  dropall 0 | stop           DURDUR

warp 384 390                 LEGENDY warp: SAHNE YENIDEN YUKLENIR (net.directenter tarzi)
                             koordinat = pos/100 (buyuk yazarsan otomatik /100)
otp1 <x> <y>                 OTP yontem 1: saldiri tusu + adim-adim (kanitli eski yontem)
otp2 <x> <y>                 OTP yontem 2 (v4.8): W+UP BASILI KALIR, karakter hedefe
                             donderilir; sicrama yok; varince tuslari otomatik birakir

autopot hp 80                can %80 ALTINDAYKEN kirmizi pot 0.4sn'de bir SUREKLI
                             (esige dek basar; 30sn'de bir kalp atisi yazar)
autopot mp 80                mana %80 altinda NORMAL mavi pot (ayni surekli mantik)
autopot                      durum raporu (hata sayaci dahil)
autopot 0                    hepsini kapat
autopot_item hp              oto-pot ESYASI (72723-6..): pasifse bas, bitince yenile
autopot_item mp              mana oto-pot esyasi (72727-30..)
autopot_item 0               esya izlemesini kapat
```

**Kaldırılanlar (kullanıcı isteği, v2.3):** `speed`/`aspeed` (sunucu tanımıyordu), `chchange`/`relogin` (karakteri değiştiriyordu — CH değil; detaylı versiyon sonra yapılacak).

**warp koordinat hesabı:** `pos` raporu pixel verir (örn 38421 39017) → warp değeri = **/100** (384 390). Her harita 256x256 birim; atlas koordinatı verilirse **harita sınırı yok** (GlobalPositionToMapInfo o haritayı yükler). warp sonrası `pos` ile kontrol et — sunucu senkronu için konum paketi otomatik gider.

**selljunk/sellall akışı (v4.8):** (1) komut anında yakın NPC'ye **1 tık** (`SendOnClickPacket`, 3500px içinde en yakın) — tekrarlı tıklama YOK ('sürekli npc açıyo' bitti). (2) `shop.IsOpen()` SESSİZ izlenir: dükkan açılınca satış otomatik başlar; 8 sn içinde açılmazsa EN FAZLA 1 tık daha, o da olmazsa durur ve 'NPCye KENDIN tikla' der — **sen elle tıklayınca da satış kendiliğinden başlar**. (3) Satış: çöp eşyalar **tek tek** (0.4sn arayla) ÖNCE `net.SendShopSellPacket(slot)` (m2k/Taubuyer NightTown kanıtı — 1-arg), yoksa `SendShopSellPacketNew(slot, adet)` (uiShop.py kanıtı). (4) Tam tur bitince **doğrulama turları**: kalan satılabilirler için en fazla 2 tekrar; bitince özet (satılan/atlanan) + 'dukkan açık kalır, ESC ile kapat'. (5) Efsunlular **asla satılmaz** (`sellall force` hariç). Durdurma her an: `selljunk 0` / `sellall 0`.

**dropall akışı (v4.8):** 0.45 sn'de bir **1-arg `net.SendItemDropPacket(slot)`** (m2k DropAllItems NightTown kanıtı; v4.7'nin 2-arg New paketi bu sunucuda işlevsizdi). 2 doğrulama turu; hiçbir şey atılamazsa 'sunucu yere atmayı engelliyor olabilir' teşhisi yazar. Durdurma: `dropall 0`.

## 4. NEDEN BU MİMARİ GÜVENLİ? (kısa hatırlatma)

| Eski yöntem (cppcmpr / Generated v9.2.0) | MaxExecutor |
|---|---|
| Worker thread'den Python C-API → **GIL crash** (RC1/RC3) | Yalnız ana thread (WndProc) → GIL zaten bizde |
| C++ stack'inde sahte PyInt/TupleObject (RC19) | Sahte obje YOK — gerçek PyRun_SimpleString |
| SendAttackPacket'a prolog hook → MazeProtector/decrypt çakışması (RC18) | Fonksiyon hook'u YOK |
| SHM bayt dilimi komutlar | Atomik dosya kuyruğu (`.tmp` → `MoveFile`) |
| `gc.get_objects()` heap taraması (RC2) | Yok |
| Çift giriş StartGame+DirectEnter → NPC yok (RC12) | Tek giriş: UI yolu seçilince DirectEnter ÇAĞRILMAZ (v3.2); DirectEnter yalnız UI bulunamazsa tek başına |

Worker thread yalnız **dosya yazar + PostMessage** atar; Python'a hiç dokunmaz. Drain her mesajda
en fazla **4 komut** işler ve render'a nefes verir (`MAX_CMDS_PER_DRAIN`).

---

## 5. ESKİ YOL — MaximumPyScript_STABLE.py (alternatif)

Bu, eski SHM mimarisinin yamalı hali (v18-STABLE). **MaxExecutor'u tercih et;** bunu yalnız
eski Controller (win32apiMetin2Py / cppcmpr) zincirini kullanacaksan çalıştır:

1. Eski DLL'in (Kaynak.cpp v6 GILGuard'lı derlemesi) yüklü ve `Control_<PID>` SHM'si açık olmalı.
2. Oyun içi Python'a gir:
   ```
   py exec(open('C:/MaximumPyScript_STABLE.py').read())
   ```
3. Yamalar otomatik uygulanır: tek giriş (NPC fix), loading-recovery kilidi, GameWindow kanıtı.
4. SHM komutları eski MaximumController v4 GUI'siyle aynı.

---

## 6. SORUN GİDERME

| Belirti | Sebep | Çözüm |
|---|---|---|
| **HER KOMUTA `!! PYTHON HATASI`** (v1.5 saha bulgusu 6) | v1.5 hatası: bootstrap ~660 karaktere büyüdü ama eski üreticiler `char buf[256/512]` + `_snprintf` kullanıyordu → .cmd dosyaları satır ortasında kopuk Python kodu (255/511 byte) → SyntaxError. Kanıt: maxexec.log'taki byte boyutları + pyerr.log'daki kesik satırlar | **v1.6 kullan** — tüm üreticiler std::string (FIX-23). Ayrıca pyerr.log'da `EOL while scanning string literal` görüyorsan ve maxexec.log'ta EXEC satırı 255/511 byte diyorsa → kesinlikle v1.5'tesin, v1.6 DLL'i kopyala |
| **newchar/joblist çalışıyor ama selchar/mkchar/delchar HATASI** (v1.5 saha bulgusu) | Aynı kök neden: çalışanlar std::string üreticili, patlayanlar sabit tamponluydu | v1.6 (FIX-23) — yukarıdaki satır |
| **`AttributeError: 'module' object has no attribute 'selchar'`** (ya da herhangi bir yeni komut sessiz kalıyor) | **Diskteki pylib.py eski (v2.0) — DLL yeni** (saha testi 5: DLL v1.4 + pylib v2.0). Yeni komutlar pylib v3.0 ister | **v1.5 kullan: gömülü pylib otomatik yazar** (pylib_eski_*.py yedeği alınır). v1.4'te isen: bundle'daki yeni pylib.py'yi elle kopyala. v1.5'te bu durum ASLA sessiz kalamaz: açılışta `!! PYLIB ESI` uyarısı + komut hatasında `!! PYTHON HATASI — detay: pyerr` konsol satırı + `results\last_warning.txt` / `last_pyfail.txt` |
| **`ImportError: No module named maxlib`** (pyerr.log'da tekrar tekrar; status → "sonuc dosyasi yok") | **`C:\MaxExec\pylib.py` makinede yok** — v1.2 saha bulgusu: `load` sessiz IOError yedi, maxlib kurulmadı, her komut import hatası yedi. Zincir kendisi sağlamdı (py_probe.txt oluştu) | bundle zip'teki `pylib.py`'yi `C:\MaxExec` içine kopyala. **v1.3 otomatik yükler + dosya yoksa konsolda "pylib.py : YOK!!" der; komutlar kendini onarır** |
| **`load` komutu "dosya YOK" diyor** | Yanlış/eksik yol | `load C:/MaxExec/pylib.py` — ya da hiç yazma; v1.3 otomatik yükler |
| **C:\ yazma izni şüphesi** | — | **KANIT: py_probe.txt + alive.txt oyun süreci tarafından yazıldı ve göründü → C:\ sağlıklı, VirtualStore sorunu YOK.** Yine de istersen: `basedir.txt` içine `D:\MaxExec` yaz → tüm dosyalar oraya taşınır (pylib.py'yi de oraya koy!) |
| Python hatasını konsolda görmek | — | **`pyerr`** komutu — pyerr.log'un son 30 satırını döker. **v1.5: hata anında konsol da `!! PYTHON HATASI (dosya) — detay: pyerr` diye uyarır** + `results\last_pyfail.txt` + alive.txt'de `pyfail=` sayacı |
| **Komutlar kuyruğa yazılıyor ama hiçbir sonuç dosyası oluşmuyor** (v1.1 saha bulgusu) | v1.1 drenajı yalnız WndProc subclass + PostMessage'a dayanıyordu; subclass etkisizse zincir ölür | **v1.2+ kullan** — SetTimer yolu WndProc'tan bağımsız. Test: `results\py_probe.txt` oluşmalı (30 sn bekle) |
| `SCENE=?` dönüyor | mainStream frame-walk ile bulunamadı | `status` tekrar dene (frame yürüyüşü her çağrıda çalışır); oyunun intro ekranı değişmişse `raw` ile `import sys; print(sys.modules.keys())` incele |
| `selserver` "serverList.SelectItem YOK" | Bu ekranda değil ya da attr adı farklı | Önce `serverlist` yaz — aday attr'ları raporlar |
| **Konsol açılıyor AMA hiç yazı yazmıyor** (v1.0 hatası) | GUI process'in CRT stdout'u geçersiz handle ile başlar; `AllocConsole` sonrası CRT konsola yeniden bağlanmamıştı | **v1.2'ye güncelle** (freopen CONIN$/CONOUT$ + unbuffered fix). Her adım ayrıca `maxexec.log`'a yazılır |
| `VirtualAllocEx basarisiz: 8` (NOT_ENOUGH_MEMORY) | Oyun 32-bit adres alanı (2GB) pack dosyalarıyla dolu/parçalı | Oyunu ilk açtığın anda (login ekranı çıkınca hemen) inject et; cmd'yi Yönetici yap; olmazsa oyunu yeniden başlat |
| Konsol penceresi görünmüyor | Oyun tam ekran, konsol arkada | v1.1+ konsolu TOPMOST yapar. Alt+Tab ile "MaxExecutor" penceresini ara |
| **Konsol hiç açılmadı (headless mod)** | AllocConsole bazı koruma/ortamlarda başarısız olur | Sorun değil: `C:\MaxExec\queue\` klasörüne komutu elle `.cmd` dosyası olarak bırak — otomatik drenaj işler |
| Python kodum hata verdi, nerede göreceğim? | Python traceback'leri oyun içine gider | `load` sonrası tüm Python hataları `C:\MaxExec\pyerr.log`'da |
| `MaxInject.exe` "sureci bulunamadi" | Oyun kapalı ya da exe adı farklı | Oyunu aç; `MaxInject.exe <gercek-exe-adı>` |
| "OpenProcess basarisiz (5)" | Yönetici değil | cmd'yi Yönetici olarak aç |
| `python27.dll : YOK` | Oyun Python'u başlatmamış | Login ekranına kadar bekle; DLL 20 sn boyunca otomatik tekrar dener |
| `oyun penceresi: BULUNAMADI` | Pencere henüz yok | DLL 20 sn yeniden dener |
| `status` → "sonuc dosyasi yok" | pylib yüklü değil ya da hata yedi | `pyerr` komutuna bak; pylib.py dosyası yerinde mi? (v1.3 otomatik yükler) |
| `login` sonrası hiçbir şey olmuyor | Hatalı ID/şifre veya serverlist ekranı atlanmış | Önce `selserver` yap; sonra `last_login.txt` + `pyerr.log` + oyun popup'ı (OnLoginFailure: NOID/WRONGPWD/ALREADY...) |
| NPC'ler gelmiyor | Eski script alışkanlığı: çift giriş | `enter` TEK SEFER; `waitfor GameWindow 60` ile bekle |
| Oyunda lag/kasma | Çok sık komut | Drain 4 komut/mesaj sınırlı; `raw` spamı yapma |
| GIL hatası hâlâ geliyor | Başka eski DLL enjekte (Kaynak.cpp v1/v2/pythonSenderv1) | O DLL'leri KALDIRIR — MaxExecutor tek başına yeterli |

---

## 7. YENİDEN DERLEME (kaynağı değiştirirsen)

```bash
# Debian/Ubuntu'da: sudo apt install g++-mingw-w64-i686 (root yoksa: apt-get download + dpkg -x)
# ONCELIKLI: PLUSMAXGOD_PyScript.py degistirdiysen gomulu kopyayi yeniden uret (FIX-22):
python3 scripts/embed_pylib.py        # pylib_embedded.h yenilenir (kaynak: PLUSMAXGOD_PyScript.py)
i686-w64-mingw32-g++ -shared -static -static-libgcc -static-libstdc++ -O2 \
    -o bin/MaxExecutor.dll MaxExecutor.cpp -luser32 -lkernel32 -lgdi32

i686-w64-mingw32-g++ -static -static-libgcc -O2 \
    -o bin/MaxInject.exe MaxInject.cpp -luser32 -lkernel32

# dogrulama (ikisi de pei-i386 / i386 cikmali):
i686-w64-mingw32-objdump -f bin/MaxExecutor.dll | grep architecture
# root-less alternatif (oturum 12-13 yolu):
#   zig c++ -target x86-windows-gnu -O2 -shared MaxExecutor.cpp -o bin/MaxExecutor.dll
#   zig c++ -target x86-windows-gnu -O2 MaxInject.cpp -o bin/MaxInject.exe
```
Visual Studio kullanacaksan: x86 platform, DLL projesi, `/MT` (statik CRT), ek include yok.

---

## 8. TEST KONTROL LİSTESİ (kullanıcı tarafında)

- [ ] `MaxInject.exe` → konsol açıldı, `python27.dll : BULUNDU`
- [ ] `PLUSMAXGOD_PyScript.py : v4.1 (uyumlu)` ya da `GUNCELLENDI -> v4.1` satırı göründü
- [ ] 30 sn sonra `results\last_pylib_load.txt` VAR (oto-yükleme kanıtı)
- [ ] `status` → `SCENE=LoginWindow+ServerList` benzeri çıktı
- [ ] `login id pwd` → `waitfor SelectCharacterWindow 30` ile ekran geçişi
- [ ] `charlist` → `results/last_charlist.txt` dolu (5 slot, race/level/isim)
- [ ] `enter 0` → `waitfor GameWindow 60` → **NPC'ler görünüyor mu?**
- [ ] **v1.8 oyun-ici:** `stat` + `pos` + `inv 0` + `equip` + `skill` raporları dolu mu?
- [ ] **v1.8 hareket:** `goto <x> <y>` yürüdü mü? (tp'yi önce güvenli yerde dene)
- [ ] **v1.8 kesif:** `pyfiles` → `pydumpall` → `C:\MaxExec\dump\INDEX.txt` oluştu mu?
- [ ] **v1.8 katalog:** `plusquest` → `dump\PLUSQuest_live.txt` oluştu mu? (AI'ya gönderilecek)
- [ ] (yeni karakter) `empire` + `create` + hata takibi
