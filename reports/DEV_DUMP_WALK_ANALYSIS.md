# DEV RAPOR — Dump.rar Python Katmanı + LegendySF-V2 Hareket Protokolü ve Adım Atma Animasyonu Mekanizması

*Üretim: 2026-10-28 | Görev: DEEP SCAN | Referans: DrLegendy/LegendySF-V2 (ClientSource + GameSource) + dump.rar (PLUSMAXGOD pydumpall v4.1 çıktısı) + PDF versiyonu: `reports/LegendySF-Dump_Derin_Analiz_Raporu.pdf` (19 sayfa)*

> **Bu rapor ne yapar?** (1) dump.rar içindeki 154 Python dosyasını envanterler ve C++ karşılıklarıyla eşleştirir, (2) "C++'da yapılabilenlerin hangilerini Python'da yapabiliriz" sorusunu üç kategoriyle kesin sınırlarıyla cevaplar, (3) botların "tek ayak havada, adım animasyonu tamamlanmadan yürüme" davranışının kök nedenini dosya:satır kanıtıyla çözer.

---

## İçindekiler
- 1. Yönetici Özeti
- 2. dump.rar Envanteri (154 dosya)
- 3. LegendySF-V2 C++ Envanteri
- 4. C++ vs Python Karşılaştırma Matrisi
- 5. Hareket Protokolü: TPacketCGMove + FUNC sabitleri + throttles
- 6. ÇEKİRDEK BULGU: Tek Ayak Havada Yürüme Mekanizması
- 7. Bilinçli mi? Motivasyon + Sunucu Tespiti
- 8. Uygulama Notları
- 9. Kaynakça (kod kanıtları + web)

---

## 1. Yönetici Özeti

| # | Bulgu |
|---|---|
| B1 | **Tek ayak havada yürümenin kök nedeni:** bot `chr.SetPixelPosition` ışınlaması + tek karelik `DIK_UP` tuş simülasyonu yapar; hareket vektörü 1.0'ı aşmadığı için istemci state'i **FUNC_WAIT** olarak bildirir (FUNC_MOVE değil). Sunucu FUNC_WAIT'i anlık konum kabulü sayar; izleyici istemci her FUNC_WAIT'te yürüyüş animasyonunu BAŞLATIP anında durdurur. Döngü her ~100 ms'de animasyonu kare 0'dan yeniden başlatır → tam adım asla oynatılamaz. |
| B2 | **Bilinçli yöntem:** LegendySF kaynaklarında `ENABLE_TP_SPEED_CHECK` yorum satırında (input_main.cpp:1557) → FUNC_WAIT konumlarında mesafe kontrolü yok; küçük adım dizisi ışınlama hızı üretir, tek büyük sıçrama reddedilir (Boost bulgusuyla uyumlu). Animasyon bozukluğu = kabul edilmiş yan etki. |
| B3 | **SendCharacterStatePacket Python'a kapalı.** İstemci bu paketi kendi event handler'larıyla otomatik gönderir: OnWaiting→FUNC_WAIT @100ms (>1px koşulu), OnMoving→FUNC_MOVE @300ms (PythonPlayerEventHandler.cpp:38-94). Bot elle göndermez; teorideki "adım atarken daha az döngüde yollama" dolaylı doğru. |
| B4 | **C++/Python sınırı 3 kategori:** A) saf Python'da yapılabilenler (hareket, ışınlama, saldırı döngüsü, item/chat/shop), B) özel C++ modül gerektirenler (m2BotLib: ham CG_ATTACK — net modülünde SendAttackPacket binding'i YOK), C) istemci-içi Python'da imkânsızlar (paket koklama, DLL injection, bellek erişimi). |
| B5 | **Sunucu tespiti:** ENABLE_TP_SPEED_CHECK etkinleştirme + FUNC_WAIT frekans/mesafe istatistiği + hareket vektörü-FUNC tutarsızlık denetimi + dwTime geri-ileri zaman denetimi (Bölüm 7, 6 önlem). |

