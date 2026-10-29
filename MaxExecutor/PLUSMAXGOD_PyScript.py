# -*- coding: utf-8 -*-
"""
===========================================================================
 PLUSMAXGOD_PyScript.py - MaxExecutor Ana-Thread Komut Kutuphanesi (v5.1)
 v5.1 DEGISIKLIKLER:
   * oto-pot (hp/mp otomatik iksir basma + oto-pot esyasi izlemesi)
     ozelligi ve ilgili tum komutlar TAMAMEN KALDIRILDI (kullanici istegi).
     Otomatik acilis dosyasi okuma/yazma davranisi da cikarildi.
 v5.0 DEGISIKLIKLER (saha testi 16 raporu - tumu kanitli):
   * slots COK-HUCRELI ESYA: bazi esyalar 2-3 hucre kaplar (kilic 1x3, zirh
     2x3). v4.9 her esyayi 1 slot saniyordu -> oyun 32 bos gosterirken biz 34
     diyorduk. Simdi item.GetItemSize ile (w,h) okunur, kaplanan hucreler
     sayilir ve haritada 'o' ile gosterilir (5 slot/satir - oyunun izgarasi).
     KANIT: edithack.py:751 'slot-5' kontrolu (5 sutun, yukseklik +5 adim) +
     GetItemSize 6 NightTown dosyasinda calisan desen.
   * sellall/selljunk v5.0: (1) KOK NEDEN - shop.IsOpen() flicker'i v4.9'da
     cur'u SIFIRLIYORDU -> sonsuz faz0<->faz1 ping-pongu ('5 dk sonra tekrar
     npcye tiklayip satmaya calisiyo'). Artik cur KORUNUR + flicker sayaci.
     (2) KARA LISTE: 2 dogrulama turunda da duran esya bir daha DENENMEZ,
     ATILAMAYAN/SATILAMAYAN olarak isim+boyut listesiyle raporlanir.
     (3) 120sn HARD DEADLINE. (4) bitince dukkan OTOMATIK KAPATILIR
     (net.SendShopEndPacket - ShopScanner.py:566 kaniti; 'kapatamiyom' bitti).
   * dropall v5.0: ayni kara liste + 120sn siniri + isimli KALAN raporu.
     NOT: sunucu BURST paketlerini yavas isleyebilir -> esyalar dongu
     bittikten sonra dakikalar icinde tek tek duser ('5 dk da bir atiyo'
     buydu); tekrar dropall yazmaya gerek yok, kalanlar raporlanir.
 v4.8 DEGISIKLIKLER (saha testi 14 dev raporu - tumu kanitli):
   * otp2 SUREKLI BASILI: 'bas cek degil' - SetPixelPosition sicramalari
     KALDIRILDI; karakter SetRotation ile hedefe donderilir, W+UP tusu
     basili KALIR (her tik yenilenir), varince otomatik birakilir.
     (GetDegree donus konvansiyonu: darealfreakbot/pasha37-levelbot)
   * slots SAYIM DUZELTMESI: TOPLAM = sekme x sekme-boyu (2x45=90; eski
     kod INVENTORY_SLOT_COUNT=168 diyordu) + 9 kolonlu slot HARITASI
     (#=esya .=bos E=efsunlu ?=okuma-hata) + okuma-hata sayaci +
     GetElk/GetGold yang yedegi.
   * selljunk/sellall YENI AKIS: (1) ONCE kanitli 1-arg paket
     net.SendShopSellPacket(slot) - m2k Inventorymanager + Taubuyer
     NightTown kaniti (v4.7 yanlislikla yeni 2-arg paketle basliyordu
     -> hic satmiyordu); (2) surekli NPC acma dongusu YOK - 1 tik +
     8sn sessiz bekleme, dukkan acilmazsa kendin tikla mesaji;
     (3) DURDUR: selljunk 0 / sellall 0 ('kapatamiyom' fix)
   * dropall DUZELTME: ONCE kanitli 1-arg net.SendItemDropPacket(slot)
     (m2k DropAllItems NightTown kaniti; v4.7'nin 2-arg New paketi bu
     sunucuda hic atmiyordu) + DURDUR: dropall 0 + 0-atilan teshisi
   * sell/drop [LIVE] SPAM biti: her 3sn'de bir ozet satiri (eski kodun
     'NPC dukkani aciliyor' firtinasi yok)
 v4.7 DEGISIKLIKLER (saha testi 13 dev raporu - tumu kanitli):
   * KALDIRILDI: speed/aspeed (sunucu tanimiyordu) + chchange/relogin
     (karakteri degistirmisti - kullanici istegi; sonra detayli yapilacak)
   * warp: LEGENDY YOLU - background.Destroy + Initialize + WarpTest
     (sahne YENIDEN yuklenir; LegendySF-V2 consolemodule 'warp' komutu
     birebir; bu istemcide background.WarpTest VAR - canli katalog)
   * otp -> otp1 (eski kanitli yontem) + otp2 YENI (atak yerine W tusu
     basili: player.SetSingleDIKKeyState(app.DIK_W, 1))
   * otpstop FIX: saldiri tusu artik MUTLAKA birakilir (yol ortasinda
     durdurunca BASILI kaliyordu - attackkeystate bug raporu)
   * YENI: slots (envanter doluluk %) | selljunk/sellall (NPC'ye sat;
     efsunlu ASLA satilmaz; m2k Inventorymanager + uiShop kaniti) |
     dropall (tek tek atma - bazi sunucular toplu atmayi reddeder)
   * _pack_read: sys.modules['pack'] DIREKT + __main__ pack_open
     (serverinfo.py dumplama dustu raporu); pydumpall: C modulleri
     API-STUB olarak yazilir (player.py/chr.py gercek API icerigi)
   * live.txt oturum basinda temizlenir (DLL acilisinda konsol eski
     [LIVE] balik satirlarini geri oynamiordu - kullanici raporu)
 v4.6 DEGISIKLIKLER (saha testi 12 dev raporu - tumu NightTown dump kanitli):
   * near: tip FILTRESI kalkti - metin tasi (tip=2) artik bulunur!
     (kagb-multihack kaniti: 0=MOB 2=METIN 6=OYUNCU)
   * speed/aspeed: 0.5sn DONGU (Crap_Levelbot yontemi - sunucu hizi
     surekli sifirlar, tek atis etkisizdi)
   * antifly: saldiri tusu DEFAULT DEGIL (1=kilit 2=+Güclü Beden
     efezgi 3=orijinal saldirili)
   * chchange/relogin: select ekranindan stream.SetLoginPhase()
     (networkModule.py oyun yolu - karakter ekraninda takilma bitti)
   * attr etiketleri: efsun 1-5 + 6./7. BONUS (efsunbotu kaniti)
   * YENI: warp (otp adim + SendCharacterPositionPacket) | antistun |
     antislow | combo (surekli vurus: chr.testSetComboType) |
     statdown (/stat-) |
     skillupui/statupui (oyunun kendi UI fonksiyonlari) |
     efsun <slot>|all (bonus efsun raporu)
 "PLUSMAXGOD" SURUMU - v4.4 tamami + v4.5 kok-neden onarimi
 v4.5 DEGISIKLIKLER (saha testi 11 "hatali sistem" raporu - KOK NEDEN):
   * v4.4 YUKLENEMIYORDU: yeni _NearScanWnd/_GoTakeWnd/_AntiFlyWnd
     siniflari ui_WindowBase tanimindan ONCE kullaniyordu -> import
     aninda NameError -> BootImport sessizce ESKI pylib.py v3.2'ye
     dustu -> itemscanall/morph/otp/speed/morphtarget/fakemount
     AttributeError + serverlist eski mesaji + near _my_vid hatasi.
     COZUM: ui_WindowBase tanimi siniflarin ustune tasindi + import ui
     korumali (ui yuklu degilse yedek taban).
   * fishtp kalintisi (oneshot / "tek atis bitti") tamamen temizlendi.
   * DLL v2.1 cifti: BootImport yukseltme denemesi oturum basina 1 kez;
     basarisizlik TRACEBACK ile results\last_pylib_fail.txt'e yazilir.
 (v4.4 icerigi aynen korundu)
===========================================================================
 v4.4 DEGISIKLIKLER (kullanici saha raporlari + NightTown dump + LegendySF
 Client/GameSource kanitlari):

   KALDIRILDI (kullanici istegi): fishdelay, fishswap, fishswapnow, fishtp
   YENI: morphtarget (hedef NPC/mob/oyuncuya donus) | cloneplayer (hedef
     oyuncuya donus) | fakemount (sahte binis - chr.MountHorse, skill SERBEST)
     | speed/aspeed (chr.SetMoveSpeed/SetAttackSpeed, max 1100!) | statup
     ('/stat ht|iq|st|dx') | skillup ('/skillup idx') | antifly 1/2 (kanit
     AntiFly.py: SetLoopMotion WAIT + SetAttackKeyState) | antiflyeffect
     (chrmgr.SetAffect) | itemfind (isimle esya arama) | iteminfo (tam proto)
     | attr/attrall (efsun okuma: player.GetItemAttribute) | useon
     (net.SendItemUseToItemPacket - efsun/5.attr/kostum) | efsunsw | gotake
     (esyaya yuru+topla)
   FIX: clone Z (GetPixelPosition UCLU (x,y,z) + GetMainCharacterPosition) +
     SAC (net.GetAccountCharacterSlotDataInteger ACCOUNT_CHARACTER_SLOT_HAIR)
   FIX: morph/spawn gorsel tazeleme (_visual_kick: Update/Deform+Hide/Show+
     WAIT) - 'zirh tak-cikar' artik gerekmiyor
   FIX: near (vid 1..2000 -> 1..50000 anlik + 0..4M arka plan tarama; bu
     sunucuda VID 20000+, eski tarama hicbir sey bulamiyordu)
   FIX: otp (saldiri tusu yol boyunca BASILI, varista birakilir; delay 50ms)
   FIX: relogin/chchange (net.Disconnect yerine net.ExitGame/LogOutGame -
     sunucu-driven faz gecisi; 'sahne degismiyo, her sey kayboluyor' bitti)
   FIX: konsol karisikligi (pylib_load artik kisa; C++ taraflari kilitli)
   FIX: itemscanall 50k kesme hatasi

 v4.3 DEGISIKLIKLER (saha testi 10 + LegendySF/Client tam kaynak analizi):

   SAHA TEZHISI (live.txt: 32 atis, 0 isirtma, 14 kacan - KOK NEDEN BULUNDU):
     * ISIRTMA (GC_REACT) Python'a HIC BIR CALLBACK GONDERMIYOR! Client
       kaynak (PythonNetworkStreamPhaseGame.cpp: FISHING_SUBHEADER_GC_REACT):
       sadece C++ SetFishEmoticon()+ReactFishing() cagirir. OnFishingNotify
       SADECE PredictFish() TRUE ise gelir = balik-zihni hapi (27610) varsa
       (fishing.cpp:374 AFFECT_FISH_MIND_PILL)! -> dongu isirtmayi HIC
       goremedi; her kacis olta-yemini SIFIRLADI (rod->SetSocket(2,0)) ->
       sonraki atis YEMSZIZ gitti -> 45sn bosa bekledi (alterne desen).
     * FIX-1: HAPI: fish baslarken envanterde 27610 varsa OTOMATIK kullan.
       Hapi ile HER isirtmada OnFishingNotify(isfish, balik-adi) gelir ->
       100% isirtma algisi + canli balik adi + ogrenme tablosu dogru calisir.
     * FIX-2: Kacis/yer-hata hook'unda dongu BEKLEMEZ - hemen pre'ye doner
       (yem tak -> at). 45sn kayip bitti.
     * FIX-3: yem takildiktan sonra (soket2>0) atis yapilir (baitwait).
     * Isirtma penceresi 6sn (event PASSES_PER_SEC(6)); isirtma 10-40sn.
     * fishswap <vnum> filtresi (fishswap 11499) + fishswapnow (aninda test).
     * fishtp: TEK ATIS (isinla->at->geri isinla->cek->durdur).
     * 400 birim su: compiled C++ (c_fFishingDistance, GetFishingRot 10'ar
       derece tarama) - PYTHON DEGISKENI YOK. Gerek de yok: sunucu su
       istemez (char.cpp CHARACTER::fishing -> sadece ATTR_BLOCK).
   OPTIMIZETP (otp): sunucu FUNC_MOVE paketinde mesafe>25m ise geri atar
     (input_main.cpp ENABLE_TP_SPEED_CHECK; kullanicinin saha raporu).
     otp = adim adim senkron isinlama (240px=24m adim + MoveToDestPosition).
   KLON: sac kopyala (probe) + clonemod (swap/takip).
   spawnscan: nonplayer.GetMonsterName(vnum) ile mob_proto taramasi -
     spawn 20016 gorunmez cunku race istemci mob_proto'sunda yok (kanit).
   itemscan: TAM liste C:\MaxExec\itemscan_full.txt (python dogrudan yazar,
     DLL sonuc-dosyasi limiti YOK) + itemscanall (1-99999 tam tarama).

 v4.2 DEGISIKLIKLER (saha testi 9 - "hepsi basarili, sadece serverlist hatali"
 + kullanici GOD MOD istek listesi sonrasi):

   SAHA KANITLARI (LegendySF-V2 kaynaklari + kullanici botlari + canli katalog):
     * serverlist hatasi KOK NEDEN: ServerList = "listbox2" -> ui.ListBar2
       sinifi; GetItemText METODU YOK (ui.py:3094-3274)! Isimler keyDict/
       textDict sozlugunde. v4.1 GetItemText cagirip 'isim okunamadi'
       basiyordu. v4.2 sozlugu dogrudan okur + kendi sonuc dosyasi.
     * BALIKCILIK TAM MEKANIK (LegendySF fishing.cpp - klasik mainline):
       - Cast -> sunucu 10-40sn rastgele bekler -> GC_REACT (isirtma!)
       - Isirtmada 6sn pencere: tepki ms = (simdi - hang_time)
       - Compute(): ms>6000 -> basarisiz; time_step=(ms+99)/200 (200ms kova)
       - BASARI = number(1,100) <= aFishingTime[tip][kova] -> GECECE TEPKI
         HER ZAMAN EN IYI DEGIL! tip0 balik kova 0-4'te %0, kova 13-15'te
         %30-80. tip2 balik ANINDA (%80 kova 5). tip3 = hep %100.
       - Sonra number(1, zorluk) <= olta-seviyesi (soket2+value0)
       - KACIRIRSAN (6sn asimi) olta-skilli SIFIRLANIR (SetSocket(2,0))!
       - Fish Mind (71072/UNIQUE_GROUP) -> daha iyi balik tablosu (prob_idx 2)
       -> v4.2 fish dongusu: ADAPTIF GECIKME OGRENICI (balik adina gore
          gecikme->basari tablosu tutar, C:\MaxExec\fish_learn.txt'de kalici)
     * CLIENT su kontrolu: InstanceBaseMotion.cpp GetFishingRot() - cast
       icin 400 birim icinde SU GEREKLI (10'ar derece tarama). Sunucu
       kontrolu YOK (char.cpp CHARACTER::fishing -> sadece ATTR_BLOCK).
       -> fishspot yolu: su kenarinda at, tp ile uzaklas, balik orada!
     * YER ITEMI TARAMASI: textTail.Pick(x, y) ekran-koordinat secici
       (kullanicinin pickupstealer.py + Itemstealer.py kaniti)
     * QUEST API: quest.GetQuestCount/GetQuestData/GetQuestLastTime
       (uicharacter.py:812-876 kaniti; GetQuestData 4'lu doner:
       ad, ikon, sayac-ad, sayac-deger)
     * SAHTE ITEME: player.SetItemData(slot, vnum, adet) + SetItemAttribute
       + SetItemMetinSocket (itemcreator.py CreateItem kaniti - HAYALET)
     * SAHTE INSTANCE/KLON/MORF: introselect.py MakeCharacter KANIT SIRASI:
       CreateInstance(vid) -> SelectInstance(vid) -> SetVirtualID ->
       SetNameString -> SetRace -> SetArmor -> SetHair -> SetMotionMode ->
       SetLoopMotion -> SetRotation -> Show. Butun 1-arg setterlar SECILI
       instance'a uygulanir (PythonCharacterModule.cpp: GetSelectedInstancePtr)!
       Demirci = race 20016 (npclist.txt).
     * SIMYA = Dragon Soul: player.DRAGON_SOUL_INVENTORY + GetItemIndex 2-arg
       (PythonPlayerModule.cpp:788: 1-arg VE 2-arg formlari var)

   YENI KOMUTLAR (28): unequip unequipall chchange relogin ground groundtake
   autotake quest fakeitem fakeclear clone unclone spawn morph unmorph
   setarmor setweapon simya ds itemscan fish fishstop fishdelay fishkeep
   fishswap fishspot fishstat fishtest canli

   v4.3 KOMUTLAR (10): fishtp fishswapnow otp optimizetp otpstop otpstep
   otpdelay clonemod spawnscan itemscanall

 v4.1 DEGISIKLIKLER (saha testi 8 - pydumpall 2 bayt sorunu sonrasi):
   Saha bulgusu: v4.0 pydumpall 144 hedefin 73'unu doktu (diskteki botlar)
   AMA oyunun KENDI modulleri (app/chr/player/game/ui/introLogin...) 2 bayt
   cikti. Kok nedeni: app.GetFileList bu istemcide SADECE DISK dosyalarini
   listeliyor (73'ü de kullanici botlari); oyun modulleri root PACK icinde;
   app.OpenTextFile pack dosyalarinda handle verip 0 SATIR donduruyor.

   YENI KANITLI OKUMA ZINCIRI (dump klasorunden cikan calisan botlarin
   kendi kodunda birebir kullanildigi GORULDU - GOD MOD kanit taramasi):
     1) pack.Exist(ad) + pack.Get(ad)      <- FileExtractor.py:407
                                            New_Levelbot.py:363
        "playersettingmodule.py" icerigini pack'ten STRING olarak okuyor!
     2) pack_open(ad, 'r').readlines()     <- edithack.py:888/911/939
                                            itemcreator.py:418/441/469
        pack icindeki item_list.txt'yi okuyor (diskte DEGIL!)
     3) app.OpenTextFile + GetTextFileLineCount + GetTextFileLine
        (cycu.py:92-105; SAHA TESTI: pack dosyalarinda 0 satir - disk
        dosyalarinda calisir, YEDEK olarak kalir)
     4) disk open (en son yedek)

   * _pack_read(ad)  : yukaridaki 4 katmanli zincir; (yontem, icerik) doner
   * _name_variants(): introLogin/intrologin/IntroLogin gibi buyuk-kucuk
     harf varyantlari + locale/ro/ui/ + UIScript/ yollari turenir
   * pydump v2       : pack-first zincir + varyant taramasi; yontem raporu
   * pydumpall v2    : hedef listesi ARTIK CANLI sys.modules'ten (130 modul)
     + import-probe + disk/GetFileList + UI script yollari (oyun log'unda
     gorulen locale/ro/ui/*.py + UIScript/*.py); INDEX'e yontem + byte
     kolonu; 0 byte -> 'BOS' isaretli (sahte OK yok)
   * pyfiles v2      : [6] pack API kesfi (dir(pack) + hasattr Exist/Get/
     pack_open) + GetFileList=disk-only saha notu + modul __file__ raporu
   * plusquest/pyscan: dokunulmadi (saha testi 8'de mukemmel calisti,
     PLUSQuest_live.txt 439KB canli katalog)

 v4.0 DEGISIKLIKLER (oturum 13 - "hepsi calisti" sonrasi GOD MOD genisleme):
   Diskteki dosya adi: pylib.py -> PLUSMAXGOD_PyScript.py (DLL v1.8 cifti;
   eski pylib.py hala YEDEK olarak kabul edilir - BootImport once yenisini
   dener, bulamazsa pylib.py'yi yukler ve surum guard'i uyari basar).

   A) OYUN-ICI KOMUTLAR (kanit: nighttown koleksiyonu 4000+ kullanim +
      cycu.py - kullanici ekosisteminde birebir dogrulanmis API'ler):
      stat()          : seviye/HP/SP/EXP/race/grup/empire/hiz raporu
                        (player.GetStatus + net.GetMainActorRace - cycu)
      pos()           : x/y/z + harita adi (chr.GetPixelPosition - cycu +
                        background.GetCurrentMapName - 34 kanitli kullanim)
      inv(page)       : envanter raporu (player.GetItemIndex 267 kanit +
                        player.INVENTORY_PAGE_SIZE sabiti 147 kanit +
                        item.SelectItem/GetItemName 300/171 kanit)
      equip()         : ekipman raporu (EQUIPMENT_BASE_INDEX slotlari)
      skill()         : beceri raporu (player.GetSkillLevel/GetSkillGrade/
                        IsSkillCoolTime + skill.GetSkillName - kanitli)
      near()          : yakin varlik taramasi VID sweep (chr.GetInstanceType
                        57 kanit + chr.GetNameByVID 52 kanit +
                        nonplayer.GetLevelByVID kanit)
      chat <mesaj>    : net.SendChatPacket (cycu + 117 kanit)
      whisper <k> <m> : net.SendWhisperPacket (9 kanit)
      ride/revive/logout/back : cycu-kanitli hizli eylemler
      zoom <mesafe>   : app.SetCameraMaxDistance (cycu + 13 kanit)
      use <slot>      : net.SendItemUsePacket(slot) (218 kanit!)
      pickup          : player.PickCloseItem (15 kanit)
      drop <slot> <n> : net.SendItemDropPacketNew (cycu; DESTRUKTIF!)
      goto <x> <y>    : chr.MoveToDestPosition(vid,x,y) YURUYUS (36 kanit)
      tp <x> <y>      : chr.SetPixelPosition(x,y) ISINLAMA (211 kanit!)
      key <DIK> <0/1> : player.SetSingleDIKKeyState (368 kanit!)
      attack <0/1>    : player.SetAttackKeyState (100 kanit)

   B) KESIF KOMUTLARI (eski_ai_sohbet'deki 5 yontem, GOD MOD ile dogrulanmis:
      app.GetFileList bu istemcide 0 kullanim - aday olarak denenir;
      app.OpenTextFile ise KANITLI dosya okuma yolu - 24 kanit + cycu):
      pyfiles         : 5 yontemle py dosyalarini bulur (app.GetFileList /
                        sys.modules / pkgutil / disk taramasi / import-probe)
      pydump <ad>     : tek py dosyasini dump\ klasorune doker
      pydumpall       : bulunan BUTUN py'leri dump\ klasorune + INDEX.txt
      pyscan <modul>  : modulun fonksiyonlarini argumanlariyla listeler
      plusquest       : yuklu TUM modulleri tarar -> dump\PLUSQuest_live.txt
                        (pyscanall takma adi ayni isi yapar)

 v3.2 DEGISIKLIKLER (saha testi 7 "enter takiliyor + sahte CREATE_FAILURE"):
   * enter(): UI START yolu ONCELIKLI - SelectSlot + StartGame()/startButton
     (MaximumPyScript_Merged_calisan yolu + kullanici dogrulamasi). Saha
     kaniti: DirectEnter YENI olusan karakterde server tarafindan reddediliyor
     (loading acilip login ekranina geri atiyor), eski karakterde calisiyor.
     DirectEnter artik sadece UI yolu bulunamazsa YEDEK.
   * mkchar(): paket yolu artik SADECE OLUSTUR butonu bulunamazsa yollanir.
     Kanit: cift paket (buton + direkt) -> 1 basari + 1 CREATE_FAILURE: 0
     ("0 karakter yaratilamaz") - karakter zaten olusmustu, 2. paket
     reddedildi. Sahte hata kokten biter.
   * enter(): UI yolu secildiginde DirectEnter CAGRILMAZ (RC12 cift-giris
     yasagi: UI StartGame paketi kendisi yollar, ustune bir de DirectEnter
     NPC yukleme hatasi yapar).
 v3.1 DEGISIKLIKLER (oturum 11 - saha testi 6 "PYTHON HATASI" sonrasi):
   * _write() artik raporlarini KONSOLA da basar ([CHARLIST]/[JOBLIST]/...
     etiketiyle). DLL v1.6 probe'u sys.stdout'u CONOUT$'a baglar; boylece
     charlist/joblist/newchar/mkchar/selchar/delchar cikislari KONSOLDA
     CANLI gorunur - results klasorune bakmak zorunda degilsin.
   * _log_game_error(): oyun hatasi (yanlis sifre vb.) aninda konsola da
     duser - [OYUN HATASI] satiri, lasterr yazmadan gorunur.
   * status(echo) parametresi: waitfor polling'i artik konsolu spam etmez.
   * lasterr DLL tarafindan pretty-print edildigi icin echo'suz yazar.
   * Konsola giden metinler ASCII'ye cekildi (CP857'de mojibake olmasin).
 v3.0 DEGISIKLIKLER (giris basarili sonrasi istekler - oturum 9):
   * OTO HATA IZLEME: LoginWindow.OnLoginFailure + SelectCharacterWindow
     OnCreateFailure/OnDeleteFailure/OnDeleteSuccess hook'lari (Python-seviye,
     kanitlanmis guvenli - LoginEventTracker/recorder v13-14 deseni).
     Yanlis sifre/arti kodlar results\last_error.txt'ye duser.
   * YENI KOMUTLAR:
       selchar <slot>     : karakter slotu sec (orn. 4. slot)
       newchar            : "karakter olustur" butonuna bas
       joblist            : sinif/cinsiyet tablosu + olusturma ekran durumu
       mkchar <ad> <race> : UI akisi - sinif gez + cinsiyet + isim + OLUSTUR
       empirelist         : bayrak listesi + mevcut empire
       empireui <1-3>     : bayrak sec + ILERLE (UI yolu - kanitlanmis)
       delchar <slot>     : karakter sil butonuna bas + kod dialogu ac
       delcode <kod>      : silme kodunu yaz + ONAYLA
   * login() raporuna "lasterr" ipucu eklendi.
 v2.0 DEGISIKLIKLER (saha testi 25.10 sonrasi):
   * mainStream artik FRAME YURUYUSU ile bulunur (sys._current_frames).
     __main__.mainStream bu client'ta YOK - calisan script
     (MaximumPyScript_Merged_calisan) bunu kanitladi; ayni teknik.
   * SAHNE: LoginWindow + serverBoard -> 'LoginWindow+ServerList'
     (server isimleri listbox + CH listesi + OK butonu ekran!)
   * YENI selserver(srv, ch): serverList.SelectItem + channelList.SelectItem
     + serverSelectButton.CallEvent  (calisan scriptin birebir yolu)
   * login: UI YOLU ONCELIKLI (idEditLine/pwdEditLine/loginButton.CallEvent),
     yoksa paket yolu (net.SetLoginInfo + baglanti)
   * enter: UI senkron (SelectSlot) + TEK DirectEnter (RC12 yasagi)
 GIL NOTU: butun fonksiyonlar ana thread'de (drain icinde) calisir;
   sadece dict/attr okumalari + dosya yazimi var; gc.get_objects YOK.
   HOOK NOTU: Python-seviye fonksiyon atamasi (class attr) - C++ tarafinda
   hook YOK; bu desen LoginEventTracker_GILSafe + recorder v13/v14'te
   saha-kanitli (0 ms GIL, sadece atama).
===========================================================================
"""

import sys
import time
import os

RESULT_DIR = r'C:\MaxExec\results'
DUMP_DIR   = r'C:\MaxExec\dump'   # v4.0: py dump + PLUSQuest_live buraya

# SURUM ISARETI - DLL v1.8 bunu okur (FIX-19). PLUSMAXGOD_PyScript.py
# degistirmeden bu satiri silme/degistirme! Eski pylib (v3.x) major 3
# oldugu icin DLL v1.8 acilista KOSKOCA uyar basar.
PYLIB_VERSION = '5.2'

RACE_TABLE = {
    0: ('Warrior', 'E'), 1: ('Ninja', 'K'), 2: ('Sura', 'E'), 3: ('Shaman', 'K'),
    4: ('Warrior', 'K'), 5: ('Ninja', 'E'), 6: ('Sura', 'K'), 7: ('Shaman', 'E'),
    8: ('Wolfman', 'E'),
}
JOB_NAMES = {0: 'Warrior', 1: 'Ninja', 2: 'Sura', 3: 'Shaman', 4: 'Wolfman'}
SLOT_COUNT = 5

# olusturma ekrani donusumleri (MaximumPyScript_Merged_calisan'dan - kanitli)
EMPIRE_NAMES    = {0: 'None', 1: 'Shinsoo', 2: 'Chunjo', 3: 'Jinno'}
RACE_TO_SLOT    = {0: 0, 4: 0, 1: 1, 5: 1, 2: 2, 6: 2, 3: 3, 7: 3, 8: 0}
RACE_TO_GENDER  = {0: 0, 1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0, 8: 0}

# oyun hata kodlari (LoginEventTracker_GILSafe'dan - client'in kendi kodlari)
LOGIN_FAILURE_CODES = {
    'ALREADY':  'Hesap zaten giris yapmis',   'NOID':     'Boyle bir hesap yok',
    'WRONGPWD': 'Yanlis sifre',               'FULL':     'Server dolu',
    'SHUTDOWN': 'Server kapali/bakimda',      'REPAIR':   'Hesap tamir asamasinda',
    'BLOCK':    'Hesap engellendi',           'QUIT':     'Cok fazla hatali deneme',
    'BESAMEKEY':'Cift login anahtari',        'NOTAVAIL': 'Hesap kullanilamaz',
    'NOBILL':   'Abonelik/bakiye yok',        'BLKLOGIN': 'Giris engellendi',
    'WEBBLK':   'Web uzerinden engellendi',   'BADSCLID': 'Yanlis sosyal ID',
    'AGELIMIT': 'Yas/saat sinirlamasi',       'VERSION':  'Client versiyon uyumsuz',
}
CREATE_FAIL_CODES = {0: 'karakter yaratilamaz', 1: 'isim zaten mevcut'}

# ---------------------------------------------------------------------------
# yardimcilar
# ---------------------------------------------------------------------------
def _res_name(name):
    if not os.path.isdir(RESULT_DIR):
        try:
            os.makedirs(RESULT_DIR)
        except:
            pass
    return os.path.join(RESULT_DIR, 'last_%s.txt' % name)

def _write(name, text, echo=True):
    """Sonucu results\last_<ad>.txt'ye yazar; echo=True ise KONSOLA da basar.
    (DLL v1.6 probe'u sys.stdout'u CONOUT$'a baglayinca canli gorunur -
    FIX-28. Yazma/yazdirma hatalari yutulur, komut zinciri bozulmaz.)"""
    try:
        f = open(_res_name(name), 'w')
        f.write(text)
        f.close()
    except:
        pass
    if echo:
        try:
            _ls = text.rstrip('\n').split('\n')
            sys.stdout.write('[%s] %s\n' % (name.upper(), _ls[0]))
            for _l in _ls[1:]:
                sys.stdout.write('%s\n' % _l)
        except:
            pass

def _fmt_error(e):
    return '%s: %s' % (type(e).__name__, str(e))

def _dump_name(name):
    """v4.0: dump klasoru yolu (olusturur). py dump + PLUSQuest_live buraya."""
    if not os.path.isdir(DUMP_DIR):
        try:
            os.makedirs(DUMP_DIR)
        except:
            pass
    return os.path.join(DUMP_DIR, name)

def _ingame():
    """v4.0: oyunda miyiz? (cycu.py kanitli desen: GetPixelPosition 'None'
    donmuyorsa ana aktor var demektir). Menulerde/loading'de False."""
    try:
        import net, chr
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            return False
        if not vid or vid <= 0:
            return False
        p = chr.GetPixelPosition(vid)
        if p is None or str(p) == 'None':
            return False
        try:
            if len(p) < 2:
                return False
        except:
            return False
        return True
    except:
        return False

# ---------------------------------------------------------------------------
# OTO HATA IZLEME - oyun hatalarini results\last_error.txt'ye dusurur
# (LoginEventTracker_GILSafe + recorder v13/v14'te saha-kanitli desen)
# ---------------------------------------------------------------------------
_HOOKS_OK = []

def _log_game_error(kind, detail):
    try:
        f = open(_res_name('error'), 'a')
        f.write('[%s] %s: %s\n' % (time.strftime('%H:%M:%S'), kind, detail))
        f.close()
    except:
        pass
    # v3.1: canli bildirim - hata olur olmaz konsola duser (lasterr'siz)
    try:
        sys.stdout.write('[OYUN HATASI] %s: %s\n' % (kind, detail))
    except:
        pass

def _install_error_hooks():
    """Python-seviye class hook'lari (idempotent - _mx_hooked bayragi).
    Kurulamayan modul varsa sessiz gecer; status() her cagrida tekrar dener."""
    try:
        # 1) LoginWindow.OnLoginFailure(error) - yanlis sifre vb.
        intro = sys.modules.get('introLogin', None) or sys.modules.get('intrologin', None)
        if intro is not None:
            LW = getattr(intro, 'LoginWindow', None)
            orig = getattr(LW, 'OnLoginFailure', None) if LW is not None else None
            if orig is not None and not getattr(orig, '_mx_hooked', False):
                def _h_login_fail(self_lw, *a, **kw):
                    try:
                        code = a[0] if a else '?'
                        _log_game_error('LOGIN_FAILURE',
                                        '%s (%s)' % (code, LOGIN_FAILURE_CODES.get(code, 'bilinmeyen')))
                    except:
                        pass
                    return orig(self_lw, *a, **kw)
                _h_login_fail._mx_hooked = True
                _h_login_fail._mx_orig = orig
                LW.OnLoginFailure = _h_login_fail
                _HOOKS_OK.append('OnLoginFailure')
        # 2) SelectCharacterWindow create/delete sonuclari
        isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
        if isel is not None:
            SW = getattr(isel, 'SelectCharacterWindow', None)
            if SW is not None:
                for mname, kind, mtable in (
                        ('OnCreateFailure', 'CREATE_FAILURE', CREATE_FAIL_CODES),
                        ('OnDeleteFailure', 'DELETE_FAILURE', None),
                        ('OnDeleteSuccess', 'DELETE_SUCCESS', None)):
                    orig = getattr(SW, mname, None)
                    if orig is None or getattr(orig, '_mx_hooked', False):
                        continue
                    def _mk(orig=orig, mname=mname, kind=kind, mtable=mtable):
                        def _h(self_sw, *a, **kw):
                            try:
                                code = a[0] if a else ''
                                desc = mtable.get(code, '') if mtable else ''
                                _log_game_error(kind, '%s %s' % (code, desc))
                            except:
                                pass
                            return orig(self_sw, *a, **kw)
                        _h._mx_hooked = True
                        _h._mx_orig = orig
                        return _h
                    try:
                        setattr(SW, mname, _mk())
                        _HOOKS_OK.append(mname)
                    except:
                        pass
    except:
        pass

def lasterr_text():
    """last_error.txt icerigi (DLL komutu bunu okur; pylib yedek yazar)."""
    try:
        f = open(_res_name('error'), 'r')
        data = f.read()
        f.close()
        return data if data.strip() else 'henuz oyun hatasi yakalanmadi\n'
    except:
        return 'henuz oyun hatasi yaklanmadi\n'

def lasterr():
    # v3.1: echo'suz - DLL komutu last_error.txt'yi zaten pretty-print eder
    _write('lasterr', lasterr_text(), echo=False)

# ---------------------------------------------------------------------------
# mainStream - FRAME YURUYUSU (calisan script teknigi, hooksuz)
# ---------------------------------------------------------------------------
_MS_CACHE = None

def _find_ms_from_frames():
    """sys._current_frames() ile mainStream local'ini tara (~0.05ms GIL)."""
    global _MS_CACHE
    if _MS_CACHE is not None:
        return _MS_CACHE
    try:
        frames = sys._current_frames()
    except AttributeError:
        return None
    for tid in frames:
        f = frames[tid]
        depth = 0
        while f is not None and depth < 30:
            try:
                fl = f.f_locals
            except:
                break
            for nm in ('mainStream', 'stream', 'main_stream', 'appStream'):
                ms = fl.get(nm)
                if ms is not None and hasattr(ms, 'curPhaseWindow'):
                    _MS_CACHE = ms
                    return ms
            try:
                f = f.f_back
            except:
                break
            depth += 1
    return None

def _get_ms():
    return _find_ms_from_frames()

# ---------------------------------------------------------------------------
# sahne cozumleme (hooksuz - tip adi + attr okumasi)
# ---------------------------------------------------------------------------
def _phase_window():
    ms = _get_ms()
    if ms is None:
        return None, None
    for attr in ('curPhaseWindow', 'phaseWindow', 'curWindow'):
        try:
            pw = getattr(ms, attr, None)
        except:
            pw = None
        if pw is not None and pw != 0:
            return ms, pw
    return ms, None

def _scene_name():
    """'LoginWindow+ServerList' / 'LoginWindow' / 'SelectCharacterWindow' /
    'CreateCharacterWindow' / 'SelectEmpireWindow' / 'LoadingWindow' /
    'GameWindow' / '?'"""
    ms, pw = _phase_window()
    if pw is None:
        # yedek: baglanti varsa loading/game varsay
        try:
            import net
            if net.IsConnect():
                if sys.modules.get('game') is not None:
                    return 'GameWindow'
                return 'LoadingWindow'
        except:
            pass
        return '?'
    try:
        tn = type(pw).__name__
    except:
        return '?'
    if tn == 'LoginWindow':
        # serverBoard/serverList varsa BU EKRAN server listesi (kullanici: listbox+OK)
        for sb in ('serverBoard', 'serverList', 'channelList'):
            if getattr(pw, sb, None) is not None:
                return 'LoginWindow+ServerList'
        return 'LoginWindow'
    if tn == 'LogoWindow':
        return 'LoginWindow'
    return tn

def _pw_by_type(*tnames):
    """sahne penceresini tip adiyla getir (None olabilir)."""
    ms, pw = _phase_window()
    if pw is None:
        return None
    try:
        if type(pw).__name__ in tnames:
            return pw
    except:
        pass
    return None

# ---------------------------------------------------------------------------
# 1) SERVERLIST v2 - SAHA TESTI 9 KOK NEDENI: ServerList = "listbox2" ->
#    ui.ListBar2 sinifi; GetItemText METODU YOK (ui.py:3094-3274, keyDict/
#    textDict sozlugunde tutar). v4.1 'isim okunamadi' basiyordu.
#    v4.2: sozlugun kendisini okur + KENDI sonuc dosyasi (last_serverlist.txt;
#    v4.1'de selserver ayni dosyaya yazip uzerine basiyordu).
# ---------------------------------------------------------------------------
def _listbox_dump(prefix, lb, lines):
    """ui.ListBox/ListBar2 icerigini her yoldan soyler (GetItemText YOK!)."""
    n = -1
    try:
        n = int(lb.GetItemCount())
    except:
        pass
    lines.append('%s: adedi=%s sinif=%s' % (prefix, str(n), type(lb).__name__))
    sel = None
    try:
        sel = lb.GetSelectedItem()
        lines.append('%s: secili=%s' % (prefix, str(sel)))
    except:
        pass
    # YOL A: textDict sozlugu (ui.ListBox: textDict[i] = metin)
    got = 0
    try:
        td = getattr(lb, 'textDict', None)
        if td and len(td) > 0:
            for k in sorted(td.keys()):
                try:
                    lines.append('  %s[%s] %s' % (prefix, str(k), str(td[k])))
                    got += 1
                    if got >= 40:
                        lines.append('  ... (40+ satir kesildi)')
                        break
                except:
                    pass
    except:
        pass
    # YOL B: keyDict + itemList yedegi
    if got == 0:
        try:
            kd = getattr(lb, 'keyDict', None)
            if kd and len(kd) > 0:
                for k in sorted(kd.keys()):
                    try:
                        lines.append('  %s[%s] %s' % (prefix, str(k), str(kd[k])))
                        got += 1
                        if got >= 40:
                            break
                    except:
                        pass
        except:
            pass
    if got == 0:
        try:
            il = getattr(lb, 'itemList', None)
            if il and len(il) > 0:
                for i, it in enumerate(il[:40]):
                    lines.append('  %s[%d] %s' % (prefix, i, str(it)))
                got = len(il)
        except:
            pass
    if got == 0:
        lines.append('  %s: (sozluk/liste bos - once server gorunmeli)' % prefix)
    return n

def serverlist():
    try:
        pw = _pw_by_type('LoginWindow')
        if pw is None:
            _write('serverlist', 'HATA: LoginWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        lines = ['SCENE=%s' % _scene_name()]
        sl = getattr(pw, 'serverList', None)
        cl = getattr(pw, 'channelList', None)
        if sl is None and cl is None:
            lines.append('serverList/channelList attr YOK! LoginWindow adaylari:')
            for a in dir(pw):
                if 'erver' in a or 'hannel' in a or 'ist' in a:
                    lines.append('  aday attr: %s = %s' % (a, type(getattr(pw, a)).__name__))
        else:
            if sl is not None:
                _listbox_dump('server', sl, lines)
            else:
                lines.append('server: serverList attr YOK')
            if cl is not None:
                _listbox_dump('channel', cl, lines)
            else:
                lines.append('channel: channelList attr YOK (server secilince dolar)')
            lines.append('---')
            lines.append('secme: selserver <server> <ch> (orn. selserver 0 0)')
        _write('serverlist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('serverlist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 2) SELSERVER - server+CH sec, OK butonuna bas (calisan scriptin yolu)
# ---------------------------------------------------------------------------
# v5.2: kimlik hatirla (chchange/relogin bunlari kullanir) + C:\MaxExec\login.dat
# v5.2 YENI: 'third' alani (bazi serverlar 3. editline ister: PIN/ID/guard code)
_SAVE = {'srv': 0, 'ch': 0, 'id': '', 'pwd': '', 'slot': 0, 'third': ''}

def _save_login_file():
    try:
        f = open(r'C:\MaxExec\login.dat', 'w')
        f.write('%s\t%s\t%d\t%d\t%d\t%s\n' % (_SAVE['id'], _SAVE['pwd'], _SAVE['srv'], _SAVE['ch'], _SAVE['slot'], _SAVE.get('third', '')))
        f.close()
    except:
        pass

def _load_login_file():
    try:
        f = open(r'C:\MaxExec\login.dat', 'r')
        p = f.read().strip().split('\t')
        f.close()
        if len(p) >= 3:
            _SAVE['id'] = p[0]; _SAVE['pwd'] = p[1]
            _SAVE['srv'] = int(p[2]) if len(p) > 2 and p[2].lstrip('-').isdigit() else 0
            _SAVE['ch'] = int(p[3]) if len(p) > 3 and p[3].lstrip('-').isdigit() else 0
            _SAVE['slot'] = int(p[4]) if len(p) > 4 and p[4].lstrip('-').isdigit() else 0
            _SAVE['third'] = p[5] if len(p) > 5 else ''
    except:
        pass

# ---------------------------------------------------------------------------
# 2a) UNIVERSAL UI YARDIMCILARI (v5.2 - GitHub 28-client arastirmasi sonucu)
# ---------------------------------------------------------------------------
# Arastirma kanitlari (RESEARCH.md): resmi 2014 akisi (idEditLine/pwdEditLine/
# serverList/channelList/serverSelectButton) - m2dev-client, Lead, Baseline,
# battal34, TurkMMO-MS5.8 | Marty 5.3 akisi (serverList YOK, channelButton
# dict, pw.Connect(id,pwd)) - AdmKojuro | eski katman (authSocket.SetLoginInfo,
# info['channel']) - N2Play | coklu-hesap slotu (id_editline_s, autoLogin(idx))
# - reign2 | PIN 3. alani (pin_edit_line) - proyecto-metin.
# SONUC: tek bir attr adi YOK - aday listeleri + GetChild yolu + dir() taramasi
# sart. Asagidaki yardimcilar 5 mimariyi de kapsar.

_LOGIN_ID_NAMES = ('idEditLine', 'id_editline', 'idEditline', 'EditLine_ID',
                   'userIdEditLine', 'idEditLineBox', 'userId')
_LOGIN_PWD_NAMES = ('pwdEditLine', 'pwd_editline', 'pwdEditline', 'EditLine_PWD',
                    'passwordEditLine', 'passEditLine', 'pwdEditLineBox')
_LOGIN_BTN_NAMES = ('loginButton', 'LoginButton', 'login_connectButton',
                    'loginOKButton', 'btnLogin', 'connectLoginButton')
_SERVERLIST_NAMES = ('serverList', 'ServerList', 'serverListBox')
_CHLIST_NAMES = ('channelList', 'ChannelList', 'channelListBox')
_REGIONLIST_NAMES = ('regionList', 'RegionList', 'regionListBox')
_OKBTN_NAMES = ('serverSelectButton', 'ServerSelectButton', 'serverInitButton',
                'serverOKButton', 'serverGoButton', 'selectConnectButton')

def _child_by_names(pw, names):
    """attr yolu -> GetChild yolu -> dir() gevsek tarama. Donduren:
    (bulunan_ad, nesne, yol) | (None, None, None)."""
    if pw is None:
        return None, None, None
    # YOL 1: dogrudan attr
    for nm in names:
        try:
            v = getattr(pw, nm, None)
            if v is not None:
                return nm, v, 'attr'
        except:
            pass
    # YOL 2: GetChild (uiscript adi ile - clientlarin cogunda calisir)
    for nm in names:
        try:
            if hasattr(pw, 'GetChild'):
                v = pw.GetChild(nm)
                if v is not None:
                    return nm, v, 'GetChild'
        except:
            pass
    # YOL 3: dir() gevsek eslesme (ad farklilari: idEditLine2, serverListBoxEx...)
    try:
        for a in dir(pw):
            la = a.lower()
            for nm in names:
                ln = nm.lower()
                if la == ln or (len(ln) > 5 and ln in la):
                    try:
                        v = getattr(pw, a, None)
                    except:
                        continue
                    if v is not None:
                        return a, v, 'tarama'
    except:
        pass
    return None, None, None

def _scan_editlines(pw):
    """LoginWindow'daki TUM editline'lar: [(attr, nesne), ...] (GetText olanlar)."""
    found = []
    seen = {}
    if pw is None:
        return found
    try:
        for a in dir(pw):
            la = a.lower()
            if 'editline' in la or 'edit_line' in la or la == 'pin':
                try:
                    v = getattr(pw, a, None)
                except:
                    continue
                if v is None or not hasattr(v, 'GetText'):
                    continue
                if id(v) in seen:
                    continue
                seen[id(v)] = 1
                found.append((a, v))
    except:
        pass
    # GetChild yolu: bilinen uiscript editline adlari (attr'a atanmamis olabilir)
    for nm in ('EditLine_ID', 'EditLine_PWD', 'id_editline', 'pwd_editline',
               'idEditLine', 'pwdEditLine', 'pin_editline', 'editline_pin',
               'connect_editline', 'guardcode'):
        try:
            if hasattr(pw, 'GetChild'):
                v = pw.GetChild(nm)
                if v is not None and hasattr(v, 'GetText') and id(v) not in seen:
                    seen[id(v)] = 1
                    found.append(('GetChild:' + nm, v))
        except:
            pass
    return found

def _classify_editlines(pw):
    """Editline'lari rolune gore ayirir: (id_t, pwd_t, third_list, tumu).
    id_t/pwd_t: (ad, nesne) | None. third_list: 3. alan adaylari."""
    els = _scan_editlines(pw)
    id_t = None; pwd_t = None; used = {}
    # tur 1: kesin adlar
    for a, v in els:
        la = a.lower().replace('getchild:', '')
        if id_t is None and ('ideditline' in la or 'id_editline' in la or
                             la.endswith('_id') or 'userid' in la):
            id_t = (a, v); used[id(v)] = 1
        elif pwd_t is None and ('pwd' in la or 'pass' in la):
            pwd_t = (a, v); used[id(v)] = 1
    # tur 2: gevsek (id/user iceren - pwd olmayan)
    if id_t is None:
        for a, v in els:
            if id(v) in used:
                continue
            la = a.lower()
            if 'pwd' not in la and 'pass' not in la and ('id' in la or 'user' in la or 'pin' in la):
                id_t = (a, v); used[id(v)] = 1
                break
    if pwd_t is None:
        for a, v in els:
            if id(v) in used:
                continue
            pwd_t = (a, v); used[id(v)] = 1
            break
    third = [(a, v) for a, v in els if id(v) not in used]
    return id_t, pwd_t, third, els

def _set_editline(el, text):
    """EditLine.SetText guvenli cagri (bazi clientlarda SetTextF/ime farklari)."""
    try:
        el.SetText(text)
        return 'SetText'
    except:
        pass
    try:
        el.SetTextF(text)
        return 'SetTextF'
    except:
        pass
    try:
        el.InsertIntoCurrentLine(text)
        return 'Insert'
    except:
        pass
    return None

def _press_button(btn):
    """Buton tetikleme: CallEvent -> Event -> Down (client farklilari icin)."""
    for m in ('CallEvent', 'Event', 'Down'):
        if hasattr(btn, m):
            try:
                getattr(btn, m)()
                return m
            except:
                pass
    return None

# ---------------------------------------------------------------------------
# 2b) SELSERVER UNIVERSAL (v5.2) - 3 mimari destekler:
#     (1) listbox'li (resmi 2014: serverList+channelList+serverSelectButton)
#     (2) Marty 5.3 tarzi (serverList YOK, channelButton dict + pw.SetChannel)
#     (3) coklu bolge (regionList + REGION_DICT)
#     ok=0 verilirse OK butonuna basmaz (bazi serverlarda OK yok/kullanilmaz)
# ---------------------------------------------------------------------------
def selserver(srv, ch, ok=1):
    try:
        srv = int(srv); ch = int(ch)
        _SAVE['srv'] = srv; _SAVE['ch'] = ch
        _save_login_file()
        pw = _pw_by_type('LoginWindow')
        if pw is None:
            _write('server', 'HATA: LoginWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        ok_pressed = False
        # (0) coklu bolge clientlari: region listesi (srv index'i BOLGE olabilir)
        rn, rl, ry = _child_by_names(pw, _REGIONLIST_NAMES)
        if rl is not None and hasattr(rl, 'SelectItem'):
            try:
                cnt = 0
                try:
                    cnt = int(rl.GetItemCount())
                except:
                    pass
                if cnt > 1:
                    rl.SelectItem(srv)
                    log.append('OK: regionList.SelectItem(%d) [coklu-bolge, %d bolge]' % (srv, cnt))
                    time.sleep(0.3)
                    srv = 0  # bolge secildi; server index'i sifirdan baslar
            except Exception, e0:
                log.append('UYARI: regionList secilemedi (%s)' % _fmt_error(e0))
        # (1) resmi 2014 listbox yolu
        sn, sl, sy = _child_by_names(pw, _SERVERLIST_NAMES)
        if sl is not None and hasattr(sl, 'SelectItem'):
            try:
                sl.SelectItem(srv)
                log.append('OK: %s.SelectItem(%d) [%s]' % (str(sn), srv, sy))
                time.sleep(0.3)
            except Exception, e1:
                log.append('UYARI: server secilemedi (%s)' % _fmt_error(e1))
        cn, cl, cy = _child_by_names(pw, _CHLIST_NAMES)
        if cl is not None and hasattr(cl, 'SelectItem'):
            try:
                cl.SelectItem(ch)
                log.append('OK: %s.SelectItem(%d) [%s]' % (str(cn), ch, cy))
                time.sleep(0.3)
            except Exception, e2:
                log.append('UYARI: channel secilemedi (%s)' % _fmt_error(e2))
        elif cl is None:
            # (2) Marty 5.3 tarzi: channelButton dict (ch -> buton)
            cb = getattr(pw, 'channelButton', None)
            picked = None
            if cb is not None:
                try:
                    items = list(cb.items())
                    for k, b in items:
                        if int(k) == ch:
                            picked = b
                            break
                    if picked is None:
                        # dict anahtar 1'den mi basliyor? (ch=0 -> ilk buton)
                        if ch == 0 and len(items) > 0:
                            picked = sorted(items, key=lambda kv: int(kv[0]))[0][1]
                except Exception, e3:
                    log.append('UYARI: channelButton dict okunamadi (%s)' % _fmt_error(e3))
            if picked is not None:
                m = _press_button(picked)
                if m:
                    log.append('OK: channelButton[%d].%s() [Marty buton tarzi]' % (ch, m))
                else:
                    log.append('UYARI: channelButton[%d] tetiklenemedi' % ch)
            elif hasattr(pw, 'SetChannel'):
                try:
                    pw.SetChannel(ch)
                    log.append('OK: pw.SetChannel(%d) [Marty metodu]' % ch)
                except Exception, e4:
                    log.append('UYARI: pw.SetChannel calismadi (%s)' % _fmt_error(e4))
            else:
                log.append('UYARI: channelList YOK - TEK-SERVER/Tek-CH modu olabilir (ch index kullanilmiyor)')
        # (3) OK butonu (ok parametresi)
        if int(ok):
            on_, btn, by = _child_by_names(pw, _OKBTN_NAMES)
            if btn is None:
                # gevsek tarama: ...Select...Button
                try:
                    for a in dir(pw):
                        if 'elect' in a and 'utton' in a:
                            btn = getattr(pw, a, None)
                            if btn is not None:
                                on_ = a; by = 'tarama'
                                break
                except:
                    pass
            if btn is not None and hasattr(btn, 'CallEvent'):
                try:
                    btn.CallEvent()
                    ok_pressed = True
                    log.append('OK: %s.CallEvent() [%s] -> server board onaylandi' % (str(on_), by))
                except Exception, e5:
                    log.append('UYARI: OK butonu basilamadi (%s)' % _fmt_error(e5))
            else:
                log.append('UYARI: OK butonu YOK - bazi clientlarda (Marty 5.3) OK zaten yok, login direkt baglanir')
        else:
            log.append('ok=0: OK butonuna basilMAdi (kullanici istegi)')
        _write('server', '\n'.join(log) + '\n')
    except Exception, e:
        _write('server', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 3) LOGIN UNIVERSAL (v5.2) - 3 yol sirali:
#    YOL A: UI - id/pwd/3.alan editline + login butonu (5 mimariyi kapsayan
#           aday taramasi; 3. alan varsa VE third verildiyse doldurulur,
#           verilmese bile raporlanir)
#    YOL B: pw.Connect(id, pwd) - resmi 2014 + Marty 5.3 class metodu
#    YOL C: paket - stream/net.SetLoginInfo + Connect (authSocket yedegi)
# ---------------------------------------------------------------------------
def login(user, pwd, third=None):
    try:
        _SAVE['id'] = str(user); _SAVE['pwd'] = str(pwd)
        if third is not None:
            _SAVE['third'] = str(third)
        _save_login_file()
        log = ['SCENE=%s' % _scene_name()]
        pw = _pw_by_type('LoginWindow')
        ui_ok = False
        if pw is not None:
            # --- YOL A: editline taramasi (attr + GetChild + dir taramasi)
            id_t, pwd_t, third_t, els = _classify_editlines(pw)
            if id_t is not None and pwd_t is not None:
                try:
                    m1 = _set_editline(id_t[1], user)
                    m2 = _set_editline(pwd_t[1], pwd)
                    log.append('OK: id alan dolduruldu (%s via %s)' % (id_t[0], m1))
                    log.append('OK: pwd alan dolduruldu (%s via %s)' % (pwd_t[0], m2))
                    if third_t:
                        t0 = third_t[0]
                        log.append('BILGI: 3. editline algilandi: %s (tip: %s)' % (t0[0], type(t0[1]).__name__))
                        if third is not None and str(third) != '':
                            m3 = _set_editline(t0[1], str(third))
                            if m3:
                                log.append('OK: 3. alan dolduruldu (%s via %s) = "%s"' % (t0[0], m3, str(third)))
                            else:
                                log.append('UYARI: 3. alan doldurulamadi (SetText yok)')
                        else:
                            log.append('UYARI: 3. alan DOLDURULMADI - server istiyorsa login <id> <pwd> <3.alan> dene')
                    time.sleep(0.3)
                except Exception, ef:
                    log.append('UYARI: alanlar doldurulamadi (%s)' % _fmt_error(ef))
                # login butonu (coklu aday)
                bn, btn, by = _child_by_names(pw, _LOGIN_BTN_NAMES)
                if btn is not None and hasattr(btn, 'CallEvent'):
                    try:
                        btn.CallEvent()
                        ui_ok = True
                        log.append('OK: %s.CallEvent() [%s]' % (str(bn), by))
                    except Exception, eb:
                        log.append('UYARI: login butonu basilamadi (%s)' % _fmt_error(eb))
                elif btn is None and hasattr(pw, '__OnClickLoginButton'):
                    try:
                        pw.__OnClickLoginButton()
                        ui_ok = True
                        log.append('OK: pw.__OnClickLoginButton() direkt cagrildi')
                    except Exception, ec:
                        log.append('UYARI: __OnClickLoginButton calismadi (%s)' % _fmt_error(ec))
            # --- YOL B: pw.Connect(id, pwd) class metodu (resmi 2014 + Marty)
            if not ui_ok and hasattr(pw, 'Connect') and callable(pw.Connect):
                try:
                    pw.Connect(user, pwd)
                    ui_ok = True
                    log.append('OK: pw.Connect(id,pwd) class metodu')
                except Exception, eB:
                    log.append('UYARI: pw.Connect calismadi (%s)' % _fmt_error(eB))
        else:
            log.append('UYARI: LoginWindow bulunamadi - paket yolu denenecek (SCENE=%s)' % _scene_name())
        # --- YOL C: paket yolu (authSocket yedegi ile)
        if not ui_ok:
            import net
            sent = None
            if hasattr(net, 'SetLoginInfo'):
                try:
                    net.SetLoginInfo(user, pwd)
                    sent = 'net.SetLoginInfo'
                except Exception, eC:
                    log.append('UYARI: net.SetLoginInfo (%s)' % _fmt_error(eC))
            elif hasattr(net, 'SetLoginInfoMap'):
                # eski clientlarda map parametreli imza (N2Play authSocket tarzi)
                try:
                    net.SetLoginInfo(user, pwd, 'EN', 0)
                    sent = 'net.SetLoginInfo(4arg)'
                except:
                    pass
            ms = _get_ms()
            if ms is not None and hasattr(ms, 'Connect'):
                try:
                    ms.Connect()
                    sent = (sent or '?') + ' + stream.Connect()'
                except:
                    pass
            if sent is not None and 'Connect' not in sent and hasattr(net, 'ConnectToAccountServer'):
                try:
                    net.ConnectToAccountServer()
                    sent = sent + ' + net.ConnectToAccountServer()'
                except Exception, eC2:
                    log.append('UYARI: net.ConnectToAccountServer (%s)' % _fmt_error(eC2))
            if sent:
                ui_ok = True
                log.append('OK: paket yolu (%s)' % sent)
            else:
                log.append('HATA: tum login yollari basarisiz - `uiprobe` ciktisini gonder')
        log.append('Beklenen: waitfor SelectCharacterWindow 30')
        log.append('Sonuc takibi: lasterr (yanlis sifre = LOGIN_FAILURE: WRONGPWD yakalanir)')
        _write('login', '\n'.join(log) + '\n')
        _write('status', status_text())
    except Exception, e:
        _write('login', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 3b) UIPROBE (v5.2 YENI) - login ekranini TAM tarar: hangi mimaride
#     oldugunu, 3. editline olup olmadigini, hangi argumanlarla login/
#     selserver verilmesi gerektigini raporlar. Saha tani komutu.
# ---------------------------------------------------------------------------
def uiprobe():
    try:
        pw = _pw_by_type('LoginWindow')
        lines = ['SCENE=%s' % _scene_name()]
        if pw is None:
            lines.append('HATA: LoginWindow sahnesinde degil - probe icin login ekrani acik olmali')
            _write('uiprobe', '\n'.join(lines) + '\n')
            return
        try:
            lines.append('class: %s (modul: %s)' % (type(pw).__name__, type(pw).__module__))
        except:
            pass
        # --- editline envanteri
        id_t, pwd_t, third_t, els = _classify_editlines(pw)
        lines.append('--- EDITLINE (%d) ---' % len(els))
        for a, v in els:
            tag = ''
            if id_t is not None and a == id_t[0]:
                tag = ' <- ID'
            elif pwd_t is not None and a == pwd_t[0]:
                tag = ' <- PWD'
            elif any(a == t[0] for t in third_t):
                tag = ' <- 3.ALAN ADAYI'
            txtlen = '?'
            try:
                txtlen = len(v.GetText() or '')
            except:
                pass
            has_set = 'SetText' if hasattr(v, 'SetText') else ('SetTextF' if hasattr(v, 'SetTextF') else 'SetText-YOK')
            lines.append('  %s (sinif=%s, metin_uzunluk=%s, %s)%s' % (a, type(v).__name__, str(txtlen), has_set, tag))
        if third_t:
            lines.append('SONUC: 3. editline VAR - login <id> <pwd> <3.alan> kullan (3. alan adlari: %s)' %
                         ', '.join(t[0] for t in third_t[:3]))
        else:
            lines.append('SONUC: 3. editline YOK - login <id> <pwd> yeterli')
        # --- buton envanteri
        lines.append('--- BUTON (CallEvent olanlar) ---')
        n_btn = 0
        try:
            for a in dir(pw):
                if 'utton' in a or a in ('loginButton', 'serverSelectButton'):
                    v = getattr(pw, a, None)
                    if v is not None and hasattr(v, 'CallEvent'):
                        n_btn += 1
                        lines.append('  %s (sinif=%s)' % (a, type(v).__name__))
        except:
            pass
        if n_btn == 0:
            lines.append('  (attr ile buton yok - GetChild/uiscript adi farkli olabilir)')
        # --- listbox envanteri
        lines.append('--- LISTBOX / SECIM ---')
        rn, rl, ry = _child_by_names(pw, _REGIONLIST_NAMES)
        sn, sl, sy = _child_by_names(pw, _SERVERLIST_NAMES)
        cn, cl, cy = _child_by_names(pw, _CHLIST_NAMES)
        for nm, obj, yol in (('regionList', rl, ry), ('serverList', sl, sy), ('channelList', cl, cy)):
            if obj is None:
                lines.append('  %s: YOK' % nm)
            else:
                cnt = '?'; sel = '?'
                try:
                    cnt = int(obj.GetItemCount())
                except:
                    pass
                try:
                    sel = str(obj.GetSelectedItem())
                except:
                    pass
                lines.append('  %s: adet=%s secili=%s (sinif=%s, yol=%s)' % (nm, str(cnt), sel, type(obj).__name__, yol))
        # --- Marty channelButton dict
        cb = getattr(pw, 'channelButton', None)
        if cb is not None:
            try:
                keys = sorted([str(k) for k in cb.keys()])
                lines.append('  channelButton dict VAR: CH butonlari = %s (Marty tarzi - OK butonu yok)' % ','.join(keys))
            except:
                lines.append('  channelButton dict VAR (icerik okunamadi)')
        # --- metotlar
        meth = []
        for m in ('Connect', 'SetChannel', '__OnClickLoginButton', '__OnClickSelectServerButton'):
            if hasattr(pw, m):
                meth.append(m)
        if meth:
            lines.append('  LoginWindow metotlari: %s' % ', '.join(meth))
        # --- serverInfo.REGION_DICT (coklu bolge bilgisi)
        try:
            import serverInfo
            rd = getattr(serverInfo, 'REGION_DICT', None)
            if rd:
                lines.append('--- serverInfo.REGION_DICT (%d bolge) ---' % len(rd))
                for rid in sorted(rd.keys())[:6]:
                    try:
                        reg = rd[rid]
                        svs = [str(k) + ':' + str(reg[k].get('name', '?')) for k in sorted(reg.keys()) if isinstance(reg[k], dict)][:10]
                        lines.append('  bolge[%s]: %s' % (str(rid), ', '.join(svs)))
                    except:
                        lines.append('  bolge[%s]: (okunamadi)' % str(rid))
        except:
            lines.append('serverInfo.REGION_DICT: okunamadi (modul yok)')
        # --- oneriler
        lines.append('--- ONERI AKISI ---')
        if sl is not None:
            lines.append('  selserver <srv> <ch>  ->  login <id> <pwd> [3.alan]')
        else:
            lines.append('  TEK-SERVER modu: selserver 0 <ch> ok=0 dene, sonra login <id> <pwd> [3.alan]')
        lines.append('  gizemli alanlarda: uiprobe ciktisini sunucu degisince tekrar al')
        _write('uiprobe', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('uiprobe', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 3c) RELOGIN (v5.2 YENI - v4.6'daki komutun universal donusu)
#     Iki mod:
#       TAM  (default): /logout -> char ekranina dus -> net.Disconnect ->
#                       login ekranina dus -> selserver+login (yeni oturum)
#       HIZI (reloginquick): /logout -> char ekranina dus -> selchar(slot)
#                       (baglanti acik kalir, sadece karaktere tekrar girer)
#     State-machine: DLL 150ms nabzi (_tick) surer - ana thread bloklanmaz.
# ---------------------------------------------------------------------------
_RELOGIN = {'on': 0, 'step': 0, 't0': 0.0, 'deadline': 0.0,
            'id': '', 'pwd': '', 'third': '', 'srv': 0, 'ch': 0, 'slot': 0,
            'log': []}

def _relog_live(msg):
    try:
        _RELOGIN['log'].append(msg)
        if len(_RELOGIN['log']) > 40:
            _RELOGIN['log'] = _RELOGIN['log'][-40:]
        try:
            sys.stdout.write('[RELOGIN] ' + msg + chr(10))
        except:
            pass
    except:
        pass

def _relog_flush(final):
    try:
        if final:
            _write('relogin', chr(10).join(_RELOGIN['log']) + chr(10))
        else:
            # araci adim raporlarini da yaz (cokme durumunda kanit)
            _write('relogin_step', chr(10).join(_RELOGIN['log']) + chr(10))
    except:
        pass

def relogin(id=None, pwd=None, srv=None, ch=None, third=None, ok=1):
    """TAM relogin: logout -> disconnect -> login ekraninda yeni oturum.
    Parametre verilmezse C:\\MaxExec\\login.dat (login/selserver kayitlari)
    kullanilir. Oyunda degilse direkt login akisina gecer."""
    try:
        _load_login_file()
        _RELOGIN['id'] = str(id) if id is not None else _SAVE.get('id', '')
        _RELOGIN['pwd'] = str(pwd) if pwd is not None else _SAVE.get('pwd', '')
        _RELOGIN['third'] = str(third) if third is not None else _SAVE.get('third', '')
        _RELOGIN['srv'] = int(srv) if srv is not None else int(_SAVE.get('srv', 0))
        _RELOGIN['ch'] = int(ch) if ch is not None else int(_SAVE.get('ch', 0))
        if not _RELOGIN['id'] or not _RELOGIN['pwd']:
            _write('relogin', 'HATA: id/pwd yok - `relogin <id> <pwd> [srv] [ch]` ver veya once login/selserver kullan\n')
            return
        import time as _t
        _RELOGIN.update({'on': 1, 'step': 0, 't0': _t.time(), 'deadline': _t.time() + 15.0, 'log': []})
        _relog_live('TAM relogin BASLADI: %s (srv=%d ch=%d)' % (_RELOGIN['id'], _RELOGIN['srv'], _RELOGIN['ch']))
        _relog_flush(False)
        _write('relogin', 'OK: relogin state-machine basladi (DLL 150ms nabzi surer)\nAdimlar: logout -> disconnect -> login -> selserver -> login\nTakip: last_relogin_step.txt | sonuc: last_relogin.txt\n')
    except Exception, e:
        _write('relogin', 'HATA ' + _fmt_error(e) + '\n')

def reloginquick(slot=0):
    """HIZI relogin: /logout -> char ekranindan ayni karaktere tekrar gir
    (baglanti korunur - sadece karaktere donus)."""
    try:
        import time as _t
        _RELOGIN.update({'on': 2, 'step': 10, 't0': _t.time(), 'deadline': _t.time() + 15.0,
                         'slot': int(slot), 'log': [], 'id': _SAVE.get('id', ''), 'pwd': _SAVE.get('pwd', ''),
                         'third': _SAVE.get('third', ''), 'srv': _SAVE.get('srv', 0), 'ch': _SAVE.get('ch', 0)})
        _relog_live('HIZI relogin BASLADI (slot %d): /logout -> selchar' % int(slot))
        _relog_flush(False)
        _write('relogin', 'OK: HIZI relogin basladi (/logout -> selchar %d)\n' % int(slot))
    except Exception, e:
        _write('relogin', 'HATA ' + _fmt_error(e) + '\n')

def _relogin_tick():
    """_tick() icinden ~150ms'de bir cagrilir (DLL nabzi)."""
    if not _RELOGIN.get('on'):
        return
    try:
        import time as _t
        now = _t.time()
        if now - _RELOGIN['t0'] < 0.25:
            return
        _RELOGIN['t0'] = now
        sc = _scene_name()
        st = _RELOGIN['step']
        # zaman asimi korumasi
        if now > _RELOGIN['deadline']:
            _relog_live('ZAMAN ASIMI (adim %d, sahne=%s) - relogin DURDURULDU' % (st, sc))
            _relog_flush(True)
            _RELOGIN['on'] = 0
            return
        if st == 0:  # oyunda mi? -> /logout
            if sc == 'GameWindow':
                try:
                    import net
                    net.SendChatPacket('/logout')
                    _relog_live('oyunda: /logout gonderildi (sahne=%s)' % sc)
                except Exception, e0:
                    _relog_live('/logout gonderilemedi (%s) - disconnect yolu' % _fmt_error(e0))
            else:
                _relog_live('oyunda degil (sahne=%s) - direkt login akisi' % sc)
            _RELOGIN['step'] = 1
            _RELOGIN['deadline'] = now + 15.0
        elif st == 1:  # char ekranini bekle
            if sc == 'SelectCharacterWindow':
                _relog_live('char ekranina dusuldu')
                _RELOGIN['step'] = 2
                _RELOGIN['deadline'] = now + 15.0
        elif st == 2:  # char ekraninda: TAM mod -> disconnect | HIZI mod -> selchar
            if _RELOGIN['on'] == 2:  # HIZI
                _relog_live('selchar(%d) gonderiliyor' % _RELOGIN['slot'])
                try:
                    selchar(_RELOGIN['slot'])
                except Exception, e1:
                    _relog_live('selchar hatasi: %s' % _fmt_error(e1))
                _RELOGIN['step'] = 5
                _RELOGIN['deadline'] = now + 30.0
                return
            import net
            done = False
            for meth in ('Disconnect', 'DisconnectGame'):
                if hasattr(net, meth):
                    try:
                        getattr(net, meth)()
                        _relog_live('net.%s() cagrildi - login ekranina dusuluyor' % meth)
                        done = True
                        break
                    except Exception, e2:
                        _relog_live('net.%s hatasi: %s' % (meth, _fmt_error(e2)))
            if done:
                _RELOGIN['step'] = 3
                _RELOGIN['deadline'] = now + 20.0
            # disconnect metodu yoksa: 2s bekle, tekrar dene (deadline korur)
        elif st == 3:  # login ekranini bekle
            if sc in ('LoginWindow', 'LoginWindow+ServerList'):
                _relog_live('login ekranina dusuldu - selserver(%d,%d) + login uygulanacak' % (_RELOGIN['srv'], _RELOGIN['ch']))
                try:
                    selserver(_RELOGIN['srv'], _RELOGIN['ch'], 1)
                except Exception, e3:
                    _relog_live('selserver hatasi: %s' % _fmt_error(e3))
                _RELOGIN['step'] = 4
                _RELOGIN['deadline'] = now + 20.0
        elif st == 4:  # login uygula
            _relog_live('login(%s, ***) uygulaniyor' % _RELOGIN['id'])
            try:
                login(_RELOGIN['id'], _RELOGIN['pwd'], _RELOGIN['third'] or None)
            except Exception, e4:
                _relog_live('login hatasi: %s' % _fmt_error(e4))
            _RELOGIN['step'] = 5
            _RELOGIN['deadline'] = now + 40.0
        elif st == 5:  # sonuc bekle
            if sc == 'GameWindow':
                _relog_live('BASARILI: GameWindow\'a donuldu (relogin tamam)')
                _relog_flush(True)
                _RELOGIN['on'] = 0
            elif sc == 'SelectCharacterWindow' and _RELOGIN['on'] == 2:
                _relog_live('BASARILI: char ekranina donuldu (hizi relogin tamam)')
                _relog_flush(True)
                _RELOGIN['on'] = 0
    except Exception, e:
        try:
            _relog_live('tick hatasi: %s - relogin durduruldu' % _fmt_error(e))
            _relog_flush(True)
            _RELOGIN['on'] = 0
        except:
            pass

# ---------------------------------------------------------------------------
# 4) CHARLIST - 5 slot tablosu (net slot data)
# ---------------------------------------------------------------------------
def charlist():
    try:
        import net
        lines = []
        count = 0
        empty_slots = []
        for i in range(SLOT_COUNT):
            try:
                pid = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)
            except:
                pid = 0
            if not pid:
                empty_slots.append(i)
                lines.append('[slot %d] BOS' % i)
                continue
            count += 1
            try:
                name = net.GetAccountCharacterSlotDataString(i, net.ACCOUNT_CHARACTER_SLOT_NAME)
            except:
                name = '?'
            try:
                level = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
            except:
                level = -1
            try:
                race = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_RACE)
            except:
                race = -1
            job = JOB_NAMES.get(race % 4, '?') if race >= 0 else '?'
            sex = RACE_TABLE.get(race, ('?', '?'))[1]
            lines.append('[slot %d] %s  Lv.%d  %s(%s)  race=%d' % (i, name, level, job, sex, race))
        lines.append('---')
        lines.append('TOPLAM: %d / %d | BOS: %s' % (count, SLOT_COUNT, str(empty_slots)))
        _write('charlist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('charlist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 5) EMPIRE (ilk karakter icin) - paket yolu
# ---------------------------------------------------------------------------
def empire(n):
    try:
        if n not in (1, 2, 3):
            _write('empire', 'HATA: empire 1/2/3 olmali\n')
            return
        import net
        net.SendSelectEmpirePacket(n)
        _write('empire', 'OK: empire=%d gonderildi (cevap: SelectCharacterWindow tazelenir)\n' % n)
    except Exception, e:
        _write('empire', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 6) CREATE - paket yolu (statlar server'da; 30 sn cooldown var)
# ---------------------------------------------------------------------------
def create(slot, name, race, shape):
    try:
        if slot < 0 or slot >= SLOT_COUNT:
            _write('create', 'HATA: slot 0..%d\n' % (SLOT_COUNT - 1))
            return
        if race not in RACE_TABLE:
            _write('create', 'HATA: race 0..8\n')
            return
        if len(name) > 12:
            _write('create', 'HATA: isim > 12 karakter\n')
            return
        import net
        net.SendCreateCharacterPacket(slot, name, race, shape, 0, 0, 0, 0)
        job, sex = RACE_TABLE[race]
        _write('create', 'OK: slot=%d ad=%s race=%d(%s-%s) shape=%d\n'
                         'Kontrol: 30 sn sonra charlist (create cooldown 30sn)\n'
                         % (slot, name, race, job, sex, shape))
    except Exception, e:
        _write('create', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 7) ENTER - UI START yolu ONCELIKLI (v3.2 - saha testi 7 fix)
#    Saha kaniti: DirectEnter yeni olusan karakterde server tarafindan
#    reddediliyor (loading acilip login ekranina geri atiyor), eski
#    karakterde calisiyor. Calisan script + kullanici dogrulamasi: once
#    SelectSlot + StartGame. DirectEnter YEDEK (UI yolu bulunamazsa).
#    RC12 cift-giris yasagi korunur: UI StartGame paketi kendisi yollar,
#    ustune bir de DirectEnter cagirmak NPC yukleme hatasi yapar.
# ---------------------------------------------------------------------------
def enter(slot):
    try:
        _SAVE['slot'] = int(slot)
        _save_login_file()
        log = []
        sw = _pw_by_type('SelectCharacterWindow')
        ui_ok = False
        if sw is not None:
            try:
                if hasattr(sw, 'SelectSlot'):
                    sw.SelectSlot(slot)
                    log.append('OK: SelectSlot(%d)' % slot)
            except:
                pass
            try:
                sw.slot = slot
            except:
                pass
            # a) StartGame metodu (start butonunun handler'i - calisan script yolu)
            try:
                if hasattr(sw, 'StartGame'):
                    sw.StartGame()
                    log.append('OK: StartGame() - UI giris yolu')
                    ui_ok = True
            except:
                pass
            # b) start butonu attr'si
            if not ui_ok:
                for attr in ('startButton', 'btnStart', 'btn_start', 'StartButton'):
                    b = getattr(sw, attr, None)
                    if b is not None and hasattr(b, 'CallEvent'):
                        b.CallEvent()
                        log.append('OK: %s.CallEvent() - UI giris yolu' % attr)
                        ui_ok = True
                        break
            # c) ElementDictionary yedegi
            if not ui_ok:
                ed = getattr(sw, 'ElementDictionary', None) or {}
                for key in ('start_button', 'btnStart', 'startButton'):
                    b = ed.get(key, None)
                    if b is not None and hasattr(b, 'CallEvent'):
                        b.CallEvent()
                        log.append('OK: start butonu (ElementDictionary: %s)' % key)
                        ui_ok = True
                        break
        if ui_ok:
            log.append('NOT: DirectEnter cagrilmadi (UI paketi kendisi yollar - cift giris yasagi)')
            log.append('Beklenen: waitfor GameWindow 60')
            _write('enter', '\n'.join(log) + '\n')
            return
        # d) YEDEK: UI yolu bulunamadiysa paket yolu (eski davranis)
        if sw is None:
            log.append('UYARI: SelectCharacterWindow bulunamadi (SCENE=%s) - paket yolu' % _scene_name())
        else:
            log.append('UYARI: StartGame/start butonu bulunamadi - paket yolu')
        try:
            import net
            net.DirectEnter(slot)
            log.append('OK: DirectEnter(%d) - YEDEK paket yolu' % slot)
            log.append('Beklenen: waitfor GameWindow 60')
        except Exception, e:
            log.append('HATA DirectEnter: ' + _fmt_error(e))
        _write('enter', '\n'.join(log) + '\n')
    except Exception, e:
        _write('enter', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 9) SELCHAR - karakter slotu sec (orn. 4. slotu secmek)
# ---------------------------------------------------------------------------
def selchar(slot):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('selchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'istenen slot=%d' % slot]
        try:
            sw.SelectSlot(slot)
            log.append('OK: SelectSlot(%d)' % slot)
        except Exception, e:
            log.append('UYARI: SelectSlot hatasi (%s) - slot attr atanacak' % _fmt_error(e))
            try:
                sw.slot = slot
                log.append('OK: slot=%d attr atandi' % slot)
            except Exception, e2:
                _write('selchar', '\n'.join(log + ['HATA: slot attr de atilanamadi ' + _fmt_error(e2)]) + '\n')
                return
        time.sleep(0.3)
        try:
            cn = getattr(sw, 'CharacterName', None)
            if cn is not None and hasattr(cn, 'GetText'):
                log.append('secilen karakter: %s' % cn.GetText())
        except:
            pass
        log.append('Kontrol: charlist (slot isaretlenmis olmali)')
        _write('selchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('selchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 10) NEWCHAR - "karakter olustur" butonuna bas
# (btnCreate instance attr None olabilir - ElementDictionary + dir() yedekli,
#  kanitlanmis _click_create_button deseni)
# ---------------------------------------------------------------------------
def newchar():
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('newchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        btn = None
        for attr in ('btnCreate', 'createButton', 'btn_create'):
            b = getattr(sw, attr, None)
            if b is not None and hasattr(b, 'CallEvent'):
                btn = b
                log.append('buton attr: %s' % attr)
                break
        if btn is None:
            ed = getattr(sw, 'ElementDictionary', None) or {}
            for key in ('create_button', 'btnCreate', 'CreateButton'):
                b = ed.get(key, None)
                if b is not None and hasattr(b, 'CallEvent'):
                    btn = b
                    log.append('buton (ElementDictionary): %s' % key)
                    break
        if btn is None:
            for a in dir(sw):
                if 'reate' in a and ('utton' in a or 'utton' in a.lower()):
                    try:
                        b = getattr(sw, a)
                    except:
                        continue
                    if b is not None and hasattr(b, 'CallEvent'):
                        btn = b
                        log.append('aday buton: %s' % a)
                        break
        if btn is None:
            extra = ['HATA: create butonu bulunamadi!']
            try:
                for a in dir(sw):
                    if 'reate' in a or 'utton' in a:
                        extra.append('  aday attr: %s = %s' % (a, type(getattr(sw, a)).__name__))
            except:
                pass
            _write('newchar', '\n'.join(log + extra) + '\n')
            return
        btn.CallEvent()
        log.append('OK: create butonuna basildi')
        log.append('Beklenen: bayrak ekrani (ilk karakter) VEYA olusturma ekrani')
        log.append('Sonraki: status -> empireui <1-3> VEYA mkchar <ad> <race>')
        _write('newchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('newchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 11) JOBLIST - sinif/cinsiyet tablosu + olusturma ekran durumu
# ---------------------------------------------------------------------------
def joblist():
    try:
        lines = ['SCENE=%s' % _scene_name(), '', 'race tablosu (mkchar <ad> <race>):']
        for r in sorted(RACE_TABLE):
            job, sex = RACE_TABLE[r]
            lines.append('  race %d = %s (%s)' % (r, job, 'Erkek' if sex == 'E' else 'Kadin'))
        ccw = _pw_by_type('CreateCharacterWindow')
        if ccw is not None:
            lines.append('')
            lines.append('olusturma ekrani ACIK:')
            lines.append('  mevcut slot(idx) = %s' % str(getattr(ccw, 'slot', '?')))
            lines.append('  gender           = %s' % str(getattr(ccw, 'gender', '?')))
            try:
                edn = getattr(ccw, 'editCharacterName', None)
                if edn is not None and hasattr(edn, 'GetText'):
                    lines.append('  isim kutusu      = "%s"' % edn.GetText())
            except:
                pass
            try:
                gbl = getattr(ccw, 'genderButtonList', [])
                lines.append('  genderButtonList = %d buton' % len(gbl))
            except:
                pass
        else:
            lines.append('')
            lines.append('(olusturma ekrani kapali - newchar ile ac)')
        _write('joblist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('joblist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 12) MKCHAR - UI akisiyla karakter olustur (sinif gez + cinsiyet + isim + OLUSTUR)
# (v3.2 fix: paket yolu SADECE buton bulunamazsa - cift paket sahte
#  CREATE_FAILURE uretir; saha testi 7 kaniti)
# ---------------------------------------------------------------------------
def mkchar(name, race):
    try:
        if race not in RACE_TABLE:
            _write('mkchar', 'HATA: race 0..8 (joblist yaz)\n')
            return
        if len(name) > 12:
            _write('mkchar', 'HATA: isim > 12 karakter\n')
            return
        log = ['SCENE=%s' % _scene_name(),
               'hedef: ad=%s race=%d (%s-%s)' % (name, race,
                                                 RACE_TABLE[race][0], RACE_TABLE[race][1])]
        ccw = _pw_by_type('CreateCharacterWindow')
        if ccw is None:
            _write('mkchar', '\n'.join(log + ['HATA: CreateCharacterWindow acik degil - once newchar']) + '\n')
            return
        # a) sinif slotuna gez (Warrior->Ninja->Sura->Shaman)
        target_slot = RACE_TO_SLOT.get(race, 3)
        target_gender = RACE_TO_GENDER.get(race, 0)
        cur = getattr(ccw, 'slot', 0)
        log.append('sinif slotu: %d -> %d' % (cur, target_slot))
        try:
            cur = int(cur)
        except:
            cur = 0
        if cur != target_slot:
            incr = getattr(ccw, '_CreateCharacterWindow__IncreaseSlotIndex', None)
            if incr is not None:
                steps = (target_slot - cur) % 4
                for s in range(steps):
                    try:
                        incr()
                        time.sleep(1.0)
                        if int(getattr(ccw, 'slot', -1)) == target_slot:
                            break
                    except:
                        break
            try:
                ccw.slot = target_slot
            except:
                pass
            log.append('OK: sinif slotu = %d' % target_slot)
        # b) cinsiyet
        sel_g = getattr(ccw, '_CreateCharacterWindow__SelectGender', None)
        if sel_g is not None:
            try:
                sel_g(target_gender)
                time.sleep(0.3)
                log.append('OK: __SelectGender(%d)' % target_gender)
            except:
                pass
        try:
            ccw.gender = target_gender
        except:
            pass
        gbl = getattr(ccw, 'genderButtonList', None) or []
        if len(gbl) > target_gender:
            try:
                gbl[target_gender].CallEvent()
                time.sleep(0.3)
                log.append('OK: genderButtonList[%d].CallEvent()' % target_gender)
            except:
                pass
        sbl = getattr(ccw, 'shapeButtonList', None) or []
        if len(sbl) > target_gender:
            try:
                sbl[target_gender].CallEvent()
            except:
                pass
        # c) isim
        edn = getattr(ccw, 'editCharacterName', None)
        if edn is not None and hasattr(edn, 'SetText'):
            edn.SetText(name)
            log.append('OK: isim = "%s"' % name)
        else:
            log.append('UYARI: editCharacterName bulunamadi!')
        # d) OLUSTUR butonu (enter)
        btn = None
        for attr in ('btnCreate', 'createButton', 'btn_create'):
            b = getattr(ccw, attr, None)
            if b is not None and hasattr(b, 'CallEvent'):
                btn = b
                break
        if btn is None:
            ed = getattr(ccw, 'ElementDictionary', None) or {}
            for key in ('create_button', 'btnCreate', 'CreateButton'):
                b = ed.get(key, None)
                if b is not None and hasattr(b, 'CallEvent'):
                    btn = b
                    break
        if btn is not None:
            btn.CallEvent()
            log.append('OK: OLUSTUR butonuna basildi')
        else:
            log.append('UYARI: olustur butonu bulunamadi - sadece paket yolu')
        # e) paket yolu SADECE buton bulunamadiysa (v3.2 fix)
        #    UI OLUSTUR butonu paketi KENDISI yollar (kanit: cift paket ->
        #    1 basari + 1 CREATE_FAILURE: 0 - karakter zaten olusmustu, 2.
        #    paket reddedildi). Buton bastiktan sonra bir de paket yollamak
        #    SAHTE hata uretir - artik yollanmiyor.
        if btn is None:
            log.append('UYARI: buton yok - paket yolu deneniyor')
            time.sleep(1.0)
            slot = -1
            try:
                import net
                for i in range(SLOT_COUNT):
                    pid = 0
                    try:
                        pid = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)
                    except:
                        pid = 0
                    if not pid:
                        slot = i
                        break
            except:
                pass
            if slot < 0:
                slot = 0
            try:
                import net
                use_emp = 0
                try:
                    eid = net.GetEmpireID()
                    if eid > 0:
                        use_emp = eid
                except:
                    pass
                net.SendCreateCharacterPacket(slot, name, race, target_gender, use_emp, 0, 0, 0)
                log.append('OK: SendCreateCharacterPacket(slot=%d, race=%d, shape=%d) - paket yolu' % (slot, race, target_gender))
            except Exception, e2:
                log.append('HATA: paket yolu hatasi: %s' % _fmt_error(e2))
        else:
            log.append('OK: paket yolu atlandi (buton kendisi yollar - cift paket sahte CREATE_FAILURE yapar)')
        log.append('Kontrol: waitfor SelectCharacterWindow 15 -> charlist')
        log.append('Hata olursa: lasterr (CREATE_FAILURE yakalanir)')
        _write('mkchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('mkchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 13) EMPIRELIST - bayrak listesi + mevcut empire
# ---------------------------------------------------------------------------
def empirelist():
    try:
        lines = ['SCENE=%s' % _scene_name()]
        try:
            import net
            eid = net.GetEmpireID()
            lines.append('hesabin empire\'i: %d (%s)' % (eid, EMPIRE_NAMES.get(eid, '?')))
        except Exception, e:
            lines.append('net.GetEmpireID okunamadi: %s' % _fmt_error(e))
        ew = _pw_by_type('SelectEmpireWindow', 'ReselectEmpireWindow')
        if ew is None:
            lines.append('(bayrak ekrani acik degil)')
        else:
            lines.append('bayrak ekrani ACIK (%s):' % type(ew).__name__)
            try:
                lines.append('  empireID = %s' % str(getattr(ew, 'empireID', '?')))
            except:
                pass
            try:
                ed = getattr(ew, 'ElementDictionary', None) or {}
                cnt = 0
                for key, obj in ed.items():
                    try:
                        if type(obj).__name__ == 'EmpireButton':
                            cnt += 1
                            lines.append('  EmpireButton: key=%s arg=%s' % (key, str(getattr(obj, 'arg', '?'))))
                    except:
                        pass
                if cnt == 0:
                    lines.append('  (ElementDictionary\'de EmpireButton yok - OnSelectEmpire ile secilecek)')
            except:
                pass
        lines.append('')
        lines.append('bayrak tablosu: 1=Shinsoo (kirmizi) 2=Chunjo (sari) 3=Jinno (mavi)')
        try:
            isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
            if isel is not None:
                en = getattr(isel, 'EMPIRE_NAME', None)
                if en:
                    lines.append('client isimleri: %s' % str(en))
        except:
            pass
        _write('empirelist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('empirelist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 14) EMPIREUI - bayrak sec + ILERLE (kanitlanmis do_select_empire deseni)
# ---------------------------------------------------------------------------
def empireui(n):
    try:
        if n not in (1, 2, 3):
            _write('empireui', 'HATA: empire 1/2/3\n')
            return
        ew = _pw_by_type('SelectEmpireWindow', 'ReselectEmpireWindow')
        if ew is None:
            _write('empireui', 'HATA: bayrak ekrani acik degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'hedef empire=%d (%s)' % (n, EMPIRE_NAMES.get(n, '?'))]
        # a) OnSelectEmpire - bayragi isaretle
        try:
            ew.OnSelectEmpire(n)
            time.sleep(0.5)
            log.append('OK: OnSelectEmpire(%d)' % n)
        except Exception, e:
            log.append('UYARI: OnSelectEmpire hatasi: %s' % _fmt_error(e))
        try:
            ew.empireID = n
            log.append('OK: empireID=%d atandi' % n)
        except:
            pass
        # b) EmpireButton'a tikla (ElementDictionary, arg eslesmeli)
        clicked = False
        try:
            ed = getattr(ew, 'ElementDictionary', None) or {}
            for key, obj in ed.items():
                try:
                    if type(obj).__name__ == 'EmpireButton' and getattr(obj, 'arg', -1) == n:
                        obj.CallEvent()
                        clicked = True
                        time.sleep(1.0)
                        log.append('OK: EmpireButton(%s).CallEvent()' % key)
                        break
                except:
                    pass
        except:
            pass
        if not clicked:
            log.append('(EmpireButton bulunamadi/eslesmedi - OnSelectEmpire yeterli olabilir)')
        # c) ILERLE - ClickSelectButton
        done = False
        try:
            ew.ClickSelectButton()
            done = True
            log.append('OK: ClickSelectButton() - ilerlendi')
        except Exception, e:
            log.append('UYARI: ClickSelectButton hatasi: %s' % _fmt_error(e))
        if not done:
            try:
                ed = getattr(ew, 'ElementDictionary', None) or {}
                sb = ed.get('select_button', None)
                if sb is not None and hasattr(sb, 'CallEvent'):
                    sb.CallEvent()
                    log.append('OK: select_button.CallEvent() - ilerlendi')
            except:
                pass
        # d) paket yolu yedegi (ekran gecmezse)
        time.sleep(1.5)
        scene_now = _scene_name()
        log.append('simdi sahne: %s' % scene_now)
        if 'Empire' in scene_now:
            try:
                import net
                net.SendSelectEmpirePacket(n)
                log.append('YEDEK: SendSelectEmpirePacket(%d) gonderildi' % n)
            except Exception, e:
                log.append('UYARI: paket yolu hatasi: %s' % _fmt_error(e))
        log.append('Beklenen: olusturma ekrani (yoksa bayrak kayitliyse direkt olusturma)')
        log.append('Sonraki: status -> mkchar <ad> <race>')
        _write('empireui', '\n'.join(log) + '\n')
    except Exception, e:
        _write('empireui', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 15) DELCHAR - karakter sil akisi: slot sec + silme sorusu + kod dialogu AC
# (kanitlanmis chardeleter v8 deseni - CallEvent YOK, dogrudan metodlar)
# ---------------------------------------------------------------------------
def delchar(slot):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('delchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'hedef slot=%d' % slot]
        # dialog temizligi (once acik kalan kutular kapat)
        try:
            pib = getattr(sw, 'privateInputBoard', None)
            if pib is not None:
                try:
                    sw.CancelInputPrivateCode()
                except:
                    pass
                log.append('eski kod dialogu kapatildi')
        except:
            pass
        # 1) slot sec
        try:
            sw.SelectSlot(slot)
            log.append('OK: SelectSlot(%d)' % slot)
        except Exception, e:
            log.append('UYARI: SelectSlot hatasi: %s' % _fmt_error(e))
        time.sleep(0.5)
        # 2) silme sorusu dialogu
        try:
            sw.PopupDeleteQuestion()
            log.append('OK: PopupDeleteQuestion() - "karakteri sil" sorusu')
        except Exception, e:
            log.append('UYARI: PopupDeleteQuestion hatasi: %s' % _fmt_error(e))
        time.sleep(0.5)
        # 3) kod dialogu
        try:
            sw.InputPrivateCode()
            log.append('OK: InputPrivateCode() - kod dialogu ACILDI')
            log.append('SONRA: delcode <silme-kodu> yaz')
        except Exception, e:
            log.append('HATA: InputPrivateCode hatasi: %s' % _fmt_error(e))
        # NOT_NEED_DELETE_CODE bayragi (kod istemeyen serverlar)
        try:
            isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
            if isel is not None:
                if getattr(isel, 'NOT_NEED_DELETE_CODE', False):
                    log.append('NOT: bu server silme kodu istemiyor olabilir (NOT_NEED_DELETE_CODE=1)')
        except:
            pass
        _write('delchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('delchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 16) DELCODE - silme kodunu yaz + ONAYLA (chardeleter v8 - inputValue EditLine)
# ---------------------------------------------------------------------------
def delcode(code):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('delcode', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        pib = getattr(sw, 'privateInputBoard', None)
        if pib is None:
            try:
                sw.InputPrivateCode()
                time.sleep(0.5)
            except:
                pass
            pib = getattr(sw, 'privateInputBoard', None)
        if pib is None:
            _write('delcode', '\n'.join(log + ['HATA: kod dialogu acik degil - once delchar <slot>']) + '\n')
            return
        log.append('kod dialogu: %s' % type(pib).__name__)
        # EditLine bul (inputValue oncelikli - chardeleter kaniti)
        edit = None
        for attr in ('inputValue', 'inputBoard', 'editLine', 'edit', 'input', 'textEdit'):
            obj = getattr(pib, attr, None)
            if obj is not None and hasattr(obj, 'SetText') and hasattr(obj, 'GetText'):
                tn = type(obj).__name__
                if 'Button' not in tn and 'TextLine' not in tn:
                    edit = obj
                    log.append('EditLine: %s (%s)' % (attr, tn))
                    break
        if edit is None:
            try:
                for attr in dir(pib):
                    if attr.startswith('__'):
                        continue
                    try:
                        obj = getattr(pib, attr)
                    except:
                        continue
                    if obj is not None and hasattr(obj, 'SetText') and hasattr(obj, 'GetText'):
                        tn = type(obj).__name__
                        if 'Button' not in tn and 'TextLine' not in tn:
                            edit = obj
                            log.append('EditLine (dir): %s (%s)' % (attr, tn))
                            break
            except:
                pass
        if edit is None:
            _write('delcode', '\n'.join(log + ['HATA: kod giris kutusu bulunamadi!']) + '\n')
            return
        edit.SetText(str(code))
        try:
            wr = edit.GetText()
            log.append('OK: kod yazildi: "%s"' % wr)
        except:
            log.append('OK: kod yazildi')
        time.sleep(0.3)
        # ONAYLA
        try:
            sw.AcceptInputPrivateCode()
            log.append('OK: AcceptInputPrivateCode() - ONAYLANDI')
        except Exception, e:
            log.append('HATA: AcceptInputPrivateCode hatasi: %s' % _fmt_error(e))
        time.sleep(1.0)
        log.append('Sonuc: lasterr (DELETE_SUCCESS/DELETE_FAILURE) + charlist')
        _write('delcode', '\n'.join(log) + '\n')
    except Exception, e:
        _write('delcode', 'HATA ' + _fmt_error(e) + '\n')
# ---------------------------------------------------------------------------
# 8) STATUS - sahne + baglanti + stream bilgisi (+ lazy hook kurulumu)
# ---------------------------------------------------------------------------
def status_text():
    if len(_HOOKS_OK) < 4:
        _install_error_hooks()   # moduller sonra yuklenmis olabilir - tekrar dene
    try:
        import net
        try:
            conn = 1 if net.IsConnect() else 0
        except:
            conn = -1
    except:
        conn = -2
    scene = _scene_name()
    ms = _get_ms()
    return 'SCENE=%s | CONN=%d | stream=%s | t=%s\n' % (
        scene, conn,
        'yakalandi' if ms is not None else 'YOK',
        time.strftime('%H:%M:%S'))

def status(echo=True):
    # v3.1: waitfor polling'i echo=0 ile cagirir - konsol spami olmaz
    _write('status', status_text(), echo=echo)

# ===========================================================================
# v4.0 - OYUN-ICI KOMUTLAR (oyunda iken; `waitfor GameWindow 60` sonrasi)
# Kanit havuzu: nighttown koleksiyonu (4000+ kullanim, kullanici ekosistemi)
# + cycu.py. Her komut _ingame() guard'i ile baslar; menu ekraninda nazik
# hata verir. Butun raporlar results\last_<ad>.txt'ye + konsola duser.
# ===========================================================================

# ---------------------------------------------------------------------------
# stat() - karakter durumu (cycu.py kanitlari: player.GetStatus(LEVEL/HP/
# MAX_HP/SP/MAX_SP/EXP/NEXT_EXP), net.GetMainActorRace/SkillGroup, GetName)
# ---------------------------------------------------------------------------
def stat():
    try:
        if not _ingame():
            _write('stat', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player, net, chr
        L = ['SCENE=%s' % _scene_name()]
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            pass
        try:
            L.append('ad        = %s' % str(player.GetName()))
        except:
            try:
                L.append('ad        = %s' % str(chr.GetNameByVID(vid)))
            except:
                pass
        def _gs(cname):
            try:
                c = getattr(player, cname, None)
                if c is None:
                    return None
                return player.GetStatus(c)
            except:
                return None
        lvl = _gs('LEVEL');   hp = _gs('HP');      mhp = _gs('MAX_HP')
        sp  = _gs('SP');      msp = _gs('MAX_SP')
        ex  = _gs('EXP');     nex = _gs('NEXT_EXP')
        spd = _gs('MOVING_SPEED')
        if lvl is not None: L.append('seviye    = %s' % str(lvl))
        if hp is not None and mhp is not None:
            L.append('HP        = %s / %s  (%d%%)' % (str(hp), str(mhp), _pct(hp, mhp)))
        if sp is not None and msp is not None:
            L.append('SP        = %s / %s  (%d%%)' % (str(sp), str(msp), _pct(sp, msp)))
        if ex is not None and nex is not None:
            L.append('EXP       = %s / %s  (%d%%)' % (str(ex), str(nex), _pct(ex, nex)))
        if spd is not None: L.append('hiz       = %s (MOVING_SPEED)' % str(spd))
        try:
            r = net.GetMainActorRace()
            L.append('race      = %s (%s-%s)' % (str(r), RACE_TABLE.get(r, ('?', '?'))[0], RACE_TABLE.get(r, ('?', '?'))[1]))
        except:
            pass
        try:
            L.append('skill grup= %s' % str(net.GetMainActorSkillGroup()))
        except:
            pass
        try:
            e = net.GetEmpireID()
            L.append('empire    = %d (%s)' % (e, EMPIRE_NAMES.get(e, '?')))
        except:
            pass
        try:
            L.append('biniyor   = %s' % ('evet' if player.IsMountingHorse() else 'hayir'))
        except:
            pass
        L.append('pozisyon  : pos yaz | beceriler: skill yaz')
        _write('stat', '\n'.join(L) + '\n')
    except Exception, e:
        _write('stat', 'HATA ' + _fmt_error(e) + '\n')

def _pct(v, m):
    try:
        fm = float(m)
        if fm <= 0:
            return 0
        return int(float(v) / fm * 100.0)
    except:
        return 0

# ---------------------------------------------------------------------------
# pos() - pozisyon + harita (chr.GetPixelPosition - cycu kaniti;
# background.GetCurrentMapName - nighttown'da 34 kanitli kullanim)
# ---------------------------------------------------------------------------
def pos():
    try:
        if not _ingame():
            _write('pos', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import net, chr, background, player
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            pass
        p = None
        try:
            p = chr.GetPixelPosition(vid)
        except:
            pass
        if p is None or str(p) == 'None':
            try:
                p = player.GetMainCharacterPosition()
            except:
                pass
        if p is None or str(p) == 'None':
            _write('pos', 'HATA: pozisyon okunamadi\n')
            return
        x, y, z = 0, 0, 0
        try:
            x = int(p[0]); y = int(p[1]); z = int(p[2])
        except:
            pass
        L = ['vid    = %s' % str(vid),
             'x      = %d' % x,
             'y      = %d' % y,
             'z      = %d' % z,
             'metre  = (%d, %d)   [client koordinat /100]' % (x // 100, y // 100)]
        mname = ''
        try:
            mname = str(background.GetCurrentMapName())
        except:
            pass
        L.append('harita = %s' % (mname or '?'))
        L.append('isinlanma: tp %d %d | yuruyus: goto %d %d' % (x, y, x, y))
        _write('pos', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pos', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# inv(page) - envanter raporu (player.GetItemIndex 267 kanit +
# player.INVENTORY_PAGE_SIZE 147 kanit + player.GetItemCount 44 kanit +
# item.SelectItem/GetItemName 300/171 kanit)
# ---------------------------------------------------------------------------
def inv(page=0):
    try:
        if not _ingame():
            _write('inv', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player
        try:
            page = int(page)
        except:
            page = 0
        psize = 45
        try:
            psize = int(player.INVENTORY_PAGE_SIZE)
        except:
            psize = 45
        base = page * psize
        L = ['envanter sayfa %d  slotlar %d..%d  (INVENTORY_PAGE_SIZE=%d, 5 sutun x %d satir)' % (page, base, base + psize - 1, psize, psize / 5)]
        n = 0
        cells = 0
        for i in range(base, base + psize):
            vnum = 0
            try:
                vnum = int(player.GetItemIndex(i))
            except:
                vnum = 0
            if vnum <= 0:
                continue
            n += 1
            w, h = _item_size(vnum)
            cells += w * h
            cnt = ''
            try:
                c = int(player.GetItemCount(i))
                if c > 1:
                    cnt = ' x%d' % c
            except:
                pass
            boyut = ''
            if w > 1 or h > 1:
                boyut = ' (%dx%d)' % (w, h)
            iname = _item_name(vnum)
            L.append('  [%3d] vnum=%-7d %s%s%s' % (i, vnum, iname, boyut, cnt))
        L.append('---')
        L.append('esya: %d / %d (bu sayfa)  kaplanan hucre: %d  bos hucre: %d' % (n, psize, cells, psize - cells))
        if psize - cells == 0:
            L.append('sayfa dolu gorunuyor - diger sayfa: inv %d' % (page + 1))
        L.append('ekipman: equip | kullan: use <slot> | birak: drop <slot> <adet>')
        _write('inv', '\n'.join(L) + '\n')
    except Exception, e:
        _write('inv', 'HATA ' + _fmt_error(e) + '\n')

def _item_name(vnum):
    """item.SelectItem + GetItemName (300/171 kanit) - isim okunamazsa vnum."""
    try:
        import item
        item.SelectItem(vnum)
        s = str(item.GetItemName())
        return s if s else ('vnum %d' % vnum)
    except:
        return ('vnum %d' % vnum)

# ---------------------------------------------------------------------------
# equip() - ekipman raporu (EQUIPMENT_BASE_INDEX = envanter sonrasi slotlar)
# ---------------------------------------------------------------------------
def equip():
    try:
        if not _ingame():
            _write('equip', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player
        eb = 90
        try:
            eb = int(player.EQUIPMENT_BASE_INDEX)
        except:
            eb = 90
        L = ['ekipman (EQUIPMENT_BASE_INDEX=%d, %d slot)' % (eb, 20)]
        n = 0
        for i in range(eb, eb + 20):
            vnum = 0
            try:
                vnum = int(player.GetItemIndex(i))
            except:
                vnum = 0
            if vnum <= 0:
                continue
            n += 1
            iname = _item_name(vnum)
            L.append('  [%3d] vnum=%-7d %s' % (i, vnum, iname))
        L.append('---')
        L.append('giyili esya: %d' % n)
        _write('equip', '\n'.join(L) + '\n')
    except Exception, e:
        _write('equip', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# skill() - beceri raporu (player.GetSkillLevel/GetSkillGrade/IsSkillCoolTime
# + skill.GetSkillName - nighttown kanitli; slot taramasi + index taramasi)
# ---------------------------------------------------------------------------
def _skill_line(L, slot, idx):
    nm = ''
    try:
        import skill
        nm = str(skill.GetSkillName(idx))
    except:
        pass
    lv = ''
    try:
        import player as _player
        lv = ' Lv%s' % str(int(_player.GetSkillLevel(idx)))
    except:
        pass
    gr = ''
    try:
        import player as _player
        g = int(_player.GetSkillGrade(idx))
        if g > 0:
            gr = ' G%s' % str(g)
    except:
        pass
    cd = ''
    if slot is not None:
        try:
            import player as _player
            cd = '  [CD]' if _player.IsSkillCoolTime(slot) else ''
        except:
            pass
    L.append('  slot=%-3s idx=%-4d %s%s%s%s' % (str(slot if slot is not None else '-'), idx, nm, lv, gr, cd))

def skill():
    try:
        if not _ingame():
            _write('skill', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player, net
        L = ['SCENE=%s' % _scene_name()]
        race = -1
        grp = -1
        try:
            race = net.GetMainActorRace()
        except:
            pass
        try:
            grp = net.GetMainActorSkillGroup()
        except:
            pass
        L.append('race=%s (%s) | skill grubu=%s' % (str(race), RACE_TABLE.get(race, ('?', '?'))[0], str(grp)))
        found = False
        # A) slot -> index yolu (player.GetSkillIndex varsa - slot bazli CD de verir)
        try:
            for slot in range(1, 33):
                try:
                    idx = int(player.GetSkillIndex(slot))
                except:
                    break
                if idx <= 0:
                    continue
                found = True
                _skill_line(L, slot, idx)
        except:
            pass
        # B) index taramasi (ogrenilmis beceriler: GetSkillLevel > 0)
        if not found:
            L.append('(GetSkillIndex yok - ogrenilmis beceri taramasi:)')
            for idx in range(1, 130):
                try:
                    if int(player.GetSkillLevel(idx)) > 0:
                        _skill_line(L, None, idx)
                except:
                    continue
        L.append('kullanim: player.ClickSkillSlot(<slot>) + IsSkillCoolTime - cycu kanitli')
        _write('skill', '\n'.join(L) + '\n')
    except Exception, e:
        _write('skill', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# near() - yakin varlik taramasi (VID sweep + chr.GetInstanceType 57 kanit +
# chr.GetNameByVID 52 kanit + nonplayer.GetLevelByVID kanit).
# NOT: GetInstanceList bu istemcide 0 kanit (eski AI'nin onerdigi yok) -
# GOD MOD yontemi: 1..2000 VID gezinmesi, tek komutta <10ms.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# v4.4 NEAR - GENIS VID TARAMASI
# KOK NEDEN (saha testi 10: vid=28878 varken bulunan=0): eski tarama yalniz
# vid 1..2000'e bakiyordu; bu sunucuda VID'ler 20000+ oluyor!
# KANIT YONTEMI (vidscanner.py - MobScanner): chr.GetInstanceType(vid) ile
# 0..4.000.000 kaba tarama; gecerli tip + chr.HasInstance + GetPixelPosition.
# Anlik: vid 1..50000 | Arka plan: 4M'a kadar pencere-dongusu (her Update
# 40000 vid; oyun donmaz) -> bitince C:\\MaxExec\\near_full.txt
# ---------------------------------------------------------------------------
NEAR_SCAN_CHUNK = 40000
NEAR_SCAN_MAX = 4000000
# v4.6: INSTANCE_TYPE_GATE kaldirildi (bu istemcide yok), tip FILTRESI
# kalkti (tasi tip=2 atiliyordu). KANIT sayisal degerler (NightTown dump):
#   0=MOB/ENEMY (kagb 'wykrywaczmetkow' boss dedektoru: a==0 + GetRace ile
#   boss listesi) | 2=METIN TASI (kagb: 'if a==2' metin dedektoru;
#   MetinFinder.SetVIDRange: 'if 2 == chr.GetInstanceType(i)') |
#   6=OYUNCU (eiglib: 'GetInstanceType(vid) == 6' fısıldayan-listesi).
NEAR_TYPES = ('INSTANCE_TYPE_PLAYER', 'INSTANCE_TYPE_NPC', 'INSTANCE_TYPE_ENEMY',
              'INSTANCE_TYPE_BUILDING', 'INSTANCE_TYPE_OBJECT')
NEAR_TYPE_FALLBACK = {0: 'MOB', 2: 'METIN', 6: 'OYUNCU'}

def _near_tnames():
    import chr
    tn = {}
    for c in NEAR_TYPES:
        try:
            tn[int(getattr(chr, c))] = c.replace('INSTANCE_TYPE_', '')
        except:
            pass
    for k, v in NEAR_TYPE_FALLBACK.items():
        tn.setdefault(k, v)   # sabit kanit-degerler (0=MOB 2=METIN 6=OYUNCU)
    return tn

def _near_scan_range(brange, erange):
    """vid araligini tara -> [(vid, tip, x, y)] (vidscanner yontemi)"""
    import chr
    out = []
    gtyp = chr.GetInstanceType
    hexst = chr.HasInstance
    gpos = chr.GetPixelPosition
    # v4.6: tip FILTRESI YOK - her gecerli instance doner (metin tasi tip=2
    # artik listelenir; bilinmeyen tipler 'TIP-n' etiketiyle gorunur)
    for vid in xrange(int(brange), int(erange)):
        try:
            t = int(gtyp(vid))
        except:
            continue
        if t < 0:
            continue
        try:
            if not hexst(vid):
                continue
        except:
            continue
        try:
            p = gpos(vid)
            px, py = int(p[0]), int(p[1])
        except:
            continue
        out.append((vid, t, px, py))
    return out

def _near_row_lines(rows, myvid, mx, my):
    """ortak satir uretici (tip/isim/level/race/morph-ipucu)"""
    import chr, nonplayer
    tnames = _near_tnames()
    L = []
    tc = {}
    for d2, v, t, px, py in rows:
        tl = tnames.get(t, str(t))
        tc[tl] = tc.get(tl, 0) + 1
        nm = ''
        try:
            nm = str(chr.GetNameByVID(v))
        except:
            pass
        lv = ''
        if tl in ('NPC', 'ENEMY', 'METIN', 'MOB', 'OYUNCU'):
            try:
                lv = ' Lv%s' % str(nonplayer.GetLevelByVID(v))
            except:
                pass
        if tl == 'METIN' or tl == 'MOB':
            tl = tl + '*'   # v4.6: metin tasi / mob isareti
        rv = 0
        try:
            rv = int(chr.GetVirtualNumber(v))
        except:
            rv = 0
        hint = ' | morph %d' % rv if rv > 0 else ''
        L.append('  vid=%-6d %-7s dist=%-6d konum=(%d,%d) %s%s%s%s' % (v, tl, int(d2 ** 0.5), px, py, nm, lv, (' race=%d' % rv) if rv > 0 else '', hint))
    L.append('tip sayilari: %s' % ', '.join(['%s=%d' % (k, tc[k]) for k in tc]))
    return L

def near(quickmax=50000):
    """v4.4 GENIS tarama: vid 1..50000 ANLIK (eski 1..2000 buyuk sunucularda
    hicbir sey bulamıyordu). Ayni anda arka plan tam tarama baslar (0..4M,
    kanit: vidscanner.py) - bitince near_full.txt"""
    try:
        if not _ingame():
            _write('near', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import chr
        vid = _my_vid()
        myp = chr.GetPixelPosition(vid)
        mx, my = int(myp[0]), int(myp[1])
        try:
            qm = int(quickmax)
        except:
            qm = 50000
        if qm <= 0 or qm > 500000:
            qm = 50000
        rows = []
        for v, t, px, py in _near_scan_range(1, qm):
            if v == vid or (px == 0 and py == 0):
                continue
            dx = px - mx; dy = py - my
            d2 = dx * dx + dy * dy
            if d2 > 100000000:
                continue
            rows.append((d2, v, t, px, py))
        rows.sort()
        L = ['benim vid=%d konum=(%d,%d) | ANLIK tarama: vid 1..%d, bulunan=%d' % (vid, mx, my, qm, len(rows))]
        L.extend(_near_row_lines(rows[:60], vid, mx, my))
        if len(rows) > 60:
            L.append('  ... +%d varlik daha (yakinlik sirali)' % (len(rows) - 60))
        L.append('---')
        L.append('secme: chr.SelectInstance(<vid>) | hedefe donus: morphtarget (tikla once)')
        L.append('race=X -> morph <race> / spawn <race> (demirci=20016)')
        L.append('v4.6: METIN* = metin tasi (tip=2) | MOB* = yaratik (tip=0) | OYUNCU (tip=6)')
        L.append('tip sayilari (kayit): 0=MOB 1=NPC 2=METIN 6=OYUNCU - digerleri TIP-n')
        L.append('ARKA PLAN tam tarama (0..%d) basladi -> bittiğinde: C:\\MaxExec\\near_full.txt' % NEAR_SCAN_MAX)
        _near_full_start()
        _write('near', '\n'.join(L) + '\n')
    except Exception, e:
        _write('near', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# v4.5 KOK-NEDEN DUZELTISI: ui taban sinifi buraya (siniflardan ONCE)
# tasindi. v4.4'te 'ui_WindowBase = _ui_mod.ScriptWindow' tanimi asagida
# (v4.2 bolumunde) idi; _NearScanWnd/_GoTakeWnd/_AntiFlyWnd gibi v4.4
# siniflari tanimdan ONCE kullaniyordu -> import sirasinda NameError ->
# exec basarisiz -> BootImport eski pylib.py v3.2'ye dusuyordu ('PYTHON
# HATASI' ailesinin gercek kok nedeni). Artik sira: TANIM -> siniflar.
# 'import ui' korumali: ui yuklu degilse yedek taban kullanilir (dongu
# pencereleri zaten KOMUT aninda kurulur - o zamana ui kesin yukludur).
# ---------------------------------------------------------------------------
try:
    import ui as _ui_mod
except Exception:
    _ui_mod = None
try:
    ui_WindowBase = _ui_mod.ScriptWindow
except Exception:
    class ui_WindowBase(object):   # v4.5 yedek taban (ui sonra yuklenir)
        def __init__(self): pass
        def Show(self): pass
        def Hide(self): pass
        def Destroy(self): pass
        def SetTop(self): pass

_NEAR = {'win': None, 'phase': 0, 'rows': {}}

class _NearScanWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            import chr
            st = _NEAR
            brange = st['phase']
            if brange >= NEAR_SCAN_MAX:
                self._finish()
                return
            erange = brange + NEAR_SCAN_CHUNK
            myp = None
            try:
                myp = chr.GetPixelPosition(_my_vid())
            except:
                pass
            for v, t, px, py in _near_scan_range(brange, erange):
                if myp is not None:
                    dx = px - int(myp[0]); dy = py - int(myp[1])
                    d2 = dx * dx + dy * dy
                else:
                    d2 = 999999999
                st['rows'][v] = (t, px, py, d2)
            st['phase'] = erange
            if (erange // NEAR_SCAN_CHUNK) % 10 == 0:
                _live('NEAR: tam tarama %%%d (bulunan=%d)' % (erange * 100 // NEAR_SCAN_MAX, len(st['rows'])))
        except Exception, e:
            _live('NEAR tarama hatasi: ' + _fmt_error(e))
            _near_full_stop()

    def _finish(self):
        st = _NEAR
        try:
            import chr
            vid = _my_vid()
            myp = None
            try:
                myp = chr.GetPixelPosition(vid)
            except:
                pass
            rows = []
            for v, (t, px, py, d2) in st['rows'].items():
                if v == vid:
                    continue
                rows.append((d2, v, t, px, py))
            rows.sort()
            L = []
            if myp is not None:
                L.append('benim vid=%d konum=(%d,%d)' % (vid, int(myp[0]), int(myp[1])))
            L.append('TAM TARAMA bitti: %d varlik (vid 0..%d)' % (len(rows), NEAR_SCAN_MAX))
            L.extend(_near_row_lines(rows[:300], vid, 0, 0))
            if len(rows) > 300:
                L.append('  ... +%d varlik daha' % (len(rows) - 300))
            f = open(r'C:\MaxExec\near_full.txt', 'w')
            f.write('\n'.join(L) + '\n')
            f.close()
            _live('NEAR: tam tarama bitti -> %d varlik | tam liste: C:\\MaxExec\\near_full.txt' % len(rows))
        except Exception, e:
            _live('NEAR finish hatasi: ' + _fmt_error(e))
        _near_full_stop()

def _near_full_start():
    if _NEAR['win'] is None:
        _NEAR['phase'] = 0
        _NEAR['rows'] = {}
        _NEAR['win'] = _NearScanWnd()
        _live('NEAR: arka plan tam tarama basladi (0..%d)' % NEAR_SCAN_MAX)

def _near_full_stop():
    try:
        if _NEAR['win'] is not None:
            _NEAR['win'].Hide()
            _NEAR['win'].Destroy()
    except:
        pass
    _NEAR['win'] = None

# ---------------------------------------------------------------------------
# chat / whisper - sohbet (net.SendChatPacket cycu + 117 kanit;
# net.SendWhisperPacket 9 kanit). Slash komutlari da chat ile gider.
# ---------------------------------------------------------------------------
def chat(msg):
    try:
        if not _ingame():
            _write('chat', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import net
        s = str(msg)
        net.SendChatPacket(s)
        tag = ' (slash komutu)' if s.startswith('/') else ''
        _write('chat', 'OK gonderildi: "%s"%s' % (s[:80], tag))
    except Exception, e:
        _write('chat', 'HATA ' + _fmt_error(e) + '\n')

def whisper(who, msg):
    try:
        if not _ingame():
            _write('whisper', 'HATA: oyunda degilsin\n')
            return
        import net
        net.SendWhisperPacket(str(who), str(msg))
        _write('whisper', 'OK -> %s: "%s"' % (str(who)[:24], str(msg)[:80]))
    except Exception, e:
        _write('whisper', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# HIZLI EYLEMLER (cycu.py kanitlari)
# ---------------------------------------------------------------------------
def ride():
    chat('/ride')            # cycu: net.SendChatPacket('/ride')

def revive():
    try:
        if not _ingame():
            _write('revive', 'HATA: oyunda degilsin\n')
            return
        import chr
        chr.Revive()
        _write('revive', 'OK: chr.Revive() - hayata dondun (cycu kaniti)')
    except Exception, e:
        _write('revive', 'HATA ' + _fmt_error(e) + '\n')

def logout():
    chat('/logout')          # cycu: '/logout' -> sonraki: waitfor SelectCharacterWindow

def back():
    chat('/phase_select')    # cycu: '/phase_select' -> karakter secim ekranina donus

def zoom(dist):
    try:
        d = int(dist)
        import app
        app.SetCameraMaxDistance(d)
        _write('zoom', 'OK: app.SetCameraMaxDistance(%d) (cycu kaniti: 12000)' % d)
    except Exception, e:
        _write('zoom', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# ESYA ISLEMLERI (net.SendItemUsePacket 218 kanit; player.PickCloseItem 15
# kanit; net.SendItemDropPacketNew cycu kaniti - DESTRUKTIF!)
# ---------------------------------------------------------------------------
def use(slot):
    try:
        if not _ingame():
            _write('use', 'HATA: oyunda degilsin\n')
            return
        import net
        s = int(slot)
        net.SendItemUsePacket(s)
        _write('use', 'OK: net.SendItemUsePacket(%d) - slot inv raporundaki numara' % s)
    except Exception, e:
        _write('use', 'HATA ' + _fmt_error(e) + '\n')

def pickup():
    try:
        if not _ingame():
            _write('pickup', 'HATA: oyunda degilsin\n')
            return
        import player
        player.PickCloseItem()
        _write('pickup', 'OK: player.PickCloseItem() - en yakin esya alindi')
    except Exception, e:
        _write('pickup', 'HATA ' + _fmt_error(e) + '\n')

def drop(slot, count):
    try:
        if not _ingame():
            _write('drop', 'HATA: oyunda degilsin\n')
            return
        import net
        s = int(slot); c = int(count)
        net.SendItemDropPacketNew(s, c)
        _write('drop', 'OK: net.SendItemDropPacketNew(%d, %d) - YERDE, geri alinabilir mi kontrol et!' % (s, c))
    except Exception, e:
        _write('drop', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# HAREKET (chr.MoveToDestPosition 36 kanit - yuruyus; chr.SetPixelPosition
# 211 kanit - isinlama, 2-arg desen: chr.SetPixelPosition(x, y))
# ---------------------------------------------------------------------------
def goto(x, y):
    try:
        if not _ingame():
            _write('goto', 'HATA: oyunda degilsin\n')
            return
        import player, chr, net
        vid = 0
        try:
            vid = int(player.GetMainCharacterIndex())
        except:
            try:
                vid = int(net.GetMainActorVID())
            except:
                vid = 0
        chr.MoveToDestPosition(vid, int(x), int(y))
        _write('goto', 'OK: chr.MoveToDestPosition(vid=%d, %d, %d) - yuruyus basladi (36 kanit)' % (vid, int(x), int(y)))
    except Exception, e:
        _write('goto', 'HATA ' + _fmt_error(e) + '\n')

def tp(x, y):
    try:
        if not _ingame():
            _write('tp', 'HATA: oyunda degilsin\n')
            return
        import chr, player
        # v4.2 GUVENLIK: 1-arg SetPixelPosition SECILI instance'a gider
        # (PythonCharacterModule.cpp kaniti) - morph/klon secimi bozmasin
        try:
            chr.SelectInstance(int(player.GetMainCharacterIndex()))
        except:
            pass
        chr.SetPixelPosition(int(x), int(y))
        _write('tp', 'OK: chr.SetPixelPosition(%d, %d) - isinlanma (211 kanit; 2-arg desen)' % (int(x), int(y)))
        pos()
    except Exception, e:
        _write('tp', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# GIRDI SIMULASYONU (player.SetSingleDIKKeyState 368 kanit!
# player.SetAttackKeyState 100 kanit) - key/attack
# ---------------------------------------------------------------------------
def key(dikname, down):
    try:
        import app, player
        code = None
        try:
            code = int(dikname)
        except:
            code = getattr(app, 'DIK_' + str(dikname).upper(), None)
        if code is None:
            _write('key', 'HATA: DIK_%s bulunamadi (bilinenler: UP DOWN LEFT RIGHT SPACE LSHIFT W A S D B F5)\n' % str(dikname).upper())
            return
        st = 1 if (int(down) if str(down).isdigit() else 1) else 0
        player.SetSingleDIKKeyState(code, st)
        _write('key', 'OK: SetSingleDIKKeyState(DIK_%s=%s, %s)' % (str(dikname).upper(), str(code), 'BASILI' if st else 'birakildi'))
    except Exception, e:
        _write('key', 'HATA ' + _fmt_error(e) + '\n')

def attack(mode):
    try:
        if not _ingame():
            _write('attack', 'HATA: oyunda degilsin\n')
            return
        import player
        m = 1 if (int(mode) if str(mode).isdigit() else 1) else 0
        player.SetAttackKeyState(m)
        _write('attack', 'OK: SetAttackKeyState(%d) - %s (100 kanit)' % (m, 'SALDIRI BASILI' if m else 'birakildi'))
    except Exception, e:
        _write('attack', 'HATA ' + _fmt_error(e) + '\n')

# ===========================================================================
# v4.1 - KESIF KOMUTLARI (oyundaki Python dosyalarini bulma + dokme + tarama)
# ESKI AI DOGRULARI/YANLISLARI - GOD MOD hukmu + SAHA TESTI 8 hukmu:
#   * app.GetFileList("*.py"): eski AI "en iyi yontem" dedi - YALANDI.
#     SAHA TESTI 8: calisiyor AMA SADECE DISK dosyalarini veriyor (73'ü de
#     kullanici botlari; oyunun kendi modulleri listede YOK). Disk keşfi
#     icin faydali, pack icin ise YARARSIZ.
#   * app.OpenTextFile + GetTextFileLineCount + GetTextFileLine: KISMEN.
#     cycu.py kanitli AMA SAHA TESTI 8: pack dosyalarinda handle verip
#     0 SATIR donduruyor (59 modul 2 bayt cikti). Disk dosyalarinda
#     calisir. YEDEK olarak kalir.
#   * pack.Exist + pack.Get: GERCEK YOL - dump'lanan calisan botlarin
#     kendi kodunda kanitli (FileExtractor.py ExtractScript + New_Levelbot
#     pack.Get("playersettingmodule.py") root pack'ten KAYNAK okuyor!).
#   * pack_open(ad, mod): dosya-objesi (read/readlines) - edithack +
#     itemcreator'un pack icindeki item_list.txt'yi okuma yolu.
#   * sys.modules: dogru - yuklu 130 modulu verir (bedava, risksiz);
#     v4.1 pydumpall hedef listesi ARTIK buradan canli uretilir.
#   * pkgutil.iter_modules: embedded importer'da calismaz (saha: ImportError)
#   * os.listdir: disk aciksa calisir (saha: 73 bot dosyasi buldu)
# ===========================================================================

# --- v4.1: pack API kanit durumu (pyfiles raporunda guncellenir) ---
_PACK_API = {'Exist': False, 'Get': False, 'pack_open': False, 'dir': []}

# SAHA KANITI: oyunun kendi log'unda gorulen UI script dosyalari
# (locale/ro/ui/ + UIScript/ + uiscript/ pack yollari)
_UI_SCRIPT_PATHS = (
    'locale/ro/ui/selectcharacterwindow.py', 'locale/ro/ui/InventoryWindow.py',
    'locale/ro/ui/dragonsoulwindow.py', 'locale/ro/ui/dragonsoulrefinewindow.py',
    'locale/ro/ui/SystemDialog.py', 'locale/ro/ui/passworddialog.py',
    'locale/ro/ui/giftbox.py', 'locale/ro/ui/EnergyBar.py',
    'locale/ro/ui/WebWindow.py', 'locale/ro/ui/TaskBar.py',
    'UIScript/LoadingWindow.py', 'UIScript/CharacterWindow.py',
    'UIScript/BeltInventoryWindow.py', 'UIScript/PickMoneyDialog.py',
    'UIScript/PopupDialog.py', 'UIScript/AtlasWindow.py',
    'UIScript/SafeboxWindow.py', 'UIScript/MallWindow.py',
    'UIScript/exchangedialog.py', 'UIScript/shopdialog.py',
    'UIScript/restartdialog.py', 'UIScript/PrivateShopBuilder.py',
    'UIScript/MouseButtonWindow.py', 'UIScript/RightMouseButtonWindow.py',
    'UIScript/HelpWindow.py', 'UIScript/CubeWindow.py',
    'UIScript/CubeResultWindow.py', 'UIScript/selectitemwindow.py',
    'UIScript/MiniMap.py', 'UIScript/gamewindow.py',
    'uiscript/questiondialog.py', 'uiscript/questiondialog2.py',
    'uiscript/refinedialog.py', 'uiscript/attachstonedialog.py',
    'uiscript/popupdialog.py', 'uiscript/changepassworddialog.py',
    'uiscript/restartdialog.py', 'uiscript/sash_combinewindow.py',
    'uiscript/sash_absorbwindow.py',
)

# stdlib/sistem modulleri - pack'te kaynagi YOK, Exist denemesi ziyan
_STDLIB_SKIP = (
    'sys', 'os', 'nt', 'ntpath', 'stat', 'string', 're', 'math', 'time',
    'imp', 'marshal', 'signal', 'site', 'types', 'errno', 'abc', 'codecs',
    'operator', 'functools', 'traceback', 'linecache', 'encodings',
    'copy_reg', 'genericpath', 'sre_compile', 'sre_constants', 'sre_parse',
    'sysconfig', 'UserDict', 'exceptions', 'locale', '_locale',
)

def _name_variants(name):
    """v4.1: bir modul adini pack icinde aranabilir tam yol adaylarina
    genisletir (buyuk-kucuk harf oyunu kanitli: introLogin.py + intrologin)."""
    nm = str(name).strip().replace('\\', '/').lstrip('/')
    while nm.startswith('./'):
        nm = nm[2:]
    base = nm[:-3] if nm.lower().endswith('.py') else nm
    low = base.lower()
    cap = low[0].upper() + low[1:]
    # dogrudan yol zaten klasorlu geldiyse varyantlara dokunma
    out = []
    def _push(v):
        if v and v not in out:
            out.append(v)
    if '/' in nm:
        _push(nm if nm.lower().endswith('.py') else nm + '.py')
        _push(nm)
        return out
    for cand in (base, low, cap):
        _push(cand + '.py')
        _push(cand)
    for pre in ('root/', 'locale/ro/ui/', 'locale/tr/ui/',
                'UIScript/', 'uiscript/'):
        _push(pre + low + '.py')
        _push(pre + cap + '.py')
    return out

def _pack_read(name):
    """v4.1 KANITLI 4-KATMANLI OKUMA ZINCIRI (en guclu once):
      1) pack.Exist + pack.Get  (FileExtractor.py:407 + New_Levelbot.py:363)
      2) pack_open(ad,'r')      (edithack.py:888 + itemcreator.py:418)
      3) app.OpenTextFile + GetTextFileLineCount/Line (cycu.py:92; pack'te
         0 satir verdigi icin yedek)
      4) disk open
    Donus: (yontem-adi, icerik-str) | (None, hata-aciklamasi)
    icerik her zaman str; binary ise repr degil ham bytes-decode denenir."""
    nm = str(name)
    # --- 0) v4.7: pack modulunu ONCE sys.modules'dan DIREKT al (import
    #     zinciri hic ismesin - saha raporu: gomulu pylib'de serverinfo.py
    #     dumplanmadi; disk dosyalari dustu. sys.modules her zaman gercek
    #     C modulunu verir - oyun kendi importcusuna (system.py
    #     __pack_import) hicbir sorgu yollamaz) ---
    _pm = None
    try:
        import sys as _sysp
        _pm = _sysp.modules.get('pack', None)
        if _pm is not None:
            _PACK_API['sysmod'] = True
    except:
        _pm = None
    if _pm is None:
        try:
            import pack as _pm
        except Exception:
            _pm = None
    if _pm is None:
        try:
            import sys as _sysp2
            _mn = _sysp2.modules.get('__main__', None)
            if _mn is not None:
                _pm = getattr(_mn, 'pack', None)
        except:
            _pm = None
    # --- 1) pack.Get (EN GUCLU - root pack kaynak okuma kaniti) ---
    try:
        if _pm is None:
            raise ImportError('pack modulu bulunamadi (sys.modules/import/__main__)')
        _packmod = _pm
        try:
            if _packmod.Exist(nm):
                try:
                    c = _packmod.Get(nm)
                    if c:
                        try:
                            return ('pack.Get', str(c))
                        except:
                            return ('pack.Get', repr(c))
                    if c == '':
                        # var ama bos: notla ama devam etme - pack'te gercekten bos
                        return ('pack.Get', '')
                except AttributeError:
                    _PACK_API['Get'] = False
        except AttributeError:
            _PACK_API['Exist'] = False
        # --- 2) pack_open (dosya-objesi yolu) ---
        po = None
        try:
            po = pack_open  # global builtin (istemci injected)
            _PACK_API['pack_open'] = True
        except NameError:
            po = None
        if po is None:
            try:
                po = getattr(_packmod, 'pack_open', None)
                if po is not None:
                    _PACK_API['pack_open'] = True
            except:
                po = None
        if po is None:
            try:
                import sys as _sysp3
                _mn = _sysp3.modules.get('__main__', None)
                if _mn is not None:
                    po = getattr(_mn, 'pack_open', None)
                    if po is not None:
                        _PACK_API['pack_open'] = True
            except:
                po = None
        if po is not None:
            for mode in ('r', 'rb'):
                try:
                    f = po(nm, mode)
                    data = f.read()
                    try:
                        f.close()
                    except:
                        pass
                    if data:
                        try:
                            return ('pack_open.' + mode, str(data))
                        except:
                            return ('pack_open.' + mode, repr(data))
                    if data == '':
                        return ('pack_open.' + mode, '')
                except:
                    continue
    except ImportError:
        pass
    # --- 3) app.OpenTextFile (cycu deseni - disk dosyalarinda calisir) ---
    try:
        import app as _app
        try:
            h = _app.OpenTextFile(nm)
            if h:
                n = 0
                try:
                    n = int(_app.GetTextFileLineCount(h))
                except:
                    n = 0
                if n > 0:
                    ln = []
                    for i in range(min(n, 20000)):
                        try:
                            ln.append(_app.GetTextFileLine(h, i))
                        except:
                            ln.append('')
                    return ('app.OpenTextFile', '\n'.join(ln) + '\n')
        except:
            pass
    except ImportError:
        pass
    # --- 4) disk (en son yedek) ---
    try:
        f2 = open(nm, 'r')
        data = f2.read()
        f2.close()
        return ('disk', data)
    except:
        pass
    return (None, 'acilamadi: ' + nm)


_KNOWN_CLIENT_MODULES = (
    # C modulleri (dahili)
    'app', 'net', 'player', 'chr', 'item', 'nonplayer', 'background', 'skill',
    'chat', 'guild', 'messenger', 'quest', 'event', 'wndMgr', 'grp', 'grpText',
    'grpImage', 'ime', 'snd', 'effect', 'fly', 'mood', 'dbg', 'exception',
    'miniMap', 'web', 'profiler', 'pack', 'filer',
    # python tarafli client modulleri (case varyantlariyla)
    'system', 'systemhide', 'constInfo', 'constinfo', 'localeInfo', 'localeinfo',
    'serverInfo', 'serverinfo', 'ServerInfo', 'colorInfo', 'playerSettingModule',
    'playersettingmodule', 'itemdata', 'ui', 'uiScript', 'uiCommon', 'uiTip',
    'uiSystem', 'uiInventory', 'uiCharacter', 'uiTarget', 'uiChat', 'uiGuild',
    'uiMessenger', 'uiQuest', 'uiPrivateShop', 'uiShop', 'uiExchange',
    'uiOption', 'uiHelp', 'uiMap', 'uiAffect', 'uiMiniMap', 'uiGameOption',
    'uiWhisper', 'uiDragonSoul', 'uiPet', 'interfacemodule', 'interfaceModule',
    'game', 'introLogin', 'intrologin', 'introSelect', 'introselect',
    'introCreate', 'introcreate', 'introLoading', 'introloading',
    'introLogo', 'intrologo', 'introEmpire', 'introempire',
    # kullanici ekosistemi (nighttown)
    'm2kmod', 'pyDetour', 'switchbot', 'hackbar',
)

def _discover_pyfiles():
    """5 yontemi de calistirir; dict dondurur. Hepsi guard'li - hata notlara."""
    res = {'app.GetFileList': [], 'sys.modules': [], 'pkgutil': [],
           'disk': [], 'probe': [], 'notlar': [], 'getfilelist_var': False}
    # --- [1] app.GetFileList (eski AI'nin "en iyi" dedigi; bu client'ta 0 kanit)
    try:
        import app
        if hasattr(app, 'GetFileList'):
            res['getfilelist_var'] = True
            try:
                fl = app.GetFileList('*.py')
                for f in fl:
                    try:
                        res['app.GetFileList'].append(str(f))
                    except:
                        pass
            except Exception, e:
                res['notlar'].append('app.GetFileList VAR ama cagri hatasi: ' + _fmt_error(e))
        else:
            res['notlar'].append('app.GetFileList BU ISTEMCIDE YOK (beklenen: 0 kanit) - OpenTextFile yolu kullanilacak')
    except Exception, e:
        res['notlar'].append('app modulu yok?: ' + _fmt_error(e))
    # --- [2] sys.modules (yuklu moduller - eski AI dogru soylemisti)
    try:
        for k in sys.modules.keys():
            try:
                if k and '.' not in k and not k.startswith('_'):
                    res['sys.modules'].append(str(k))
            except:
                pass
        res['sys.modules'].sort()
    except:
        pass
    # --- [3] pkgutil.iter_modules (embedded importer desteklemeyebilir)
    try:
        import pkgutil
        cnt = 0
        for mi in pkgutil.iter_modules():
            try:
                n = getattr(mi, 'name', None) or str(mi)
                res['pkgutil'].append(str(n))
                cnt += 1
                if cnt > 500:
                    break
            except:
                pass
        res['pkgutil'].sort()
    except Exception, e:
        res['notlar'].append('pkgutil.iter_modules kullanilamadi (%s) - embedded importer desteklemiyor olabilir (beklenen)' % _fmt_error(e))
    # --- [4] disk taramasi (cwd + sys.path + TEMP/TMP - kullanici notu:
    #      nighttown workspace'te, degilse temp/tmp'te)
    roots = []
    try:
        roots.append(str(os.getcwd()))
    except:
        pass
    for p in sys.path:
        try:
            if p and os.path.isdir(str(p)):
                roots.append(str(p))
        except:
            pass
    for envk in ('TEMP', 'TMP'):
        try:
            v = os.environ.get(envk, '')
            if v and os.path.isdir(v):
                roots.append(v)
        except:
            pass
    seen = []
    for r in roots:
        if r not in seen:
            seen.append(r)
    disk = []
    try:
        for r in seen[:40]:
            try:
                for fn in os.listdir(r):
                    try:
                        if str(fn).lower().endswith('.py') and str(fn) not in disk:
                            full = os.path.join(r, str(fn))
                            try:
                                if os.path.isfile(full):
                                    disk.append(str(fn))
                            except:
                                disk.append(str(fn))
                    except:
                        pass
            except:
                pass
    except:
        pass
    disk.sort()
    res['disk'] = disk
    res['roots'] = seen
    # --- [5] import-probe (bilinen metin2 modulleri - import denemesi bedava)
    for mname in _KNOWN_CLIENT_MODULES:
        try:
            if mname in sys.modules:
                res['probe'].append(mname)
                continue
            __import__(mname)
            res['probe'].append(mname)
        except:
            pass
    # --- [6] v4.1: pack API kesfi + modul __file__ taramasi (SAHA TESTI 8
    #      sonrasi: pack.Exist/pack.Get/pack_open GERCEK okuma yolu) ---
    try:
        import pack as _pk
        try:
            _PACK_API['dir'] = [str(x) for x in dir(_pk)]
        except:
            pass
        for fn in ('Exist', 'Get', 'GetList', 'Open', 'pack_open', 'IsExist'):
            try:
                if hasattr(_pk, fn):
                    _PACK_API[fn] = True
            except:
                pass
        res['pack_api'] = dict(_PACK_API)
    except Exception, e:
        res['notlar'].append('pack modulu yok/okunamadi: ' + _fmt_error(e))
    try:
        po = None
        try:
            po = pack_open
            _PACK_API['pack_open'] = True
        except NameError:
            pass
        res['pack_open_global'] = (po is not None)
    except:
        res['pack_open_global'] = False
    mf = []
    try:
        for k in sys.modules.keys():
            try:
                m = sys.modules[k]
                f = getattr(m, '__file__', None)
                if f:
                    mf.append(str(k) + ' -> ' + str(f))
            except:
                pass
        mf.sort()
    except:
        pass
    res['modfiles'] = mf
    return res

def pyfiles():
    try:
        disc = _discover_pyfiles()
        L = ['py dosyasi kesif raporu (5 yontem)  t=' + time.strftime('%H:%M:%S'), '']
        gfl = disc.get('app.GetFileList', [])
        L.append('[1] app.GetFileList("*.py") - %s' % ('VAR' if disc.get('getfilelist_var') else 'BU ISTEMCIDE YOK (0 kanit - eski AI yanildi)'))
        if gfl:
            for f in gfl[:60]:
                L.append('    ' + f)
            if len(gfl) > 60:
                L.append('    ... +%d daha' % (len(gfl) - 60))
        L.append('')
        sm = disc.get('sys.modules', [])
        L.append('[2] sys.modules (yuklu moduller): %d' % len(sm))
        if sm:
            L.append('    ' + ', '.join(sm[:90]))
        L.append('')
        pk = disc.get('pkgutil', [])
        L.append('[3] pkgutil.iter_modules: %s' % ('%d modul' % len(pk) if pk else 'bos/kullanilamaz (embedded importer - beklenen)'))
        if pk:
            L.append('    ' + ', '.join(pk[:80]))
        L.append('')
        dk = disc.get('disk', [])
        L.append('[4] disk taramasi (cwd + sys.path + TEMP/TMP): %d dosya' % len(dk))
        try:
            for r in disc.get('roots', [])[:12]:
                L.append('    tarama yolu: %s' % r)
        except:
            pass
        if dk:
            for f in dk[:60]:
                L.append('    ' + f)
            if len(dk) > 60:
                L.append('    ... +%d daha' % (len(dk) - 60))
        L.append('')
        pr = disc.get('probe', [])
        L.append('[5] import-probe (bilinen moduller): %d bulundu' % len(pr))
        if pr:
            L.append('    ' + ', '.join(pr))
        L.append('')
        for n in disc.get('notlar', []):
            L.append('NOT: ' + n)
        L.append('')
        # v4.1: pack API kesfi (SAHA TESTI 8: GERCEK pack okuma yolu)
        pa = disc.get('pack_api') or {}
        L.append('[6] pack API kesfi (v4.1 - GERCEK pack okuma yolu):')
        try:
            import pack as _pk
            L.append('    pack.Exist  : %s' % ('VAR' if pa.get('Exist') else 'YOK?'))
            L.append('    pack.Get    : %s  (kanit: New_Levelbot.py 363 - root pack kaynak okuyor)' % ('VAR' if pa.get('Get') else 'YOK?'))
            L.append('    pack_open   : %s  (kanit: edithack.py 888 + itemcreator.py 418)' % ('VAR' if (pa.get('pack_open') or disc.get('pack_open_global')) else 'YOK?'))
            dd = pa.get('dir') or []
            if dd:
                L.append('    dir(pack)   : %s' % ', '.join(dd[:40]))
        except ImportError:
            L.append('    pack modulu import edilemedi')
        L.append('    NOT: app.GetFileList SADECE DISK listeler (saha testi 8);')
        L.append('    oyun modulleri root PACK icinde -> pack.Get yolu kullanilir')
        L.append('')
        mf = disc.get('modfiles', [])
        L.append('[7] modul __file__ raporu: %d modul dosya yolu bildiriyor' % len(mf))
        for row in mf[:40]:
            L.append('    ' + row)
        if len(mf) > 40:
            L.append('    ... +%d daha' % (len(mf) - 40))
        L.append('')
        L.append('SONRAKI: pydump <ad> (tek dosya) | pydumpall (hepsi) | pyscan <modul> | plusquest')
        _write('pyfiles', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pyfiles', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pydump(name) - v4.1: tek dosyayi KANITLI zincirle dok
#   pack.Get -> pack_open -> app.OpenTextFile -> disk  (cycu v4.0'daki tek
#   yontem pack'te 0 satir veriyordu - saha testi 8 kaniti)
# ---------------------------------------------------------------------------
def pydump(name=None):
    try:
        if not name:
            _write('pydump', 'kullanim: pydump <dosya-ad>  (orn. pydump introLogin | pydump game | adaylar: pyfiles)\n')
            return
        nm = str(name).strip()
        base = nm[:-3] if nm.lower().endswith('.py') else nm
        cands = _name_variants(base)
        used = None
        method = None
        text = None
        for c in cands:
            m, data = _pack_read(c)
            if m is not None and data:
                used = c
                method = m
                text = data
                break
            if m is not None and data == '':
                # var ama bos - kaydet ve dur (pack'te gercekten bos dosya)
                used = c
                method = m + ' (BOS!)'
                text = ''
                break
        if text is None:
            # v4.7: C modulu ise (player/chr/net/...) API stub yaz
            if base in _KNOWN_CLIENT_MODULES:
                try:
                    stub = _cmod_stub(base)
                    f = open(_dump_name(safe + '.py'), 'w')
                    f.write(stub)
                    f.close()
                    _write('pydump', 'OK: %s C modulu -> API-STUB yazildi (%d satir; kaynak .py yok - dump\\%s.py)\norn: pyscan %s canli katalog' % (base, stub.count(chr(10)), safe, base))
                    return
                except:
                    pass
            _write('pydump', 'HATA: hicbir yontemle acilamadi: %s\nDenenen adaylar (%d): %s\nNot: pyfiles raporundaki isimleri kullan; oyun modulleri pack icindedir (pack.Get yolu)\n' % (nm, len(cands), ', '.join(cands[:12])))
            return
        safe = ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in base]) or 'adsiz'
        try:
            f = open(_dump_name(safe + '.py'), 'w')
            f.write(text)
            f.close()
        except Exception, e2:
            _write('pydump', 'HATA yazma: %s\n' % _fmt_error(e2))
            return
        ln = text.split('\n')
        L = ['OK: %s -> dump\\%s.py  (yontem: %s | %d satir, %d byte)' % (used, safe, method, len(ln), len(text)),
             '--- ilk 40 satir ---']
        L.extend(ln[:40])
        if len(ln) > 40:
            L.append('... (%d satir daha - tam dosya dump klasorunde)' % (len(ln) - 40))
        _write('pydump', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pydump', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pydumpall() - v4.1: TUM py dosyalarini KANITLI zincirle dump\ + INDEX.txt
#   hedefler: canli sys.modules (oyunun kendi modulleri!) + import-probe +
#   disk/GetFileList + UI script yollari. Okuma: pack.Get -> pack_open ->
#   app.OpenTextFile -> disk. 0 byte'lar 'BOS' isaretlenir (sahte OK yok).
# ---------------------------------------------------------------------------
def _cmod_stub(modname):
    """C modulu icin API stub kaynagi uret (v4.7 - dump klasorunde
    player.py/chr.py/net.py gercek dir() icerigiyle olusur)."""
    import sys as _sysc
    m = _sysc.modules.get(modname, None)
    if m is None:
        try:
            m = __import__(modname)
        except:
            m = None
    L = ['# -*- coding: utf-8 -*-',
         '# %s - DAHILI C MODULU (kaynak .py YOK - Plusmaxgod v4.7 API STUB)' % modname,
         '# dir(%s) introspection: sabitler + fonksiyon listesi (gercek degerler)' % modname,
         '']
    if m is None:
        L.append('# (modul su an import edilemedi)')
        return chr(10).join(L) + chr(10)
    try:
        names = dir(m)
    except:
        names = []
    for nm in sorted(names):
        if nm.startswith('__'):
            continue
        try:
            v = getattr(m, nm)
        except:
            continue
        tv = type(v).__name__
        if tv in ('builtin_function_or_method', 'function'):
            L.append('def %s(*args): pass   # C fonksiyonu (imza bilinmiyor)' % nm)
        elif tv == 'int':
            L.append('%s = %d' % (nm, int(v)))
        elif tv == 'str':
            L.append('%s = %r' % (nm, str(v)))
        elif tv == 'module':
            L.append('# (alt modul: %s)' % nm)
        else:
            L.append('%s = None   # tip: %s' % (nm, tv))
    return chr(10).join(L) + chr(10)

def pydumpall():
    try:
        disc = _discover_pyfiles()
        # --- hedef listesi v4.1 ---
        # (1) canli sys.modules: oyunun kendi modulleri (en degerli kisim)
        targets = []          # (gorunen-ad, arama-adi, hedef-kaynak-not)
        seen_names = []
        for mn in disc.get('sys.modules', []):
            if mn in _STDLIB_SKIP:
                continue
            if mn not in seen_names:
                seen_names.append(mn)
                targets.append((mn, mn, 'sys.modules'))
        # (2) import-probe artiklari (sys.modules'te olmayan varsa)
        for mn in disc.get('probe', []):
            if mn in _STDLIB_SKIP or mn in seen_names:
                continue
            seen_names.append(mn)
            targets.append((mn, mn, 'probe'))
        # (3) disk + GetFileList (kullanici botlari - birebir isim)
        gfl = disc.get('app.GetFileList', [])
        for fname in disc.get('disk', []) + gfl:
            base = fname[:-3] if str(fname).lower().endswith('.py') else fname
            if base not in seen_names:
                seen_names.append(base)
                targets.append((base, base, 'disk'))
        # (4) UI script yollari (oyun log kanitli pack yollari)
        uihit = []
        for upath in _UI_SCRIPT_PATHS:
            m, data = _pack_read(upath)
            if m is not None:
                uihit.append((upath, m, len(data or '')))
        cap = 600
        targets = targets[:cap]
        pa = disc.get('pack_api') or {}
        n_sys = len([t for t in targets if t[2] == 'sys.modules'])
        n_prb = len([t for t in targets if t[2] == 'probe'])
        n_dsk = len([t for t in targets if t[2] == 'disk'])
        idx = ['PLUSMAXGOD pydumpall INDEX (v4.1 kanitli zincir)  t=' + time.strftime('%Y-%m-%d %H:%M:%S'),
               'pack API: Exist=%s Get=%s pack_open=%s (kanit: FileExtractor/New_Levelbot/edithack/itemcreator)' % (
                   pa.get('Exist', '?'), pa.get('Get', '?'), pa.get('pack_open', disc.get('pack_open_global', '?'))),
               'hedefler: sys.modules=%d probe-artigi=%d disk=%d UI-script-hit=%d | cap %d' % (
                   n_sys, n_prb, n_dsk, len(uihit), cap),
               '']
        if disc.get('notlar'):
            for n in disc['notlar']:
                idx.append('NOT: ' + n)
            idx.append('')
        okc = 0
        errc = 0
        boc = 0
        errs = []
        methods = {}
        c = 0
        for gname, sname, src in targets:
            c += 1
            if (c % 25) == 0:
                try:
                    sys.stdout.write('[PYDUMPALL] ilerleme %d/%d\n' % (c, len(targets)))
                except:
                    pass
            text = None
            used = None
            method = None
            for cand in _name_variants(sname):
                m, data = _pack_read(cand)
                if m is None:
                    continue
                if data:
                    text = data
                    used = cand
                    method = m
                    break
                if data == '':
                    text = ''
                    used = cand
                    method = m
                    break
            if text is None:
                # stdlib C-modulleri (app/net/chr/player) kaynak dosyasizdir -
                # bunlar hata DEGIL, 'KAYNAKSIZ(C)' olarak isaretlenir
                if gname not in _KNOWN_CLIENT_MODULES:
                    errc += 1
                    errs.append(gname)
                    idx.append('OKUNAMADI   %-28s (%s)' % (gname, src))
                else:
                    # v4.7: C modulleri (player/chr/net/item...) artik
                    # KAYNAKSIZ birakilmiyor - API-STUB dosyasi yazilir
                    # (dir() introspection: sabitler + fonksiyon listesi).
                    # Kullanici istegi: 'player.py leri dumplayamiyordu'.
                    try:
                        stub = _cmod_stub(gname)
                        f = open(_dump_name(gname + '.py'), 'w')
                        f.write(stub)
                        f.close()
                        idx.append('API-STUB    %-28s (C modulu; %d satir API listesi - kaynak .py yok)' % (gname + '.py', stub.count(chr(10))))
                    except:
                        idx.append('KAYNAKSIZ(C) %-28s (dahili C modulu - .py kaynagi yok)' % gname)
                continue
            safe = ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in (gname if '/' not in gname else gname.split('/')[-1][:-3])]) or 'adsiz'
            if '/' in gname:
                safe = ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in gname.replace('/', '_')])
            try:
                f = open(_dump_name(safe + '.py'), 'w')
                f.write(text)
                f.close()
                nb = len(text)
                if nb == 0:
                    boc += 1
                    idx.append('BOS         %-28s 0 byte (yontem: %s | ad: %s)' % (safe + '.py', method, used))
                else:
                    okc += 1
                    methods[method] = methods.get(method, 0) + 1
                    idx.append('OK %6d byte %-28s (yontem: %s | ad: %s)' % (nb, safe + '.py', method, used))
            except:
                errc += 1
                errs.append(gname)
                idx.append('YAZILAMADI  %s' % gname)
        # UI script hasilari INDEX'e
        if uihit:
            idx.append('')
            idx.append('--- UI script yollari (oyun log kanitli pack yollari) ---')
            for upath, m, nb in uihit:
                safe = 'ui__' + ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in upath.replace('/', '_')])
                try:
                    m2, data2 = _pack_read(upath)
                    if m2 is not None:
                        f = open(_dump_name(safe + '.py'), 'w')
                        f.write(data2 or '')
                        f.close()
                    idx.append('%s %8d byte %-44s (yontem: %s)' % ('BOS ' if nb == 0 else 'OK  ', nb, upath, m2 or m))
                except:
                    idx.append('HATA         %-44s' % upath)
        idx.append('')
        idx.append('ozet: %d OK, %d BOS, %d hata | yontem dagilimi: %s' % (
            okc, boc, errc, ', '.join(['%s=%d' % (k, v) for k, v in methods.items()])))
        idx.append('klasor: C:\\MaxExec\\dump')
        if errs:
            idx.append('hatalilar: ' + ', '.join(errs[:24]))
        try:
            f = open(_dump_name('INDEX.txt'), 'w')
            f.write('\n'.join(idx) + '\n')
            f.close()
        except:
            pass
        L = ['hedef: %d modul/dosya (+%d UI yolu)' % (len(targets), len(uihit)),
             'ozet: %d OK, %d BOS, %d hata | yontemler: %s' % (okc, boc, errc, ', '.join(['%s=%d' % (k, v) for k, v in methods.items()])),
             'INDEX: C:\\MaxExec\\dump\\INDEX.txt',
             'SONRAKI ADIM: dump klasorunu zipleyip AI\'ya gonder -> PLUSQuest.md guncellenir']
        _write('pydumpall', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pydumpall', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pyscan(modul) - yuklu modulun fonksiyonlarini argumanlariyla listeler
# (eski AI'nin dir()/globals() onerisi - GOD MOD ile arguman cikarimina
#  yukseltildi: py2 func_code / py3 __code__, C fonksiyonlari isaretlenir)
# ---------------------------------------------------------------------------
def pyscan(modname=None):
    try:
        if not modname:
            _write('pyscan', 'kullanim: pyscan <modul-ad>  (orn. pyscan player | adaylar: pyfiles)\n')
            return
        mn = str(modname).strip()
        mod = sys.modules.get(mn, None)
        if mod is None:
            try:
                mod = __import__(mn)
            except Exception, e:
                _write('pyscan', 'HATA: modul yuklu degil/icebilirmedi: %s (%s)\nIpucu: pyfiles yaz; hepsi icin plusquest\n' % (mn, _fmt_error(e)))
                return
        L = ['modul : %s' % mn,
             'tip   : %s' % type(mod).__name__,
             'dosya : %s' % str(getattr(mod, '__file__', 'dahili/C-modulu')),
             '']
        names = []
        try:
            names = dir(mod)
        except:
            pass
        ncall = 0
        for n in names:
            if n.startswith('__'):
                continue
            try:
                obj = getattr(mod, n)
            except:
                continue
            tn = type(obj).__name__
            sig = ''
            if callable(obj) or tn == 'builtin_function_or_method':
                ncall += 1
                code = None
                try:
                    code = getattr(obj, 'func_code', None)
                except:
                    code = None
                if code is None:
                    try:
                        code = getattr(obj, '__code__', None)
                    except:
                        code = None
                if code is not None:
                    try:
                        k = int(code.co_argcount)
                        sig = '(%s)' % ', '.join(list(code.co_varnames[:k]))
                    except:
                        sig = '(?)'
                else:
                    sig = '(C-fonksiyonu: argumanlar PLUSQuest.md katalogunda)'
            L.append('  %-34s %-26s %s' % (n, tn, sig))
        L.append('')
        L.append('ozet: %d attr, %d callable' % (len(names), ncall))
        _write('pyscan', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pyscan', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# plusquest() - yuklu TUM modulleri tarar -> dump\PLUSQuest_live.txt
# (eski AI'nin "sys.modules + dir()" fikrinin GOD MOD uygulamasi:
#  tum moduller, siniflandirilmis, dosyaya dokulen, AI'ya gonderilebilir)
# ---------------------------------------------------------------------------
def plusquest():
    try:
        L = ['=' * 72,
             'PLUSQuest_live - yuklu modullerin CANLI fonksiyon katalogu',
             'uretim: PLUSMAXGOD_PyScript.py v%s  t=%s' % (PYLIB_VERSION, time.strftime('%Y-%m-%d %H:%M:%S')),
             'python: %s' % str(sys.version).split()[0],
             'oyun ici: %s' % ('EVET - tam katalog' if _ingame() else 'HAYIR (menusun: oyunda daha fazla modul yuklenir, oyundayken tekrar calistir)'),
             '=' * 72, '']
        mods = []
        try:
            mods = sorted([m for m in sys.modules.keys() if m and '.' not in m and not m.startswith('_')])
        except:
            pass
        mods = mods[:250]
        tot = 0
        for mn in mods:
            mod = sys.modules.get(mn)
            if mod is None:
                continue
            try:
                names = dir(mod)
            except:
                names = []
            L.append('== %s (%s) ==' % (mn, str(getattr(mod, '__file__', 'dahili/C'))))
            c = 0
            for n in names[:500]:
                if n.startswith('__'):
                    continue
                try:
                    obj = getattr(mod, n)
                except:
                    continue
                tn = type(obj).__name__
                sig = ''
                if callable(obj):
                    code = None
                    try:
                        code = getattr(obj, 'func_code', None) or getattr(obj, '__code__', None)
                    except:
                        code = None
                    if code is not None:
                        try:
                            sig = '(%s)' % ', '.join(list(code.co_varnames[:int(code.co_argcount)]))
                        except:
                            sig = '(?)'
                    else:
                        sig = '(C)'
                L.append('   %-32s %-24s %s' % (n, tn, sig))
                c += 1
                tot += 1
            if len(names) > 500:
                L.append('   ... +%d attr daha' % (len(names) - 500))
            L.append('')
        L.append('ozet: %d modul, %d attr listelendi' % (len(mods), tot))
        out = _dump_name('PLUSQuest_live.txt')
        try:
            f = open(out, 'w')
            f.write('\n'.join(L) + '\n')
            f.close()
        except Exception, e2:
            _write('plusquest', 'HATA yazma: %s\n' % _fmt_error(e2))
            return
        _write('plusquest', 'OK: %d modul, %d attr -> %s\nSONRAKI: bu dosyayi AI\'ya gonder -> PLUSQuest.md kataloguna islenir\n' % (len(mods), tot, out))
    except Exception, e:
        _write('plusquest', 'HATA ' + _fmt_error(e) + '\n')

pyscanall = plusquest   # takma ad - ayni isi yapar

# ---------------------------------------------------------------------------
# ===========================================================================
# v4.2 UI YARDIMCISI - 1-arg setterlarin hedefi "SECILI instance" oldugu
# icin tum dongu pencereleri ui.ScriptWindow turetir (botlarin OnUpdate
# deseni: Pickup.py/fishbot1.0.py kaniti - ana thread guvenli, kilitlenme
# yok; ayri thread KULLANILMAZ)
# ===========================================================================
# (v4.5 DUZELT: ui_WindowBase tanimi bu konumdan yukariya tasindi)

# ===========================================================================
# v4.2 - GOD MOD PAKETI (saha testi 9 istekleri)
# KANITLAR: LegendySF-V2 fishing.cpp/InstanceBaseMotion.cpp/char.cpp +
#           kullanici botlari (fishbot1.0, itemcreator, pickupstealer,
#           EQChanger) + introselect.py MakeCharacter + canli katalog
# UYARI: sahte item/instance/morf istemci-TARAFIDIR (sunucu gormez);
#        fish/autotake/chchange gercek paketler yollar.
# ===========================================================================

# --- canli cikti kanali: C++ v1.9 izleyici bu dosyayi takip eder ----------
LIVE_PATH = r'C:\MaxExec\live.txt'

def _live(msg):
    """canli durum satiri yaz (cmd penceresinde [LIVE] ile akar)"""
    try:
        f = open(LIVE_PATH, 'a')
        f.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), str(msg)))
        f.close()
    except:
        pass

def canli(msg=''):
    """elle canli satir bas (test icin): canli merhaba"""
    _live(msg if msg else 'canli test %s' % time.strftime('%H:%M:%S'))
    _write('canli', 'OK: live.txt yazildi (cmd penceresinde gorunmeli)')

# ---------------------------------------------------------------------------
# UNEQUIP - ekipman cikarma (use tersi: takili slot'a SendItemUsePacket =
# cikarma; kullanici saha testi 9'da 'use ile takma'yi dogruladi)
# ---------------------------------------------------------------------------
_EQ_PARTS = {
    'body': 0, 'zirh': 0, 'govde': 0,
    'head': 1, 'kask': 1,
    'shoes': 2, 'ayak': 2, 'bot': 2,
    'wrist': 3, 'bileklik': 3,
    'weapon': 4, 'silah': 4,
    'neck': 5, 'kolye': 5,
    'ear': 6, 'kupe': 6,
    'unique': 7, 'ozel': 7, 'kalkan': 7,
    'arrow': 8, 'ok': 8,
    'costume': 14, 'kostum': 14,
    'hair': 15, 'sa': 15,
}

def _eq_base():
    import player
    try:
        return int(player.EQUIPMENT_BASE_INDEX)
    except:
        return 90

def unequip(part):
    try:
        if not _ingame():
            _write('unequip', 'HATA: oyunda degilsin\n')
            return
        import net, player, item
        eb = _eq_base()
        p = str(part).strip().lower()
        if p.isdigit():
            slot = int(p)
        else:
            if p not in _EQ_PARTS:
                _write('unequip', 'HATA: bilinmeyen parca "%s"\nparcalar: %s\nveya slot no (equip raporundaki [90..])' % (p, ' '.join(sorted(_EQ_PARTS.keys()))))
                return
            slot = eb + _EQ_PARTS[p]
        vnum = 0
        try:
            vnum = int(player.GetItemIndex(slot))
        except:
            vnum = 0
        if vnum <= 0:
            _write('unequip', 'HATA: slot %d bos zaten (once equip yaz, slotlara bak)' % slot)
            return
        net.SendItemUsePacket(slot)
        time.sleep(0.25)
        after = 0
        try:
            after = int(player.GetItemIndex(slot))
        except:
            after = 0
        if after <= 0:
            _write('unequip', 'OK: slot %d cikarildi (%s)\ntakmak icin: use <envanter-slotu> (saha dogrulandi)' % (slot, _item_name(vnum)))
        else:
            _write('unequip', 'UYARI: paket gitti ama slot %d hala dolu gorunuyor (%s)\nenvanter dolu olabilir - yer ac (drop) veya 1sn bekle equip ile kontrol et' % (slot, _item_name(vnum)))
    except Exception, e:
        _write('unequip', 'HATA ' + _fmt_error(e) + '\n')

def unequipall():
    try:
        if not _ingame():
            _write('unequipall', 'HATA: oyunda degilsin\n')
            return
        import net, player
        eb = _eq_base()
        out = ['ekipman cikarma (slot: sonuc)']
        n = 0
        for slot in range(eb, eb + 20):
            try:
                if int(player.GetItemIndex(slot)) > 0:
                    try:
                        net.SendItemUsePacket(slot)
                        time.sleep(0.12)
                        out.append('  %d: paket gitti' % slot)
                        n += 1
                    except Exception, e2:
                        out.append('  %d: HATA %s' % (slot, _fmt_error(e2)))
            except:
                pass
        out.append('---')
        out.append('%d slot icin cikarma paketi gonderildi; kontrol: equip' % n)
        out.append('NOT: envanter doluysa cogu esya cikamaz - once yer ac')
        _write('unequipall', '\n'.join(out) + '\n')
    except Exception, e:
        _write('unequipall', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# GROUND - yerdeki esyalari tara (KANIT: kullanici pickupstealer.py +
# Itemstealer.py textTail.Pick(x,y) ekran-taramasi; yer esyalari chr
# instance DEGIL - textTail kuyrugu vardir, vid'si Pick ile alınir)
# ---------------------------------------------------------------------------
_TAKE = {'win': None, 'last': 0.0, 'cnt': 0}

def _ground_scan():
    """ekran tarar -> vid listesi (mesafe bilinmiyorsa ekran sirali)"""
    import textTail
    vids = {}
    for sy in range(120, 620, 15):
        for sx in range(280, 840, 20):
            try:
                v = int(textTail.Pick(sx, sy))
            except:
                continue
            if v > 0:
                vids[v] = 1
    return vids.keys()

def ground():
    try:
        if not _ingame():
            _write('ground', 'HATA: oyunda degilsin\n')
            return
        import textTail, chr, player, net
        vids = _ground_scan()
        me = 0
        try:
            me = int(player.GetMainCharacterIndex())
        except:
            pass
        myp = None
        try:
            myp = chr.GetPixelPosition(me)
        except:
            myp = None
        L = ['yerdeki esyalar: %d adet (ekran taramasi textTail.Pick)' % len(vids)]
        rows = []
        for v in vids:
            wpos = ''
            try:
                p = textTail.GetPosition(v)
                if p is not None:
                    wpos = ' dunya=(%d,%d)' % (int(p[0]), int(p[1]))
                    if myp is not None:
                        dx = int(p[0]) - int(myp[0]); dy = int(p[1]) - int(myp[1])
                        wpos += ' mesafe=%d' % int((dx * dx + dy * dy) ** 0.5)
            except:
                pass
            rows.append('  vid=%d%s' % (v, wpos))
        rows.sort()
        L.extend(rows[:50])
        if len(rows) > 50:
            L.append('  ... +%d daha' % (len(rows) - 50))
        L.append('---')
        L.append('alma: groundtake all (hepsi) | groundtake <vid> (tek)')
        L.append('surekli: autotake 1 | esya adlari vid ile okunamaz (sunucu paketi)')
        _write('ground', '\n'.join(L) + '\n')
    except Exception, e:
        _write('ground', 'HATA ' + _fmt_error(e) + '\n')

def groundtake(mode):
    try:
        if not _ingame():
            _write('groundtake', 'HATA: oyunda degilsin\n')
            return
        import net
        s = str(mode).strip().lower()
        if s in ('all', 'hepsi', ''):
            vids = _ground_scan()
            n = 0
            for v in vids[:60]:
                try:
                    net.SendItemPickUpPacket(v)
                    n += 1
                except:
                    pass
            _write('groundtake', 'OK: %d esya icin alma paketi gonderildi (SendItemPickUpPacket)' % n)
        else:
            v = int(s)
            net.SendItemPickUpPacket(v)
            _write('groundtake', 'OK: vid %d icin alma paketi gonderildi' % v)
    except Exception, e:
        _write('groundtake', 'HATA ' + _fmt_error(e) + '\n')

class _TakeLoopWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            now = time.time()
            if now - _TAKE['last'] < 0.4:
                return
            _TAKE['last'] = now
            vids = _ground_scan()
            if not vids:
                return
            import net
            for v in vids[:40]:
                try:
                    net.SendItemPickUpPacket(v)
                    _TAKE['cnt'] += 1
                except:
                    pass
            _live('TAKE: otomatik toplama devam (%d paket, toplam %d)' % (len(vids[:40]), _TAKE['cnt']))
        except:
            pass

def autotake(flag):
    try:
        if not _ingame():
            _write('autotake', 'HATA: oyunda degilsin\n')
            return
        f = 1 if (str(flag) in ('1', 'on', 'acik', 'True', 'true')) else 0
        if f:
            if _TAKE['win'] is None:
                _TAKE['win'] = _TakeLoopWnd()
                _TAKE['cnt'] = 0
            _write('autotake', "OK: otomatik toplama ACIK (0.4sn'de bir ekran taranir, hepsi alinir)\ndurdur: autotake 0")
        else:
            try:
                if _TAKE['win'] is not None:
                    _TAKE['win'].Hide()
                    _TAKE['win'].Destroy()
            except:
                pass
            _TAKE['win'] = None
            _write('autotake', 'OK: otomatik toplama KAPALI')
    except Exception, e:
        _write('autotake', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# v4.4 GOTAKE - esyaya YURU + TOPLA (kullanici: 'yanina gidip toplamak gibi
# ozellikler ekleyebiliriz'). Yol: textTail.GetPosition -> MoveToDestPosition
# -> yakinlik < 150px -> net.SendItemPickUpPacket (Instantpickup.py kaniti).
# ---------------------------------------------------------------------------
_GOTAKE = {'win': None, 'list': [], 't0': 0.0, 'cnt': 0}

class _GoTakeWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            import time, chr, net, textTail
            st = _GOTAKE
            now = time.time()
            if now - st['t0'] < 0.3:
                return
            st['t0'] = now
            while st['list']:
                v = st['list'][0]
                p = None
                try:
                    p = textTail.GetPosition(v)
                except:
                    p = None
                if p is None:
                    st['list'].pop(0)   # esya kaybolmus/alinmis -> siradaki
                    continue
                me = _my_vid()
                mp = chr.GetPixelPosition(me)
                dx = int(p[0]) - int(mp[0]); dy = int(p[1]) - int(mp[1])
                dist = (dx * dx + dy * dy) ** 0.5
                if dist > 150:
                    try:
                        chr.MoveToDestPosition(me, int(p[0]), int(p[1]))
                    except:
                        pass
                    return   # yuruyor - sonraki tick'te mesafe tekrar
                try:
                    net.SendItemPickUpPacket(v)
                    st['cnt'] += 1
                    _live('GOTAKE: alindi vid=%d (toplam %d, kalan %d)' % (v, st['cnt'], len(st['list']) - 1))
                except:
                    pass
                st['list'].pop(0)
            _write('gotake', 'OK: bitti - %d esya alindi' % st['cnt'])
            _gotake_stop()
        except Exception, e:
            _live('GOTAKE hatasi: ' + _fmt_error(e))
            _gotake_stop()

def _gotake_stop():
    try:
        if _GOTAKE['win'] is not None:
            _GOTAKE['win'].Hide()
            _GOTAKE['win'].Destroy()
    except:
        pass
    _GOTAKE['win'] = None
    _GOTAKE['list'] = []

def gotake(mode):
    """esyaya yuru + topla: gotake <vid> | gotake all (yakinlik sirali hepsi)"""
    try:
        if not _ingame():
            _write('gotake', 'HATA: oyunda degilsin\n')
            return
        import chr
        s = str(mode).strip().lower()
        vids = []
        if s in ('all', 'hepsi', ''):
            vids = _ground_scan()
            me = _my_vid()
            myp = None
            try:
                myp = chr.GetPixelPosition(me)
            except:
                pass
            if myp is not None:
                import textTail
                keyed = []
                for v in vids:
                    try:
                        p = textTail.GetPosition(v)
                        dx = int(p[0]) - int(myp[0]); dy = int(p[1]) - int(myp[1])
                        keyed.append((dx * dx + dy * dy, v))
                    except:
                        keyed.append((999999999, v))
                keyed.sort()
                vids = [v for d2, v in keyed]
        else:
            vids = [int(s)]
        if not vids:
            _write('gotake', 'UYARI: yerde esya yok (once ground yaz - tarama)')
            return
        _GOTAKE['list'] = list(vids[:60])
        _GOTAKE['cnt'] = 0
        if _GOTAKE['win'] is None:
            _GOTAKE['win'] = _GoTakeWnd()
        _write('gotake', 'OK: %d esyaya sirayla yurunup alinacak (vid: %s...)\ndurdur: gotake stop' % (len(_GOTAKE['list']), ', '.join(str(v) for v in _GOTAKE['list'][:5])))
    except Exception, e:
        _write('gotake', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# QUEST - aktif gorevler (KANIT: uicharacter.py:812-876:
# GetQuestCount + GetQuestData(4'lu) + GetQuestLastTime(2'lu))
# ---------------------------------------------------------------------------
def quest():
    try:
        if not _ingame():
            _write('quest', 'HATA: oyunda degilsin\n')
            return
        import quest as qm
        n = 0
        try:
            n = int(qm.GetQuestCount())
        except Exception, e1:
            _write('quest', 'HATA: GetQuestCount yok -> %s' % _fmt_error(e1))
            return
        L = ['aktif gorev: %d' % n]
        for i in range(min(n, 30)):
            name = '?'; counter = ''
            try:
                d = qm.GetQuestData(i)
                if d and len(d) >= 4:
                    name = str(d[0]); 
                    if str(d[2]):
                        counter = ' [%s: %s]' % (str(d[2]), str(d[3]))
                elif d and len(d) >= 1:
                    name = str(d[0])
            except Exception, e2:
                name = '(okunamadi: %s)' % _fmt_error(e2)
            idx = ''
            try:
                idx = ' idx=%d' % int(qm.GetQuestIndex(i))
            except:
                pass
            last = ''
            try:
                lt = qm.GetQuestLastTime(i)
                if lt and len(lt) >= 2:
                    last = ' kalan=%s' % str(lt[1])
            except:
                pass
            L.append('  [%d] %s%s%s%s' % (i, name, counter, idx, last))
        L.append('---')
        L.append('gorev penceresi icin oyunda N tusu; gorev butonu: raw event.QuestButtonClick(-2147483648+<idx>)')
        _write('quest', '\n'.join(L) + '\n')
    except Exception, e:
        _write('quest', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# FAKEITEM - hayalet esya (KANIT: itemcreator.py CreateItem:
# player.SetItemData(slot, vnum, adet) + SetItemAttribute +
# SetItemMetinSocket). UYARI: SADECE ISTEMCI GOSTERGESI - sunucuya
# gercek esya degil, kullanamaz/satamazsin; relogin temizler.
# ---------------------------------------------------------------------------
def fakeitem(vnum, count=1):
    try:
        if not _ingame():
            _write('fakeitem', 'HATA: oyunda degilsin\n')
            return
        import player, item
        v = int(vnum); c = int(count)
        try:
            item.SelectItem(v)
            nm = str(item.GetItemName())
        except:
            nm = '?'
        total = 0
        try:
            total = int(player.INVENTORY_SLOT_COUNT)
        except:
            try:
                total = int(player.INVENTORY_PAGE_SIZE) * int(getattr(player, 'INVENTORY_PAGE_COUNT', 2))
            except:
                total = 90
        placed = -1
        for s in range(total):
            occ = False
            try:
                occ = bool(player.isItem(s))
            except:
                try:
                    occ = int(player.GetItemIndex(s)) > 0
                except:
                    occ = False
            if occ:
                continue
            if s >= 5:
                try:
                    above = int(player.GetItemIndex(s - 5))
                    if above > 0:
                        item.SelectItem(above)
                        if int(item.GetItemSize()[1]) >= 2:
                            continue
                except:
                    pass
            try:
                player.SetItemData(s, v, c)
                placed = s
                break
            except Exception, e2:
                _write('fakeitem', 'HATA: SetItemData slot %d -> %s' % (s, _fmt_error(e2)))
                return
        if placed < 0:
            _write('fakeitem', 'HATA: bos slot yok (envanter dolu)')
            return
        _write('fakeitem', 'OK: slot %d -> vnum %d (%s) x%d\nUYARI: HAYALET esya - istemci gorunumu, sunucuda YOK (kullan/sat olmaz)\nbonus eklemek: raw player.SetItemAttribute(%d, 0, <bonus-tip>, <deger>)\nmetin: raw player.SetItemMetinSocket(%d, 0, <metin-vnum>)\ntemizlik: fakeclear all (veya relogin)' % (placed, v, nm, c, placed, placed))
    except Exception, e:
        _write('fakeitem', 'HATA ' + _fmt_error(e) + '\n')

def fakeclear(mode):
    try:
        if not _ingame():
            _write('fakeclear', 'HATA: oyunda degilsin\n')
            return
        import player
        s = str(mode).strip().lower()
        if s in ('all', 'hepsi', ''):
            total = 0
            try:
                total = int(player.INVENTORY_SLOT_COUNT)
            except:
                total = 90
            n = 0
            for i in range(total):
                try:
                    if player.isItem(i):
                        player.SetItemData(i, 0, 0)
                        n += 1
                except:
                    pass
            _write('fakeclear', 'OK: %d slot temizlendi (vnum=0)\nNOT: gercek esyalarin gorunumu de gitti - relogin eski haline getirir!' % n)
        else:
            i = int(s)
            player.SetItemData(i, 0, 0)
            _write('fakeclear', 'OK: slot %d temizlendi (relogin geri getirir)' % i)
    except Exception, e:
        _write('fakeclear', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# FAKE INSTANCE / KLON / MORF
# KANIT: introselect.py MakeCharacter SIRASI (bu motor ailesinin kendi
# kodu): CreateInstance(vid) -> SelectInstance(vid) -> SetVirtualID ->
# SetNameString -> SetRace -> SetArmor -> SetHair -> SetMotionMode ->
# SetLoopMotion -> SetRotation -> Show. BUTUN 1-arg setterlar SECILI
# instance'a uygulanir (PythonCharacterModule.cpp GetSelectedInstancePtr).
# Demirci race=20016 (npclist.txt). ISTEMCI-TARAFI (sunucu gormez).
# ---------------------------------------------------------------------------
_CLONE = {'vids': [], 'next': 400100000, 'morph': None}

def _my_vid():
    import player, net
    try:
        return int(player.GetMainCharacterIndex())
    except:
        try:
            return int(net.GetMainActorVID())
        except:
            return 0

def _find_free_vid():
    import chr
    v = _CLONE['next']
    _CLONE['next'] += 7
    try:
        if chr.HasInstance(v):
            return _find_free_vid()
    except:
        pass
    return v

_APPEAR_PATH = r'C:\MaxExec\char_look.txt'

def _char_slot_of_session():
    """girilen karakter slotu (login/enter kaydeder; yoksa 0)"""
    try:
        return int(_SAVE.get('slot', 0))
    except:
        return 0

def _appear_of_me():
    """kendimin gorunusunu oku (klon icin): race+zirh+silah+sac
    v4.4 SAC FIX (saha testi 10: 'clone saci kopyalamiyor'):
    Instance'ta hair GETTER yoktur (PythonCharacterModule: sadece SetHair/
    ChangeHair). KANITLI okuma yolu: net.GetAccountCharacterSlotDataInteger(
    slot, net.ACCOUNT_CHARACTER_SLOT_HAIR) - hesap karakter tablosu login
    paketinden doldurulur ve TUM OTURUM boyunca bellekte kalir.
    Okunan deger C:\MaxExec\char_look.txt'ye cache'lenir."""
    import chr, player, net
    me = _my_vid()
    race = 4
    try:
        race = int(chr.GetRace(me))
    except:
        pass
    eb = _eq_base()
    try:
        armor = int(player.GetItemIndex(eb))
    except:
        armor = 0
    try:
        weapon = int(player.GetItemIndex(eb + 4))
    except:
        weapon = 0
    hair = 0
    got = False
    slot = _char_slot_of_session()
    try:
        h = int(net.GetAccountCharacterSlotDataInteger(slot, net.ACCOUNT_CHARACTER_SLOT_HAIR))
        if h >= 0:
            hair = h
            got = True
    except:
        pass
    if not got:
        # yedek 1: bazi derlemelerde var
        try:
            hair = int(player.GetHair())
            got = True
        except:
            pass
    if not got:
        # yedek 2: onceki oturumdan cache
        try:
            f = open(_APPEAR_PATH, 'r')
            hair = int(f.read().strip())
            f.close()
            got = True
        except:
            pass
    if got:
        try:
            f = open(_APPEAR_PATH, 'w')
            f.write(str(hair))
            f.close()
        except:
            pass
    return race, armor, weapon, hair

def clone(offset=80, hair=-1):
    """kendimin klonunu yanina spawn et (gorunum: ayni irk+zirh+silah+SAC)
    v4.4 FIX1 - Z: GetPixelPosition artik (x,y,z) UCLU donuyor
    (WalkToMobs.py kaniti: 'mobX, mobY, mobZ = chr.GetPixelPosition(i)') +
    player.GetMainCharacterPosition da (px,py,pz) verir (mypy.py kaniti) ->
    klon ARTIK YERIN ALTINA DUSMEZ. FIX2 - sac: hesap karakter tablosundan
    otomatik okunur ( AppearanceYardimci: _appear_of_me).
    Sac yine yanlissa zorla: clone 80 <sac-degeri>"""
    try:
        if not _ingame():
            _write('clone', 'HATA: oyunda degilsin\n')
            return
        import chr, player
        me = _my_vid()
        p = chr.GetPixelPosition(me)
        x = int(p[0]) + int(offset); y = int(p[1]) - int(offset)
        z = 0
        try:
            z = int(p[2])
        except:
            z = 0
        if not z:
            # yedek 1: uclu GetMainCharacterPosition (mypy.py kaniti)
            try:
                z = int(player.GetMainCharacterPosition()[2])
            except:
                z = 0
        if not z:
            # yedek 2: arazi yuksekligi
            try:
                import background
                z = int(background.GetHeight(int(p[0]), int(p[1])))
            except:
                pass
        race, armor, weapon, ahair = _appear_of_me()
        hair = int(hair)
        if hair < 0:
            hair = ahair
        vid = _find_free_vid()
        steps = _mk_fake(vid, race, x, y, z, name=str(chr.GetName(me)) + '2',
                         armor=armor, hair=hair, weapon=weapon, npc=False)
        if steps is None:
            return
        _CLONE['vids'].append(vid)
        _write('clone', 'OK: klon spawn vid=%d race=%d zirh=%d silah=%d sac=%d z=%d\nkonum=(%d,%d)\nadimlar: %s\nsilinek: unclone all | unclone %d\nsac yanlissa: clone %d <sac-degeri> | mod: clonemod swap/1/0' % (vid, race, armor, weapon, hair, z, x, y, ', '.join(steps), vid, int(offset)))
    except Exception, e:
        _write('clone', 'HATA ' + _fmt_error(e) + '\n')

def spawn(race, name='NPC', x=0, y=0):
    """sahte NPC spawn (demirci = spawn 20016; pozisyon 0,0 = benim yanım)
    v4.4: z ARTIK kendi Z'in (yerin dibine dusme FIX) + uretim sonrasi
    konum geri-okunup rapora yazilir ('xyz konumu dogru mu' kontrolu)"""
    try:
        if not _ingame():
            _write('spawn', 'HATA: oyunda degilsin\n')
            return
        import chr
        r = int(race)
        if int(x) == 0 and int(y) == 0:
            p = chr.GetPixelPosition(_my_vid())
            x = int(p[0]) + 60; y = int(p[1]) + 60
            try:
                z = int(p[2])
            except:
                z = 0
        else:
            # v4.4: elle konum verilince z = kendi z (ayni bolge)
            try:
                z = int(chr.GetPixelPosition(_my_vid())[2])
            except:
                z = 0
        # v4.3: race istemci mob_proto'da var mi? (gorunmezlik kontrolu)
        mname = ''
        try:
            import nonplayer
            mname = str(nonplayer.GetMonsterName(r))
        except:
            mname = ''
        vid = _find_free_vid()
        steps = _mk_fake(vid, r, int(x), int(y), z, name=str(name), npc=True)
        if steps is None:
            return
        _CLONE['vids'].append(vid)
        # v4.4: uretim sonrasi GERCEK konumu geri oku (dogrulama)
        rp = ''
        try:
            rpp = chr.GetPixelPosition(vid)
            rp = ' | okunan-konum=(%s,%s)' % (str(rpp[0]), str(rpp[1]))
        except:
            rp = ''
        if mname:
            _write('spawn', 'OK: sahte NPC vid=%d race=%d (%s) ad=%s konum=(%d,%d) z=%d%s\nadimlar: %s\nsilinek: unclone all | unclone %d' % (vid, r, mname, str(name), int(x), int(y), z, rp, ', '.join(steps), vid))
        else:
            _write('spawn', 'UYARI: race %d istemci mob_proto\'sunda YOK -> GORUNMEZ olur (data yaratildi ama model yok)\nGECERLI race listesi: spawnscan 1 30000 yaz (C:\\MaxExec\\spawnscan_full.txt)\nvid=%d yaratildi (gorunmez olabilir) konum=(%d,%d) z=%d%s, silmek: unclone %d' % (r, vid, int(x), int(y), z, rp, vid))
    except Exception, e:
        _write('spawn', 'HATA ' + _fmt_error(e) + '\n')

def _mk_fake(vid, race, x, y, z, name='NONAME', armor=0, hair=0, weapon=0, npc=False):
    """introselect MakeCharacter sirasi - her adim raporlanir"""
    import chr
    steps = []
    try:
        chr.CreateInstance(vid)
        steps.append('CreateInstance')
    except Exception, e:
        _write('spawn', 'HATA: CreateInstance -> ' + _fmt_error(e))
        return None
    try:
        chr.SelectInstance(vid)
        steps.append('SelectInstance')
    except Exception, e:
        steps.append('SelectInstance HATA:' + _fmt_error(e))
    try:
        chr.SetVirtualID(vid)
        steps.append('SetVirtualID')
    except:
        pass
    if npc:
        try:
            t = int(getattr(chr, 'INSTANCE_TYPE_NPC', 1))
            chr.SetInstanceType(t)
            steps.append('SetInstanceType(NPC)')
        except:
            pass
    try:
        chr.SetNameString(str(name))
        steps.append('SetNameString')
    except:
        pass
    try:
        chr.SetRace(int(race))
        steps.append('SetRace(%d)' % int(race))
    except Exception, e:
        _write('spawn', 'HATA: SetRace -> ' + _fmt_error(e))
        return None
    if armor:
        try:
            chr.SetArmor(int(armor))
            steps.append('SetArmor')
        except:
            pass
    if hair:
        try:
            chr.SetHair(int(hair))
            steps.append('SetHair')
        except:
            pass
    if weapon:
        try:
            chr.SetWeapon(int(weapon))
            steps.append('SetWeapon')
        except:
            pass
    try:
        chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
        steps.append('SetMotionMode')
    except:
        pass
    try:
        chr.SetLoopMotion(chr.MOTION_WAIT)
        steps.append('SetLoopMotion(WAIT)')
    except:
        pass
    try:
        chr.SetRotation(0.0)
        steps.append('SetRotation')
    except:
        pass
    try:
        chr.SetPixelPosition(int(x), int(y), int(z))
        steps.append('SetPixelPosition')
    except:
        try:
            chr.SetPixelPosition(int(x), int(y))
            steps.append('SetPixelPosition(2-arg)')
        except Exception, e:
            steps.append('SetPixelPosition HATA:' + _fmt_error(e))
    try:
        chr.Show()
        steps.append('Show')
    except:
        pass
    # v4.4 GORSEL YENILEME (kullanici sahasi: spawn/morph ancak zirh degisince
    # gorunuyordu -> render'in aktoru yeniden insa etmesi icin tazeleme):
    try:
        chr.Update()
        steps.append('Update')
    except:
        try:
            chr.Deform()
            steps.append('Deform')
        except:
            pass
    try:
        chr.Hide()
        chr.Show()
        steps.append('Hide+Show')
    except:
        pass
    # secimi geri kendime al (1-arg tp vs bozulmasin)
    try:
        chr.SelectInstance(_my_vid())
    except:
        pass
    return steps

def unclone(mode):
    try:
        if not _ingame():
            _write('unclone', 'HATA: oyunda degilsin\n')
            return
        import chr
        s = str(mode).strip().lower()
        if s in ('all', 'hepsi', ''):
            n = 0
            for v in list(_CLONE['vids']):
                try:
                    chr.DeleteInstance(v)
                    n += 1
                except:
                    pass
            _CLONE['vids'] = []
            _write('unclone', 'OK: %d sahte instance silindi' % n)
        else:
            v = int(s)
            chr.DeleteInstance(v)
            if v in _CLONE['vids']:
                _CLONE['vids'].remove(v)
            _write('unclone', 'OK: vid %d silindi' % v)
    except Exception, e:
        _write('unclone', 'HATA ' + _fmt_error(e) + '\n')

def _visual_kick(vid):
    """v4.4 GORSEL TAZELEME (kullanici: 'zirh tak cikar degil, refresh ilgili
    bir fnc olabilir'). Kanit: PythonCharacterModule.cpp chr.Update/chr.Deform/
    chr.Hide/chr.Show + chr.Refresh (bazi derlemelerde govdesi BOS!). Sira:
    Update/Deform -> Show-onay -> Hide+Show -> WAIT hareketi. Bu; SetRace/
    SetArmor sonrasi modelin yeniden insa edilmesini tetikler."""
    import chr
    try:
        chr.SelectInstance(int(vid))
    except:
        pass
    try:
        chr.Update()
    except:
        try:
            chr.Deform()
        except:
            pass
    show_ok = True
    try:
        chr.Show()
    except:
        show_ok = False
    if show_ok:
        try:
            chr.Hide()
            chr.Show()
        except:
            try:
                chr.Show()
            except:
                pass
    try:
        chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
    except:
        pass
    try:
        chr.SetLoopMotion(chr.MOTION_WAIT)
    except:
        pass

def morph(race):
    """kendini baska race gorunumune donustur (demirci: morph 20016)
    YOL: SelectInstance(ben) + SetRace(race) - CInstanceBase::SetRace
    aktoru yeniden kurar (InstanceBase.cpp:996). ISTEMCI-TARAFI: digerleri
    seni ninja gorur; warp/relugin geri alir."""
    try:
        if not _ingame():
            _write('morph', 'HATA: oyunda degilsin\n')
            return
        import chr
        me = _my_vid()
        if _CLONE['morph'] is None:
            orig = 4
            try:
                orig = int(chr.GetRace(me))
            except:
                orig = 4
            _CLONE['morph'] = orig
        r = int(race)
        # v4.3: mob_proto kontrolu - yoksa gorunmez olursun (saha: morph 20016)
        mname = ''
        try:
            import nonplayer
            mname = str(nonplayer.GetMonsterName(r))
        except:
            mname = ''
        if not mname:
            _write('morph', 'HATA: race %d istemci mob_proto\'sunda YOK -> gorunmez olurdun (saha testi: morph 20016 gorunmez oldu)\nGECERLI race listesi: spawnscan 1 30000 (C:\\MaxExec\\spawnscan_full.txt)\nistemci-tarafi gorunum race listesi icin ayrica: setarmor/setweapon serbest' % r)
            return
        try:
            chr.SelectInstance(me)
            chr.SetRace(r)
            try:
                chr.SetMotionMode(chr.MOTION_MODE_GENERAL)
            except:
                pass
            try:
                chr.SetLoopMotion(chr.MOTION_WAIT)
            except:
                pass
            _visual_kick(me)
            _write('morph', 'OK: gorunum race=%d yapildi (eski: %d)\ndemirci=20016, simyaci=20001, satici=20010 | gorsel tazeleme uygulandi\nYINE gorunmezse: setarmor <giyili-zirh-vnumu> (kendi zirhini yeniden uygular)\nGERI: unmorph | UYARI: istemci-tarafi, warp/relogin geri alir' % (r, _CLONE['morph']))
        except Exception, e2:
            _write('morph', 'HATA: SetRace(%d) -> %s\nNOT: bazi clientlarda ana instance race degisimi kapali; sahte NPC yolu: spawn %d' % (r, _fmt_error(e2), r))
    except Exception, e:
        _write('morph', 'HATA ' + _fmt_error(e) + '\n')

def unmorph():
    try:
        if not _ingame():
            _write('unmorph', 'HATA: oyunda degilsin\n')
            return
        import chr, player, net
        if _CLONE['morph'] is None:
            _write('unmorph', 'BILGI: morph kaydi yok (zaten normal gorunum?)')
            return
        me = _my_vid()
        try:
            chr.SelectInstance(me)
            chr.SetRace(_CLONE['morph'])
            try:
                chr.SetLoopMotion(chr.MOTION_WAIT)
            except:
                pass
            _visual_kick(me)
            _write('unmorph', 'OK: gorunum race=%d geri alindi (gorsel tazeleme uygulandi)' % _CLONE['morph'])
        except Exception, e2:
            _write('unmorph', 'HATA: %s\nyedek yol: ekipmani cikar-tak (unequip body; use <slot>) sunucudan gorunumu tazeler' % _fmt_error(e2))
        _CLONE['morph'] = None
    except Exception, e:
        _write('unmorph', 'HATA ' + _fmt_error(e) + '\n')

def setarmor(vnum):
    """gorunum zirhi (EQChanger.py kaniti: chr.SetArmor 1-arg)"""
    try:
        if not _ingame():
            _write('setarmor', 'HATA: oyunda degilsin\n')
            return
        import chr
        chr.SelectInstance(_my_vid())
        chr.SetArmor(int(vnum))
        _visual_kick(_my_vid())
        _write('setarmor', 'OK: gorunum zirhi %d (istemci-tarafi; relogin/warp giderir)' % int(vnum))
    except Exception, e:
        _write('setarmor', 'HATA ' + _fmt_error(e) + '\n')

def setweapon(vnum):
    """gorunum silahi (EQChanger.py kaniti: chr.SetWeapon 1-arg)"""
    try:
        if not _ingame():
            _write('setweapon', 'HATA: oyunda degilsin\n')
            return
        import chr
        chr.SelectInstance(_my_vid())
        chr.SetWeapon(int(vnum))
        _visual_kick(_my_vid())
        _write('setweapon', 'OK: gorunum silahi %d (istemci-tarafi)' % int(vnum))
    except Exception, e:
        _write('setweapon', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# SIMYA (Dragon Soul) + ITEMSCAN
# KANIT: player.DRAGON_SOUL_INVENTORY sabiti + GetItemIndex 1/2-arg
# (PythonPlayerModule.cpp:788) + item.SelectItem/GetItemName/GetItemType.
# simya olusturma kodu: /i <vnum> <adet> (saha testi 9: /i 27400 kaniti)
# ---------------------------------------------------------------------------
def simya():
    try:
        if not _ingame():
            _write('simya', 'HATA: oyunda degilsin\n')
            return
        import player, item
        ds = int(getattr(player, 'DRAGON_SOUL_INVENTORY', 3))
        pages = int(getattr(player, 'DRAGON_SOUL_PAGE_COUNT', 4))
        psize = int(getattr(player, 'DRAGON_SOUL_PAGE_SIZE', 32))
        L = ['SIMYA (Dragon Soul) raporu', 'DS envanter: window=%d sayfa=%d/slot=%d' % (ds, pages, psize)]
        n = 0
        for slot in range(min(pages * psize, 200)):
            idx = 0
            try:
                idx = int(player.GetItemIndex(ds, slot))
            except:
                try:
                    idx = int(player.GetItemIndex(slot))
                except:
                    idx = 0
            if idx <= 0:
                continue
            n += 1
            cnt = 1
            try:
                cnt = int(player.GetItemCount(ds, slot))
            except:
                try:
                    cnt = int(player.GetItemCount(slot))
                except:
                    cnt = 1
            L.append('  [DS %3d] vnum=%-7d x%-4d %s | /i %d %d' % (slot, idx, cnt, _item_name(idx), idx, cnt))
            if n >= 60:
                L.append('  ... (60+ kesildi)')
                break
        if n == 0:
            L.append('  (DS envanter bos)')
        # ana envanterdeki simya tasi tipleri
        L.append('--- ana envanterde ITEM_TYPE_DS esyalar:')
        m = 0
        total = 0
        try:
            total = int(player.INVENTORY_SLOT_COUNT)
        except:
            total = 90
        for s in range(total):
            idx = 0
            try:
                idx = int(player.GetItemIndex(s))
            except:
                idx = 0
            if idx <= 0:
                continue
            try:
                item.SelectItem(idx)
                if int(item.GetItemType()) == int(item.ITEM_TYPE_DS):
                    cnt = 1
                    try:
                        cnt = int(player.GetItemCount(s))
                    except:
                        cnt = 1
                    L.append('  [inv %3d] vnum=%-7d x%-4d %s | /i %d %d' % (s, idx, cnt, _item_name(idx), idx, cnt))
                    m += 1
                    if m >= 30:
                        L.append('  ... (30+ kesildi)')
                        break
            except:
                pass
        if m == 0:
            L.append('  (ana envanterde DS tipi esya yok)')
        L.append('---')
        L.append('OLUSTURMA: /i <vnum> <adet> (saha: /i 27400 olta, /i 27801 200 solucan)')
        L.append('vnum kesfi: itemscan <min> <max> (orn. itemscan 55000 55999)')
        _write('simya', '\n'.join(L) + '\n')
    except Exception, e:
        _write('simya', 'HATA ' + _fmt_error(e) + '\n')

ds = simya   # kisaltma

def itemscan(mn, mx):
    """item tablosu taramasi (item.SelectItem + GetItemName) - simya/balik
    vnum kesfi; aralik 50.000'den buyukse kesilir"""
    try:
        if not _ingame():
            _write('itemscan', 'HATA: oyunda degilsin\n')
            return
        import item
        a = int(mn); b = int(mx)
        if b < a:
            a, b = b, a
        if b - a > 50000:
            b = a + 50000
        found = []
        tcount = {}
        for v in xrange(a, b + 1):
            nm = ''
            try:
                item.SelectItem(v)
                nm = str(item.GetItemName())
            except:
                continue
            if not nm:
                continue
            t = -1
            try:
                t = int(item.GetItemType())
            except:
                t = -1
            tcount[t] = tcount.get(t, 0) + 1
            found.append((v, nm, t))
        # v4.3: TAM LISTE python ile dogrudan dosyaya (DLL sonuc limiti YOK)
        path = r'C:\MaxExec\itemscan_full.txt'
        try:
            f = open(path, 'w')
            f.write('itemscan %d-%d: %d esya\n' % (a, b, len(found)))
            f.write('tip dagilimi: %s\n' % ', '.join(['%s=%d' % (k, tcount[k]) for k in sorted(tcount)]))
            for v, nm, t in found:
                f.write('vnum=%-7d tip=%-2d %s | /i %d\n' % (v, t, nm, v))
            f.close()
        except Exception, e2:
            path = 'YAZILAMADI: ' + _fmt_error(e2)
        L = ['itemscan %d-%d: %d esya bulundu' % (a, b, len(found))]
        L.append('tip dagilimi: %s' % ', '.join(['%s=%d' % (k, tcount[k]) for k in sorted(tcount)]))
        for v, nm, t in found[:120]:
            L.append('  vnum=%-7d tip=%-2d %s | /i %d' % (v, t, nm, v))
        if len(found) > 120:
            L.append('  ... +%d daha -> TAM LISTE: %s' % (len(found) - 120, path))
        L.append('NOT: ITEM_TYPE_DS=%s ITEM_TYPE_FISH=%s (simya/balik bu tiplerde)' % (str(getattr(item, 'ITEM_TYPE_DS', '?')), str(getattr(item, 'ITEM_TYPE_FISH', '?'))))
        _write('itemscan', '\n'.join(L) + '\n')
    except Exception, e:
        _write('itemscan', 'HATA ' + _fmt_error(e) + '\n')

def itemscanall():
    """v4.3: TUM vnum uzayi (1-99999) -> tam liste itemscan_full.txt"""
    return itemscan(1, 99999)

# ---------------------------------------------------------------------------
# BALIK SISTEMI - tam mekanik (LegendySF fishing.cpp, klasik mainline):
#   cast -> sunucu 10-40sn bekler -> GC_REACT (isirtma, 6sn pencere)
#   take -> Compute(fish, ms, level): ms>6000=hata;
#           kova=(ms+99)/200; number(1,100)<=aFishingTime[tip][kova]
#           VE number(1,zorluk)<=olta-seviyesi(soket2+value0)
#   KACIRMA = olta-skilli SIFIR (rod->SetSocket(2,0))!
#   CLIENT: cast icin 400 birim icinde su gerekli (GetFishingRot);
#   sunucuda su kontrolu YOK -> fishspot: su kenarinda at, tp ile uzaklas!
# RESMI TEPKI TABLOSU (aFishingTime; % olarak kova=(ms+99)/200):
#   tip0: 0,0,0,0,0,2,4,8,12,16,20,22,25,30,50,80,50,30,25,22,20,16,12,8,4,2,0..
#   tip1: 0 x16 sonra 4,8,12,16,20,22,25,30,50,80,50,30,25,22,20
#   tip2: 20,22,25,30,50,80,50,30,25,22,20,16,12,8,4,0 x16
#   tip3: HEP %100   |  tip4: 20,20,20,20,20,22,24,28,32,36,40,42,45,50,70,100..
# -> ANINDA TEPKI HER ZAMAN EN IYI DEGIL! fishdelay auto (ogrenici) ONERILIR.
# ---------------------------------------------------------------------------
FISH_TIME_TABLE = (
    (0, 0, 0, 0, 0, 2, 4, 8, 12, 16, 20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20, 16, 12, 8, 4, 2, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 8, 12, 16, 20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20),
    (20, 22, 25, 30, 50, 80, 50, 30, 25, 22, 20, 16, 12, 8, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    (100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100),
    (20, 20, 20, 20, 20, 22, 24, 28, 32, 36, 40, 42, 45, 50, 70, 100, 70, 50, 45, 42, 40, 36, 32, 28, 24, 22, 20, 20, 20, 20, 20),
)
FISH_DELAY_AUTO_STEPS = (0, 200, 400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000, 4400, 4800, 5200)
FISH_ROD_MIN, FISH_ROD_MAX = 27400, 27420
FISH_BAITS = (27800, 27801, 27802)
FISH_LIVE = tuple(range(27803, 27824)) + (27987,)
FISH_DEAD = tuple(range(27833, 27854)) + (27802,)
FISH_LEARN_PATH = r'C:\MaxExec\fish_learn.txt'

_FISH = {
    'win': None, 'state': 'stop', 't0': 0.0,
    'delay': 'auto', 'cur_delay': 0,
    'keep': 0, 'spot': None, 'home': None,
    'bite_t': 0.0, 'bite_fish': '', 'bite_isfish': 0,
    'last_result': '', 'cast_t': 0.0, 'bait_t': 0.0, 'pill': 0,
    'stats': {'atis': 0, 'isirtma': 0, 'ok': 0, 'hata': 0, 'birak': 0, 'yerhata': 0, 'asim': 0},
    'inv0': 0, 'hooks': [], 'auto_i': 0, 'learn': {},
}

# v4.3 KANIT: LegendySF fishing.h:12 FISH_MIND_PILL_VNUM = 27610
#   char_item.cpp:3053: kullanilinca AddAffect(AFFECT_FISH_MIND_PILL, 20dk)
#   fishing.cpp:374 PredictFish: hapi/presitz/varsa TRUE ->
#   event 420: FISH paketi yollar -> client OnFishingNotify(isfish, adi)
#   (client PythonNetworkStreamPhaseGame.cpp GC_FISH subheader)
#   HAPISIZ: REACT'ta python callback YOK -> dongu isirtmayi goremzdi.
FISH_MIND_PILL = 27610

def _fish_try_pill():
    """boot'ta 1 kez: balik-zihni hapi varsa kullan"""
    if _FISH['pill']:
        return
    import player, net
    try:
        total = int(player.INVENTORY_SLOT_COUNT)
    except:
        total = 90
    for s in range(total):
        try:
            v = int(player.GetItemIndex(s))
        except:
            continue
        if v == FISH_MIND_PILL:
            try:
                net.SendItemUsePacket(s)
                _FISH['pill'] = 1
                _live('FISH: balik-zihni hapi kullanildi (slot %d) - isirtmada balik adi akacak' % s)
            except:
                pass
            return
    _live('FISH: HAPI YOK -> /i 27610 yaz, envantere alip fish yeniden baslat (isirtmada balik adi + %100 guvenli algila icin ONEMLI)')

def _fish_learn_load():
    try:
        f = open(FISH_LEARN_PATH, 'r')
        for ln in f:
            p = ln.rstrip('\n').split('\t')
            if len(p) >= 4:
                try:
                    _FISH['learn'].setdefault(p[0], {})[int(p[1])] = [int(p[2]), int(p[3])]
                except:
                    pass
        f.close()
    except:
        pass

def _fish_learn_save():
    try:
        f = open(FISH_LEARN_PATH, 'w')
        for fn, dd in _FISH['learn'].items():
            for d, v in dd.items():
                f.write('%s\t%d\t%d\t%d\n' % (fn, d, v[0], v[1]))
        f.close()
    except:
        pass

def _fish_time_ms():
    try:
        import app
        return int(app.GetTime() * 1000.0)
    except:
        return int(time.time() * 1000.0)

def _fish_install_hooks():
    """game.GameWindow fishing callback'lerini yakala (kanit:
    PythonNetworkStreamPhaseGame.cpp 3916-3943 PyCallClassMemberFunc)"""
    if _FISH['hooks']:
        return 'zaten kurulu'
    ok = []
    try:
        import game
        gw = getattr(game, 'GameWindow', None)
        if gw is None:
            return 'game.GameWindow bulunamadi'
        def _mk(name, tag):
            orig = getattr(gw, name, None)
            def patched(*a):
                try:
                    _fish_event(tag, a)
                except:
                    pass
                if orig is not None:
                    try:
                        return orig(*a)
                    except:
                        pass
            return name, orig, patched
        for name, tag in (('OnFishingNotify', 'NOTIFY'), ('OnFishingSuccess', 'SUCCESS'),
                          ('OnFishingFailure', 'FAIL'), ('OnFishingWrongPlace', 'WRONGPLACE'),
                          ('OnFishingNotifyUnknown', 'UNKNOWN')):
            try:
                nm, orig, patched = _mk(name, tag)
                setattr(gw, name, patched)
                _FISH['hooks'].append((gw, name, orig))
                ok.append(name)
            except Exception, e:
                ok.append('%s:HATA(%s)' % (name, _fmt_error(e)))
        return ','.join(ok)
    except Exception, e:
        return 'HATA: ' + _fmt_error(e)

def _fish_remove_hooks():
    for gw, name, orig in _FISH['hooks']:
        try:
            if orig is not None:
                setattr(gw, name, orig)
        except:
            pass
    _FISH['hooks'] = []

def _fish_event(tag, args):
    if tag == 'NOTIFY':
        try:
            _FISH['bite_fish'] = str(args[1]); _FISH['bite_isfish'] = int(args[0])
        except:
            pass
        _FISH['bite_t'] = _fish_time_ms()
        _FISH['stats']['isirtma'] += 1
        _live('FISH: ISIRTMA! (%s) %s' % (_FISH['bite_fish'] or 'isim yok', _FISH['delay'] == 'auto' and 'gecikme=ogren' or ('gecikme=%dms' % _FISH['delay'])))
    elif tag == 'SUCCESS':
        fn = ''
        try:
            fn = str(args[1])
        except:
            pass
        _FISH['last_result'] = 'OK:' + fn
        _FISH['stats']['ok'] += 1
        _live('FISH: TUTTU! %s (golveren balik: %d)' % (fn, _fish_count()))
    elif tag == 'FAIL':
        _FISH['last_result'] = 'FAIL'
        _FISH['stats']['hata'] += 1
        _live('FISH: kacti - hemen yeniden hazirlaniyor (yem kontrol)')
        if _FISH['state'] == 'wait':
            _FISH['state'] = 'pre'
            _FISH['t0'] = _fish_time_ms()
    elif tag == 'WRONGPLACE':
        _FISH['stats']['yerhata'] += 1
        _FISH['last_result'] = 'WRONGPLACE'
        _live('FISH: yanlis yer! fishspot <x> <y> ile su-kenari koordinatini isaretle')
        if _FISH['state'] == 'wait':
            _FISH['state'] = 'pre'
            _FISH['t0'] = _fish_time_ms()
    elif tag == 'UNKNOWN':
        _FISH['bite_t'] = _fish_time_ms()
        _FISH['bite_fish'] = '?'
        _FISH['stats']['isirtma'] += 1
        _live('FISH: ISIRTMA! (bilinmeyen)')

def _fish_count():
    import player
    n = 0
    try:
        total = int(player.INVENTORY_SLOT_COUNT)
    except:
        total = 90
    for s in range(total):
        try:
            v = int(player.GetItemIndex(s))
        except:
            continue
        if v in FISH_LIVE or v in FISH_DEAD:
            n += 1
    return n

def _fish_find_rod():
    import player
    try:
        total = int(player.INVENTORY_SLOT_COUNT)
    except:
        total = 90
    for s in range(total):
        try:
            v = int(player.GetItemIndex(s))
        except:
            continue
        if FISH_ROD_MIN <= v <= FISH_ROD_MAX:
            return s
    return -1

def _fish_find_bait():
    import player
    try:
        total = int(player.INVENTORY_SLOT_COUNT)
    except:
        total = 90
    for s in range(total):
        try:
            v = int(player.GetItemIndex(s))
        except:
            continue
        if v in FISH_BAITS:
            return s
    return -1

def _fish_rod_equipped():
    import player
    eb = _eq_base()
    try:
        v = int(player.GetItemIndex(eb + 4))
        return FISH_ROD_MIN <= v <= FISH_ROD_MAX
    except:
        return False

def _fish_rod_skill():
    import player
    eb = _eq_base()
    try:
        return int(player.GetItemMetinSocket(eb + 4, 2))
    except:
        return -1

def _fish_pick_delay():
    """auto modda ogrenilmis en iyi gecikme; yoksa siradaki aday"""
    if _FISH['delay'] != 'auto':
        return int(_FISH['delay'])
    fn = _FISH['bite_fish']
    dd = _FISH['learn'].get(fn)
    if dd:
        best = None; bestrate = -1.0
        for d, v in dd.items():
            if v[0] >= 3:
                r = float(v[1]) / float(v[0])
                if r > bestrate:
                    bestrate = r; best = d
        if best is not None:
            return int(best)
    steps = FISH_DELAY_AUTO_STEPS
    d = steps[_FISH['auto_i'] % len(steps)]
    _FISH['auto_i'] += 1
    return int(d)

def _fish_status_line():
    st = _FISH['stats']
    b = st['isirtma']; ok = st['ok']
    pct = ('%.1f' % (100.0 * ok / b)) if b > 0 else '0.0'
    sk = _fish_rod_skill()
    return 'FISH durum=%s | atis=%d isirtma=%d tutulan=%d kacan=%d oran=%s%% | olta-skill=%s | balik-env=%d | gecikme=%s' % (
        _FISH['state'], st['atis'], b, ok, st['hata'], pct,
        (str(sk) if sk >= 0 else '?'), _fish_count(),
        ('auto/ogren' if _FISH['delay'] == 'auto' else str(_FISH['delay']) + 'ms'))

class _FishLoopWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            import player, chr, net, chrmgr
            st = _FISH
            now = _fish_time_ms()
            sn = st['state']
            if sn == 'stop':
                return
            if sn == 'boot':
                r = _fish_install_hooks()
                _fish_learn_load()
                st['inv0'] = _fish_count()
                _fish_try_pill()
                st['state'] = 'pre'; st['t0'] = now
                _live('FISH basladi | hook=%s | hapi=%s | balik-env=%d | %s' % (r, st['pill'], st['inv0'], _fish_status_line()))
                return
            # ortak guvenlik: secim bende olsun
            if sn in ('cast', 'take'):
                try:
                    chr.SelectInstance(int(player.GetMainCharacterIndex()))
                except:
                    pass
            if sn == 'pre':
                # olta takili mi?
                if not _fish_rod_equipped():
                    rs = _fish_find_rod()
                    if rs < 0:
                        _fish_stop_err('oltada YOK (env: /i 27400 ile olustur)')
                        return
                    if now - st['t0'] > 700:
                        net.SendItemUsePacket(rs)
                        st['t0'] = now
                    return
                # yem var mi? (soket2 = yem seviyesi; KACIRMA 0'a duser!)
                if _fish_rod_skill() == 0:
                    bs = _fish_find_bait()
                    if bs < 0:
                        _fish_stop_err('yem YOK (/i 27801 200 ile solucan)')
                        return
                    if now - st['t0'] > 700:
                        net.SendItemUsePacket(bs)
                        st['state'] = 'baitwait'
                        st['t0'] = now
                    return
                st['state'] = 'cast'; st['t0'] = now
                return
            if sn == 'baitwait':
                # v4.3: yemin oltaya takilmasini BEKLE (soket2>0) - yemsiz
                # atis sunucuda reddedilir (char.cpp: 'yem tak' + return)
                if _fish_rod_skill() > 0:
                    st['state'] = 'cast'; st['t0'] = now
                    _live('FISH: yem takildi (seviye=%d) - atis hazir' % _fish_rod_skill())
                    return
                if now - st['t0'] > 4000:
                    st['state'] = 'pre'; st['t0'] = now
                return
            if sn == 'cast':
                if now - st['t0'] < 300:
                    return
                # fishspot modu: su kenarina isinla, at, geri don
                if st['spot']:
                    try:
                        chr.SetPixelPosition(int(st['spot'][0]), int(st['spot'][1]))
                    except:
                        pass
                player.SetAttackKeyState(1)
                st['state'] = 'cast2'; st['t0'] = now
                return
            if sn == 'cast2':
                player.SetAttackKeyState(0)
                st['stats']['atis'] += 1
                st['bite_fish'] = ''; st['bite_isfish'] = 0; st['last_result'] = ''
                st['bite_t'] = 0
                st['state'] = 'gotown'; st['t0'] = now
                return
            if sn == 'gotown':
                if now - st['t0'] >= 1000:
                    if st['spot'] and st['home']:
                        try:
                            chr.SetPixelPosition(int(st['home'][0]), int(st['home'][1]))
                        except:
                            pass
                    st['state'] = 'wait'; st['t0'] = now
                    _live('FISH: oltayi atti (%d. atis) bekleniyor...' % st['stats']['atis'])
                return
            if sn == 'wait':
                # isirtma: hook (NOTIFY) ya da baloncuk (emoticon mesgul)
                bite = False
                if st['bite_t'] > 0 and st['bite_fish'] != '':
                    bite = True
                else:
                    # v4.3: baloncuk hem secili hem ANA instance'ta bakilir
                    # (chrmgr.IsPossibleEmoticon -> GetSelectedInstancePtr /
                    #  GetInstancePtr; InstanceBaseEffect.cpp:1007)
                    try:
                        if not chrmgr.IsPossibleEmoticon(-1):
                            bite = True
                    except:
                        pass
                    if not bite:
                        try:
                            mv = int(net.GetMainActorVID())
                            if mv > 0 and not chrmgr.IsPossibleEmoticon(mv):
                                bite = True
                        except:
                            pass
                    if bite:
                        st['bite_t'] = now
                        if not st['bite_fish']:
                            st['bite_fish'] = 'baloncuk'
                if bite:
                    st['state'] = 'bite'
                    return
                if now - st['t0'] > 50000:
                    st['stats']['asim'] += 1
                    _live('FISH: 45sn isirtma yok - tekrar atiliyor')
                    st['state'] = 'pre'; st['t0'] = now
                return
            if sn == 'bite':
                d = _fish_pick_delay()
                st['cur_delay'] = d
                if now - st['bite_t'] >= d:
                    player.SetAttackKeyState(1)
                    st['state'] = 'take'; st['t0'] = now
                return
            if sn == 'take':
                player.SetAttackKeyState(0)
                st['state'] = 'result'; st['t0'] = now
                return
            if sn == 'result':
                if now - st['t0'] < 1200:
                    return
                # sonuc: hook SUCCESS/FAIL zaten saydi; envanter degisimi de bak
                inv = _fish_count()
                fn = st['bite_fish']
                if st['last_result'].startswith('OK'):
                    # ogren: (balik, gecikme) -> basari
                    if fn and fn != 'baloncuk':
                        dd = st['learn'].setdefault(fn, {})
                        v = dd.setdefault(st['cur_delay'], [0, 0])
                        v[0] = v[0] + 1; v[1] = v[1] + 1
                        _fish_learn_save()
                    # fishkeep: istenmeyen baligi birak
                    if st['keep'] > 0:
                        _fish_drop_unwanted(st['keep'])
                elif st['last_result'] == 'FAIL':
                    if fn and fn != 'baloncuk':
                        dd = st['learn'].setdefault(fn, {})
                        v = dd.setdefault(st['cur_delay'], [0, 0])
                        v[0] = v[0] + 1
                        _fish_learn_save()
                st['bite_fish'] = ''
                st['state'] = 'pre'; st['t0'] = now
                _live(_fish_status_line())
                return
        except Exception, e:
            _live('FISH dongu hatasi: ' + _fmt_error(e))
            _FISH['state'] = 'pre'; _FISH['t0'] = _fish_time_ms()

def _fish_drop_unwanted(keep):
    import player, net
    try:
        total = int(player.INVENTORY_SLOT_COUNT)
    except:
        total = 90
    for s in range(total):
        try:
            v = int(player.GetItemIndex(s))
        except:
            continue
        if v > 0 and (v in FISH_LIVE or v in FISH_DEAD) and v != keep:
            try:
                net.SendItemDropPacketNew(s, 1)
                _FISH['stats']['birak'] += 1
                _live('FISH: %d birakildi (hedef %d)' % (v, keep))
                return
            except:
                pass

def _fish_stop_err(msg):
    _live('FISH DURDU: ' + msg)
    _write('fish', 'DURDU: ' + msg + '\n' + _fish_status_line())
    fishstop()

def _start_fish(res):
    try:
        if not _ingame():
            _write(res, 'HATA: oyunda degilsin (balik icin oyunda ol)\n')
            return
        if _FISH['win'] is None:
            _FISH['win'] = _FishLoopWnd()
        _FISH['state'] = 'boot'
        _FISH['t0'] = _fish_time_ms()
        _write(res, 'OK: balik dongusu BASLADI\nmod: gecikme=%s (auto-ogrenici) | fishkeep=%s | fishspot=%s | hapi=%s\nAKIS: olta+yem otomatik kontrol, atis otomatik, isirtmada otomatik cekis\nCANLI IZLEME: cmd penceresinde [LIVE] satirlari akar\nHAPI: /i 27610 -> her isirtmada balik adi gelir (100% algila)\nayarlar: fishkeep <vnum|0> | fishspot <x> <y> | fishspot 0\ndurdur: fishstop | rapor: fishstat' % (
            str(_FISH['delay']), str(_FISH['keep'] or 'kapali'), str(_FISH['spot'] or 'kapali'), str(_FISH['pill'])))
    except Exception, e:
        _write(res, 'HATA ' + _fmt_error(e) + '\n')

def fish():
    _start_fish('fish')


def fishstop():
    try:
        _FISH['state'] = 'stop'
        _fish_remove_hooks()
        try:
            import player
            player.SetAttackKeyState(0)
        except:
            pass
        try:
            if _FISH['win'] is not None:
                _FISH['win'].Hide()
                _FISH['win'].Destroy()
        except:
            pass
        _FISH['win'] = None
        _write('fish', 'OK: balik dongusu durdurdu\n' + _fish_status_line())
        _live('FISH: durduruldu')
    except Exception, e:
        _write('fishstop', 'HATA ' + _fmt_error(e) + '\n')

def fishkeep(vnum):
    try:
        v = int(vnum)
        _FISH['keep'] = v
        if v > 0:
            _write('fishkeep', 'OK: sadece vnum %d tutulacak, diger baliklar YERE BIRAKILACAK (0=hepsi tutulur)\nNOT: balik secimi sunucuda zar atilir (DetermineFish) - istemci secemez; bu filtre istemedigini birakir' % v)
        else:
            _write('fishkeep', 'OK: filtre kapali (hepsi tutulur)')
    except Exception, e:
        _write('fishkeep', 'HATA ' + _fmt_error(e) + '\n')

def fishspot(x, y):
    try:
        xi = int(x); yi = int(y)
        if xi == 0 and yi == 0:
            _FISH['spot'] = None
            _write('fishspot', 'OK: su-noktasi KAPALI (normal mod: su kenarinda durup atar)')
            return
        import chr, player
        me = _my_vid()
        p = chr.GetPixelPosition(me)
        _FISH['spot'] = (xi, yi)
        _FISH['home'] = (int(p[0]), int(p[1]))
        _write('fishspot', 'OK: su-noktasi=(%d,%d), calisma-noktasi=(%d,%d)\nMOD: her atista su kenarina isinla -> at -> geri isinla -> bekle\n(istemci cast icin 400 birim icinde su ister; SUNUCU istemez - buradan\n sonrasina bakilmaksizin balik gelir! su kenarina gitmek icin once oraya\n yuru: goto <x> <y>, sonra fishspot <x> <y> ile noktayi isaretle)' % (xi, yi, int(p[0]), int(p[1])))
    except Exception, e:
        _write('fishspot', 'HATA ' + _fmt_error(e) + '\n')

def fishstat():
    try:
        L = ['BALIK RAPORU', _fish_status_line(),
             'son sonuc: %s' % (_FISH['last_result'] or '-'),
             'ogrenilen tablo (balik -> gecikme: deneme/basari):']
        for fn, dd in _FISH['learn'].items():
            parts = []
            for d, v in sorted(dd.items()):
                parts.append('%dms:%d/%d' % (d, v[1], v[0]))
            L.append('  %s -> %s' % (fn, ' '.join(parts)))
        L.append('tablo dosyasi: %s' % FISH_LEARN_PATH)
        L.append('resmi tepki tablosu (kova=(ms+99)/200): tip3=hep %100; tip2 aninda 80; tip0 gecikmeli 80; tip1 5sn civari 80')
        _write('fishstat', '\n'.join(L) + '\n')
    except Exception, e:
        _write('fishstat', 'HATA ' + _fmt_error(e) + '\n')

def fishtest():
    """tek atis testi: olta+yem kontrol, at, isirtmayi bekleme - durum raporu"""
    try:
        if not _ingame():
            _write('fishtest', 'HATA: oyunda degilsin\n')
            return
        import player, chr, net
        out = ['FISH TEST RAPORU']
        out.append('olta takili: %s' % _fish_rod_equipped())
        rs = _fish_find_rod()
        out.append('envanterde olta slot: %s' % (rs if rs >= 0 else 'YOK'))
        bs = _fish_find_bait()
        out.append('envanterde yem slot: %s (27800/27801/27802)' % (bs if bs >= 0 else 'YOK'))
        out.append('olta-skill (soket2): %d' % _fish_rod_skill())
        out.append('envanterde balik: %d adet' % _fish_count())
        try:
            import chrmgr
            out.append('baloncuk musait (IsPossibleEmoticon): %d (1=temiz)' % int(chrmgr.IsPossibleEmoticon(-1)))
        except:
            pass
        if rs >= 0:
            out.append('ONERI: fish yaz (otomatik dongu) | tek atis: key SPACE 1 sonrasinda key SPACE 0')
        _write('fishtest', '\n'.join(out) + '\n')
    except Exception, e:
        _write('fishtest', 'HATA ' + _fmt_error(e) + '\n')


# ---------------------------------------------------------------------------
# v4.3 OPTIMIZETP (otp) - sunucuyla SENKRON adimli isinlama
# KANIT: input_main.cpp CG_MOVE: FUNC_MOVE -> ch->Goto(x,y) (sunucu YURUR);
#   ENABLE_TP_SPEED_CHECK: yuruyus paketinde mesafe > 25m (binmede 60m)
#   -> ch->Show(eski konum) = GERI ATMA (kullanicinin saha raporu: birebir).
#   -> otp: her adim SetPixelPosition(adim) + MoveToDestPosition(adim) +
#      bekle. Adim <= otpstep px (240px = 24m < 25m). Istemci aninda ilerler,
#      sunucu adim adim takip eder -> hareket serbest, geri atlama yok.
# ---------------------------------------------------------------------------
_OTP = {'win': None, 'on': 0, 'mode': 1, 'tx': 0, 'ty': 0, 'step': 240,
        'delay': 50, 't0': 0.0, 'n': 0,
        # v4.8 otp2 SUREKLI BASILI modu icin ek durum
        'lastd': 0.0, 'stuck': 0}

def _otp_keys_release():
    """v4.8 GUVENLIK: otp hangi modda olursa olsun TUM tuslari MUTLAKA birak.
    (saldiri tusu + W + UP ok tusu - game.py MoveUp kaniti DIK_UP kullaniyor;
    kullanici otp2'de 'basili tutsun, varinca biraksin' istedi - otpstop ve
    varis buradan gecer.)"""
    try:
        import player
        player.SetAttackKeyState(0)
    except:
        pass
    try:
        import player, app
        player.SetSingleDIKKeyState(app.DIK_W, 0)
        player.SetSingleDIKKeyState(app.DIK_UP, 0)
    except:
        pass

class _OtpWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        # v4.9: govde _otp_tick'te - DLL nabzi (maxlib._tick) + bu pencere
        # ayni govdeyi cagirir (cift surus, zaman kapili -> guvenli).
        _otp_tick()

def _otp_tick():
    """v4.9 OTP dongu govdesi:
    mod 1 = saldiri-tusu adimlama (v4.4'ten beri kanitli),
    mod 2 = ISINLANA-ISINLANA + ADIM (saha testi 15 kullanici tarifi:
    'isinlana isinlana gidecek ama yine adim atacak - her adim
    sendcharacterstate tetikler, oyun bizi geri atmasin diye')."""
    try:
        import chr, player
        st = _OTP
        if not st['on']:
            return
        now = _fish_time_ms()
        # v4.9: mod 2 en az 100ms nabiz; mod 1 otpdelay ile ayarlanir
        tick = st['delay'] if st['mode'] == 1 else max(100, st['delay'])
        if now - st['t0'] < tick:
            return
        st['t0'] = now
        vid = 0
        try:
            vid = int(player.GetMainCharacterIndex())
        except:
            vid = 0
        try:
            chr.SelectInstance(vid)
        except:
            pass
        p = chr.GetPixelPosition(vid)
        cx = int(p[0]); cy = int(p[1])
        dx = st['tx'] - cx; dy = st['ty'] - cy
        dist = (dx * dx + dy * dy) ** 0.5
        arrive = st['step'] * 1.2 if st['mode'] == 1 else max(120, st['step'] / 2)
        if dist <= arrive:
            _otp_keys_release()
            st['on'] = 0
            try:
                st['win'].Hide(); st['win'].Destroy()
            except:
                pass
            st['win'] = None
            yontem = 'adim-adim (saldirtusu)' if st['mode'] == 1 else 'isinlana-isinlana + adim'
            _live('OTP: varildi (%s) konum=(%d,%d)' % (yontem, cx, cy))
            _write('otp', 'OK: varildi (%s). konum=(%d,%d)\nNOT: tum tuslar birakildi' % (yontem, cx, cy))
            return
        if st['mode'] == 2:
            # v4.9 ISINLANA-ISINLANA + ADIM (kullanici tarifi - saha testi 15):
            #  1) ISINLANMA sicramasi: SetPixelPosition (darealfreakbot.py:692
            #     + Teleporthack-Music SetPixelPosition kaniti) - adim <= 240px
            #     (25m TP-kontrol altinda; otpstep 240 onerilen)
            #  2) GERCEK ADIM: MoveToDestPosition(vid, x, y) (eiglib WalkCOORD
            #     + WalkToMobs kaniti) + 1-kare UP basilisi (darealfreakbot
            #     Debug() deseni: SetSingleDIKKeyState(UP,1) sonra 0) ->
            #     her adimda sendcharacterstate tetiklenir, sunucu konumu
            #     takip eder -> geri atma YOK
            #  3) net.SendCharacterPositionPacket (warp'in ek konum senkronu)
            import app, net
            step = st['step']
            if step > 240:
                step = 240          # 25m TP-kontrol guvenlik tavani
            if step > dist:
                step = dist
            k = step / dist
            nx = int(cx + dx * k); ny = int(cy + dy * k)
            try:
                chr.SetPixelPosition(nx, ny)
            except:
                pass
            try:
                chr.MoveToDestPosition(vid, nx, ny)
            except:
                pass
            try:
                player.SetSingleDIKKeyState(app.DIK_UP, 1)
                player.SetSingleDIKKeyState(app.DIK_UP, 0)
            except:
                pass
            try:
                net.SendCharacterPositionPacket()
            except:
                pass
            st['n'] += 1
            # ilerleme tani: uzaklik ARTIYORSA engel/yone carpma demektir
            if st['lastd'] > 0 and dist > st['lastd'] + 30:
                st['stuck'] += 1
                if st['stuck'] % 10 == 1:
                    _live('OTP2: uzaklik artiyor (%d->%dpx) - engel var olabilir' % (int(st['lastd']), int(dist)))
            st['lastd'] = dist
            if st['n'] % 20 == 0:
                _live('OTP2: isinlana-isinlana + adim, kalan ~%dpx (%d adim)' % (int(dist), st['n']))
        else:
            try:
                player.SetAttackKeyState(1)
            except:
                pass
            k = st['step'] / dist
            nx = int(cx + dx * k); ny = int(cy + dy * k)
            try:
                chr.SetPixelPosition(nx, ny)
            except:
                pass
            try:
                chr.MoveToDestPosition(vid, nx, ny)
            except:
                pass
            st['n'] += 1
            if st['n'] % 10 == 0:
                _live('OTP: %d adim, kalan ~%dpx' % (st['n'], int(dist)))
    except Exception, e:
        _live('OTP hatasi: ' + _fmt_error(e))
        _otp_keys_release()
        _OTP['on'] = 0
        _OTP['lastd'] = 0.0
        _OTP['stuck'] = 0


def _otp_start(x, y, mode):
    # v4.9 ALT-KOMUT (saha testi 15: 'otp delay 1' ValueError yiyordu):
    # artik 'otp delay <ms>' / 'otp step <px>' / 'otp stop' da calisir.
    try:
        a = str(x).strip().lower()
        if a in ('delay', 'bekle', 'otpdelay'):
            otpdelay(y)
            return
        if a in ('step', 'adim', 'otpstep'):
            otpstep(y)
            return
        if a in ('stop', 'dur', 'kapat', '0'):
            otpstop()
            return
        if not _ingame():
            _write('otp', 'HATA: oyunda degilsin\n')
            return
        import chr
        _OTP['tx'] = int(x); _OTP['ty'] = int(y)
        _OTP['mode'] = int(mode)
        _OTP['on'] = 1; _OTP['n'] = 0
        _OTP['lastd'] = 0.0; _OTP['stuck'] = 0
        _OTP['t0'] = _fish_time_ms() - 99999
        if _OTP['win'] is None:
            _OTP['win'] = _OtpWnd()
        p = chr.GetPixelPosition(_my_vid())
        if _OTP['mode'] == 2:
            _write('otp2', 'OK: (%d,%d) -> (%d,%d) | MOD 2 v4.9: ISINLANA-ISINLANA + ADIM\nher adim: SetPixelPosition sicramasi + MoveToDestPosition + 1-kare UP basin\n-> sendcharacterstate tetiklenir, sunucu takip eder (geri atma YOK)\nadim boyu: %dpx (otpstep ile ayarla; 240=24m guvenli) | dur: otpstop\notp1 <x> <y> = saldiri-tusu yontemi' % (int(p[0]), int(p[1]), _OTP['tx'], _OTP['ty'], _OTP['step']))
        else:
            _write('otp1', 'OK: (%d,%d) -> (%d,%d) | adim=%dpx bekle=%dms | MOD 1: SALDIRI tusu basili (v4.4 kanitli)\nDur: otpstop | ayar: otpstep/otpdelay | diger yontem: otp2 (isinlana-isinlana + adim)' % (int(p[0]), int(p[1]), _OTP['tx'], _OTP['ty'], _OTP['step'], _OTP['delay']))
    except Exception, e:
        _write('otp', 'HATA ' + _fmt_error(e) + '\nkullanim: otp <x> <y> | otp delay <ms> | otp step <px> | dur: otpstop\n')

def otp1(x, y):
    """OPTIMIZETP YONTEM 1 (MEVCUT KANITLI YONTEM - v4.4'ten beri):
    sunucuyla senkron adim adim isinlama; yol boyunca SALDIRI tusu basili
    (geri-tepme engeli), varista birakir. Dur: otpstop
    v4.9: 'otp delay <ms>' / 'otp step <px>' / 'otp stop' da calisir."""
    _otp_start(x, y, 1)

def otp2(x, y):
    """OPTIMIZETP YONTEM 2 (v4.9 - ISINLANA-ISINLANA + ADIM, kullanici tarifi):
    her adimda SetPixelPosition sicramasi + MoveToDestPosition + 1-kare UP
    basin -> sendcharacterstate tetiklenir, sunucu konumu takip eder, oyun
    geri atmaz. Adim boyu otpstep (240px oneri = 24m, 25m kontrol altinda).
    Varista tuslar otomatik birakilir. Dur: otpstop (veya 'otp stop')"""
    _otp_start(x, y, 2)

otp = otp1
optimizetp = otp1



def otpstop():
    try:
        _OTP['on'] = 0
        _otp_keys_release()      # v4.7 FIX: durdurunca tuslar MUTLAKA birakilir
        try:
            if _OTP['win'] is not None:
                _OTP['win'].Hide(); _OTP['win'].Destroy()
        except:
            pass
        _OTP['win'] = None
        _write('otpstop', 'OK: otp durduruldu (%d adim) - saldiri ve yuruyus tuslari birakildi' % _OTP['n'])
    except Exception, e:
        _write('otpstop', 'HATA ' + _fmt_error(e) + '\n')


def otpstep(v):
    try:
        n = int(v)
        if n < 50: n = 50
        if n > 600: n = 600
        _OTP['step'] = n
        _write('otpstep', 'OK: adim=%dpx (240=24m: TP-kontrol 25m alti GUENLI; ustu geri atma riski)' % n)
    except Exception, e:
        _write('otpstep', 'HATA ' + _fmt_error(e) + '\n')

def otpdelay(v):
    try:
        n = int(v)
        if n < 10: n = 10
        if n > 10000: n = 10000
        _OTP['delay'] = n
        _write('otpdelay', 'OK: bekleme=%dms (dusuk=hizli; 50 varsayilan)\nnot: mod 1 icin gecerli; mod 2 (isinlana+adim) en az 100ms nabizla atar' % n)
    except Exception, e:
        _write('otpdelay', 'HATA ' + _fmt_error(e) + '\n')


# ---------------------------------------------------------------------------
# v4.3 CLONEMOD - klon ile yer degis / klon takip (ayna)
# GERCEK KONTROL IMKANSIZ (sunucu hareket paketlerini gercek karakterden
# alir; baska instance'a input yolu YOK) -> sunun en yakin hali:
#   swap = yer degis-tokus | 1 = klon seni aynalar | 0 = kapat
# ---------------------------------------------------------------------------
_CLONEMOD = {'win': None, 'follow': 0, 'offset': 70}

class _CloneFollowWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            if not _CLONEMOD['follow'] or not _CLONE['vids']:
                return
            import chr
            vid = _CLONE['vids'][-1]
            me = _my_vid()
            p = chr.GetPixelPosition(me)
            x = int(p[0]) + _CLONEMOD['offset']; y = int(p[1]) - _CLONEMOD['offset']
            try:
                chr.SelectInstance(vid)
                try:
                    chr.SetPixelPosition(x, y, int(p[2]))
                except:
                    chr.SetPixelPosition(x, y)
            except:
                pass
            try:
                chr.SelectInstance(me)
            except:
                pass
        except:
            pass

def clonemod(mode):
    """klon modu: swap=yer degis-tokus | 1=klon takip (ayna) | 0=kapat"""
    try:
        if not _ingame():
            _write('clonemod', 'HATA: oyunda degilsin\n')
            return
        import chr
        s = str(mode).strip().lower()
        if s in ('0', 'off', 'kapat'):
            _CLONEMOD['follow'] = 0
            try:
                if _CLONEMOD['win'] is not None:
                    _CLONEMOD['win'].Hide(); _CLONEMOD['win'].Destroy()
            except:
                pass
            _CLONEMOD['win'] = None
            _write('clonemod', 'OK: klon takip KAPATILDI')
            return
        if not _CLONE['vids']:
            _write('clonemod', 'HATA: klon yok - once clone yaz')
            return
        cv = _CLONE['vids'][-1]
        me = _my_vid()
        if s == 'swap':
            pp = chr.GetPixelPosition(me)
            cp = chr.GetPixelPosition(cv)
            chr.SelectInstance(me)
            try:
                chr.SetPixelPosition(int(cp[0]), int(cp[1]), int(cp[2]))
            except:
                chr.SetPixelPosition(int(cp[0]), int(cp[1]))
            chr.SelectInstance(cv)
            try:
                chr.SetPixelPosition(int(pp[0]), int(pp[1]), int(pp[2]))
            except:
                chr.SetPixelPosition(int(pp[0]), int(pp[1]))
            try:
                chr.SelectInstance(me)
            except:
                pass
            _write('clonemod', 'OK: YER DEGIS-TOKUS yapildi (sen <-> klon vid=%d)\nNOT: istemci-tarafi; sunucu seni eski konumda gorur -\n yurumek/uzaklasmak icin otp kullan' % cv)
            return
        _CLONEMOD['follow'] = 1
        if _CLONEMOD['win'] is None:
            _CLONEMOD['win'] = _CloneFollowWnd()
        _write('clonemod', 'OK: klon TAKIP modu (vid=%d her adimda yaninda aynalanir)\nKAPAT: clonemod 0 | YER DEGIS: clonemod swap\nNOT: gercek kontrol sunucuda kalir - input hep gercek karaktere gider; klon gorunum/ayna yoldasidir' % cv)
    except Exception, e:
        _write('clonemod', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# v4.3 SPAWNSCAN - istemci mob_proto taramasi (spawn/morph icin gecerli race)
# KANIT: PythonNonPlayerModule.cpp:70 GetMonsterName(vnum) -> mob_proto ad.
# Instance YARATMAZ - data okur: guvenli + hizli. TAM liste:
#   C:\MaxExec\spawnscan_full.txt
# ---------------------------------------------------------------------------
def spawnscan(mn=1, mx=30000):
    try:
        if not _ingame():
            _write('spawnscan', 'HATA: oyunda degilsin\n')
            return
        import nonplayer
        a = int(mn); b = int(mx)
        if b < a:
            a, b = b, a
        if b - a > 100000:
            b = a + 100000
        found = []
        for v in xrange(a, b + 1):
            nm = ''
            try:
                nm = str(nonplayer.GetMonsterName(v))
            except:
                continue
            if nm:
                found.append((v, nm))
        path = r'C:\MaxExec\spawnscan_full.txt'
        try:
            f = open(path, 'w')
            f.write('spawnscan %d-%d: %d gecerli race\n' % (a, b, len(found)))
            for v, nm in found:
                f.write('race=%-7d %s | spawn %d | morph %d\n' % (v, nm, v, v))
            f.close()
        except Exception, e2:
            path = 'YAZILAMADI: ' + _fmt_error(e2)
        L = ['spawnscan %d-%d: %d gecerli race (istemci mob_proto)' % (a, b, len(found))]
        for v, nm in found[:80]:
            L.append('  race=%-7d %s' % (v, nm))
        if len(found) > 80:
            L.append('  ... +%d daha -> TAM LISTE: %s' % (len(found) - 80, path))
        L.append('kullanim: spawn <race> | morph <race>')
        _write('spawnscan', '\n'.join(L) + '\n')
    except Exception, e:
        _write('spawnscan', 'HATA ' + _fmt_error(e) + '\n')

# ===========================================================================
# v4.4 YENI KOMUTLAR (saha testi 10 istekleri)
# Kanitlar: buffbot.py player.GetTargetVID | New_Levelbot.py chr.GetRace(vid)
#   PythonCharacterModule.cpp chr.MountHorse(20030)/DismountHorse (saf istemci)
#   PythonCharacterManagerModule.cpp chrmgr.SetAffect(vid, efekt, gorunur)
#   multihack2/vbmultihack/Crap_Levelbot.py chr.SetMoveSpeed/SetAttackSpeed
#   uiCharacter.py '/stat ht' + '/skillup <idx>' | efsunbotu.py
#   net.SendItemUseToItemPacket + player.GetItemAttribute
# ===========================================================================
APPLY_NAMES = {
    1: 'max-hp', 2: 'max-sp', 3: 'con/vit', 4: 'int', 5: 'str', 6: 'dex',
    7: 'saldiri-hizi', 8: 'hareket-hizi', 9: 'buyu-hizi', 10: 'hp-yenileme',
    11: 'sp-yenileme', 12: 'zehir-sansi', 13: 'bayiltma-sansi', 14: 'yavaslatma-sansi',
    15: 'kritik-sansi', 16: 'delici-sansi', 17: 'insana-karsi-guc',
    18: 'hayvana-karsi', 19: 'orka-karsi', 20: 'milgyo-karsi', 21: 'oluye-karsi',
    22: 'seytana-karsi', 23: 'hp-emme', 24: 'sp-emme', 25: 'mana-yakma',
    26: 'hasar-sp-geri', 27: 'blok-sansi', 28: 'kacinma-sansi', 29: 'kilac-direnci',
    30: 'ciftel-kilic-direnci', 31: 'hanccer-direnci', 32: 'ccan-direnci',
    33: 'yelpaze-direnci', 34: 'ok-direnci', 35: 'ates-direnci', 36: 'simsek-direnci',
    37: 'buyu-direnci', 38: 'ruzgar-direnci', 39: 'vurus-yansitma',
    40: 'lanet-yansitma', 41: 'zehir-azaltma', 42: 'oldurme-sp-geri',
    43: 'exp-bonus', 44: 'yang-bonus', 45: 'esya-drop-bonus', 46: 'iksir-bonus',
    47: 'oldurme-hp-geri', 48: 'bayiltma-bagisiklik', 49: 'yavaslatma-bagisiklik',
    50: 'dusme-bagisiklik', 51: 'skill', 52: 'ok-menzili', 53: 'vurus-degeri',
    54: 'savunma-degeri', 55: 'buyu-vurus-degeri', 56: 'buyu-savunma',
    57: 'lanet-sansi', 58: 'max-stamina', 59: 'savasci-ya-karsi',
    60: 'ninjaya-karsi', 61: 'suraya-karsi', 62: 'samana-karsi',
    63: 'canavara-karsi-guc',
}

def morphtarget():
    """HEDEF'e donus (kullanici: 'targetledigine donus olsa mesela npcyi
    targetledim ona donusur veya bi mobu'). Oyun ICINDE bir NPC/mob/oyuncuya
    TIKLA (hedef secilir), sonra morphtarget yaz. Kanit: player.GetTargetVID
    (buffbot.py) + chr.GetRace(vid) (New_Levelbot.py/WalkToMobs.py)."""
    try:
        if not _ingame():
            _write('morphtarget', 'HATA: oyunda degilsin\n')
            return
        import chr, player
        tv = 0
        try:
            tv = int(player.GetTargetVID())
        except:
            tv = 0
        if tv <= 0:
            _write('morphtarget', 'HATA: hedef yok - once bir NPC/mob/oyuncuya TIKLA (sec), sonra morphtarget')
            return
        ttype = -1
        try:
            ttype = int(chr.GetInstanceType(tv))
        except:
            pass
        r = 0
        try:
            r = int(chr.GetRace(tv))
        except:
            r = 0
        nm = ''
        try:
            nm = str(chr.GetNameByVID(tv))
        except:
            pass
        if r <= 0:
            _write('morphtarget', 'HATA: hedefin race okunamadi (vid=%d ad=%s)' % (tv, nm))
            return
        if ttype == int(getattr(chr, 'INSTANCE_TYPE_PLAYER', 6)):
            # oyuncu -> mob_proto kontrolune takilma, dogrudan race degis
            import chr as _c
            me = _my_vid()
            try:
                if _CLONE['morph'] is None:
                    try:
                        _CLONE['morph'] = int(_c.GetRace(me))
                    except:
                        _CLONE['morph'] = 4
                _c.SelectInstance(me)
                _c.SetRace(r)
                _visual_kick(me)
                _write('morphtarget', 'OK: oyuncu %s (race=%d) gorunumune dondun\nGERI: unmorph | zirh farkliyse: setarmor <vnum>' % (nm, r))
            except Exception, e2:
                _write('morphtarget', 'HATA: %s' % _fmt_error(e2))
            return
        _write('morphtarget', 'BILGI: hedef vid=%d ad=%s race=%d -> morph uygulanuyor' % (tv, nm, r))
        morph(r)
    except Exception, e:
        _write('morphtarget', 'HATA ' + _fmt_error(e) + '\n')

def cloneplayer():
    """HEDEF OYUNCUYA donus (kullanici: 'cloneplayer eklense targetledigin
    playere donussun direk'). Okunabilen: race + AD (GetNameByVID).
    Zirh/sac DIGER oyuncunun instance'indan OKUNAMAZ (client getteri yok) -
    kendi kiyafetin kalir; setarmor <vnum> ile tamamlarsin."""
    try:
        if not _ingame():
            _write('cloneplayer', 'HATA: oyunda degilsin\n')
            return
        import chr, player
        tv = 0
        try:
            tv = int(player.GetTargetVID())
        except:
            tv = 0
        if tv <= 0:
            _write('cloneplayer', 'HATA: hedef yok - bir oyuncuya TIKLA (sec), sonra cloneplayer')
            return
        r = 0
        try:
            r = int(chr.GetRace(tv))
        except:
            r = 0
        nm = ''
        try:
            nm = str(chr.GetNameByVID(tv))
        except:
            pass
        if r <= 0:
            _write('cloneplayer', 'HATA: hedef race okunamadi (vid=%d ad=%s)' % (tv, nm))
            return
        me = _my_vid()
        try:
            if _CLONE['morph'] is None:
                try:
                    _CLONE['morph'] = int(chr.GetRace(me))
                except:
                    _CLONE['morph'] = 4
            chr.SelectInstance(me)
            chr.SetRace(r)
            try:
                chr.SetNameString(nm)   # istemci-tarafi isim (best-effort)
            except:
                pass
            _visual_kick(me)
            _write('cloneplayer', 'OK: %s (race=%d) gorunumune dondun (ISTEMCI: irk+ad)\nismi degismediyse: istemci ad-tablosundan geliyor (normal)\nzirh tamamlama: setarmor <vnum> | GERI: unmorph\nNOT: sen hala kendisin - sunucuda isim/binek ayni' % (nm, r))
        except Exception, e2:
            _write('cloneplayer', 'HATA: %s' % _fmt_error(e2))
    except Exception, e:
        _write('cloneplayer', 'HATA ' + _fmt_error(e) + '\n')

def fakemount(mode=1):
    """SAHTE BINIS (kullanici: 'at a binmis olsak ama binmemis durumda
    tipte gostertse ve hareket edebilsek yani skillde atabilsek').
    KANIT: PythonCharacterModule.cpp chr.MountHorse -> CInstanceBase::
    MountHorse(20030) - SAF ISTEMCI GORUNUMU, sunucuya paket GITMEZ!
    -> at ustunde GORUNURSUN, sunucu bilmeye devam eder: skill SERBEST.
    fakemount 1 = bin | fakemount 0 = in | gercek binis: chat /ride"""
    try:
        if not _ingame():
            _write('fakemount', 'HATA: oyunda degilsin\n')
            return
        import chr
        m = 1 if str(mode) in ('1', 'on', 'acik', 'bin') else 0
        try:
            chr.SelectInstance(_my_vid())
        except:
            pass
        if m:
            chr.MountHorse(20030)
            _visual_kick(_my_vid())
            _write('fakemount', 'OK: SAHTE binis (at ustunde gorunursun; sunucu BILMEZ)\nskill serbest, hasar binmemis halde - istedigini yap\ninmek: fakemount 0 | gercek binis: chat /ride')
        else:
            chr.DismountHorse()
            _visual_kick(_my_vid())
            _write('fakemount', 'OK: sahte inis')
    except Exception, e:
        _write('fakemount', 'HATA ' + _fmt_error(e) + '\n(Bu istemcide chr.MountHorse yok olabilir - help: chat /ride)')

ridefake = fakemount   # kisaltma

# (v4.7) speed KALDIRILDI - sunucu chr.SetMoveSpeed tanimiyor
# (saha testi 12: "speed ve aspeed calismiyor" - kullanici istegiyle silindi)


# (v4.7) aspeed KALDIRILDI - ayni neden


def statup(part, count=1):
    """stat PUANI ver (KANIT: uiCharacter.py:72-76 statusPlusCommandDict:
    HTH='/stat ht', INT='/stat iq', STR='/stat st', DEX='/stat dx').
    orn: statup st 10  (10 puan VIT'e) | kontrol: stat yaz"""
    try:
        if not _ingame():
            _write('statup', 'HATA: oyunda degilsin\n')
            return
        import net
        p = str(part).strip().lower()
        alias = {'ht': 'ht', 'vit': 'ht', 'con': 'ht',
                 'iq': 'iq', 'int': 'iq',
                 'st': 'st', 'str': 'st',
                 'dx': 'dx', 'dex': 'dx'}
        if p not in alias:
            _write('statup', 'HATA: part ht|i|st|dx olmali (orn: statup st 10)\nht=vucut iq=zeka st=guc dx=ceviklik')
            return
        p = alias[p]
        n = int(count)
        if n < 1: n = 1
        if n > 200: n = 200
        ok = 0
        for i in range(n):
            try:
                net.SendChatPacket('/stat ' + p)
                ok += 1
            except:
                break
        _write('statup', 'OK: %d x /stat %s gonderildi\nkontrol: stat yaz (kalan puan orada)' % (ok, p))
    except Exception, e:
        _write('statup', 'HATA ' + _fmt_error(e) + '\n')

def skillup(idx, count=1):
    """skill PUANI ver (KANIT: uiCharacter.py:947
    net.SendChatPacket('/skillup ' + str(skillIndex))).
    idx = skill raporundaki index (skill yaz). orn: skillup 3 10"""
    try:
        if not _ingame():
            _write('skillup', 'HATA: oyunda degilsin\n')
            return
        import net
        si = int(idx)
        n = int(count)
        if n < 1: n = 1
        if n > 100: n = 100
        ok = 0
        for i in range(n):
            try:
                net.SendChatPacket('/skillup ' + str(si))
                ok += 1
            except:
                break
        _write('skillup', 'OK: %d x /skillup %s gonderildi\nkontrol: skill yaz' % (ok, si))
    except Exception, e:
        _write('skillup', 'HATA ' + _fmt_error(e) + '\n')

# --- ANTIFLY (sekme/ucus engeli) -------------------------------------------
# KANIT (kullanici dump): AntiFly.py + antifly_sekmeme_.py - BlockFly:
#   chr.SetLoopMotion(chr.MOTION_WAIT) + player.SetAttackKeyState(TRUE)
# WAIT animasyonu ucus/sekme hareketini ezer; saldiri basiliyken sunucu
# itme uygulamaz. EK yontem (kullanici onerisi): chrmgr.SetAffect ile efekt
# eklemek -> antiflyeffect.
_ANTIFLY = {'win': None, 'mode': 0, 't0': 0.0}

class _AntiFlyWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            import time, chr, player
            st = _ANTIFLY
            if st['mode'] == 0:
                return
            now = time.time()
            if now - st['t0'] < 0.35:
                return
            st['t0'] = now
            me = _my_vid()
            try:
                chr.SelectInstance(me)
            except:
                pass
            try:
                chr.SetLoopMotion(chr.MOTION_WAIT)
            except:
                pass
            # v4.6: mod 2 = + Guclu Beden (zihinsel savasci) efezgi - devrilmeme
            if st['mode'] == 2:
                try:
                    import chrmgr
                    chrmgr.SetAffect(me, chr.AFFECT_CHEONGEUN, 1)
                except:
                    pass
            # v4.6: saldiri tusu SADECE mod 3'te (orijinal AntiFly.py) -
            # kullanici istegi: saldirmadan da devrilmemek istiyor
            if st['mode'] == 3:
                try:
                    player.SetAttackKeyState(1)
                except:
                    pass
        except:
            pass

def _antifly_stop():
    try:
        import player
        player.SetAttackKeyState(0)
    except:
        pass
    try:
        if _ANTIFLY['win'] is not None:
            _ANTIFLY['win'].Hide()
            _ANTIFLY['win'].Destroy()
    except:
        pass
    _ANTIFLY['win'] = None
    _ANTIFLY['mode'] = 0

def antifly(mode):
    """ANTIFLY / DEVRILME ENGELI - v4.6 mod seti (saldıri tusu artik
    varsayilan DEGIL - kullanici istegi):
    antifly 1 = animasyon kilidi (WAIT - sekme/ucus animasyonunu ezer)
    antifly 2 = animasyon kilidi + GUCLU BEDEN efezgi (zihinsel savasci
                skilinin devrilmeme etkisi: chr.AFFECT_CHEONGEON -
                'birine daldiginda devrilmeme' icin)
    antifly 3 = ORIJINAL AntiFly.py (WAIT + saldiri tusu basili - botun
                tam yontemi; otomatik vurur!)
    antifly 0 = kapat (saldiri tusunu da birakir)"""
    try:
        if not _ingame():
            _write('antifly', 'HATA: oyunda degilsin\n')
            return
        m = int(mode)
        if m == 0:
            _antifly_stop()
            _write('antifly', 'OK: antifly KAPALI (saldiri tusu birakildi, efezgi temizlendi)')
            return
        if m not in (1, 2, 3):
            m = 1   # v4.6: bilinmeyen mod -> 1 (SALDIRISIZ; eskiden 1'e
                    # zorlaniyordu ve saldirili mod saniliyordu!)
        _ANTIFLY['mode'] = m
        if _ANTIFLY['win'] is None:
            _ANTIFLY['win'] = _AntiFlyWnd()
        _ANTIFLY['t0'] = 0.0
        dsc = {1: 'animasyon kilidi (saldirmaz)', 2: 'animasyon + GUCLU BEDEN efezgi (cheongeun)',
               3: 'ORIJINAL: animasyon + SALDIRI BASILI (otomatik vurur!)'}
        _write('antifly', 'OK: antifly mod %d = %s\n0=kapat | 1=kilit | 2=kilit+efeekt(Guclu Beden) | 3=orijinal(saldirili)' % (m, dsc.get(m, '?')))
    except Exception, e:
        _write('antifly', 'HATA ' + _fmt_error(e) + '\n')

def antiflyeffect(eft=1):
    """karaktere EFEKT/AFEKKT ekle (chrmgr.SetAffect(vid, efekt, 1) - mypy.py
    kaniti). v4.6: isim de kabul eder:
      antiflyeffect cheongeun -> GUCLU BEDEN (zihinsel savasci devrilmeme!)
      antiflyeffect stun / slow / poison -> o efezgi ekler (test icin)
      antiflyeffect <sayi> -> do\xfdvan sayi. Kalici degil (warp temizler)."""
    try:
        if not _ingame():
            _write('antiflyeffect', 'HATA: oyunda degilsin\n')
            return
        import chrmgr, chr
        me = _my_vid()
        ad = {'cheongeun': 'AFFECT_CHEONGEUN', 'guclu': 'AFFECT_CHEONGEUN',
              'guclubeden': 'AFFECT_CHEONGEUN', 'geomgyeong': 'AFFECT_GEOMGYEONG',
              'stun': 'AFFECT_STUN', 'slow': 'AFFECT_SLOW',
              'poison': 'AFFECT_POISON', 'kwaesok': 'AFFECT_KWAESOK'}
        k = str(eft).strip().lower()
        if k in ad:
            aid = int(getattr(chr, ad[k]))
            nm = ad[k]
        else:
            aid = int(eft); nm = 'efekt #%d' % aid
        chrmgr.SetAffect(me, aid, 1)
        _write('antiflyeffect', 'OK: %s (id=%d) eklendi -> vid=%d\nkalici degildir (harita gecisi temizler) | kalici dongu: antifly 2' % (nm, aid, me))
    except Exception, e:
        _write('antiflyeffect', 'HATA ' + _fmt_error(e) + '\n')

# --- ESYA KESIF + EFSUN ----------------------------------------------------
def itemfind(kelime):
    """ISIMLE esya ara (kullanici: 'simyayi bulamadim', 'erkek ninja kostum
    seti', '5. efsun ekleme kuresi'...). 1..99999 canli tarama.
    orn: itemfind simya | itemfind kostum | itemfind efsun | itemfind ejder"""
    try:
        if not _ingame():
            _write('itemfind', 'HATA: oyunda degilsin\n')
            return
        import item
        key = str(kelime).strip().lower()
        if not key:
            _write('itemfind', 'HATA: kelime gerekli (orn: itemfind simya)')
            return
        found = []
        for a in range(1, 100000, 50000):
            b = min(a + 49999, 99999)
            for v in xrange(a, b + 1):
                try:
                    item.SelectItem(v)
                    nm = str(item.GetItemName())
                except:
                    continue
                if nm and key in nm.lower():
                    try:
                        tp = int(item.GetItemType())
                    except:
                        tp = -1
                    found.append((v, nm, tp))
        path = r'C:\MaxExec\itemscan_find.txt'
        try:
            f = open(path, 'w')
            f.write('itemfind \"%s\": %d esya\n' % (key, len(found)))
            for v, nm, tp in found:
                f.write('vnum=%-7d tip=%-2d %s | /i %d | iteminfo %d\n' % (v, tp, nm, v, v))
            f.close()
        except:
            pass
        L = ['itemfind \"%s\": %d esya bulundu' % (key, len(found))]
        for v, nm, tp in found[:80]:
            L.append('  vnum=%-7d tip=%-2d %s | /i %d | iteminfo %d' % (v, tp, nm, v, v))
        if len(found) > 80:
            L.append('  ... +%d daha -> TAM LISTE: %s' % (len(found) - 80, path))
        if not found:
            L.append('IPUCU: baska kelime dene (itemfind tas, itemfind ejder, itemfind kuresi...)')
        _write('itemfind', '\n'.join(L) + '\n')
    except Exception, e:
        _write('itemfind', 'HATA ' + _fmt_error(e) + '\n')

def iteminfo(vnum):
    """esyannin TAM proto bilgisi (kanit: efsunbotu.py item.GetAffect/GetValue/
    GetLimit kullanimi): ad/tip/boyut/degerler/proto-efsunlar/limitler.
    Kostum ve simya tasi tiplerini ayirt etmek icin."""
    try:
        if not _ingame():
            _write('iteminfo', 'HATA: oyunda degilsin\n')
            return
        import item
        v = int(vnum)
        item.SelectItem(v)
        L = ['iteminfo vnum=%d' % v]
        try:
            L.append('ad: %s' % str(item.GetItemName()))
        except:
            pass
        try:
            L.append('aciklama: %s' % str(item.GetItemDescription()))
        except:
            pass
        try:
            L.append('ozet: %s' % str(item.GetItemSummary()))
        except:
            pass
        try:
            L.append('tip=%d alt-tip=%d boyut=%d' % (int(item.GetItemType()), int(item.GetItemSubType()), int(item.GetItemSize())))
        except:
            pass
        for i in range(6):
            try:
                val = int(item.GetValue(i))
                if val != 0:
                    L.append('  deger%d=%d' % (i, val))
            except:
                break
        for i in range(7):
            try:
                ap = item.GetAffect(i)
                tv = int(ap[0]); vv = int(ap[1])
                if tv != 0:
                    L.append('  proto-efsun%d: apply=%d deger=%d (%s +%s)' % (i, tv, vv, APPLY_NAMES.get(tv, '?'), vv))
            except:
                break
        for i in range(3):
            try:
                lm = item.GetLimit(i)
                if int(lm[0]) != 0:
                    L.append('  limit%d: tip=%d deger=%s' % (i, int(lm[0]), str(lm[1])))
            except:
                break
        fl = []
        for i in range(20):
            try:
                if item.IsFlag(1 << i):
                    fl.append(str(1 << i))
            except:
                break
        if fl:
            L.append('  flaglar: %s' % ','.join(fl))
        _write('iteminfo', '\n'.join(L) + '\n')
    except Exception, e:
        _write('iteminfo', 'HATA ' + _fmt_error(e) + '\n')

def attr(slot):
    """esyannin EFSUNLARINI oku (kullanici: 'efsunlu mu efsunsuz mu efsunlari
    ne?'). KANIT: efsunbotu.py player.GetItemAttribute(slot, i).
    slot: envanter 0..89, ekipman 90+ (equip raporundaki numaralar).
    ayrica: attrall = tum ekipmanin efsunlari"""
    try:
        if not _ingame():
            _write('attr', 'HATA: oyunda degilsin\n')
            return
        import player, item
        s = int(slot)
        v = 0
        try:
            v = int(player.GetItemIndex(s))
        except:
            pass
        if v <= 0:
            _write('attr', 'HATA: slot %d bos (slot listesi: inv / equip yaz)' % s)
            return
        try:
            item.SelectItem(v)
            nm = str(item.GetItemName())
            tp = int(item.GetItemType())
            stp = int(item.GetItemSubType())
        except:
            nm = '?'; tp = -1; stp = -1
        L = ['slot %d: vnum=%d %s (tip=%d alt=%d)' % (s, v, nm, tp, stp)]
        n = 0
        for i in range(7):
            try:
                a = player.GetItemAttribute(s, i)
                tv = int(a[0]); vv = int(a[1])
            except:
                break
            if tv == 0:
                continue
            n += 1
            if i < 5:
                L.append('  efsun %d/5:  apply=%-3d deger=%-5d (%s +%s)' % (i + 1, tv, vv, APPLY_NAMES.get(tv, '?'), vv))
            else:
                L.append('  BONUS %d/7 (6./7. efsun): apply=%-3d deger=%-5d (%s +%s)' % (i + 1, tv, vv, APPLY_NAMES.get(tv, '?'), vv))
        if n == 0:
            L.append('  (efsun YOK - efsunsuz esya)')
        sok = []
        for i in range(4):
            try:
                sv = int(player.GetItemMetinSocket(s, i))
                if sv > 0:
                    sok.append('%d' % sv)
            except:
                break
        if sok:
            L.append('  soketler: %s' % ', '.join(sok))
        L.append('---')
        L.append('v4.6: efsun 1-5 = normal | BONUS = 6./7. (rare) efsun (efsunbotu.py index kaniti)')
        L.append('efsun degistirme: useon <kagit-slot> %d (kagit: itemfind efsun) | efsunsw %d' % (s, s))
        _write('attr', '\n'.join(L) + '\n')
    except Exception, e:
        _write('attr', 'HATA ' + _fmt_error(e) + '\n')

def attrall():
    """TUM ekipmanin efsunlarini tek raporda doker (attr <slot> kisayolu)"""
    try:
        if not _ingame():
            _write('attrall', 'HATA: oyunda degilsin\n')
            return
        import player, item
        try:
            eb = _eq_base()
        except:
            eb = 90
        L = ['EKIPMAN EFSUN RAPORU']
        for off in range(12):
            s = eb + off
            try:
                v = int(player.GetItemIndex(s))
            except:
                continue
            if v <= 0:
                continue
            try:
                item.SelectItem(v)
                nm = str(item.GetItemName())
            except:
                nm = '?'
            parts = []
            for i in range(7):
                try:
                    a = player.GetItemAttribute(s, i)
                    tv = int(a[0]); vv = int(a[1])
                except:
                    break
                if tv != 0:
                    parts.append('%s +%s' % (APPLY_NAMES.get(tv, 'apply%d' % tv), vv))
            L.append('  slot %d vnum=%-7d %s | %s' % (s, v, nm, ', '.join(parts) if parts else 'efsun yok'))
        _write('attrall', '\n'.join(L) + '\n')
    except Exception, e:
        _write('attrall', 'HATA ' + _fmt_error(e) + '\n')

def useon(src, dst):
    """esyayi DIGER ESYANIN UZERINDE kullan (efsun ekleme/degistirme/
    5. efsun kuresi/kostum efsunu hepsi bu paketle!). KANIT: efsunbotu.py
    net.SendItemUseToItemPacket(i, self.index).
    useon <kagit-slotu> <hedef-esya-slotu> - hedef ekipman slotu da olur (90+)"""
    try:
        if not _ingame():
            _write('useon', 'HATA: oyunda degilsin\n')
            return
        import net
        s = int(src); d = int(dst)
        net.SendItemUseToItemPacket(s, d)
        _write('useon', 'OK: SendItemUseToItemPacket(src=%d, dst=%d) gonderildi\nsrc=kullanilan esya (efsun kagidi/kuresi) | dst=hedef esya\nsonuc: envanteri acip esyanin uzerine gel (efsunlar degisti mi)' % (s, d))
    except Exception, e:
        _write('useon', 'HATA ' + _fmt_error(e) + '\n')

EFSUN_SWITCH_VNUMS = (71084, 71051, 70063, 71052)

def efsunsw(dst):
    """envanterdeki EFSUN-DEGISTIRME kagidini otomatik bulup hedef esyaya
    kullanir (kullanici: 'efsun degistirme'). efsunsw <hedef-esya-slotu>
    kagit bulunamazsa: itemfind efsun ile kendi serverinin kagidini bul,
    sonra useon <kagit-slot> <esya-slot>"""
    try:
        if not _ingame():
            _write('efsunsw', 'HATA: oyunda degilsin\n')
            return
        import player
        d = int(dst)
        try:
            total = int(player.INVENTORY_SLOT_COUNT)
        except:
            total = 90
        for s in range(total):
            try:
                v = int(player.GetItemIndex(s))
            except:
                continue
            if v in EFSUN_SWITCH_VNUMS:
                useon(s, d)
                return
        _write('efsunsw', 'HATA: efsun kagidi envanterde yok (aranan vnumlar: %s)\ncozum: itemfind efsun (serverin kagidini bul) -> useon <kagit-slot> %d' % (str(EFSUN_SWITCH_VNUMS), d))
    except Exception, e:
        _write('efsunsw', 'HATA ' + _fmt_error(e) + '\n')


# ===========================================================================
# v4.6 YENI KOMUTLAR (saha testi 12 dev raporu)
# ===========================================================================

# --- WARP: LEGENDY YOLU (v4.7 - sahne YENIDEN yuklenir) --------------------
# KANIT: LegendySF-V2 consolemodule.py:409 'warp' console komutu:
#     background.Destroy(); background.Initialize()
#     background.WarpTest(iWarpX, iWarpY)
#     background.RegisterEnvironmentData(0, "d:/ymir work/environment/b3.msenv")
#     background.SetEnvironmentData(0); background.SetShadowLevel(SHADOW_ALL)
# C++ taraf: WarpTest(x,y) -> CPythonBackground::Warp(x*100, y*100) ->
# GlobalPositionToMapInfo -> LoadMap(harita, yerel)  = SAHNE YUKLENIR.
# Bu istemcinin background modulunde WarpTest VAR (canli katalog kaniti).
# Kullanici tarifi: "net.directenter gibi calisir - sahne yuklenir oyun
# yeniden yuklenir". x,y = GLOBAL koordinat (pixel/100; pos degeri /100).
def warp(x, y):
    """ISINLANMA v4.7 - LEGENDY YOLU (sahne yeniden yukleme):
    warp <x> <y>   x,y = GLOBAL koordinat = pos raporunun /100'u
                   (orn pos 38421 39017 -> warp 384 390; buyuk yazarsan
                   otomatik /100 yapilir). Harita siniri YOK - atlas
                   koordinatiyla diger haritaya da gecer.
    Akis: background.Destroy + Initialize + WarpTest (SAHNE YENIDEN
    YUKLENIR - net.directenter tarzi) -> cevre/golge kur -> karakteri
    hedefe yerlestir (SetPixelPosition) -> konum paketi (senkron).
    kontrol: pos"""
    try:
        if not _ingame():
            _write('warp', 'HATA: oyunda degilsin\n')
            return
        import background, chr
        xi = int(x); yi = int(y)
        # buyuk deger = pixel koordinat -> global birim (pixel/100)
        if xi > 4095 or yi > 4095:
            xi = xi / 100; yi = yi / 100
        _live('WARP: (%d,%d) global - sahne yeniden yukleniyor (Legendy yolu)' % (xi, yi))
        try:
            background.Destroy()
            background.Initialize()
            background.WarpTest(xi, yi)
        except Exception, e1:
            _write('warp', 'HATA WarpTest: ' + _fmt_error(e1) +
                   '\n(bu istemcide background.WarpTest olmayabilir - kontrol: pyfiles)\n')
            return
        try:
            background.RegisterEnvironmentData(0, 'd:/ymir work/environment/b3.msenv')
        except:
            pass
        try:
            background.SetEnvironmentData(0)
        except:
            pass
        try:
            background.SetShadowLevel(background.SHADOW_ALL)
        except:
            pass
        # karakteri yeni haritada hedef noktaya yerlestir (global -> yerel)
        lx = xi * 100; ly = yi * 100
        try:
            lp = background.GlobalPositionToLocalPosition(xi * 100, yi * 100)
            lx = int(lp[0]); ly = int(lp[1])
        except:
            pass
        try:
            vid = _my_vid()
            chr.SelectInstance(vid)
            chr.SetPixelPosition(lx, ly)
        except:
            pass
        try:
            import net
            net.SendCharacterPositionPacket()
        except:
            pass
        mp = '?'
        try:
            mp = str(background.GetCurrentMapName())
        except:
            pass
        _write('warp', 'OK: warp (%d,%d) global - SAHNE YENIDEN YUKLENDI (Legendy yolu)\nharita=%s  yerel konum=(%d,%d)\nNOT: background.WarpTest = LegendySF-V2 console warp komutunun birebiri\n(sahne yuklenir - net.directenter tarzi). Sunucu senkronu icin konum paketi\ngonderildi. Kontrol: pos yaz' % (xi, yi, mp, lx, ly))
    except Exception, e:
        _write('warp', 'HATA ' + _fmt_error(e) + '\n')

# --- ANTISTUN / ANTISLOW (efektsel cozum) ----------------------------------
# KANIT: chr modulu AFFECT_STUN/AFFECT_SLOW/AFFECT_KWAESOK sabitleri (canli
# katalog) + chrmgr.SetAffect(vid, afekt, 0/1) (mypy.py 3-arg kaniti).
# Sunucu efezgi tekrar gonderse de dongu her 0.4sn yeniden temizler.
_ANTIEFF = {'win': None, 'stun': 0, 'slow': 0, 't0': 0.0}

class _AntiEffWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        try:
            import time, chr, chrmgr
            st = _ANTIEFF
            if st['stun'] == 0 and st['slow'] == 0:
                return
            now = time.time()
            if now - st['t0'] < 0.4:
                return
            st['t0'] = now
            me = _my_vid()
            if st['stun']:
                try:
                    chrmgr.SetAffect(me, chr.AFFECT_STUN, 0)
                except:
                    pass
            if st['slow']:
                try:
                    chrmgr.SetAffect(me, chr.AFFECT_SLOW, 0)
                except:
                    pass
                try:
                    chrmgr.SetAffect(me, chr.AFFECT_KWAESOK, 0)
                except:
                    pass
        except:
            pass

def _antieff_win_stop():
    try:
        if _ANTIEFF['win'] is not None:
            _ANTIEFF['win'].Hide()
            _ANTIEFF['win'].Destroy()
    except:
        pass
    _ANTIEFF['win'] = None

def antistun(mode):
    """ANTISTUN (kullanici: 'stunlanma yasarsak aninda cozsun'): 0.4sn'lik
    dongu AFFECT_STUN'i surekli temizler -> sersemleme ani kalkar (gorsel +
    hareket kilidi acilir; sunucu tarafinin kendi suresi kisalamaz ama
    sen sersemleme animasyonunda kilitli kalmazsin). antistun 1|0"""
    try:
        if not _ingame():
            _write('antistun', 'HATA: oyunda degilsin\n')
            return
        _ANTIEFF['stun'] = 1 if int(mode) else 0
        if _ANTIEFF['stun'] or _ANTIEFF['slow']:
            if _ANTIEFF['win'] is None:
                _ANTIEFF['win'] = _AntiEffWnd()
            _ANTIEFF['t0'] = 0.0
            _write('antistun', 'OK: antistun ACIK (0.4sn dongu - AFFECT_STUN temizleme)\ntam etki icin: antislow 1 + speed <deger> ile birlikte kullan')
        else:
            if _ANTIEFF['slow'] == 0:
                _antieff_win_stop()
            _write('antistun', 'OK: antistun KAPALI')
    except Exception, e:
        _write('antistun', 'HATA ' + _fmt_error(e) + '\n')

def antislow(mode):
    """ANTISLOW (kullanici: 'anti yavaslama ekle'): 0.4sn dongu
    AFFECT_SLOW + AFFECT_KWAESOK temizler. Gerçek hareket hizi sunucuda
    yavaslamis kalabilir -> speed <deger> dongusuyle birlikte kullan
    (speed her 0.5sn hizi yeniden uygular). antislow 1|0"""
    try:
        if not _ingame():
            _write('antislow', 'HATA: oyunda degilsin\n')
            return
        _ANTIEFF['slow'] = 1 if int(mode) else 0
        if _ANTIEFF['stun'] or _ANTIEFF['slow']:
            if _ANTIEFF['win'] is None:
                _ANTIEFF['win'] = _AntiEffWnd()
            _ANTIEFF['t0'] = 0.0
            _write('antislow', 'OK: antislow ACIK (AFFECT_SLOW+KWAESOK temizleme)\nNOT: yavaslama sunucu kaynakliysa speed <gercek-hizin> dongusunu de ac')
        else:
            if _ANTIEFF['stun'] == 0:
                _antieff_win_stop()
            _write('antislow', 'OK: antislow KAPALI')
    except Exception, e:
        _write('antislow', 'HATA ' + _fmt_error(e) + '\n')

# --- COMBO (surekli vurus - 'damage animasyonu' tekniği) --------------------
def combo(m):
    """SUREKLI VURUS (kullanici tarifli: 'renderle ilgili animasyonu damage
    animasyonuyla degistirince ... surekli vurmaca'). KANIT: 123klo-multihack
    'Combo' duzmesi: chr.testSetComboType(2). combo 1..3 = combo tipi,
    combo 0 = kapat. Saldırı animasyonu kısalir/kesişir -> arka arkaya vurur."""
    try:
        if not _ingame():
            _write('combo', 'HATA: oyunda degilsin\n')
            return
        import chr
        n = int(m)
        if n < 0 or n > 3:
            n = 0
        try:
            chr.SelectInstance(_my_vid())
        except:
            pass
        chr.testSetComboType(n)
        _write('combo', 'OK: combo tipi=%d\n0=kapat | 1/2/3 dene (2 = 123klo-multihack kaniti)\nsaldiri hizi icin: aspeed <n> (dongulu)' % n)
    except Exception, e:
        _write('combo', 'HATA ' + _fmt_error(e) + '\n')

# --- STAT GERI ALMA + UI-YOLU fonksiyonlar ---------------------------------
def statdown(part, count=1):
    """stat PUANI GERI AL (v4.6, KANIT: uiCharacter.py statusMinusCommandDict:
    '/stat- ht' - oyunun kendi minus butonlari bunu yollar).
    orn: statdown st 3"""
    try:
        if not _ingame():
            _write('statdown', 'HATA: oyunda degilsin\n')
            return
        import net
        p = str(part).strip().lower()
        alias = {'ht': 'ht', 'vit': 'ht', 'con': 'ht',
                 'iq': 'iq', 'int': 'iq',
                 'st': 'st', 'str': 'st',
                 'dx': 'dx', 'dex': 'dx'}
        if p not in alias:
            _write('statdown', 'HATA: part ht|iq|st|dx olmali (orn: statdown st 3)')
            return
        p = alias[p]
        try:
            c = max(1, min(50, int(count)))
        except:
            c = 1
        for i in range(c):
            net.SendChatPacket('/stat- %s' % p)
        _write('statdown', 'OK: %d x /stat- %s gonderildi\nkontrol: stat yaz (puan geri doner - puan-geri-alma kosullari gecerliyse)' % (c, p))
    except Exception, e:
        _write('statdown', 'HATA ' + _fmt_error(e) + '\n')

def _char_wnd():
    """oyunun karakter penceresi (game.interface.wndCharacter - game.py:1065
    kaniti: 'if self.interface.wndCharacter')"""
    g = sys.modules.get('game', None)
    if g is None:
        return None
    itf = getattr(g, 'interface', None)
    if itf is None:
        return None
    return getattr(itf, 'wndCharacter', None)

def skillupui(slot):
    """SKILL Puanini OYUNUN KENDI UI FONKSIYONUyla ver (kullanici: 'farkli py
    fonksiyonu ile de olabilir'). KANIT: uiCharacter.py OnPressedSlotButton
    (karakter penceresinin + dugmesi tam bunu cagiriyor). slot = skill
    raporundaki GORUNEN slot (1..40). Not: oyunun kendisi de net.SendChatPacket
    ('/skillup N') kullanir - baska paket yok (uiCharacter.py:947 kaniti)."""
    try:
        if not _ingame():
            _write('skillupui', 'HATA: oyunda degilsin\n')
            return
        w = _char_wnd()
        if w is None:
            _write('skillupui', 'HATA: karakter penceresi yok (oyunda V ile ac sonra dene)\nyedek: skillup <idx> (chat paketi yolu)')
            return
        w.OnPressedSlotButton(int(slot))
        _write('skillupui', 'OK: OnPressedSlotButton(%d) cagrildi (oyunun + dugme fonksiyonu)\nkontrol: skill yaz' % int(slot))
    except Exception, e:
        _write('skillupui', 'HATA ' + _fmt_error(e) + '\n')

def statupui(part):
    """STAT + dugmesini OYUNUN KENDI fonksiyonuyla 'tikla' (kullanici: '/stat
    iq fonksiyonla da gonderilebilir'). KANIT: uiCharacter.py
    __OnClickStatusPlusButton(statusKey) - HTH/INT/STR/DEX anahtarlari.
    Bu da sonunda net.SendChatPacket('/stat N') yollar (oyunun kendisi boyle
    yapar) ama UI durumu da guncellenir. part: ht|iq|st|dx"""
    try:
        if not _ingame():
            _write('statupui', 'HATA: oyunda degilsin\n')
            return
        w = _char_wnd()
        if w is None:
            _write('statupui', 'HATA: karakter penceresi yok (oyunda V ile ac sonra dene)\nyedek: statup <part> (chat paketi yolu)')
            return
        p = str(part).strip().lower()
        key = {'ht': 'HTH', 'vit': 'HTH', 'con': 'HTH',
               'iq': 'INT', 'int': 'INT',
               'st': 'STR', 'str': 'STR',
               'dx': 'DEX', 'dex': 'DEX'}.get(p)
        if key is None:
            _write('statupui', 'HATA: part ht|iq|st|dx olmali')
            return
        m = getattr(w, '_CharacterWindow__OnClickStatusPlusButton', None)
        if m is not None:
            m(key)
            _write('statupui', 'OK: __OnClickStatusPlusButton(%s) cagrildi (oyunun + dugme fonksiyonu)\nkontrol: stat yaz' % key)
        else:
            bd = getattr(w, 'statusPlusButtonDict', None)
            if bd and key in bd:
                bd[key].CallEvent()
                _write('statupui', 'OK: %s + dugmesi CallEvent ile tiklandi\nkontrol: stat yaz' % key)
            else:
                _write('statupui', 'HATA: stat dugmesi bulunamadi - yedek: statup %s' % p)
    except Exception, e:
        _write('statupui', 'HATA ' + _fmt_error(e) + '\n')

# --- EFSUN okuma (attr'nin kullanici-dostu yeni adi) ------------------------
def efsun(slot='all'):
    """envanter/ekipman esyasininin BONUS EFSUNLARINI oku (kullanici: 'asil
    bize bonus efsunu lazim envanterdeki itemin'). efsun <slot> (envanter
    0..89 / ekipman 90+) | efsun all (ekipman + envanterdeki TUM efsunlular)
    KANIT: player.GetItemAttribute(slot, i) (efsunbotu.py: 0-4 normal,
    5-6 = 6./7. BONUS)."""
    try:
        k = str(slot).strip().lower()
        if k in ('all', 'hepsi', ''):
            efsun_all()
            return
        attr(slot)
    except Exception, e:
        _write('efsun', 'HATA ' + _fmt_error(e) + '\n')

def efsun_all():
    """ekipman + envanterdeki EFSUNLU esyalarin tam bonus raporu"""
    try:
        if not _ingame():
            _write('efsun', 'HATA: oyunda degilsin\n')
            return
        import player, item
        try:
            total = int(player.INVENTORY_SLOT_COUNT)
        except:
            total = 90
        try:
            eb = _eq_base()
        except:
            eb = 90
        L = ['BONUS EFSUN RAPORU (envanter + ekipman) - v4.6']
        nl = []
        for s in range(total):
            try:
                v = int(player.GetItemIndex(s))
            except:
                continue
            if v <= 0:
                continue
            parts = []
            for i in range(7):
                try:
                    a = player.GetItemAttribute(s, i)
                    tv = int(a[0]); vv = int(a[1])
                except:
                    break
                if tv != 0:
                    if i < 5:
                        parts.append('%s +%s' % (APPLY_NAMES.get(tv, 'apply%d' % tv), vv))
                    else:
                        parts.append('[B%d] %s +%s' % (i + 1, APPLY_NAMES.get(tv, 'apply%d' % tv), vv))
            if parts:
                try:
                    item.SelectItem(v)
                    nm = str(item.GetItemName())
                except:
                    nm = '?'
                nl.append('  [ENV] slot %-3d vnum=%-7d %s | %s' % (s, v, nm, ', '.join(parts)))
        ne = []
        for off in range(12):
            s = eb + off
            try:
                v = int(player.GetItemIndex(s))
            except:
                continue
            if v <= 0:
                continue
            parts = []
            for i in range(7):
                try:
                    a = player.GetItemAttribute(s, i)
                    tv = int(a[0]); vv = int(a[1])
                except:
                    break
                if tv != 0:
                    if i < 5:
                        parts.append('%s +%s' % (APPLY_NAMES.get(tv, 'apply%d' % tv), vv))
                    else:
                        parts.append('[B%d] %s +%s' % (i + 1, APPLY_NAMES.get(tv, 'apply%d' % tv), vv))
            if parts:
                try:
                    item.SelectItem(v)
                    nm = str(item.GetItemName())
                except:
                    nm = '?'
                ne.append('  [EKIP] slot %-3d vnum=%-7d %s | %s' % (s, v, nm, ', '.join(parts)))
        L.extend(ne)
        L.extend(nl)
        if not ne and not nl:
            L.append('  (hiç efsunlu esya yok - efsunsuz envanter)')
        L.append('---')
        L.append('[B6]/[B7] = 6./7. BONUS efsun (rare) | tek esya: efsun <slot> | degistir: efsunsw <slot>')
        _write('efsun', chr(10).join(L) + chr(10))
    except Exception, e:
        _write('efsun', 'HATA ' + _fmt_error(e) + '\n')


# ===========================================================================
# v4.7 ENVANTER YONETIMI (kullanici istegi - saha testi 13):
#   slots              -> kac sekme/slot, doluluk %, kalan bos slot
#   selljunk           -> cop esyalari yakindaki NPC dukkanina sat
#                         (SADECE cop listesindekiler; EFSUNLU ASLA satilmaz)
#   selljunk add/del/list/name -> cop listesini yonet (junklist.txt)
#   sellall [force]    -> envanterin TAMAMINI sat (efsunlular yine atlanir;
#                         'force' ile efsunlular dahil - DIKKAT!)
#   dropall            -> envanterin tamamini YERE AT (tek tek - bazi
#                         sunucular toplu atmayi reddeder)
# KANITLAR: m2k Inventorymanager.py (shop.IsOpen + net.SendShopSellPacket,
#   xrange(0,90) + net.SendItemDropPacket) + uiShop.py:231
#   (net.SendShopSellPacketNew(slotPos, count)) + interfacemodule.py:720
#   OpenShopDialog(vid) + ItemUse.py net.SendOnClickPacket(vid) kanitlari.
# ===========================================================================
JUNK_PATH = r'C:\MaxExec\junklist.txt'
_JUNK = {'vnums': None, 'names': []}

def _junk_defaults():
    """cop varsayilani: baliklar (FISH_LIVE/FISH_DEAD kopyasi - literal,
    siralama bagimliligi olmasin diye burada yazili)."""
    vs = []
    for v in range(27803, 27824):
        vs.append(v)            # canli baliklar
    vs.append(27987)
    for v in range(27833, 27854):
        vs.append(v)            # olu balik iskeletleri
    vs.append(27802)            # kucuk balik (yemluk)
    return vs

def _junk_load():
    if _JUNK['vnums'] is not None:
        return _JUNK['vnums']
    vs = _junk_defaults()
    try:
        f = open(JUNK_PATH, 'r')
        for ln in f.readlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            if ln.lower().startswith('v '):
                try:
                    vs.append(int(ln[2:].strip()))
                except:
                    pass
            elif ln.lower().startswith('n '):
                _JUNK['names'].append(ln[2:].strip().lower())
        f.close()
    except:
        pass
    _JUNK['vnums'] = vs
    return vs

def _junk_save():
    try:
        f = open(JUNK_PATH, 'w')
        f.write('# PLUSMAXGOD cop-esya listesi (selljunk bunlari satar)\n')
        f.write('# v <vnum>   -> vnum ekle\n')
        f.write('# n <isim>   -> isim icerek esya ekle (kucuk harf)\n')
        defs = _junk_defaults()
        for v in _junk_load():
            if v not in defs:
                f.write('v %d\n' % v)
        for nm in _JUNK['names']:
            f.write('n %s\n' % nm)
        f.close()
    except:
        pass

def _is_junk(vnum):
    vnum = int(vnum)
    if vnum in _junk_load():
        return True
    if _JUNK['names']:
        nm = _item_name(vnum).lower()
        for pat in _JUNK['names']:
            if pat and pat in nm:
                return True
    return False

def _has_efsun(slot):
    """slottaki esya EFSUN (bonus) tasiyor mu? (efsunbotu.py kaniti:
    GetItemAttribute index 0-4 normal + 5-6 BONUS). SATMA/ATMA guvenligi."""
    import player
    for i in range(7):
        try:
            a = player.GetItemAttribute(slot, i)
            if a and int(a[0]) != 0:
                return True
        except:
            return False
    return False

# ---------------------------------------------------------------------------
# v5.0 COK-HUCRELI ESYA BOYUTU (saha testi 16: 'bazi itemler 3 slot bazi
# 2 slot yer kapliyor, ilk envanterde 32 bos yer var'). KANIT: item.SelectItem(vnum) + item.GetItemSize()
# -> (w, h) - swich.py:905, EQChanger.py:99, pasha37:2238, efsunbotu.py:793,
# edithack.py:754, itemcreator.py:322 (6 NightTown dosyasi). Izgara 5 sutun
# x 9 satir, slot = satir*5 + sutun (edithack 'slot-5' kontrolu: yuksekligi
# >=2 olan esya 5 slot alttaki hucreyi kapatir -> dikey adim +5, yatay +1).
# ---------------------------------------------------------------------------
_ITEM_SIZE_CACHE = {}

def _item_size(vnum):
    """vnum -> (w, h) hucre boyutu. Okunamazsa (1, 1) - guvenli taraf:
    boyutu bilinmeyen esya tek hucre sayilir (asiri sayim yapilmaz)."""
    try:
        vnum = int(vnum)
    except:
        return 1, 1
    if vnum <= 0:
        return 1, 1
    r = _ITEM_SIZE_CACHE.get(vnum)
    if r is not None:
        return r
    r = (1, 1)
    try:
        import item
        item.SelectItem(vnum)
        sz = item.GetItemSize()
        w = int(sz[0])
        h = int(sz[1])
        if w < 1 or h < 1:
            w = 1
            h = 1
        if w > 5:
            w = 5
        if h > 9:
            h = 9
        r = (w, h)
    except:
        r = (1, 1)
    _ITEM_SIZE_CACHE[vnum] = r
    return r

def _item_cells(slot, vnum, page_base, page_size):
    """slottaki esyanin KAPLADIGI tum hucreler (slot dahil). 5 sutunlu
    izgarada satir=(slot-base)//5, sutun=(slot-base)%5; hucre(r,c) =
    base + r*5 + c. Sayfa tasmasi kirpilir (bozuk veri guvenligi)."""
    w, h = _item_size(vnum)
    if w == 1 and h == 1:
        return [slot]
    try:
        base = int(page_base)
        ps = int(page_size)
    except:
        return [slot]
    rows = ps // 5
    if rows < 1:
        return [slot]
    off = slot - base
    if off < 0:
        return [slot]
    r0 = off // 5
    c0 = off % 5
    out = []
    for dr in range(h):
        rr = r0 + dr
        if rr < 0 or rr >= rows:
            continue
        for dc in range(w):
            cc = c0 + dc
            if cc < 0 or cc >= 5:
                continue
            out.append(base + rr * 5 + cc)
    return out

def slots():
    """ENVANTER OZETI (v5.0 - saha testi 16 COK-HUCRELI ESYA):
    bazi esyalar 2-3 hucre kaplar (kilic 1x3, zirh 2x3...). v4.9 her esyayi
    1 slot saniyordu -> oyun 32 bos gosterirken biz 34 diyorduk. Simdi
    item.GetItemSize ile (w,h) okunup KAPLANAN HUCRE sayiliyor - oyunun
    gostergesiyle AYNI sonuc. Harita 5 slot/satir (oyunun 5x9 izgarasi):
    #=esya-basi  o=esya-devami (cok-hucreli)  .=bos  E=efsunlu  ?=hata."""
    try:
        if not _ingame():
            _write('slots', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player
        try:
            pc = int(player.INVENTORY_PAGE_COUNT)
        except:
            pc = 2
        try:
            ps = int(player.INVENTORY_PAGE_SIZE)
        except:
            ps = 45
        if pc < 1: pc = 2
        if ps < 1: ps = 45
        tot = pc * ps
        try:
            cnt_all = int(player.INVENTORY_SLOT_COUNT)
        except:
            cnt_all = tot
        L = ['ENVANTER DURUMU (v5.0 - cok-hucreli esya sayilir)']
        yang = -1
        try:
            yang = int(player.GetElk())
        except:
            try:
                yang = int(player.GetGold())
            except:
                yang = -1
        if yang >= 0:
            L.append('yang: %d' % yang)
        L.append('sekmeler: %d x %d slot = TOPLAM %d slot (5 sutun x %d satir/sekme)' % (pc, ps, tot, ps / 5))
        if cnt_all != tot:
            L.append('(client INVENTORY_SLOT_COUNT=%d - kostuem/kemer alani dahil olabilir)' % cnt_all)
        full = 0        # kaplanan HUCRE (oyun gostergesiyle ayni)
        nitems = 0      # esya sayisi
        efs = 0
        errs = 0
        for pg in range(pc):
            base = pg * ps
            top = base + ps
            grid = []
            pg_items = 0
            pg_efs = 0
            multi = []
            for s in range(base, top):
                try:
                    v = int(player.GetItemIndex(s))
                except:
                    v = -1
                    errs += 1
                if v < 0:
                    grid.append('?')
                    continue
                if v == 0:
                    grid.append('.')
                    continue
                pg_items += 1
                w, h = _item_size(v)
                try:
                    e = _has_efsun(s)
                except:
                    e = False
                if e:
                    pg_efs += 1
                grid.append('E' if e else '#')
                if w > 1 or h > 1:
                    multi.append((s, _item_name(v), w, h, v))
            # 2. GECIS: cok-hucreli esya govde hucreleri 'o' (grid artik tam)
            for s2, nm2, w2, h2, v2 in multi:
                for c2 in _item_cells(s2, v2, base, ps):
                    j = c2 - base
                    if 0 <= j < ps and grid[j] == '.':
                        grid[j] = 'o'
            dolu = 0
            for ch in grid:
                if ch != '.' and ch != '?':
                    dolu += 1
            full += dolu
            nitems += pg_items
            efs += pg_efs
            kalan = ps - dolu
            pct = (100 * dolu) / ps
            tag = '  <-- DOLU!' if kalan == 0 else ''
            L.append('  sekme %d: slot %d..%d  esya=%d  kaplanan=%d hucre  bos=%d hucre  %%%d  efsunlu=%d%s' % (pg, base, top - 1, pg_items, dolu, kalan, pct, pg_efs, tag))
            # v5.0: 5 slot/satir haritasi - oyunun 5x9 izgarasiyla ayni yonelis
            i = 0
            while i < len(grid):
                L.append('    ' + ' '.join(grid[i:i + 5]) + '   (slot %d..%d)' % (base + i, base + i + len(grid[i:i + 5]) - 1))
                i += 5
            if multi:
                mm = ['    cok-hucreli esya:']
                for s2, nm2, w2, h2, v2 in multi[:8]:
                    mm.append('[%d] %s (%dx%d)' % (s2, nm2, w2, h2))
                L.append(' '.join(mm))
                if len(multi) > 8:
                    L.append('    ... + %d tane daha (detay: inv %d)' % (len(multi) - 8, pg))
        # v4.8: 90 ustu alanlarda esya var mi (kostuem/kemer/ds)?
        if cnt_all > tot:
            extra = 0
            for s in range(tot, cnt_all):
                try:
                    if int(player.GetItemIndex(s)) > 0:
                        extra += 1
                except:
                    pass
            if extra:
                L.append('diger alanlar (slot %d..%d): %d esya (kostuem/kemer alani)' % (tot, cnt_all - 1, extra))
        pct = (100 * full) / tot if tot > 0 else 0
        L.append('---')
        L.append('TOPLAM: %d esya / %d hucre DOLU  (%%%d)  BOS KALAN: %d hucre  efsunlu: %d' % (nitems, full, pct, tot - full, efs))
        if errs:
            L.append('UYARI: %d slot OKUNAMADI (?) - sayim hatali olabilir' % errs)
        if tot - full == 0:
            L.append('!! ENVANTER TAMAMEN DOLU - cop sat: selljunk | hepsi: sellall')
        L.append('harita: #=esya-basi  o=esya-devami(cok-hucreli)  .=bos  E=efsunlu  ?=okuma-hatasi')
        L.append('cok-hucreli = 2+ hucre kaplayan esya (kilic 1x3, zirh 2x3) - oyunla AYNI sayim')
        L.append('detay: inv <sekme> | efsunlar: efsun all | cop sat: selljunk | hepsi: sellall | yere at: dropall')
        _write('slots', '\n'.join(L) + '\n')
    except Exception, e:
        _write('slots', 'HATA ' + _fmt_error(e) + '\n')

def _shop_npc_near(maxdist=3500):
    """yakindaki dukkan acilabilir NPC (instance tip=1) vid'si; yoksa 0.
    Kanit: ItemUse.py:553 net.SendOnClickPacket(vid) + near taramasi."""
    try:
        import chr
        me = _my_vid()
        myp = chr.GetPixelPosition(me)
        mx, my = int(myp[0]), int(myp[1])
        best = 0
        bd = int(maxdist) * int(maxdist)
        for v, t, px, py in _near_scan_range(1, 30000):
            if v == me or t != 1:
                continue
            dx = px - mx; dy = py - my
            d2 = dx * dx + dy * dy
            if d2 < bd:
                bd = d2
                best = v
        return best
    except:
        return 0

_SELL = {'win': None, 'on': 0, 'mode': 'junk', 'force': 0, 'cur': 0,
         'pass': 0, 't0': 0.0, 'n': 0, 'skip': 0,
         'faz': 0, 't_faz': 0.0, 'clicks': 0, 'vid': 0,
         'method': 'eski-1arg', 't_log': 0.0, 'errs': 0, 'left': 0,
         # v5.0 (saha testi 16: '5 dk sonra tekrar npcye tiklayip satmaya
         # calisiyor' + 'durmalarini lazim'): KOK NEDEN - v4.9'da IsOpen
         # flicker donusunde cur SIFIRLANIYORDU -> dukkan acilinca bastan
         # basliyor -> faz2'ye ULASILMIYORDU (sonsuz faz0<->faz1). Artik:
         # cur KORUNUR + flicker sayaci + 120sn HARD DEADLINE + kara liste
         # (2 turda da duran esya bir daha denenmez) + bitince dukkan KAPANIR.
         't_start': 0.0, 'flick': 0, 'stuck': None, 'flick_arada': 0}

def _sell_wname():
    return 'sellall' if _SELL['mode'] == 'all' else 'selljunk'

def _sell_stop(msg):
    """SELL dongusunu DURDUR - selljunk 0 / sellall 0 / stop hepsi buradan."""
    st = _SELL
    st['on'] = 0
    try:
        if st['win'] is not None:
            st['win'].Hide(); st['win'].Destroy()
    except:
        pass
    st['win'] = None
    _live('SELL DURDU: ' + msg)
    _write(_sell_wname(), 'DURDU: ' + msg + '\nyeniden: selljunk (veya sellall)')

def _sell_blacklist():
    """kara liste: 2 dogrulama turunda da duran slotlar (sunucu reddi)."""
    st = _SELL
    bl = []
    for s, c in (st['stuck'] or {}).items():
        if c >= 2:
            bl.append(s)
    return bl

def _sell_is_sellable(s, v):
    """slot s (vnum v) bu modda satilabilir mi? (efsun/junk kurallari)"""
    st = _SELL
    if v <= 0:
        return False
    if _has_efsun(s) and not st['force']:
        return False
    if st['mode'] == 'junk' and not _is_junk(v):
        return False
    return True

def _sell_left_items():
    """kalan satilabilir esyalar [(slot, vnum)] - kara liste DISINDA."""
    import player
    try:
        tot = int(player.INVENTORY_PAGE_COUNT) * int(player.INVENTORY_PAGE_SIZE)
    except:
        tot = 90
    bl = _sell_blacklist()
    out = []
    for s in range(tot):
        if s in bl:
            continue
        try:
            v = int(player.GetItemIndex(s))
        except:
            v = 0
        if v > 0 and _sell_is_sellable(s, v):
            out.append((s, v))
    return out

def _sell_report_items(items):
    """kalan esyalari ISIM + BOYUT ile listele (ilk 12)."""
    L = []
    for s, v in items[:12]:
        w, h = _item_size(v)
        boy = (' (%dx%d)' % (w, h)) if (w > 1 or h > 1) else ''
        L.append('  [%d] vnum=%d %s%s' % (s, v, _item_name(v), boy))
    if len(items) > 12:
        L.append('  ... + %d tane daha (detay: inv)' % (len(items) - 12))
    return L

def _sell_close_shop():
    """v5.0: dukkani KAPAT. KANIT: net.SendShopEndPacket - ShopScanner.py:566
    (bu sunucuda calisan bot satislari bitince boyle kapatir; 'dukkan acik
    kaliyor, kapatamiyom' sikayetinin kapanisi)."""
    try:
        import net
        net.SendShopEndPacket()
        return 1
    except:
        return 0

def _sell_done(deadline=0):
    st = _SELL
    st['on'] = 0
    try:
        if st['win'] is not None:
            st['win'].Hide(); st['win'].Destroy()
    except:
        pass
    st['win'] = None
    kapat = _sell_close_shop()
    left = _sell_left_items()
    bl = _sell_blacklist()
    tag = ' (120sn sure siniri)' if deadline else ''
    if len(left) > 0 or len(bl) > 0:
        _live('SELL: BITTI%s - %d paket, KALAN %d + kara-liste %d | dukkan kapatildi=%d' % (tag, st['n'], len(left), len(bl), kapat))
        L = ['BITTI%s: satis paketi=%d  yontem=%s' % (tag, st['n'], st['method'])]
        if len(bl) > 0:
            L.append('SATILAMAYANLAR (2 turda da satilmadi - sunucu reddi, bir daha DENENMEZ):')
            blitems = []
            import player
            for s in bl:
                try:
                    v = int(player.GetItemIndex(s))
                except:
                    v = 0
                if v > 0:
                    blitems.append((s, v))
            L.extend(_sell_report_items(blitems))
        if len(left) > 0:
            L.append('hala satilabilir gorunen (%d):' % len(left))
            L.extend(_sell_report_items(left))
            L.append('(tekrar denemek icin: sellall / selljunk)')
        L.append('dukkan otomatik kapatildi (%s) - kontrol: slots' % ('OK' if kapat else 'basarisiz - ESC ile kapat'))
        _write(_sell_wname(), '\n'.join(L) + '\n')
    else:
        _live('SELL: BITTI%s - %d paket, %d atlandi (yontem=%s) | dukkan kapatildi=%d' % (tag, st['n'], st['skip'], st['method'], kapat))
        _write(_sell_wname(), 'OK: SATMA BITTI%s\nsatis paketi=%d  atlanan=%d (efsunlu/cop-olmayan)\ndukkan otomatik kapatildi (%s)\nkontrol: slots' % (tag, st['n'], st['skip'], 'OK' if kapat else 'basarisiz - ESC ile kapat'))


def _sell_try_open(vid):
    """NPC'ye TEK tik. Kanit: ItemUse.py:553 net.SendOnClickPacket(vid)."""
    try:
        import net
        net.SendOnClickPacket(vid)
        return 1
    except:
        return 0

class _SellWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        _sell_tick()

def _sell_tick():
    """v5.0 SATIS dongusu (saha testi 16: 'sellall 5 dk sonra tekrar npcye
    tiklayip satmaya calisiyor' KOK NEDEN DUGUMU):
    v4.9'da shop.IsOpen() FLICKER donusunde cur=0 ile faz0'a dusuluyordu;
    dukkan aninda acilinca burst bastan basliyor, faz2 dogrulamasina HIC
    ulasilmiyordu -> dongu sonsuz. v5.0: (1) cur flicker'da KORUNUR,
    (2) flicker sayaci (10 ustu kesin dur), (3) 120sn HARD DEADLINE,
    (4) kara liste - 2 turda da duran esya bir daha denenmez, dongu
    erken biter, (5) bitince dukkan otomatik KAPANIR."""
    st = _SELL
    if not st['on']:
        return
    try:
        import time
        now = time.time()
    except:
        return
    # --- v5.0 HARD DEADLINE: ne olursa olsun 120 sn'de dur -----------------
    if st['t_start'] and (now - st['t_start']) >= 120.0:
        _sell_done(deadline=1)
        return
    # --- faz 0: dukkan bekle (SESSIZ - log spam YOK) -----------------------
    if st['faz'] == 0:
        try:
            import time, shop
            try:
                opened = int(shop.IsOpen())
            except:
                opened = 0
            if opened:
                st['faz'] = 1
                st['t_faz'] = now
                st['t0'] = 0.0
                st['flick_arada'] = 0
                # v5.0: cur KORUNUR - flicker donusunde bastan BASLANMAZ!
                if (now - st['t_log']) >= 3.0:
                    st['t_log'] = now
                    _live('SELL: dukkan acik - BURST slot %d.. (v5.0 flicker-koruma)' % st['cur'])
                return
            if (now - st['t_faz']) >= 8.0:
                if st['clicks'] < 2:
                    st['clicks'] += 1
                    st['t_faz'] = now
                    vid = _shop_npc_near()
                    if vid > 0:
                        st['vid'] = vid
                        _sell_try_open(vid)
                        _live('SELL: NPCye tekrar tiklandi (vid=%d, deneme %d/2)' % (vid, st['clicks']))
                    else:
                        _sell_stop('yakinda dukkanli NPC yok (3500px) - goto <x> <y> ile yanas, sonra tekrar')
                        return
                else:
                    _sell_stop('dukkan acilmadi (2 deneme) - NPCye KENDIN tikla, dukkan acilinca otomatik satar')
                    return
        except Exception, e:
            st['errs'] += 1
            if st['errs'] <= 3:
                _live('SELL faz0 hatasi: ' + _fmt_error(e))
            if st['errs'] > 50:
                _sell_stop('cok hata (%d)' % st['errs'])
        return
    # --- faz 1: BURST sat (45 slot tek nabizda - m2k deseni) --------------
    if st['faz'] == 1:
        try:
            import time, player, net, shop
            try:
                opened = int(shop.IsOpen())
            except:
                opened = 1
            if not opened:
                # v5.0: FLICKER! cur KORUNUR (v4.9 sifirlayip sonsuz dongu
                # yapiyordu). 2sn SESSIZ bekle, sonra faz0.
                if not st['flick_arada']:
                    st['flick'] += 1
                    st['flick_arada'] = 1
                    if st['flick'] <= 5 or (st['flick'] % 10) == 0:
                        _live('SELL: dukkan flicker #%d (slot %d KORUNDU - bastan baslanmadi)' % (st['flick'], st['cur']))
                    if st['flick'] >= 10:
                        _sell_stop('dukkan surekli flip-flap (flicker x%d) - sunucu/istemci senkron bozuk' % st['flick'])
                        return
                if (now - st['t_faz']) >= 2.0:
                    st['faz'] = 0
                    st['t_faz'] = now
                return
            st['flick_arada'] = 0
            if now - st['t0'] < 0.12:
                return
            st['t0'] = now
            st['t_faz'] = now
            try:
                tot = int(player.INVENTORY_PAGE_COUNT) * int(player.INVENTORY_PAGE_SIZE)
            except:
                tot = 90
            if st['cur'] >= tot:
                st['faz'] = 2
                st['t_faz'] = now
                _live('SELL: BURST turu bitti - paket=%d atlanan=%d (2sn dogrulama)' % (st['n'], st['skip']))
                return
            bl = _sell_blacklist()
            ilktur = st['cur']
            burst = 0
            while st['cur'] < tot and burst < 45:
                s = st['cur']
                st['cur'] = s + 1
                burst += 1
                if s in bl:
                    continue
                try:
                    v = int(player.GetItemIndex(s))
                except:
                    v = 0
                if v <= 0:
                    continue
                if not _sell_is_sellable(s, v):
                    st['skip'] += 1
                    continue
                # PAKET ONCELIGI: ONCE kanitli 1-arg (m2k/Taubuyer), yoksa
                # yeni 2-arg (uiShop.py:231 SendShopSellPacketNew)
                sent = 0
                if st['method'] == 'eski-1arg':
                    try:
                        net.SendShopSellPacket(s)
                        sent = 1
                    except AttributeError:
                        st['method'] = 'yeni'
                    except:
                        pass
                if not sent and st['method'] == 'yeni':
                    try:
                        cnt = int(player.GetItemCount(s))
                    except:
                        cnt = 1
                    if cnt < 1:
                        cnt = 1
                    try:
                        net.SendShopSellPacketNew(s, cnt)
                        sent = 1
                    except:
                        pass
                if sent:
                    st['n'] += 1
                else:
                    st['left'] += 1
            if st['n'] > 0 and (now - st['t_log']) >= 3.0:
                st['t_log'] = now
                _live('SELL: %d paket gonderildi (slot %d..%d, %s)' % (st['n'], ilktur, st['cur'] - 1, st['method']))
        except Exception, e:
            st['errs'] += 1
            if st['errs'] <= 3:
                _live('SELL hatasi: ' + _fmt_error(e))
            if st['errs'] > 50:
                _sell_stop('cok hata (%d)' % st['errs'])
        return
    # --- faz 2: dogrulama (kara liste + tumu reddedildiyse ERKEN bitis) ---
    if st['faz'] == 2:
        try:
            import time, player
            now = time.time()
            if (now - st['t_faz']) < 2.0:
                return
            left = _sell_left_items()
            # stuck sayaci: bu turda da duranlar (sunucu gercekten satmiyor)
            stk = st['stuck'] or {}
            for s, v in left:
                stk[s] = stk.get(s, 0) + 1
            st['stuck'] = stk
            bl = _sell_blacklist()
            aktif = [x for x in left if x[0] not in bl]
            st['pass'] += 1
            st['left'] = len(left)
            if len(aktif) > 0 and st['pass'] < 4:
                st['faz'] = 1
                st['cur'] = 0          # tam tur bastan (kara liste atlanir)
                st['t0'] = 0.0
                st['t_faz'] = now
                _live('SELL: dogrulama - %d esya hala duruyor (%d kara-listede), BURST tekrar (tur %d)' % (len(aktif), len(bl), st['pass'] + 1))
                return
            _sell_done()
        except Exception, e:
            st['errs'] += 1
            if st['errs'] <= 3:
                _live('SELL faz2 hatasi: ' + _fmt_error(e))
            if st['errs'] > 50:
                _sell_stop('cok hata (%d)' % st['errs'])
        return


def _sell_start(mode, force=0):
    try:
        if not _ingame():
            _write('selljunk', 'HATA: oyunda degilsin\n')
            return
        import time
        _SELL.update({'on': 1, 'mode': mode, 'force': force, 'cur': 0,
                      'pass': 0, 'left': 0, 't0': 0.0, 'n': 0, 'skip': 0,
                      'errs': 0, 'faz': 0, 't_faz': time.time(), 'clicks': 0,
                      'vid': 0, 'method': 'eski-1arg', 't_log': 0.0,
                      't_start': time.time(), 'flick': 0, 'stuck': {},
                      'flick_arada': 0})
        if _SELL['win'] is None:
            _SELL['win'] = _SellWnd()
        vid = _shop_npc_near()
        tiklandi = ' - once NPCye yanas'
        if vid > 0:
            _SELL['vid'] = vid
            _SELL['clicks'] = 1
            if _sell_try_open(vid):
                tiklandi = ' (vid=%d) Tiklandi' % vid
            else:
                tiklandi = ' - tiklanamadi, KENDIN tikla'
        else:
            _live('SELL: yakinda NPC yok - NPCye KENDIN tikla, dukkan acilinca satis baslar')
        _live('SELL: BASLADI (mod=%s force=%d) - v5.0: 120sn siniri + kara liste + flicker korumasi' % (mode, force))
        if mode == 'junk':
            jl = _junk_load()
            _write('selljunk', 'OK: COP SATMA HAZIR (v5.0)\n1) yakin NPCye tiklandi%s\n2) dukkan acilinca cop esyalar BURST gider (45 slot/nabiz)\n3) 2 turda satilmayan esya KARA LISTEYE girer - bir daha denenmez,\n   isim listesiyle raporlanir (sunucu reddi = gorev/kilitli esya olabilir)\n4) isinince dukkan OTOMATIK KAPATILIR (SendShopEndPacket)\n5) 120 sn HARD SINIR - dongu ne olursa olsun durur\ncop listesi: %d vnum + %d isim kalibi\nEFSUNLU esyalar ASLA satilmaz!\nDUR: selljunk 0  | liste: selljunk list | ekle: selljunk add <vnum>\nbitince: slots' % (tiklandi, len(jl), len(_JUNK['names'])))
        else:
            extra = ' (EFSUNLULAR DAHIL - DIKKAT!)' if force else '\nefsunlu esyalar ATLANIR (korumali mod) - gercekten hepsi: sellall force'
            _write('sellall', 'OK: TUM ENVANTER SATISI HAZIR (v5.0)%s\n1) NPCye tiklandi%s\n2) dukkan acilinca BURST satis (45 slot/nabiz)\n3) 2 turda satilmayan KARA LISTEYE girer + isim listesi raporlanir\n4) bitince dukkan OTOMATIK KAPATILIR (SendShopEndPacket)\n5) 120 sn HARD SINIR - dongu ne olursa olsun durur\nDUR: sellall 0' % (extra, tiklandi))
    except Exception, e:
        _write('selljunk', 'HATA ' + _fmt_error(e) + '\n')

def selljunk(sub=''):
    """COP ESYA SATISI (v4.9 BURST AKIS - saha testi 15 duzeltmesi):
    selljunk            -> cop satmaya hazirlan (NPCye 1 tik, dukkan ACILIR
                           ACILMAZ BURST satis baslar; acilmazsa NPCye
                           KENDIN tikla - spam YOK, surekli acma YOK)
    selljunk 0 | stop   -> DURDUR (v4.7'de durdurma yoktu - 'kapatamiyom')
    selljunk list       -> cop listesini goster
    selljunk add <vnum> -> vnum'u cop listesine ekle (kalici: junklist.txt)
    selljunk del <vnum> -> cikar
    selljunk name <isim> -> isim icerek esyalari cop say (kucuk harf)
    Satis paketi: ONCE kanitli 1-arg SendShopSellPacket(slot)
    (m2k Inventorymanager + Taubuyer NightTown kaniti), yoksa
    SendShopSellPacketNew(slot, adet) (uiShop.py kaniti)"""
    try:
        a = str(sub).strip()
        p = a.split()
        k = p[0].lower() if p else ''
        if k in ('0', 'stop', 'kapat', 'dur', 'off'):
            _sell_stop('elle durduruldu (selljunk %s)' % (k if k else '0'))
            return
        if not a:
            _sell_start('junk')
            return
        if k == 'list':
            jl = _junk_load()
            L = ['COP LISTESI (selljunk bunlari satar)', 'vnum sayisi: %d (varsayilan: baliklar)' % len(jl)]
            defs = _junk_defaults()
            extra = [v for v in jl if v not in defs]
            if extra:
                L.append('eklenen vnumlar: %s' % ' '.join([str(v) for v in extra]))
            if _JUNK['names']:
                L.append('isim kaliplari: %s' % ' | '.join(_JUNK['names']))
            L.append('dosya: %s' % JUNK_PATH)
            L.append('ekle: selljunk add <vnum> | isimle: selljunk name <kelime>')
            _write('selljunk', '\n'.join(L) + '\n')
        elif k == 'add':
            v = int(p[1])
            if v not in _junk_load():
                _JUNK['vnums'].append(v)
            _junk_save()
            _write('selljunk', 'OK: vnum %d cop listesinde (%s)' % (v, JUNK_PATH))
        elif k == 'del':
            v = int(p[1])
            if v in _junk_load():
                _JUNK['vnums'].remove(v)
            _junk_save()
            _write('selljunk', 'OK: vnum %d listeden cikarildi' % v)
        elif k == 'name':
            nm = a[5:].strip().lower()
            if nm and nm not in _JUNK['names']:
                _JUNK['names'].append(nm)
            _junk_save()
            _write('selljunk', 'OK: isim kalibi "%s" eklendi (esya isminde gecen satar)' % nm)
        else:
            _write('selljunk', 'kullanim: selljunk | selljunk list | selljunk add <vnum> | selljunk name <isim>\n')
    except Exception, e:
        _write('selljunk', 'HATA ' + _fmt_error(e) + '\n')

def sellall(force=''):
    """TUM ENVANTERI NPC'YE SAT (v4.9 BURST): 'envanterin hepsini npcye sat'.
    EFSUNLU esyalar yine ATLANIR (kayip riski!) - gercekten tamami:
    sellall force. DURDUR: sellall 0 (veya sellall stop)."""
    try:
        a = str(force).strip().lower()
        if a in ('0', 'stop', 'kapat', 'dur', 'off'):
            _sell_stop('elle durduruldu (sellall %s)' % (a if a else '0'))
            return
        f = 1 if a in ('force', 'f', 'hepsi') else 0
        _sell_start('all', f)
    except Exception, e:
        _write('sellall', 'HATA ' + _fmt_error(e) + '\n')

_DROP = {'win': None, 'on': 0, 'cur': 0, 'pass': 0, 't0': 0.0, 'n': 0,
         'method': 'eski-1arg', 'left': 0, 't_log': 0.0, 'errs': 0,
         'wait': 0, 't_wait': 0.0,
         # v5.0 (saha testi 16: 'dropall 5 dk da bir atiyo durmuyo'):
         # kara liste (3 turda da dusmeyen bir daha denenmez) + 120sn HARD
         # DEADLINE + ATILAMAYANLAR isim+boyut listesiyle raporlanir.
         # NOT: sunucu BURST paketlerini YAVAS isleyebilir -> esyalar dongu
         # bittikten SONRA dakikalar icinde tek tek duser ('5 dk da bir
         # atiyo' buydu) - bu sunucu davranisi, tekrar komut gerekmez.
         't_start': 0.0, 'stuck': None}

def _drop_wname():
    return 'dropall'

def _drop_stop(msg):
    st = _DROP
    st['on'] = 0
    try:
        if st['win'] is not None:
            st['win'].Hide(); st['win'].Destroy()
    except:
        pass
    st['win'] = None
    _live('DROPALL DURDU: ' + msg)
    _write('dropall', 'DURDU: ' + msg)

def _drop_blacklist():
    """kara liste: 3 dogrulama turunda da duran slotlar (sunucu reddi)."""
    st = _DROP
    bl = []
    for s, c in (st['stuck'] or {}).items():
        if c >= 3:
            bl.append(s)
    return bl

def _drop_left_items():
    """kalan esyalar [(slot, vnum)] - kara liste DISINDA."""
    import player
    try:
        tot = int(player.INVENTORY_PAGE_COUNT) * int(player.INVENTORY_PAGE_SIZE)
    except:
        tot = 90
    bl = _drop_blacklist()
    out = []
    for s in range(tot):
        if s in bl:
            continue
        try:
            v = int(player.GetItemIndex(s))
        except:
            v = 0
        if v > 0:
            out.append((s, v))
    return out

def _drop_report_items(items):
    """kalan esyalari ISIM + BOYUT ile listele (ilk 12)."""
    L = []
    for s, v in items[:12]:
        w, h = _item_size(v)
        boy = (' (%dx%d)' % (w, h)) if (w > 1 or h > 1) else ''
        L.append('  [%d] vnum=%d %s%s' % (s, v, _item_name(v), boy))
    if len(items) > 12:
        L.append('  ... + %d tane daha (detay: inv)' % (len(items) - 12))
    return L

def _drop_done(deadline=0):
    st = _DROP
    st['on'] = 0
    try:
        if st['win'] is not None:
            st['win'].Hide(); st['win'].Destroy()
    except:
        pass
    st['win'] = None
    tag = ' (120sn sure siniri)' if deadline else ''
    bl = _drop_blacklist()
    blitems = []
    if bl:
        import player
        for s in bl:
            try:
                v = int(player.GetItemIndex(s))
            except:
                v = 0
            if v > 0:
                blitems.append((s, v))
    left = _drop_left_items()
    if st['n'] == 0 and not blitems and not left:
        _live('DROPALL: BITTI - 0 esya atildi (sunucu reddediyor olabilir)')
        _write('dropall', 'BITTI: 0 esya atildi!\nBU SUNUCU yere atmayi engelliyor olabilir (drop yasagi / level siniri).\nAlternatif: NPC varsa sellall (sat), ya da itemleri sakla.\nkontrol: slots')
    elif blitems or left:
        _live('DROPALL: BITTI%s - %d atildi, ATILAMAYAN %d | kalan %d' % (tag, st['n'], len(blitems), len(left)))
        L = ['BITTI%s: atilan=%d (yontem=%s)' % (tag, st['n'], st['method'])]
        if blitems:
            L.append('ATILAMAYANLAR (3 turda da dusmedi - sunucu reddi; gorev/kilitli')
            L.append('esya olabilir - bir daha DENENMEZ):')
            L.extend(_drop_report_items(blitems))
        if left:
            L.append('hala atilabilir gorunen (%d):' % len(left))
            L.extend(_drop_report_items(left))
            L.append('(tekrar denemek icin: dropall)')
        L.append('NOT: sunucu paketleri YAVAS isleyebilir - esyalar dakikalar icinde')
        L.append('tek tek duser; dongu zaten bitti, tekrar dropall yazmak gerekmez.')
        L.append('kontrol: slots')
        _write('dropall', '\n'.join(L) + '\n')
    else:
        _live('DROPALL: BITTI%s - %d esya atildi (yontem=%s)' % (tag, st['n'], st['method']))
        _write('dropall', 'OK: ATMA BITTI%s - %d slot yere atildi (yontem=%s)\nNOT: sunucu paketleri YAVAS isleyebilir - esyalar dakikalar icinde tek tek duser.\nkontrol: slots' % (tag, st['n'], st['method']))

class _DropAllWnd(ui_WindowBase):
    def __init__(self):
        ui_WindowBase.__init__(self)
        self.Show()

    def OnUpdate(self):
        _drop_tick()

def _drop_tick():
    """v5.0 ATMA dongusu (saha testi 16: 'dropall tahminen 5 dk da bir atiyo
    durmuyo'): BURST korunur (m2k kaniti) + KARA LISTE: 3 turda da dusmeyen
    esya bir daha denenmez + 120sn HARD DEADLINE + ATILAMAYANLAR isim+boyut
    listesiyle raporlanir. Sunucu paketleri yavas isliyorsa esyalar dongu
    bittikten sonra dakikalar icinde tek tek duser - dongu 15sn civarinda
    biter ve KALAN esya raporu bir kez yazilir (5 dkda bir tekrar YOK)."""
    try:
        import time, player, net
        st = _DROP
        if not st['on']:
            return
        now = time.time()
        # --- v5.0 HARD DEADLINE: ne olursa olsun 120 sn'de dur --------------
        if st['t_start'] and (now - st['t_start']) >= 120.0:
            _drop_done(deadline=1)
            return
        # tur arasi dogrulama molasi (2.5sn - sunucu islesin diye)
        if st['wait']:
            if (now - st['t_wait']) < 2.5:
                return
            st['wait'] = 0
        if now - st['t0'] < 0.12:
            return
        st['t0'] = now
        try:
            tot = int(player.INVENTORY_PAGE_COUNT) * int(player.INVENTORY_PAGE_SIZE)
        except:
            tot = 90
        if st['cur'] >= tot:
            # tur bitti - dogrulama + kara liste guncelle
            st['pass'] += 1
            left = _drop_left_items()
            stk = st['stuck'] or {}
            for s, v in left:
                stk[s] = stk.get(s, 0) + 1
            st['stuck'] = stk
            bl = _drop_blacklist()
            aktif = [x for x in left if x[0] not in bl]
            st['left'] = len(left)
            if len(aktif) > 0 and st['pass'] < 5:
                st['cur'] = 0
                st['wait'] = 1
                st['t_wait'] = now
                _live('DROPALL: dogrulama - %d esya hala duruyor (%d kara-listede), BURST tekrar (tur %d)' % (len(aktif), len(bl), st['pass'] + 1))
                return
            _drop_done()
            return
        bl = _drop_blacklist()
        ilktur = st['cur']
        burst = 0
        while st['cur'] < tot and burst < 45:
            s = st['cur']
            st['cur'] = s + 1
            burst += 1
            if s in bl:
                continue
            try:
                v = int(player.GetItemIndex(s))
            except:
                v = 0
            if v <= 0:
                continue
            # PAKET ONCELIGI: ONCE kanitli 1-arg net.SendItemDropPacket
            # (m2k Inventorymanager DropAllItems); YOKSA
            # net.SendItemDropPacketNew(slot, adet) (cycu.py kaniti)
            sent = 0
            if st['method'] == 'eski-1arg':
                try:
                    net.SendItemDropPacket(s)
                    sent = 1
                except AttributeError:
                    st['method'] = 'yeni'
                except:
                    pass
            if not sent and st['method'] == 'yeni':
                try:
                    cnt = int(player.GetItemCount(s))
                except:
                    cnt = 1
                if cnt < 1:
                    cnt = 1
                try:
                    net.SendItemDropPacketNew(s, cnt)
                    sent = 1
                except:
                    pass
            if sent:
                st['n'] += 1
        if st['n'] > 0 and (now - st['t_log']) >= 3.0:
            st['t_log'] = now
            _live('DROPALL: %d paket gonderildi (slot %d..%d, %s)' % (st['n'], ilktur, st['cur'] - 1, st['method']))
    except Exception, e:
        st = _DROP
        st['errs'] += 1
        if st['errs'] <= 3:
            _live('DROPALL hatasi: ' + _fmt_error(e))
        if st['errs'] > 50:
            _drop_stop('cok hata (%d)' % st['errs'])


def dropall(sub=''):
    """TUM ENVANTERI YERE AT (v5.0 - saha testi 16 '5 dk da bir atiyo
    durmuyo' duzeltmesi): BURST gonderim korunur (m2k kaniti). YENI:
    3 turda da dusmeyen esya KARA LISTEYE girer (bir daha denenmez) ve
    ATILAMAYANLAR olarak isim+boyut listesiyle raporlanir + 120sn HARD
    SINIR (dongu ne olursa olsun durur). Sunucu paketleri yavas isliyorsa
    esyalar dongu bittikten sonra dakikalar icinde tek tek duser - bu
    sunucunun davranisi, tekrar komut yazmak gerekmez. EFsunlular dahil
    HER SEY atilir - geri alinamaz! DURDUR: dropall 0 (veya dropall stop)."""
    try:
        a = str(sub).strip().lower()
        if a in ('0', 'stop', 'kapat', 'dur', 'off'):
            _drop_stop('elle durduruldu (dropall %s)' % (a if a else '0'))
            return
        if not _ingame():
            _write('dropall', 'HATA: oyunda degilsin\n')
            return
        import time
        _DROP.update({'on': 1, 'cur': 0, 'pass': 0, 't0': 0.0, 'n': 0,
                      'method': 'eski-1arg', 'left': 0, 't_log': 0.0,
                      'errs': 0, 'wait': 0, 't_wait': 0.0,
                      't_start': time.time(), 'stuck': {}})
        if _DROP['win'] is None:
            _DROP['win'] = _DropAllWnd()
        _live('DROPALL: BASLADI - v5.0 (120sn siniri + kara liste + isimli kalan raporu)')
        _write('dropall', 'OK: TUM ENVANTER YERE ATILIYOR (v5.0)\nBURST: 45 slot/nabiz (m2k DropAllItems kaniti)\nv5.0 YENI:\n  - 3 turda dusmeyen esya KARA LISTEYE girer (bir daha denenmez)\n  - ATILAMAYAN esyalar isim + boyut listesiyle raporlanir (bir kez)\n  - 120 sn HARD SINIR - dongu ne olursa olsun durur\nNOT: sunucu paketleri YAVAS isleyebilir - esyalar dongu bittikten sonra\n     dakikalar icinde tek tek duser (5 dkda bir dusme SUNUCUDAN, dongudan degil)\nefsunlular DAHIL her sey atilir (GERI ALINAMAZ!)\nDUR: dropall 0 | bitince: slots')
    except Exception, e:
        _write('dropall', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# v5.0 TEK NABIZ: DLL'in 150ms hizli timer'i (v2.6) maxlib._tick() cagirir;
# ui dongu pencereleri de ayni govdelere yonlendirilir (cift surus). Tum
# donguler zaman kapili oldugu icin cift tetiklenme guvenlidir. saha testi
# 15 kok nedeni: donguler 1 islem sonrasi duruyordu - artik DLL timer'i
# bagimsiz ikinci kalptir.
# ---------------------------------------------------------------------------
_TICK = {'t': 0.0, 'n': 0, 'err': 0}

def _tick():
    """DLL TimerProc burayi ~150ms'de bir cagirir (v2.6 DLL). Eski DLL'de
    yalnizca ui pencereleri surer - yine de calisir (cift surus)."""
    try:
        import time
        now = time.time()
        st = _TICK
        if now - st['t'] < 0.05:
            return
        st['t'] = now
        st['n'] += 1
        _otp_tick()
        _sell_tick()
        _drop_tick()
        _relogin_tick()   # v5.2: relogin state-machine (DLL nabzi ile surer)
    except Exception, e:
        st = _TICK
        st['err'] += 1
        if st['err'] <= 3:
            try:
                _live('TICK hatasi: ' + _fmt_error(e))
            except:
                pass


# ---------------------------------------------------------------------------
# modul kaydi - DLL snippet'leri `import maxlib; maxlib.xxx()` der
# ---------------------------------------------------------------------------
import types as _types
import sys as _sys
_maxlib = _sys.modules.get('maxlib', None)
if _maxlib is None:
    _maxlib = _types.ModuleType('maxlib')
for _k, _v in globals().items():
    if _k.startswith('__'):
        continue
    setattr(_maxlib, _k, _v)
_sys.modules['maxlib'] = _maxlib

# ---------------------------------------------------------------------------
# yukleme raporu
# ---------------------------------------------------------------------------
_install_error_hooks()   # oto hata izleme - yanlis sifre vb. last_error.txt'ye
# v4.4 KULLANICI ISTEGI: oyuna girer girmez konsola uzun yazi dizileri
# (balik/komut listesi) basilmasin. Tam rapor DOSYADA:
#   results\last_pylib_load.txt  |  konsola sadece 1 kisa satir:
# v4.7: live.txt oturum basinda TEMIZ baslar - DLL acilisinda konsol
# ESKI oturumun [LIVE] balik satirlarini geri oynatiyordu (kullanici raporu)
try:
    _lf = open(LIVE_PATH, 'w')
    _lf.close()
except:
    pass

_write('pylib_load',
       'PLUSMAXGOD_PyScript v%s yuklendi (ANA THREAD)' % PYLIB_VERSION + chr(10) +
       'v5.2: UNIVERSAL LOGIN/SELSERVER - 28-client GitHub arastirmasi ile (RESEARCH.md)' + chr(10) +
       '  login <id> <pwd> [3.alan]  : 3-parametreli login (PIN/guard/slot) + pw.Connect yolu' + chr(10) +
       '  selserver <srv> <ch> [ok]  : listbox + Marty channelButton + coklu-bolge + ok=0 modu' + chr(10) +
       '  uiprobe                    : login ekrani tam taramasi (mimari tespit + 3. alan raporu)' + chr(10) +
       '  relogin [id pwd [srv ch]]  : TAM relogin (logout->disconnect->login akisi)' + chr(10) +
       '  reloginquick [slot]        : HIZI relogin (logout->selchar, baglanti korunur)' + chr(10) +
       'v5.1: oto-pot (hp/mp) ozelligi ve komutlari KALDIRILDI' + chr(10) +
       'v5.0: slots COK-HUCRELI esya (GetItemSize - oyunla AYNI sayim) | sell/drop KARA LISTE + 120sn siniri + isimli kalan raporu' + chr(10) +
       'sellall bitince dukkan OTOMATIK KAPANIR (SendShopEndPacket) | sell flicker korumasi (sonsuz dongu kok-nedeni kapandi)' + chr(10) +
       'v4.9: sell/drop BURST | otp2 ISINLANA+ADIM | DLL 150ms nabzi (_tick)' + chr(10) +
       'otp delay/step alt-komut | durdurma: selljunk 0 / sellall 0 / dropall 0' + chr(10) +
       'v4.5: ui_WindowBase sira hatasi duzeltildi (v4.4 yuklenemeyip v3.2\'ye dusuyordu!)' + chr(10) +
       'v4.4 OZET: fishdelay/fishswap/fishswapnow/fishtp KALDIRILDI' + chr(10) +
       'YENI: morphtarget cloneplayer fakemount speed aspeed statup skillup antifly antiflyeffect itemfind iteminfo attr useon efsunsw gotake' + chr(10) +
       'DEGIS: near=genis vid taramasi + arka plan 4M | otp=attackkey+50ms | clone=Z+sac-fix | morph/spawn=gorsel tazeleme | relogin/chchange=ExitGame yolu' + chr(10) +
       'hata izleme hooklari: %s' % (', '.join(_HOOKS_OK) if _HOOKS_OK else 'henuz kurulamadi (status ile tekrar denenir)') + chr(10)
       + status_text(), echo=False)
try:
    sys.stdout.write('[MAXLIB] pylib v%s aktif (tum komutlar: help)' % PYLIB_VERSION + chr(10))
except:
    pass
