# DEV_LOGIN_FLOW — Giriş → Karakter Seçme → Karakter Oluşturma → Bayrak → Oyuna Girme
## LegendySF-V2 Gerçek Kaynak Kodu Üzerinden Fonksiyon Karşılıkları (Hardcode Seviyesi)

> **Kaynak:** `/home/z/my-project/repos/LegendySF-V2/Legendy.Source/` (Metin2 client + server tam kaynak)
> **Amaç:** Otomasyon scriptinin giriş akışını sürmesi için gereken HER fonksiyonun gerçek oyun karşılığı, parametreleri, typedef/packet struct kullanımı, server tarafındaki handler'ı ve hata dalları.
> **Okuma:** `CLI` = ClientSource/Client/UserInterface/ · `ETC` = ClientSource/Client/EterLib/ · `SRV` = GameSource/Server/ · `PY` = Metin2Client/pack/root/ (client'ın Python scriptleri — repoda mevcut)
> **Kısaltmasız tam yol örneği:** `Legendy.Source/ClientSource/Client/UserInterface/PythonNetworkStreamPhaseSelect.cpp`

---

## 0. ÖNCE MİMARİ GERÇEKLER (yanlış varsayımları kıran 6 bulgu)

1. **5 karakter slotu var.** `SRV/common/CommonDefines.h:33` → `ENABLE_PLAYER_PER_ACCOUNT5` ve `CLI/Locale_inc.h:19`. Client tarafı `CLI/Packet.h:422` → `PLAYER_PER_ACCOUNT4 = 5` (isim 4 kalmasına rağmen değer 5). Server tarafı `PLAYER_PER_ACCOUNT` = 5.
2. **Otomasyon iki sunucuya bağlanır, tek değil.** `PY/serverinfo.py:4-41`: auth (login) sunucusu `30001` port, oyun kanalları `30003/30007/30011/30015`. `PY/constinfo.py:67` → `KEEP_ACCOUNT_CONNETION_ENABLE=1` → login AKIŞI HER ZAMAN auth sunucusu üzerinden key ile döner. Doğrudan `HEADER_CG_LOGIN` (şifreli düz login) oyun sunucusunda reddedilir: `SRV/game/src/input_login.cpp:131-137` `test_server` değilse `"VERSION"` hatası döner.
3. **PHASE_CREATE diye bir faz YOK.** Karakter oluşturma penceresi, PHASE_SELECT içinde bir UI alt penceresidir. Faz enum'u: `CLI/Packet.h:1165-1179`.
4. **`TSimplePlayer.byJob` aslında JOB değil MAIN_RACE değeridir.** Yani serverdan gelen sayı 0-8 arasıdır (sınıf+ cinsiyet birlikte). `CLI/PythonNetworkStream.cpp:407-408` bu alanı `ACCOUNT_CHARACTER_SLOT_RACE` olarak döner. Sınıfa çevirmek = `race % 4` (`CLI/InstanceBase.h:1180-1188`).
5. **Karakter seçme paketini UI değil introLoading yollar.** `PY/introselect.py` StartGame'e basınca sadece `net.DirectEnter(slot)` çağırır (yeni TCP bağlantısı kurar); asıl `net.SendSelectCharacterPacket(slot)` çağrısı `PY/introloading.py:147-148` içinde yapılır (LoadingWindow.Open sırasında). Otomasyonun "oyuna gir" komutu = `net.DirectEnter(slot)`, SONRASI client kendi kendine select paketini yollar.
6. **CRC magic cube login'de etkisiz.** `BuildProcessCRC()` PHASE_SELECT'e geçerken çağrılır (`CLI/PythonNetworkStream.cpp:642-645`) ama parçalar yalnız in-game `TPacketCGAttack` içinde tüketilir (`PythonNetworkStreamPhaseGame.cpp:2635-2636`). Login akışını otomatikleştirmek CRC'yi bozmaz.

---

## 1. FAZ / SAHNE SİSTEMİ (nerede olduğumuzu nasıl biliriz)

### 1a. Server→Client faz enum'u (`EPhase`)

Kaynak: `CLI/Packet.h:1165-1179` (server tarafında aynı değerler `DESC::SetPhase` ile kullanılır):

```cpp
enum EPhase
{
    PHASE_CLOSE         = 0,    // bağlantı kapanıyor → client login ekranına döner
    PHASE_HANDSHAKE     = 1,    // zaman senkronu / el sıkışma
    PHASE_LOGIN         = 2,    // login paketi bekleniyor
    PHASE_SELECT        = 3,    // karakter seçim ekranı
    PHASE_LOADING       = 4,    // harita/oyun yükleniyor
    PHASE_GAME          = 5,    // oyun içi
    PHASE_DEAD          = 6,
    PHASE_DBCLIENT_CONNECTING, PHASE_DBCLIENT, PHASE_P2P, PHASE_AUTH  // auth sunucu fazları
};
```

### 1b. Faz geçiş paketi ve client dağıtıcısı

| Fonksiyon | Dosya:satır | Ne yapar |
|---|---|---|
| `CPythonNetworkStream::RecvPhasePacket` | `CLI/PythonNetworkStream.cpp:621` | `TPacketGCPhase{bHeader=0xfd, bPhase}` okur; `PHASE_CLOSE`→`ClosePhase()` (:630), `PHASE_HANDSHAKE`→`SetHandShakePhase()` (:634), `PHASE_LOGIN`→`SetLoginPhase()` (:638), `PHASE_SELECT`→`SetSelectPhase()` + `BuildProcessCRC()` (:642-645), `PHASE_LOADING`→`SetLoadingPhase()` (:652), `PHASE_GAME`→`SetGamePhase()` (:656) |

**Otomasyon için anahtar:** faz değişimi = `HEADER_GC_PHASE (0xfd)` paketi. Script bunu paket seviyesinde göremez ama client C++ her faz geçişinde ilgili Python penceresini açar → **aşağıdaki phase-window mekanizmasıyla Python'dan okunur.**

### 1c. PHASE_WINDOW enum'u (Python'dan okunabilir ekran numaraları)

Kaynak: `CLI/PythonNetworkStream.h:74-81`, Python sabitleri `CLI/PythonNetworkStreamModule.cpp:2118-2124`:

| Sabit | Değer | Ekran | Python dosyası (repoda mevcut) |
|---|---|---|---|
| `net.PHASE_WINDOW_LOGO` | 0 | Logo | — |
| `net.PHASE_WINDOW_LOGIN` | 1 | Giriş ekranı | `PY/intrologin.py` (`LoginWindow`) |
| `net.PHASE_WINDOW_SELECT` | 2 | Karakter seçimi | `PY/introselect.py` (`SelectCharacterWindow`) |
| `net.PHASE_WINDOW_CREATE` | 3 | Karakter oluşturma | `PY/introcreate.py` (`CreateCharacterWindow`) |
| `net.PHASE_WINDOW_LOAD` | 4 | Yükleniyor | `PY/introloading.py` (`LoadingWindow`) |
| `net.PHASE_WINDOW_GAME` | 5 | Oyun içi | `PY/game.py` (`GameWindow`) |
| `net.PHASE_WINDOW_EMPIRE` | 6 | İmparatorluk/bayrak seçimi | `PY/introempire.py` (`SelectEmpireWindow`/`ReselectEmpireWindow`) |

Her ekran penceresi açılırken `net.SetPhaseWindow(net.PHASE_WINDOW_X, self)` çağırır (ör. `introselect.py:340`, `introempire.py:54`). C++ tarafı bunu `CPythonNetworkStream::SetPhaseWindow` (`CLI/PythonNetworkStream.cpp:364`) saklar.

**Faz sürücü zinciri (Python):** `PY/networkmodule.py:165-240` — `SetLogoPhase/SetLoginPhase/SetSelectEmpirePhase/SetReselectEmpirePhase/SetSelectCharacterPhase/SetCreateCharacterPhase/SetLoadingPhase/SetGamePhase` fonksiyonları ilgili intro*.py ekranını açar. Otomasyon `mainStream.SetSelectCharacterPhase()` gibi çağrılarla ekran arasında ZORLA geçiş yapabilir (ama LOADING sırasında ASLA — GIL analiz raporuna bak).

### 1d. Script içinden sahne okuma (hangi pencere açık?)

En güvenilir yöntem (client'ta zaten çalışan mekanizma): `MainStream.SetPhaseWindow` izlemesi. MainStream nesnesi `PY/networkmodule.py` akışında tutulur; hangi pencere açıldıysa `net.PHASE_WINDOW_*` değeriyle kaydedilir.

**C++ tarafında `net.GetPhaseWindow` diye bir glue YOK.** Script tarafında üç yol:
1. `SetPhaseWindow`'u izlemek (birebir çağrı takibi — çağrıldığında argümanlardan `PHASE_WINDOW_*` ve pencere nesnesi alınır)
2. Pencere nesnesinin tip adına bakmak: `type(phase_window).__name__ == 'SelectCharacterWindow'` → SELECT, `'LoginWindow'` → LOGIN, `'CreateCharacterWindow'` → CREATE, `'SelectEmpireWindow'`/`'ReselectEmpireWindow'` → EMPIRE, `'LoadingWindow'` → LOAD, `'GameWindow'` → GAME
3. `net.IsConnect()` (`CLI/PythonNetworkStreamModule.cpp` glue) bağlantı durumu verir; faz vermez — sadece yardımcı.

---

## 2. HANDSHAKE EVRESİ (login'den önce)

| Taraf | Fonksiyon | Dosya:satır | İmza/Parametre | Ne yapar | Paket |
|---|---|---|---|---|---|
| srv | `DESC::Setup` | `SRV/game/src/desc.cpp:237` (faz @270, `StartHandshake` @271) | `bool Setup(LPFDWATCH, socket_t, const sockaddr_in&, DWORD handle, DWORD handshake)` | Bağlantı kabulünde `PHASE_HANDSHAKE` set eder, `m_dwHandshake` üretir | gönderir `TPacketGCHandshake{bHeader=0xff, dwHandshake, dwTime, lDelta}` |
| srv | `CInputProcessor::Handshake` | `SRV/game/src/input.cpp:186` | `void Handshake(LPDESC d, const char* c_pData)` | `d->GetHandshake() == p->dwHandshake` doğrular; zaman senkron döngüsü (`DESC::HandshakeProcess`, `desc.cpp:666-717`, `HANDSHAKE_RETRY_LIMIT`); başarılıysa `SetPhase(PHASE_LOGIN)` (auth sunucuda `PHASE_AUTH`, `input.cpp:204-207`) | alır `TPacketCGHandshake`, yeniden yollar `TPacketGCHandshake` |
| cli | `CPythonNetworkStream::HandShakePhase` | `CLI/PythonNetworkStreamPhaseHandShake.cpp:14` | `void HandShakePhase(void)` | Faz döngüsü: `HEADER_GC_HANDSHAKE(0xff)` → paketi `dwTime += lDelta*2` ile geri yollar; `HEADER_GC_BINDUDP(0xfe)`; `HEADER_GC_PING(44)`; `_IMPROVED_PACKET_ENCRYPTION_` varsa `KEY_AGREEMENT` | alır/gönderir `TPacketGCHandshake` |
| cli | `CPythonNetworkStream::SetHandShakePhase` | `CLI/PythonNetworkStreamPhaseHandShake.cpp:101` | `void` | `m_strPhase="HandShake"`, `SetGameOnline()`, Python callback `"OnHandShake"` (`PY/intrologin.py:412` ses çalar) | — |
| cli | `RecvPingPacket` | `CLI/PythonNetworkStream.cpp:667` | `bool RecvPingPacket(void)` | `TPacketCGPong{bHeader=0xfe}` yanıtlar. **Otomasyon PING'e cevap vermezse server bağlantıyı kapatır** (`ping_event`, `SRV/game/src/desc.cpp:198-205`) | alır `TPacketGCPing(44)`, yollar `TPacketCGPong(0xfe)` |

**Otomasyon notu:** Bu evreyi client kendisi halleder (exe içi C++ döngü). Script'in burada işi yok; sadece handshake başarısızsa ekran `PHASE_CLOSE` ile login'e döner.

---

## 3. LOGIN EVRESİ — iki bağlantı, iki paket

Bu client'ın login akışı İKİ ayrı TCP oturumundan oluşur:

```
[A] AUTH SUNUCUSU (30001) : TPacketCGLogin3  (şifre, adwClientKey) → TPacketGCAuthSuccess{dwLoginKey}
[B] OYUN SUNUCUSU (3000x) : TPacketCGLogin2  (isim, dwLoginKey, adwClientKey) → TPacketGCEmpire + TPacketGCLoginSuccess4
```

### 3a. Client login gönderimi

| Fonksiyon | Dosya:satır | İmza | Ne yapar | Paket |
|---|---|---|---|---|
| `CPythonNetworkStream::SetLoginInfo` | `CLI/PythonNetworkStream.cpp:512` | `void SetLoginInfo(const char* c_szID, const char* c_szPassword)` | `m_stID`/`m_stPassword` saklar | — |
| `CPythonNetworkStream::SetLoginKey` | `CLI/PythonNetworkStream.cpp:523` | `void SetLoginKey(DWORD dwLoginKey)` | Auth'dan gelen key'i saklar; key != 0 ise client `SendLoginPacketNew` moduna geçer | — |
| `CPythonNetworkStream::SetLoginPhase` | `CLI/PythonNetworkStreamPhaseLogin.cpp:97` | `void` | Faz="Login"; **login'i OTOMATİK yollar**: `m_dwLoginKey != 0` → `SendLoginPacketNew` (:118-134); ardından `ClearLoginInfo()`, Python `"OnLoginStart"` (`PY/intrologin.py:418`), `__ClearSelectCharacterData()` | `HEADER_CG_LOGIN2` |
| `CPythonNetworkStream::SendLoginPacket` | `CLI/PythonNetworkStreamPhaseLogin.cpp:256` | `bool (const char* c_szName, const char* c_szPassword)` | Eski düz-şifre login — yalnız `test_server` (bakınız §0.2) | `TPacketCGLogin{header=1, name[31], pwd[17]}` |
| `CPythonNetworkStream::SendLoginPacketNew` | `CLI/PythonNetworkStreamPhaseLogin.cpp:276` | `bool (const char* c_szName, const char* c_szPassword)` | Key'li login: isim + `m_dwLoginKey` + `g_adwEncryptKey[4]`; **gönderimden sonra** şifreli moda geçer: `SetSecurityMode(true, g_adwEncryptKey, g_adwDecryptKey)` (:304-306) | `TPacketCGLogin2{header=109, name[31], DWORD login_key, DWORD adwClientKey[4]}` (client `CLI/Packet.h:581`; server `SRV/game/src/packet.h:580`) |
| `CPythonNetworkStream::__RecvLoginKeyPacket` | `CLI/PythonNetworkStreamPhaseLogin.cpp:408` | `bool` | `HEADER_GC_LOGIN_KEY(118)` → `m_dwLoginKey` saklar | `TPacketGCLoginKey{bHeader, DWORD dwLoginKey}` |

### 3b. AUTH (hesap) bağlantısı — gerçekte kullanılan yol

| Taraf | Fonksiyon | Dosya:satır | Ne yapar | Paket |
|---|---|---|---|---|
| cli | `CAccountConnector::__AuthState_RecvPhase` | `CLI/AccountConnector.cpp:229` (gönderim @310-337) | `PHASE_AUTH` gelince `TPacketCGLogin3` yollar | `HEADER_CG_LOGIN3(111)`: `TPacketCGLogin3{header=111, name[31], pwd[17], adwClientKey[4]}` |
| cli | `__AuthState_RecvAuthSuccess` | `CLI/AccountConnector.cpp:443` | `TPacketGCAuthSuccess` alır: `bResult==0` → Python `"OnLoginFailure"("BESAMEKEY")`; değilse Panama IV decrypt, `rkNet.SetLoginKey(dwLoginKey)`, **oyun kanalına yeniden bağlanır** `rkNet.Connect(game_addr)`, auth bağlantısını kapatır | `HEADER_GC_AUTH_SUCCESS(150)`: `TPacketGCAuthSuccess{dwLoginKey, bResult}` (client `Packet.h:2626`, server `packet.h:954`) |
| cli | `__AuthState_RecvAuthFailure` | `CLI/AccountConnector.cpp:501` | `TPacketGCLoginFailure.szStatus`'ı Python `"OnLoginFailure"`'a taşır | `HEADER_GC_LOGIN_FAILURE(7)` |
| cli | `__AuthState_RecvHandshake` | `CLI/AccountConnector.cpp:345` | Auth bağlantısında handshake yankısı | `TPacketGCHandshake` |
| srv(auth) | `CInputAuth::Login` | `SRV/game/src/input_auth.cpp:75` | `FN_IS_VALID_LOGIN_STRING`, `"SHUTDOWN"` (bakım), `ALREADY` (`FindByLoginName` — aynı hesap zaten bağlı), Panama key = `dwKey ^ adwClientKey[0..3]` (:123-125), SQL `QID_AUTH_LOGIN` (:183-208) | hatalarda `TPacketGCLoginFailure` |
| srv(auth) | `DBManager::QID_AUTH_LOGIN` sonuç işleyicisi | `SRV/game/src/db.cpp:682-899` | Hata merdiveni → `LoginFailure(d, ...)`: `NOID`(:713), `WRONGPWD`(:827), `NOTAVAIL`(:833), `ALREADY`(:839), `BADSCLID`(:845), `AGELIMIT`(:851), status kolonu ≠ "OK" → status kendisi (:855-860), `BLKLOGIN`(:866), billing `NOBILL`/`BLOCK`(:913/:925). Başarı → `LoginPrepare`(:889) | `TPacketGCLoginFailure{header=7, szStatus[9]}` (`LOGIN_STATUS_MAX_LEN=8`) |
| srv(auth) | `DBManager::LoginPrepare` / `SendAuthLogin` | `SRV/game/src/db.cpp:499 / :472` | Hesapta matrix kod varsa `TPacketGCMatrixCard(116)`; yoksa DB core'a `HEADER_GD_AUTH_LOGIN` | — |
| db | `CClientManager::QUERY_AUTH_LOGIN` | `SRV/db/src/ClientManager.cpp:1884` | `HEADER_DG_AUTH_LOGIN` + sonuç byte | — |
| srv | `CInputDB::AuthLogin` | `SRV/game/src/input_db.cpp:1757` | Başarıda Panama listesi + paket crypt keyleri + **`TPacketGCAuthSuccess{bHeader=150, dwLoginKey=d->GetLoginKey(), bResult=1}`** | — |

### 3c. OYUN sunucusu login'i (`CInputLogin`) ve cevabı

| Taraf | Fonksiyon | Dosya:satır | Ne yapar | Paket |
|---|---|---|---|---|
| srv | `CInputLogin::Login` | `SRV/game/src/input_login.cpp:120` | `HEADER_CG_LOGIN(1)` handler; `test_server` değilse `"VERSION"` reddi (:131-137); `SHUTDOWN`(:139-145), `FULL` kullanıcı limiti(:147-162) | `TPacketGCLoginFailure` |
| srv | `CInputLogin::LoginByKey` | `SRV/game/src/input_login.cpp:172` | `HEADER_CG_LOGIN2(109)` handler: engelli ülke IP kontrolü → `PHASE_CLOSE`(:180-191), `SHUTDOWN`/`FULL`(:193-221), `d->SetLoginKey`, `d->SetSecurityKey(adwClientKey)`; DB'ye `TPacketGDLoginByKey{szLogin, dwLoginKey, adwClientKey[4], szIP}` (:230-237) | — |
| db | `CClientManager::QUERY_LOGIN_BY_KEY` | `SRV/db/src/ClientManagerLogin.cpp:83` | key bulunamadı → `HEADER_DG_LOGIN_NOT_EXIST`; **hesap zaten oyunda** → `HEADER_DG_LOGIN_ALREADY`(:116-124); login adı uyuşmuyor → `NOT_EXIST`(:126-131); **adwClientKey uyuşmuyor → `NOT_EXIST`**(:133-144); sonra player_index yükle | — |
| srv | `CInputDB::LoginSuccess` | `SRV/game/src/input_db.cpp:112` | `pTab->status != "OK"` → `LoginFailure(d, status)`(:139-150); `GetServerLocation` ile her karaktere `lAddr/wPort` doldurur(:158); hesabı bağlar; **`TPacketGCEmpire{bHeader=90, bEmpire}`** yollar — hesapta karakter/lokasyon yoksa `number(1,3)` rastgele(:163-176), varsa `d->GetEmpire()`; sonra **`d->SetPhase(PHASE_SELECT)`**(:178) ve `d->SendLoginSuccessPacket()`(:179) | `HEADER_GC_EMPIRE(90)`, `HEADER_GC_PHASE(0xfd)`, `HEADER_GC_LOGIN_SUCCESS4(32)` |
| srv | `DESC::SendLoginSuccessPacket` | `SRV/game/src/desc.cpp:931` | **KARAKTER TABLOSU PAKETİ**: `TPacketGCLoginSuccess{bHeader=32, TSimplePlayer players[5], DWORD guild_id[5], char guild_name[5][13], DWORD handle, DWORD random_key}` (`SRV/game/src/packet.h:943-952`) | `HEADER_GC_LOGIN_SUCCESS4(32)` |
| srv | `CInputDB::LoginAlready` | `SRV/game/src/input_db.cpp:1274` | Aynı login'in eski bağlantısını koparır (`DisconnectOfSameLogin` :1286), sonra `LoginFailure(d, "ALREADY")`(:1299) | `HEADER_GC_LOGIN_FAILURE "ALREADY"` |
| cli | `CPythonNetworkStream::__RecvLoginSuccessPacket4` | `CLI/PythonNetworkStreamPhaseLogin.cpp:184` | 5× `TSimplePlayerInformation` + guild verilerini `m_akSimplePlayerInfo[]`'a kopyalar; Python `PHASE_WINDOW_SELECT` → `"Refresh"` çağırır (:206) — **bu pak repoda `introselect.py:780`'de Refresh bilinçli no-op; pencere açılırken slotları kendisi okur (§4b)** | `HEADER_GC_LOGIN_SUCCESS4(32)` |
| cli | `CPythonNetworkStream::__RecvLoginFailurePacket` | `CLI/PythonNetworkStreamPhaseLogin.cpp:226` | Python `PHASE_WINDOW_LOGIN` → `"OnLoginFailure"(szStatus)` (`PY/intrologin.py:422` → `loginFailureMsgDict` :179-198) | `TPacketGCLoginFailure` |
| cli | `OnConnectFailure` | `CLI/PythonNetworkStreamPhaseLogin.cpp:213` | Python `"OnConnectFailure"` (`PY/intrologin.py:394`) | — |

### 3d. Client'ın anladığı login hata kodları (TAM LİSTE)

Kaynak: `PY/intrologin.py:179-198` (`loginFailureMsgDict`):

| Kod | Anlam | Kaynak noktası |
|---|---|---|
| `ALREADY` | Hesap zaten oyunda | db.cpp:839 / LoginAlready input_db.cpp:1274 |
| `NOID` | Hesap yok | db.cpp:713 |
| `WRONGPWD` | Şifre yanlış | db.cpp:827 |
| `FULL` | Sunucu dolu | input_login.cpp:147-162 |
| `SHUTDOWN` | Sunucu bakımda | input_login.cpp:139-145 / input_auth.cpp |
| `REPAIR` | Onarım gerekli | db.cpp ladder |
| `BLOCK` | Hesap bloklu (billing) | db.cpp:925 |
| `WRONGMAT` | Matrix kart cevabı yanlış | matrix akışı |
| `QUIT` | Çıkış | ladder |
| `BESAMEKEY` | Auth success bResult=0 (key verilemedi) | AccountConnector.cpp:443 |
| `NOTAVAIL` | Hesap kullanılamaz | db.cpp:833 |
| `NOBILL` | Ödeme yok | db.cpp:913 |
| `BLKLOGIN` | Login bloklu | db.cpp:866 |
| `WEBBLK` | Web bloku | ladder |
| `BADSCLID` | SCL id hatalı | db.cpp:845 |
| `AGELIMIT` | Yaş limiti | db.cpp:851 |
| *(bilinmeyen)* | `LOGIN_FAILURE_UNKNOWN + kod` | intrologin.py fallback |

**Otomasyon cevap izleme özeti:** giriş başarılı sinyali = `HEADER_GC_LOGIN_SUCCESS4(32)` (Python'da pencere `PHASE_WINDOW_SELECT` açılır) + öncesinde `TPacketGCEmpire(90)`; başarısızlık sinyali = `OnLoginFailure(kod)` callback'i ya da ekranın LOGIN penceresinde kalması + popup metni.

---

## 4. KARAKTER SEÇME EVRESİ (PHASE_SELECT)

### 4a. Karakter tablosu struct'ı — `TSimplePlayerInformation` (client) / `TSimplePlayer` (server)

Client: `CLI/Packet.h:1219-1242` · Server karşılığı: `SRV/common/tables.h:347-369`. Alanlar birebir eşleşmek zorunda (`ENABLE_OFFICAL_CHARACTER_SCREEN` iki tarafta da açık → `dwLastPlayTime` alanı var):

```cpp
typedef struct SSimplePlayerInformation
{
    DWORD dwID;              // player id (0 = slot BOŞ)
    char  szName[25];        // karakter adı
    BYTE  byJob;             // DİKKAT: JOB değil, MAIN_RACE değeri (0-8, §6a'ya bak)
    BYTE  byLevel;           // level
    DWORD dwPlayMinutes;
    DWORD dwLastPlayTime;    // ENABLE_OFFICAL_CHARACTER_SCREEN
    BYTE  byST, byHT, byDX, byIQ;   // statlar (STR/DEX/VIT/INT)
    WORD  wMainPart;         // zırh görünümü (part)
    BYTE  bChangeName;       // 1 ise isim değişikliği zorunlu → seçim sessizce reddedilir (§4d)
    WORD  wHairPart;         // saç
    WORD  wAccePart;         // ENABLE_ACCE_SYSTEM
    BYTE  bDummy[4];
    long  x, y;              // spawn koordinatı
    LONG  lAddr;             // kanal sunucu IP (dolduran: CInputDB::LoginSuccess:158)
    WORD  wPort;             // kanal sunucu port
    BYTE  bySkillGroup;      // 1/2 beceri grubu
} TSimplePlayerInformation;
```

### 4b. Listeyi PYTHON'dan okuma — otomasyonun asıl API'si

Glue: `net.GetAccountCharacterSlotDataInteger(slot, type)` → `CLI/PythonNetworkStreamModule.cpp:164`, `net.GetAccountCharacterSlotDataString(slot, type)` → `:179`. Erişimciler `CLI/PythonNetworkStream.cpp:396 / :451`.

`ACCOUNT_CHARACTER_SLOT_*` enum'u — `CLI/PythonNetworkStream.h:45-70` (Python sabitleri `PythonNetworkStreamModule.cpp:2126-2149`):

| Sabit | Değer | Alan | Tip |
|---|---|---|---|
| `ACCOUNT_CHARACTER_SLOT_ID` | 0 | `dwID` | int (0 = slot boş) |
| `ACCOUNT_CHARACTER_SLOT_NAME` | 1 | `szName` | string |
| `ACCOUNT_CHARACTER_SLOT_RACE` | 2 | `byJob` (**MAIN_RACE 0-8**) | int |
| `ACCOUNT_CHARACTER_SLOT_LEVEL` | 3 | `byLevel` | int |
| `ACCOUNT_CHARACTER_SLOT_STR` | 4 | `byST` | int |
| `ACCOUNT_CHARACTER_SLOT_DEX` | 5 | `byDX` | int |
| `ACCOUNT_CHARACTER_SLOT_HTH` | 6 | `byHT` | int |
| `ACCOUNT_CHARACTER_SLOT_INT` | 7 | `byIQ` | int |
| `ACCOUNT_CHARACTER_SLOT_PLAYTIME` | 8 | `dwPlayMinutes` | int |
| `ACCOUNT_CHARACTER_SLOT_FORM` | 9 | `wMainPart` | int |
| `ACCOUNT_CHARACTER_SLOT_ADDR` | 10 | `lAddr` | int (IP dword) |
| `ACCOUNT_CHARACTER_SLOT_PORT` | 11 | `wPort` | int |
| `ACCOUNT_CHARACTER_SLOT_GUILD_ID` | 12 | `guild_id` | int |
| `ACCOUNT_CHARACTER_SLOT_GUILD_NAME` | 13 | `guild_name` | string |
| `ACCOUNT_CHARACTER_SLOT_CHANGE_NAME_FLAG` | 14 | `bChangeName` | int |
| `ACCOUNT_CHARACTER_SLOT_HAIR` | 15 | `wHairPart` | int |
| `ACCOUNT_CHARACTER_SLOT_ACCE` | 16 | `wAccePart` | int |
| `ACCOUNT_CHARACTER_SLOT_LAST_PLAYTIME` | 17 | `dwLastPlayTime` | int |

**Karakter listesi / sayısı / sınıfı / leveli okuma — referans client kodu** (`PY/introselect.py:115-171`, `MyCharacters.LoadCharacterData`):

```python
# PY/introselect.py:119-138 (birebir — bu OTOMASYONUN okuma deseni)
for i in xrange(CHARACTER_SLOT_COUNT_MAX):        # 5  (introselect.py:37)
        pid = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)
        if not pid:
                self.EmptySlot.append(i); continue        # slot BOŞ
        name  = net.GetAccountCharacterSlotDataString (i, net.ACCOUNT_CHARACTER_SLOT_NAME)
        level = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
        race  = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_RACE)  # MAIN_RACE
        form  = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_FORM)
        ...
```

- **Kaç karakter var:** `pid != 0` olan slot sayısı. **Boş slotlar:** `EmptySlot` listesi (create için kullanılacak).
- **Sınıf (ninja mı sura mı):** `chr.RaceToJob(race)` — glue `PY/playersettingmodule.py` + C++ `RaceToJob` (`CLI/InstanceBase.h:1180-1188`) = `race % 4` (8 ise 4=wolfman). JOB enum: `JOB_WARRIOR=0, JOB_ASSASSIN=1 (ninja), JOB_SURA=2, JOB_SHAMAN=3, JOB_WOLFMAN=4` (`PY/playersettingmodule.py:14-19`; server `SRV/common/length.h:201-211`).
- **Cinsiyet:** `RaceToSex(race)` (`CLI/InstanceBase.h:1190-1210`) — race değeri cinsiyeti içinde taşır (§6a tablosu).
- Not: `player.GetStatus/GetName/GetJob` (`CLI/PythonPlayerModule.cpp:2530-2542`) OYUN İÇİ erişimcileridir; seçim ekranında çalışmaz.

### 4c. Karakter seçme / silme paketleri

| Taraf | Fonksiyon | Dosya:satır | İmza | Paket | Not |
|---|---|---|---|---|---|
| cli | `CPythonNetworkStream::SendSelectCharacterPacket` | `CLI/PythonNetworkStreamPhaseSelect.cpp:165` | `bool SendSelectCharacterPacket(BYTE Index)` | `TPacketCGSelectCharacter{header=6, player_index}` (server adı `TPacketCGPlayerSelect`, `SRV/game/src/packet.h:622`) | glue `netSendSelectCharacterPacket` `PythonNetworkStreamModule.cpp:484`; **çağıran `PY/introloading.py:147-148` (introselect değil!)** |
| cli | `CPythonNetworkStream::SendDestroyCharacterPacket` | `CLI/PythonNetworkStreamPhaseSelect.cpp:181` | `bool (BYTE index, const char* szPrivateCode)` | `TPacketCGDestroyCharacter{header=5, index, char szPrivateCode[8]}` (`PRIVATE_CODE_LENGTH=8`, `Packet.h:450`) | glue `:649`; çağıran `PY/introselect.py:841` (sosyal kod diyalogu: `PopupDeleteQuestion` → `InputPrivateCode` → `AcceptInputPrivateCode` — chardeleter_result.txt ile kanıtlanmış akış) |
| cli | `__RecvPlayerDestroySuccessPacket` | `CLI/PythonNetworkStreamPhaseSelect.cpp:268` | — | `TPacketGCDestroyCharacterSuccess{header=10, BYTE account_index}` → Python `"OnDeleteSuccess"(i)` (`introselect.py:854`) | slotu temizler |
| cli | `__RecvPlayerDestroyFailurePacket` | `CLI/PythonNetworkStreamPhaseSelect.cpp:282` | — | `HEADER_GC_PLAYER_DELETE_WRONG_SOCIAL_ID(11)` → Python `"OnDeleteFailure"` | sosyal kod yanlış |
| srv | `CInputLogin::CharacterSelect` | `SRV/game/src/input_login.cpp:270` | — | hesap bağlı mı kontrolü(:277), `index < PLAYER_PER_ACCOUNT(=5)`(:283), **`bChangeName` flag'liyse SESSİZCE reddedilir**(:289-294 — cevap paketi YOK, client loading'de asılı kalır) | `TPlayerLoadPacket{account_id, player_id, account_index}` → `HEADER_GD_PLAYER_LOAD`(:296-302); yönlendirme `Analyze:1063` (`HEADER_CG_CHARACTER_SELECT=6`) |
| srv | `CInputDB::PlayerLoad` | `SRV/game/src/input_db.cpp:348` | — | spawn çözümü (`GetValidLocation`, imparatorluk-köyü fallback :382-393), `CreateCharacter`+`BindDesc`(:412-418), P2P login duyurusu, **`d->SetPhase(PHASE_LOADING)`**(:449) + `ch->MainCharacterPacket()`(:450), `PointsPacket()`, `SkillLevelPacket()`, SDB/HybridCrypt(:454-459), HackShield/XTrap oturumu(:494-506). Harita `map_allow` dışında → köye warp + `PHASE_CLOSE`(:461-472) | `HEADER_GC_MAIN_CHARACTER2_EMPIRE(113)`, `HEADER_GC_PHASE(PHASE_LOADING)` |

### 4d. Server select hata/kenar dalları

- Slot boş / index kötü → `sys_err` yazılır ve **CEVAP PAKETİ YOK** (`input_login.cpp:277-287`) → client loading'de asılı kalır (otomasyon buna timeout koymalı).
- `bChangeName==1` → cevap YOK (`:289-294`); client seçim ekranı isim-değiştir diyaloğu açar (`introselect.py:738-741`, `net.SendChangeNamePacket` → `CInputLogin::ChangeName` `input_login.cpp:240` → `HEADER_GD_CHANGE_NAME` → `CInputDB::ChangeName` `input_db.cpp:318` → `TPacketGCChangeName{header=107, DWORD pid, name[25]}` → client `__RecvChangeName` `PhaseSelect.cpp:292` → `"OnChangeName"`).

---

## 5. EMPIRE (BAYRAK/İMPARATORLUK) SEÇİMİ

**Ne zaman gerekir:** Hesabın HİÇ karakteri yoksa. Server her login-success'ta `TPacketGCEmpire` yollar (`input_db.cpp:163-176`); karar client UI'dadır: `introselect.Open()` 0 karakter görünce `stream.SetCharacterSlot(emptySlot); self.SelectEmpire=True` (`introselect.py:519-521`) → `OnUpdate` → `SetReselectEmpirePhase` → introEmpire ekranı → seçim → `net.SendSelectEmpirePacket`.

| Taraf | Fonksiyon | Dosya:satır | İmza / struct | Ne yapar | Paket |
|---|---|---|---|---|---|
| cli | `CPythonNetworkStream::SendSelectEmpirePacket` | `CLI/PythonNetworkStreamPhaseSelect.cpp:149` | `bool SendSelectEmpirePacket(DWORD dwEmpireID)` | Bayrak seçimini yollar ve yerelde `SetEmpireID(dwEmpireID)` yapar | `TPacketCGEmpire{bHeader=90, bEmpire}` (client `Packet.h:2302`; server `packet.h:1777`) |
| cli | `CPythonNetworkStream::__RecvEmpirePacket` | `CLI/PythonNetworkStreamPhaseLogin.cpp:146` (ayrıca SelectPhase `PhaseSelect.cpp:59-62`) | — | `m_dwEmpireID` saklar (başlangıç 0, ctor `PythonNetworkStream.cpp:898`) | `TPacketGCEmpire{bHeader=90, bEmpire}` |
| cli | `CPythonNetworkStream::IsSelectedEmpire` | `CLI/PythonNetworkStream.cpp:388` | — | `m_dwEmpireID != 0` → `SetSelectPhase` bununla `SetSelectCharacterPhase` mi `SetSelectEmpirePhase` mi çağıracağına karar verir (`PhaseSelect.cpp:34-38`) | — |
| py | `net.SendSelectEmpirePacket(empire)` | glue `CLI/PythonNetworkStreamModule.cpp:413` | — | Çağıranlar: `PY/introempire.py:247` (taze hesap) ve `:334` (`ReselectEmpireWindow`); pencere varsayılanı `empireID=app.GetRandom(1,3)` (`introempire.py:57`), sol/sağ butonlar 1↔3 dolaştırır (:232-244) | `HEADER_CG_EMPIRE(90)` |
| srv | `CInputLogin::Empire` | `SRV/game/src/input_login.cpp:839` | — | `bEmpire >= EMPIRE_MAX_NUM(4)` → `PHASE_CLOSE`(:843-847); **hesapta karakter varsa SESSİZCE döner** (`r.bEmpire != 0` iken tüm `players[i].dwID == 0` zorunlu, :849-861); DB'ye `TEmpireSelectPacket{dwAccountID, bEmpire}` → `HEADER_GD_EMPIRE_SELECT`(:863-868) | — |
| db | `CClientManager::QUERY_EMPIRE_SELECT` | `SRV/db/src/ClientManager.cpp:1112` | — | `UPDATE player_index SET empire=N`; tüm pid'leri imparatorluk köyüne ışınlar (`g_start_map`: 1/21/41, `g_start_position`, :1140-1176); `HEADER_DG_EMPIRE_SELECT` + empire byte(:1180-1181) | — |
| srv | `CInputDB::EmpireSelect` | `SRV/game/src/input_db.cpp:1302` | — | `rTable.bEmpire` set, `TPacketGCEmpire(90)` yollar, oyuncu başlangıç koordinatlarını düzeltir, `GetServerLocation`, **`d->SendLoginSuccessPacket()`** → client LoginSuccess4'ü TEKRAR alır (5 boş slot) → create penceresine akar | `HEADER_GC_EMPIRE`, `HEADER_GC_LOGIN_SUCCESS4(32)` |

**Bayrak değerleri:** `EMPIRE_A=1 (Shinsoo/Kırmızı), EMPIRE_B=2 (Chunjo/Sarı), EMPIRE_C=3 (Jinno/Mavi)` — client sabitleri `CLI/PythonNetworkStreamModule.cpp:2155-2157`; server `EMPIRE_MAX_NUM=4` (`SRV/common/length.h:31`).

**Bayrak listesini görme / seçme (UI yolu):** `introempire.py` — `ew.OnSelectEmpire(id)` / `EmpireButton.IsShow()/CallEvent()` / `ClickSelectButton()` akışı scriptlerce kullanılıyor (`maximum_log` kanıtlı: "SelectEmpire OK"). **Paket yolu (doğrudan):** `net.SendSelectEmpirePacket(1|2|3)` — server tarafı tek kontrolü "0 karakter" şartı.

**"Sonraki pencereye geçti mi" kontrolü:** seçimden sonra server `LoginSuccess4`'ü yeniden yollar → client SELECT ekranına döner → bu kez 0 karakter + empire kayıtlı olduğundan `CreateCharacterButton` görünür olur (`introselect.py:709-726`). Yani geçiş kanıtı = pencerenin `SelectCharacterWindow`'a dönmesi.

---

## 6. KARAKTER OLUŞTURMA AKIŞI

### 6a. Enum'lar — TAM DEĞERLER (hardcode)

**MAIN_RACE** (paketteki `job` alanına yazılan değer; `CLI/PythonPlayer.cpp:10-24` == `SRV/game/src/char.h:50-64`):

| Değer | Sabit | Anlam |
|---|---|---|
| 0 | `MAIN_RACE_WARRIOR_M` | Erkek Savaşçı |
| 1 | `MAIN_RACE_ASSASSIN_W` | Kadın Ninja |
| 2 | `MAIN_RACE_SURA_M` | Erkek Sura |
| 3 | `MAIN_RACE_SHAMAN_W` | Kadın Şaman |
| 4 | `MAIN_RACE_WARRIOR_W` | Kadın Savaşçı |
| 5 | `MAIN_RACE_ASSASSIN_M` | Erkek Ninja |
| 6 | `MAIN_RACE_SURA_W` | Kadın Sura |
| 7 | `MAIN_RACE_SHAMAN_M` | Erkek Şaman |
| 8 | `MAIN_RACE_WOLFMAN_M` | Erkek Wolfman (`ENABLE_WOLFMAN_CHARACTER`) |

Python karşılıkları: `PY/playersettingmodule.py:21-30` (`RACE_WARRIOR_M=0 … RACE_WOLFMAN_M=8`).

**SHAPE = cinsiyet DEĞİL, zırh gövde varyantı:** create penceresindeki cinsiyet butonları RACE'i seçer (`M2_CONST_ID[job][MAN=0/WOMAN=1]`, `PY/introcreate.py:19-20, 40-46`); shape butonları `shape` 0/1 yollar (`SelectShape` `introcreate.py:583`; server `shape > 1` reddeder `input_login.cpp:505`, `part_base` olarak saklar `:450`).

**Create paketi** `TPacketCGCreateCharacter` (client `CLI/Packet.h:1284-1295`; server adı `command_player_create` → `TPacketCGPlayerCreate`, `SRV/game/src/packet.h:635-646`):

```cpp
typedef struct SPacketCGCreateCharacter
{
    BYTE header;      // 4  = HEADER_CG_CHARACTER_CREATE
    BYTE index;       // slot (0..4)
    char name[25];    // istenen karakter adı
    WORD job;         // MAIN_RACE değeri (0..8)  ← "cins" buradan
    BYTE shape;       // 0/1 zırh varyantı
    BYTE CON; BYTE INT; BYTE STR; BYTE DEX;   // server İHMAL EDER (aşağıda)
} TPacketCGCreateCharacter;
```

### 6b. Client akışı (`PY/introcreate.py`)

- **Oluştur butonu** `CreateCharacterButton` `introcreate.py:622-645`: isim kontrolleri (`CheckCreateCharacterName` :667-680: boş değil, GM adı değil, `net.IsInsultIn(name)` değil), sonra:

```python
# introcreate.py:633-642 (birebir)
chrSlot    = self.stream.GetCharacterSlot()
raceIndex  = self.M2_CONST_ID[self.job_id][self.gender]     # 0..8 MAIN_RACE
shapeIndex = self.shape                                      # 0/1
statCon/statInt/statStr/statDex = self.M2STATPOINT[self.job_id][0..3]
net.SendCreateCharacterPacket(chrSlot, textName, raceIndex, shapeIndex,
                              statCon, statInt, statStr, statDex)
```

- Glue: `netSendCreateCharacterPacket` `CLI/PythonNetworkStreamModule.cpp:610-647` (0<=index<=3 doğrulaması **|| hatası** içeriyor → fiilen doğrulama yok; `CPythonNetworkStream::SendCreateCharacterPacket` `CLI/PythonNetworkStreamPhaseSelect.cpp:198`'e iletiyor).
- **Sıra:** empire ÖNCE (yalnız 0 karakter şartıyla, §5), create SONRA.

### 6c. Server mantığı — KAPI KAPI (tam zincir)

| Kapı | Fonksiyon:satır | Detay |
|---|---|---|
| Alım | `CInputLogin::CharacterCreate` `SRV/game/src/input_login.cpp:478` | `HEADER_CG_CHARACTER_CREATE(4)`, yönlendirme `Analyze:1067` |
| 1 | `:493-497` | `g_BlockCharCreation` config → `TPacketGCCreateFailure{header=9, bType=0}` |
| 2 | `:499-503` | **isim uzunluğu > 12** (`@DsProject17`) → failure bType=0 |
| 3 | `:505-509` | `!check_name(name)` veya `shape > 1` → bType=0. `check_name` locale fn (`SRV/game/src/locale_service.cpp`): `check_name_latin1 :271` (min 2 karakter, harf+rakam+ÄÖÜß), `check_name_alphabet :317`, ortak kuyruk `check_name_independent :86` (banlı kelimeler + MOB adları reddi) |
| 4 | `:513-521` | isim == hesap login adı → **bType=1** |
| Tablo | `NewPlayerTable2` `:425-476` | `job >= MAIN_RACE_MAX_NUM` → fail; `RaceToJob(job)` (= job%4); `level=1`, `part_base=shape`; **statlar/hp/sp `JobInitialPoints`'tan** (`SRV/game/src/constants.cpp:4-25`) — **client'in gönderdiği CON/INT/STR/DEX İHMAL EDİLİR**; spawn = `CREATE_START_X/Y(empire) ± 300` |
| İleri | `:523-544` | `TPlayerCreatePacket` → `HEADER_GD_PLAYER_CREATE` |
| DB | `CClientManager::__QUERY_PLAYER_CREATE` `SRV/db/src/ClientManagerPlayer.cpp:832` | **anti-flood: hesap başına 1 create / 30 sn** → `HEADER_DG_PLAYER_CREATE_FAILED`(:839-850); slot `pidN` doluysa → `HEADER_DG_PLAYER_CREATE_ALREADY`(:868-873); **`SELECT COUNT(*) FROM player WHERE name=` → isim mevcut → `HEADER_DG_PLAYER_CREATE_ALREADY`**(:901-906); INSERT player + `UPDATE player_index SET pidN` (insert fail → ALREADY :960-965, index update fail → FAILED :969-982); başarı → `TPacketDGCreateSuccess{bAccountCharacterIndex, TSimplePlayer player}` (`SRV/common/tables.h:382-386`) |
| Cevap-OK | `CInputDB::PlayerCreateSuccess` `SRV/game/src/input_db.cpp:200` | `lAddr/wPort` doldurur (`CMapLocation`), desc hesap tablosunu günceller, **`TPacketGCPlayerCreateSuccess{header=8, BYTE bAccountCharacterIndex, TSimplePlayer player}`** (`HEADER_GC_CHARACTER_CREATE_SUCCESS`) |
| Cevap-FAIL | `CInputDB::PlayerCreateFailure` `SRV/game/src/input_db.cpp:187` | **`TPacketGCCreateFailure{header=9, BYTE bType}`** — **bType 0 = genel** (bloklu/uzunluk/karakter-hatası/db fail/30-sn bekleme), **bType 1 = isim zaten mevcut** (ya da isim==login, ya da slot dolu) |

### 6d. Client'ta sonucun görünmesi (HATA TAKİBİ)

- **Başarı:** `__RecvPlayerCreateSuccessPacket` `CLI/PythonNetworkStreamPhaseSelect.cpp:237-254` → slot verisi saklanır → Python `PHASE_WINDOW_CREATE` `"OnCreateSuccess"` (`introcreate.py:453` `createSuccess=True`) → 2 sn animasyon sonrası `OnUpdate` :744-749 → `stream.SetSelectCharacterPhase()` ile seçim ekranına döner.
- **Hata:** `__RecvPlayerCreateFailurePacket` `CLI/PythonNetworkStreamPhaseSelect.cpp:256-266` → `"OnCreateFailure"(bType)` CREATE ve SELECT pencerelerinin ikisine de yollanır → `introcreate.py:457-469`:
  - `bType == 1` → `localeInfo.CREATE_EXIST_SAME_NAME` ("Bu ismi zaten başka bir karakter kullanıyor." — `pack/locale/locale/tr/locale_game.txt:286`)
  - **diğer her bType** → `CREATE_FAILURE` ("Karakteri yaratamazsın." — `locale_game.txt:287`)
- **Slot dolu** (5/5) client'ta gönderimden ÖNCE yakalanır: `CREATE_FULL` ("Başka karakter oluşturamazsın." — `locale_game.txt:288`, gösteren `introselect.py:712-715`).

**Otomasyon hata izleme önerisi (hook'suz):** create komutundan sonra slot tablosunu yokla — `net.GetAccountCharacterSlotDataInteger(slot, ID) != 0` olduysa BAŞARILI; N saniye sonra hâlâ 0 ise HATA (sebep ayrımı için UI popup metni okunabilir ya da sayısal ayrım `bType` gerekiyorsa tek seferlik izleme penceresi `OnCreateFailure`'a takılabilir — MaxExecutor'da state-yoklaması yeterli).

---

## 7. SEÇME → OYUNA GİRME (select → loading → game)

| Adım | Fonksiyon | Dosya:satır | Ne yapar | Paket |
|---|---|---|---|---|
| 1 | `CPythonNetworkStream::ConnectGameServer` | `CLI/PythonNetworkStream.cpp:499` | `net.DirectEnter(slot)` glue (`PythonNetworkStreamModule.cpp:473`) → `m_dwSelectedCharacterIndex` saklanır, `__DirectEnterMode_Set(slot)`(:827), `CNetworkStream::Connect(lAddr, wPort)` — slotun `TSimplePlayerInformation`'ından gelen KANAL sunucusuna | yeni TCP oturumu |
| 2 | `CPythonNetworkStream::SetSelectPhase` (2. login, direct mod) | `CLI/PythonNetworkStreamPhaseSelect.cpp:9-39` | Yeni bağlantıda handshake + `SendLoginPacketNew` (otomatik, `SetLoginPhase:118-121`) ve 2. `PHASE_SELECT`: `__DirectEnterMode_IsSet()` → Python `"SetLoadingPhase"` handler'ı(:28-31) → `introLoading.LoadingWindow.Open()` | — |
| 3 | `introLoading.Open` | `PY/introloading.py:147-148` | **Karakter seçme paketini burada yollar**: `chrSlot=self.stream.GetCharacterSlot(); net.SendSelectCharacterPacket(chrSlot)` | `TPacketCGSelectCharacter{header=6, player_index}` |
| 4 | `CInputLogin::CharacterSelect` → `CInputDB::PlayerLoad` | `input_login.cpp:270` → `input_db.cpp:348` | Oyuncu yüklenir, `SetPhase(PHASE_LOADING)`, `ch->MainCharacterPacket()` | `HEADER_GC_PHASE(0xfd, PHASE_LOADING)`; `TPacketGCMainCharacter2_EMPIRE{header=113, DWORD dwVID, WORD wRaceNum, char szName[25], long lX,lY,lZ, BYTE byEmpire, BYTE bySkillGroup}` (`SRV/game/src/packet.h:1106-1151`; client `Packet.h:1547-1556`); + `HEADER_GC_CHARACTER_POINTS(16)`, `HEADER_GC_SKILL_LEVEL(76)` |
| 5 | `RecvMainCharacter2_EMPIRE` | `CLI/PythonNetworkStreamPhaseLoading.cpp:223-246` | Ana aktör VID/race/empire/skillgroup saklanır, `rkPlayer.SetName/SetMainCharacterIndex`, Python `PHASE_WINDOW_LOAD` → **`"LoadData"(x, y)`**(:240), ardından `SendClientVersionPacket()`(:244) | alır 113; yollar versiyon |
| 6 | `CPythonNetworkStream::SendClientVersionPacket` | `CLI/PythonNetworkStreamPhaseGame.cpp:4236-4270` | EU locale'lerde `TPacketCGClientVersion2{header=0xf1, filename[33], timestamp[33]="1215955205"}`; değilse `TPacketCGClientVersion{header=0xfd, ...}` | `HEADER_CG_CLIENT_VERSION(0xfd)` |
| 6s | `CInputProcessor::Version` | `SRV/game/src/input.cpp:216-224` | `d->SetClientVersion(timestamp)`; `g_bCheckClientVersion` açıksa `Entergame`'de zorlanır (`input_login.cpp:683-707`; uyuşmazlık → notice + `DelayedDisconnect(0)` + `HackLog("VERSION_CONFLICT")`) — **otomasyon doğru versiyon stringini yollamalı (client kendi yollar)** | — |
| 7 | `introLoading.LoadData(x,y)` | `PY/introloading.py:203-…` | Yükleme adımları; `__LoadMap` → `net.Warp(x,y)`(:335-336); sonunda `__StartGame` → `net.StartGame()`(:386) | — |
| 8 | `CPythonNetworkStream::StartGame` | `CLI/PythonNetworkStreamPhaseLoading.cpp:343` | `m_isStartGame=TRUE` → `OnProcess` tüketir (`PythonNetworkStream.cpp:700-708`) → Python `"SetGamePhase"` → `game.GameWindow.Open()` | — |
| 9 | `game.py GameWindow.Open` | `PY/game.py:204` | **`net.SendEnterGamePacket()`** → glue `netSendEnterGamePacket` (`PythonNetworkStreamModule.cpp:667`) → `CPythonNetworkStream::SendEnterGame` (`PhaseLoading.cpp:348-365`) | `TPacketCGEnterFrontGame{header=10}` = `HEADER_CG_ENTERGAME` |
| 10 | `CInputLogin::Entergame` | `SRV/game/src/input_login.cpp:592-837` | `d->GetCharacter()` yoksa `PHASE_CLOSE`(:596-600); konum düzeltme; `ch->Show(...)`(:620); **`d->SetPhase(PHASE_GAME)`**(:625); PVP listesi, messenger login, land listesi, **`TPacketGCTime{header=106, time}`**(:658-661), **`TPacketGCChannel{header=121, channel}`**(:663-666), karşılama, premium etkiler, versiyon kontrolü, at, savaş alanı duyurusu | `HEADER_GC_PHASE(PHASE_GAME)`, `HEADER_GC_TIME`, `HEADER_GC_CHANNEL` |
| 11 | `CPythonNetworkStream::SetGamePhase` | `CLI/PythonNetworkStreamPhaseGame.cpp:897-917` | Phase="Game"; `rkPlayer.SetMainCharacterIndex(GetMainActorVID())`, `__RefreshStatus()` → oyun tamamen canlı. **Python'dan "oyundayım" sinyali:** pencere `GameWindow` (PHASE_WINDOW_GAME) + `net.IsConnect()`; ayrı bir `net.IsInGame` glue YOK | — |

### ⚠️ ÇİFT GİRİŞ YASAĞI (NPC-yüklenmeme hatasının kökü)

`net.DirectEnter(slot)` çağrısı **TEK BAŞINA yeterli** ve client zaten: yeni bağlantı kurar → 2. login'i kendisi yapar → `SetLoadingPhase` → `SendSelectCharacterPacket` → yükleme → `SendEnterGamePacket` zincirinin TAMAMINI kendi yürütür (adım 2→11). Otomasyon `StartGame()` (UI yolu) + `net.DirectEnter()`'i PEŞ PEŞE çağırırsa (mevcut scriptlerdeki gibi — 0.1 sn arayla) select+enter dizisi İKİ KEZ gider; ikinci giriş ilk girişin faz geçişini/spawn akışını bozar → **NPC'ler görünmez**. Doğrusu: YA `sw.StartGame()` (UI) YA `net.DirectEnter(sl)` (paket) — asla ikisi birden. (C++ tarafındaki `Controller.h:1199-1212` zaten yalnız `net.DirectEnter` yapıyor — doğrulanmış doğru şekil.)

---

## 8. ANTI-CHEAT / CRC / VERSİYON — login yolunda ne var?

| Mekanizma | Yer | Login yolunda etkili mi? |
|---|---|---|
| **CRC magic cube** | `CLI/ProcessCRC.cpp:96 BuildProcessCRC()` — `PHASE_SELECT`'te bir kez çağrılır (`PythonNetworkStream.cpp:642-645`); `abCRCMagicCube[8]` = exe bellek-CRC + dosya-CRC, `abCRCXorTable{102,30,188,44,39,201,43,5}` ile XOR (`ProcessCRC.cpp:5-6`) | **Hayır.** Parçalar yalnız in-game `TPacketCGAttack.bCRCMagicCubeProcPiece/bCRCMagicCubeFilePiece` içinde tüketilir (`PythonNetworkStreamPhaseGame.cpp:2635-2636`). HK/TW locale'lerde kurulmaz bile (`ProcessCRC.cpp:98-103`). Login otomasyonunu etkilemez. |
| `__SendCRCReportPacket` (`HEADER_CG_CRC_REPORT=103`) | `CLI/PythonNetworkStreamPhaseGame.cpp:4207-4234` — **gövde tamamen yorum satırı (no-op)** | ölü kod |
| **Sequence sistemi** | Client `SendSequence()` 32768 girişli tablodan byte ekler (`ETC/NetStream.cpp:838-854`, tablo @889); `net.SetPacketSequenceMode()` (`PythonNetworkStreamModule.cpp:1706`) ile bağlantı bazında açılır — `PY/intrologin.py:664-665` (`constInfo.SEQUENCE_PACKET_ENABLE=1`) | Server'da `ENABLE_SEQUENCE_SYSTEM` **KAPALI** (`SRV/common/CommonDefines.h:13`) → fazladan byte yok sayılır. Otomasyona zararı yok. |
| **Şifreleme** | Handshake'te statik key: `SetSecurityMode(true, LocaleService_GetSecurityKey())` (`PhaseLogin.cpp:99-102`). `SendLoginPacketNew` sonrası gerçek keyler `g_adwEncryptKey/DecryptKey` (`PhaseLogin.cpp:285-306`; server yansıması `d->SetSecurityKey` `input_login.cpp:227`; server varsayılan `"1234abcd5678efgh"` `desc.cpp:265-266`). `_IMPROVED_PACKET_ENCRYPTION_` (ECDH) iki tarafta derliyse KEY_AGREEMENT devrede | Otomasyon paket seviyesine inerse: handshake key statik, login2 `adwClientKey[4]` auth anında saklanan keyle birebir aynı OLMALI. UI/paket-üstü yöntemlerde (DirectEnter, CallEvent) konu yok — client kendi keylerini kullanır. |
| **Login-key + client-key bağlama** | Auth `dwLoginKey` verir; DB core `QUERY_LOGIN_BY_KEY` `adwClientKey` karşılaştırır (`SRV/db/src/ClientManagerLogin.cpp:133-144`) | Aynı 4 DWORD client key hem `HEADER_CG_LOGIN3` (auth) hem `HEADER_CG_LOGIN2` (oyun) içinde olmalı — client bunu otomatik yapar. |
| HackShield / XTrap | `RecvHSCheckRequest`/`RecvXTrapVerifyRequest` (`PhaseHandShake.cpp:269/:309`), server `CXTrapManager::CreateClientSession` `PlayerLoad`'ta (`input_db.cpp:506`), `HEADER_CG_XTRAP_ACK(204)` `input_login.cpp:1141-1146` | define'a bağlı (`XTRAP_CLIENT_ENABLE` vb.); bu build'de kapalıysa yok sayılır. |
| **30-sn create cooldown** | `SRV/db/src/ClientManagerPlayer.cpp:839-850` (`s_createTimeByAccountID`) | Evet — otomasyon üst üste create atarsa ikincisi generic failure (bType=0) alır. En az 30 sn beklemeli. |
| Ping/pong + handshake retry | server boş/yanlış desc'leri kapatır (`desc.cpp:183-225`, `desc.cpp:707-713`) | `HEADER_GC_PING(44)` → `HEADER_CG_PONG(0xfe)` — client kendi cevaplar. |

**Elle girişten fark yaratacak tek şey kalmaz:** (a) `adwClientKey` tutarlılığı, (b) `g_bCheckClientVersion` CONFIG'te açıksa doğru versiyon stringi, (c) ping cevaplama, (d) client'ın kendi UI callback'lerinin (`OnLoginStart`, `OnLoginFailure`, `LoadData`, `OnCreateSuccess/Failure`) bozulmadan kalması — çünkü C++ katmanı her şeyi `PyCallClassMemberFunc` ile Python'a çeker.

---

## 9. OTOMASYON İÇİN DURUM MAKİNESİ (xGODMOD2 adım adım eşlemesi)

Kullanıcının istediği adımların birebir eşlemesi — her adım: koşul → işlem → başarı kontrolü → hata yakalama:

| # | İstenen adım | Fonksiyon/paket | "Yapıldı" kanıtı | Hata yakalama |
|---|---|---|---|---|
| 1 | **Giriş yapma** | `net.SetLoginInfo(id,pwd)` + `net.ConnectToAccountServer()` (glue `Module.cpp:346`) ya da UI: `idEditLine/pwdEditLine.SetText` + `loginButton.CallEvent()` | pencere `LoginWindow` → `SelectCharacterWindow`'a döner | `OnLoginFailure(kod)` callback (§3d tablo) / ekran LOGIN'de kalır |
| 2 | **Giriş cevabını izleme** | client içi: `HEADER_GC_AUTH_SUCCESS(150)` → key → kanala connect → `HEADER_CG_LOGIN2(109)` → `TPacketGCLoginSuccess4(32)` | `PHASE_WINDOW_SELECT` penceresi açılır | `TPacketGCLoginFailure{7, szStatus}` |
| 3 | **Karakter seçim ekranında mı?** | `SetPhaseWindow(PHASE_WINDOW_SELECT)` izle; `net.IsConnect()`=True | `SelectCharacterWindow` tipi görünür | `PHASE_CLOSE` → LoginWindow'a geri düşer |
| 4 | **Kaç karakter / cins / level / isimleri listele** | `net.GetAccountCharacterSlotDataInteger/String(i, SLOT_*)` i=0..4 (§4b referans döngü) | `ID != 0` slot sayısı; `RACE`→sınıf (`race%4`), `LEVEL`, `NAME` | — |
| 5 | **Karakter yoksa oluştur butonuna basabilmek** | UI: `introselect.CreateCharacterButton` akışı → `stream.SetCreateCharacterPhase()`; pencere `CreateCharacterWindow` açılır | pencere tipi `CreateCharacterWindow` | slot doluysa client zaten `CREATE_FULL` popup (§6d) |
| 6 | **Bayrak listesi + bayrak seçme** | 0 karakter ise otomatik `ReselectEmpireWindow`; seçim: `net.SendSelectEmpirePacket(1|2|3)` ya da UI `ew.OnSelectEmpire` + `ClickSelectButton` | pencere SELECT'e geri döner (server `LoginSuccess4` tekrar yollar) | `bEmpire >= 4` → `PHASE_CLOSE`; karakter varsa sessiz ret |
| 7 | **Sonraki pencere (sınıf seçimi + nick) kontrolü** | `SetCreateCharacterPhase` → `CreateCharacterWindow`; UI değişkenleri: `ccw.job_id` (0-3), `ccw.gender` (0/1), `ccw.shape` (0/1), `ccw.editCharacterName.SetText(ad)` | pencere CREATE'te + seçim alanları doldurulmuş | — |
| 8 | **Karakter oluşturma** | `net.SendCreateCharacterPacket(slot, ad, race 0-8, shape 0/1, 0,0,0,0)` (statlar server'da `JobInitialPoints`'tan — ihmal edilir, §6c) | `net.GetAccountCharacterSlotDataInteger(slot, ID) != 0` + pencere SELECT'e döner | `TPacketGCCreateFailure{9, bType}`: **1=isim alınmış** ("Bu ismi zaten..."), **0=genel** ("Karakteri yaratamazsın."); ayrıca 30-sn cooldown → generic fail |
| 9 | **Hata notunu düşme** | bType ayrımı + popup/locale metni (`CREATE_EXIST_SAME_NAME` / `CREATE_FAILURE` / `CREATE_FULL`) | hata kaydı yazılır, yeni isimle retry (farklı slot) | — |
| 10 | **İstenen karakteri seçip oyuna girme** | **`net.DirectEnter(slot)` TEK BAŞINA** (çift giriş YASAĞI §7) | pencere `LoadingWindow` → `GameWindow`; server `PHASE_GAME` + `TPacketGCTime(106)` + `TPacketGCChannel(121)` | `PHASE_CLOSE` (hesap/versiyon/harita sorunu); loading 60sn'den uzun sürerse ortada select-paketi cevabı yok demektir (§4d sessiz reddi) |

**Slot-bağımsız kural:** `TSimplePlayerInformation.lAddr/wPort` zaten kanal bilgisini taşır; `DirectEnter` aynı kanal sunucusuna 2. bağlantıyı kurar (serverinfo.py'deki portlara değil, slot verisindeki porte).

---

## 10. END-TO-END AKIŞ DİYAGRAMI (paket isimleri + handler'larla)

```
 [app start] prototype.py RunApp:19 → MainStream.SetLogoPhase (networkmodule.py:165)
    → introLogo → stream.SetLoginPhase (networkmodule.py:171) → introLogin.LoginWindow
    → kullanıcı/komut gönderir → LoginWindow.Connect (intrologin.py:662)
        net.SetPacketSequenceMode() (SEQUENCE_PACKET_ENABLE=1)
        stream.SetLoginInfo(id,pwd) → net.SetLoginInfo (Module.cpp:389)
        stream.Connect() → KEEP_ACCOUNT_CONNETION_ENABLE=1 → net.ConnectToAccountServer (Module.cpp:346)

 ── AUTH SUNUCUSU (192.168.0.13:30001) ──────────────────────────────────────────
 1. S: DESC::Setup → SetPhase(PHASE_HANDSHAKE) + TPacketGCHandshake{0xff}
 2. C: HandShakePhase yankılar {0xff} → S: CInputProcessor::Handshake (input.cpp:186)
       ok → S: SetPhase(PHASE_AUTH)   [TPacketGCPhase{0xfd, PHASE_AUTH}]
 3. C: CAccountConnector::__AuthState_RecvPhase (AccountConnector.cpp:229)
       → TPacketCGLogin3{111, name, pwd, adwClientKey[4]}
 4. S(auth): CInputAuth::Login (input_auth.cpp:75) → SQL QID_AUTH_LOGIN
       HATA → LoginFailure(d,"NOID|WRONGPWD|ALREADY|NOTAVAIL|BADSCLID|AGELIMIT|<status>|BLKLOGIN|NOBILL|BLOCK|SHUTDOWN")
             → TPacketGCLoginFailure{7, szStatus} → C: OnLoginFailure (intrologin.py:422)
       OK  → DBManager::LoginPrepare (db.cpp:499) → SendAuthLogin (db.cpp:472)
             → DB core QUERY_AUTH_LOGIN (ClientManager.cpp:1884)
             → CInputDB::AuthLogin (input_db.cpp:1757)
             → TPacketGCAuthSuccess{150, dwLoginKey, bResult=1}
 5. C: __AuthState_RecvAuthSuccess (AccountConnector.cpp:443)
       bResult=0 → OnLoginFailure("BESAMEKEY")
       değilse SetLoginKey(key); net.Connect(oyun_kanali, 30003|30007|30011|30015); auth kapat

 ── OYUN SUNUCUSU (kanal) — login ───────────────────────────────────────────────
 6. S: handshake (1. adımla aynı) → SetPhase(PHASE_LOGIN) [TPacketGCPhase{0xfd,2}]
 7. C: SetLoginPhase (PhaseLogin.cpp:97) OTOMATİK yollar
       TPacketCGLogin2{109, name, dwLoginKey, adwClientKey[4]}   (SendLoginPacketNew:276)
       → S: CInputLogin::LoginByKey (input_login.cpp:172)
            HATA(VERSION/SHUTDOWN/FULL/BLOCKED_COUNTRY) → TPacketGCLoginFailure
       → DB: HEADER_GD_LOGIN_BY_KEY → QUERY_LOGIN_BY_KEY (ClientManagerLogin.cpp:83)
             key/ALREADY/client-key uyuşmazlığı → HEADER_DG_LOGIN_NOT_EXIST|LOGIN_ALREADY
       → S: CInputDB::LoginSuccess (input_db.cpp:112)
            status!="OK" → LoginFailure(status)
            → TPacketGCEmpire{90, bEmpire|rastgele 1..3}
            → SetPhase(PHASE_SELECT) [TPacketGCPhase{0xfd,3}]
            → TPacketGCLoginSuccess4{32, TSimplePlayer players[5], guilds, handle, random_key}
 8. C: __RecvEmpirePacket (m_dwEmpireID) ; RecvPhasePacket→SetSelectPhase (PhaseSelect.cpp:9)
       IsSelectedEmpire() → PyCall "SetSelectCharacterPhase" → introSelect.Open (introselect.py:369)
       * pencere birkaç frame sonra açılır (phase curtain) ve slot tablosunu KENDİ okur *
       __RecvLoginSuccessPacket4 (PhaseLogin.cpp:184) m_akSimplePlayerInfo[5] doldurur
       (PyCall "Refresh" — bu pakte bilinçli no-op)

 ── EMPIRE (yalnız hesapta 0 karakter varsa) ────────────────────────────────────
 9. C: introSelect.Open 0 karakter görür (introselect.py:519-521)
       → OnUpdate → SetReselectEmpirePhase → introEmpire.ReselectEmpireWindow
       → ClickSelectButton (introempire.py:334) → net.SendSelectEmpirePacket(1|2|3)
       → TPacketCGEmpire{90, bEmpire}
 10. S: CInputLogin::Empire (input_login.cpp:839)
       bEmpire>=4 → PHASE_CLOSE ; karakter varsa sessiz ret
       → DB: HEADER_GD_EMPIRE_SELECT → QUERY_EMPIRE_SELECT (ClientManager.cpp:1112,
         UPDATE player_index.empire + pid'leri köye ışınla)
       → CInputDB::EmpireSelect (input_db.cpp:1302)
         → TPacketGCEmpire{90} + TPacketGCLoginSuccess4{32} (tazeleme, hâlâ 0 karakter)
 11. C: select ekranı → CreateCharacterButton (introselect.py:709)
       full → CREATE_FULL popup ; değilse stream.SetCreateCharacterPhase → introCreate

 ── KARAKTER OLUŞTURMA ──────────────────────────────────────────────────────────
 12. C: CreateCharacterButton (introcreate.py:622)
       net.SendCreateCharacterPacket(slot, name, race 0..8, shape 0/1, CON,INT,STR,DEX)
       → TPacketCGCreateCharacter{4, index, name[25], WORD job(race), shape, 4×BYTE}
 13. S: CInputLogin::CharacterCreate (input_login.cpp:478)
       g_BlockCharCreation            → TPacketGCCreateFailure{9, 0}
       len(name)>12                   → TPacketGCCreateFailure{9, 0}
       !check_name | shape>1          → TPacketGCCreateFailure{9, 0}
       name==hesap-login              → TPacketGCCreateFailure{9, 1}
       NewPlayerTable2 (race kötü)    → TPacketGCCreateFailure{9, 0}
       değilse HEADER_GD_PLAYER_CREATE → __QUERY_PLAYER_CREATE (ClientManagerPlayer.cpp:832)
            son create <30sn           → DG_PLAYER_CREATE_FAILED  → {9, 0}
            slot pid dolu              → DG_PLAYER_CREATE_ALREADY → {9, 1}
            isim player tablosunda     → DG_PLAYER_CREATE_ALREADY → {9, 1}
            INSERT fail                → DG_PLAYER_CREATE_ALREADY → {9, 1}
            index update fail          → DG_PLAYER_CREATE_FAILED  → {9, 0}
            OK → TPacketDGCreateSuccess
       → CInputDB::PlayerCreateSuccess (input_db.cpp:200)
            slot sınır dışı → HEADER_GC_CHARACTER_CREATE_FAILURE byte
            OK → TPacketGCPlayerCreateSuccess{8, bAccountCharacterIndex, TSimplePlayer}
 14. C: __RecvPlayerCreateSuccessPacket (PhaseSelect.cpp:237) → "OnCreateSuccess"
       (introcreate.py:453) → 2 sn sonra → seçim ekranına dönüş; slotlar güncell
        __RecvPlayerCreateFailurePacket (PhaseSelect.cpp:256) → "OnCreateFailure(bType)"
       type==1 → CREATE_EXIST_SAME_NAME ; değilse CREATE_FAILURE (introcreate.py:457-469)

 ── SEÇ → OYUNA GİR ─────────────────────────────────────────────────────────────
 15. C: StartGameButton (introselect.py:732) → 0.2 sn animasyon → net.DirectEnter(slot)
       (introselect.py:765) = ConnectGameServer (PythonNetworkStream.cpp:499)
       __DirectEnterMode_Set(slot) + Connect(lAddr, wPort)   [aynı kanal sunucusu]
 16. yeni TCP: handshake → PHASE_LOGIN [0xfd,2] → tekrar TPacketCGLogin2{109}
       → CInputLogin::LoginByKey → DB LoginSuccess → TPacketGCEmpire + PHASE_SELECT
       + TPacketGCLoginSuccess4{32}
 17. C: SetSelectPhase __DirectEnterMode_IsSet() görür → PyCall "SetLoadingPhase"
       → introLoading.Open (introloading.py:147-148)
       → net.SendSelectCharacterPacket(chrSlot) → TPacketCGSelectCharacter{6, index}
 18. S: CInputLogin::CharacterSelect (input_login.cpp:270)
       hesap yok / index>=5 / bChangeName → sys_err + CEVAP YOK (asılı kalır)
       → HEADER_GD_PLAYER_LOAD → CInputDB::PlayerLoad (input_db.cpp:348)
         harita izinli değil → köye warp + PHASE_CLOSE
         OK → SetPhase(PHASE_LOADING) [0xfd,4]
         → TPacketGCMainCharacter2_EMPIRE{113, dwVID, wRaceNum, szName, x,y,z, byEmpire, bySkillGroup}
         → TPacketGCPoints{16} (tüm POINT_*), TPacketGCSkillLevel{76}
 19. C: RecvMainCharacter2_EMPIRE (PhaseLoading.cpp:223) → "LoadData"(x,y)
       → introLoading yükleme adımları (__LoadMap → net.Warp) → net.StartGame (introloading.py:386)
       → OnProcess (PythonNetworkStream.cpp:700) → "SetGamePhase" → game.GameWindow.Open
       → net.SendEnterGamePacket (game.py:204) → TPacketCGEnterFrontGame{10}
 20. S: CInputLogin::Entergame (input_login.cpp:592)
       karakter yok → PHASE_CLOSE
       → ch->Show, SetPhase(PHASE_GAME) [0xfd,5],
         TPacketGCTime{106}, TPacketGCChannel{121}, PVP/messenger/land listeleri
         versiyon kontrolü (g_bCheckClientVersion) → uyuşmazlık: notice + DelayedDisconnect
 21. C: SetGamePhase (PhaseGame.cpp:897) — OYUN İÇİ.
       [oturum ortası: HEADER_GC_PING{44} → TPacketCGPong{0xfe};
        HEADER_GC_WARP{65} → RecvWarpPacket DirectEnterMode ile yeniden bağlanır (PhaseGame.cpp:969);
        GC_PHASE{0xfd, PHASE_CLOSE=0} → ClosePhase → login penceresine dönüş]
```

**Otomasyon kopya kâğıdı:** izlenecek tekil sinyaller — `TPacketGCLoginFailure.szStatus` (login hataları), `HEADER_GC_LOGIN_SUCCESS4(32)` + slot tablosu (select ekranı), `TPacketGCCreateFailure.bType` (0=genel/"yaratamazsın", 1=isim alınmış), `TPacketGCPlayerCreateSuccess(8)` (create OK), `TPacketGCMainCharacter2_EMPIRE(113)` ("karakter X ile yükleme başladı"), `HEADER_GC_PHASE(5)` (oyun içi). Empire: yalnız slot tablosu TAMAMEN boşken `HEADER_CG_EMPIRE` (1..3); değilse doğrudan `HEADER_CG_PLAYER_CREATE`.

---

## 11. HIZLI FONKSİYON İNDEKSİ (dosya:satır — arama tablosu)

### Client (CLI = ClientSource/Client/UserInterface/)
| Fonksiyon | Dosya:satır |
|---|---|
| `CPythonNetworkStream::SetLoginInfo` | PythonNetworkStream.cpp:512 |
| `CPythonNetworkStream::SetLoginKey` | PythonNetworkStream.cpp:523 |
| `CPythonNetworkStream::ConnectGameServer` | PythonNetworkStream.cpp:499 |
| `CPythonNetworkStream::SetPhaseWindow` / `ClearPhaseWindow` | PythonNetworkStream.cpp:364 / 372 |
| `CPythonNetworkStream::GetAccountCharacterSlotDatau/z` | PythonNetworkStream.cpp:396 / 451 |
| `CPythonNetworkStream::IsSelectedEmpire` | PythonNetworkStream.cpp:388 |
| `CPythonNetworkStream::RecvPhasePacket` | PythonNetworkStream.cpp:621 |
| `CPythonNetworkStream::RecvPingPacket` | PythonNetworkStream.cpp:667 |
| `CPythonNetworkStream::OnProcess` (StartGame tüketimi) | PythonNetworkStream.cpp:700 |
| `CPythonNetworkStream::ClosePhase` | PythonNetworkStream.cpp:750 |
| `CPythonNetworkStream::__ClearSelectCharacterData` | PythonNetworkStream.cpp:808 |
| `__DirectEnterMode_Set/_IsSet` | PythonNetworkStream.cpp:827 |
| `CPythonNetworkStream::HandShakePhase` | PythonNetworkStreamPhaseHandShake.cpp:14 |
| `CPythonNetworkStream::SetHandShakePhase` | PythonNetworkStreamPhaseHandShake.cpp:101 |
| `RecvHandshakeOKPacket` / `RecvHandshakePacket` | PythonNetworkStreamPhaseHandShake.cpp:156 / 128 |
| `RecvHSCheckRequest` / `RecvXTrapVerifyRequest` | PythonNetworkStreamPhaseHandShake.cpp:269 / 309 |
| `CPythonNetworkStream::SetLoginPhase` | PythonNetworkStreamPhaseLogin.cpp:97 |
| `__RecvLoginSuccessPacket3/4` | PythonNetworkStreamPhaseLogin.cpp:156 / 184 |
| `OnConnectFailure` | PythonNetworkStreamPhaseLogin.cpp:213 |
| `__RecvLoginFailurePacket` | PythonNetworkStreamPhaseLogin.cpp:226 |
| `SendDirectEnterPacket` (ölü kod) | PythonNetworkStreamPhaseLogin.cpp:239 |
| `SendLoginPacket` | PythonNetworkStreamPhaseLogin.cpp:256 |
| `SendLoginPacketNew` | PythonNetworkStreamPhaseLogin.cpp:276 |
| `SendRunupMatrixAnswerPacket` / `SendNEWCIBNPasspodAnswerPacket` / `SendChinaMatrixCardPacket` | PythonNetworkStreamPhaseLogin.cpp:320 / 355 / 369 |
| `__RecvLoginKeyPacket` | PythonNetworkStreamPhaseLogin.cpp:408 |
| `__RecvEmpirePacket` | PythonNetworkStreamPhaseLogin.cpp:146 |
| `CPythonNetworkStream::SetSelectPhase` | PythonNetworkStreamPhaseSelect.cpp:9 |
| `SendSelectEmpirePacket` | PythonNetworkStreamPhaseSelect.cpp:149 |
| `SendSelectCharacterPacket` | PythonNetworkStreamPhaseSelect.cpp:165 |
| `SendDestroyCharacterPacket` | PythonNetworkStreamPhaseSelect.cpp:181 |
| `SendCreateCharacterPacket` | PythonNetworkStreamPhaseSelect.cpp:198 |
| `__RecvPlayerCreateSuccessPacket` | PythonNetworkStreamPhaseSelect.cpp:237 |
| `__RecvPlayerCreateFailurePacket` | PythonNetworkStreamPhaseSelect.cpp:256 |
| `__RecvPlayerDestroySuccessPacket` | PythonNetworkStreamPhaseSelect.cpp:268 |
| `__RecvPlayerDestroyFailurePacket` | PythonNetworkStreamPhaseSelect.cpp:282 |
| `__RecvChangeName` | PythonNetworkStreamPhaseSelect.cpp:292 |
| `CPythonNetworkStream::SetLoadingPhase` | PythonNetworkStreamPhaseLoading.cpp:182 |
| `RecvMainCharacter2_EMPIRE` | PythonNetworkStreamPhaseLoading.cpp:223 |
| `CPythonNetworkStream::StartGame` | PythonNetworkStreamPhaseLoading.cpp:343 |
| `CPythonNetworkStream::SendEnterGame` | PythonNetworkStreamPhaseLoading.cpp:348 |
| `CPythonNetworkStream::SetGamePhase` | PythonNetworkStreamPhaseGame.cpp:897 |
| `RecvWarpPacket` | PythonNetworkStreamPhaseGame.cpp:969 |
| `SendAttackPacket` (CRC tüketimi) | PythonNetworkStreamPhaseGame.cpp:2599-2636 |
| `__SendCRCReportPacket` (no-op) | PythonNetworkStreamPhaseGame.cpp:4207 |
| `SendClientVersionPacket` | PythonNetworkStreamPhaseGame.cpp:4236 |
| `net.GetAccountCharacterSlotDataInteger/String` glue | PythonNetworkStreamModule.cpp:164 / 179 |
| `net.ConnectToAccountServer` glue | PythonNetworkStreamModule.cpp:346 |
| `net.SetLoginInfo` glue | PythonNetworkStreamModule.cpp:389 |
| `net.SendSelectEmpirePacket` glue | PythonNetworkStreamModule.cpp:413 |
| `net.DirectEnter` glue | PythonNetworkStreamModule.cpp:473 |
| `netSendSelectCharacterPacket` glue | PythonNetworkStreamModule.cpp:484 |
| `netSendCreateCharacterPacket` glue | PythonNetworkStreamModule.cpp:610 |
| `netSendEnterGamePacket` glue | PythonNetworkStreamModule.cpp:667 |
| `net.SetPacketSequenceMode` glue | PythonNetworkStreamModule.cpp:1706 |
| `PHASE_WINDOW_*` sabitleri | PythonNetworkStreamModule.cpp:2118-2124 |
| `ACCOUNT_CHARACTER_SLOT_*` sabitleri | PythonNetworkStreamModule.cpp:2126-2149 |
| `net.EMPIRE_A/B/C` | PythonNetworkStreamModule.cpp:2155-2157 |
| `BuildProcessCRC` | ProcessCRC.cpp:96 |
| `SendSequence` | EterLib/NetStream.cpp:838 |
| `RaceToJob` / `RaceToSex` | InstanceBase.h:1180-1188 / 1190-1210 |

### Server (SRV = GameSource/Server/)
| Fonksiyon | Dosya:satır |
|---|---|
| `DESC::Setup` | game/src/desc.cpp:237 |
| `DESC::HandshakeProcess` | game/src/desc.cpp:666 |
| `DESC::SendLoginSuccessPacket` | game/src/desc.cpp:931 |
| `CInputProcessor::Handshake` | game/src/input.cpp:186 |
| `CInputProcessor::Version` | game/src/input.cpp:216 |
| `LoginFailure` (global) | game/src/input.cpp:226 |
| `CInputHandshake::Analyze` | game/src/input.cpp:643 |
| `CInputAuth::Login` | game/src/input_auth.cpp:75 |
| `CInputLogin::Login` | game/src/input_login.cpp:120 |
| `CInputLogin::LoginByKey` | game/src/input_login.cpp:172 |
| `CInputLogin::ChangeName` | game/src/input_login.cpp:240 |
| `CInputLogin::CharacterSelect` | game/src/input_login.cpp:270 |
| `CInputLogin::RaceToJob` | game/src/input_login.cpp:372 |
| `NewPlayerTable2` | game/src/input_login.cpp:425 |
| `CInputLogin::CharacterCreate` | game/src/input_login.cpp:478 |
| `CInputLogin::Entergame` | game/src/input_login.cpp:592 |
| `CInputLogin::Empire` | game/src/input_login.cpp:839 |
| `CInputLogin::Analyze` | game/src/input_login.cpp:1055+ |
| `CInputDB::LoginSuccess` | game/src/input_db.cpp:112 |
| `CInputDB::PlayerCreateSuccess` / `Failure` | game/src/input_db.cpp:200 / 187 |
| `CInputDB::PlayerLoad` | game/src/input_db.cpp:348 |
| `CInputDB::ChangeName` | game/src/input_db.cpp:318 |
| `CInputDB::AuthLogin` | game/src/input_db.cpp:1757 |
| `CInputDB::LoginAlready` | game/src/input_db.cpp:1274 |
| `CInputDB::EmpireSelect` | game/src/input_db.cpp:1302 |
| `DBManager::LoginPrepare` / `SendAuthLogin` | game/src/db.cpp:499 / 472 |
| `DBManager::QID_AUTH_LOGIN` işleyici | game/src/db.cpp:682-899 |
| `CClientManager::QUERY_LOGIN_BY_KEY` | db/src/ClientManagerLogin.cpp:83 |
| `CClientManager::QUERY_AUTH_LOGIN` | db/src/ClientManager.cpp:1884 |
| `CClientManager::QUERY_EMPIRE_SELECT` | db/src/ClientManager.cpp:1112 |
| `CClientManager::__QUERY_PLAYER_CREATE` | db/src/ClientManagerPlayer.cpp:832 |
| `ping_event` | game/src/desc.cpp:198 |

### Client Python scriptleri (PY = Metin2Client/pack/root/)
| Dosya:fonksiyon | Satır | İş |
|---|---|---|
| `networkmodule.py:165-240` | — | faz sürücüleri (Set*Phase) |
| `intrologin.py:179-198` | loginFailureMsgDict | hata kodları → mesaj |
| `intrologin.py:394/412/418/422` | OnConnectFailure/OnHandShake/OnLoginStart/OnLoginFailure | event handler'ları |
| `intrologin.py:662-665` | Connect | giriş gönderimi + sequence mode |
| `introselect.py:37` | CHARACTER_SLOT_COUNT_MAX=5 | slot sayısı |
| `introselect.py:115-171` | MyCharacters.LoadCharacterData | slot okuma döngüsü (OTOMASYON REFERANSI) |
| `introselect.py:340` | net.SetPhaseWindow(SELECT, self) | pencere kaydı |
| `introselect.py:519-521` | Open | 0 karakter → empire akışı |
| `introselect.py:709-726` | CreateCharacterButton | create ekranına geçiş |
| `introselect.py:732-765` | StartGame akışı | net.DirectEnter(slot) |
| `introselect.py:841/854` | destroy/OnDeleteSuccess | karakter silme |
| `introcreate.py:19-46` | M2_CONST_ID / M2STATPOINT | cins→race eşlemesi |
| `introcreate.py:583` | SelectShape | shape 0/1 |
| `introcreate.py:622-645` | CreateCharacterButton | create paketi gönderimi |
| `introcreate.py:453-469` | OnCreateSuccess/Failure | sonuç işleme |
| `introempire.py:54-57/232-244/247/334` | empire penceresi | bayrak seçimi |
| `introloading.py:147-148` | Open | SendSelectCharacterPacket BURADA |
| `introloading.py:203-386` | LoadData/__StartGame | yükleme + StartGame |
| `game.py:204` | GameWindow.Open | SendEnterGamePacket |
| `serverinfo.py:4-41` | — | auth/game adresleri |
| `constinfo.py:66-67` | SEQUENCE_PACKET_ENABLE, KEEP_ACCOUNT_CONNETION_ENABLE | davranış anahtarları |

### Paket/struct tanımları
| Struct | Client | Server |
|---|---|---|
| `TPacketCGLogin / Login2 / Login3` | Packet.h:575-590 civarı / :581 / AccountConnector | packet.h:580 |
| `TPacketGCLoginSuccess4` (+`TSimplePlayerInformation`) | Packet.h:1277+ / :1219-1242 | packet.h:943-952 / tables.h:347-369 |
| `TPacketGCLoginFailure` | Packet.h:1277 (`LOGIN_STATUS_MAX_LEN=8`) | packet.h |
| `TPacketGCEmpire` | Packet.h:2302 | packet.h:1777 |
| `TPacketCGEmpire` | Packet.h:2302 | packet.h:1777 |
| `TPacketCGSelectCharacter` | Packet.h | packet.h:622 (TPacketCGPlayerSelect) |
| `TPacketCGDestroyCharacter` | Packet.h:450 (`PRIVATE_CODE_LENGTH=8`) | — |
| `TPacketCGCreateCharacter` | Packet.h:1284-1295 | packet.h:635-646 (TPacketCGPlayerCreate) |
| `TPacketGCPlayerCreateSuccess` | Packet.h | packet.h |
| `TPacketGCCreateFailure{header=9,bType}` | Packet.h | packet.h |
| `TPacketGCMainCharacter2_EMPIRE` | Packet.h:1547-1556 | packet.h:1106-1151 |
| `TPacketCGEnterFrontGame` | Packet.h | packet.h |
| `EPhase` enum | Packet.h:1165-1179 | — |
| `packet_auth_success` | Packet.h:2626 | packet.h:954 |

> Rapor sonu. Tüm satır numaraları LegendySF-V2 çalışma kopyası üzerinden doğrulanmıştır; repo güncellenirse satırlar kayabilir, fonksiyon adlarıyla arayın.