---

## 2. dump.rar Envanteri (154 dosya)

**Kanıt zinciri (INDEX.txt):** pydumpall v4.1, istemci içinde çalıştı; `pack.Get` ile 73 dosya diske yazıldı; sys.modules'ta 55 modül görüldü; 31 modül `KAYNAKSIZ(C)` = binary'ye gömülü C modülleri: `app, background, chat, chr, chrmgr, dbg, effect, event, fly, grp, grpImage, grpText, guild, ime, item, messenger, net, nonplayer, pack, player, profiler, quest, safebox, sash, skill, snd, systemSetting, textTail, wndMgr`.

| Kategori | Adet | Örnekler | Rol |
|---|---|---|---|
| Botlar | 18 | darealfreakbot (9511 satır), pasha37-levelbot, farmbot, WalkToMobs, fishbot1.0/1.1, buffbot, eiglib destekli yaklaş-saldır | Hareket metodlarının canlı kanıtı |
| Hack scriptleri | 51 | multihack*, teleport*, Crap_Levelbot (±2000px ışınla), moblock, zoomhack, efsunbotu, okcuhack | TP/hız desenleri |
| Client çekirdek modülleri | 43 | game.py, interfacemodule.py, introLogin, ui*.py | Meşru API referansı |
| UIScript dump'ları | 37 | ui__UIScript_*.py.py (pydumpall çift uzantı adlandırması) | Arayüz tanımları |
| Kütüphaneler | 5 | eiglib (WalkVID/WalkCOORD/SendAttack), ServerCommandParser, stringCommander | Mini bot framework'ü |

**Kritik kanıt — darealfreakbot.py:688-697 (TP-adımlama deseni):**

```python
if self.IsWalkToMob():
    chr.MoveToDestPosition(int(myVid), int(self.aimx), int(self.aimy))  # meşru yürüyüş
else:
    chr.SelectInstance(myVid)
    chr.SetPixelPosition(int(x), int(y), int(z))    # IŞINLAMA MODU
    self.Debug()

def Debug(self):                                    # :695-697
    player.SetSingleDIKKeyState(app.DIK_UP, TRUE)   # yukarı ok 1 KARE bas
    player.SetSingleDIKKeyState(app.DIK_UP, FALSE)  # -> yarım adım + FUNC_WAIT sync
```

elitepvpers Auto Hunt (Eylül 2025) yayını birebir aynı deseni kullanıyor: `SetPixelPosition(...) ... self.Debug() ... TeleportState = 1` — teknik ≥10 yıldır topluluk standardı.

---

## 3. LegendySF-V2 C++ Envanteri

- **ClientSource:** 627 .cpp/.h; 22 Python modülünde **~835 binding**: player 153, net 135, app 109, chr 83, background 48, item 45, system 39, chrmgr 38, ime 33, chat 30, minimap 27, nonplayer 21, exchange 20, texttail 18, diğer 8 modül 26.
- **GameSource:** CHARACTER (char.cpp) 223 fonksiyon; CInputMain (input_main.cpp) 52 paket işleyicisi; char_state.cpp 27.
- Dump'taki KAYNAKSIZ(C) modülleri birebir bu C++ dosyalarına karşılık gelir: `chr.MoveToDestPosition` → `chrMoveToDestPosition` (PythonCharacterModule.cpp:1179) → `NEW_MoveToDestPixelPositionDirection` (:1196).

---

## 4. C++ vs Python Karşılaştırma Matrisi

### Kategori A — Saf Python ile DOĞRUDAN (gömülü modüller)

| Yetenek | Python API | C++ kanıt |
|---|---|---|
| Animasyonlu yürüyüş | `chr.MoveToDestPosition(vid,x,y)` | PythonCharacterModule.cpp:1179 → NEW_Goto |
| Anlık ışınlama (paket YOK) | `chr.SetPixelPosition(x,y,z)` | InstanceBaseTransform.cpp:8-17 |
| Sürekli saldırı döngüsü | `player.SetAttackKeyState(True/False)` | PythonPlayerInputKeyboard.cpp:6-20 (m_isAtkKey) |
| Yön/konum okuma | `chr.SetRotation`, `chr.GetPixelPosition`, `player.GetMainCharacterPosition` | InstanceBaseTransform.cpp:24-65 vb. |
| Hedef/VID tarama | `chr.GetInstanceType`, `chr.SelectInstance`, `nonplayer.GetLevelByVID` | PythonCharacterManager/NonPlayerModule |
| Item/chat/shop/party/safebox | `net.SendItemUsePacket`, `net.SendChatPacket`, `net.SendShop*`, `net.SendSafebox*` | PythonNetworkStreamModule.cpp:1984-2048 |
| Yerel animasyon hızı | `chr.SetMoveSpeed(vid,val)` | PythonCharacterModule.cpp:1389 (sunucu hızını değiştirmez) |

### Kategori B — Özel C++ modülü (enjekte DLL) gerekir

| Yetenek | Neden | Kanıt |
|---|---|---|
| Ham CG_ATTACK paketi | net modülünde `SendAttackPacket` binding'i YOK | dump: `m2BotLib.SendAttackPacket(vid)` (darealfreakbot.py:665) |
| SendCharacterStatePacket elle çağrı | C++'ta VAR (PythonNetworkStreamPhaseGame.cpp:1152) ama Python'a AÇILMAMIŞ | Boost analizi (DEV_Report.md) |
| Ham byte akışı / ikinci bağlantı | net.Send* hazır paketler sunar; serbest akış binding yok | eiglib.ConnectToChannel (eiglib.py:81) |

### Kategori C — İstemci-içi saf Python'da İMKÂNSIZ

| Yetenek | Gerçek yol |
|---|---|
| Paket koklama | C++ enjeksiyon (MaxExecutor yaklaşımı) veya seviye-sniffer |
| DLL injection / hook | C++ DLL (WndProc + ana iş parçacığı) |
| Bellek okuma/yazma | Harici araç veya özel C modülü |
| Sunucu taraflı istismar | Kaynak kodu olan sunucuda sistem yazımı |

---

## 5. Hareket Protokolü

### TPacketCGMove (CG, header=7) / TPacketGCMove (+dwVID)

| Alan | İçerik | Kanıt |
|---|---|---|
| bFunc | FUNC_WAIT=0, FUNC_MOVE=1, FUNC_ATTACK=2, FUNC_COMBO=3, FUNC_MOB_SKILL=4, FUNC_EMOTION=5, FUNC_SKILL=0x80\|motion | InstanceBase.h:70-76; input_main.cpp:1537 |
| bArg | combo vuruş indeksi / skill arg | InstanceBase.cpp:1503 |
| bRot | açı/5 (5° çözünürlük) | PhaseGame.cpp:1167 |
| lX,lY | hedef piksel; local→global dönüşüm | :1168-1174 |
| dwTime | `ELTimer_GetServerMSec()` | :1170 |
| dwDuration | SADECE GC: FUNC_MOVE→`GetCurrentMoveDuration()`, diğerleri 0 | input_main.cpp:1685 |

### İstemci throttle programı (PythonPlayerEventHandler.cpp)

| Handler | Paket | Throttle |
|---|---|---|
| OnMove | FUNC_MOVE | anında |
| OnMoving | FUNC_MOVE | max 300 ms |
| OnWaiting | FUNC_WAIT | max 100 ms VE >1 px kayma koşulu |
| OnStop/OnWarp | FUNC_WAIT | anında |
| OnAttack/OnUseSkill | FUNC_COMBO / FUNC_SKILL | her seferinde |

**Karar noktası:** `CInstanceBase::Transform()` (InstanceBase.cpp:1994-2015) — IsWalking() iken animasyon motorunun ürettiği **hareket vektörü** >1.0 ise OnMoving, değilse OnWaiting. Işınlama → vektör ≈ 0 → hep FUNC_WAIT.

### Sunucu (CInputMain::Move, input_main.cpp:1530-1700)

| bFunc | Sunucu davranışı | Yayın |
|---|---|---|
| FUNC_MOVE | `ch->Goto(x,y)` yol simülasyonu; hız limiti | dwDuration dolu |
| FUNC_WAIT (ve saldırı) | `ch->Move(x,y)` **ANINDA konum** + `Stop()` | dwDuration = 0 |

---

## 6. ÇEKİRDEK BULGU: Tek Ayak Havada Yürüme Mekanizması

### 6.1 Animasyon motoru

```cpp
void CActorInstance::Move()                        // ActorInstance.cpp:209
{ if (m_isWalking) SetLoopMotion(NAME_WALK, 0.15f, m_fMovSpd);
  else             SetLoopMotion(NAME_RUN,  0.15f, m_fMovSpd); }

void CActorInstance::Stop(float t)                 // :221
{ __ClearMotion(); SetLoopMotion(NAME_WAIT, t); }  // kare=0

void CActorInstance::SetMoveSpeed(float s)         // :190
{ ... if (__IsMoveMotion()) { Stop(); Move(); } }  // hız değişimi = RESTART
```

`SetLoopMotion` her çağrıda `__ClearMotion()` (ActorInstanceMotion.cpp:307, 627-637) → **kare 0'a sıfırlanır**. Yürüyüş döngüsünün ilk kareleri = ayağın havaya kalktığı adım-başlangıcı pozu.

### 6.2 İzleyici istemci (StateProcess, InstanceBase.cpp:1434-1490)

- **FUNC_WAIT + fDirLen > 1 px:** StartWalking (kare 0'dan) → kısa mesafe → anında varış → EndWalking. `m_kMovAfterFunc=FUNC_WAIT`.
- **FUNC_MOVE:** StartWalking; varışta DURMAZ (`case FUNC_MOVE: break;` :1791-1794) — döngü kesintisiz.

### 6.3 Birleşim — 100 ms'lik sonsuz yarım adım

```
T+0     bot: SetPixelPosition(20px) + Debug() → ışınla + yarım adım
        sunucu: FUNC_WAIT alır → Move(x,y)+Stop() = ANINDA kabul
        izleyici: GC_MOVE FUNC_WAIT → StartWalking (kare 0, ayak kalkar)
T+~20ms izleyici: kısa mesafe bitti → EndWalking (dur)
T+100ms bot: OnWaiting (>1px) → yeni FUNC_WAIT → döngü BAŞTAN
SONUÇ:  yürüyüş döngüsü (0.5-1.0s) asla tamamlanmaz → TEK AYAK HAVADA, kayarak yürüme
```

### 6.4 Teorinin değerlendirmesi

| Teori parçası | Hüküm |
|---|---|
| "SendCharacterState'i adım atarken gönderdetmiyorlar" | ❌ Gönderiyor — ama **FUNC_WAIT olarak** (FUNC_MOVE akışını hiç açmıyor) |
| "Botlar SendCharacterState'i canavarlara sürekli yollatır" | ✅ Saldırıda yoğun akış: her vuruş FUNC_COMBO + CG_ATTACK + SyncPosition |
| "Adım atarken daha az döngüde yollarsa" | ✅ Dolaylı: FUNC_WAIT @100ms + >1px koşulu = seyrek akış |
| "Adım animasyonu tamamlanmıyor" | ✅ Kök neden: FUNC_WAIT mikro-döngüsü + SetLoopMotion kare-sıfırlama |

---

## 7. Bilinçli mi? Motivasyon + Sunucu Tespiti

**5 gerekçe:** (1) hız — yol/ivme/yürüyüş beklemesi yok; (2) LegendySF'de ENABLE_TP_SPEED_CHECK devre dışı → mesafe denetimi yok; (3) SPEEDHACK zaman denetimi (dwTime ileri-kaçış) bu desene takılmaz; (4) algı — 100ms küçük adım uzaktan "kayma" gibi algılanır, sert blink'ten az dikkat çeker; (5) paket maliyeti düşük.

**Sunucu önlemleri (LegendySF kaynak spesifik):**

| # | Önlem | Yer | Yakaladığı |
|---|---|---|---|
| 1 | ENABLE_TP_SPEED_CHECK aç | input_main.cpp:1557 | uzak FUNC_WAIT konumları |
| 2 | FUNC_WAIT mesafe bütçesi (pencere başına toplam) | CInputMain::Move | birikimli ışınlama hızı |
| 3 | FUNC_WAIT frekans sayacı | CHARACTER::Move | 10+/sn FUNC_WAIT = bot imzası |
| 4 | Hareket-FUNC tutarlılık istatistiği | sunucu | %95'i 1-30px'lik FUNC_WAIT serisi |
| 5 | dwTime geriye-kaçış denetimi | :1591-1612 yanına | replay/zaman istismarı |
| 6 | Goto-simülasyon çelişki denetimi | sunucu | anlık konum sıçramaları |

---

## 8. Uygulama Notları

- **Doğal yürüyüş için:** FUNC_MOVE akışını açık tut (`chr.MoveToDestPosition` zinciri, eiglib.WalkVID deseni); OnMoving 300ms throttle'a güven. otp (240px + MoveToDestPosition + 1300ms) bu yoldadır — izleyicide animasyon düzgündür.
- **TP-sonrası geri atma (OptimizeTP sorunu):** sunucu Goto simülasyonunu tamamlamadan yeni konum gelirse kalan mesafeyi geri sarar; TP sonrası bir FUNC_WAIT kabulü veya tam Goto süresi bekle.
- **SendCharacterStatePacket'i elle çağırma:** gereksiz ve önerilmez — throttle'ları atlayıp anormal frekans profili üretir.
- **C++→Python yol haritası:** Kategori A ile başla; ham CG_ATTACK için pylib'e yardımcı ekle (m2BotLib yerine, hook'suz); Kategori C için C++'a geç.

---

## 9. Kaynakça

**Kod kanıtları (LegendySF-V2 @ main):** PythonNetworkStreamPhaseGame.cpp:1152-1189 · PythonPlayerEventHandler.cpp:38-94 · InstanceBase.cpp:1994-2015, 1434-1490, 1289-1330 · PythonCharacterModule.cpp:1179-1199, 679-702 · InstanceBaseTransform.cpp:8-17 · GameLib/ActorInstance.cpp:190-225 · GameLib/ActorInstanceMotion.cpp:290-320, 627-637 · input_main.cpp:1530-1700 · dump/darealfreakbot.py:688-697 · dump/eiglib.py:110-153 · dump/Crap_Levelbot.py:791-874

**Web:** metin2.dev/topic/28895 (stateful server sync — FUNC_WAIT final pozisyon) · elitepvpers 5318086 (Auto Hunt 2025 — SetPixelPosition+Debug) · elitepvpers 1454073 (Global Multihack — ±2000px) · elitepvpers 4701964 (packet movement) · memorybreak.com/glbot-python-api.php (ticari bot API ışınlama)

**Ek dosyalar:** `analysis/dump_inventory.json` (tam fonksiyon envanteri) · `reports/assets/diagram_flow.png` (protokol akışı) · `reports/assets/chart_dump_kategoriler.png` · `reports/assets/chart_cpp_bindings.png` · `reports/LegendySF-Dump_Derin_Analiz_Raporu.pdf` (tam 19 sayfalık PDF)
