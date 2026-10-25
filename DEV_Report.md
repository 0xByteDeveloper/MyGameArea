# DEV RAPOR — HyperBot & C4US Fonksiyonları vs Gerçek Oyun Kaynağı (LegendySF-V2)

*Üretim: 2026-10-25 11:36 UTC | Kapsam: 1350 fonksiyon | Referans: DrLegendy/LegendySF-V2 (ClientSource + GameSource, gerçek Metin2 client & server kaynak kodu)*

> **Bu rapor ne yapar?** FULL_System.json (HyperBot-Nerwia2) ve FULL_System_A1.json (C4USMultiHack-Metin2) içindeki HER fonksiyon için üç soruya kanıtlı cevap verir: (1) Gerçek oyunda (LegendySF kaynak kodunda) karşılığı var mı? (2) Varsa ne işe yarar — hangi parametreler, hangi typedef'ler, hangi paket alanları, server karşılığı nedir? (3) Yoksa (ör. `GameFunctionsCustom::Boost`) fonksiyonun İÇİNDEKİ oyun fonksiyonları hangileri ve bunlarla ne yapılabilir?

---

## İçindekiler
- 1. Özet ve İstatistikler
- 2. Yöntem (Sistematik İlerleme)
- 3. LegendySF Referans Haritası
- 4. OYUNDA OLAN FONKSİYONLAR — HyperBot
- 5. OYUNDA OLAN FONKSİYONLAR — C4US
- 6. SARMALAYICILAR — Oyunda Yok, İçindekiler Oyunda Var (Boost dahil)
- 7. OYUNDA OLMAYANLAR — Tam Liste
- 8. Paket Zinciri Haritası
- 9. Typedef Sözlüğü
- 10. Uygulamalı Araştırma — Bununla Ne Yapılabilir?
- 11. Fonksiyon İndeksi

---
## 1. Özet ve İstatistikler

| Metrik | Değer |
|---|---|
| Taranan toplam fonksiyon | **1350** (HyperBot 596 + C4US 754) |
| Oyunda karşılığı olan | **198** |
| Sarmalayıcı (oyunda yok, içindekiler oyunda var) | **384** |
| Oyunda olmayan | **768** |
| LegendySF taranan C++ dosyası | ~1.110 (Extern hariç) |
| İndekslenen tanım noktası | 32270 |
| Paket typedef | 677 struct |
| Server handler (input_main.cpp) | 24 |

**Ana bulgular:**

1. Her iki hile projesinin paket gönderimi, oyunun gerçek `CPythonNetworkStream::Send*` fonksiyonlarına dayanır — hiçbiri kendi soketini açmaz; bu yüzden LegendySF client kaynağı her hack fonksiyonunun gerçek davranışını doğrular.
2. `SetAttackKeyState` örneği: oyun, atak tuşu durumunu `m_isAtkKey` bayrağında tutar ve mouse döngüsü (`PythonPlayerInputMouse.cpp:381`) bu bayrakla saldırıyı tetikler — hack tarafındaki 'auto attack' mantığının oyun karşılığı budur.
3. `Boost` oyunun kendi API'lerini birleştirir: `SCRIPT_SetPixelPosition` (lokal taşıma) + `SendCharacterStatePacket` (`TPacketCGMove`, `bRot=fRot/5`, `dwTime=ELTimer_GetServerMSec()`). Sunucu küçük adımları kabul eder, tek seferlik büyük sıçramayı reddeder.
4. Saldırı zinciri sunucuda `CInputMain::Attack` → `battle.cpp` hasar hesabıyla biter; client sadece talep gönderir. Anti-cheat: `SendSpecial` CRCMagicCube baytları ekler, sunucu `AssembleCRCMagicCube` ile doğrular.

## 2. Yöntem (Sistematik İlerleme)

| Aşama | İş | Çıktı |
|---|---|---|
| 0 | FULL_System.json + FULL_System_A1.json envanter birleştirme | 1.350 fonksiyon |
| 1 | LegendySF-V2 indeksleme (tanim/cagri/typedef/header/handler) | defs + calls + 1.232 typedef |
| 2 | C4US gövde çağrı grafiği (satır aralıklarından) + isim çözümleme (prefix stripping) | iç oyun çağrıları |
| 3 | Sınıflandırma: OYUNDA VAR / SARMALAYICI / YOK (jenerik isim filtresi + sınıf sayısı eşiği) | durum etiketi |
| 4 | Gövde analizi: imza, paket alanları, header, çağrı noktaları | kanıtlı semantik |
| 5 | Kürasyon: ~70 kritik fonksiyon elle araştırıldı (kaynak okunarak) | derin açıklamalar |
| 6 | BÜYÜK MD montajı | bu rapor |

**Eşleşme kuralları:** fonksiyon adı oyunda `Sinif::isim` olarak geçiyorsa ✅; jenerik isimler (`Init/Update/OnIteration`… 8+ sınıfta geçen adlar) sayılmaz; sarmalayıcı isimleri çözdürülür (`NetworkStreamSendX→SendX`, `InstanceBaseSCRIPT_X→SCRIPT_X`, `PlayerNEW_X→NEW_X`…).

## 3. LegendySF Referans Haritası

LegendySF-V2, gerçek Metin2 client ve server kaynak kodunu içerir. Bu raporun tüm 'oyunda VAR/YOK' kararları buradan gelir.

**Client (istemci) ana dosyaları:**

| Bileşen | Dosya | İçerik |
|---|---|---|
| Ağ katmanı | `ClientSource/Client/UserInterface/PythonNetworkStreamPhaseGame.cpp` | Tüm Send* fonksiyonlarının gerçek gövdeleri (SendAttackPacket:2599, SendCharacterStatePacket:1152…) |
| Paket tanımları | `ClientSource/Client/UserInterface/Packet.h` | TPacketCG*/GC* typedef'leri |
| Oyuncu durumu | `ClientSource/Client/UserInterface/PythonPlayer*.cpp` | SetAttackKeyState, giriş/akis, task |
| Varlık motoru | `ClientSource/Client/UserInterface/InstanceBase*.cpp` | SCRIPT/NEW_Get/SetPixelPosition, hareket |
| Grafik | `ClientSource/Client/GameLib/` | CGraphicThingInstance::SetCurPixelPosition |

**Server (sunucu) ana dosyaları:**

| Bileşen | Dosya | İçerik |
|---|---|---|
| Paket dağıtıcı | `GameSource/Server/game/src/input_main.cpp` | HEADER_CG_* case'leri, CInputMain::Attack:1702 |
| Hasar | `GameSource/Server/game/src/battle.cpp` | Attack, CalcMeleeDamage |
| Paket tanımları | `GameSource/Server/game/src/packet.h` | TPacketCGAttack:656 (CRC alanları dahil) |
| Karakter | `GameSource/Server/game/src/char.cpp` | CHARACTER, Move, SyncPosition |

## 4. OYUNDA OLAN FONKSİYONLAR — HyperBot

> Her giriş: **oyunda karşılığı**, **imza**, **parametreler**, **typedef**, **ne işe yarar**, **paket/server karşılığı**, **oyunda çağrıldığı yerler**.

### Sınıf: `Background` (3 fonksiyon)

#### `Background::GetTerrainHeight`
*Konum (hack):* `HyperBot/Background.cpp:32-39` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/MapManager.cpp:193` (CMapManager::GetTerrainHeight); `client: GameLib/MapManager.cpp:197` (CMapManager::GetTerrainHeight)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapManager.h:45` — `float GetTerrainHeight(float fx, float fy);`
- `client: GameLib/MapManager.cpp:193` — `float CMapManager::GetTerrainHeight(float fx, float fy)`
- `client: GameLib/MapManager.cpp:197` — `TraceError("CMapManager::GetTerrainHeight(%f, %f) - Accessing in a not initialized map", fx, fy);`

#### `Background::GetResourcePointer`
*Konum (hack):* `HyperBot/Background.cpp:152-160` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/ResourceManager.cpp:271` (CResourceManager::GetResourcePointer)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Area.cpp:613` — `CGraphicThing * pThing = (CGraphicThing *)rkResMgr.GetResourcePointer(Data.strFileName.c_str());`
- `client: GameLib/Area.cpp:649` — `CGraphicThing* pLODModelThing = (CGraphicThing *)rkResMgr.GetResourcePointer(stLODModelFileName.c_str());`
- `client: GameLib/Area.cpp:735` — `CAttributeData * pAttributeData = (CAttributeData *) CResourceManager::Instance().GetResourcePointer(c_szAttributeFileName);`

#### `Background::GetD3DTexture`
*Konum (hack):* `HyperBot/Background.cpp:170-181` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterGrnLib/Material.cpp:142` (CGrannyMaterial::GetD3DTexture); `client: EterLib/GrpShadowTexture.cpp:60` (CGraphicShadowTexture::GetD3DTexture)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoorRender.cpp:629` — `STATEMANAGER.SetTexture(1, m_BuildingTransparentImageInstance.GetTexturePointer()->GetD3DTexture());`
- `client: GameLib/MapOutdoorRender.cpp:859` — `STATEMANAGER.SetTexture(0, m_attrImageInstance.GetTexturePointer()->GetD3DTexture());`
- `client: GameLib/FlyTrace.cpp:36` — `m_lpTexture = pTexture->GetD3DTexture();`

### Sınıf: `CGraphicImageTexture` (2 fonksiyon)

#### `CGraphicImageTexture::GetTexture`
*Konum (hack):* `HyperBot/Background.cpp:239-244` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: PRTerrainLib/TextureSet.cpp:116` (CTextureSet::GetTexture); `client: EterLib/StateManager.cpp:489` (CStateManager::GetTexture)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoorRenderHTP.cpp:420` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`
- `client: GameLib/MapOutdoorRenderHTP.cpp:444` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`
- `client: GameLib/MapOutdoorRenderHTP.cpp:526` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`

#### `CGraphicImageTexture::GetPath`
*Konum (hack):* `HyperBot/Background.cpp:259-264` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/Filename.h:144` (CFilename::GetPath); `client: EterBase/Filename.h:301` (CFileNameHelper::GetPath)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterBase/Filename.h:86` — `string GetPath(void); // if filename is "/idv/code/file.cpp", it returns "/idv/code"`
- `client: EterBase/Filename.h:144` — `inline string CFilename::GetPath(void) // if filename is "/idv/code/file.cpp", it returns "/idv/code"`
- `client: EterBase/Filename.h:237` — `static string GetPath(string& str); // if filename is "/idv/code/file.cpp", it returns "/idv/code"`

### Sınıf: `Color` (6 fonksiyon)

#### `Color::Color`
*Konum (hack):* `HyperBot/color.h:6-11` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` (CSpeedGrassWrapper::Color)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/EffectMeshInstance.cpp:149` — `D3DXCOLOR Color(1.0f, 1.0f, 1.0f, 1.0f);`
- `client: EterLib/GrpLightManager.cpp:277` — `D3DXCOLOR Color(m_d3dLight.Diffuse);`
- `client: EterLib/GrpLightManager.cpp:283` — `D3DXCOLOR Color(m_d3dLight.Ambient);`

#### `Color::Color`
*Konum (hack):* `HyperBot/color.h:15-19` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` (CSpeedGrassWrapper::Color)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/EffectMeshInstance.cpp:149` — `D3DXCOLOR Color(1.0f, 1.0f, 1.0f, 1.0f);`
- `client: EterLib/GrpLightManager.cpp:277` — `D3DXCOLOR Color(m_d3dLight.Diffuse);`
- `client: EterLib/GrpLightManager.cpp:283` — `D3DXCOLOR Color(m_d3dLight.Ambient);`

#### `Color::Color`
*Konum (hack):* `HyperBot/color.h:19-24` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` (CSpeedGrassWrapper::Color)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/EffectMeshInstance.cpp:149` — `D3DXCOLOR Color(1.0f, 1.0f, 1.0f, 1.0f);`
- `client: EterLib/GrpLightManager.cpp:277` — `D3DXCOLOR Color(m_d3dLight.Diffuse);`
- `client: EterLib/GrpLightManager.cpp:283` — `D3DXCOLOR Color(m_d3dLight.Ambient);`

#### `Color::Color`
*Konum (hack):* `HyperBot/color.h:24-29` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` (CSpeedGrassWrapper::Color)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/EffectMeshInstance.cpp:149` — `D3DXCOLOR Color(1.0f, 1.0f, 1.0f, 1.0f);`
- `client: EterLib/GrpLightManager.cpp:277` — `D3DXCOLOR Color(m_d3dLight.Diffuse);`
- `client: EterLib/GrpLightManager.cpp:283` — `D3DXCOLOR Color(m_d3dLight.Ambient);`

#### `Color::SetColor`
*Konum (hack):* `HyperBot/color.h:29-37` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterPythonLib/PythonWindow.cpp:854` (CBox::SetColor); `client: EterPythonLib/PythonWindow.cpp:876` (CBar::SetColor)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoor.cpp:288` — `m_ScreenFilter.SetColor(mc_pEnvironmentData->FilteringColor);`
- `client: SphereLib/spherepack.cpp:39` — `mRoot->SetColor(0x00FFFFFF);`
- `client: SphereLib/spherepack.cpp:47` — `mLeaf->SetColor(0x00FFFFFF);`

#### `Color::GetColor`
*Konum (hack):* `HyperBot/color.h:37-45` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: SphereLib/spherepack.cpp:388` (SpherePackFactory::GetColor); `client: EterLib/GrpBase.cpp:456` (CGraphicBase::GetColor)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: SphereLib/spherepack.cpp:174` — `mRoot->Render(mRoot->GetColor());`
- `client: SphereLib/spherepack.cpp:175` — `mLeaf->Render(mLeaf->GetColor());`
- `client: SphereLib/spherepack.cpp:217` — `link->GetColor());`

### Sınıf: `ConfigManager` (1 fonksiyon)

#### `ConfigManager::GetFileName`
*Konum (hack):* `HyperBot/ConfigManager.cpp:52-57` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/Property.cpp:30` (CProperty::GetFileName); `client: MilesLib/SoundData.cpp:10` (CSoundData::GetFileName)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Property.cpp:30` — `const char * CProperty::GetFileName()`
- `client: GameLib/Property.cpp:171` — `return CPropertyManager::Instance().Put(c_pszFileName, file.GetFileName());`
- `client: GameLib/PropertyManager.cpp:158` — `itor->second->GetFileName(),`

### Sınıf: `Console` (3 fonksiyon)

#### `Console::SetColor`
*Konum (hack):* `HyperBot/Backend.cpp:109-115` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterPythonLib/PythonWindow.cpp:854` (CBox::SetColor); `client: EterPythonLib/PythonWindow.cpp:876` (CBar::SetColor)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoor.cpp:288` — `m_ScreenFilter.SetColor(mc_pEnvironmentData->FilteringColor);`
- `client: SphereLib/spherepack.cpp:39` — `mRoot->SetColor(0x00FFFFFF);`
- `client: SphereLib/spherepack.cpp:47` — `mLeaf->SetColor(0x00FFFFFF);`

#### `Console::Write`
*Konum (hack):* `HyperBot/Backend.h:107-115` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/FileBase.cpp:94` (CFileBase::Write); `client: EterPack/EterPack.cpp:113` (CMakePackLog::Write)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Property.cpp:131` — `file.Write(&fourcc, sizeof(DWORD));`
- `client: GameLib/Property.cpp:132` — `file.Write("\r\n", 2);`
- `client: GameLib/Property.cpp:147` — `file.Write(m_stCRC.c_str(), m_stCRC.length());`

#### `Console::WriteError`
*Konum (hack):* `HyperBot/Backend.h:135-146` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterPack/EterPack.cpp:168` (CMakePackLog::WriteError)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterPack/EterPack.h:230` — `void WriteError(const char* c_szBuf);`
- `client: EterPack/EterPack.cpp:168` — `void CMakePackLog::WriteError(const char* c_szBuf)`

### Sınıf: `Entity` (22 fonksiyon)

#### `Entity::IsBoss`
*Konum (hack):* `HyperBot/Entity.cpp:51-65` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `server: game/src/char.cpp:8324` (CHARACTER::IsBoss)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `server: game/src/char.cpp:8324` — `bool CHARACTER::IsBoss()`
- `server: game/src/char.h:721` — `bool IsBoss();`
- `server: game/src/battle.cpp:350` — `if (pkVictim->IsBoss())`

#### `Entity::IsEnemy`
*Konum (hack):* `HyperBot/Entity.cpp:65-70` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:301` (CActorInstance::IsEnemy); `client: UserInterface/InstanceBase.cpp:2451` (CInstanceBase::IsEnemy)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:301` — `bool CActorInstance::IsEnemy()`
- `client: GameLib/ActorInstance.h:267` — `bool IsEnemy();`
- `client: UserInterface/PythonCharacterModule.cpp:168` — `return Py_BuildValue("i", pInstance->IsEnemy());`

#### `Entity::IsPC`
*Konum (hack):* `HyperBot/Entity.cpp:70-75` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:285` (CActorInstance::IsPC); `client: UserInterface/InstanceBase.cpp:2441` (CInstanceBase::IsPC)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:285` — `bool CActorInstance::IsPC()`
- `client: GameLib/ActorInstanceData.cpp:82` — `if( IsPC())`
- `client: GameLib/ActorInstanceFly.cpp:39` — `if (pFlyInstance->IsPC())`

#### `Entity::IsNPC`
*Konum (hack):* `HyperBot/Entity.cpp:75-80` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:293` (CActorInstance::IsNPC); `client: UserInterface/InstanceBase.cpp:2446` (CInstanceBase::IsNPC)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:293` — `bool CActorInstance::IsNPC()`
- `client: GameLib/ActorInstanceBattle.cpp:563` — `if (rkActorDst.IsNPC())`
- `client: GameLib/ActorInstance.h:266` — `bool IsNPC();`

#### `Entity::IsStone`
*Konum (hack):* `HyperBot/Entity.cpp:80-85` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:309` (CActorInstance::IsStone); `client: UserInterface/InstanceBase.cpp:2456` (CInstanceBase::IsStone)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:309` — `bool CActorInstance::IsStone()`
- `client: GameLib/ActorInstance.cpp:378` — `if (IsStone())`
- `client: GameLib/ActorInstanceBattle.cpp:560` — `if (rkActorDst.IsStone())`

#### `Entity::IsWalking`
*Konum (hack):* `HyperBot/Entity.cpp:99-107` | *Proje:* HyperBot | *Kategori:* movement
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBaseMovement.cpp:193` (CInstanceBase::IsWalking)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBase.cpp:1450` — `if (!IsWalking())`
- `client: UserInterface/InstanceBase.cpp:1482` — `if (!IsWalking())`
- `client: UserInterface/InstanceBase.cpp:1505` — `if (!IsWalking())`

#### `Entity::IsBuilding`
*Konum (hack):* `HyperBot/Entity.cpp:107-112` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:333` (CActorInstance::IsBuilding); `client: UserInterface/InstanceBase.cpp:2512` (CInstanceBase::IsBuilding)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:333` — `bool CActorInstance::IsBuilding()`
- `client: GameLib/MapOutdoorUpdate.cpp:572` — `if (((CActorInstance *)pInstance)->IsBuilding())`
- `client: GameLib/ActorInstanceBattle.cpp:554` — `if (rkActorDst.IsBuilding())`

#### `Entity::IsDoor`
*Konum (hack):* `HyperBot/Entity.cpp:112-117` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:341` (CActorInstance::IsDoor); `client: UserInterface/InstanceBase.cpp:2517` (CInstanceBase::IsDoor)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:341` — `bool CActorInstance::IsDoor()`
- `client: GameLib/ActorInstanceBattle.cpp:557` — `if (rkActorDst.IsDoor())`
- `client: GameLib/ActorInstanceBattle.cpp:655` — `if (rVictim.IsBuilding() || rVictim.IsDoor())`

#### `Entity::GetType`
*Konum (hack):* `HyperBot/Entity.cpp:122-127` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/FlyTarget.cpp:73` (CFlyTarget::GetType); `client: GameLib/ItemData.cpp:241` (CItemData::GetType)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:530` — `if (TYPE_BUILDING != GetType())`
- `client: GameLib/RaceMotionData.h:237` — `UINT GetType() const;`
- `client: GameLib/FlyTarget.cpp:53` — `return (TYPE_OBJECT==GetType());`

#### `Entity::GetPixelPosition`
*Konum (hack):* `HyperBot/Entity.cpp:127-134` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstancePosition.cpp:83` (CActorInstance::GetPixelPosition)

**Ne işe yarar:** Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Kanıt (LegendySF):** `UserInterface/PythonCharacterModule.cpp:727,865`

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRotation.cpp:100` — `pInstance->GetPixelPosition(&PixelPosition);`
- `client: GameLib/GameEventManager.cpp:18` — `pActorInstance->GetPixelPosition(&PixelPosition);`
- `client: GameLib/FlyingObjectManager.cpp:177` — `pStartActor->GetPixelPosition(&posStart);`

#### `Entity::GetRace`
*Konum (hack):* `HyperBot/Entity.cpp:134-140` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstanceData.cpp:51` (CActorInstance::GetRace); `client: UserInterface/InstanceBase.cpp:2232` (CInstanceBase::GetRace)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceData.cpp:51` — `DWORD CActorInstance::GetRace()`
- `client: GameLib/ActorInstanceBattle.cpp:567` — `if (IS_HUGE_RACE(rkActorDst.GetRace()))`
- `client: GameLib/ActorInstanceBattle.cpp:609` — `if (IS_PARTY_HUNTING_RACE(rVictim.GetRace()))`

#### `Entity::GetJob`
*Konum (hack):* `HyperBot/Entity.cpp:140-145` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `server: game/src/char.cpp:1838` (CHARACTER::GetJob); `server: game/src/char.cpp:1846` (CHARACTER::GetJob)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `server: game/src/input_db.cpp:441` — `ch->GetDesc()->GetAccountTable().id, ch->GetPlayerID(), ch->GetLevel(), ch->GetJob(), ch->GetRealPoint(POINT_PLAYTIME));`
- `server: game/src/input_db.cpp:487` — `ch->GetJob(),`
- `server: game/src/char.cpp:852` — `SetPolymorph(GetJob(), true);`

#### `Entity::GetVirtualNumber`
*Konum (hack):* `HyperBot/Entity.cpp:153-158` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:2578` (CInstanceBase::GetVirtualNumber)

**Ne işe yarar:** Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Kanıt (LegendySF):** `client: CInstanceBase | hack: C4US GameFunctionsCustom.h:1030-1062`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:221` — `switch (CPythonNonPlayer::Instance().GetEventType(pkInst->GetVirtualNumber()))`
- `client: UserInterface/PythonCharacterModule.cpp:890` — `return Py_BuildValue("i", pkInst->GetVirtualNumber());`
- `client: UserInterface/InstanceBase.cpp:2526` — `int vnum = GetVirtualNumber();`

#### `Entity::GetRotation`
*Konum (hack):* `HyperBot/Entity.cpp:163-168` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstanceRotation.cpp:109` (CActorInstance::GetRotation); `client: EterLib/GrpObjectInstance.cpp:155` (CGraphicObjectInstance::GetRotation)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRotation.cpp:109` — `float CActorInstance::GetRotation()`
- `client: GameLib/ActorInstanceRender.cpp:96` — `D3DXMatrixRotationZ(&kD3DMatLook, D3DXToRadian(GetRotation()));`
- `client: GameLib/ActorInstance.cpp:376` — `SetAdvancingRotation(GetRotation());`

#### `Entity::GetLevel`
*Konum (hack):* `HyperBot/Entity.cpp:168-173` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:228` (SHORSE::GetLevel); `client: UserInterface/InstanceBase.cpp:2189` (CInstanceBase::GetLevel)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:1275` — `return Py_BuildValue("i", pInstance->GetLevel());`
- `client: UserInterface/PythonCharacterModule.cpp:1288` — `return Py_BuildValue("i", pInstance->GetLevel());`
- `client: UserInterface/InstanceBase.cpp:228` — `UINT CInstanceBase::SHORSE::GetLevel()`

#### `Entity::GetEmpireID`
*Konum (hack):* `HyperBot/Entity.cpp:173-178` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStream.cpp:803` (CPythonNetworkStream::GetEmpireID); `client: UserInterface/InstanceBase.cpp:546` (CInstanceBase::GetEmpireID)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.cpp:803` — `DWORD CPythonNetworkStream::GetEmpireID()`
- `client: UserInterface/InstanceBase.cpp:546` — `DWORD CInstanceBase::GetEmpireID()`
- `client: UserInterface/PythonNetworkStreamModule.cpp:130` — `return Py_BuildValue("i", rkNetStream.GetEmpireID());`

#### `Entity::GetBoundBox`
*Konum (hack):* `HyperBot/Entity.cpp:178-185` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/DungeonBlock.cpp:177` (CDungeonBlock::GetBoundBox); `client: EterGrnLib/ModelInstanceCollisionDetection.cpp:181` (CGrannyModelInstance::GetBoundBox)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/DungeonBlock.cpp:120` — `pInstance->GetBoundBox(m_pv3Min, m_pv3Max);`
- `client: GameLib/DungeonBlock.cpp:177` — `void CDungeonBlock::GetBoundBox(D3DXVECTOR3 * pv3Min, D3DXVECTOR3 * pv3Max)`
- `client: GameLib/DungeonBlock.cpp:193` — `pInstance->GetBoundBox(&v3Min, &v3Max);`

#### `Entity::IsGameMaster`
*Konum (hack):* `HyperBot/Entity.cpp:194-202` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:516` (CInstanceBase::IsGameMaster)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:194` — `return Py_BuildValue("i", pInstance->IsGameMaster());`
- `client: UserInterface/InstanceBase.cpp:516` — `BOOL CInstanceBase::IsGameMaster()`
- `client: UserInterface/InstanceBase.cpp:534` — `if (IsGameMaster())`

#### `Entity::IsAttacking`
*Konum (hack):* `HyperBot/Entity.cpp:202-209` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBaseMovement.cpp:216` (CInstanceBase::IsAttacking)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBase.h:654` — `BOOL IsAttacking();`
- `client: UserInterface/InstanceBaseBattle.cpp:466` — `if (!__IsMainInstance() && !IsAttacking())`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2253` — `if (!pkInstMain->IsAttacking())`

#### `Entity::IsPartyMember`
*Konum (hack):* `HyperBot/Entity.cpp:234-241` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:638` (CInstanceBase::IsPartyMember)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:207` — `return Py_BuildValue("i", pInstance->IsPartyMember());`
- `client: UserInterface/InstanceBase.cpp:638` — `bool CInstanceBase::IsPartyMember()`
- `client: UserInterface/InstanceBase.h:580` — `bool IsPartyMember();`

#### `Entity::IsPartyMember`
*Konum (hack):* `HyperBot/Entity.cpp:241-247` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:638` (CInstanceBase::IsPartyMember)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:207` — `return Py_BuildValue("i", pInstance->IsPartyMember());`
- `client: UserInterface/InstanceBase.cpp:638` — `bool CInstanceBase::IsPartyMember()`
- `client: UserInterface/InstanceBase.h:580` — `bool IsPartyMember();`

#### `Entity::SCRIPT_SetPixelPosition`
*Konum (hack):* `HyperBot/Entity.cpp:252-259` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBaseTransform.cpp:8` (CInstanceBase::SCRIPT_SetPixelPosition)

**Ne işe yarar:** Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set edilir. Paket GONDERMEZ - sadece client ici gorunum/fizik konumunu degistirir. C4US Boost'un ilk adimi budur: lokal tasi, sonra state paketiyle sunucuyu haberdar et.

**İmza (oyun):** `void CInstanceBase::SCRIPT_SetPixelPosition(float fx, float fy)`
**Parametreler:** fx, fy: float - dunya piksel koordinatlari (z otomatik zeminden)
**Typedef kullanımı:** TPixelPosition (fx, fy, fz float uclusu)
**Bununla ne yapılabilir:** Ile ne yapilir: cagirilirsa karakter client'ta istenilen yere isinlanir (wallhack/teleport gorunumu). Sunucuya hareket paketi eslik etmezse sunucu tarafindan 'geri cekilirsiniz' (pozisyon resync) alinir; bu yuzden Boost gibi sarmalayicilar TPacketCGMove ile birlikte kullanir.
**Kanıt (LegendySF):** `UserInterface/InstanceBaseTransform.cpp:8-12`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBaseTransform.cpp:8` — `void CInstanceBase::SCRIPT_SetPixelPosition(float fx, float fy)`
- `client: UserInterface/PythonCharacterModule.cpp:699` — `pkInst->SCRIPT_SetPixelPosition(iX, iY);`
- `client: UserInterface/InstanceBase.cpp:827` — `SCRIPT_SetPixelPosition(float(c_rkCreateData.m_lPosX), float(c_rkCreateData.m_lPosY));`

### Sınıf: `GameMainInstance` (3 fonksiyon)

#### `GameMainInstance::GetItem`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:113-158` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ✅ VAR — `client: EterPack/EterPack.cpp:1562` (CEterFileDict::GetItem); `server: game/src/char_item.cpp:268` (CHARACTER::GetItem)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterPack/EterPack.h:93` — `Item* GetItem(DWORD dwFileNameHash, const char* c_pszFileName);`
- `client: EterPack/EterPack.cpp:1562` — `CEterFileDict::Item* CEterFileDict::GetItem(DWORD dwFileNameHash, const char * c_pszFileName)`
- `client: EterPack/EterPackManager.cpp:215` — `CEterFileDict::Item* pkFileItem = m_FileDict.GetItem(dwFileNameHash, strFileName.c_str());`

#### `GameMainInstance::GetItem`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:158-170` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ✅ VAR — `client: EterPack/EterPack.cpp:1562` (CEterFileDict::GetItem); `server: game/src/char_item.cpp:268` (CHARACTER::GetItem)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterPack/EterPack.h:93` — `Item* GetItem(DWORD dwFileNameHash, const char* c_pszFileName);`
- `client: EterPack/EterPack.cpp:1562` — `CEterFileDict::Item* CEterFileDict::GetItem(DWORD dwFileNameHash, const char * c_pszFileName)`
- `client: EterPack/EterPackManager.cpp:215` — `CEterFileDict::Item* pkFileItem = m_FileDict.GetItem(dwFileNameHash, strFileName.c_str());`

#### `GameMainInstance::GetBackground`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:229-235` | *Proje:* HyperBot | *Kategori:* config
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:120` (CActorInstance::GetBackground)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:120` — `IBackground& CActorInstance::GetBackground()`
- `client: GameLib/ActorInstanceMotionEvent.cpp:330` — `IBackground& rkBG=GetBackground();`
- `client: GameLib/ActorInstanceMotionEvent.cpp:365` — `IBackground& rkBG=GetBackground();`

### Sınıf: `GroundItemData` (3 fonksiyon)

#### `GroundItemData::GetPixelPosition`
*Konum (hack):* `HyperBot/Item.cpp:56-63` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstancePosition.cpp:83` (CActorInstance::GetPixelPosition)

**Ne işe yarar:** Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Kanıt (LegendySF):** `UserInterface/PythonCharacterModule.cpp:727,865`

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRotation.cpp:100` — `pInstance->GetPixelPosition(&PixelPosition);`
- `client: GameLib/GameEventManager.cpp:18` — `pActorInstance->GetPixelPosition(&PixelPosition);`
- `client: GameLib/FlyingObjectManager.cpp:177` — `pStartActor->GetPixelPosition(&posStart);`

#### `GroundItemData::GetVirtualNumber`
*Konum (hack):* `HyperBot/Item.cpp:63-68` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:2578` (CInstanceBase::GetVirtualNumber)

**Ne işe yarar:** Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Kanıt (LegendySF):** `client: CInstanceBase | hack: C4US GameFunctionsCustom.h:1030-1062`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:221` — `switch (CPythonNonPlayer::Instance().GetEventType(pkInst->GetVirtualNumber()))`
- `client: UserInterface/PythonCharacterModule.cpp:890` — `return Py_BuildValue("i", pkInst->GetVirtualNumber());`
- `client: UserInterface/InstanceBase.cpp:2526` — `int vnum = GetVirtualNumber();`

#### `GroundItemData::GetBoundBox`
*Konum (hack):* `HyperBot/Item.cpp:68-74` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/DungeonBlock.cpp:177` (CDungeonBlock::GetBoundBox); `client: EterGrnLib/ModelInstanceCollisionDetection.cpp:181` (CGrannyModelInstance::GetBoundBox)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/DungeonBlock.cpp:120` — `pInstance->GetBoundBox(m_pv3Min, m_pv3Max);`
- `client: GameLib/DungeonBlock.cpp:177` — `void CDungeonBlock::GetBoundBox(D3DXVECTOR3 * pv3Min, D3DXVECTOR3 * pv3Max)`
- `client: GameLib/DungeonBlock.cpp:193` — `pInstance->GetBoundBox(&v3Min, &v3Max);`

### Sınıf: `HookManager` (27 fonksiyon)

#### `HookManager::BlockMovement`
*Konum (hack):* `HyperBot/BlockMovement.cpp:1-10` | *Proje:* HyperBot | *Kategori:* movement
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstanceCollisionDetection.cpp:661` (CActorInstance::BlockMovement); `client: UserInterface/InstanceBase.cpp:309` (CInstanceBase::BlockMovement)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:617` — `BlockMovement();`
- `client: GameLib/ActorInstanceCollisionDetection.cpp:661` — `void CActorInstance::BlockMovement()`
- `client: GameLib/ActorInstance.h:332` — `void BlockMovement();`

#### `HookManager::EndScene`
*Konum (hack):* `HyperBot/D3DDevice.cpp:1-201` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/StateManager.cpp:51` (CStateManager::EndScene)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/StateManager.h:239` — `void EndScene();`
- `client: EterLib/GrpShadowTexture.cpp:128` — `ms_lpd3dDevice->EndScene();`
- `client: EterLib/StateManager.cpp:51` — `void CStateManager::EndScene()`

#### `HookManager::__ShowMapName`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:1-8` | *Proje:* HyperBot | *Kategori:* hook
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:876` (CPythonNetworkStream::__ShowMapName)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamPhaseGameActor.cpp:336` — `__ShowMapName(pkNetActorData->m_lCurX, pkNetActorData->m_lCurY);`
- `client: UserInterface/PythonNetworkStreamPhaseGameActor.cpp:341` — `__ShowMapName(pkNetActorData->m_lCurX, pkNetActorData->m_lCurY);`
- `client: UserInterface/PythonNetworkStream.h:629` — `void __ShowMapName(LONG lLocalX, LONG lLocalY);`

#### `HookManager::SendAttackPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:8-27` | *Proje:* HyperBot | *Kategori:* attack_packet
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` (CPythonNetworkStream::SendAttackPacket)

**Ne işe yarar:** Melee saldiri talebi: TPacketCGAttack{header=HEADER_CG_ATTACK, bType=uMotAttack(0=normal,1=combo), dwVictimVID} doldurup SendSpecial ile yollar; SendSpecial saldiri paketlerine CRCMagicCube baytlarini ekler (sunucu anti-cheat), sonra SendSequence sirayi muhurler. Hasari sunucu hesaplar - client yalnizca 'vuruyorum' der.

**İmza (oyun):** `bool CPythonNetworkStream::SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim)`
**Parametreler:** uMotAttack: UINT - saldiri tipi (0 normal, 1 combo) | dwVIDVictim: DWORD - kurban VID
**Typedef kullanımı:** TPacketCGAttack { BYTE header; BYTE bType; DWORD dwVictimVID; BYTE bCRCMagicCubeProcPiece; BYTE bCRCMagicCubeFilePiece; } (server packet.h:656)
**Server karşılığı:** HEADER_CG_ATTACK -> input_main.cpp:1750 -> CInputMain::Attack (1702): CRC dogrulama, victim bulma, mesafe kontrolu, char->Attack -> battle.cpp hasar
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:2599-2624`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:146` — `bool SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` — `bool CPythonNetworkStream::SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:168` — `rkStream.SendAttackPacket(uSkill, dwVIDVictim);`

#### `HookManager::SendOnClickPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:29-35` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` (CPythonNetworkStream::SendOnClickPacket)

**Ne işe yarar:** Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bayt yamasi).

**Typedef kullanımı:** TPacketCGOnClick
**Server karşılığı:** HEADER_CG_ON_CLICK -> input_main.cpp:3367 -> CInputMain::OnClick

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:681` — `rkNetStream.SendOnClickPacket(index);`
- `client: UserInterface/PythonNetworkStream.h:198` — `bool SendOnClickPacket(DWORD vid);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` — `bool CPythonNetworkStream::SendOnClickPacket(DWORD vid)`

#### `HookManager::SendScriptAnswerPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:35-41` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` (CPythonNetworkStream::SendScriptAnswerPacket)

**Ne işe yarar:** NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Server karşılığı:** HEADER_CG_SCRIPT_ANSWER -> dispatcher

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:191` — `bool SendScriptAnswerPacket(int iAnswer);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` — `bool CPythonNetworkStream::SendScriptAnswerPacket(int iAnswer)`
- `client: UserInterface/PythonEventManager.cpp:905` — `CPythonNetworkStream::Instance().SendScriptAnswerPacket(iAnswer);`

#### `HookManager::SendGiveItemPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:41-47` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` (CPythonNetworkStream::SendGiveItemPacket)

**Ne işe yarar:** Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.

**Server karşılığı:** HEADER_CG_ITEM_GIVE -> input_main.cpp:3322

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:973` — `rkNetStream.SendGiveItemPacket(iTargetVID, Cell, iItemCount);`
- `client: UserInterface/PythonNetworkStream.h:261` — `bool SendGiveItemPacket(DWORD dwTargetVID, TItemPos ItemPos, int iItemCount);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` — `bool CPythonNetworkStream::SendGiveItemPacket(DWORD dwTargetVID, TItemPos ItemPos, int iItemCount)`

#### `HookManager::SendShootPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:47-53` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` (CPythonNetworkStream::SendShootPacket)

**Ne işe yarar:** Yay/ok atisi: HEADER_CG_SHOOT + uSkill. Genellikle AddFlyTargeting ile ciftli calisir (mermi hedefi).

**Server karşılığı:** HEADER_CG_SHOOT -> input_main.cpp:1784 -> CInputMain::Shoot

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:203` — `bool SendShootPacket(UINT uSkill);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` — `bool CPythonNetworkStream::SendShootPacket(UINT uSkill)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:242` — `rpns.SendShootPacket(dwSkillIndex);`

#### `HookManager::SendTargetPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:53-59` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` (CPythonNetworkStream::SendTargetPacket)

**Ne işe yarar:** Hedef secim bildirimi (dwVID); sunucu hedef dogrulayip HP/uzaklik bilgisi yollar (HEADER_GC_TARGET).

**Server karşılığı:** HEADER_CG_TARGET -> CInputMain (dispatcher) -> hedef state

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:149` — `bool SendTargetPacket(DWORD dwVID);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` — `bool CPythonNetworkStream::SendTargetPacket(DWORD dwVID)`
- `client: UserInterface/PythonPlayerInput.cpp:109` — `CPythonNetworkStream::Instance().SendTargetPacket(0);`

#### `HookManager::SendAddFlyTargetingPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:59-65` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736` (CPythonNetworkStream::SendAddFlyTargetingPacket)

**Ne işe yarar:** Ucan mermi (ok/beceri) icin hedef kaydi: dwTargetVID + TPixelPosition varis noktasi; sunucu merminin isabetini buna gore cozer.

**Typedef kullanımı:** TPacketCGFlyTargeting, TPixelPosition
**Server karşılığı:** HEADER_CG_ADD_FLY_TARGETING -> input_main.cpp:3376

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:682` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(pkInstEach->GetVirtualID(), pkInstEach->GetGraphicThingInstanceRef().OnGetFlyTargetPosition`
- `client: UserInterface/PythonPlayerSkill.cpp:704` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(pkInstEach->GetVirtualID(), pkInstEach->GetGraphicThingInstanceRef().OnGetFlyTargetPosition`
- `client: UserInterface/PythonPlayerSkill.cpp:723` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(0, kPPosDst);`

#### `HookManager::SendFlyTargetingPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:65-71` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` (CPythonNetworkStream::SendFlyTargetingPacket)

**Ne işe yarar:** Ucan hedef guncellemesi (mevcut mermi icin hedef tazeleme).

**Server karşılığı:** HEADER_CG_FLY_TARGETING -> dispatcher

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:201` — `bool SendFlyTargetingPacket(DWORD dwTargetVID, const TPixelPosition& kPPosTarget);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` — `bool CPythonNetworkStream::SendFlyTargetingPacket(DWORD dwTargetVID, const TPixelPosition & kPPosTarget)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:237` — `rpns.SendFlyTargetingPacket(m_pInstTarget->GetVirtualID(), m_pInstTarget->GetGraphicThingInstancePtr()->OnGetFlyTargetPosition());`

#### `HookManager::SendScriptButtonPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:71-77` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2312` (CPythonNetworkStream::SendScriptButtonPacket)

**Ne işe yarar:** Quest diyalog butonuna basma bildirimi (ilerlet/kapat).

**Server karşılığı:** HEADER_CG_SCRIPT_BUTTON -> dispatcher

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:192` — `bool SendScriptButtonPacket(unsigned int iIndex);`
- `client: UserInterface/PythonEventManagerMoudle.cpp:238` — `CPythonNetworkStream::Instance().SendScriptButtonPacket(iIndex);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2312` — `bool CPythonNetworkStream::SendScriptButtonPacket(unsigned int iIndex)`

#### `HookManager::SendRefinePacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:77-83` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` (CPythonNetworkStream::SendRefinePacket)

**Ne işe yarar:** Gelistirme (refine) onayi: esya konumu + gelistirme tipi; sunucu malzeme/oran kontrolu yapar.

**Server karşılığı:** HEADER_CG_REFINE -> CInputMain::Refine

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:1689` — `rns.SendRefinePacket(iSlotIndex, iType);`
- `client: UserInterface/PythonNetworkStream.h:267` — `bool SendRefinePacket(BYTE byPos, BYTE byType);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` — `bool CPythonNetworkStream::SendRefinePacket(BYTE byPos, BYTE byType)`

#### `HookManager::SendCharacterStatePacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:89-95` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` (CPythonNetworkStream::SendCharacterStatePacket); `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1178` (CPythonNetworkStream::SendCharacterStatePacket)

**Ne işe yarar:** Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, konumu __LocalPositionToGlobalPosition ile global harita koordinatina cevirir (x<204800 assert'i: harita siniri). bFunc: hareket tipi (yurume/kosma/bekleme...), dwTime sunucu saatiyle hiz desync tespiti icin.

**İmza (oyun):** `bool CPythonNetworkStream::SendCharacterStatePacket(const TPixelPosition&, float fDstRot, UINT eFunc, UINT uArg)`
**Parametreler:** TPixelPosition hedef konum | fDstRot float yon | eFunc UINT hareket fonksiyonu | uArg UINT ek arguman
**Typedef kullanımı:** TPacketCGMove, TPixelPosition
**Server karşılığı:** HEADER_CG_CHARACTER_MOVE (HEADER_CG_MOVE ailesi) -> input_main.cpp:3263 -> CInputMain::Move -> SyncPosition
**Bununla ne yapılabilir:** Ile ne yapilir: bu paketi kucuk adimlarla + sik gondermek Boost tarzi hiz saglar (sunucu adimlar arasi mesafeyi toparlar, tek seferlik buyuk sifrelemede kick gelir). bRot 5 dereceye yuvarlandigi icin hizli yon degisimi kaybolur; dwTime sunucu saatiyle kontrol edildiginden gecmis/zaman istismari tespit edilir.
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:1152-1192`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerInputMouse.cpp:303` — `rkNetStream.SendCharacterStatePacket(kPPosCur, fCurRot, CInstanceBase::FUNC_WAIT, 0);`
- `client: UserInterface/PythonNetworkStream.h:147` — `bool SendCharacterStatePacket(const TPixelPosition& c_rkPPosDst, float fDstRot, UINT eFunc, UINT uArg);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` — `bool CPythonNetworkStream::SendCharacterStatePacket(const TPixelPosition& c_rkPPosDst, float fDstRot, UINT eFunc, UINT uArg)`

#### `HookManager::SendUseSkillPacket`
*Konum (hack):* `HyperBot/DevModeHooks.cpp:95-101` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191` (CPythonNetworkStream::SendUseSkillPacket)

**Ne işe yarar:** Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.

**İmza (oyun):** `bool CPythonNetworkStream::SendUseSkillPacket(DWORD dwSkillIndex, DWORD dwTargetVID=0)`
**Typedef kullanımı:** TPacketCGUseSkill { BYTE header; DWORD dwVnum; DWORD dwTargetVID; }
**Server karşılığı:** HEADER_CG_USE_SKILL -> input_main.cpp:3340 -> CInputMain::UseSkill -> char->UseSkill
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:1193-1206`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:139` — `CPythonNetworkStream::Instance().SendUseSkillPacket(rkSkillInst.dwIndex);`
- `client: UserInterface/PythonPlayerSkill.cpp:482` — `CPythonNetworkStream::Instance().SendUseSkillPacket(rkSkillInst.dwIndex, dwSlotIndex);`
- `client: UserInterface/PythonPlayerSkill.cpp:756` — `rkNetStream.SendUseSkillPacket(rkSkillInst.dwIndex, dwTargetVID);`

#### `HookManager::IncreaseExternalForce`
*Konum (hack):* `HyperBot/IncreaseExternalForce.cpp:1-13` | *Proje:* HyperBot | *Kategori:* movement
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/PhysicsObject.cpp:53` (CPhysicsObject::IncreaseExternalForce)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/PhysicsObject.cpp:53` — `void CPhysicsObject::IncreaseExternalForce(const D3DXVECTOR3 & c_rvBasePosition, float fForce)`
- `client: GameLib/PhysicsObject.h:71` — `void IncreaseExternalForce(const D3DXVECTOR3 & c_rvBasePosition, float fForce);`
- `client: GameLib/ActorInstanceBattle.cpp:602` — `rVictim.m_PhysicsObject.IncreaseExternalForce(kVictimPos, c_rAttackData.fExternalForce); //*nForceRatio/100.0f);`

#### `HookManager::Send`
*Konum (hack):* `HyperBot/NetworkStream.cpp:1-24` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:758` (CNetworkStream::Send); `client: EterLib/NetStream.cpp:821` (CNetworkStream::Send)

**Ne işe yarar:** (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Kanıt (LegendySF):** `client: UserInterface/PythonNetworkStream.cpp (Send/SendSpecial) | hack: HyperBot Network.cpp:104`

**Oyunda çağrıldığı yerler:**
- `client: ScriptLib/PythonUtils.cpp:320` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/PythonUtils.cpp:368` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/StdAfx.h:53` — `virtual void Send() = 0;`

#### `HookManager::Recv`
*Konum (hack):* `HyperBot/NetworkStream.cpp:24-42` | *Proje:* HyperBot | *Kategori:* packet_recv
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:718` (CNetworkStream::Recv); `client: EterLib/NetStream.cpp:727` (CNetworkStream::Recv)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:718` — `bool CNetworkStream::Recv(int size)`
- `client: EterLib/NetStream.cpp:727` — `bool CNetworkStream::Recv(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:808` — `bool CNetworkStream::Recv(int len, void* pDestBuf)`

#### `HookManager::RecvDamageInfoPacket`
*Konum (hack):* `HyperBot/NetworkStream.cpp:42-84` | *Proje:* HyperBot | *Kategori:* packet_recv
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2451` (CPythonNetworkStream::RecvDamageInfoPacket)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).
**Paket:** `TPacketGCDamageInfo` → `BYTE header`, `DWORD dwVID`, `BYTE flag`, `int damage`
**Paket:** `TPacketGCTarget` → `BYTE header`, `DWORD dwVID`, `BYTE bHPPercent`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:509` — `bool RecvDamageInfoPacket();`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:405` — `ret = RecvDamageInfoPacket();`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2451` — `bool CPythonNetworkStream::RecvDamageInfoPacket()`

#### `HookManager::OnScriptEventStart`
*Konum (hack):* `HyperBot/OnScriptEventStart.cpp:1-12` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamEvent.cpp:15` (CPythonNetworkStream::OnScriptEventStart)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamEvent.cpp:15` — `void CPythonNetworkStream::OnScriptEventStart(int iSkin, int iIndex)`
- `client: UserInterface/PythonNetworkStream.h:609` — `void OnScriptEventStart(int iSkin, int iIndex);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2291` — `CPythonNetworkStream::Instance().OnScriptEventStart(ScriptPacket.skin,iIndex);`

#### `HookManager::ProcessTerrainCollision`
*Konum (hack):* `HyperBot/ProcessTerrainCollision.cpp:1-10` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/CameraProcedure.cpp:12` (CCamera::ProcessTerrainCollision)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/Camera.h:219` — `void ProcessTerrainCollision();`
- `client: UserInterface/CameraProcedure.cpp:12` — `void CCamera::ProcessTerrainCollision()`
- `client: UserInterface/CameraProcedure.cpp:316` — `ProcessTerrainCollision();`

#### `HookManager::RecvWhisperPacket`
*Konum (hack):* `HyperBot/RecvWhisperPacket.cpp:1-9` | *Proje:* HyperBot | *Kategori:* packet_recv
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1448` (CPythonNetworkStream::RecvWhisperPacket)

**Ne işe yarar:** TPacketGCWhisper, TPacketCGWhisper yapısını doldurup HEADER_CG_WHISPER başlığıyla sunucuya gönderir; ayarladığı alanlar: bHeader. İstemciden sunucuya giden bir talep fonksiyonudur.
**Paket:** `TPacketGCWhisper` → `BYTE bHeader`, `WORD wSize`, `BYTE bType`
**Paket:** `TPacketCGWhisper` → `BYTE bHeader`, `WORD wSize`
**Header:** `HEADER_CG_WHISPER`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:468` — `bool RecvWhisperPacket();`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:298` — `ret = RecvWhisperPacket();`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1448` — `bool CPythonNetworkStream::RecvWhisperPacket()`

#### `HookManager::RenderGame`
*Konum (hack):* `HyperBot/RenderGame.cpp:1-31` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonApplication.cpp:168` (CPythonApplication::RenderGame)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonApplicationModule.cpp:415` — `CPythonApplication::Instance().RenderGame();`
- `client: UserInterface/PythonApplication.cpp:168` — `void CPythonApplication::RenderGame()`
- `client: UserInterface/PythonApplication.h:167` — `void RenderGame();`

#### `HookManager::TestActorCollision`
*Konum (hack):* `HyperBot/TestActorCollision.cpp:1-10` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstanceCollisionDetection.cpp:555` (CActorInstance::TestActorCollision)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceCollisionDetection.cpp:555` — `BOOL CActorInstance::TestActorCollision(CActorInstance & rVictim)`
- `client: GameLib/ActorInstanceCollisionDetection.cpp:560` — `if (m_pkHorse->TestActorCollision(rVictim))`
- `client: GameLib/ActorInstance.h:339` — `BOOL TestActorCollision(CActorInstance& rVictim);`

#### `HookManager::UpdateGame`
*Konum (hack):* `HyperBot/UpdateGame.cpp:3-92` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonApplication.cpp:321` (CPythonApplication::UpdateGame)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonApplicationModule.cpp:409` — `CPythonApplication::Instance().UpdateGame();`
- `client: UserInterface/PythonApplication.cpp:321` — `void CPythonApplication::UpdateGame()`
- `client: UserInterface/PythonApplication.h:166` — `void UpdateGame();`

#### `HookManager::UpdateKeyboard`
*Konum (hack):* `HyperBot/UpdateKeyboard.cpp:1-13` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/Input.cpp:88` (CInputKeyboard::UpdateKeyboard)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/Input.h:26` — `void UpdateKeyboard();`
- `client: EterLib/Input.cpp:88` — `void CInputKeyboard::UpdateKeyboard()`
- `client: UserInterface/PythonApplication.cpp:474` — `UpdateKeyboard();`

#### `HookManager::__SendHack`
*Konum (hack):* `HyperBot/__SendHack.cpp:1-8` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` (CPythonNetworkStream::__SendHack)

**Ne işe yarar:** TPacketCGHack, TPacketCGMessenger yapısını doldurup HEADER_CG_HACK, HEADER_CG_MESSENGER başlığıyla sunucuya gönderir; ayarladığı alanlar: bHeader, header. İstemciden sunucuya giden bir talep fonksiyonudur.
**Paket:** `TPacketCGHack` → `BYTE bHeader`
**Paket:** `TPacketCGMessenger` → `BYTE header`, `BYTE subheader`
**Header:** `HEADER_CG_HACK`, `HEADER_CG_MESSENGER`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:411` — `bool __SendHack(const char* c_szMsg);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:198` — `__SendHack(m_kQue_stHack.front().c_str());`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` — `bool CPythonNetworkStream::__SendHack(const char* c_szMsg)`

### Sınıf: `Item` (1 fonksiyon)

#### `Item::GetItemData`
*Konum (hack):* `HyperBot/Item.cpp:26-40` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonShop.cpp:65` (CPythonShop::GetItemData); `client: UserInterface/PythonShop.cpp:84` (CPythonShop::GetItemData)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonShop.cpp:11` — `// if (!GetItemData(dwSlotPos, &itemData))`
- `client: UserInterface/PythonShop.cpp:65` — `BOOL CPythonShop::GetItemData(DWORD dwIndex, const TShopItemData ** c_ppItemData)`
- `client: UserInterface/PythonShop.cpp:70` — `return GetItemData(tabIdx, dwSlotPos, c_ppItemData);`

### Sınıf: `ItemData` (3 fonksiyon)

#### `ItemData::GetType`
*Konum (hack):* `HyperBot/Item.cpp:137-143` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/FlyTarget.cpp:73` (CFlyTarget::GetType); `client: GameLib/ItemData.cpp:241` (CItemData::GetType)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:530` — `if (TYPE_BUILDING != GetType())`
- `client: GameLib/RaceMotionData.h:237` — `UINT GetType() const;`
- `client: GameLib/FlyTarget.cpp:53` — `return (TYPE_OBJECT==GetType());`

#### `ItemData::GetSubType`
*Konum (hack):* `HyperBot/Item.cpp:143-149` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ItemData.cpp:246` (CItemData::GetSubType)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ItemData.cpp:246` — `BYTE CItemData::GetSubType() const`
- `client: GameLib/ItemData.cpp:258` — `switch (GetSubType())`
- `client: GameLib/ItemData.cpp:298` — `if (GetType()==CItemData::ITEM_TYPE_COSTUME && GetSubType()==CItemData::COSTUME_WEAPON)`

#### `ItemData::GetRefineLevel`
*Konum (hack):* `HyperBot/Item.cpp:149-159` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `server: game/src/item.cpp:1555` (CItem::GetRefineLevel)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `server: game/src/mining.cpp:162` — `return defaultPct + SkillLevelAddPct[MINMAX(0, iSkillLevel, 40)] + PickGradeAddPct[MINMAX(0, pick->GetRefineLevel(), 9)];`
- `server: game/src/questlua_pc.cpp:1550` — `lua_pushnumber(L, item->GetRefineLevel());`
- `server: game/src/questlua_pc.cpp:1581` — `if (item->GetRefineLevel() > level_limit)`

### Sınıf: `Math` (1 fonksiyon)

#### `Math::GetDistance`
*Konum (hack):* `HyperBot/Math.cpp:13-18` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:2619` (CInstanceBase::GetDistance); `client: UserInterface/InstanceBase.cpp:2626` (CInstanceBase::GetDistance)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoorUpdate.cpp:235` — `float fDistance = pCamera->GetDistance();`
- `client: EterLib/GrpLightManager.cpp:96` — `return l->GetDistance() < r->GetDistance();`
- `client: EterLib/GrpLightManager.cpp:96` — `return l->GetDistance() < r->GetDistance();`

### Sınıf: `Matrix` (3 fonksiyon)

#### `Matrix::Transform`
*Konum (hack):* `HyperBot/matrix.h:151-155` | *Proje:* HyperBot | *Kategori:* gui
**Oyunda karşılığı:** ✅ VAR — `client: EffectLib/ParticleInstance.cpp:124` (CParticleInstance::Transform); `client: EffectLib/ParticleInstance.cpp:276` (CParticleInstance::Transform)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Area.cpp:420` — `pObjectInstance->pThingInstance->Transform();`
- `client: GameLib/ActorInstance.cpp:41` — `Transform();`
- `client: GameLib/DungeonBlock.cpp:71` — `Transform();`

#### `Matrix::Rotate`
*Konum (hack):* `HyperBot/matrix.h:155-158` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpBase.cpp:414` (CGraphicBase::Rotate)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterPythonLib/PythonGraphicModule.cpp:266` — `CPythonGraphic::Instance().Rotate(Degree, x, y, z);`
- `client: EterLib/GrpBase.h:179` — `void Rotate(float degree, float x, float y, float z);`
- `client: EterLib/GrpBase.cpp:414` — `void CGraphicBase::Rotate(float degree, float x, float y, float z)`

#### `Matrix::Identity`
*Konum (hack):* `HyperBot/matrix.h:176-180` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EffectLib/ParticleSystemInstance.cpp:419` (CScreen::Identity); `client: EterLib/GrpScreen.cpp:830` (CScreen::Identity)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/ParticleSystemInstance.cpp:419` — `CScreen::Identity();`
- `client: EterPythonLib/PythonGraphicModule.cpp:803` — `CPythonGraphic::Instance().Identity();`
- `client: EterLib/GrpScreen.cpp:830` — `void CScreen::Identity()`

### Sınıf: `MatrixCppImpl4x4` (2 fonksiyon)

#### `MatrixCppImpl4x4::Transform`
*Konum (hack):* `HyperBot/matrix_impl.h:177-191` | *Proje:* HyperBot | *Kategori:* gui
**Oyunda karşılığı:** ✅ VAR — `client: EffectLib/ParticleInstance.cpp:124` (CParticleInstance::Transform); `client: EffectLib/ParticleInstance.cpp:276` (CParticleInstance::Transform)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Area.cpp:420` — `pObjectInstance->pThingInstance->Transform();`
- `client: GameLib/ActorInstance.cpp:41` — `Transform();`
- `client: GameLib/DungeonBlock.cpp:71` — `Transform();`

#### `MatrixCppImpl4x4::Rotate`
*Konum (hack):* `HyperBot/matrix_impl.h:191-203` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpBase.cpp:414` (CGraphicBase::Rotate)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterPythonLib/PythonGraphicModule.cpp:266` — `CPythonGraphic::Instance().Rotate(Degree, x, y, z);`
- `client: EterLib/GrpBase.h:179` — `void Rotate(float degree, float x, float y, float z);`
- `client: EterLib/GrpBase.cpp:414` — `void CGraphicBase::Rotate(float degree, float x, float y, float z)`

### Sınıf: `Network` (21 fonksiyon)

#### `Network::SendRefinePacket`
*Konum (hack):* `HyperBot/Network.cpp:7-14` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` (CPythonNetworkStream::SendRefinePacket)

**Ne işe yarar:** Gelistirme (refine) onayi: esya konumu + gelistirme tipi; sunucu malzeme/oran kontrolu yapar.

**Server karşılığı:** HEADER_CG_REFINE -> CInputMain::Refine

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:1689` — `rns.SendRefinePacket(iSlotIndex, iType);`
- `client: UserInterface/PythonNetworkStream.h:267` — `bool SendRefinePacket(BYTE byPos, BYTE byType);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` — `bool CPythonNetworkStream::SendRefinePacket(BYTE byPos, BYTE byType)`

#### `Network::Recv`
*Konum (hack):* `HyperBot/Network.cpp:14-21` | *Proje:* HyperBot | *Kategori:* packet_recv
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:718` (CNetworkStream::Recv); `client: EterLib/NetStream.cpp:727` (CNetworkStream::Recv)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:718` — `bool CNetworkStream::Recv(int size)`
- `client: EterLib/NetStream.cpp:727` — `bool CNetworkStream::Recv(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:808` — `bool CNetworkStream::Recv(int len, void* pDestBuf)`

#### `Network::IsConnected`
*Konum (hack):* `HyperBot/Network.cpp:28-33` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `server: game/src/log.cpp:50` (LogManager::IsConnected); `server: game/src/db.cpp:104` (DBManager::IsConnected)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `server: game/src/db.h:85` — `bool IsConnected();`
- `server: game/src/db.h:196` — `bool IsConnected();`
- `server: game/src/log.h:45` — `bool IsConnected();`

#### `Network::ConnectGameServer`
*Konum (hack):* `HyperBot/Network.cpp:33-40` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStream.cpp:499` (CPythonNetworkStream::ConnectGameServer)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.cpp:499` — `void CPythonNetworkStream::ConnectGameServer(UINT iChrSlot)`
- `client: UserInterface/PythonNetworkStreamModule.cpp:480` — `rkNetStream.ConnectGameServer(nChrSlot);`
- `client: UserInterface/PythonNetworkStream.h:130` — `void ConnectGameServer(UINT iChrSlot);`

#### `Network::SetLoginInfo`
*Konum (hack):* `HyperBot/Network.cpp:40-52` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/AccountConnector.cpp:25` (CAccountConnector::SetLoginInfo); `client: UserInterface/PythonNetworkStream.cpp:512` (CPythonNetworkStream::SetLoginInfo)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/AccountConnector.cpp:25` — `void CAccountConnector::SetLoginInfo(const char * c_szName, const char * c_szPwd)`
- `client: UserInterface/AccountConnector.cpp:488` — `rkNet.SetLoginInfo(kAuthSuccessOpenIDPacket.login, "0000");`
- `client: UserInterface/AccountConnector.cpp:724` — `SetLoginInfo("", "");`

#### `Network::SelectAnswer`
*Konum (hack):* `HyperBot/Network.cpp:52-59` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonEventManager.cpp:898` (CPythonEventManager::SelectAnswer)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonEventManagerMoudle.cpp:195` — `CPythonEventManager::Instance().SelectAnswer(iIndex, iAnswer);`
- `client: UserInterface/PythonEventManager.cpp:898` — `void CPythonEventManager::SelectAnswer(int iIndex, int iAnswer)`
- `client: UserInterface/PythonEventManager.h:180` — `void SelectAnswer(int iIndex, int iAnswer);`

#### `Network::Send`
*Konum (hack):* `HyperBot/Network.cpp:102-109` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:758` (CNetworkStream::Send); `client: EterLib/NetStream.cpp:821` (CNetworkStream::Send)

**Ne işe yarar:** (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Kanıt (LegendySF):** `client: UserInterface/PythonNetworkStream.cpp (Send/SendSpecial) | hack: HyperBot Network.cpp:104`

**Oyunda çağrıldığı yerler:**
- `client: ScriptLib/PythonUtils.cpp:320` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/PythonUtils.cpp:368` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/StdAfx.h:53` — `virtual void Send() = 0;`

#### `Network::SendChatPacket`
*Konum (hack):* `HyperBot/Network.cpp:127-134` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206` (CPythonNetworkStream::SendChatPacket)

**Ne işe yarar:** Sohbet mesaji: TPacketCGChat{header, len, type} + metin; type: NORMAL/SHOUT/PARTY/GUILD/WHISPER... Bosluk mesaj yollamaz; client sutun siniri uygular, sunucu rate-limit ve renk/kanal kurallari uygular.

**İmza (oyun):** `bool CPythonNetworkStream::SendChatPacket(const char* c_szChat, BYTE byType)`
**Server karşılığı:** HEADER_CG_CHAT -> input_main.cpp:3247 -> CInputMain::Chat
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:1207+`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.cpp:222` — `SendChatPacket("/quit");`
- `client: UserInterface/PythonNetworkStream.cpp:234` — `SendChatPacket("/phase_select");`
- `client: UserInterface/PythonNetworkStream.cpp:247` — `SendChatPacket("/logout");`

#### `Network::SendAttackPacket`
*Konum (hack):* `HyperBot/Network.cpp:134-142` | *Proje:* HyperBot | *Kategori:* attack_packet
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` (CPythonNetworkStream::SendAttackPacket)

**Ne işe yarar:** Melee saldiri talebi: TPacketCGAttack{header=HEADER_CG_ATTACK, bType=uMotAttack(0=normal,1=combo), dwVictimVID} doldurup SendSpecial ile yollar; SendSpecial saldiri paketlerine CRCMagicCube baytlarini ekler (sunucu anti-cheat), sonra SendSequence sirayi muhurler. Hasari sunucu hesaplar - client yalnizca 'vuruyorum' der.

**İmza (oyun):** `bool CPythonNetworkStream::SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim)`
**Parametreler:** uMotAttack: UINT - saldiri tipi (0 normal, 1 combo) | dwVIDVictim: DWORD - kurban VID
**Typedef kullanımı:** TPacketCGAttack { BYTE header; BYTE bType; DWORD dwVictimVID; BYTE bCRCMagicCubeProcPiece; BYTE bCRCMagicCubeFilePiece; } (server packet.h:656)
**Server karşılığı:** HEADER_CG_ATTACK -> input_main.cpp:1750 -> CInputMain::Attack (1702): CRC dogrulama, victim bulma, mesafe kontrolu, char->Attack -> battle.cpp hasar
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:2599-2624`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:146` — `bool SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` — `bool CPythonNetworkStream::SendAttackPacket(UINT uMotAttack, DWORD dwVIDVictim)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:168` — `rkStream.SendAttackPacket(uSkill, dwVIDVictim);`

#### `Network::__SendHack`
*Konum (hack):* `HyperBot/Network.cpp:150-156` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` (CPythonNetworkStream::__SendHack)

**Ne işe yarar:** TPacketCGHack, TPacketCGMessenger yapısını doldurup HEADER_CG_HACK, HEADER_CG_MESSENGER başlığıyla sunucuya gönderir; ayarladığı alanlar: bHeader, header. İstemciden sunucuya giden bir talep fonksiyonudur.
**Paket:** `TPacketCGHack` → `BYTE bHeader`
**Paket:** `TPacketCGMessenger` → `BYTE header`, `BYTE subheader`
**Header:** `HEADER_CG_HACK`, `HEADER_CG_MESSENGER`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:411` — `bool __SendHack(const char* c_szMsg);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:198` — `__SendHack(m_kQue_stHack.front().c_str());`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` — `bool CPythonNetworkStream::__SendHack(const char* c_szMsg)`

#### `Network::SendAddFlyTargetingPacket`
*Konum (hack):* `HyperBot/Network.cpp:156-164` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736` (CPythonNetworkStream::SendAddFlyTargetingPacket)

**Ne işe yarar:** Ucan mermi (ok/beceri) icin hedef kaydi: dwTargetVID + TPixelPosition varis noktasi; sunucu merminin isabetini buna gore cozer.

**Typedef kullanımı:** TPacketCGFlyTargeting, TPixelPosition
**Server karşılığı:** HEADER_CG_ADD_FLY_TARGETING -> input_main.cpp:3376

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:682` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(pkInstEach->GetVirtualID(), pkInstEach->GetGraphicThingInstanceRef().OnGetFlyTargetPosition`
- `client: UserInterface/PythonPlayerSkill.cpp:704` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(pkInstEach->GetVirtualID(), pkInstEach->GetGraphicThingInstanceRef().OnGetFlyTargetPosition`
- `client: UserInterface/PythonPlayerSkill.cpp:723` — `CPythonNetworkStream::Instance().SendAddFlyTargetingPacket(0, kPPosDst);`

#### `Network::SendFlyTargetingPacket`
*Konum (hack):* `HyperBot/Network.cpp:164-172` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` (CPythonNetworkStream::SendFlyTargetingPacket)

**Ne işe yarar:** Ucan hedef guncellemesi (mevcut mermi icin hedef tazeleme).

**Server karşılığı:** HEADER_CG_FLY_TARGETING -> dispatcher

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:201` — `bool SendFlyTargetingPacket(DWORD dwTargetVID, const TPixelPosition& kPPosTarget);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` — `bool CPythonNetworkStream::SendFlyTargetingPacket(DWORD dwTargetVID, const TPixelPosition & kPPosTarget)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:237` — `rpns.SendFlyTargetingPacket(m_pInstTarget->GetVirtualID(), m_pInstTarget->GetGraphicThingInstancePtr()->OnGetFlyTargetPosition());`

#### `Network::SendOnClickPacket`
*Konum (hack):* `HyperBot/Network.cpp:180-188` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` (CPythonNetworkStream::SendOnClickPacket)

**Ne işe yarar:** Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bayt yamasi).

**Typedef kullanımı:** TPacketCGOnClick
**Server karşılığı:** HEADER_CG_ON_CLICK -> input_main.cpp:3367 -> CInputMain::OnClick

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:681` — `rkNetStream.SendOnClickPacket(index);`
- `client: UserInterface/PythonNetworkStream.h:198` — `bool SendOnClickPacket(DWORD vid);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` — `bool CPythonNetworkStream::SendOnClickPacket(DWORD vid)`

#### `Network::SendScriptAnswerPacket`
*Konum (hack):* `HyperBot/Network.cpp:188-196` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` (CPythonNetworkStream::SendScriptAnswerPacket)

**Ne işe yarar:** NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Server karşılığı:** HEADER_CG_SCRIPT_ANSWER -> dispatcher

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:191` — `bool SendScriptAnswerPacket(int iAnswer);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` — `bool CPythonNetworkStream::SendScriptAnswerPacket(int iAnswer)`
- `client: UserInterface/PythonEventManager.cpp:905` — `CPythonNetworkStream::Instance().SendScriptAnswerPacket(iAnswer);`

#### `Network::SendGiveItemPacket`
*Konum (hack):* `HyperBot/Network.cpp:196-204` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` (CPythonNetworkStream::SendGiveItemPacket)

**Ne işe yarar:** Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.

**Server karşılığı:** HEADER_CG_ITEM_GIVE -> input_main.cpp:3322

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:973` — `rkNetStream.SendGiveItemPacket(iTargetVID, Cell, iItemCount);`
- `client: UserInterface/PythonNetworkStream.h:261` — `bool SendGiveItemPacket(DWORD dwTargetVID, TItemPos ItemPos, int iItemCount);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` — `bool CPythonNetworkStream::SendGiveItemPacket(DWORD dwTargetVID, TItemPos ItemPos, int iItemCount)`

#### `Network::SendItemUsePacket`
*Konum (hack):* `HyperBot/Network.cpp:204-212` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486` (CPythonNetworkStream::SendItemUsePacket)

**Ne işe yarar:** Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Typedef kullanımı:** TPacketCGItemUse, TItemPos { BYTE window_type; WORD cell; }
**Server karşılığı:** HEADER_CG_ITEM_USE -> input_main.cpp:3272 -> CInputMain::ItemUse

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:706` — `rkNetStream.SendItemUsePacket(Cell);`
- `client: UserInterface/PythonNetworkStream.h:158` — `bool SendItemUsePacket(TItemPos pos);`
- `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486` — `bool CPythonNetworkStream::SendItemUsePacket(TItemPos pos)`

#### `Network::SendItemUseToItemPacket`
*Konum (hack):* `HyperBot/Network.cpp:212-220` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524` (CPythonNetworkStream::SendItemUseToItemPacket)

**Ne işe yarar:** Esyayi baska esya uzerinde kullanma (tas ekleme, bonus degistirme materyali): kaynak/hedef cell.

**Server karşılığı:** HEADER_CG_ITEM_USE_TO_ITEM -> input_main.cpp:3317

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:740` — `rkNetStream.SendItemUseToItemPacket(SourceCell, TargetCell);`
- `client: UserInterface/PythonNetworkStream.h:159` — `bool SendItemUseToItemPacket(TItemPos source_pos, TItemPos target_pos);`
- `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524` — `bool CPythonNetworkStream::SendItemUseToItemPacket(TItemPos source_pos, TItemPos target_pos)`

#### `Network::SendShootPacket`
*Konum (hack):* `HyperBot/Network.cpp:220-228` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` (CPythonNetworkStream::SendShootPacket)

**Ne işe yarar:** Yay/ok atisi: HEADER_CG_SHOOT + uSkill. Genellikle AddFlyTargeting ile ciftli calisir (mermi hedefi).

**Server karşılığı:** HEADER_CG_SHOOT -> input_main.cpp:1784 -> CInputMain::Shoot

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:203` — `bool SendShootPacket(UINT uSkill);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` — `bool CPythonNetworkStream::SendShootPacket(UINT uSkill)`
- `client: UserInterface/PythonPlayerEventHandler.cpp:242` — `rpns.SendShootPacket(dwSkillIndex);`

#### `Network::SendUseSkillPacket`
*Konum (hack):* `HyperBot/Network.cpp:228-236` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191` (CPythonNetworkStream::SendUseSkillPacket)

**Ne işe yarar:** Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.

**İmza (oyun):** `bool CPythonNetworkStream::SendUseSkillPacket(DWORD dwSkillIndex, DWORD dwTargetVID=0)`
**Typedef kullanımı:** TPacketCGUseSkill { BYTE header; DWORD dwVnum; DWORD dwTargetVID; }
**Server karşılığı:** HEADER_CG_USE_SKILL -> input_main.cpp:3340 -> CInputMain::UseSkill -> char->UseSkill
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:1193-1206`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:139` — `CPythonNetworkStream::Instance().SendUseSkillPacket(rkSkillInst.dwIndex);`
- `client: UserInterface/PythonPlayerSkill.cpp:482` — `CPythonNetworkStream::Instance().SendUseSkillPacket(rkSkillInst.dwIndex, dwSlotIndex);`
- `client: UserInterface/PythonPlayerSkill.cpp:756` — `rkNetStream.SendUseSkillPacket(rkSkillInst.dwIndex, dwTargetVID);`

#### `Network::SendTargetPacket`
*Konum (hack):* `HyperBot/Network.cpp:236-244` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` (CPythonNetworkStream::SendTargetPacket)

**Ne işe yarar:** Hedef secim bildirimi (dwVID); sunucu hedef dogrulayip HP/uzaklik bilgisi yollar (HEADER_GC_TARGET).

**Server karşılığı:** HEADER_CG_TARGET -> CInputMain (dispatcher) -> hedef state

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStream.h:149` — `bool SendTargetPacket(DWORD dwVID);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` — `bool CPythonNetworkStream::SendTargetPacket(DWORD dwVID)`
- `client: UserInterface/PythonPlayerInput.cpp:109` — `CPythonNetworkStream::Instance().SendTargetPacket(0);`

#### `Network::SendCharacterStatePacket`
*Konum (hack):* `HyperBot/Network.cpp:244-252` | *Proje:* HyperBot | *Kategori:* packet_send
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` (CPythonNetworkStream::SendCharacterStatePacket); `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1178` (CPythonNetworkStream::SendCharacterStatePacket)

**Ne işe yarar:** Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, konumu __LocalPositionToGlobalPosition ile global harita koordinatina cevirir (x<204800 assert'i: harita siniri). bFunc: hareket tipi (yurume/kosma/bekleme...), dwTime sunucu saatiyle hiz desync tespiti icin.

**İmza (oyun):** `bool CPythonNetworkStream::SendCharacterStatePacket(const TPixelPosition&, float fDstRot, UINT eFunc, UINT uArg)`
**Parametreler:** TPixelPosition hedef konum | fDstRot float yon | eFunc UINT hareket fonksiyonu | uArg UINT ek arguman
**Typedef kullanımı:** TPacketCGMove, TPixelPosition
**Server karşılığı:** HEADER_CG_CHARACTER_MOVE (HEADER_CG_MOVE ailesi) -> input_main.cpp:3263 -> CInputMain::Move -> SyncPosition
**Bununla ne yapılabilir:** Ile ne yapilir: bu paketi kucuk adimlarla + sik gondermek Boost tarzi hiz saglar (sunucu adimlar arasi mesafeyi toparlar, tek seferlik buyuk sifrelemede kick gelir). bRot 5 dereceye yuvarlandigi icin hizli yon degisimi kaybolur; dwTime sunucu saatiyle kontrol edildiginden gecmis/zaman istismari tespit edilir.
**Kanıt (LegendySF):** `UserInterface/PythonNetworkStreamPhaseGame.cpp:1152-1192`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerInputMouse.cpp:303` — `rkNetStream.SendCharacterStatePacket(kPPosCur, fCurRot, CInstanceBase::FUNC_WAIT, 0);`
- `client: UserInterface/PythonNetworkStream.h:147` — `bool SendCharacterStatePacket(const TPixelPosition& c_rkPPosDst, float fDstRot, UINT eFunc, UINT uArg);`
- `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` — `bool CPythonNetworkStream::SendCharacterStatePacket(const TPixelPosition& c_rkPPosDst, float fDstRot, UINT eFunc, UINT uArg)`

### Sınıf: `Player` (8 fonksiyon)

#### `Player::DismountHorse`
*Konum (hack):* `HyperBot/Entity.cpp:299-304` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:1068` (CInstanceBase::DismountHorse)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonCharacterModule.cpp:555` — `pkInst->DismountHorse();`
- `client: UserInterface/InstanceBase.cpp:1068` — `void CInstanceBase::DismountHorse()`
- `client: UserInterface/InstanceBase.cpp:3356` — `DismountHorse();`

#### `Player::MountHorse`
*Konum (hack):* `HyperBot/Entity.cpp:304-309` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:784` (CActorInstance::MountHorse); `client: UserInterface/InstanceBase.cpp:1055` (CInstanceBase::MountHorse)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:784` — `void CActorInstance::MountHorse(CActorInstance * pkHorse)`
- `client: GameLib/ActorInstance.h:531` — `void MountHorse(CActorInstance* pkHorse);`
- `client: UserInterface/PythonCharacterModule.cpp:546` — `pkInst->MountHorse(20030);`

#### `Player::IsMountingHorse`
*Konum (hack):* `HyperBot/Entity.cpp:309-314` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBase.cpp:1050` (CInstanceBase::IsMountingHorse)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBase.cpp:295` — `if (!IsMountingHorse())`
- `client: UserInterface/InstanceBase.cpp:302` — `if (!IsMountingHorse())`
- `client: UserInterface/InstanceBase.cpp:1050` — `BOOL CInstanceBase::IsMountingHorse()`

#### `Player::StartWalking`
*Konum (hack):* `HyperBot/Entity.cpp:321-328` | *Proje:* HyperBot | *Kategori:* movement
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBaseMovement.cpp:149` (CInstanceBase::StartWalking)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBase.cpp:1451` — `StartWalking();`
- `client: UserInterface/InstanceBase.cpp:1484` — `StartWalking();`
- `client: UserInterface/InstanceBase.cpp:1506` — `StartWalking();`

#### `Player::GetPickingPosition`
*Konum (hack):* `HyperBot/Entity.cpp:328-335` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpScreen.cpp:582` (CScreen::GetPickingPosition)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/GrpScreen.cpp:582` — `void CScreen::GetPickingPosition(float t, float* x, float* y, float* z)`
- `client: EterLib/GrpScreen.h:62` — `void GetPickingPosition(float t, float* x, float* y, float* z);`

#### `Player::SetRotation`
*Konum (hack):* `HyperBot/Entity.cpp:335-340` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstanceRotation.cpp:10` (CActorInstance::SetRotation); `client: GameLib/ActorInstanceRotation.cpp:67` (CGraphicObjectInstance::SetRotation)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRotation.cpp:10` — `void CActorInstance::SetRotation(float fRot)`
- `client: GameLib/ActorInstanceRotation.cpp:13` — `m_pkHorse->SetRotation(fRot);`
- `client: GameLib/ActorInstanceRotation.cpp:67` — `CGraphicObjectInstance::SetRotation(m_rotX, m_rotY, m_fcurRotation);`

#### `Player::IsBowMode`
*Konum (hack):* `HyperBot/Entity.cpp:413-420` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:262` (CActorInstance::IsBowMode); `client: UserInterface/InstanceBase.cpp:1226` (CInstanceBase::IsBowMode)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:170` — `if (IsBowMode())`
- `client: GameLib/ActorInstance.cpp:262` — `bool CActorInstance::IsBowMode()`
- `client: GameLib/ActorInstanceBattle.cpp:178` — `if (IsBowMode())`

#### `Player::SetTarget`
*Konum (hack):* `HyperBot/Entity.cpp:427-432` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/Camera.cpp:235` (CCamera::SetTarget); `client: UserInterface/PythonPlayerEventHandler.cpp:252` (CNormalBowAttack_FlyEventHandler_AutoClear::SetTarget)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/Camera.cpp:235` — `void CCamera::SetTarget(const D3DXVECTOR3 & v3Target)`
- `client: EterLib/GrpBase.cpp:248` — `pCamera->SetTarget(v3Target);`
- `client: EterLib/Camera.h:176` — `void SetTarget(const D3DXVECTOR3 & v3Target);`

### Sınıf: `RouteCreator` (3 fonksiyon)

#### `RouteCreator::Play`
*Konum (hack):* `HyperBot/RouteCreator.cpp:296-323` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: MilesLib/SoundInstanceStream.cpp:45` (CSoundInstanceStream::Play); `client: MilesLib/SoundInstance3D.cpp:65` (CSoundInstance3D::Play)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: MilesLib/SoundInstance.h:15` — `virtual void Play(int iLoopCount = 1, DWORD dwPlayCycleTimeLimit = 0) const = 0;`
- `client: MilesLib/SoundInstance.h:39` — `void Play(int iLoopCount = 1, DWORD dwPlayCycleTimeLimit = 0) const;`
- `client: MilesLib/SoundInstance.h:67` — `void Play(int iLoopCount = 1, DWORD dwPlayCycleTimeLimit = 0) const;`

#### `RouteCreator::OnUseItem`
*Konum (hack):* `HyperBot/RouteCreator.cpp:345-355` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ✅ VAR — `server: game/src/questnpc.cpp:280` (NPC::OnUseItem)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: game/src/questnpc.h:67` — `bool OnUseItem(PC& pc, bool bReceiveAll);`
- `server: game/src/questmanager.cpp:834` — `return m_mapNPC[item->GetVnum()].OnUseItem(*pPC, bReceiveAll);`
- `server: game/src/questnpc.cpp:280` — `bool NPC::OnUseItem(PC& pc, bool bReceiveAll)`

#### `RouteCreator::OnPickupItem`
*Konum (hack):* `HyperBot/RouteCreator.cpp:418-428` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ✅ VAR — `server: game/src/questnpc.cpp:966` (NPC::OnPickupItem)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: game/src/questnpc.h:81` — `bool OnPickupItem(PC& pc);`
- `server: game/src/questmanager.cpp:1950` — `return m_mapNPC[item->GetVnum()].OnPickupItem(*pPC);`
- `server: game/src/questnpc.cpp:966` — `bool NPC::OnPickupItem(PC& pc)`

### Sınıf: `SPacketGCHybridCryptKeys` (1 fonksiyon)

#### `SPacketGCHybridCryptKeys::GetFixedHeaderSize`
*Konum (hack):* `HyperBot/PacketDefs.h:2627-2631` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/AccountConnector.cpp:388` (TPacketGCHybridCryptKeys::GetFixedHeaderSize); `client: UserInterface/AccountConnector.cpp:404` (TPacketGCHybridSDB::GetFixedHeaderSize)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.
**Paket:** `TPacketGCPing` → `BYTE header`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/AccountConnector.cpp:388` — `int iFixedHeaderSize = TPacketGCHybridCryptKeys::GetFixedHeaderSize();`
- `client: UserInterface/AccountConnector.cpp:404` — `int iFixedHeaderSize = TPacketGCHybridSDB::GetFixedHeaderSize();`
- `client: UserInterface/PythonNetworkStreamPhaseHandShake.cpp:172` — `int iFixedHeaderSize = TPacketGCHybridCryptKeys::GetFixedHeaderSize();`

### Sınıf: `SPacketGCHybridSDB` (1 fonksiyon)

#### `SPacketGCHybridSDB::GetFixedHeaderSize`
*Konum (hack):* `HyperBot/PacketDefs.h:2655-2659` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/AccountConnector.cpp:388` (TPacketGCHybridCryptKeys::GetFixedHeaderSize); `client: UserInterface/AccountConnector.cpp:404` (TPacketGCHybridSDB::GetFixedHeaderSize)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.
**Paket:** `TPacketGCPing` → `BYTE header`

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/AccountConnector.cpp:388` — `int iFixedHeaderSize = TPacketGCHybridCryptKeys::GetFixedHeaderSize();`
- `client: UserInterface/AccountConnector.cpp:404` — `int iFixedHeaderSize = TPacketGCHybridSDB::GetFixedHeaderSize();`
- `client: UserInterface/PythonNetworkStreamPhaseHandShake.cpp:172` — `int iFixedHeaderSize = TPacketGCHybridCryptKeys::GetFixedHeaderSize();`

### Sınıf: `Screen` (6 fonksiyon)

#### `Screen::SetDepth`
*Konum (hack):* `HyperBot/Screen.cpp:91-96` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpExpandedImageInstance.cpp:143` (CGraphicExpandedImageInstance::SetDepth)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/GrpExpandedImageInstance.h:29` — `void SetDepth(float fDepth);`
- `client: EterLib/GrpExpandedImageInstance.cpp:143` — `void CGraphicExpandedImageInstance::SetDepth(float fDepth)`
- `client: EterLib/GrpMarkInstance.h:23` — `void SetDepth(float fDepth);`

#### `Screen::SetRenderState`
*Konum (hack):* `HyperBot/Screen.cpp:176-192` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/StateManager.cpp:453` (CStateManager::SetRenderState)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRender.cpp:114` — `STATEMANAGER.SetRenderState(D3DRS_LIGHTING, FALSE);`
- `client: GameLib/ActorInstanceRender.cpp:122` — `STATEMANAGER.SetRenderState(D3DRS_LIGHTING, TRUE);`
- `client: GameLib/ActorInstanceRender.cpp:178` — `STATEMANAGER.SetRenderState(D3DRS_TEXTUREFACTOR, D3DXCOLOR(1.0f, 1.0f, 1.0f, m_fAlphaValue));`

#### `Screen::RestoreRenderState`
*Konum (hack):* `HyperBot/Screen.cpp:192-210` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ✅ VAR — `client: EterGrnLib/Material.cpp:46` (CGrannyMaterial::RestoreRenderState); `client: EterLib/StateManager.cpp:439` (CStateManager::RestoreRenderState)

**Ne işe yarar:** Görsel/arayüz katmanı fonksiyonu; render/overlay akışına katkı sağlar (oyun tarafında karşılığı soyutluktur).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstanceRender.cpp:85` — `STATEMANAGER.RestoreRenderState(D3DRS_CULLMODE);`
- `client: GameLib/ActorInstanceRender.cpp:123` — `STATEMANAGER.RestoreRenderState(D3DRS_ZENABLE);`
- `client: GameLib/ActorInstanceRender.cpp:146` — `STATEMANAGER.RestoreRenderState(D3DRS_ALPHABLENDENABLE);`

#### `Screen::__CreatePDTVertexBufferList`
*Konum (hack):* `HyperBot/Screen.cpp:371-388` | *Proje:* HyperBot | *Kategori:* module
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpDevice.cpp:616` (CGraphicDevice::__CreatePDTVertexBufferList)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/GrpDevice.h:63` — `bool __CreatePDTVertexBufferList();`
- `client: EterLib/GrpDevice.cpp:560` — `if (!__CreatePDTVertexBufferList())`
- `client: EterLib/GrpDevice.cpp:616` — `bool CGraphicDevice::__CreatePDTVertexBufferList()`

#### `Screen::__DestroyPDTVertexBufferList`
*Konum (hack):* `HyperBot/Screen.cpp:388-400` | *Proje:* HyperBot | *Kategori:* module
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpDevice.cpp:604` (CGraphicDevice::__DestroyPDTVertexBufferList)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/GrpDevice.h:62` — `void __DestroyPDTVertexBufferList();`
- `client: EterLib/GrpDevice.cpp:604` — `void CGraphicDevice::__DestroyPDTVertexBufferList()`
- `client: EterLib/GrpDevice.cpp:720` — `__DestroyPDTVertexBufferList();`

#### `Screen::GetTextSize`
*Konum (hack):* `HyperBot/Screen.cpp:652-664` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: EterPythonLib/PythonWindow.cpp:1018` (CTextLine::GetTextSize); `client: EterLib/GrpTextInstance.cpp:1119` (CGraphicTextInstance::GetTextSize)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterPythonLib/PythonGraphicTextModule.cpp:40` — `pTextInstance->GetTextSize(&width, &height);`
- `client: EterPythonLib/PythonWindow.cpp:1018` — `void CTextLine::GetTextSize(int* pnWidth, int* pnHeight)`
- `client: EterPythonLib/PythonWindow.cpp:1020` — `m_TextInstance.GetTextSize(pnWidth, pnHeight);`

### Sınıf: `Skill` (5 fonksiyon)

#### `Skill::GetSkillData`
*Konum (hack):* `HyperBot/Skill.cpp:1-6` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonSkill.cpp:747` (CPythonSkill::GetSkillData)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonItem.cpp:507` — `if ((dwSkillVnum != 0) && CPythonSkill::Instance().GetSkillData(dwSkillVnum, &c_pSkillData))`
- `client: UserInterface/PythonPlayerSkill.cpp:26` — `if (!CPythonSkill::Instance().GetSkillData(dwSkillIndex, &pSkillData))`
- `client: UserInterface/PythonPlayerSkill.cpp:48` — `if (!CPythonSkill::Instance().GetSkillData(dwSkillIndex, &pSkillData))`

#### `Skill::IsSkillCoolTime`
*Konum (hack):* `HyperBot/Skill.cpp:139-147` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayer.cpp:1168` (CPythonPlayer::IsSkillCoolTime)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerModule.cpp:524` — `return Py_BuildValue("i", CPythonPlayer::Instance().IsSkillCoolTime(iSlotIndex));`
- `client: UserInterface/PythonPlayer.h:402` — `BOOL IsSkillCoolTime(DWORD dwSlotIndex);`
- `client: UserInterface/PythonPlayer.cpp:1168` — `BOOL CPythonPlayer::IsSkillCoolTime(DWORD dwSlotIndex)`

#### `Skill::IsSkillActive`
*Konum (hack):* `HyperBot/Skill.cpp:147-156` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayer.cpp:1176` (CPythonPlayer::IsSkillActive)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:131` — `if (IsSkillActive(dwSlotIndex))`
- `client: UserInterface/PythonPlayerSkill.cpp:480` — `if (IsSkillActive(dwSlotIndex))`
- `client: UserInterface/PythonPlayerModule.cpp:544` — `return Py_BuildValue("i", CPythonPlayer::Instance().IsSkillActive(iSlotIndex));`

#### `Skill::GetSkillIndex`
*Konum (hack):* `HyperBot/Skill.cpp:164-172` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayer.cpp:980` (CPythonPlayer::GetSkillIndex)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerModule.cpp:669` — `return Py_BuildValue("i", CPythonPlayer::Instance().GetSkillIndex(iSlotIndex));`
- `client: UserInterface/PythonPlayer.h:384` — `int GetSkillIndex(DWORD dwSlotIndex);`
- `client: UserInterface/PythonPlayer.cpp:980` — `int CPythonPlayer::GetSkillIndex(DWORD dwSlotIndex)`

#### `Skill::UseSkill`
*Konum (hack):* `HyperBot/Skill.cpp:182-190` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `server: game/src/char_skill.cpp:98` (TSkillUseInfo::UseSkill); `server: game/src/char_skill.cpp:2431` (CHARACTER::UseSkill)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: game/src/char_skill.cpp:98` — `bool TSkillUseInfo::UseSkill(bool isGrandMaster, DWORD vid, DWORD dwCooltime, int splashcount, int hitcount, int range)`
- `server: game/src/char_skill.cpp:2431` — `bool CHARACTER::UseSkill(DWORD dwVnum, LPCHARACTER pkVictim, bool bUseGrandMaster)`
- `server: game/src/char_skill.cpp:2518` — `if (!UseSkill(dwVnum, this))`

### Sınıf: `SkillData` (2 fonksiyon)

#### `SkillData::IsAttackSkill`
*Konum (hack):* `HyperBot/Skill.cpp:128-133` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonSkill.cpp:1207` (SSkillData::IsAttackSkill)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonPlayerSkill.cpp:198` — `if (pSkillData->IsAttackSkill())`
- `client: UserInterface/PythonSkill.h:195` — `BOOL IsAttackSkill();`
- `client: UserInterface/PythonSkill.cpp:1207` — `BOOL CPythonSkill::SSkillData::IsAttackSkill()`

#### `SkillData::GetTexture`
*Konum (hack):* `HyperBot/Skill.cpp:133-139` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ✅ VAR — `client: PRTerrainLib/TextureSet.cpp:116` (CTextureSet::GetTexture); `client: EterLib/StateManager.cpp:489` (CStateManager::GetTexture)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoorRenderHTP.cpp:420` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`
- `client: GameLib/MapOutdoorRenderHTP.cpp:444` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`
- `client: GameLib/MapOutdoorRenderHTP.cpp:526` — `const TTerrainTexture & rTexture = m_TextureSet.GetTexture(j);`

## 5. OYUNDA OLAN FONKSİYONLAR — C4US

> Her giriş: **oyunda karşılığı**, **imza**, **parametreler**, **typedef**, **ne işe yarar**, **paket/server karşılığı**, **oyunda çağrıldığı yerler**.

### Dosya: `EngineX-Pro/AutoTalk.h` (1 fonksiyon)

#### `AutoTalk::OnStop`
*Konum (hack):* `EngineX-Pro/AutoTalk.h:9-13` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Buff.h` (1 fonksiyon)

#### `Buff::OnStop`
*Konum (hack):* `EngineX-Pro/Buff.h:125-131` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/CRender.cpp` (2 fonksiyon)

#### `GenerateTexture`
*Konum (hack):* `EngineX-Pro/CRender.cpp:55-74` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/SkyBox.cpp:155` (CSkyObject::GenerateTexture)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/SkyBox.cpp:155` — `CGraphicImageInstance * CSkyObject::GenerateTexture(const char * szfilename)`
- `client: EterLib/SkyBox.cpp:260` — `CGraphicImageInstance * pGraphicImageInstance = GenerateTexture(c_szFileName);`
- `client: EterLib/SkyBox.cpp:272` — `CGraphicImageInstance * pGraphicImageInstance = GenerateTexture(c_szFileName);`

#### `CRender::RenderSphere`
*Konum (hack):* `EngineX-Pro/CRender.cpp:221-250` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpScreen.cpp:369` (CScreen::RenderSphere)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Area.cpp:1322` — `RenderSphere(NULL, fx, fy, fz, float(dwRange) * fMaxVolumeAreaPercentage, D3DFILL_POINT);`
- `client: GameLib/Area.cpp:1323` — `RenderSphere(NULL, fx, fy, fz, float(dwRange), D3DFILL_POINT);`
- `client: EterLib/CollisionData.cpp:221` — `s.RenderSphere(NULL, m_attribute.v3Position.x, m_attribute.v3Position.y, m_attribute.v3Position.z, m_attribute.fRadius, d3dFillMode);`

### Dosya: `EngineX-Pro/Configuration.h` (1 fonksiyon)

#### `Configuration::OnStop`
*Konum (hack):* `EngineX-Pro/Configuration.h:29-33` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Debug.h` (1 fonksiyon)

#### `Debug::OnStop`
*Konum (hack):* `EngineX-Pro/Debug.h:16-20` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/DynamicTimer.h` (1 fonksiyon)

#### `DynamicTimer::Check`
*Konum (hack):* `EngineX-Pro/DynamicTimer.h:26-48` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `server: game/src/skill_power.cpp:8` (CTableBySkill::Check); `server: game/src/exchange.cpp:280` (CExchange::Check)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: game/src/skill_power.h:22` — `bool Check() const;`
- `server: game/src/skill_power.cpp:8` — `bool CTableBySkill::Check() const`
- `server: game/src/exchange.cpp:280` — `bool CExchange::Check(int * piItemCount)`

### Dosya: `EngineX-Pro/Farm.h` (1 fonksiyon)

#### `Farm::OnStop`
*Konum (hack):* `EngineX-Pro/Farm.h:56-63` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/FileExtension.h` (4 fonksiyon)

#### `FileExtension::Read`
*Konum (hack):* `EngineX-Pro/FileExtension.h:83-89` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/MappedFile.cpp:229` (CMappedFile::Read); `client: EterBase/FileBase.cpp:106` (CFileBase::Read)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ItemManager.cpp:281` — `file.Read(&dwFourCC, sizeof(DWORD));`
- `client: GameLib/ItemManager.cpp:285` — `file.Read(&dwVersion, sizeof(DWORD));`
- `client: GameLib/ItemManager.cpp:286` — `file.Read(&dwStride, sizeof(DWORD));`

#### `FileExtension::Write`
*Konum (hack):* `EngineX-Pro/FileExtension.h:89-95` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/FileBase.cpp:94` (CFileBase::Write); `client: EterPack/EterPack.cpp:113` (CMakePackLog::Write)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Property.cpp:131` — `file.Write(&fourcc, sizeof(DWORD));`
- `client: GameLib/Property.cpp:132` — `file.Write("\r\n", 2);`
- `client: GameLib/Property.cpp:147` — `file.Write(m_stCRC.c_str(), m_stCRC.length());`

#### `FileExtension::Write`
*Konum (hack):* `EngineX-Pro/FileExtension.h:95-102` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/FileBase.cpp:94` (CFileBase::Write); `client: EterPack/EterPack.cpp:113` (CMakePackLog::Write)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Property.cpp:131` — `file.Write(&fourcc, sizeof(DWORD));`
- `client: GameLib/Property.cpp:132` — `file.Write("\r\n", 2);`
- `client: GameLib/Property.cpp:147` — `file.Write(m_stCRC.c_str(), m_stCRC.length());`

#### `FileExtension::Read`
*Konum (hack):* `EngineX-Pro/FileExtension.h:110-116` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterBase/MappedFile.cpp:229` (CMappedFile::Read); `client: EterBase/FileBase.cpp:106` (CFileBase::Read)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ItemManager.cpp:281` — `file.Read(&dwFourCC, sizeof(DWORD));`
- `client: GameLib/ItemManager.cpp:285` — `file.Read(&dwVersion, sizeof(DWORD));`
- `client: GameLib/ItemManager.cpp:286` — `file.Read(&dwStride, sizeof(DWORD));`

### Dosya: `EngineX-Pro/Fish.h` (1 fonksiyon)

#### `Fish::OnStop`
*Konum (hack):* `EngineX-Pro/Fish.h:32-43` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/GameFunctionsCustom.h` (4 fonksiyon)

#### `GameFunctionsCustom::MountHorse`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:275-287` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:784` (CActorInstance::MountHorse); `client: UserInterface/InstanceBase.cpp:1055` (CInstanceBase::MountHorse)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:784` — `void CActorInstance::MountHorse(CActorInstance * pkHorse)`
- `client: GameLib/ActorInstance.h:531` — `void MountHorse(CActorInstance* pkHorse);`
- `client: UserInterface/PythonCharacterModule.cpp:546` — `pkInst->MountHorse(20030);`

#### `GameFunctionsCustom::GetD3DTexture`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1181-1215` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterGrnLib/Material.cpp:142` (CGrannyMaterial::GetD3DTexture); `client: EterLib/GrpShadowTexture.cpp:60` (CGraphicShadowTexture::GetD3DTexture)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: GameLib/MapOutdoorRender.cpp:629` — `STATEMANAGER.SetTexture(1, m_BuildingTransparentImageInstance.GetTexturePointer()->GetD3DTexture());`
- `client: GameLib/MapOutdoorRender.cpp:859` — `STATEMANAGER.SetTexture(0, m_attrImageInstance.GetTexturePointer()->GetD3DTexture());`
- `client: GameLib/FlyTrace.cpp:36` — `m_lpTexture = pTexture->GetD3DTexture();`

#### `GameFunctionsCustom::GetDegreeFromDirection`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1279-1302` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/InstanceBaseTransform.cpp:72` (CInstanceBase::GetDegreeFromDirection); `client: UserInterface/PythonPlayerInputKeyboard.cpp:91` (CPythonPlayer::GetDegreeFromDirection)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/InstanceBaseTransform.cpp:62` — `float fDegree = GetDegreeFromDirection(dir);`
- `client: UserInterface/InstanceBaseTransform.cpp:69` — `m_GraphicThingInstance.BlendRotation(GetDegreeFromDirection(dir), blendTime);`
- `client: UserInterface/InstanceBaseTransform.cpp:72` — `float CInstanceBase::GetDegreeFromDirection(int dir)`

#### `GameFunctionsCustom::GlobalPositionToLocalPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1504-1517` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonBackground.cpp:709` (CPythonBackground::GlobalPositionToLocalPosition)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamPhaseGameActor.cpp:17` — `rkBgMgr.GlobalPositionToLocalPosition(rGlobalX, rGlobalY);`
- `client: UserInterface/PythonApplication.cpp:1194` — `rkBG.GlobalPositionToLocalPosition(x, y);`
- `client: UserInterface/PythonBackground.cpp:709` — `void CPythonBackground::GlobalPositionToLocalPosition(LONG& rGlobalX, LONG& rGlobalY)`

### Dosya: `EngineX-Pro/Inventory.h` (1 fonksiyon)

#### `Inventory::OnStop`
*Konum (hack):* `EngineX-Pro/Inventory.h:9-13` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Item.h` (1 fonksiyon)

#### `Item::OnStop`
*Konum (hack):* `EngineX-Pro/Item.h:24-28` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Logger.h` (4 fonksiyon)

#### `LogWindow::GetColor`
*Konum (hack):* `EngineX-Pro/Logger.h:54-79` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: SphereLib/spherepack.cpp:388` (SpherePackFactory::GetColor); `client: EterLib/GrpBase.cpp:456` (CGraphicBase::GetColor)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: SphereLib/spherepack.cpp:174` — `mRoot->Render(mRoot->GetColor());`
- `client: SphereLib/spherepack.cpp:175` — `mLeaf->Render(mLeaf->GetColor());`
- `client: SphereLib/spherepack.cpp:217` — `link->GetColor());`

#### `LogWindow::Draw`
*Konum (hack):* `EngineX-Pro/Logger.h:140-210` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/LensFlare.cpp:524` (CFlare::Draw); `client: SpeedTreeLib/SpeedGrassWrapper.cpp:61` (CSpeedGrassWrapper::Draw)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/LensFlare.h:52` — `void Draw(float fBrightScale, int nWidth, int nHeight, int nX, int nY);`
- `client: EterLib/LensFlare.cpp:327` — `m_cFlare.Draw(m_fAfterBright,`
- `client: EterLib/LensFlare.cpp:524` — `void CFlare::Draw(float fBrightScale, int nWidth, int nHeight, int nX, int nY)`

#### `Logger::Add`
*Konum (hack):* `EngineX-Pro/Logger.h:224-245` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/Decal.cpp:257` (CDecalManager::Add); `server: game/src/marriage.cpp:555` (CManager::Add)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/PropertyManager.h:26` — `// bool Add(const char * c_pszFileName);`
- `client: EterLib/Decal.h:89` — `void Add(CDecal * pDecal);`
- `client: EterLib/Decal.cpp:257` — `void CDecalManager::Add(CDecal * pDecal)`

#### `Logger::Draw`
*Konum (hack):* `EngineX-Pro/Logger.h:245-250` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/LensFlare.cpp:524` (CFlare::Draw); `client: SpeedTreeLib/SpeedGrassWrapper.cpp:61` (CSpeedGrassWrapper::Draw)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/LensFlare.h:52` — `void Draw(float fBrightScale, int nWidth, int nHeight, int nX, int nY);`
- `client: EterLib/LensFlare.cpp:327` — `m_cFlare.Draw(m_fAfterBright,`
- `client: EterLib/LensFlare.cpp:524` — `void CFlare::Draw(float fBrightScale, int nWidth, int nHeight, int nX, int nY)`

### Dosya: `EngineX-Pro/Main.h` (3 fonksiyon)

#### `Main::OnStop`
*Konum (hack):* `EngineX-Pro/Main.h:160-168` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

#### `Main::Revive`
*Konum (hack):* `EngineX-Pro/Main.h:402-440` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/ActorInstance.cpp:538` (CActorInstance::Revive); `client: UserInterface/InstanceBaseBattle.cpp:660` (CInstanceBase::Revive)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.cpp:538` — `void CActorInstance::Revive()`
- `client: GameLib/ActorInstance.h:369` — `void Revive();`
- `client: UserInterface/PythonCharacterModule.cpp:564` — `pkInst->Revive();`

#### `Main::Target`
*Konum (hack):* `EngineX-Pro/Main.h:776-829` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `server: game/src/questmanager.cpp:705` (CQuestManager::Target); `server: game/src/input_main.cpp:2031` (CInputMain::Target)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: game/src/questmanager.h:126` — `bool Target(unsigned int pc, DWORD dwQuestIndex, const char * c_pszTargetName, const char * c_pszVerb);`
- `server: game/src/questmanager.cpp:705` — `bool CQuestManager::Target(unsigned int pc, DWORD dwQuestIndex, const char * c_pszTargetName, const char * c_pszVerb)`
- `server: game/src/cmd_gm.cpp:162` — `ch->ChatPacket(CHAT_TYPE_INFO, "Target(%s) is in %d channel (my channel %d)", arg1, pkCCI->bChannel, g_bChannel);`

### Dosya: `EngineX-Pro/MainDungs.h` (1 fonksiyon)

#### `MainDungs::OnStop`
*Konum (hack):* `EngineX-Pro/MainDungs.h:153-161` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/MemoryExtension.h` (2 fonksiyon)

#### `MemoryExtension::GetWord`
*Konum (hack):* `EngineX-Pro/MemoryExtension.h:106-112` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `server: db/src/Config.cpp:29` (CConfig::GetWord)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `server: db/src/Config.cpp:29` — `bool CConfig::GetWord(FILE *fp, char *tar)`
- `server: db/src/Config.cpp:109` — `while (GetWord(fp, szTmp))`
- `server: db/src/Config.h:18` — `bool GetWord(FILE* fp, char* dest);`

#### `MemoryExtension::SetRange`
*Konum (hack):* `EngineX-Pro/MemoryExtension.h:192-202` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/GrpLightManager.cpp:245` (CLight::SetRange)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EffectLib/SimpleLightInstance.cpp:99` — `pLight->SetRange(fRange);`
- `client: EterLib/GrpLightManager.cpp:245` — `void CLight::SetRange(float fRange)`
- `client: EterLib/GrpLightManager.cpp:336` — `SetRange(fRange);`

### Dosya: `EngineX-Pro/MiscExtension.h` (1 fonksiyon)

#### `MiscExtension::GetServerTime`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:211-252` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonApplication.cpp:1223` (CPythonApplication::GetServerTime)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonApplicationModule.cpp:544` — `return Py_BuildValue("i", CPythonApplication::Instance().GetServerTime());`
- `client: UserInterface/PythonApplication.cpp:1223` — `time_t CPythonApplication::GetServerTime()`
- `client: UserInterface/PythonApplication.h:212` — `time_t GetServerTime();`

### Dosya: `EngineX-Pro/Network.cpp` (31 fonksiyon)

#### `Network::GetHostName`
*Konum (hack):* `EngineX-Pro/Network.cpp:19-26` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:6` (CNetworkAddress::GetHostName)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:8` — `static bool GetHostName(char* szName, int size);`
- `client: EterLib/NetAddress.cpp:6` — `bool CNetworkAddress::GetHostName(char* szName, int size)`
- `server: game/src/input_db.cpp:291` — `LogManager::instance().CharLog(pack.player.dwID, 0, 0, 0, "CREATE PLAYER", "", d->GetHostName());`

#### `Network::IsIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:26-33` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:33` (CNetworkAddress::IsIP)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:36` — `bool IsIP(const char* c_szAddr);`
- `client: EterLib/NetAddress.cpp:33` — `bool CNetworkAddress::IsIP(const char* c_szAddr)`
- `client: EterLib/NetAddress.cpp:42` — `if (IsIP(c_szAddr))`

#### `Network::SetConnection`
*Konum (hack):* `EngineX-Pro/Network.cpp:33-51` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkDatagram.cpp:76` (CPythonNetworkDatagram::SetConnection)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamModule.cpp:342` — `//CPythonNetworkDatagram::Instance().SetConnection(c_szIP, iPort);`
- `client: UserInterface/PythonNetworkDatagram.cpp:76` — `void CPythonNetworkDatagram::SetConnection(const char * c_szIP, WORD wPortIndex)`
- `client: UserInterface/PythonNetworkDatagram.h:18` — `void SetConnection(const char * c_szIP, WORD wPortIndex);`

#### `Network::SetLocalIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:51-56` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:56` (CNetworkAddress::SetLocalIP)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:18` — `void SetLocalIP();`
- `client: EterLib/NetAddress.cpp:56` — `void CNetworkAddress::SetLocalIP()`

#### `Network::SetIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:56-61` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:61` (CNetworkAddress::SetIP); `client: EterLib/NetAddress.cpp:66` (CNetworkAddress::SetIP)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:19` — `void SetIP(DWORD ip);`
- `client: EterLib/NetAddress.h:20` — `void SetIP(const char* c_szIP);`
- `client: EterLib/NetAddress.cpp:44` — `SetIP(c_szAddr);`

#### `Network::SetIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:61-66` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:61` (CNetworkAddress::SetIP); `client: EterLib/NetAddress.cpp:66` (CNetworkAddress::SetIP)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:19` — `void SetIP(DWORD ip);`
- `client: EterLib/NetAddress.h:20` — `void SetIP(const char* c_szIP);`
- `client: EterLib/NetAddress.cpp:44` — `SetIP(c_szAddr);`

#### `Network::SetDNS`
*Konum (hack):* `EngineX-Pro/Network.cpp:66-74` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:71` (CNetworkAddress::SetDNS)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:21` — `bool SetDNS(const char* c_szDNS);`
- `client: EterLib/NetAddress.cpp:48` — `if (!SetDNS(c_szAddr))`
- `client: EterLib/NetAddress.cpp:71` — `bool CNetworkAddress::SetDNS(const char* c_szDNS)`

#### `Network::SetPort`
*Konum (hack):* `EngineX-Pro/Network.cpp:74-79` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:79` (CNetworkAddress::SetPort)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:23` — `void SetPort(int port);`
- `client: EterLib/NetAddress.cpp:52` — `SetPort(port);`
- `client: EterLib/NetAddress.cpp:79` — `void CNetworkAddress::SetPort(int port)`

#### `Network::GetIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:84-89` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:89` (CNetworkAddress::GetIP); `client: EterLib/NetAddress.cpp:94` (CNetworkAddress::GetIP)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:28` — `void GetIP(char* szIP, int len);`
- `client: EterLib/NetAddress.h:30` — `DWORD GetIP();`
- `client: EterLib/NetAddress.cpp:89` — `DWORD CNetworkAddress::GetIP()`

#### `Network::GetIP`
*Konum (hack):* `EngineX-Pro/Network.cpp:89-97` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:89` (CNetworkAddress::GetIP); `client: EterLib/NetAddress.cpp:94` (CNetworkAddress::GetIP)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:28` — `void GetIP(char* szIP, int len);`
- `client: EterLib/NetAddress.h:30` — `DWORD GetIP();`
- `client: EterLib/NetAddress.cpp:89` — `DWORD CNetworkAddress::GetIP()`

#### `Network::GetPort`
*Konum (hack):* `EngineX-Pro/Network.cpp:97-102` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetAddress.cpp:102` (CNetworkAddress::GetPort)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetAddress.h:25` — `int GetPort();`
- `client: EterLib/NetAddress.cpp:102` — `int CNetworkAddress::GetPort()`
- `server: game/src/desc.h:86` — `WORD GetPort() { return m_wPort; }`

#### `Network::SetRecvBufferSize`
*Konum (hack):* `EngineX-Pro/Network.cpp:102-117` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:37` (CNetworkStream::SetRecvBufferSize); `client: EterLib/NetDatagramReceiver.cpp:67` (CNetDatagramReceiver::SetRecvBufferSize)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:37` — `void CNetworkStream::SetRecvBufferSize(int recvBufSize)`
- `client: EterLib/NetDatagramReceiver.h:19` — `void SetRecvBufferSize(int recvBufSize);`
- `client: EterLib/NetDatagramReceiver.cpp:67` — `void CNetDatagramReceiver::SetRecvBufferSize(int recvBufSize)`

#### `Network::SetSendBufferSize`
*Konum (hack):* `EngineX-Pro/Network.cpp:117-134` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:55` (CNetworkStream::SetSendBufferSize)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:55` — `void CNetworkStream::SetSendBufferSize(int sendBufSize)`
- `client: EterLib/NetStream.h:18` — `void SetSendBufferSize(int sendBufSize);`
- `client: UserInterface/AccountConnector.cpp:726` — `SetSendBufferSize(2048);`

#### `Network::Disconnect`
*Konum (hack):* `EngineX-Pro/Network.cpp:287-300` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:357` (CNetworkStream::Disconnect); `client: UserInterface/AccountConnector.cpp:61` (CAccountConnector::Disconnect)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:357` — `void CNetworkStream::Disconnect()`
- `client: EterLib/NetStream.h:36` — `void Disconnect();`
- `client: UserInterface/AccountConnector.cpp:61` — `void CAccountConnector::Disconnect()`

#### `Network::ClearRecvBuffer`
*Konum (hack):* `EngineX-Pro/Network.cpp:386-394` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:462` (CNetworkStream::ClearRecvBuffer)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:462` — `void CNetworkStream::ClearRecvBuffer()`
- `client: EterLib/NetStream.h:29` — `void ClearRecvBuffer();`
- `client: UserInterface/PythonNetworkStream.cpp:566` — `ClearRecvBuffer();`

#### `Network::GetRecvBufferSize`
*Konum (hack):* `EngineX-Pro/Network.cpp:394-399` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:467` (CNetworkStream::GetRecvBufferSize)

**Ne işe yarar:** Paket akışında HEADER_CG_LOGIN, HEADER_CG_ATTACK başlığını kullanır.
**Header:** `HEADER_CG_LOGIN`, `HEADER_CG_ATTACK`, `HEADER_CG_CHAT`, `HEADER_CG_PLAYER_CREATE`

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:467` — `int CNetworkStream::GetRecvBufferSize()`
- `client: EterLib/NetStream.cpp:474` — `if (GetRecvBufferSize() < size)`
- `client: EterLib/NetStream.cpp:482` — `if (GetRecvBufferSize() < size)`

#### `Network::Peek`
*Konum (hack):* `EngineX-Pro/Network.cpp:399-407` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:472` (CNetworkStream::Peek); `client: EterLib/NetStream.cpp:480` (CNetworkStream::Peek)

**Ne işe yarar:** Paket akışında HEADER_CG_LOGIN, HEADER_CG_ATTACK başlığını kullanır.
**Header:** `HEADER_CG_LOGIN`, `HEADER_CG_ATTACK`, `HEADER_CG_CHAT`, `HEADER_CG_PLAYER_CREATE`

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:472` — `bool CNetworkStream::Peek(int size)`
- `client: EterLib/NetStream.cpp:480` — `bool CNetworkStream::Peek(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:720` — `if (!Peek(size))`

#### `Network::Peek`
*Konum (hack):* `EngineX-Pro/Network.cpp:407-416` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:472` (CNetworkStream::Peek); `client: EterLib/NetStream.cpp:480` (CNetworkStream::Peek)

**Ne işe yarar:** Paket akışında HEADER_CG_LOGIN, HEADER_CG_ATTACK başlığını kullanır.
**Header:** `HEADER_CG_LOGIN`, `HEADER_CG_ATTACK`, `HEADER_CG_CHAT`, `HEADER_CG_PLAYER_CREATE`

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:472` — `bool CNetworkStream::Peek(int size)`
- `client: EterLib/NetStream.cpp:480` — `bool CNetworkStream::Peek(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:720` — `if (!Peek(size))`

#### `Network::Recv`
*Konum (hack):* `EngineX-Pro/Network.cpp:416-428` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:718` (CNetworkStream::Recv); `client: EterLib/NetStream.cpp:727` (CNetworkStream::Recv)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:718` — `bool CNetworkStream::Recv(int size)`
- `client: EterLib/NetStream.cpp:727` — `bool CNetworkStream::Recv(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:808` — `bool CNetworkStream::Recv(int len, void* pDestBuf)`

#### `Network::Recv`
*Konum (hack):* `EngineX-Pro/Network.cpp:428-438` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:718` (CNetworkStream::Recv); `client: EterLib/NetStream.cpp:727` (CNetworkStream::Recv)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:718` — `bool CNetworkStream::Recv(int size)`
- `client: EterLib/NetStream.cpp:727` — `bool CNetworkStream::Recv(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:808` — `bool CNetworkStream::Recv(int len, void* pDestBuf)`

#### `Network::Send`
*Konum (hack):* `EngineX-Pro/Network.cpp:443-459` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:758` (CNetworkStream::Send); `client: EterLib/NetStream.cpp:821` (CNetworkStream::Send)

**Ne işe yarar:** (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Kanıt (LegendySF):** `client: UserInterface/PythonNetworkStream.cpp (Send/SendSpecial) | hack: HyperBot Network.cpp:104`

**Oyunda çağrıldığı yerler:**
- `client: ScriptLib/PythonUtils.cpp:320` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/PythonUtils.cpp:368` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/StdAfx.h:53` — `virtual void Send() = 0;`

#### `Network::Peek`
*Konum (hack):* `EngineX-Pro/Network.cpp:459-464` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:472` (CNetworkStream::Peek); `client: EterLib/NetStream.cpp:480` (CNetworkStream::Peek)

**Ne işe yarar:** Paket akışında HEADER_CG_LOGIN, HEADER_CG_ATTACK başlığını kullanır.
**Header:** `HEADER_CG_LOGIN`, `HEADER_CG_ATTACK`, `HEADER_CG_CHAT`, `HEADER_CG_PLAYER_CREATE`

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:472` — `bool CNetworkStream::Peek(int size)`
- `client: EterLib/NetStream.cpp:480` — `bool CNetworkStream::Peek(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:720` — `if (!Peek(size))`

#### `Network::Recv`
*Konum (hack):* `EngineX-Pro/Network.cpp:464-469` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:718` (CNetworkStream::Recv); `client: EterLib/NetStream.cpp:727` (CNetworkStream::Recv)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:718` — `bool CNetworkStream::Recv(int size)`
- `client: EterLib/NetStream.cpp:727` — `bool CNetworkStream::Recv(int size, char * pDestBuf)`
- `client: EterLib/NetStream.cpp:808` — `bool CNetworkStream::Recv(int len, void* pDestBuf)`

#### `Network::SendFlush`
*Konum (hack):* `EngineX-Pro/Network.cpp:469-476` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:813` (CNetworkStream::SendFlush)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:813` — `bool CNetworkStream::SendFlush(int len, const void* pSrcBuf)`
- `client: EterLib/NetStream.h:48` — `bool SendFlush(int len, const void* pSrcBuf);`

#### `Network::Send`
*Konum (hack):* `EngineX-Pro/Network.cpp:476-481` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:758` (CNetworkStream::Send); `client: EterLib/NetStream.cpp:821` (CNetworkStream::Send)

**Ne işe yarar:** (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Kanıt (LegendySF):** `client: UserInterface/PythonNetworkStream.cpp (Send/SendSpecial) | hack: HyperBot Network.cpp:104`

**Oyunda çağrıldığı yerler:**
- `client: ScriptLib/PythonUtils.cpp:320` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/PythonUtils.cpp:368` — `g_pkExceptionSender->Send();`
- `client: ScriptLib/StdAfx.h:53` — `virtual void Send() = 0;`

#### `Network::IsOnline`
*Konum (hack):* `EngineX-Pro/Network.cpp:481-486` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:826` (CNetworkStream::IsOnline)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:826` — `bool CNetworkStream::IsOnline()`
- `client: EterLib/NetStream.h:50` — `bool IsOnline();`
- `client: UserInterface/PythonNetworkStream.cpp:253` — `if (!IsOnline())`

#### `Network::OnProcess`
*Konum (hack):* `EngineX-Pro/Network.cpp:486-491` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:856` (CNetworkStream::OnProcess); `client: UserInterface/PythonNetworkStream.cpp:700` (CPythonNetworkStream::OnProcess)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:349` — `if (!OnProcess())`
- `client: EterLib/NetStream.cpp:856` — `bool CNetworkStream::OnProcess()`
- `client: EterLib/NetStream.h:60` — `virtual bool OnProcess();`

#### `Network::OnRemoteDisconnect`
*Konum (hack):* `EngineX-Pro/Network.cpp:491-499` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:861` (CNetworkStream::OnRemoteDisconnect); `client: UserInterface/AccountConnector.cpp:682` (CAccountConnector::OnRemoteDisconnect)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:332` — `OnRemoteDisconnect();`
- `client: EterLib/NetStream.cpp:343` — `OnRemoteDisconnect();`
- `client: EterLib/NetStream.cpp:351` — `OnRemoteDisconnect();`

#### `Network::OnDisconnect`
*Konum (hack):* `EngineX-Pro/Network.cpp:499-506` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:865` (CNetworkStream::OnDisconnect); `client: UserInterface/AccountConnector.cpp:696` (CAccountConnector::OnDisconnect)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:362` — `//OnDisconnect();`
- `client: EterLib/NetStream.cpp:865` — `void CNetworkStream::OnDisconnect()`
- `client: EterLib/NetStream.h:59` — `virtual void OnDisconnect();`

#### `Network::OnConnectSuccess`
*Konum (hack):* `EngineX-Pro/Network.cpp:506-513` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:869` (CNetworkStream::OnConnectSuccess); `client: UserInterface/AccountConnector.cpp:677` (CAccountConnector::OnConnectSuccess)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:313` — `OnConnectSuccess();`
- `client: EterLib/NetStream.cpp:869` — `void CNetworkStream::OnConnectSuccess()`
- `client: EterLib/NetStream.h:56` — `virtual void OnConnectSuccess();`

#### `Network::OnConnectFailure`
*Konum (hack):* `EngineX-Pro/Network.cpp:513-520` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterLib/NetStream.cpp:874` (CNetworkStream::OnConnectFailure); `client: UserInterface/AccountConnector.cpp:669` (CAccountConnector::OnConnectFailure)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: EterLib/NetStream.cpp:318` — `OnConnectFailure();`
- `client: EterLib/NetStream.cpp:414` — `OnConnectFailure();`
- `client: EterLib/NetStream.cpp:429` — `OnConnectFailure();`

### Dosya: `EngineX-Pro/PacketHandler.cpp` (1 fonksiyon)

#### `PacketHandler::CheckPacket`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:2-30` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonNetworkStream.cpp:528` (CPythonNetworkStream::CheckPacket); `client: UserInterface/PythonNetworkDatagram.cpp:21` (CPythonNetworkDatagram::CheckPacket)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: UserInterface/PythonNetworkStreamPhaseSelect.cpp:45` — `if (!CheckPacket(&header))`
- `client: UserInterface/PythonNetworkStream.cpp:528` — `bool CPythonNetworkStream::CheckPacket(TPacketHeader * pRetHeader)`
- `client: UserInterface/PythonNetworkStream.cpp:716` — `//while(CheckPacket(&header))`

### Dosya: `EngineX-Pro/PacketSniffer.h` (1 fonksiyon)

#### `PacketSniffer::OnStop`
*Konum (hack):* `EngineX-Pro/PacketSniffer.h:39-43` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/PatternScan.h` (1 fonksiyon)

#### `PatternScan::Search`
*Konum (hack):* `EngineX-Pro/PatternScan.h:86-135` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `server: db/src/Config.cpp:152` (CConfig::Search)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `server: db/src/Config.cpp:152` — `std::string * CConfig::Search(const char* key)`
- `server: db/src/Config.cpp:164` — `std::string * pstStr = Search(key);`
- `server: db/src/Config.cpp:179` — `std::string * pstStr = Search(key);`

### Dosya: `EngineX-Pro/Protection.h` (1 fonksiyon)

#### `Protection::OnStop`
*Konum (hack):* `EngineX-Pro/Protection.h:12-16` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/PythonScript.h` (1 fonksiyon)

#### `PythonScript::OnStop`
*Konum (hack):* `EngineX-Pro/PythonScript.h:11-15` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Singleton.h` (1 fonksiyon)

#### `Singleton::InstancePtr`
*Konum (hack):* `EngineX-Pro/Singleton.h:25-30` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: GameLib/Area.cpp:77` (CEffectManager::InstancePtr); `client: GameLib/Area.cpp:1139` (CEffectManager::InstancePtr)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/Area.cpp:77` — `//if (!CEffectManager::InstancePtr())`
- `client: GameLib/Area.cpp:1139` — `if (CEffectManager::InstancePtr())`
- `client: EterBase/Singleton.h:30` — `__forceinline static T * InstancePtr()`

### Dosya: `EngineX-Pro/Spam.h` (1 fonksiyon)

#### `Spam::OnStop`
*Konum (hack):* `EngineX-Pro/Spam.h:43-47` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/Status.h` (1 fonksiyon)

#### `Status::OnStop`
*Konum (hack):* `EngineX-Pro/Status.h:24-28` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

### Dosya: `EngineX-Pro/TAbstractSingleton.h` (1 fonksiyon)

#### `TAbstractSingleton::GetSingleton`
*Konum (hack):* `EngineX-Pro/TAbstractSingleton.h:20-26` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: EterPack/EterPack.cpp:47` (CMakePackLog::GetSingleton); `client: EterPack/EterPack.cpp:1054` (CMakePackLog::GetSingleton)

**Ne işe yarar:** Oyun durumundan bilgi okuyan sorgu fonksiyonu; oyun tarafında benzer sorgular yönetici sınıflarında yer alır.

**Oyunda çağrıldığı yerler:**
- `client: EterPack/EterPack.h:216` — `static CMakePackLog& GetSingleton();`
- `client: EterPack/EterPack.cpp:47` — `CMakePackLog& CMakePackLog::GetSingleton()`
- `client: EterPack/EterPack.cpp:1054` — `CMakePackLog::GetSingleton().Writef("Overwrite[type:%u] %s\n", pIndex->compressed_type, pIndex->filename);`

### Dosya: `EngineX-Pro/Visuals.h` (1 fonksiyon)

#### `Visuals::OnStop`
*Konum (hack):* `EngineX-Pro/Visuals.h:9-13` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ✅ VAR — `client: UserInterface/PythonPlayerEventHandler.cpp:88` (CPythonPlayerEventHandler::OnStop)

**Ne işe yarar:** Fonksiyon oyun kaynağında birebir eşleşti; gövde analizi belirgin paket/kalıp üretmedi (yardımcı/kurulum niteliği).

**Oyunda çağrıldığı yerler:**
- `client: GameLib/ActorInstance.h:52` — `virtual void OnStop(const SState& c_rkState) = 0;`
- `client: GameLib/ActorInstanceEvent.cpp:72` — `rkEventHandler.OnStop(kState);`
- `client: GameLib/ActorInstanceEvent.cpp:163` — `virtual void OnStop(const SState& c_rkState) {}`

## 6. SARMALAYICILAR — Oyunda Yok, İçindekiler Oyunda Var

> Bu bölüm kullanıcının örneğiyledir: `Boost` oyunun kendi fonksiyonu DEĞİLDİR ama içindekiler (`SendCharacterStatePacket`, `SCRIPT_SetPixelPosition`…) oyunun fonksiyonlarıdır. Her sarmalayıcı için iç oyun fonksiyonları tek tek çözümlenir.

### HyperBot — 87 sarmalayıcı

#### `AutoItemPickup::PreIteration`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:146-166` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AutoItemPickup::OnRenderWorld`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:185-215` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetDepth` (hack çağrısı: `SetDepth`) — oyunda: `client: EterLib/GrpExpandedImageInstance.cpp:143`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AutoItemPickup::IsValid`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:220-234` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `GetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AutoItemPickup::AddNewTarget`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:262-276` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AutoItemPickup::LoadItemsWhitelistFile`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:276-362` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetFileName` (hack çağrısı: `GetFileName`) — oyunda: `client: GameLib/Property.cpp:30`
1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AutoItemPickup::WriteItemsWhitelistFile`
*Konum (hack):* `HyperBot/AutoItemPickup.cpp:362-390` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetFileName` (hack çağrısı: `GetFileName`) — oyunda: `client: GameLib/Property.cpp:30`
1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `HookManager::HookManager`
*Konum (hack):* `HyperBot/Backend.cpp:2-70` | *Proje:* HyperBot | *Kategori:* hook
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`
1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console::Console`
*Konum (hack):* `HyperBot/Backend.cpp:78-97` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console`
*Konum (hack):* `HyperBot/Backend.cpp:97-109` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console::WriteCmd`
*Konum (hack):* `HyperBot/Backend.h:115-126` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console::WriteInfo`
*Konum (hack):* `HyperBot/Backend.h:126-135` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console::WriteDebug`
*Konum (hack):* `HyperBot/Backend.h:146-157` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Console::WriteMultiColor`
*Konum (hack):* `HyperBot/Backend.h:169-179` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Background::GetCurTerrainIndex`
*Konum (hack):* `HyperBot/Background.cpp:115-124` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Background::GetCurMinimapTerrainTexture`
*Konum (hack):* `HyperBot/Background.cpp:132-146` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Background::GetItemTexture`
*Konum (hack):* `HyperBot/Background.cpp:160-170` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItem` (hack çağrısı: `GetItem`) — oyunda: `client: EterPack/EterPack.cpp:1562`
1. `GetResourcePointer` (hack çağrısı: `GetResourcePointer`) — oyunda: `client: EterLib/ResourceManager.cpp:271`
1. `GetTexture` (hack çağrısı: `GetTexture`) — oyunda: `client: PRTerrainLib/TextureSet.cpp:116`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ConfigManager::LoadConfigFromFile`
*Konum (hack):* `HyperBot/ConfigManager.cpp:217-261` | *Proje:* HyperBot | *Kategori:* config
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ConfigManager::CreateItemsDump`
*Konum (hack):* `HyperBot/ConfigManager.cpp:290-315` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRefineLevel` (hack çağrısı: `GetRefineLevel`) — oyunda: `server: game/src/item.cpp:1555`
1. `GetSubType` (hack çağrısı: `GetSubType`) — oyunda: `client: GameLib/ItemData.cpp:246`
1. `GetType` (hack çağrısı: `GetType`) — oyunda: `client: GameLib/FlyTarget.cpp:73`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ConfigManager::LoadGameDirectory`
*Konum (hack):* `HyperBot/ConfigManager.cpp:315-355` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `HookManager::Reset`
*Konum (hack):* `HyperBot/D3DDevice.cpp:201-210` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::GetDistanceTo`
*Konum (hack):* `HyperBot/Entity.cpp:14-22` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::GetDistanceTo`
*Konum (hack):* `HyperBot/Entity.cpp:22-29` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsMonster`
*Konum (hack):* `HyperBot/Entity.cpp:46-51` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsEnemy` (hack çağrısı: `IsEnemy`) — oyunda: `client: GameLib/ActorInstance.cpp:301`
1. `IsPC` (hack çağrısı: `IsPC`) — oyunda: `client: GameLib/ActorInstance.cpp:285`
1. `IsStone` (hack çağrısı: `IsStone`) — oyunda: `client: GameLib/ActorInstance.cpp:309`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsPolyPC`
*Konum (hack):* `HyperBot/Entity.cpp:117-122` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetType` (hack çağrısı: `GetType`) — oyunda: `client: GameLib/FlyTarget.cpp:73`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::GetBoundBoxTransformed`
*Konum (hack):* `HyperBot/Entity.cpp:185-194` | *Proje:* HyperBot | *Kategori:* gui
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBoundBox` (hack çağrısı: `GetBoundBox`) — oyunda: `client: GameLib/DungeonBlock.cpp:177`
1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsSuraRace`
*Konum (hack):* `HyperBot/Entity.cpp:209-214` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsWarriorRace`
*Konum (hack):* `HyperBot/Entity.cpp:214-219` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsAssassinRace`
*Konum (hack):* `HyperBot/Entity.cpp:219-224` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsShamanRace`
*Konum (hack):* `HyperBot/Entity.cpp:224-229` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Entity::IsOfflineShop`
*Konum (hack):* `HyperBot/Entity.cpp:229-234` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetType` (hack çağrısı: `GetType`) — oyunda: `client: GameLib/FlyTarget.cpp:73`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Player::AttackToDestInstance`
*Konum (hack):* `HyperBot/Entity.cpp:279-291` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Player::ShortBlinkTo`
*Konum (hack):* `HyperBot/Entity.cpp:340-413` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`
1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `GetRotation` (hack çağrısı: `GetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `IsMountingHorse` (hack çağrısı: `IsMountingHorse`) — oyunda: `client: UserInterface/InstanceBase.cpp:1050`
1. `SendCharacterStatePacket` (hack çağrısı: `SendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `HyperGUI::Render`
*Konum (hack):* `HyperBot/GUI.cpp:179-234` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsConnected` (hack çağrısı: `IsConnected`) — oyunda: `server: game/src/log.cpp:50`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameInformer::PreIteration`
*Konum (hack):* `HyperBot/GameInformer.cpp:48-99` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetEmpireID` (hack çağrısı: `GetEmpireID`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:803`
1. `GetLevel` (hack çağrısı: `GetLevel`) — oyunda: `client: UserInterface/InstanceBase.cpp:228`
1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`
1. `IsEnemy` (hack çağrısı: `IsEnemy`) — oyunda: `client: GameLib/ActorInstance.cpp:301`
1. `IsGameMaster` (hack çağrısı: `IsGameMaster`) — oyunda: `client: UserInterface/InstanceBase.cpp:516`
1. `IsNPC` (hack çağrısı: `IsNPC`) — oyunda: `client: GameLib/ActorInstance.cpp:293`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameInformer::ShowLegacyInfoBox`
*Konum (hack):* `HyperBot/GameInformer.cpp:129-218` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameMainInstance::GetEntity`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:57-71` | *Proje:* HyperBot | *Kategori:* config
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `GetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameMainInstance::GetEntity`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:71-85` | *Proje:* HyperBot | *Kategori:* config
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetType` (hack çağrısı: `GetType`) — oyunda: `client: GameLib/FlyTarget.cpp:73`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameMainInstance::GetEntities`
*Konum (hack):* `HyperBot/GameMainInstance.cpp:99-113` | *Proje:* HyperBot | *Kategori:* config
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetType` (hack çağrısı: `GetType`) — oyunda: `client: GameLib/FlyTarget.cpp:73`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::GetItemSlot`
*Konum (hack):* `HyperBot/Item.cpp:12-26` | *Proje:* HyperBot | *Kategori:* item
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItem` (hack çağrısı: `GetItem`) — oyunda: `client: EterPack/EterPack.cpp:1562`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GroundItemData::GetBoundBoxTransformed`
*Konum (hack):* `HyperBot/Item.cpp:74-80` | *Proje:* HyperBot | *Kategori:* gui
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GroundItemData::GetDistanceTo`
*Konum (hack):* `HyperBot/Item.cpp:93-99` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Memory::Memory`
*Konum (hack):* `HyperBot/Memory.cpp:7-34` | *Proje:* HyperBot | *Kategori:* memory
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetColor` (hack çağrısı: `SetColor`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:854`
1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Memory::GetAddress`
*Konum (hack):* `HyperBot/Memory.cpp:101-115` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Memory::GetPointer`
*Konum (hack):* `HyperBot/Memory.cpp:115-129` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `WriteError` (hack çağrısı: `WriteError`) — oyunda: `client: EterPack/EterPack.cpp:168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscHacks::OnMenuFrame`
*Konum (hack):* `HyperBot/MiscHacks.cpp:16-72` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscHacks::PreIteration`
*Konum (hack):* `HyperBot/MiscHacks.cpp:72-103` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `GetRace` (hack çağrısı: `GetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscHacks::RunSpeedBoost`
*Konum (hack):* `HyperBot/MiscHacks.cpp:126-164` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`
1. `GetRotation` (hack çağrısı: `GetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `IsWalking` (hack çağrısı: `IsWalking`) — oyunda: `client: UserInterface/InstanceBaseMovement.cpp:193`
1. `SCRIPT_SetPixelPosition` (hack çağrısı: `SCRIPT_SetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:8`
   - Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set…
1. `SendCharacterStatePacket` (hack çağrısı: `SendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscHacks::AutoUsePassiveSkills`
*Konum (hack):* `HyperBot/MiscHacks.cpp:176-223` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `DismountHorse` (hack çağrısı: `DismountHorse`) — oyunda: `client: UserInterface/InstanceBase.cpp:1068`
1. `IsMountingHorse` (hack çağrısı: `IsMountingHorse`) — oyunda: `client: UserInterface/InstanceBase.cpp:1050`
1. `MountHorse` (hack çağrısı: `MountHorse`) — oyunda: `client: GameLib/ActorInstance.cpp:784`
1. `UseSkill` (hack çağrısı: `UseSkill`) — oyunda: `server: game/src/char_skill.cpp:98`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::PreIteration`
*Konum (hack):* `HyperBot/RouteCreator.cpp:40-56` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`
1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::PostIteration`
*Konum (hack):* `HyperBot/RouteCreator.cpp:61-69` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Play` (hack çağrısı: `Play`) — oyunda: `client: MilesLib/SoundInstanceStream.cpp:45`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::OnRenderWorld`
*Konum (hack):* `HyperBot/RouteCreator.cpp:69-97` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::OnSend`
*Konum (hack):* `HyperBot/RouteCreator.cpp:140-251` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItem` (hack çağrısı: `GetItem`) — oyunda: `client: EterPack/EterPack.cpp:1562`
1. `GetItemData` (hack çağrısı: `GetItemData`) — oyunda: `client: UserInterface/PythonShop.cpp:65`
1. `GetVirtualNumber` (hack çağrısı: `GetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).
1. `OnPickupItem` (hack çağrısı: `OnPickupItem`) — oyunda: `server: game/src/questnpc.cpp:966`
1. `OnUseItem` (hack çağrısı: `OnUseItem`) — oyunda: `server: game/src/questnpc.cpp:280`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::StartRecording`
*Konum (hack):* `HyperBot/RouteCreator.cpp:277-288` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::PerformAction`
*Konum (hack):* `HyperBot/RouteCreator.cpp:428-501` | *Proje:* HyperBot | *Kategori:* gui
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendChatPacket` (hack çağrısı: `SendChatPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206`
   - Sohbet mesaji: TPacketCGChat{header, len, type} + metin; type: NORMAL/SHOUT/PARTY/GUILD/WHISPER... Bosluk mesaj yollamaz; client sutun siniri uygular, sunucu rate-limit ve renk/kanal kurallari uygular.
1. `SendGiveItemPacket` (hack çağrısı: `SendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.
1. `SendItemUsePacket` (hack çağrısı: `SendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.
1. `SendItemUseToItemPacket` (hack çağrısı: `SendItemUseToItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524`
   - Esyayi baska esya uzerinde kullanma (tas ekleme, bonus degistirme materyali): kaynak/hedef cell.
1. `SendOnClickPacket` (hack çağrısı: `SendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendRefinePacket` (hack çağrısı: `SendRefinePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095`
   - Gelistirme (refine) onayi: esya konumu + gelistirme tipi; sunucu malzeme/oran kontrolu yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RouteCreator::MoveToDestination`
*Konum (hack):* `HyperBot/RouteCreator.cpp:501-525` | *Proje:* HyperBot | *Kategori:* movement
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SCRIPT_SetPixelPosition` (hack çağrısı: `SCRIPT_SetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:8`
   - Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RecordData::RecordData`
*Konum (hack):* `HyperBot/RouteCreator.cpp:525-533` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::_RenderCircleProgress3D`
*Konum (hack):* `HyperBot/Screen.cpp:66-91` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`
1. `GetTerrainHeight` (hack çağrısı: `GetTerrainHeight`) — oyunda: `client: GameLib/MapManager.cpp:193`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::RenderDrawList`
*Konum (hack):* `HyperBot/Screen.cpp:96-130` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::StartRender`
*Konum (hack):* `HyperBot/Screen.cpp:130-145` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`
1. `__CreatePDTVertexBufferList` (hack çağrısı: `__CreatePDTVertexBufferList`) — oyunda: `client: EterLib/GrpDevice.cpp:616`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::EndRender`
*Konum (hack):* `HyperBot/Screen.cpp:145-150` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `RestoreRenderState` (hack çağrısı: `RestoreRenderState`) — oyunda: `client: EterGrnLib/Material.cpp:46`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::_RenderCircle`
*Konum (hack):* `HyperBot/Screen.cpp:227-299` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetBackground` (hack çağrısı: `GetBackground`) — oyunda: `client: GameLib/ActorInstance.cpp:120`
1. `GetTerrainHeight` (hack çağrısı: `GetTerrainHeight`) — oyunda: `client: GameLib/MapManager.cpp:193`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Screen::Screen`
*Konum (hack):* `HyperBot/Screen.h:6-7` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__DestroyPDTVertexBufferList` (hack çağrısı: `__DestroyPDTVertexBufferList`) — oyunda: `client: EterLib/GrpDevice.cpp:604`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Skill::GetSelfBuffSkillList`
*Konum (hack):* `HyperBot/Skill.cpp:12-26` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetSkillData` (hack çağrısı: `GetSkillData`) — oyunda: `client: UserInterface/PythonSkill.cpp:747`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Skill::GetTargetBuffSkillList`
*Konum (hack):* `HyperBot/Skill.cpp:26-40` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetSkillData` (hack çağrısı: `GetSkillData`) — oyunda: `client: UserInterface/PythonSkill.cpp:747`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Skill::GetAttackSkillList`
*Konum (hack):* `HyperBot/Skill.cpp:40-58` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetSkillData` (hack çağrısı: `GetSkillData`) — oyunda: `client: UserInterface/PythonSkill.cpp:747`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Skill::GetSkillList`
*Konum (hack):* `HyperBot/Skill.cpp:58-109` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetSkillData` (hack çağrısı: `GetSkillData`) — oyunda: `client: UserInterface/PythonSkill.cpp:747`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Skill::IsSkillReady`
*Konum (hack):* `HyperBot/Skill.cpp:156-164` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetSkillData` (hack çağrısı: `GetSkillData`) — oyunda: `client: UserInterface/PythonSkill.cpp:747`
1. `IsSkillActive` (hack çağrısı: `IsSkillActive`) — oyunda: `client: UserInterface/PythonPlayer.cpp:1176`
1. `IsSkillCoolTime` (hack çağrısı: `IsSkillCoolTime`) — oyunda: `client: UserInterface/PythonPlayer.cpp:1168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `WaitHack::PreIteration`
*Konum (hack):* `HyperBot/WaitHack.cpp:74-97` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `WaitHack::OnRenderWorld`
*Konum (hack):* `HyperBot/WaitHack.cpp:116-146` | *Proje:* HyperBot | *Kategori:* visual
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetDepth` (hack çağrısı: `SetDepth`) — oyunda: `client: EterLib/GrpExpandedImageInstance.cpp:143`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `WaitHack::IsValid`
*Konum (hack):* `HyperBot/WaitHack.cpp:151-181` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsBoss` (hack çağrısı: `IsBoss`) — oyunda: `server: game/src/char.cpp:8324`
1. `IsBuilding` (hack çağrısı: `IsBuilding`) — oyunda: `client: GameLib/ActorInstance.cpp:333`
1. `IsDoor` (hack çağrısı: `IsDoor`) — oyunda: `client: GameLib/ActorInstance.cpp:341`
1. `IsNPC` (hack çağrısı: `IsNPC`) — oyunda: `client: GameLib/ActorInstance.cpp:293`
1. `IsPC` (hack çağrısı: `IsPC`) — oyunda: `client: GameLib/ActorInstance.cpp:285`
1. `IsStone` (hack çağrısı: `IsStone`) — oyunda: `client: GameLib/ActorInstance.cpp:309`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `WaitHack::AttackTarget`
*Konum (hack):* `HyperBot/WaitHack.cpp:186-231` | *Proje:* HyperBot | *Kategori:* combat
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsAttacking` (hack çağrısı: `IsAttacking`) — oyunda: `client: UserInterface/InstanceBaseMovement.cpp:216`
1. `IsBowMode` (hack çağrısı: `IsBowMode`) — oyunda: `client: GameLib/ActorInstance.cpp:262`
1. `SendAttackPacket` (hack çağrısı: `SendAttackPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599`
   - Melee saldiri talebi: TPacketCGAttack{header=HEADER_CG_ATTACK, bType=uMotAttack(0=normal,1=combo), dwVictimVID} doldurup SendSpecial ile yollar; SendSpecial saldiri paketlerine CRCMagicCube baytlarini ekler (sunucu anti-…
1. `SendCharacterStatePacket` (hack çağrısı: `SendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …
1. `SendFlyTargetingPacket` (hack çağrısı: `SendFlyTargetingPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759`
   - Ucan hedef guncellemesi (mevcut mermi icin hedef tazeleme).
1. `SendShootPacket` (hack çağrısı: `SendShootPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721`
   - Yay/ok atisi: HEADER_CG_SHOOT + uSkill. Genellikle AddFlyTargeting ile ciftli calisir (mermi hedefi).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `WaitHack::AddNewTarget`
*Konum (hack):* `HyperBot/WaitHack.cpp:231-244` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::FromHSB`
*Konum (hack):* `HyperBot/color.h:263-321` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Red`
*Konum (hack):* `HyperBot/color.h:321-326` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Green`
*Konum (hack):* `HyperBot/color.h:326-331` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Blue`
*Konum (hack):* `HyperBot/color.h:331-336` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::LightBlue`
*Konum (hack):* `HyperBot/color.h:336-341` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Orange`
*Konum (hack):* `HyperBot/color.h:341-346` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Grey`
*Konum (hack):* `HyperBot/color.h:346-351` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::DarkGrey`
*Konum (hack):* `HyperBot/color.h:351-356` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Black`
*Konum (hack):* `HyperBot/color.h:356-361` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::White`
*Konum (hack):* `HyperBot/color.h:361-366` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Purple`
*Konum (hack):* `HyperBot/color.h:366-371` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Pink`
*Konum (hack):* `HyperBot/color.h:371-376` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::Yellow`
*Konum (hack):* `HyperBot/color.h:376-381` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::ColdBlue`
*Konum (hack):* `HyperBot/color.h:381-386` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Color::FireRed`
*Konum (hack):* `HyperBot/color.h:386-391` | *Proje:* HyperBot | *Kategori:* core
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Color` (hack çağrısı: `Color`) — oyunda: `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

### C4US — 297 sarmalayıcı

#### `GameFunctionsCustom::Boost`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:990-1028` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `GetRotation` (hack çağrısı: `PlayerGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `SCRIPT_SetPixelPosition` (hack çağrısı: `InstanceBaseSCRIPT_SetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:8`
   - Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set…
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Buff::OnUpdate`
*Konum (hack):* `EngineX-Pro/Buff.h:131-289` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `PlayerGetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`
1. `Check` (hack çağrısı: `Check`) — oyunda: `server: game/src/skill_power.cpp:8`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SetTarget` (hack çağrısı: `PlayerSetTarget`) — oyunda: `client: EterLib/Camera.cpp:235`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Buff::OnTab1`
*Konum (hack):* `EngineX-Pro/Buff.h:293-404` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetTargetVID` (hack çağrısı: `PlayerGetTargetVID`) — oyunda: `client: UserInterface/PythonPlayerInput.cpp:76`
1. `GetNameString` (hack çağrısı: `PlayerGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RestoreStateWithWorld::RestoreStateWithWorld`
*Konum (hack):* `EngineX-Pro/CRender.cpp:79-119` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRenderState` (hack çağrısı: `GetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:418`
1. `GetTextureStageState` (hack çağrısı: `GetTextureStageState`) — oyunda: `client: EterLib/StateManager.cpp:532`
1. `GetTransform` (hack çağrısı: `GetTransform`) — oyunda: `client: GameLib/DungeonBlock.cpp:170`
1. `SetTexture` (hack çağrısı: `SetTexture`) — oyunda: `client: GameLib/WeaponTrace.cpp:361`
1. `SetPixelShader` (hack çağrısı: `SetPixelShader`) — oyunda: `client: EterLib/StateManager.cpp:575`
1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RestoreStateWithWorld::RestoreStateWithWorld`
*Konum (hack):* `EngineX-Pro/CRender.cpp:119-138` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`
1. `SetTextureStageState` (hack çağrısı: `SetTextureStageState`) — oyunda: `client: EterLib/StateManager.cpp:523`
1. `SetTransform` (hack çağrısı: `SetTransform`) — oyunda: `client: EterLib/StateManager.cpp:621`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RestoreStateGame::RestoreStateGame`
*Konum (hack):* `EngineX-Pro/CRender.cpp:161-201` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRenderState` (hack çağrısı: `GetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:418`
1. `GetTextureStageState` (hack çağrısı: `GetTextureStageState`) — oyunda: `client: EterLib/StateManager.cpp:532`
1. `GetTransform` (hack çağrısı: `GetTransform`) — oyunda: `client: GameLib/DungeonBlock.cpp:170`
1. `SetTexture` (hack çağrısı: `SetTexture`) — oyunda: `client: GameLib/WeaponTrace.cpp:361`
1. `SetPixelShader` (hack çağrısı: `SetPixelShader`) — oyunda: `client: EterLib/StateManager.cpp:575`
1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `RestoreStateGame::RestoreStateGame`
*Konum (hack):* `EngineX-Pro/CRender.cpp:201-220` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`
1. `SetTextureStageState` (hack çağrısı: `SetTextureStageState`) — oyunda: `client: EterLib/StateManager.cpp:523`
1. `SetTransform` (hack çağrısı: `SetTransform`) — oyunda: `client: EterLib/StateManager.cpp:621`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::RenderBox`
*Konum (hack):* `EngineX-Pro/CRender.cpp:250-277` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `SetIndices` (hack çağrısı: `SetIndices`) — oyunda: `client: EterLib/GrpIndexBuffer.cpp:12`
1. `SetStreamSource` (hack çağrısı: `SetStreamSource`) — oyunda: `client: EterLib/StateManager.cpp:716`
1. `DrawIndexedPrimitive` (hack çağrısı: `DrawIndexedPrimitive`) — oyunda: `client: EterLib/StateManager.cpp:759`
1. `SetVertexShader` (hack çağrısı: `SetVertexShader`) — oyunda: `client: EterLib/StateManager.cpp:549`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::Line3D`
*Konum (hack):* `EngineX-Pro/CRender.cpp:283-325` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Lock` (hack çağrısı: `Lock`) — oyunda: `client: MilesLib/SoundManager3D.cpp:189`
1. `Unlock` (hack çağrısı: `Unlock`) — oyunda: `client: MilesLib/SoundManager3D.cpp:197`
1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `SetStreamSource` (hack çağrısı: `SetStreamSource`) — oyunda: `client: EterLib/StateManager.cpp:716`
1. `DrawPrimitive` (hack çağrısı: `DrawPrimitive`) — oyunda: `client: EterLib/StateManager.cpp:748`
1. `Release` (hack çağrısı: `Release`) — oyunda: `client: MilesLib/SoundData.cpp:42`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::Circle`
*Konum (hack):* `EngineX-Pro/CRender.cpp:357-367` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `DrawPrimitiveUP` (hack çağrısı: `DrawPrimitiveUP`) — oyunda: `client: EterLib/StateManager.cpp:753`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::Box3D`
*Konum (hack):* `EngineX-Pro/CRender.cpp:367-386` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetTexture` (hack çağrısı: `SetTexture`) — oyunda: `client: GameLib/WeaponTrace.cpp:361`
1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `DrawPrimitiveUP` (hack çağrısı: `DrawPrimitiveUP`) — oyunda: `client: EterLib/StateManager.cpp:753`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::Cube3D`
*Konum (hack):* `EngineX-Pro/CRender.cpp:388-409` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetTexture` (hack çağrısı: `SetTexture`) — oyunda: `client: GameLib/WeaponTrace.cpp:361`
1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `DrawPrimitiveUP` (hack çağrısı: `DrawPrimitiveUP`) — oyunda: `client: EterLib/StateManager.cpp:753`
1. `DrawIndexedPrimitiveUP` (hack çağrısı: `DrawIndexedPrimitiveUP`) — oyunda: `client: EterLib/StateManager.cpp:764`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CRender::FilledCircle3D`
*Konum (hack):* `EngineX-Pro/CRender.cpp:409-440` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetTexture` (hack çağrısı: `SetTexture`) — oyunda: `client: GameLib/WeaponTrace.cpp:361`
1. `SetRenderState` (hack çağrısı: `SetRenderState`) — oyunda: `client: EterLib/StateManager.cpp:453`
1. `SetVertex` (hack çağrısı: `SetVertex`) — oyunda: `client: EterLib/SkyBox.cpp:65`
1. `DrawPrimitiveUP` (hack çağrısı: `DrawPrimitiveUP`) — oyunda: `client: EterLib/StateManager.cpp:753`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CryptExtension::base64_encode`
*Konum (hack):* `EngineX-Pro/CryptExtension.h:89-139` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CryptExtension::b64decode`
*Konum (hack):* `EngineX-Pro/CryptExtension.h:139-177` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `string_format`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:2-12` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ImGui::Combo`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:12-26` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ImGui::Combo`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:26-35` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ImGui::ListBox`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:35-44` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ImGui::Selectable2`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:241-376` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ImGui::ItemImage`
*Konum (hack):* `EngineX-Pro/CustomWidgets.cpp:394-465` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Debug::OnTab1`
*Konum (hack):* `EngineX-Pro/Debug.h:118-217` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`
1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`
1. `SendGiveItemPacket` (hack çağrısı: `NetworkStreamSendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Action::Action`
*Konum (hack):* `EngineX-Pro/DelayActions.h:39-52` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `bind` (hack çağrısı: `bind`) — oyunda: `server: game/src/main.cpp:481`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `DelayActions::AppendBlock`
*Konum (hack):* `EngineX-Pro/DelayActions.h:163-177` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `DelayActions::AppendBlockUnique`
*Konum (hack):* `EngineX-Pro/DelayActions.h:177-191` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `DelayActions::Update`
*Konum (hack):* `EngineX-Pro/DelayActions.h:191-221` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `DelayActions::Clear`
*Konum (hack):* `EngineX-Pro/DelayActions.h:221-232` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `DynamicTimer::CheckAutoSet`
*Konum (hack):* `EngineX-Pro/DynamicTimer.h:4-26` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Farm::CheckClosestCoord`
*Konum (hack):* `EngineX-Pro/Farm.h:23-47` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Farm::OnStart`
*Konum (hack):* `EngineX-Pro/Farm.h:47-56` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Farm::OnUpdate`
*Konum (hack):* `EngineX-Pro/Farm.h:63-205` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsDead` (hack çağrısı: `InstanceBaseIsDead`) — oyunda: `client: GameLib/ActorInstance.cpp:423`
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Farm::OnRender`
*Konum (hack):* `EngineX-Pro/Farm.h:205-235` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Farm::OnTab1`
*Konum (hack):* `EngineX-Pro/Farm.h:235-297` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `FileExtension::GetAppDataDirectory`
*Konum (hack):* `EngineX-Pro/FileExtension.h:3-13` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `FileExtension::GetCommonDataDirectory`
*Konum (hack):* `EngineX-Pro/FileExtension.h:13-22` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `FileExtension::GetCurrentExeDirectory`
*Konum (hack):* `EngineX-Pro/FileExtension.h:32-40` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `FileExtension::CreateDirectoryPath`
*Konum (hack):* `EngineX-Pro/FileExtension.h:71-83` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Read` (hack çağrısı: `Read`) — oyunda: `client: EterBase/MappedFile.cpp:229`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `FileExtension::Append`
*Konum (hack):* `EngineX-Pro/FileExtension.h:102-110` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Read` (hack çağrısı: `Read`) — oyunda: `client: EterBase/MappedFile.cpp:229`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::OnStart`
*Konum (hack):* `EngineX-Pro/Fish.h:17-32` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::OnTab2`
*Konum (hack):* `EngineX-Pro/Fish.h:183-220` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::OnTab3`
*Konum (hack):* `EngineX-Pro/Fish.h:220-239` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::OnTab4`
*Konum (hack):* `EngineX-Pro/Fish.h:239-256` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::OnTab5`
*Konum (hack):* `EngineX-Pro/Fish.h:256-276` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::CheckPosition`
*Konum (hack):* `EngineX-Pro/Fish.h:332-353` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::Cast`
*Konum (hack):* `EngineX-Pro/Fish.h:353-394` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendFishingPacket` (hack çağrısı: `NetworkStreamSendFishingPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3853`
1. `GetRotation` (hack çağrısı: `PlayerGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `SetAttackKeyState` (hack çağrısı: `PlayerSetAttackKeyState`) — oyunda: `client: UserInterface/PythonPlayerInputKeyboard.cpp:6`
   - Atak tusunun (Space/ctrl vurusu) basili olup olmadigini tutar: m_isAtkKey=true/false. Oyun dongusu (PythonPlayerInputMouse.cpp:381) bu bayragi her kare kontrol ederek saldiriyi tetikler; balik tutma modundaysa (IsFishing…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::Cast2`
*Konum (hack):* `EngineX-Pro/Fish.h:394-424` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendEmoticon` (hack çağrısı: `NetworkStreamSendEmoticon`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:882`
1. `GetRotation` (hack çağrısı: `PlayerGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::NewCast`
*Konum (hack):* `EngineX-Pro/Fish.h:424-505` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::RefineRod`
*Konum (hack):* `EngineX-Pro/Fish.h:505-556` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemMetinSocket` (hack çağrısı: `PlayerGetItemMetinSocket`) — oyunda: `client: UserInterface/PythonPlayer.cpp:685`
1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendGiveItemPacket` (hack çağrısı: `NetworkStreamSendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::BuyBait`
*Konum (hack):* `EngineX-Pro/Fish.h:556-573` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.
1. `SendShopBuyPacket` (hack çağrısı: `NetworkStreamSendShopBuyPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:401`
1. `SendShopEndPacket` (hack çağrısı: `NetworkStreamSendShopEndPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:383`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::SellItems`
*Konum (hack):* `EngineX-Pro/Fish.h:573-632` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendGiveItemPacket` (hack çağrısı: `NetworkStreamSendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.
1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.
1. `SendShopSellPacketNew` (hack çağrısı: `NetworkStreamSendShopSellPacketNew`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:455`
1. `SendShopEndPacket` (hack çağrısı: `NetworkStreamSendShopEndPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:383`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::DropItems`
*Konum (hack):* `EngineX-Pro/Fish.h:632-650` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendItemDropPacketNew` (hack çağrısı: `NetworkStreamSendItemDropPacketNew`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:611`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::KillFishes`
*Konum (hack):* `EngineX-Pro/Fish.h:650-669` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::UseBait`
*Konum (hack):* `EngineX-Pro/Fish.h:669-697` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Fish::ParseMessage`
*Konum (hack):* `EngineX-Pro/Fish.h:697-841` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::GetVIDByInstance`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:4-49` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::CharacterManagerGetInstancePtr`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:49-61` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `InstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: GameLib/Area.cpp:77`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::ItemManagerGetItemDataPointer`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:61-73` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemDataPointer` (hack çağrısı: `ItemManagerGetItemDataPointer`) — oyunda: `client: GameLib/ItemManager.cpp:47`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::ItemDataGetName`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:86-108` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemDataPointer` (hack çağrısı: `ItemManagerGetItemDataPointer`) — oyunda: `client: GameLib/ItemManager.cpp:47`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetMainCharacterIndex`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:108-128` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetStatus`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:128-147` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetStatus` (hack çağrısı: `PlayerGetStatus`) — oyunda: `client: UserInterface/PythonPlayer.cpp:478`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetItemIndex`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:147-180` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetItemCount`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:180-199` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemCount` (hack çağrısı: `PlayerGetItemCount`) — oyunda: `client: UserInterface/PythonPlayer.cpp:658`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetName`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:199-219` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetName` (hack çağrısı: `PlayerGetName`) — oyunda: `client: UserInterface/PythonPlayer.cpp:490`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetItemMetinSocket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:219-238` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemMetinSocket` (hack çağrısı: `PlayerGetItemMetinSocket`) — oyunda: `client: UserInterface/PythonPlayer.cpp:685`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetItemAttribute`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:238-249` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemAttribute` (hack çağrısı: `PlayerGetItemAttribute`) — oyunda: `client: UserInterface/PythonPlayer.cpp:696`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetItemMetinSocket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:249-268` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemMetinSocket` (hack çağrısı: `PlayerGetItemMetinSocket`) — oyunda: `client: UserInterface/PythonPlayer.cpp:685`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetRace`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:268-287` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `PlayerGetRace`) — oyunda: `client: UserInterface/PythonPlayer.cpp:326`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerNEW_SetSingleDIKKeyState`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:287-305` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_SetSingleDIKKeyState` (hack çağrısı: `PlayerNEW_SetSingleDIKKeyState`) — oyunda: `client: UserInterface/PythonPlayerInputKeyboard.cpp:22`
   - Tek bir DirectInput tusunun (DIK kodu) basili/birakilmis durumunu isler; balik modunu iptal eder, tusa gore oyuncu aksiyonunu yonlendirir (yurume/saldiri/skill tuslari).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerClickSkillSlot`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:305-324` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `ClickSkillSlot` (hack çağrısı: `PlayerClickSkillSlot`) — oyunda: `client: UserInterface/PythonPlayerSkill.cpp:107`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerIsSkillCoolTime`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:324-343` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsSkillCoolTime` (hack çağrısı: `PlayerIsSkillCoolTime`) — oyunda: `client: UserInterface/PythonPlayer.cpp:1168`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerIsSkillActive`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:343-362` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsSkillActive` (hack çağrısı: `PlayerIsSkillActive`) — oyunda: `client: UserInterface/PythonPlayer.cpp:1176`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerGetTargetVID`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:362-381` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetTargetVID` (hack çağrısı: `PlayerGetTargetVID`) — oyunda: `client: UserInterface/PythonPlayerInput.cpp:76`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerSetTarget`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:381-400` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Target` (hack çağrısı: `PlayerSetTarget`) — oyunda: `server: game/src/questmanager.cpp:705`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerSetAttackKeyState`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:400-418` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetAttackKeyState` (hack çağrısı: `PlayerSetAttackKeyState`) — oyunda: `client: UserInterface/PythonPlayerInputKeyboard.cpp:6`
   - Atak tusunun (Space/ctrl vurusu) basili olup olmadigini tutar: m_isAtkKey=true/false. Oyun dongusu (PythonPlayerInputMouse.cpp:381) bu bayragi her kare kontrol ederek saldiriyi tetikler; balik tutma modundaysa (IsFishing…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::Player__OnPressActor`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:418-429` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__OnPressActor` (hack çağrısı: `Player__OnPressActor`) — oyunda: `client: UserInterface/PythonPlayerInput.cpp:301`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::Player__OnClickActor`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:429-440` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__OnClickActor` (hack çağrısı: `Player__OnClickActor`) — oyunda: `client: UserInterface/PythonPlayerInput.cpp:259`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::PlayerNEW_GetMainActorPtr`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:440-452` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendItemUsePacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:464-505` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `ItemUse` (hack çağrısı: `ItemUse`) — oyunda: `server: game/src/input_main.cpp:879`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendItemUseToItemPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:505-517` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemUseToItemPacket` (hack çağrısı: `NetworkStreamSendItemUseToItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524`
   - Esyayi baska esya uzerinde kullanma (tas ekleme, bonus degistirme materyali): kaynak/hedef cell.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendChatPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:517-536` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `ChatPacket` (hack çağrısı: `NetworkStreamSendChatPacket`) — oyunda: `server: game/src/char.cpp:4202`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendRefinePacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:536-591` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendRefinePacket` (hack çağrısı: `NetworkStreamSendRefinePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095`
   - Gelistirme (refine) onayi: esya konumu + gelistirme tipi; sunucu malzeme/oran kontrolu yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSendExchangeStartPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:591-611` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendExchangeStartPacket` (hack çağrısı: `NetworkStreamSendSendExchangeStartPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2117`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSendExchangeItemAddPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:611-631` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendExchangeItemAddPacket` (hack çağrısı: `NetworkStreamSendSendExchangeItemAddPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2158`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSendExchangeAcceptPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:631-651` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendExchangeAcceptPacket` (hack çağrısı: `NetworkStreamSendSendExchangeAcceptPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2202`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendWhisperPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:651-692` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendWhisperPacket` (hack çağrısı: `NetworkStreamSendWhisperPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1481`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendItemPickUpPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:692-712` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemPickUpPacket` (hack çağrısı: `NetworkStreamSendItemPickUpPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:735`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendItemDropPacketNew`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:712-732` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemDropPacketNew` (hack çağrısı: `NetworkStreamSendItemDropPacketNew`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:611`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendOnClickPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:732-752` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendShopSellPacketNew`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:752-786` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendShopSellPacketNew` (hack çağrısı: `NetworkStreamSendShopSellPacketNew`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:455`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendShopBuyPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:786-806` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendShopBuyPacket` (hack çağrısı: `NetworkStreamSendShopBuyPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:401`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendShopEndPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:806-826` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendShopEndPacket` (hack çağrısı: `NetworkStreamSendShopEndPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:383`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendGiveItemPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:826-846` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendGiveItemPacket` (hack çağrısı: `NetworkStreamSendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendItemMovePacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:846-866` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemMovePacket` (hack çağrısı: `NetworkStreamSendItemMovePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:689`
   - Envanter icinde/bankada esya tasima: kaynak ve hedef TItemPos gonderir; sunucu slot gecerliligini kontrol eder.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamConnectGameServer`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:866-911` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `ConnectGameServer` (hack çağrısı: `ConnectGameServer`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:499`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamIsOnline`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:911-930` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsOnline` (hack çağrısı: `NetworkStreamIsOnline`) — oyunda: `client: EterLib/NetStream.cpp:826`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamGetMainActorSkillGroup`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:930-949` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetMainActorSkillGroup` (hack çağrısı: `NetworkStreamGetMainActorSkillGroup`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:793`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamGetAccountCharacterSlotDataz`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:949-968` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetAccountCharacterSlotDataz` (hack çağrısı: `NetworkStreamGetAccountCharacterSlotDataz`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:451`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendScriptAnswerPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1019-1039` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamServerCommand`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1039-1050` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `ServerCommand` (hack çağrısı: `NetworkStreamServerCommand`) — oyunda: `client: UserInterface/PythonNetworkStreamCommand.cpp:131`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendFishingPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1050-1062` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendFishingPacket` (hack çağrısı: `NetworkStreamSendFishingPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3853`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendEmoticon`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1074-1086` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendEmoticon` (hack çağrısı: `NetworkStreamSendEmoticon`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:882`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSpecial`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1086-1098` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendSpecial` (hack çağrısı: `NetworkStreamSendSpecial`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2626`
   - Ozel gonderim: paket header'ina gore ek islem yapar - HEADER_CG_ATTACK icin CRCMagicCube baytlarini paketin sonuna isler (anti-cheat), digerlerini dogrudan kuyruga ekler.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendAttackPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1098-1110` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendAttackPacket` (hack çağrısı: `NetworkStreamSendAttackPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599`
   - Melee saldiri talebi: TPacketCGAttack{header=HEADER_CG_ATTACK, bType=uMotAttack(0=normal,1=combo), dwVictimVID} doldurup SendSpecial ile yollar; SendSpecial saldiri paketlerine CRCMagicCube baytlarini ekler (sunucu anti-…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendUseSkillPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1110-1122` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendUseSkillPacket` (hack çağrısı: `NetworkStreamSendUseSkillPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191`
   - Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendAddFlyTargetingPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1122-1134` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendAddFlyTargetingPacket` (hack çağrısı: `NetworkStreamSendAddFlyTargetingPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736`
   - Ucan mermi (ok/beceri) icin hedef kaydi: dwTargetVID + TPixelPosition varis noktasi; sunucu merminin isabetini buna gore cozer.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendShootPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1134-1146` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendShootPacket` (hack çağrısı: `NetworkStreamSendShootPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721`
   - Yay/ok atisi: HEADER_CG_SHOOT + uSkill. Genellikle AddFlyTargeting ile ciftli calisir (mermi hedefi).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamRecv`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1146-1158` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Recv` (hack çağrısı: `NetworkStreamRecv`) — oyunda: `client: EterLib/NetStream.cpp:718`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSend`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1158-1184` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Send` (hack çağrısı: `Send`) — oyunda: `client: EterLib/NetStream.cpp:758`
   - (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSequence`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1185-1201` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendSequence` (hack çağrısı: `NetworkStreamSendSequence`) — oyunda: `client: EterLib/NetStream.cpp:838`
   - Paket sirasi (sequence) baytini gonderir: sunucu paket akis sirasini dogrulayip kayip/saldiri tespiti yapar. Her gonderimden sonra cagrilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendSyncPositionPacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1201-1241` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendSequence` (hack çağrısı: `NetworkStreamSendSequence`) — oyunda: `client: EterLib/NetStream.cpp:838`
   - Paket sirasi (sequence) baytini gonderir: sunucu paket akis sirasini dogrulayip kayip/saldiri tespiti yapar. Her gonderimden sonra cagrilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStreamSendCharacterStatePacket`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1241-1340` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendSequence` (hack çağrısı: `NetworkStreamSendSequence`) — oyunda: `client: EterLib/NetStream.cpp:838`
   - Paket sirasi (sequence) baytini gonderir: sunucu paket akis sirasini dogrulayip kayip/saldiri tespiti yapar. Her gonderimden sonra cagrilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::NetworkStream__DirectEnterMode_Set`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1340-1353` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__DirectEnterMode_Set` (hack çağrısı: `NetworkStream__DirectEnterMode_Set`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:827`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBase__SetAffect`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1364-1382` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__SetAffect` (hack çağrısı: `InstanceBase__SetAffect`) — oyunda: `client: UserInterface/InstanceBaseEffect.cpp:913`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseNEW_GetPixelPosition`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1382-1404` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseNEW_MoveToDestPixelPositionDirection`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1404-1425` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_MoveToDestPixelPositionDirection` (hack çağrısı: `InstanceBaseNEW_MoveToDestPixelPositionDirection`) — oyunda: `client: UserInterface/InstanceBaseMovement.cpp:241`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseGetInstanceType`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1425-1449` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseGetVirtualNumber`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1449-1473` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseIsMountingHorse`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1473-1492` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `IsMountingHorse` (hack çağrısı: `InstanceBaseIsMountingHorse`) — oyunda: `client: UserInterface/InstanceBase.cpp:1050`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseGetNameString`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1492-1519` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseSCRIPT_SetPixelPosition`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1519-1565` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetPixelPosition` (hack çağrısı: `InstanceBaseSCRIPT_SetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:90`
   - Python katmanindan karakter tasima: PythonCharacterModule.cpp:699 pkInst->SCRIPT_SetPixelPosition. Script/Python yanindan teleport - oyun icinde yalnizca yetkili scriptlerde kullanilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceSetRotation`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1565-1606` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseGetRotation`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1606-1654` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::InstanceBaseIsDead`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1666-1682` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Dead` (hack çağrısı: `InstanceBaseIsDead`) — oyunda: `server: game/src/pvp.cpp:332`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::BackgroundLocalPositionToGlobalPosition`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1694-1706` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `LocalPositionToGlobalPosition` (hack çağrısı: `BackgroundLocalPositionToGlobalPosition`) — oyunda: `client: UserInterface/PythonBackground.cpp:715`
   - __LocalPositionToGlobalPosition: harita lokal koordinatini global koordinata cevirir (chunk/region ofsetleri eklenir). TPacketCGMove.lX/lY bununla doldurulur.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::BackgroundGlobalPositionToMapInfo`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1706-1735` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GlobalPositionToMapInfo` (hack çağrısı: `BackgroundGlobalPositionToMapInfo`) — oyunda: `client: UserInterface/PythonBackground.cpp:726`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctions::GetBackgroundHeight`
*Konum (hack):* `EngineX-Pro/GameFunctions.h:1739-1782` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetWindowWidth`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:5-15` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetClientRect` (hack çağrısı: `GetClientRect`) — oyunda: `client: EterLib/MSWindow.cpp:150`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetWindowHeight`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:15-23` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetClientRect` (hack çağrısı: `GetClientRect`) — oyunda: `client: EterLib/MSWindow.cpp:150`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetHpProcentageStatus`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:23-30` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetStatus` (hack çağrısı: `PlayerGetStatus`) — oyunda: `client: UserInterface/PythonPlayer.cpp:478`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetMpProcentageStatus`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:30-37` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetStatus` (hack çağrısı: `PlayerGetStatus`) — oyunda: `client: UserInterface/PythonPlayer.cpp:478`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::FindItemSlotInInventoryByName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:37-61` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `GetItemDataPointer` (hack çağrısı: `ItemManagerGetItemDataPointer`) — oyunda: `client: GameLib/ItemManager.cpp:47`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::ItemSplitter`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:61-79` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `SendItemMovePacket` (hack çağrısı: `NetworkStreamSendItemMovePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:689`
   - Envanter icinde/bankada esya tasima: kaynak ve hedef TItemPos gonderir; sunucu slot gecerliligini kontrol eder.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:79-92` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`
1. `GetNameString` (hack çağrısı: `PlayerGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetNameString`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:92-104` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsInstance`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:124-137` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceGetInstanceTypeByVID`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:137-150` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceIsDead`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:150-163` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `IsDead` (hack çağrısı: `InstanceBaseIsDead`) — oyunda: `client: GameLib/ActorInstance.cpp:423`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsDead`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:163-176` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `IsDead` (hack çağrısı: `InstanceBaseIsDead`) — oyunda: `client: GameLib/ActorInstance.cpp:423`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerRevive`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:176-198` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendChatPacket` (hack çağrısı: `NetworkStreamSendChatPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206`
   - Sohbet mesaji: TPacketCGChat{header, len, type} + metin; type: NORMAL/SHOUT/PARTY/GUILD/WHISPER... Bosluk mesaj yollamaz; client sutun siniri uygular, sunucu rate-limit ve renk/kanal kurallari uygular.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsMountingHorse`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:198-211` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `IsMountingHorse` (hack çağrısı: `InstanceBaseIsMountingHorse`) — oyunda: `client: UserInterface/InstanceBase.cpp:1050`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerCanRefineRod`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:211-224` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsRodEquipped`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:224-243` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetPixelPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:258-275` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::UnMountHorse`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:287-299` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendChatPacket` (hack çağrısı: `NetworkStreamSendChatPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206`
   - Sohbet mesaji: TPacketCGChat{header, len, type} + metin; type: NORMAL/SHOUT/PARTY/GUILD/WHISPER... Bosluk mesaj yollamaz; client sutun siniri uygular, sunucu rate-limit ve renk/kanal kurallari uygular.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::UseAllItemVnumInInventory`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:299-310` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetCloseObject`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:310-331` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetCloseObjectByVnum`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:331-356` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::UseAllFishVnumInInventoryTillSize`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:369-398` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `GetItemMetinSocket` (hack çağrısı: `PlayerGetItemMetinSocket`) — oyunda: `client: UserInterface/PythonPlayer.cpp:685`
1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::FindItemSlotsInInventory`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:398-413` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::FindItemSlotsInInventory`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:413-428` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::FindItemSlotInInventory`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:428-442` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::IsFullInventory`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:442-461` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InventoryEquippedPercentage`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:461-481` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetCharacterDistance`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:481-496` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `GetDistance` (hack çağrısı: `InstanceBaseGetDistance`) — oyunda: `client: UserInterface/InstanceBase.cpp:2619`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceGetNameByVID`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:496-509` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceGetNameStringByVID`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:509-521` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerMoveToDestPixelPositionDirection`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:521-534` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `NEW_MoveToDestPixelPositionDirection` (hack çağrısı: `InstanceBaseNEW_MoveToDestPixelPositionDirection`) — oyunda: `client: UserInterface/InstanceBaseMovement.cpp:241`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsMoreLessPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:534-539` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetDistance` (hack çağrısı: `PlayerGetDistance`) — oyunda: `client: UserInterface/InstanceBase.cpp:2619`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerIsMoreLessPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:539-551` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `GetDistance` (hack çağrısı: `PlayerGetDistance`) — oyunda: `client: UserInterface/InstanceBase.cpp:2619`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetCharacterVidByName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:551-568` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetNPCVidByName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:568-585` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetCharacterInstanceByName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:585-602` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetCharacterVIDByName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:602-620` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetObjectListCount`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:620-625` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetObjectList`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:625-782` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `IsDead` (hack çağrısı: `InstanceBaseIsDead`) — oyunda: `client: GameLib/ActorInstance.cpp:423`
1. `GetDistance` (hack çağrısı: `InstanceBaseGetDistance`) — oyunda: `client: UserInterface/InstanceBase.cpp:2619`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::DetectPlayer`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:782-806` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetGroundItemList`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:806-847` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::IsGroundItemsCanPickup`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:847-879` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetItemProtoList`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:879-902` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetItemProtoNames`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:902-946` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceBaseGetDistance`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:946-955` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetDistance`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:955-967` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerShowTargetArrow`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:967-990` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`
1. `GetMainCharacterIndex` (hack çağrısı: `PlayerGetMainCharacterIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:291`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceIsResource`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1028-1058` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceIsResource`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1058-1088` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::InstanceIsBoss`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1139-1153` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::SendPacket`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1153-1161` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `SendSequence` (hack çağrısı: `NetworkStreamSendSequence`) — oyunda: `client: EterLib/NetStream.cpp:838`
   - Paket sirasi (sequence) baytini gonderir: sunucu paket akis sirasini dogrulayip kayip/saldiri tespiti yapar. Her gonderimden sonra cagrilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetTempPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1161-1181` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::PlayerGetRotation`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1215-1223` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRotation` (hack çağrısı: `InstanceBaseGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::Teleport`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1223-1243` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `SCRIPT_SetPixelPosition` (hack çağrısı: `InstanceBaseSCRIPT_SetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:8`
   - Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set…
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …
1. `GetRotation` (hack çağrısı: `PlayerGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::LookAtDestPixelPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1344-1384` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::LookAtDestPixelPosition`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1384-1425` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::NetworkStreamSendAttackPacket`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1425-1486` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendSpecial` (hack çağrısı: `NetworkStreamSendSpecial`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2626`
   - Ozel gonderim: paket header'ina gore ek islem yapar - HEADER_CG_ATTACK icin CRCMagicCube baytlarini paketin sonuna isler (anti-cheat), digerlerini dogrudan kuyruga ekler.
1. `SendSequence` (hack çağrısı: `NetworkStreamSendSequence`) — oyunda: `client: EterLib/NetStream.cpp:838`
   - Paket sirasi (sequence) baytini gonderir: sunucu paket akis sirasini dogrulayip kayip/saldiri tespiti yapar. Her gonderimden sonra cagrilir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::GetMapName`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1486-1504` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GameFunctionsCustom::IsMapHaveInstance`
*Konum (hack):* `EngineX-Pro/GameFunctionsCustom.h:1517-1534` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Globals::ReAddressingInstances`
*Konum (hack):* `EngineX-Pro/Globals.h:779-1173` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetViewport` (hack çağrısı: `SetViewport`) — oyunda: `client: EterPythonLib/PythonGraphic.cpp:97`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AVehHook`
*Konum (hack):* `EngineX-Pro/HWBreakPointHook.cpp:3-12` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `AVehHook`
*Konum (hack):* `EngineX-Pro/HWBreakPointHook.cpp:14-23` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Hooks::NewCPythonApplicationRenderGame`
*Konum (hack):* `EngineX-Pro/HookCore.cpp:2-22` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetTransform` (hack çağrısı: `GetTransform`) — oyunda: `client: GameLib/DungeonBlock.cpp:170`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Hooks::NewCPythonEventManagerRegisterEventSetFromString`
*Konum (hack):* `EngineX-Pro/HookCore.cpp:179-300` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Hooks::NewCNetworkStreamRecv`
*Konum (hack):* `EngineX-Pro/HookCore.cpp:300-433` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `__GlobalPositionToLocalPosition` (hack çağrısı: `__GlobalPositionToLocalPosition`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameActor.cpp:14`
1. `GlobalPositionToLocalPosition` (hack çağrısı: `GlobalPositionToLocalPosition`) — oyunda: `client: UserInterface/PythonBackground.cpp:709`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`
1. `GetMainCharacterIndex` (hack çağrısı: `PlayerGetMainCharacterIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:291`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::map_compare`
*Konum (hack):* `EngineX-Pro/Inventory.h:86-93` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `equal` (hack çağrısı: `equal`) — oyunda: `server: game/src/char_dragonsoul.cpp:147`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::Match`
*Konum (hack):* `EngineX-Pro/Inventory.h:93-113` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::OnUpdate`
*Konum (hack):* `EngineX-Pro/Inventory.h:126-215` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemAttribute` (hack çağrısı: `PlayerGetItemAttribute`) — oyunda: `client: UserInterface/PythonPlayer.cpp:696`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `SendItemUseToItemPacket` (hack çağrısı: `NetworkStreamSendItemUseToItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524`
   - Esyayi baska esya uzerinde kullanma (tas ekleme, bonus degistirme materyali): kaynak/hedef cell.
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::GetItemIconPath`
*Konum (hack):* `EngineX-Pro/Inventory.h:219-242` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemDataPointer` (hack çağrısı: `ItemManagerGetItemDataPointer`) — oyunda: `client: GameLib/ItemManager.cpp:47`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::OnTabbarRefine`
*Konum (hack):* `EngineX-Pro/Inventory.h:242-257` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendRefinePacket` (hack çağrısı: `NetworkStreamSendRefinePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095`
   - Gelistirme (refine) onayi: esya konumu + gelistirme tipi; sunucu malzeme/oran kontrolu yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::OnTabbarActions`
*Konum (hack):* `EngineX-Pro/Inventory.h:257-279` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendShopSellPacketNew` (hack çağrısı: `NetworkStreamSendShopSellPacketNew`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:455`
1. `GetItemCount` (hack çağrısı: `PlayerGetItemCount`) — oyunda: `client: UserInterface/PythonPlayer.cpp:658`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::IDName`
*Konum (hack):* `EngineX-Pro/Inventory.h:279-284` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::OnTabbarBS`
*Konum (hack):* `EngineX-Pro/Inventory.h:284-403` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `GetD3DTexture` (hack çağrısı: `GetD3DTexture`) — oyunda: `client: EterGrnLib/Material.cpp:142`
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Inventory::OnTab1`
*Konum (hack):* `EngineX-Pro/Inventory.h:403-516` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetItemIndex` (hack çağrısı: `PlayerGetItemIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:601`
1. `GetD3DTexture` (hack çağrısı: `GetD3DTexture`) — oyunda: `client: EterGrnLib/Material.cpp:142`
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetItemCount` (hack çağrısı: `PlayerGetItemCount`) — oyunda: `client: UserInterface/PythonPlayer.cpp:658`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::OnStart`
*Konum (hack):* `EngineX-Pro/Item.h:19-24` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::OnTab1`
*Konum (hack):* `EngineX-Pro/Item.h:32-170` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`
1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::OnUpdate`
*Konum (hack):* `EngineX-Pro/Item.h:263-292` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::Slots`
*Konum (hack):* `EngineX-Pro/Item.h:292-357` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Item::Pickup`
*Konum (hack):* `EngineX-Pro/Item.h:357-434` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `SendItemPickUpPacket` (hack çağrısı: `NetworkStreamSendItemPickUpPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:735`
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `LogWindow::Log`
*Konum (hack):* `EngineX-Pro/Logger.h:98-140` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `GetColor` (hack çağrısı: `GetColor`) — oyunda: `client: SphereLib/spherepack.cpp:388`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::OnStart`
*Konum (hack):* `EngineX-Pro/Main.h:148-160` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::OnUpdate`
*Konum (hack):* `EngineX-Pro/Main.h:168-244` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetRace` (hack çağrısı: `PlayerGetRace`) — oyunda: `client: GameLib/ActorInstanceData.cpp:51`
1. `Revive` (hack çağrısı: `Revive`) — oyunda: `client: GameLib/ActorInstance.cpp:538`
1. `GetDistance` (hack çağrısı: `PlayerGetDistance`) — oyunda: `client: UserInterface/InstanceBase.cpp:2619`
1. `SendUseSkillPacket` (hack çağrısı: `NetworkStreamSendUseSkillPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191`
   - Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.
1. `SetAttackKeyState` (hack çağrısı: `PlayerSetAttackKeyState`) — oyunda: `client: UserInterface/PythonPlayerInputKeyboard.cpp:6`
   - Atak tusunun (Space/ctrl vurusu) basili olup olmadigini tutar: m_isAtkKey=true/false. Oyun dongusu (PythonPlayerInputMouse.cpp:381) bu bayragi her kare kontrol ederek saldiriyi tetikler; balik tutma modundaysa (IsFishing…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::OnRender`
*Konum (hack):* `EngineX-Pro/Main.h:244-254` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::OnTab1`
*Konum (hack):* `EngineX-Pro/Main.h:254-296` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `SetAttackKeyState` (hack çağrısı: `PlayerSetAttackKeyState`) — oyunda: `client: UserInterface/PythonPlayerInputKeyboard.cpp:6`
   - Atak tusunun (Space/ctrl vurusu) basili olup olmadigini tutar: m_isAtkKey=true/false. Oyun dongusu (PythonPlayerInputMouse.cpp:381) bu bayragi her kare kontrol ederek saldiriyi tetikler; balik tutma modundaysa (IsFishing…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::OnTab2`
*Konum (hack):* `EngineX-Pro/Main.h:296-339` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Time` (hack çağrısı: `Time`) — oyunda: `server: game/src/input_db.cpp:1691`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::SwordWH`
*Konum (hack):* `EngineX-Pro/Main.h:584-627` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …
1. `SendAttackPacket` (hack çağrısı: `NetworkStreamSendAttackPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599`
   - Melee saldiri talebi: TPacketCGAttack{header=HEADER_CG_ATTACK, bType=uMotAttack(0=normal,1=combo), dwVictimVID} doldurup SendSpecial ile yollar; SendSpecial saldiri paketlerine CRCMagicCube baytlarini ekler (sunucu anti-…

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::BowWH`
*Konum (hack):* `EngineX-Pro/Main.h:627-651` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `SendAddFlyTargetingPacket` (hack çağrısı: `NetworkStreamSendAddFlyTargetingPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736`
   - Ucan mermi (ok/beceri) icin hedef kaydi: dwTargetVID + TPixelPosition varis noktasi; sunucu merminin isabetini buna gore cozer.
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `SendShootPacket` (hack çağrısı: `NetworkStreamSendShootPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721`
   - Yay/ok atisi: HEADER_CG_SHOOT + uSkill. Genellikle AddFlyTargeting ile ciftli calisir (mermi hedefi).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::SkillWH`
*Konum (hack):* `EngineX-Pro/Main.h:658-711` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `SendUseSkillPacket` (hack çağrısı: `NetworkStreamSendUseSkillPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191`
   - Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::SkillWHx50`
*Konum (hack):* `EngineX-Pro/Main.h:711-775` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `SendUseSkillPacket` (hack çağrısı: `NetworkStreamSendUseSkillPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191`
   - Beceri kullanim talebi: TPacketCGUseSkill{bHeader=HEADER_CG_USE_SKILL, dwVnum, dwTargetVID}. Client cooldown/MP/kosullari kontrol eder; sunucu tekrar dogrular.
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::WaitHack`
*Konum (hack):* `EngineX-Pro/Main.h:829-870` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Target` (hack çağrısı: `Target`) — oyunda: `server: game/src/questmanager.cpp:705`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::Odpychaj`
*Konum (hack):* `EngineX-Pro/Main.h:884-931` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::Przyciagaj`
*Konum (hack):* `EngineX-Pro/Main.h:931-976` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetInstanceType` (hack çağrısı: `InstanceBaseGetInstanceType`) — oyunda: `client: UserInterface/InstanceBase.cpp:2568`
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::Other`
*Konum (hack):* `EngineX-Pro/Main.h:977-1024` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::MPPotion`
*Konum (hack):* `EngineX-Pro/Main.h:1024-1061` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Main::HPPotion`
*Konum (hack):* `EngineX-Pro/Main.h:1086-1123` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendItemUsePacket` (hack çağrısı: `NetworkStreamSendItemUsePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486`
   - Envanterdeki esyayi kullanma talebi: TPacketCGItemUse{TItemPos Cell, DWORD dwVID} (cell: pencere+slot konumu). Pot/scroll/yemek kullaniminin kapisi.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainCore::NetworkThread`
*Konum (hack):* `EngineX-Pro/MainCore.cpp:121-139` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SetRecvBufferSize` (hack çağrısı: `SetRecvBufferSize`) — oyunda: `client: EterLib/NetStream.cpp:37`
1. `SetSendBufferSize` (hack çağrısı: `SetSendBufferSize`) — oyunda: `client: EterLib/NetStream.cpp:55`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainCore::UpdateLoop`
*Konum (hack):* `EngineX-Pro/MainCore.cpp:213-266` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::CheckRelogDT`
*Konum (hack):* `EngineX-Pro/MainDungs.h:17-53` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::DemonTowerStart`
*Konum (hack):* `EngineX-Pro/MainDungs.h:53-76` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::AtyvaDemonTowerStart`
*Konum (hack):* `EngineX-Pro/MainDungs.h:76-100` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::Dungeon175Start`
*Konum (hack):* `EngineX-Pro/MainDungs.h:100-124` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::Teleport`
*Konum (hack):* `EngineX-Pro/MainDungs.h:182-199` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::CheckCoords`
*Konum (hack):* `EngineX-Pro/MainDungs.h:199-281` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::Update175`
*Konum (hack):* `EngineX-Pro/MainDungs.h:281-360` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendOnClickPacket` (hack çağrısı: `NetworkStreamSendOnClickPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666`
   - Bir varliga tiklama bildirimi: TPacketCGOnClick{dwVID, bType}. Mob secme/NPC etkilesimi/banka acma gibi 'hedefe dokunma' olaylarinin sunucu bildirimidir. C4US AELDRA bypass'i bu kanali saldiri kanalina cevirir (+0x42 bay…
1. `SendScriptAnswerPacket` (hack çağrısı: `NetworkStreamSendScriptAnswerPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297`
   - NPC/quest diyalog cevabi: secilen secenek indeksi; AutoTalk modulleri diyalog otomasyonunu bununla yapar.
1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::UpdateDT`
*Konum (hack):* `EngineX-Pro/MainDungs.h:360-510` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `SendGiveItemPacket` (hack çağrısı: `NetworkStreamSendGiveItemPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865`
   - Esyayi NPC'ye verme (quest teslimi): dwVID + TItemPos.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainDungs::OnTab1`
*Konum (hack):* `EngineX-Pro/MainDungs.h:534-558` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`
1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::SetImages`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:161-245` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GetMapFolder`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:314-343` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::AddTab`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:366-406` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::AddMenu`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:406-452` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::ShowRadar`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:480-709` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `NEW_GetPixelPosition` (hack çağrısı: `InstanceBaseNEW_GetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:19`
   - Karakterin/varligin guncel piksel pozisyonunu (x,y,z) TPixelPosition icine okur. Botlar hedef mesafesi/yol hesabi icin bunu okur; Boost mevcut konumu almak icin kullanir.
1. `NEW_GetMainActorPtr` (hack çağrısı: `PlayerNEW_GetMainActorPtr`) — oyunda: `client: UserInterface/PythonPlayer.cpp:137`
   - Oyuncunun kendi karakter ornegine (CInstanceBase*) isaretci dondurur. Tum client modulunun 'ben kimim' cozumu budur; null ise karakter ekranda degil (yukleme, olum arasi vb.).
1. `GetD3DTexture` (hack çağrısı: `GetD3DTexture`) — oyunda: `client: EterGrnLib/Material.cpp:142`
1. `GetRotation` (hack çağrısı: `PlayerGetRotation`) — oyunda: `client: GameLib/ActorInstanceRotation.cpp:109`
1. `SCRIPT_SetPixelPosition` (hack çağrısı: `InstanceBaseSCRIPT_SetPixelPosition`) — oyunda: `client: UserInterface/InstanceBaseTransform.cpp:8`
   - Karakterin DUNYADAKI piksel pozisyonunu aninda (teleport gibi) tasir: once __GetBackgroundHeight ile zemin yuksekligi (fz) okunur, sonra NEW_SetPixelPosition -> CGraphicThingInstance::SetCurPixelPosition ile 3B konum set…
1. `SendCharacterStatePacket` (hack çağrısı: `NetworkStreamSendCharacterStatePacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152`
   - Hareket durumu paketi: TPacketCGMove{bHeader=HEADER_CG_CHARACTER_MOVE, bFunc=eFunc, bArg=uArg, bRot=fDstRot/5 (5 derece cozunurluk), lX, lY, dwTime=ELTimer_GetServerMSec()} yollar; once rotasyonu 0-360'a normalize eder, …

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::Menu`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:709-993` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MainForm::Initialize`
*Konum (hack):* `EngineX-Pro/MainForm.cpp:993-1126` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscExtension::ShowBalloon`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:10-47` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `LoadImage` (hack çağrısı: `LoadImage`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:1257`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscExtension::RandomString`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:123-139` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscExtension::RandomInt`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:139-149` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `time` (hack çağrısı: `time`) — oyunda: `client: EterBase/error.cpp:27`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscExtension::CurrentDateTime`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:188-200` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `time` (hack çağrısı: `time`) — oyunda: `client: EterBase/error.cpp:27`
1. `localtime` (hack çağrısı: `localtime`) — oyunda: `client: EterBase/error.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `MiscExtension::CurrentDateTimeShort`
*Konum (hack):* `EngineX-Pro/MiscExtension.h:200-211` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `time` (hack çağrısı: `time`) — oyunda: `client: EterBase/error.cpp:27`
1. `localtime` (hack çağrısı: `localtime`) — oyunda: `client: EterBase/error.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Network::Process`
*Konum (hack):* `EngineX-Pro/Network.cpp:209-286` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnConnectSuccess` (hack çağrısı: `OnConnectSuccess`) — oyunda: `client: EterLib/NetStream.cpp:869`
1. `time` (hack çağrısı: `time`) — oyunda: `client: EterBase/error.cpp:27`
1. `OnConnectFailure` (hack çağrısı: `OnConnectFailure`) — oyunda: `client: EterLib/NetStream.cpp:874`
1. `OnRemoteDisconnect` (hack çağrısı: `OnRemoteDisconnect`) — oyunda: `client: EterLib/NetStream.cpp:861`
1. `OnProcess` (hack çağrısı: `OnProcess`) — oyunda: `client: EterLib/NetStream.cpp:856`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Network::Connect`
*Konum (hack):* `EngineX-Pro/Network.cpp:349-386` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnRemoteDisconnect` (hack çağrısı: `OnRemoteDisconnect`) — oyunda: `client: EterLib/NetStream.cpp:861`
1. `SetConnection` (hack çağrısı: `SetConnection`) — oyunda: `client: UserInterface/PythonNetworkDatagram.cpp:76`
1. `OnConnectFailure` (hack çağrısı: `OnConnectFailure`) — oyunda: `client: EterLib/NetStream.cpp:874`
1. `time` (hack çağrısı: `time`) — oyunda: `client: EterBase/error.cpp:27`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketHandler::Process`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:30-53` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `CheckPacket` (hack çağrısı: `CheckPacket`) — oyunda: `client: UserInterface/PythonNetworkStream.cpp:528`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketHandler::SendHeartBeatResponse`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:53-66` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Send` (hack çağrısı: `Send`) — oyunda: `client: EterLib/NetStream.cpp:758`
   - (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketHandler::RecvHeartBeatPacket`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:66-77` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Recv` (hack çağrısı: `Recv`) — oyunda: `client: EterLib/NetStream.cpp:718`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketHandler::SendAuthPacket`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:77-91` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Send` (hack çağrısı: `Send`) — oyunda: `client: EterLib/NetStream.cpp:758`
   - (Client) Genel paket kuyruguna veri ekleme: ham buffer + uzunluk; tum Send* bunun uzerine kurulur. (HyperBot) Network::Send client ag kuyruguna erisir; sniffer burada dinler.

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketHandler::RecvAuthPacket`
*Konum (hack):* `EngineX-Pro/PacketHandler.cpp:93-216` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Recv` (hack çağrısı: `Recv`) — oyunda: `client: EterLib/NetStream.cpp:718`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketSniffer::ProcessSendPacket`
*Konum (hack):* `EngineX-Pro/PacketSniffer.h:77-100` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PacketSniffer::ProcessRecvPacket`
*Konum (hack):* `EngineX-Pro/PacketSniffer.h:110-136` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PatternScan::FindPattern`
*Konum (hack):* `EngineX-Pro/PatternScan.h:11-44` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Search` (hack çağrısı: `Search`) — oyunda: `server: db/src/Config.cpp:152`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PatternScan::FindPatternGlobal`
*Konum (hack):* `EngineX-Pro/PatternScan.h:44-50` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Search` (hack çağrısı: `Search`) — oyunda: `server: db/src/Config.cpp:152`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `ProtectExtension::GetCpuId`
*Konum (hack):* `EngineX-Pro/ProtectExtension.h:36-50` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `to_string` (hack çağrısı: `to_string`) — oyunda: `client: EterBase/error.cpp:31`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `GetHardwareId`
*Konum (hack):* `EngineX-Pro/ProtectExtension.h:167-195` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Protection::OnStart`
*Konum (hack):* `EngineX-Pro/Protection.h:7-12` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `OnStop` (hack çağrısı: `OnStop`) — oyunda: `client: UserInterface/PythonPlayerEventHandler.cpp:88`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PythonExtension::CheckImportNames`
*Konum (hack):* `EngineX-Pro/PythonExtension.h:6-41` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PythonGameFunctions::PlayerGetStatus`
*Konum (hack):* `EngineX-Pro/PythonGameFunctions.h:4-16` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetStatus` (hack çağrısı: `PlayerGetStatus`) — oyunda: `client: UserInterface/PythonPlayer.cpp:478`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PythonScript::OnStart`
*Konum (hack):* `EngineX-Pro/PythonScript.h:5-11` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `PythonScript::OnTab1`
*Konum (hack):* `EngineX-Pro/PythonScript.h:24-38` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Security::NewPy_InitModule4`
*Konum (hack):* `EngineX-Pro/Security.h:39-62` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::LoadItemFilter`
*Konum (hack):* `EngineX-Pro/Settings.h:9-24` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Read` (hack çağrısı: `Read`) — oyunda: `client: EterBase/MappedFile.cpp:229`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::SaveItemFilter`
*Konum (hack):* `EngineX-Pro/Settings.h:24-38` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Write` (hack çağrısı: `Write`) — oyunda: `client: EterBase/FileBase.cpp:94`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::LoadFarm`
*Konum (hack):* `EngineX-Pro/Settings.h:38-68` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Read` (hack çağrısı: `Read`) — oyunda: `client: EterBase/MappedFile.cpp:229`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::SaveFarm`
*Konum (hack):* `EngineX-Pro/Settings.h:68-89` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `Write` (hack çağrısı: `Write`) — oyunda: `client: EterBase/FileBase.cpp:94`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::LoadServerVariables`
*Konum (hack):* `EngineX-Pro/Settings.h:89-124` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `insert` (hack çağrısı: `insert`) — oyunda: `client: EterBase/Poly/Poly.cpp:547`
1. `make_pair` (hack çağrısı: `make_pair`) — oyunda: `client: GameLib/MapOutdoorRender.cpp:125`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::Load`
*Konum (hack):* `EngineX-Pro/Settings.h:124-866` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Read` (hack çağrısı: `Read`) — oyunda: `client: EterBase/MappedFile.cpp:229`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Settings::Save`
*Konum (hack):* `EngineX-Pro/Settings.h:866-1063` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Write` (hack çağrısı: `Write`) — oyunda: `client: EterBase/FileBase.cpp:94`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Spam::OnUpdate`
*Konum (hack):* `EngineX-Pro/Spam.h:47-181` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendChatPacket` (hack çağrısı: `NetworkStreamSendChatPacket`) — oyunda: `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206`
   - Sohbet mesaji: TPacketCGChat{header, len, type} + metin; type: NORMAL/SHOUT/PARTY/GUILD/WHISPER... Bosluk mesaj yollamaz; client sutun siniri uygular, sunucu rate-limit ve renk/kanal kurallari uygular.
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `GetNameString` (hack çağrısı: `InstanceBaseGetNameString`) — oyunda: `client: UserInterface/InstanceBase.cpp:2183`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Spam::OnTab1`
*Konum (hack):* `EngineX-Pro/Spam.h:181-251` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `Time` (hack çağrısı: `Time`) — oyunda: `server: game/src/input_db.cpp:1691`
1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CSplash::OnPaint`
*Konum (hack):* `EngineX-Pro/SplashScreen.cpp:42-74` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetClientRect` (hack çağrısı: `GetClientRect`) — oyunda: `client: EterLib/MSWindow.cpp:150`
1. `SetBkMode` (hack çağrısı: `SetBkMode`) — oyunda: `client: EterLib/GrpDIB.cpp:72`
1. `SetTextColor` (hack çağrısı: `SetTextColor`) — oyunda: `client: EterLib/TextBar.cpp:39`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CSplash::SetBitmap`
*Konum (hack):* `EngineX-Pro/SplashScreen.cpp:200-210` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `LoadImage` (hack çağrısı: `LoadImage`) — oyunda: `client: EterPythonLib/PythonWindow.cpp:1257`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CSplash::FreeResources`
*Konum (hack):* `EngineX-Pro/SplashScreen.cpp:240-247` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `DeleteObject` (hack çağrısı: `DeleteObject`) — oyunda: `server: game/src/input_db.cpp:1900`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `CSplash::CloseSplash`
*Konum (hack):* `EngineX-Pro/SplashScreen.cpp:247-260` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `SendMessage` (hack çağrısı: `SendMessage`) — oyunda: `server: game/src/party.cpp:860`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `Status::OnUpdate`
*Konum (hack):* `EngineX-Pro/Status.h:106-294` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `GetMainCharacterIndex` (hack çağrısı: `PlayerGetMainCharacterIndex`) — oyunda: `client: UserInterface/PythonPlayer.cpp:291`
1. `GetTargetVID` (hack çağrısı: `PlayerGetTargetVID`) — oyunda: `client: UserInterface/PythonPlayerInput.cpp:76`
1. `GetVirtualNumber` (hack çağrısı: `InstanceBaseGetVirtualNumber`) — oyunda: `client: UserInterface/InstanceBase.cpp:2578`
   - Varligin mob vnum'unu (gercek tur numarasi) dondurur; kaynak (resource) mob ayrimi, whitelist eslestirme botlarda bununla yapilir (C4US InstanceIsResource vnum tablosu 20047-30306).
1. `GetInstancePtr` (hack çağrısı: `CharacterManagerGetInstancePtr`) — oyunda: `client: UserInterface/PythonCharacterManager.cpp:638`
1. `GetPixelPosition` (hack çağrısı: `PlayerGetPixelPosition`) — oyunda: `client: GameLib/ActorInstancePosition.cpp:83`
   - Python katmanindan konum okuma; bot modulleri harita konumu almak icin kullanir.
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ToUpper`
*Konum (hack):* `EngineX-Pro/StringExtension.h:3-11` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `transform` (hack çağrısı: `transform`) — oyunda: `client: GameLib/ItemManager.cpp:436`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ReplaceString`
*Konum (hack):* `EngineX-Pro/StringExtension.h:19-28` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`
1. `replace` (hack çağrısı: `replace`) — oyunda: `client: UserInterface/UserInterface.cpp:221`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::Contains`
*Konum (hack):* `EngineX-Pro/StringExtension.h:28-36` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `transform` (hack çağrısı: `transform`) — oyunda: `client: GameLib/ItemManager.cpp:436`
1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`
1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ContainsW`
*Konum (hack):* `EngineX-Pro/StringExtension.h:36-43` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::StringFormat`
*Konum (hack):* `EngineX-Pro/StringExtension.h:99-122` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::StringFormat2`
*Konum (hack):* `EngineX-Pro/StringExtension.h:122-141` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `reset` (hack çağrısı: `reset`) — oyunda: `server: game/src/buffer_manager.cpp:34`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::StringFormatChar`
*Konum (hack):* `EngineX-Pro/StringExtension.h:141-159` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`
1. `reset` (hack çağrısı: `reset`) — oyunda: `server: game/src/buffer_manager.cpp:34`
1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::BYTEToAsciiString`
*Konum (hack):* `EngineX-Pro/StringExtension.h:159-184` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `string` (hack çağrısı: `string`) — oyunda: `client: GameLib/Area.cpp:792`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::GetWCharFromString`
*Konum (hack):* `EngineX-Pro/StringExtension.h:202-207` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ConstCharFromWChar`
*Konum (hack):* `EngineX-Pro/StringExtension.h:207-214` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::StringFromWChar`
*Konum (hack):* `EngineX-Pro/StringExtension.h:214-221` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::StringFromWString`
*Konum (hack):* `EngineX-Pro/StringExtension.h:221-227` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::Split`
*Konum (hack):* `EngineX-Pro/StringExtension.h:227-244` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `begin` (hack çağrısı: `begin`) — oyunda: `client: UserInterface/UserInterface.cpp:228`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::Split2`
*Konum (hack):* `EngineX-Pro/StringExtension.h:244-260` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `find` (hack çağrısı: `find`) — oyunda: `client: GameLib/MapOutdoorRenderHTP.cpp:461`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ASCIIToUTF8`
*Konum (hack):* `EngineX-Pro/StringExtension.h:338-348` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::UTF8ToASCII`
*Konum (hack):* `EngineX-Pro/StringExtension.h:348-360` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::ASCIIToUTF8`
*Konum (hack):* `EngineX-Pro/StringExtension.h:362-369` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `StringExtension::UTF8ToASCII`
*Konum (hack):* `EngineX-Pro/StringExtension.h:369-378` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `size` (hack çağrısı: `size`) — oyunda: `server: game/src/buffer_manager.cpp:29`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `VTableSwapHook::hook`
*Konum (hack):* `EngineX-Pro/VTableSwapHook.cpp:18-60` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `reset` (hack çağrısı: `reset`) — oyunda: `server: game/src/buffer_manager.cpp:34`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

#### `VTableSwapHook::unHook`
*Konum (hack):* `EngineX-Pro/VTableSwapHook.cpp:60-78` | *Proje:* C4US | *Kategori:* —
**Oyunda karşılığı:** ❌ YOK — ama **içindeki şu oyun fonksiyonları VAR**:

1. `reset` (hack çağrısı: `reset`) — oyunda: `server: game/src/buffer_manager.cpp:34`

**Bununla ne yapılabilir:** İç oyun fonksiyonlarının birleşimiyle hack davranışı üretilir (ayrıntı: Bölüm 10 — Uygulamalı Araştırma). Bu fonksiyon, oyunun kendi API'lerini birleştiren bir kompozittir; sunucu onaylayacağı paketleri oyunun kendi fonksiyonlarıyla gönderir.

## 7. OYUNDA OLMAYANLAR — Tam Liste

> Bunlar oyun kaynağında karşılığı olmayan fonksiyonlardır: hile DLL'inin kendi altyapısı (GUI, config, hook, hafıza, matematik) veya saf hack mantığı. Bazıları Bölüm 6'daki sarmalayıcıların bileşenleridir.

### HyperBot — 382 fonksiyon

| # | Fonksiyon | Dosya:Satır | Sınıf | Ne yapar (kısa) |
|---|---|---|---|---|
| 1 | `AutoItemPickup::Init` | `HyperBot/AutoItemPickup.cpp:2` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 2 | `AutoItemPickup::OnMenuFrame` | `HyperBot/AutoItemPickup.cpp:8` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 3 | `AutoItemPickup::OnIteration` | `HyperBot/AutoItemPickup.cpp:166` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 4 | `AutoItemPickup::PostIteration` | `HyperBot/AutoItemPickup.cpp:180` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 5 | `AutoItemPickup::OnRenderScreen` | `HyperBot/AutoItemPickup.cpp:215` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 6 | `AutoItemPickup::PickUpTarget` | `HyperBot/AutoItemPickup.cpp:234` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 7 | `AutoItemPickup::DumpItemsWhitelist` | `HyperBot/AutoItemPickup.cpp:390` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 8 | `AutoItemPickup::AutoItemPickup` | `HyperBot/AutoItemPickup.h:4` | AutoItemPickup | Otomatik esya toplama: yerdeki esya taranir, beyaz liste fil |
| 9 | `Target::m_vid` | `HyperBot/AutoItemPickup.h:19` | Target | core |
| 10 | `Target::m_vid` | `HyperBot/AutoItemPickup.h:21` | Target | core |
| 11 | `HookManager` | `HyperBot/Backend.cpp:70` | — | hook |
| 12 | `Console::WriteLine` | `HyperBot/Backend.h:102` | Console | Dahili komut konsolu: gelistirici komutlari calistirir. |
| 13 | `Background::GlobalPosToMapInfo` | `HyperBot/Background.cpp:2` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 14 | `Background::GetCurrentMapName` | `HyperBot/Background.cpp:10` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 15 | `Background::GlobalToLocalPosition` | `HyperBot/Background.cpp:20` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 16 | `Background::LocalToGlobalPosition` | `HyperBot/Background.cpp:26` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 17 | `Background::IsBlockedCoord` | `HyperBot/Background.cpp:39` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 18 | `Background::IsBlockedCoord` | `HyperBot/Background.cpp:45` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 19 | `Background::IsAttrOn` | `HyperBot/Background.cpp:53` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 20 | `Background::GetTerrainIndexFromWorldPos` | `HyperBot/Background.cpp:100` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 21 | `Background::GetMinimapTerrainTexture` | `HyperBot/Background.cpp:124` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 22 | `Background::GetMinimapTerrainArray` | `HyperBot/Background.cpp:146` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 23 | `Background::ReloadResource` | `HyperBot/Background.cpp:181` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 24 | `Background::SetViewDistance` | `HyperBot/Background.cpp:188` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 25 | `Background::_GetTerrainNumFromCoord` | `HyperBot/Background.cpp:195` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 26 | `Background::_GetTerrainPointer` | `HyperBot/Background.cpp:204` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 27 | `Background::_IsAttrOn` | `HyperBot/Background.cpp:224` | Background | Dunya/harita erisimi: yukseklik sorgusu, engel kontrolu, har |
| 28 | `CGraphicImageTexture::GetWidth` | `HyperBot/Background.cpp:244` | CGraphicImageTexture | client bellek/oyun durumu okuma sarmalayicisi |
| 29 | `CGraphicImageTexture::GetHeight` | `HyperBot/Background.cpp:249` | CGraphicImageTexture | client bellek/oyun durumu okuma sarmalayicisi |
| 30 | `CGraphicImageTexture::GetSize` | `HyperBot/Background.cpp:254` | CGraphicImageTexture | client bellek/oyun durumu okuma sarmalayicisi |
| 31 | `ConfigManager::ConfigManager` | `HyperBot/ConfigManager.cpp:6` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 32 | `ConfigManager::CreateDump` | `HyperBot/ConfigManager.cpp:36` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 33 | `ConfigManager::GetCheatDirectory` | `HyperBot/ConfigManager.cpp:47` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 34 | `ConfigManager::WriteConfigToFile` | `HyperBot/ConfigManager.cpp:57` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 35 | `ConfigManager::RegenerateConfigFile` | `HyperBot/ConfigManager.cpp:93` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 36 | `ConfigManager::GetKeyValue` | `HyperBot/ConfigManager.cpp:102` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 37 | `ConfigManager::IsValidValue` | `HyperBot/ConfigManager.cpp:135` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 38 | `ConfigManager::GenerateConfigFile` | `HyperBot/ConfigManager.cpp:143` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 39 | `ConfigManager::CreateMobsDump` | `HyperBot/ConfigManager.cpp:261` | ConfigManager | Yapilandirma yoneticisi: EBool enum'u ile on/off ayarlari; i |
| 40 | `HookManager::WndProc` | `HyperBot/D3DDevice.cpp:213` | HookManager | HyperBot hook yoneticisi: client fonksiyonlarina detour/minh |
| 41 | `HookManager::SendSyncPositionPacket` | `HyperBot/DevModeHooks.cpp:83` | HookManager | HyperBot hook yoneticisi: client fonksiyonlarina detour/minh |
| 42 | `Entity::GetRotationTo` | `HyperBot/Entity.cpp:4` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 43 | `Entity::GetRotationTo` | `HyperBot/Entity.cpp:9` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 44 | `Entity::IsCloseToPosition` | `HyperBot/Entity.cpp:29` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 45 | `Entity::HasEffect` | `HyperBot/Entity.cpp:34` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 46 | `Entity::IsSelectedTarget` | `HyperBot/Entity.cpp:41` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 47 | `Entity::IsAlive` | `HyperBot/Entity.cpp:85` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 48 | `Entity::IsStuned` | `HyperBot/Entity.cpp:92` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 49 | `Entity::GetName` | `HyperBot/Entity.cpp:145` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 50 | `Entity::GetVID` | `HyperBot/Entity.cpp:158` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 51 | `Entity::GetEffectMap` | `HyperBot/Entity.cpp:247` | Entity | Dunyadaki varliklarin (mob/NPC/oyuncu/esya) soyutlamasi: VID |
| 52 | `Player::LookAtDestPixelPosition` | `HyperBot/Entity.cpp:259` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 53 | `Player::MoveToDestPixelPosition` | `HyperBot/Entity.cpp:266` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 54 | `Player::MoveFromDestPosition` | `HyperBot/Entity.cpp:273` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 55 | `Player::SetAttackKey` | `HyperBot/Entity.cpp:291` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 56 | `Player::StopWalking` | `HyperBot/Entity.cpp:314` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 57 | `Player::GetBowRange` | `HyperBot/Entity.cpp:420` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 58 | `Player::GetTarget` | `HyperBot/Entity.cpp:432` | Player | Oyuncu verisi okuma/yazma yardimcilari (stat, skill, envante |
| 59 | `HyperGUI::HyperGUI` | `HyperBot/GUI.cpp:3` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 60 | `HyperGUI::Slide` | `HyperBot/GUI.cpp:16` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 61 | `HyperGUI::ClearAnimBuffer` | `HyperBot/GUI.cpp:35` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 62 | `HyperGUI::SetInitialPosition` | `HyperBot/GUI.cpp:46` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 63 | `HyperGUI::RenderDebug` | `HyperBot/GUI.cpp:57` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 64 | `RenderPlayers` | `HyperBot/GUI.cpp:174` | — | visual |
| 65 | `HyperGUI::AnimateMainMenu` | `HyperBot/GUI.cpp:234` | HyperGUI | HyperBot ImGui arayuz katmani: sekmeler, toggle'lar, renk te |
| 66 | `GameInformer::Init` | `HyperBot/GameInformer.cpp:2` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 67 | `GameInformer::OnMenuFrame` | `HyperBot/GameInformer.cpp:7` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 68 | `GameInformer::OnIteration` | `HyperBot/GameInformer.cpp:99` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 69 | `GameInformer::PostIteration` | `HyperBot/GameInformer.cpp:104` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 70 | `GameInformer::OnRenderWorld` | `HyperBot/GameInformer.cpp:109` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 71 | `GameInformer::OnRenderScreen` | `HyperBot/GameInformer.cpp:114` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 72 | `GameInformer::IsValid` | `HyperBot/GameInformer.cpp:119` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 73 | `GameInformer::IsLocalSpectated` | `HyperBot/GameInformer.cpp:124` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 74 | `GameInformer::GameInformer` | `HyperBot/GameInformer.h:4` | GameInformer | Oyun durumu bilgi saglayici: sunucu saati, oyuncu durumu, he |
| 75 | `GameMainInstance::GameMainInstance` | `HyperBot/GameMainInstance.cpp:2` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 76 | `GameMainInstance` | `HyperBot/GameMainInstance.cpp:13` | — | config |
| 77 | `GameMainInstance::GetCursorEntity` | `HyperBot/GameMainInstance.cpp:24` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 78 | `GameMainInstance::GetSelectedEntity` | `HyperBot/GameMainInstance.cpp:30` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 79 | `GameMainInstance::GetEntity` | `HyperBot/GameMainInstance.cpp:36` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 80 | `GameMainInstance::GetEntity` | `HyperBot/GameMainInstance.cpp:85` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 81 | `GameMainInstance::GetItems` | `HyperBot/GameMainInstance.cpp:170` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 82 | `GameMainInstance::GetLocalPlayer` | `HyperBot/GameMainInstance.cpp:217` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 83 | `GameMainInstance::GetNetworkMgr` | `HyperBot/GameMainInstance.cpp:223` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 84 | `GameMainInstance::GetNonPlayerData` | `HyperBot/GameMainInstance.cpp:235` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 85 | `GameMainInstance::GetNonPlayerData` | `HyperBot/GameMainInstance.cpp:256` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 86 | `GameMainInstance::GetItemMapPtr` | `HyperBot/GameMainInstance.cpp:271` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 87 | `GameMainInstance::GetEntityMapPtr` | `HyperBot/GameMainInstance.cpp:284` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 88 | `GameMainInstance::GetGroundItemMapPtr` | `HyperBot/GameMainInstance.cpp:296` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 89 | `GameMainInstance::GetMobTableMapPtr` | `HyperBot/GameMainInstance.cpp:304` | GameMainInstance | Client ana ornek (instance) erisimleri: oyuncu/harita durumu |
| 90 | `ICheatBase::ICheatBase` | `HyperBot/ICheatBase.h:5` | ICheatBase | core |
| 91 | `Item::GetItemSlot` | `HyperBot/Item.cpp:2` | Item | client bellek/oyun durumu okuma sarmalayicisi |
| 92 | `Item::GetItemVID` | `HyperBot/Item.cpp:40` | Item | client bellek/oyun durumu okuma sarmalayicisi |
| 93 | `Item::__GetItemVID` | `HyperBot/Item.cpp:45` | Item | item |
| 94 | `GroundItemData::GetRadius` | `HyperBot/Item.cpp:80` | GroundItemData | Yerdeki esya bilgisinin modeli (VID, vnum, pozisyon). |
| 95 | `GroundItemData::GetOwnerName` | `HyperBot/Item.cpp:85` | GroundItemData | Yerdeki esya bilgisinin modeli (VID, vnum, pozisyon). |
| 96 | `GroundItemData::CanBePickedUp` | `HyperBot/Item.cpp:99` | GroundItemData | Yerdeki esya bilgisinin modeli (VID, vnum, pozisyon). |
| 97 | `ItemData::GetNameW` | `HyperBot/Item.cpp:110` | ItemData | Envanter esya bilgisi (vnum, count, slots/bonuslar). |
| 98 | `ItemData::GetName` | `HyperBot/Item.cpp:115` | ItemData | Envanter esya bilgisi (vnum, count, slots/bonuslar). |
| 99 | `ItemData::GetDescryption` | `HyperBot/Item.cpp:120` | ItemData | Envanter esya bilgisi (vnum, count, slots/bonuslar). |
| 100 | `ItemData::GetIconPath` | `HyperBot/Item.cpp:125` | ItemData | Envanter esya bilgisi (vnum, count, slots/bonuslar). |
| 101 | `ItemData::GetModelPath` | `HyperBot/Item.cpp:132` | ItemData | Envanter esya bilgisi (vnum, count, slots/bonuslar). |
| 102 | `SItemPos::SItemPos` | `HyperBot/Item.h:112` | SItemPos | item |
| 103 | `SItemPos::SItemPos` | `HyperBot/Item.h:117` | SItemPos | item |
| 104 | `Math::RotatePoint` | `HyperBot/Math.cpp:1` | Math | core |
| 105 | `Math::CalcDeltaPoints` | `HyperBot/Math.cpp:18` | Math | core |
| 106 | `Memory::FindSignature` | `HyperBot/Memory.cpp:34` | Memory | Hafiza okuma/yazma yardimcilari (adres tabanli deger erisimi |
| 107 | `Memory::FindSignatures` | `HyperBot/Memory.cpp:68` | Memory | Hafiza okuma/yazma yardimcilari (adres tabanli deger erisimi |
| 108 | `Memory::MapSignatures` | `HyperBot/Memory.cpp:129` | Memory | Hafiza okuma/yazma yardimcilari (adres tabanli deger erisimi |
| 109 | `Memory::CallVirtualFn` | `HyperBot/Memory.h:10` | Memory | Hafiza okuma/yazma yardimcilari (adres tabanli deger erisimi |
| 110 | `MiscHacks::Init` | `HyperBot/MiscHacks.cpp:6` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 111 | `MiscHacks::OnIteration` | `HyperBot/MiscHacks.cpp:103` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 112 | `MiscHacks::PostIteration` | `HyperBot/MiscHacks.cpp:108` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 113 | `MiscHacks::OnRenderWorld` | `HyperBot/MiscHacks.cpp:112` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 114 | `MiscHacks::OnRenderScreen` | `HyperBot/MiscHacks.cpp:116` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 115 | `MiscHacks::IsValid` | `HyperBot/MiscHacks.cpp:121` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 116 | `MiscHacks::UnlockCamerZoom` | `HyperBot/MiscHacks.cpp:164` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 117 | `MiscHacks::DisableFog` | `HyperBot/MiscHacks.cpp:170` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 118 | `MiscHacks::MiscHacks` | `HyperBot/MiscHacks.h:4` | MiscHacks | Gorsel/kalite hack'leri: hiz, zoom, sis, oto-pasif beceri. W |
| 119 | `Network::__Warp` | `HyperBot/Network.cpp:21` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 120 | `Network::GetPacketsPerSec` | `HyperBot/Network.cpp:59` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 121 | `Network::GetPacketsCount` | `HyperBot/Network.cpp:77` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 122 | `Network::GetAvailablePackets` | `HyperBot/Network.cpp:82` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 123 | `Network::GetMaxPacketsCount` | `HyperBot/Network.cpp:87` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 124 | `Network::UpdatePacketSent` | `HyperBot/Network.cpp:92` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 125 | `Network::GetTargetEntity` | `HyperBot/Network.cpp:97` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 126 | `Network::NotifyShowMap` | `HyperBot/Network.cpp:109` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 127 | `Network::ShouldSend` | `HyperBot/Network.cpp:114` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 128 | `Network::SendPickUpItemPacket` | `HyperBot/Network.cpp:142` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 129 | `Network::SendSyncPositionPacket` | `HyperBot/Network.cpp:172` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 130 | `TPacketGCItemDelDeprecate::count` | `HyperBot/PacketDefs.h:1693` | TPacketGCItemDelDeprecate | core |
| 131 | `SPacketGCHybridCryptKeys::m_pStream` | `HyperBot/PacketDefs.h:2613` | SPacketGCHybridCryptKeys | core |
| 132 | `SPacketGCHybridCryptKeys::iKeyStreamLen` | `HyperBot/PacketDefs.h:2616` | SPacketGCHybridCryptKeys | core |
| 133 | `SPacketGCHybridCryptKeys::SPacketGCHybridCryptKeys` | `HyperBot/PacketDefs.h:2619` | SPacketGCHybridCryptKeys | security |
| 134 | `SPacketGCHybridSDB::m_pStream` | `HyperBot/PacketDefs.h:2644` | SPacketGCHybridSDB | core |
| 135 | `SPacketGCHybridSDB::iSDBStreamLen` | `HyperBot/PacketDefs.h:2647` | SPacketGCHybridSDB | core |
| 136 | `SPacketGCHybridSDB::SPacketGCHybridSDB` | `HyperBot/PacketDefs.h:2650` | SPacketGCHybridSDB | network |
| 137 | `SPacketCGDragonSoulRefine::header` | `HyperBot/PacketDefs.h:2772` | SPacketCGDragonSoulRefine | core |
| 138 | `SPacketGCDragonSoulRefine::header` | `HyperBot/PacketDefs.h:2781` | SPacketGCDragonSoulRefine | core |
| 139 | `PacketSniffer::PrintASCII` | `HyperBot/PacketSniffer.cpp:5` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 140 | `PacketSniffer::DumpPacket` | `HyperBot/PacketSniffer.cpp:48` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 141 | `PacketSniffer::PacketSniffer` | `HyperBot/PacketSniffer.cpp:88` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 142 | `PacketSniffer::OnRecv` | `HyperBot/PacketSniffer.cpp:94` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 143 | `PacketSniffer::OnSend` | `HyperBot/PacketSniffer.cpp:105` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 144 | `PacketSniffer::SetSendFilter` | `HyperBot/PacketSniffer.cpp:116` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 145 | `PacketSniffer::SetRecvFilter` | `HyperBot/PacketSniffer.cpp:121` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 146 | `PacketSniffer::GetHeaderName` | `HyperBot/PacketSniffer.cpp:126` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 147 | `RouteCreator` | `HyperBot/RouteCreator.cpp:9` | — | core |
| 148 | `RouteCreator::Init` | `HyperBot/RouteCreator.cpp:13` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 149 | `RouteCreator::OnMenuFrame` | `HyperBot/RouteCreator.cpp:18` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 150 | `RouteCreator::OnIteration` | `HyperBot/RouteCreator.cpp:56` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 151 | `RouteCreator::OnRenderScreen` | `HyperBot/RouteCreator.cpp:97` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 152 | `RouteCreator::IsValid` | `HyperBot/RouteCreator.cpp:135` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 153 | `RouteCreator::OnRecv` | `HyperBot/RouteCreator.cpp:251` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 154 | `RouteCreator::ShouldOpenScriptWindow` | `HyperBot/RouteCreator.cpp:272` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 155 | `RouteCreator::StopRecording` | `HyperBot/RouteCreator.cpp:288` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 156 | `RouteCreator::OnClickNPC` | `HyperBot/RouteCreator.cpp:323` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 157 | `RouteCreator::OnGiveItem` | `HyperBot/RouteCreator.cpp:333` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 158 | `RouteCreator::OnUseItemToAnotherItem` | `HyperBot/RouteCreator.cpp:355` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 159 | `RouteCreator::OnSendChatMsg` | `HyperBot/RouteCreator.cpp:366` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 160 | `RouteCreator::OnRefine` | `HyperBot/RouteCreator.cpp:377` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 161 | `RouteCreator::OnScriptButton` | `HyperBot/RouteCreator.cpp:388` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 162 | `RouteCreator::OnQuestConfirm` | `HyperBot/RouteCreator.cpp:393` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 163 | `RouteCreator::OnScriptSelectItem` | `HyperBot/RouteCreator.cpp:398` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 164 | `RouteCreator::OnQuestInputString` | `HyperBot/RouteCreator.cpp:403` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 165 | `RouteCreator::OnScriptAnswer` | `HyperBot/RouteCreator.cpp:408` | RouteCreator | Yol planlayici: harita uzerinde noktalar arasi guvenli yol u |
| 166 | `Screen::RenderLine3D` | `HyperBot/Screen.cpp:15` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 167 | `Screen::RenderCircle3D` | `HyperBot/Screen.cpp:26` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 168 | `Screen::RenderAABB3D` | `HyperBot/Screen.cpp:40` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 169 | `Screen::RenderCircleProgress3D` | `HyperBot/Screen.cpp:51` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 170 | `Screen::UpdateWorldState` | `HyperBot/Screen.cpp:150` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 171 | `Screen::BackupRenderState` | `HyperBot/Screen.cpp:159` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 172 | `Screen::_RenderLine` | `HyperBot/Screen.cpp:210` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 173 | `Screen::_RenderAABB` | `HyperBot/Screen.cpp:299` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 174 | `Screen::_SetPDTStream` | `HyperBot/Screen.cpp:325` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 175 | `Screen::_SetStreamSource` | `HyperBot/Screen.cpp:361` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 176 | `Screen::_SetTexture` | `HyperBot/Screen.cpp:400` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 177 | `Screen::_SetVertexShader` | `HyperBot/Screen.cpp:409` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 178 | `Screen::DrawStringDbg` | `HyperBot/Screen.cpp:418` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 179 | `Screen::DrawString` | `HyperBot/Screen.cpp:445` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 180 | `Screen::DrawRectFilled` | `HyperBot/Screen.cpp:476` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 181 | `Screen::DrawRectFilled` | `HyperBot/Screen.cpp:481` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 182 | `Screen::DrawRectGradient` | `HyperBot/Screen.cpp:486` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 183 | `Screen::DrawRectGradient` | `HyperBot/Screen.cpp:491` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 184 | `Screen::DrawRoundedRectFilled` | `HyperBot/Screen.cpp:496` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 185 | `Screen::DrawRoundedRectFilled` | `HyperBot/Screen.cpp:501` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 186 | `Screen::DrawRoundedRect` | `HyperBot/Screen.cpp:506` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 187 | `Screen::DrawRoundedRect` | `HyperBot/Screen.cpp:511` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 188 | `Screen::DrawRect` | `HyperBot/Screen.cpp:516` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 189 | `Screen::DrawRect` | `HyperBot/Screen.cpp:521` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 190 | `Screen::DrawRectOutlined` | `HyperBot/Screen.cpp:526` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 191 | `Screen::DrawRectOutlined` | `HyperBot/Screen.cpp:533` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 192 | `Screen::DrawCircleOutlined` | `HyperBot/Screen.cpp:538` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 193 | `Screen::DrawCircleProgressBar` | `HyperBot/Screen.cpp:545` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 194 | `Screen::DrawLine` | `HyperBot/Screen.cpp:552` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 195 | `Screen::DrawLine` | `HyperBot/Screen.cpp:557` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 196 | `Screen::DrawLine` | `HyperBot/Screen.cpp:562` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 197 | `Screen::DrawTriangleFilled` | `HyperBot/Screen.cpp:569` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 198 | `Screen::DrawTriangle` | `HyperBot/Screen.cpp:574` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 199 | `Screen::DrawCountingBar` | `HyperBot/Screen.cpp:579` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 200 | `Screen::DrawProgressBar` | `HyperBot/Screen.cpp:600` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 201 | `Screen::DrawImageRotated` | `HyperBot/Screen.cpp:618` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 202 | `Screen::DrawImage` | `HyperBot/Screen.cpp:647` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 203 | `Screen::DrawCircle` | `HyperBot/Screen.cpp:664` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 204 | `Screen::DrawCircleFilled` | `HyperBot/Screen.cpp:669` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 205 | `Screen::GetCursorPos` | `HyperBot/Screen.cpp:674` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 206 | `Screen::DrawLineGlow` | `HyperBot/Screen.cpp:679` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 207 | `Screen::m_dwVS` | `HyperBot/Screen.h:6` | Screen | Ekran cizim yardimcilari: D3D cizim, ekran koordinat donusum |
| 208 | `CStreamData::m_Stride` | `HyperBot/Screen.h:87` | CStreamData | core |
| 209 | `Clock::last_update` | `HyperBot/SimpleClock.h:7` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 210 | `Clock::GetCurTime` | `HyperBot/SimpleClock.h:7` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 211 | `Clock::Begin` | `HyperBot/SimpleClock.h:12` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 212 | `Clock::End` | `HyperBot/SimpleClock.h:17` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 213 | `Clock::Update` | `HyperBot/SimpleClock.h:22` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 214 | `Clock::GetElapsedSinceUpdate` | `HyperBot/SimpleClock.h:27` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 215 | `Clock::GetElapsed` | `HyperBot/SimpleClock.h:32` | Clock | Zaman yardimcilari (tick, gecikme olcumleri). |
| 216 | `Skill::GetSkillDataMap` | `HyperBot/Skill.cpp:6` | Skill | Beceri verisi ve beceri durumu yardimcilari (seviye, cooldow |
| 217 | `SkillData::CanSelfBuff` | `HyperBot/Skill.cpp:109` | SkillData | client bellek/oyun durumu okuma sarmalayicisi |
| 218 | `SkillData::CanTargetBuff` | `HyperBot/Skill.cpp:120` | SkillData | client bellek/oyun durumu okuma sarmalayicisi |
| 219 | `Skill::GetSkillSlot` | `HyperBot/Skill.cpp:172` | Skill | Beceri verisi ve beceri durumu yardimcilari (seviye, cooldow |
| 220 | `Skill::IsSkillUsedByRace` | `HyperBot/Skill.cpp:190` | Skill | Beceri verisi ve beceri durumu yardimcilari (seviye, cooldow |
| 221 | `Skill::IsSkillUsedByJob` | `HyperBot/Skill.cpp:210` | Skill | Beceri verisi ve beceri durumu yardimcilari (seviye, cooldow |
| 222 | `InitOnAlive` | `HyperBot/UpdateGame.cpp:92` | — | client degiskenine yazma / durum kurma sarmalayicisi |
| 223 | `WaitHack` | `HyperBot/WaitHack.cpp:4` | — | core |
| 224 | `WaitHack::Init` | `HyperBot/WaitHack.cpp:8` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 225 | `WaitHack::OnMenuFrame` | `HyperBot/WaitHack.cpp:13` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 226 | `WaitHack::OnIteration` | `HyperBot/WaitHack.cpp:97` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 227 | `WaitHack::PostIteration` | `HyperBot/WaitHack.cpp:111` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 228 | `WaitHack::OnRenderScreen` | `HyperBot/WaitHack.cpp:146` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 229 | `WaitHack::GetTargetList` | `HyperBot/WaitHack.cpp:181` | WaitHack | Coklu hedef saldiri modulu: hedef toplama, sirali hasar pake |
| 230 | `Target::m_target` | `HyperBot/WaitHack.h:18` | Target | core |
| 231 | `Target::m_distance` | `HyperBot/WaitHack.h:20` | Target | core |
| 232 | `BoundingBox::bot` | `HyperBot/bounding_box.h:10` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 233 | `BoundingBox::BoundingBox` | `HyperBot/bounding_box.h:10` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 234 | `BoundingBox::BoundingBox` | `HyperBot/bounding_box.h:18` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 235 | `BoundingBox::Zero` | `HyperBot/bounding_box.h:26` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 236 | `BoundingBox::GetMin` | `HyperBot/bounding_box.h:28` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 237 | `BoundingBox::GetMax` | `HyperBot/bounding_box.h:29` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 238 | `BoundingBox::GetMinBot` | `HyperBot/bounding_box.h:30` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 239 | `BoundingBox::GetMaxTop` | `HyperBot/bounding_box.h:31` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 240 | `BoundingBox::GetSize` | `HyperBot/bounding_box.h:32` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 241 | `BoundingBox::GetCenter` | `HyperBot/bounding_box.h:33` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 242 | `BoundingBox::IsValid` | `HyperBot/bounding_box.h:34` | BoundingBox | 3B sinir kutusu: hitbox/ gorunurluk hesaplarina destek. |
| 243 | `Color::GetU32` | `HyperBot/color.h:11` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 244 | `Color::SetRawColor` | `HyperBot/color.h:45` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 245 | `Color::GetRawColor` | `HyperBot/color.h:50` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 246 | `Color::r` | `HyperBot/color.h:55` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 247 | `Color::g` | `HyperBot/color.h:60` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 248 | `Color::b` | `HyperBot/color.h:65` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 249 | `Color::a` | `HyperBot/color.h:70` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 250 | `Color::r` | `HyperBot/color.h:75` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 251 | `Color::g` | `HyperBot/color.h:80` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 252 | `Color::b` | `HyperBot/color.h:85` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 253 | `Color::a` | `HyperBot/color.h:90` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 254 | `Color::rBase` | `HyperBot/color.h:95` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 255 | `Color::gBase` | `HyperBot/color.h:100` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 256 | `Color::bBase` | `HyperBot/color.h:105` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 257 | `Color::aBase` | `HyperBot/color.h:110` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 258 | `Color::Base` | `HyperBot/color.h:171` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 259 | `Color::BaseAlpha` | `HyperBot/color.h:182` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 260 | `Color::Hue` | `HyperBot/color.h:194` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 261 | `Color::Saturation` | `HyperBot/color.h:231` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 262 | `Color::Brightness` | `HyperBot/color.h:252` | Color | Renk yardimcilari (D3DCOLOR uretimi, aritmetik). |
| 263 | `MainThread` | `HyperBot/dllmain.cpp:1` | — | core |
| 264 | `DllMain` | `HyperBot/dllmain.cpp:21` | — | entry |
| 265 | `easeInSine` | `HyperBot/easing.cpp:9` | — | core |
| 266 | `easeOutSine` | `HyperBot/easing.cpp:13` | — | core |
| 267 | `easeInOutSine` | `HyperBot/easing.cpp:17` | — | core |
| 268 | `easeInQuad` | `HyperBot/easing.cpp:21` | — | core |
| 269 | `easeOutQuad` | `HyperBot/easing.cpp:25` | — | core |
| 270 | `easeInOutQuad` | `HyperBot/easing.cpp:29` | — | core |
| 271 | `easeInCubic` | `HyperBot/easing.cpp:33` | — | core |
| 272 | `easeOutCubic` | `HyperBot/easing.cpp:37` | — | core |
| 273 | `easeInOutCubic` | `HyperBot/easing.cpp:41` | — | core |
| 274 | `easeInQuart` | `HyperBot/easing.cpp:45` | — | core |
| 275 | `easeOutQuart` | `HyperBot/easing.cpp:50` | — | core |
| 276 | `easeInOutQuart` | `HyperBot/easing.cpp:55` | — | core |
| 277 | `easeInQuint` | `HyperBot/easing.cpp:65` | — | core |
| 278 | `easeOutQuint` | `HyperBot/easing.cpp:70` | — | core |
| 279 | `easeInOutQuint` | `HyperBot/easing.cpp:75` | — | core |
| 280 | `easeInExpo` | `HyperBot/easing.cpp:86` | — | core |
| 281 | `easeOutExpo` | `HyperBot/easing.cpp:90` | — | core |
| 282 | `easeInOutExpo` | `HyperBot/easing.cpp:94` | — | core |
| 283 | `easeInCirc` | `HyperBot/easing.cpp:102` | — | core |
| 284 | `easeOutCirc` | `HyperBot/easing.cpp:106` | — | core |
| 285 | `easeInOutCirc` | `HyperBot/easing.cpp:110` | — | core |
| 286 | `easeInBack` | `HyperBot/easing.cpp:118` | — | core |
| 287 | `easeOutBack` | `HyperBot/easing.cpp:122` | — | core |
| 288 | `easeInOutBack` | `HyperBot/easing.cpp:126` | — | core |
| 289 | `easeInElastic` | `HyperBot/easing.cpp:134` | — | core |
| 290 | `easeOutElastic` | `HyperBot/easing.cpp:139` | — | core |
| 291 | `easeInOutElastic` | `HyperBot/easing.cpp:144` | — | core |
| 292 | `easeInBounce` | `HyperBot/easing.cpp:157` | — | core |
| 293 | `easeOutBounce` | `HyperBot/easing.cpp:161` | — | core |
| 294 | `easeInOutBounce` | `HyperBot/easing.cpp:165` | — | core |
| 295 | `GetEasingFunction` | `HyperBot/easing.cpp:173` | — | client bellek/oyun durumu okuma sarmalayicisi |
| 296 | `Matrix::_impl` | `HyperBot/matrix.h:104` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 297 | `Matrix::_impl` | `HyperBot/matrix.h:110` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 298 | `Matrix::_impl` | `HyperBot/matrix.h:112` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 299 | `Matrix::_impl` | `HyperBot/matrix.h:114` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 300 | `Matrix::_impl` | `HyperBot/matrix.h:116` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 301 | `Matrix::_impl` | `HyperBot/matrix.h:119` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 302 | `Matrix::Matrix` | `HyperBot/matrix.h:119` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 303 | `Matrix::Set` | `HyperBot/matrix.h:120` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 304 | `Matrix::Set` | `HyperBot/matrix.h:124` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 305 | `Matrix::Set` | `HyperBot/matrix.h:128` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 306 | `Matrix::AxisX` | `HyperBot/matrix.h:130` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 307 | `Matrix::AxisY` | `HyperBot/matrix.h:132` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 308 | `Matrix::AxisZ` | `HyperBot/matrix.h:133` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 309 | `Matrix::Pos` | `HyperBot/matrix.h:134` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 310 | `Matrix::Buff` | `HyperBot/matrix.h:135` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 311 | `Matrix::Buff` | `HyperBot/matrix.h:137` | Matrix | 4x4 matris yardimcilari (donusum hesaplari). |
| 312 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:17` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 313 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:27` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 314 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:28` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 315 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:29` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 316 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:31` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 317 | `MatrixCppImpl4x4::MatrixCppImpl4x4` | `HyperBot/matrix_impl.h:32` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 318 | `MatrixCppImpl4x4::Set` | `HyperBot/matrix_impl.h:33` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 319 | `MatrixCppImpl4x4::Set` | `HyperBot/matrix_impl.h:39` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 320 | `MatrixCppImpl4x4::Set` | `HyperBot/matrix_impl.h:55` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 321 | `MatrixCppImpl4x4::AxisX` | `HyperBot/matrix_impl.h:97` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 322 | `MatrixCppImpl4x4::AxisY` | `HyperBot/matrix_impl.h:99` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 323 | `MatrixCppImpl4x4::AxisZ` | `HyperBot/matrix_impl.h:100` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 324 | `MatrixCppImpl4x4::Pos` | `HyperBot/matrix_impl.h:101` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 325 | `MatrixCppImpl4x4::Buff` | `HyperBot/matrix_impl.h:102` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 326 | `MatrixCppImpl4x4::Buff` | `HyperBot/matrix_impl.h:104` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 327 | `MatrixCppImpl4x4::FlipZ` | `HyperBot/matrix_impl.h:203` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 328 | `MatrixCppImpl4x4::Inverse` | `HyperBot/matrix_impl.h:218` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 329 | `MatrixCppImpl4x4::Transpose` | `HyperBot/matrix_impl.h:252` | MatrixCppImpl4x4 | Client matris sinifinin C++ uygulamasi (World/View/Proj carp |
| 330 | `w` | `HyperBot/quaternion.cpp:17` | — | core |
| 331 | `w` | `HyperBot/quaternion.cpp:22` | — | core |
| 332 | `w` | `HyperBot/quaternion.cpp:27` | — | core |
| 333 | `Quaternion::Quaternion` | `HyperBot/quaternion.cpp:29` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 334 | `Quaternion::Set` | `HyperBot/quaternion.cpp:50` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 335 | `Quaternion::FromMatrix` | `HyperBot/quaternion.cpp:58` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 336 | `Quaternion::FromAxisAndAngle` | `HyperBot/quaternion.cpp:98` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 337 | `Quaternion::FromEuler` | `HyperBot/quaternion.cpp:106` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 338 | `Quaternion::GetEuler` | `HyperBot/quaternion.cpp:127` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 339 | `Quaternion::Slerp` | `HyperBot/quaternion.cpp:214` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 340 | `Quaternion::Lerp` | `HyperBot/quaternion.cpp:271` | Quaternion | Kuaternyon donusum yardimcilari (kamera/model oryantasyonu). |
| 341 | `Max` | `HyperBot/util.h:10` | — | core |
| 342 | `Min` | `HyperBot/util.h:16` | — | core |
| 343 | `Degree` | `HyperBot/util.h:22` | — | core |
| 344 | `w` | `HyperBot/vector.cpp:16` | — | core |
| 345 | `w` | `HyperBot/vector.cpp:21` | — | core |
| 346 | `w` | `HyperBot/vector.cpp:26` | — | core |
| 347 | `Vec4::Set` | `HyperBot/vector.cpp:28` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 348 | `Vec4::Length3` | `HyperBot/vector.cpp:127` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 349 | `Vec4::Length3Sqr` | `HyperBot/vector.cpp:132` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 350 | `Vec4::Length4` | `HyperBot/vector.cpp:137` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 351 | `Vec4::Length4Sqr` | `HyperBot/vector.cpp:142` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 352 | `Vec4::Normalize3` | `HyperBot/vector.cpp:147` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 353 | `Vec4::Normalize3Safe` | `HyperBot/vector.cpp:156` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 354 | `Vec4::Normalize4` | `HyperBot/vector.cpp:172` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 355 | `Vec4::Cross` | `HyperBot/vector.cpp:179` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 356 | `Vec4::Dot3` | `HyperBot/vector.cpp:189` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 357 | `Vec4::Dot4` | `HyperBot/vector.cpp:194` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 358 | `Vec4::Lerp` | `HyperBot/vector.cpp:199` | Vec4 | 4B vektor yardimcilari (renk/kuaternyon destekleri). |
| 359 | `z` | `HyperBot/vector.cpp:235` | — | core |
| 360 | `z` | `HyperBot/vector.cpp:240` | — | core |
| 361 | `z` | `HyperBot/vector.cpp:245` | — | core |
| 362 | `Vec3::Set` | `HyperBot/vector.cpp:247` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 363 | `Vec3::Get` | `HyperBot/vector.cpp:254` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 364 | `Vec3::Length` | `HyperBot/vector.cpp:356` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 365 | `Vec3::LengthSqr` | `HyperBot/vector.cpp:361` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 366 | `Vec3::Distance` | `HyperBot/vector.cpp:366` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 367 | `Vec3::Normalize` | `HyperBot/vector.cpp:371` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 368 | `Vec3::Normalized` | `HyperBot/vector.cpp:387` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 369 | `Vec3::Cross` | `HyperBot/vector.cpp:403` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 370 | `Vec3::Dot` | `HyperBot/vector.cpp:412` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 371 | `Vec3::Lerp` | `HyperBot/vector.cpp:417` | Vec3 | 3B vektor yardimcilari (piksel/dunya koordinat islemleri). |
| 372 | `y` | `HyperBot/vector.cpp:427` | — | core |
| 373 | `y` | `HyperBot/vector.cpp:432` | — | core |
| 374 | `y` | `HyperBot/vector.cpp:437` | — | core |
| 375 | `Vec2::Set` | `HyperBot/vector.cpp:439` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 376 | `Vec2::Length` | `HyperBot/vector.cpp:516` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 377 | `Vec2::LengthSqr` | `HyperBot/vector.cpp:521` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 378 | `Vec2::NormalizeSafe` | `HyperBot/vector.cpp:526` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 379 | `Vec2::Normalize` | `HyperBot/vector.cpp:540` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 380 | `Vec2::Dot` | `HyperBot/vector.cpp:547` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 381 | `Vec2::Lerp` | `HyperBot/vector.cpp:552` | Vec2 | 2B vektor yardimcilari (uzaklik, yon, aritmetik). |
| 382 | `main` | `Injector/Injector.cpp:6` | — | injector |

### C4US — 386 fonksiyon

| # | Fonksiyon | Dosya:Satır | Sınıf | Ne yapar (kısa) |
|---|---|---|---|---|
| 1 | `AVehHook::AVehHook` | `EngineX-Pro/AVehHook.cpp:7` | AVehHook | ic yardimci |
| 2 | `AVehHook` | `EngineX-Pro/AVehHook.cpp:19` | — | ic yardimci |
| 3 | `AVehHook::EventException` | `EngineX-Pro/AVehHook.cpp:33` | AVehHook | ic yardimci |
| 4 | `AVehHook::EventUnhandledException` | `EngineX-Pro/AVehHook.cpp:37` | AVehHook | ic yardimci |
| 5 | `AVehHook::Handler` | `EngineX-Pro/AVehHook.cpp:41` | AVehHook | ic yardimci |
| 6 | `AutoTalk::OnStart` | `EngineX-Pro/AutoTalk.h:3` | AutoTalk | ic yardimci |
| 7 | `AutoTalk::OnUpdate` | `EngineX-Pro/AutoTalk.h:13` | AutoTalk | ic yardimci |
| 8 | `AutoTalk::OnRender` | `EngineX-Pro/AutoTalk.h:18` | AutoTalk | ic yardimci |
| 9 | `AutoTalk::OnTab1` | `EngineX-Pro/AutoTalk.h:22` | AutoTalk | ic yardimci |
| 10 | `AutoTalk::OnTabs` | `EngineX-Pro/AutoTalk.h:27` | AutoTalk | ic yardimci |
| 11 | `AutoTalk::OnMenu` | `EngineX-Pro/AutoTalk.h:32` | AutoTalk | ic yardimci |
| 12 | `TargetBuff::TargetBuff` | `EngineX-Pro/Buff.h:7` | TargetBuff | ic yardimci |
| 13 | `Buff::SetJobRaceTextures` | `EngineX-Pro/Buff.h:32` | Buff | client degiskenine yazma / durum kurma sarmalayicisi |
| 14 | `Buff::OnStart` | `EngineX-Pro/Buff.h:118` | Buff | ic yardimci |
| 15 | `Buff::OnRender` | `EngineX-Pro/Buff.h:289` | Buff | ic yardimci |
| 16 | `Buff::OnTabs` | `EngineX-Pro/Buff.h:404` | Buff | ic yardimci |
| 17 | `Buff::OnMenu` | `EngineX-Pro/Buff.h:409` | Buff | ic yardimci |
| 18 | `CRender::CRender` | `EngineX-Pro/CRender.cpp:20` | CRender | ic yardimci |
| 19 | `CRender` | `EngineX-Pro/CRender.cpp:22` | — | ic yardimci |
| 20 | `Clamp` | `EngineX-Pro/CRender.cpp:277` | — | ic yardimci |
| 21 | `CRender::Circle3D` | `EngineX-Pro/CRender.cpp:325` | CRender | ic yardimci |
| 22 | `CRender::FrameRate` | `EngineX-Pro/CRender.cpp:440` | CRender | ic yardimci |
| 23 | `FollowTheWhiteRabbit` | `EngineX-Pro/CheckHook.cpp:5` | — | ic yardimci |
| 24 | `FindHookDestination` | `EngineX-Pro/CheckHook.cpp:40` | — | ic yardimci |
| 25 | `Configuration::OnStart` | `EngineX-Pro/Configuration.h:16` | Configuration | ic yardimci |
| 26 | `Configuration::OnUpdate` | `EngineX-Pro/Configuration.h:33` | Configuration | ic yardimci |
| 27 | `Configuration::OnRender` | `EngineX-Pro/Configuration.h:38` | Configuration | ic yardimci |
| 28 | `Configuration::OnTab1` | `EngineX-Pro/Configuration.h:42` | Configuration | ic yardimci |
| 29 | `Configuration::OnTab2` | `EngineX-Pro/Configuration.h:119` | Configuration | ic yardimci |
| 30 | `Configuration::OnTabs` | `EngineX-Pro/Configuration.h:137` | Configuration | ic yardimci |
| 31 | `Configuration::OnMenu` | `EngineX-Pro/Configuration.h:143` | Configuration | ic yardimci |
| 32 | `CryptExtension::Xor32Encrypt` | `EngineX-Pro/CryptExtension.h:3` | CryptExtension | ic yardimci |
| 33 | `CryptExtension::Xor32Decrypt` | `EngineX-Pro/CryptExtension.h:46` | CryptExtension | ic yardimci |
| 34 | `ImGui::DrawImagePos` | `EngineX-Pro/CustomWidgets.cpp:376` | ImGui | ic yardimci |
| 35 | `ImGui::DrawImage` | `EngineX-Pro/CustomWidgets.cpp:385` | ImGui | ic yardimci |
| 36 | `ImGui::CenterHorizontal` | `EngineX-Pro/CustomWidgets.cpp:465` | ImGui | ic yardimci |
| 37 | `ImGui::CenterVertical` | `EngineX-Pro/CustomWidgets.cpp:472` | ImGui | ic yardimci |
| 38 | `ImGui::ImageAuto` | `EngineX-Pro/CustomWidgets.cpp:479` | ImGui | ic yardimci |
| 39 | `ImGui::ImageSwitcher` | `EngineX-Pro/CustomWidgets.cpp:495` | ImGui | ic yardimci |
| 40 | `ImGui::PopupButton` | `EngineX-Pro/CustomWidgets.cpp:522` | ImGui | ic yardimci |
| 41 | `ImGui::Logo` | `EngineX-Pro/CustomWidgets.cpp:568` | ImGui | ic yardimci |
| 42 | `ImGui::IconMenuButton` | `EngineX-Pro/CustomWidgets.cpp:606` | ImGui | ic yardimci |
| 43 | `ImGui::IconButton` | `EngineX-Pro/CustomWidgets.cpp:667` | ImGui | ic yardimci |
| 44 | `ImGui::IconButton2` | `EngineX-Pro/CustomWidgets.cpp:722` | ImGui | ic yardimci |
| 45 | `ImGui::InputFloatMinMax` | `EngineX-Pro/CustomWidgets.cpp:780` | ImGui | ic yardimci |
| 46 | `ImGui::Hotkey` | `EngineX-Pro/CustomWidgets.cpp:883` | ImGui | ic yardimci |
| 47 | `Debug::OnStart` | `EngineX-Pro/Debug.h:11` | Debug | ic yardimci |
| 48 | `Debug::OnUpdate` | `EngineX-Pro/Debug.h:20` | Debug | ic yardimci |
| 49 | `Debug::OnRender` | `EngineX-Pro/Debug.h:27` | Debug | ic yardimci |
| 50 | `Debug::Rozdzielacz` | `EngineX-Pro/Debug.h:31` | Debug | ic yardimci |
| 51 | `Debug::BuildShop` | `EngineX-Pro/Debug.h:48` | Debug | ic yardimci |
| 52 | `Debug::LoadTextureFromFile` | `EngineX-Pro/Debug.h:102` | Debug | ic yardimci |
| 53 | `Debug::OnTabs` | `EngineX-Pro/Debug.h:217` | Debug | ic yardimci |
| 54 | `Debug::OnMenu` | `EngineX-Pro/Debug.h:222` | Debug | ic yardimci |
| 55 | `Debug::DebugMsgBoxNoBlocking` | `EngineX-Pro/Debug.h:232` | Debug | ic yardimci |
| 56 | `GetStr` | `EngineX-Pro/Defines.h:56` | — | client bellek/oyun durumu okuma sarmalayicisi |
| 57 | `SItemPos::SItemPos` | `EngineX-Pro/Defines.h:560` | SItemPos | ic yardimci |
| 58 | `SItemPos::SItemPos` | `EngineX-Pro/Defines.h:566` | SItemPos | ic yardimci |
| 59 | `IAction::IAction` | `EngineX-Pro/DelayActions.h:10` | IAction | ic yardimci |
| 60 | `Action::Action` | `EngineX-Pro/DelayActions.h:52` | Action | ic yardimci |
| 61 | `Action::IsWaitAfter` | `EngineX-Pro/DelayActions.h:62` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 62 | `Action::IsWaitBlock` | `EngineX-Pro/DelayActions.h:67` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 63 | `Action::IsReady` | `EngineX-Pro/DelayActions.h:72` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 64 | `Action::IsEnded` | `EngineX-Pro/DelayActions.h:90` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 65 | `Action::GetFunctionPtr` | `EngineX-Pro/DelayActions.h:113` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 66 | `Action::IsUniqueEquals` | `EngineX-Pro/DelayActions.h:118` | Action | client bellek/oyun durumu okuma sarmalayicisi |
| 67 | `Action::Call` | `EngineX-Pro/DelayActions.h:134` | Action | ic yardimci |
| 68 | `DelayActions::MakeSharedPtr` | `EngineX-Pro/DelayActions.h:149` | DelayActions | ic yardimci |
| 69 | `DelayActions::Append` | `EngineX-Pro/DelayActions.h:155` | DelayActions | ic yardimci |
| 70 | `DynamicTimer::SetTick` | `EngineX-Pro/DynamicTimer.h:48` | DynamicTimer | client degiskenine yazma / durum kurma sarmalayicisi |
| 71 | `DynamicTimer::IsActive` | `EngineX-Pro/DynamicTimer.h:58` | DynamicTimer | client bellek/oyun durumu okuma sarmalayicisi |
| 72 | `Log::registerLogger` | `EngineX-Pro/ErrorLog.cpp:3` | Log | ic yardimci |
| 73 | `Log::log` | `EngineX-Pro/ErrorLog.cpp:7` | Log | ic yardimci |
| 74 | `ErrorLog::setLogLevel` | `EngineX-Pro/ErrorLog.cpp:11` | ErrorLog | ic yardimci |
| 75 | `ErrorLog::log` | `EngineX-Pro/ErrorLog.cpp:15` | ErrorLog | ic yardimci |
| 76 | `ErrorLog::push` | `EngineX-Pro/ErrorLog.cpp:20` | ErrorLog | ic yardimci |
| 77 | `ErrorLog::push` | `EngineX-Pro/ErrorLog.cpp:25` | ErrorLog | ic yardimci |
| 78 | `ErrorLog::pop` | `EngineX-Pro/ErrorLog.cpp:45` | ErrorLog | ic yardimci |
| 79 | `ErrorLog::singleton` | `EngineX-Pro/ErrorLog.cpp:54` | ErrorLog | ic yardimci |
| 80 | `Farm::TeleportToDestination` | `EngineX-Pro/Farm.h:12` | Farm | ic yardimci |
| 81 | `Farm::OnTabs` | `EngineX-Pro/Farm.h:297` | Farm | ic yardimci |
| 82 | `Farm::OnMenu` | `EngineX-Pro/Farm.h:302` | Farm | ic yardimci |
| 83 | `FileExtension::GetDirectoryPathFromFilePatch` | `EngineX-Pro/FileExtension.h:22` | FileExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 84 | `FileExtension::ReadFileSize` | `EngineX-Pro/FileExtension.h:40` | FileExtension | ic yardimci |
| 85 | `FileExtension::ReadAllBytes` | `EngineX-Pro/FileExtension.h:46` | FileExtension | ic yardimci |
| 86 | `FileExtension::ReadAllBytes` | `EngineX-Pro/FileExtension.h:59` | FileExtension | ic yardimci |
| 87 | `FileExtension::ReadDirectory` | `EngineX-Pro/FileExtension.h:116` | FileExtension | ic yardimci |
| 88 | `FileExtension::GetExtensionFilePath` | `EngineX-Pro/FileExtension.h:131` | FileExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 89 | `FileExtension::GetDirectoryFiles` | `EngineX-Pro/FileExtension.h:146` | FileExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 90 | `Fish::OnUpdate` | `EngineX-Pro/Fish.h:43` | Fish | ic yardimci |
| 91 | `Fish::OnRender` | `EngineX-Pro/Fish.h:154` | Fish | ic yardimci |
| 92 | `Fish::OnTab1` | `EngineX-Pro/Fish.h:158` | Fish | ic yardimci |
| 93 | `Fish::OnTabs` | `EngineX-Pro/Fish.h:276` | Fish | ic yardimci |
| 94 | `Fish::OnMenu` | `EngineX-Pro/Fish.h:287` | Fish | ic yardimci |
| 95 | `Fish::AppendCastDirect` | `EngineX-Pro/Fish.h:311` | Fish | ic yardimci |
| 96 | `Fish::AppendCastDirectString` | `EngineX-Pro/Fish.h:324` | Fish | ic yardimci |
| 97 | `GameFunctions::ItemSelectItem` | `EngineX-Pro/GameFunctions.h:73` | GameFunctions | ic yardimci |
| 98 | `GameFunctions::PythonPlayerNEW_Fishing` | `EngineX-Pro/GameFunctions.h:452` | GameFunctions | ic yardimci |
| 99 | `GameFunctions::NetworkStreamSendCommandPacket` | `EngineX-Pro/GameFunctions.h:968` | GameFunctions | ic yardimci |
| 100 | `GameFunctions::NetworkStreamConnect` | `EngineX-Pro/GameFunctions.h:988` | GameFunctions | ic yardimci |
| 101 | `GameFunctions::NetworkStreamSendFishingQuitPacket` | `EngineX-Pro/GameFunctions.h:1062` | GameFunctions | ic yardimci |
| 102 | `GameFunctions::SelectInstancePython` | `EngineX-Pro/GameFunctions.h:1353` | GameFunctions | ic yardimci |
| 103 | `GameFunctions::InstanceIsWaiting` | `EngineX-Pro/GameFunctions.h:1654` | GameFunctions | ic yardimci |
| 104 | `GameFunctions::NonPlayerGetTable` | `EngineX-Pro/GameFunctions.h:1682` | GameFunctions | ic yardimci |
| 105 | `GameFunctions::PyCallClassMemberFunc` | `EngineX-Pro/GameFunctions.h:1735` | GameFunctions | ic yardimci |
| 106 | `GameFunctions::ResourceManagerGetResourcePointer` | `EngineX-Pro/GameFunctions.h:1782` | GameFunctions | ic yardimci |
| 107 | `GameFunctions::ResourceReload` | `EngineX-Pro/GameFunctions.h:1794` | GameFunctions | ic yardimci |
| 108 | `GameFunctions::GraphicImageGetTexturePointer` | `EngineX-Pro/GameFunctions.h:1805` | GameFunctions | ic yardimci |
| 109 | `GameFunctions::GraphicTextureGetD3DTexture` | `EngineX-Pro/GameFunctions.h:1817` | GameFunctions | ic yardimci |
| 110 | `GameFunctionsCustom::GetCharSlotByName` | `EngineX-Pro/GameFunctionsCustom.h:104` | GameFunctionsCustom | client bellek/oyun durumu okuma sarmalayicisi |
| 111 | `GameFunctionsCustom::PlayerIsPickAxeEquipped` | `EngineX-Pro/GameFunctionsCustom.h:243` | GameFunctionsCustom | ic yardimci |
| 112 | `GameFunctionsCustom::PlayerIsBowEquipped` | `EngineX-Pro/GameFunctionsCustom.h:248` | GameFunctionsCustom | ic yardimci |
| 113 | `GameFunctionsCustom::PlayerIsWeaponEquipped` | `EngineX-Pro/GameFunctionsCustom.h:253` | GameFunctionsCustom | ic yardimci |
| 114 | `GameFunctionsCustom::GetObjectRank` | `EngineX-Pro/GameFunctionsCustom.h:1088` | GameFunctionsCustom | client bellek/oyun durumu okuma sarmalayicisi |
| 115 | `GameFunctionsCustom::UseSkillSlot` | `EngineX-Pro/GameFunctionsCustom.h:1243` | GameFunctionsCustom | ic yardimci |
| 116 | `GameFunctionsCustom::PlayerDirectEnter` | `EngineX-Pro/GameFunctionsCustom.h:1261` | GameFunctionsCustom | ic yardimci |
| 117 | `GameFunctionsCustom::GetDirectionFromDegree` | `EngineX-Pro/GameFunctionsCustom.h:1302` | GameFunctionsCustom | client bellek/oyun durumu okuma sarmalayicisi |
| 118 | `Globals::ReAddressingLocas` | `EngineX-Pro/Globals.h:1173` | Globals | ic yardimci |
| 119 | `Globals::ReAddressingPython` | `EngineX-Pro/Globals.h:3412` | Globals | ic yardimci |
| 120 | `Globals::ReDeclarationInstances` | `EngineX-Pro/Globals.h:3470` | Globals | ic yardimci |
| 121 | `Globals::ReDeclarationLocals` | `EngineX-Pro/Globals.h:3541` | Globals | ic yardimci |
| 122 | `HWBreakPointHook::hook` | `EngineX-Pro/HWBreakPointHook.cpp:23` | HWBreakPointHook | ic yardimci |
| 123 | `HWBreakPointHook::unHook` | `EngineX-Pro/HWBreakPointHook.cpp:76` | HWBreakPointHook | ic yardimci |
| 124 | `HWBreakPointHook::OnException` | `EngineX-Pro/HWBreakPointHook.cpp:102` | HWBreakPointHook | ic yardimci |
| 125 | `Hooks::NewCActorInstanceTestActorCollision` | `EngineX-Pro/HookCore.cpp:22` | Hooks | ic yardimci |
| 126 | `Hooks::NewCInstanceBaseAvoidObject` | `EngineX-Pro/HookCore.cpp:36` | Hooks | ic yardimci |
| 127 | `Hooks::NewCInstanceBaseBlockMovement` | `EngineX-Pro/HookCore.cpp:50` | Hooks | ic yardimci |
| 128 | `Hooks::NewCPhysicsObjectIncreaseExternalForce` | `EngineX-Pro/HookCore.cpp:64` | Hooks | ic yardimci |
| 129 | `Hooks::NewPyCallClassMemberFunc` | `EngineX-Pro/HookCore.cpp:79` | Hooks | ic yardimci |
| 130 | `Hooks::NewCNetworkStreamSend` | `EngineX-Pro/HookCore.cpp:438` | Hooks | ic yardimci |
| 131 | `Hooks::NewCNetworkStreamSendAeldra` | `EngineX-Pro/HookCore.cpp:544` | Hooks | ic yardimci |
| 132 | `Hooks::NewCPythonChatAppendChat` | `EngineX-Pro/HookCore.cpp:568` | Hooks | ic yardimci |
| 133 | `Hooks::NewCInputKeyboardUpdateKeyboard` | `EngineX-Pro/HookCore.cpp:603` | Hooks | ic yardimci |
| 134 | `Hooks::NewCResourceManagerGetResourcePointer` | `EngineX-Pro/HookCore.cpp:616` | Hooks | ic yardimci |
| 135 | `Hooks::NewScreenToClient` | `EngineX-Pro/HookCore.cpp:625` | Hooks | ic yardimci |
| 136 | `Hooks::NewDirectEndScene` | `EngineX-Pro/HookCore.cpp:642` | Hooks | ic yardimci |
| 137 | `Hooks::NewDirectReset` | `EngineX-Pro/HookCore.cpp:659` | Hooks | ic yardimci |
| 138 | `Hooks::Initialize` | `EngineX-Pro/HookCore.cpp:675` | Hooks | client degiskenine yazma / durum kurma sarmalayicisi |
| 139 | `IAbstractModuleBase::IAbstractModuleBase` | `EngineX-Pro/IAbstractModuleBase.h:4` | IAbstractModuleBase | ic yardimci |
| 140 | `IAbstractModuleBase::IAbstractModuleBase` | `EngineX-Pro/IAbstractModuleBase.h:6` | IAbstractModuleBase | ic yardimci |
| 141 | `IatHook` | `EngineX-Pro/IatHook.cpp:3` | — | ic yardimci |
| 142 | `m_origFunc` | `EngineX-Pro/IatHook.cpp:12` | — | ic yardimci |
| 143 | `IatHook::hook` | `EngineX-Pro/IatHook.cpp:14` | IatHook | ic yardimci |
| 144 | `IatHook::unHook` | `EngineX-Pro/IatHook.cpp:29` | IatHook | ic yardimci |
| 145 | `IatHook::FindIatThunk` | `EngineX-Pro/IatHook.cpp:46` | IatHook | ic yardimci |
| 146 | `IatHook::FindIatThunkInModule` | `EngineX-Pro/IatHook.cpp:79` | IatHook | ic yardimci |
| 147 | `Inventory::OnStart` | `EngineX-Pro/Inventory.h:3` | Inventory | ic yardimci |
| 148 | `Inventory::GetBonusTypeFromMap` | `EngineX-Pro/Inventory.h:113` | Inventory | client bellek/oyun durumu okuma sarmalayicisi |
| 149 | `Inventory::OnRender` | `EngineX-Pro/Inventory.h:215` | Inventory | ic yardimci |
| 150 | `Inventory::OnTabs` | `EngineX-Pro/Inventory.h:516` | Inventory | ic yardimci |
| 151 | `Inventory::OnMenu` | `EngineX-Pro/Inventory.h:521` | Inventory | ic yardimci |
| 152 | `Item::OnRender` | `EngineX-Pro/Item.h:28` | Item | ic yardimci |
| 153 | `Item::OnTab2` | `EngineX-Pro/Item.h:170` | Item | ic yardimci |
| 154 | `Item::OnTabs` | `EngineX-Pro/Item.h:244` | Item | ic yardimci |
| 155 | `Item::OnMenu` | `EngineX-Pro/Item.h:250` | Item | ic yardimci |
| 156 | `LogWindow::LogWindow` | `EngineX-Pro/Logger.h:40` | LogWindow | ic yardimci |
| 157 | `LogWindow::Clear` | `EngineX-Pro/Logger.h:79` | LogWindow | ic yardimci |
| 158 | `Logger::AddString` | `EngineX-Pro/Logger.h:214` | Logger | ic yardimci |
| 159 | `Main::SetJobRaceTextures` | `EngineX-Pro/Main.h:32` | Main | client degiskenine yazma / durum kurma sarmalayicisi |
| 160 | `Main::OnTab3` | `EngineX-Pro/Main.h:339` | Main | ic yardimci |
| 161 | `Main::OnTab4` | `EngineX-Pro/Main.h:355` | Main | ic yardimci |
| 162 | `Main::OnTabs` | `EngineX-Pro/Main.h:375` | Main | ic yardimci |
| 163 | `Main::OnMenu` | `EngineX-Pro/Main.h:383` | Main | ic yardimci |
| 164 | `Main::IsAttackMobDistance` | `EngineX-Pro/Main.h:440` | Main | client bellek/oyun durumu okuma sarmalayicisi |
| 165 | `Main::Skill` | `EngineX-Pro/Main.h:467` | Main | ic yardimci |
| 166 | `Main::WHCanAttack` | `EngineX-Pro/Main.h:562` | Main | ic yardimci |
| 167 | `Main::ResetSkillTimer` | `EngineX-Pro/Main.h:651` | Main | client degiskenine yazma / durum kurma sarmalayicisi |
| 168 | `Main::Potions` | `EngineX-Pro/Main.h:1061` | Main | ic yardimci |
| 169 | `MainCore::StartCrack` | `EngineX-Pro/MainCore.cpp:5` | MainCore | ic yardimci |
| 170 | `MainCore::Crack` | `EngineX-Pro/MainCore.cpp:32` | MainCore | ic yardimci |
| 171 | `MainCore::CheckMembers` | `EngineX-Pro/MainCore.cpp:59` | MainCore | ic yardimci |
| 172 | `MainCore::ConsoleOutput` | `EngineX-Pro/MainCore.cpp:113` | MainCore | ic yardimci |
| 173 | `MainCore::Initialize` | `EngineX-Pro/MainCore.cpp:141` | MainCore | client degiskenine yazma / durum kurma sarmalayicisi |
| 174 | `MainDungs::OnStart` | `EngineX-Pro/MainDungs.h:124` | MainDungs | ic yardimci |
| 175 | `MainDungs::Exit175` | `EngineX-Pro/MainDungs.h:161` | MainDungs | ic yardimci |
| 176 | `MainDungs::Restart` | `EngineX-Pro/MainDungs.h:166` | MainDungs | ic yardimci |
| 177 | `MainDungs::OnUpdate` | `EngineX-Pro/MainDungs.h:510` | MainDungs | ic yardimci |
| 178 | `MainDungs::OnRender` | `EngineX-Pro/MainDungs.h:530` | MainDungs | ic yardimci |
| 179 | `MainDungs::OnTabs` | `EngineX-Pro/MainDungs.h:558` | MainDungs | ic yardimci |
| 180 | `MainDungs::OnMenu` | `EngineX-Pro/MainDungs.h:563` | MainDungs | ic yardimci |
| 181 | `ImageLoad` | `EngineX-Pro/MainForm.cpp:49` | — | ic yardimci |
| 182 | `MainForm::Hotkey` | `EngineX-Pro/MainForm.cpp:249` | MainForm | ic yardimci |
| 183 | `GetKeyPressedTwice` | `EngineX-Pro/MainForm.cpp:258` | — | client bellek/oyun durumu okuma sarmalayicisi |
| 184 | `rotateVector` | `EngineX-Pro/MainForm.cpp:283` | — | ic yardimci |
| 185 | `rotateVectorX` | `EngineX-Pro/MainForm.cpp:296` | — | ic yardimci |
| 186 | `rotateVectorY` | `EngineX-Pro/MainForm.cpp:305` | — | ic yardimci |
| 187 | `PositionToRadarPosition` | `EngineX-Pro/MainForm.cpp:462` | — | ic yardimci |
| 188 | `SizeToZoom` | `EngineX-Pro/MainForm.cpp:473` | — | ic yardimci |
| 189 | `WndProc` | `EngineX-Pro/MainForm.cpp:1128` | — | ic yardimci |
| 190 | `MathExtension::PointInCircle` | `EngineX-Pro/MathExtension.h:4` | MathExtension | ic yardimci |
| 191 | `MemAccessor::mem_copy` | `EngineX-Pro/MemAccessor.cpp:5` | MemAccessor | ic yardimci |
| 192 | `MemAccessor::safe_mem_write` | `EngineX-Pro/MemAccessor.cpp:10` | MemAccessor | ic yardimci |
| 193 | `MemAccessor::safe_mem_read` | `EngineX-Pro/MemAccessor.cpp:15` | MemAccessor | ic yardimci |
| 194 | `MemAccessor::mem_protect` | `EngineX-Pro/MemAccessor.cpp:20` | MemAccessor | ic yardimci |
| 195 | `PLH::TranslateProtection` | `EngineX-Pro/MemProtector.cpp:48` | PLH | ic yardimci |
| 196 | `PLH::TranslateProtection` | `EngineX-Pro/MemProtector.cpp:73` | PLH | ic yardimci |
| 197 | `MemoryExtension::ReadMemory` | `EngineX-Pro/MemoryExtension.h:3` | MemoryExtension | ic yardimci |
| 198 | `MemoryExtension::WriteMemory` | `EngineX-Pro/MemoryExtension.h:31` | MemoryExtension | ic yardimci |
| 199 | `MemoryExtension::MemSet` | `EngineX-Pro/MemoryExtension.h:58` | MemoryExtension | ic yardimci |
| 200 | `MemoryExtension::SetMemory` | `EngineX-Pro/MemoryExtension.h:68` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 201 | `MemoryExtension::JmpHook` | `EngineX-Pro/MemoryExtension.h:80` | MemoryExtension | ic yardimci |
| 202 | `MemoryExtension::SetByte` | `EngineX-Pro/MemoryExtension.h:88` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 203 | `MemoryExtension::GetByte` | `EngineX-Pro/MemoryExtension.h:94` | MemoryExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 204 | `MemoryExtension::SetWord` | `EngineX-Pro/MemoryExtension.h:100` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 205 | `MemoryExtension::SetDword` | `EngineX-Pro/MemoryExtension.h:112` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 206 | `MemoryExtension::GetDword` | `EngineX-Pro/MemoryExtension.h:118` | MemoryExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 207 | `MemoryExtension::SetFloat` | `EngineX-Pro/MemoryExtension.h:124` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 208 | `MemoryExtension::GetFloat` | `EngineX-Pro/MemoryExtension.h:130` | MemoryExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 209 | `MemoryExtension::SetDouble` | `EngineX-Pro/MemoryExtension.h:136` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 210 | `MemoryExtension::SetJmp` | `EngineX-Pro/MemoryExtension.h:142` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 211 | `MemoryExtension::SetJg` | `EngineX-Pro/MemoryExtension.h:154` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 212 | `MemoryExtension::SetJa` | `EngineX-Pro/MemoryExtension.h:167` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 213 | `MemoryExtension::SetOp` | `EngineX-Pro/MemoryExtension.h:180` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 214 | `MemoryExtension::SetHook` | `EngineX-Pro/MemoryExtension.h:202` | MemoryExtension | client degiskenine yazma / durum kurma sarmalayicisi |
| 215 | `MemoryExtension::HookThis` | `EngineX-Pro/MemoryExtension.h:216` | MemoryExtension | ic yardimci |
| 216 | `MemoryExtension::ErasePEHeader` | `EngineX-Pro/MemoryExtension.h:222` | MemoryExtension | ic yardimci |
| 217 | `PLH::findPattern` | `EngineX-Pro/Misc.cpp:1` | PLH | ic yardimci |
| 218 | `PLH::findPattern_rev` | `EngineX-Pro/Misc.cpp:38` | PLH | ic yardimci |
| 219 | `MiscExtension::OpenWebiste` | `EngineX-Pro/MiscExtension.h:47` | MiscExtension | ic yardimci |
| 220 | `MiscExtension::PlayAlerSound` | `EngineX-Pro/MiscExtension.h:60` | MiscExtension | ic yardimci |
| 221 | `MiscExtension::UpdateBalloon` | `EngineX-Pro/MiscExtension.h:65` | MiscExtension | ic yardimci |
| 222 | `MiscExtension::FindTopWindow` | `EngineX-Pro/MiscExtension.h:94` | MiscExtension | ic yardimci |
| 223 | `MiscExtension::RandomFloat` | `EngineX-Pro/MiscExtension.h:149` | MiscExtension | ic yardimci |
| 224 | `EnumWindowsCallbackArgs::pid` | `EngineX-Pro/MiscExtension.h:163` | EnumWindowsCallbackArgs | ic yardimci |
| 225 | `MiscExtension::EnumWindowsCallback` | `EngineX-Pro/MiscExtension.h:166` | MiscExtension | ic yardimci |
| 226 | `MiscExtension::GetToplevelWindows` | `EngineX-Pro/MiscExtension.h:179` | MiscExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 227 | `MiscExtension::CountDistanceTwoPoints` | `EngineX-Pro/MiscExtension.h:252` | MiscExtension | ic yardimci |
| 228 | `MiscExtension::CountDistanceTwoPoints` | `EngineX-Pro/MiscExtension.h:261` | MiscExtension | ic yardimci |
| 229 | `MiscExtension::AngleBetweenTwoPoints` | `EngineX-Pro/MiscExtension.h:267` | MiscExtension | ic yardimci |
| 230 | `MiscExtension::GetPercentPointBetweenTwoPoints` | `EngineX-Pro/MiscExtension.h:304` | MiscExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 231 | `MiscExtension::GetPercentPointBetweenTwoPoints` | `EngineX-Pro/MiscExtension.h:316` | MiscExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 232 | `MiscExtension::DivideTwoPointsByDistance` | `EngineX-Pro/MiscExtension.h:330` | MiscExtension | ic yardimci |
| 233 | `Network::GetSize` | `EngineX-Pro/Network.cpp:79` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 234 | `Network::RecvInternalBuffer` | `EngineX-Pro/Network.cpp:134` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 235 | `Network::SendInternalBuffer` | `EngineX-Pro/Network.cpp:172` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 236 | `Network::PopSendBuffer` | `EngineX-Pro/Network.cpp:190` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 237 | `Network::Initialize` | `EngineX-Pro/Network.cpp:300` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 238 | `Network::Clear` | `EngineX-Pro/Network.cpp:328` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 239 | `Network::GetSendBufferSize` | `EngineX-Pro/Network.cpp:438` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 240 | `Network::Destroy` | `EngineX-Pro/Network.cpp:520` | Network | HyperBot ag katmani: paket gondericiler (Send*), gelen akis  |
| 241 | `PacketSniffer::IsEnablePacketSend` | `EngineX-Pro/PacketSniffer.h:17` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 242 | `PacketSniffer::IsEnablePacketRecv` | `EngineX-Pro/PacketSniffer.h:23` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 243 | `PacketSniffer::IsEnableReturnAddressPacketSend` | `EngineX-Pro/PacketSniffer.h:27` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 244 | `PacketSniffer::IsEnableReturnAddressPacketRecv` | `EngineX-Pro/PacketSniffer.h:32` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 245 | `PacketSniffer::OnStart` | `EngineX-Pro/PacketSniffer.h:36` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 246 | `PacketSniffer::OnUpdate` | `EngineX-Pro/PacketSniffer.h:43` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 247 | `PacketSniffer::OnRender` | `EngineX-Pro/PacketSniffer.h:47` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 248 | `PacketSniffer::OnTab1` | `EngineX-Pro/PacketSniffer.h:51` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 249 | `PacketSniffer::OnTabs` | `EngineX-Pro/PacketSniffer.h:62` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 250 | `PacketSniffer::OnMenu` | `EngineX-Pro/PacketSniffer.h:67` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 251 | `PacketSniffer::ProcessRetPacket` | `EngineX-Pro/PacketSniffer.h:100` | PacketSniffer | Paket dinleyici: Send/Recv hook'larindan gelen akisi header  |
| 252 | `m_regionSize` | `EngineX-Pro/PageAllocator.cpp:7` | — | ic yardimci |
| 253 | `PageAllocator` | `EngineX-Pro/PageAllocator.cpp:9` | — | ic yardimci |
| 254 | `PageAllocator::getBlock` | `EngineX-Pro/PageAllocator.cpp:21` | PageAllocator | ic yardimci |
| 255 | `PatternScan::FindPattern2` | `EngineX-Pro/PatternScan.h:50` | PatternScan | ic yardimci |
| 256 | `ProcessExtension::CreateThreadSafe` | `EngineX-Pro/ProcessExtension.h:3` | ProcessExtension | ic yardimci |
| 257 | `ProtectExtension::GetMacAdress` | `EngineX-Pro/ProtectExtension.h:3` | ProtectExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 258 | `ProtectExtension::GetVolumeId` | `EngineX-Pro/ProtectExtension.h:25` | ProtectExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 259 | `ProtectExtension::GetMachineName` | `EngineX-Pro/ProtectExtension.h:50` | ProtectExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 260 | `ProtectExtension::GetHWID` | `EngineX-Pro/ProtectExtension.h:58` | ProtectExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 261 | `SetAdminPrivilege` | `EngineX-Pro/ProtectExtension.h:68` | — | client degiskenine yazma / durum kurma sarmalayicisi |
| 262 | `GetPhysicalDriveSerialNumber` | `EngineX-Pro/ProtectExtension.h:102` | — | client bellek/oyun durumu okuma sarmalayicisi |
| 263 | `Protection::OnTab1` | `EngineX-Pro/Protection.h:16` | Protection | ic yardimci |
| 264 | `Protection::OnTab2` | `EngineX-Pro/Protection.h:37` | Protection | ic yardimci |
| 265 | `Protection::OnTabs` | `EngineX-Pro/Protection.h:50` | Protection | ic yardimci |
| 266 | `Protection::OnMenu` | `EngineX-Pro/Protection.h:56` | Protection | ic yardimci |
| 267 | `Protection::OnRender` | `EngineX-Pro/Protection.h:69` | Protection | ic yardimci |
| 268 | `Protection::OnUpdate` | `EngineX-Pro/Protection.h:73` | Protection | ic yardimci |
| 269 | `PythonExtension::PyTuple_GetFloat` | `EngineX-Pro/PythonExtension.h:43` | PythonExtension | ic yardimci |
| 270 | `PythonExtension::PyTuple_GetInteger` | `EngineX-Pro/PythonExtension.h:56` | PythonExtension | ic yardimci |
| 271 | `PythonExtension::PyTuple_GetString` | `EngineX-Pro/PythonExtension.h:68` | PythonExtension | ic yardimci |
| 272 | `PythonExtension::GetPythonDoubleInt` | `EngineX-Pro/PythonExtension.h:82` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 273 | `PythonExtension::GetPythonInt` | `EngineX-Pro/PythonExtension.h:101` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 274 | `PythonExtension::GetPythonFloat` | `EngineX-Pro/PythonExtension.h:114` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 275 | `PythonExtension::GetPythonString0` | `EngineX-Pro/PythonExtension.h:126` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 276 | `PythonExtension::GetPythonString1` | `EngineX-Pro/PythonExtension.h:141` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 277 | `PythonExtension::GetPythonString2` | `EngineX-Pro/PythonExtension.h:159` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 278 | `PythonExtension::GetPythonInteger1` | `EngineX-Pro/PythonExtension.h:178` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 279 | `PythonExtension::GetPythonInteger2` | `EngineX-Pro/PythonExtension.h:193` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 280 | `PythonExtension::GetPythonInteger3` | `EngineX-Pro/PythonExtension.h:209` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 281 | `PythonExtension::GetPythonD3DVECTOR1` | `EngineX-Pro/PythonExtension.h:226` | PythonExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 282 | `PythonExtension::CallPython` | `EngineX-Pro/PythonExtension.h:249` | PythonExtension | ic yardimci |
| 283 | `PythonExtension::CallPythonFloat1` | `EngineX-Pro/PythonExtension.h:255` | PythonExtension | ic yardimci |
| 284 | `PythonExtension::CallPythonString2` | `EngineX-Pro/PythonExtension.h:266` | PythonExtension | ic yardimci |
| 285 | `PythonExtension::CallPythonStringInt` | `EngineX-Pro/PythonExtension.h:278` | PythonExtension | ic yardimci |
| 286 | `PythonExtension::CallPythonInteger1` | `EngineX-Pro/PythonExtension.h:290` | PythonExtension | ic yardimci |
| 287 | `PythonExtension::CallPythonInteger2` | `EngineX-Pro/PythonExtension.h:301` | PythonExtension | ic yardimci |
| 288 | `PythonExtension::CallPythonInteger3` | `EngineX-Pro/PythonExtension.h:313` | PythonExtension | ic yardimci |
| 289 | `PythonExtension::CallPythonInteger4` | `EngineX-Pro/PythonExtension.h:326` | PythonExtension | ic yardimci |
| 290 | `PythonExtension::CallPythonInteger5` | `EngineX-Pro/PythonExtension.h:340` | PythonExtension | ic yardimci |
| 291 | `PythonExtension::CallPythonIntIntString` | `EngineX-Pro/PythonExtension.h:355` | PythonExtension | ic yardimci |
| 292 | `PythonScript::OnUpdate` | `EngineX-Pro/PythonScript.h:15` | PythonScript | ic yardimci |
| 293 | `PythonScript::OnRender` | `EngineX-Pro/PythonScript.h:20` | PythonScript | ic yardimci |
| 294 | `PythonScript::OnTabs` | `EngineX-Pro/PythonScript.h:38` | PythonScript | ic yardimci |
| 295 | `PythonScript::OnMenu` | `EngineX-Pro/PythonScript.h:46` | PythonScript | ic yardimci |
| 296 | `Security::NewLoadLibraryA` | `EngineX-Pro/Security.h:33` | Security | ic yardimci |
| 297 | `Security::NewGetThreadContext` | `EngineX-Pro/Security.h:62` | Security | ic yardimci |
| 298 | `Security::NewIsDebuggerPresent` | `EngineX-Pro/Security.h:73` | Security | ic yardimci |
| 299 | `Security::Initialize` | `EngineX-Pro/Security.h:77` | Security | client degiskenine yazma / durum kurma sarmalayicisi |
| 300 | `Settings::Remove` | `EngineX-Pro/Settings.h:1063` | Settings | ic yardimci |
| 301 | `Singleton::Singleton` | `EngineX-Pro/Singleton.h:5` | Singleton | ic yardimci |
| 302 | `Singleton::Singleton` | `EngineX-Pro/Singleton.h:13` | Singleton | ic yardimci |
| 303 | `Singleton::Instance` | `EngineX-Pro/Singleton.h:19` | Singleton | ic yardimci |
| 304 | `Singleton::instance` | `EngineX-Pro/Singleton.h:30` | Singleton | ic yardimci |
| 305 | `MyConnect` | `EngineX-Pro/Socks5.h:8` | — | ic yardimci |
| 306 | `DLLAction` | `EngineX-Pro/Socks5.h:146` | — | ic yardimci |
| 307 | `Spam::Clamp` | `EngineX-Pro/Spam.h:3` | Spam | ic yardimci |
| 308 | `Spam::GetTextColor` | `EngineX-Pro/Spam.h:9` | Spam | client bellek/oyun durumu okuma sarmalayicisi |
| 309 | `Spam::OnRender` | `EngineX-Pro/Spam.h:31` | Spam | ic yardimci |
| 310 | `Spam::OnStart` | `EngineX-Pro/Spam.h:37` | Spam | ic yardimci |
| 311 | `Spam::OnTabs` | `EngineX-Pro/Spam.h:251` | Spam | ic yardimci |
| 312 | `Spam::OnMenu` | `EngineX-Pro/Spam.h:256` | Spam | ic yardimci |
| 313 | `ExtWndProc` | `EngineX-Pro/SplashScreen.cpp:12` | — | ic yardimci |
| 314 | `CSplash::WindowProc` | `EngineX-Pro/SplashScreen.cpp:25` | CSplash | ic yardimci |
| 315 | `CSplash::Init` | `EngineX-Pro/SplashScreen.cpp:74` | CSplash | client degiskenine yazma / durum kurma sarmalayicisi |
| 316 | `CSplash::CSplash` | `EngineX-Pro/SplashScreen.cpp:86` | CSplash | ic yardimci |
| 317 | `CSplash::Start` | `EngineX-Pro/SplashScreen.cpp:93` | CSplash | ic yardimci |
| 318 | `CSplash::Start` | `EngineX-Pro/SplashScreen.cpp:102` | CSplash | ic yardimci |
| 319 | `CSplash::Start` | `EngineX-Pro/SplashScreen.cpp:114` | CSplash | ic yardimci |
| 320 | `CSplash` | `EngineX-Pro/SplashScreen.cpp:120` | — | ic yardimci |
| 321 | `CSplash::RegAndCreateWindow` | `EngineX-Pro/SplashScreen.cpp:125` | CSplash | ic yardimci |
| 322 | `CSplash::DoLoop` | `EngineX-Pro/SplashScreen.cpp:172` | CSplash | ic yardimci |
| 323 | `CSplash::ShowSplash` | `EngineX-Pro/SplashScreen.cpp:194` | CSplash | ic yardimci |
| 324 | `CSplash::SetBitmap` | `EngineX-Pro/SplashScreen.cpp:210` | CSplash | client degiskenine yazma / durum kurma sarmalayicisi |
| 325 | `CSplash::SetTransparentColor` | `EngineX-Pro/SplashScreen.cpp:260` | CSplash | client degiskenine yazma / durum kurma sarmalayicisi |
| 326 | `CSplash::MakeTransparent` | `EngineX-Pro/SplashScreen.cpp:267` | CSplash | ic yardimci |
| 327 | `SplashThread` | `EngineX-Pro/SplashScreen.h:56` | — | ic yardimci |
| 328 | `SplashScreen` | `EngineX-Pro/SplashScreen.h:74` | — | ic yardimci |
| 329 | `Status::OnStart` | `EngineX-Pro/Status.h:19` | Status | ic yardimci |
| 330 | `Status::OnRender` | `EngineX-Pro/Status.h:28` | Status | ic yardimci |
| 331 | `Status::OnTab1` | `EngineX-Pro/Status.h:32` | Status | ic yardimci |
| 332 | `Status::OnTabs` | `EngineX-Pro/Status.h:91` | Status | ic yardimci |
| 333 | `Status::OnMenu` | `EngineX-Pro/Status.h:96` | Status | ic yardimci |
| 334 | `StopWatch::StopWatch` | `EngineX-Pro/StopWatch.h:11` | StopWatch | ic yardimci |
| 335 | `StopWatch::running` | `EngineX-Pro/StopWatch.h:19` | StopWatch | ic yardimci |
| 336 | `StopWatch::start` | `EngineX-Pro/StopWatch.h:24` | StopWatch | ic yardimci |
| 337 | `StopWatch::stop` | `EngineX-Pro/StopWatch.h:30` | StopWatch | ic yardimci |
| 338 | `StopWatch::nano` | `EngineX-Pro/StopWatch.h:36` | StopWatch | ic yardimci |
| 339 | `StopWatch::milli` | `EngineX-Pro/StopWatch.h:41` | StopWatch | ic yardimci |
| 340 | `StopWatch::milli_hp` | `EngineX-Pro/StopWatch.h:46` | StopWatch | ic yardimci |
| 341 | `StopWatch::sec` | `EngineX-Pro/StopWatch.h:51` | StopWatch | ic yardimci |
| 342 | `StopWatch::sec_hp` | `EngineX-Pro/StopWatch.h:56` | StopWatch | ic yardimci |
| 343 | `StringExtension::ConstCharJoin` | `EngineX-Pro/StringExtension.h:11` | StringExtension | ic yardimci |
| 344 | `StringExtension::Equals` | `EngineX-Pro/StringExtension.h:43` | StringExtension | ic yardimci |
| 345 | `StringExtension::BinToStrhex` | `EngineX-Pro/StringExtension.h:54` | StringExtension | ic yardimci |
| 346 | `StringExtension::MakeHexString` | `EngineX-Pro/StringExtension.h:75` | StringExtension | ic yardimci |
| 347 | `StringExtension::BYTEToHex` | `EngineX-Pro/StringExtension.h:90` | StringExtension | ic yardimci |
| 348 | `StringExtension::GetWideChar` | `EngineX-Pro/StringExtension.h:184` | StringExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 349 | `StringExtension::GetLPWSTR` | `EngineX-Pro/StringExtension.h:193` | StringExtension | client bellek/oyun durumu okuma sarmalayicisi |
| 350 | `StringExtension::DWORDToHexString` | `EngineX-Pro/StringExtension.h:260` | StringExtension | ic yardimci |
| 351 | `StringExtension::HexToBytes` | `EngineX-Pro/StringExtension.h:276` | StringExtension | ic yardimci |
| 352 | `StringExtension::UTF8ToANSI` | `EngineX-Pro/StringExtension.h:293` | StringExtension | ic yardimci |
| 353 | `StringExtension::UTF8ToANSI2` | `EngineX-Pro/StringExtension.h:308` | StringExtension | ic yardimci |
| 354 | `TAbstractSingleton::TAbstractSingleton` | `EngineX-Pro/TAbstractSingleton.h:6` | TAbstractSingleton | ic yardimci |
| 355 | `TAbstractSingleton::TAbstractSingleton` | `EngineX-Pro/TAbstractSingleton.h:14` | TAbstractSingleton | ic yardimci |
| 356 | `UID::UID` | `EngineX-Pro/UID.cpp:1` | UID | ic yardimci |
| 357 | `UID::singleton` | `EngineX-Pro/UID.cpp:5` | UID | ic yardimci |
| 358 | `VEHHook::Hook` | `EngineX-Pro/VEH.hpp:24` | VEHHook | ic yardimci |
| 359 | `VEHHook::Unhook` | `EngineX-Pro/VEH.hpp:43` | VEHHook | ic yardimci |
| 360 | `VEHHook::VEHHandler` | `EngineX-Pro/VEH.hpp:54` | VEHHook | ic yardimci |
| 361 | `VEHHook::AreInSamePage` | `EngineX-Pro/VEH.hpp:78` | VEHHook | ic yardimci |
| 362 | `VFuncSwapHook` | `EngineX-Pro/VFuncSwapHook.cpp:3` | — | ic yardimci |
| 363 | `m_userOrigMap` | `EngineX-Pro/VFuncSwapHook.cpp:12` | — | ic yardimci |
| 364 | `VFuncSwapHook::hook` | `EngineX-Pro/VFuncSwapHook.cpp:14` | VFuncSwapHook | ic yardimci |
| 365 | `VFuncSwapHook::unHook` | `EngineX-Pro/VFuncSwapHook.cpp:38` | VFuncSwapHook | ic yardimci |
| 366 | `VFuncSwapHook::countVFuncs` | `EngineX-Pro/VFuncSwapHook.cpp:60` | VFuncSwapHook | ic yardimci |
| 367 | `VTableSwapHook` | `EngineX-Pro/VTableSwapHook.cpp:3` | — | ic yardimci |
| 368 | `VTableSwapHook` | `EngineX-Pro/VTableSwapHook.cpp:7` | — | ic yardimci |
| 369 | `m_origVFuncs` | `EngineX-Pro/VTableSwapHook.cpp:16` | — | ic yardimci |
| 370 | `VTableSwapHook::countVFuncs` | `EngineX-Pro/VTableSwapHook.cpp:78` | VTableSwapHook | ic yardimci |
| 371 | `VTableSwapHook::getOriginals` | `EngineX-Pro/VTableSwapHook.cpp:88` | VTableSwapHook | ic yardimci |
| 372 | `Visuals::OnStart` | `EngineX-Pro/Visuals.h:3` | Visuals | ic yardimci |
| 373 | `Visuals::OnUpdate` | `EngineX-Pro/Visuals.h:13` | Visuals | ic yardimci |
| 374 | `Visuals::OnRender` | `EngineX-Pro/Visuals.h:18` | Visuals | ic yardimci |
| 375 | `Visuals::OnTab1` | `EngineX-Pro/Visuals.h:23` | Visuals | ic yardimci |
| 376 | `Visuals::OnTab2` | `EngineX-Pro/Visuals.h:38` | Visuals | ic yardimci |
| 377 | `Visuals::OnTabs` | `EngineX-Pro/Visuals.h:62` | Visuals | ic yardimci |
| 378 | `Visuals::OnMenu` | `EngineX-Pro/Visuals.h:68` | Visuals | ic yardimci |
| 379 | `dsf75sddc5s4d65c` | `EngineX-Pro/dllmain.cpp:5` | — | ic yardimci |
| 380 | `ErrorTranslator` | `EngineX-Pro/dllmain.cpp:7` | — | ic yardimci |
| 381 | `NewSleep` | `EngineX-Pro/dllmain.cpp:24` | — | ic yardimci |
| 382 | `threadHookCheck` | `EngineX-Pro/dllmain.cpp:31` | — | ic yardimci |
| 383 | `Initialize` | `EngineX-Pro/dllmain.cpp:56` | — | client degiskenine yazma / durum kurma sarmalayicisi |
| 384 | `LM_CreateFakeThread` | `EngineX-Pro/dllmain.cpp:64` | — | ic yardimci |
| 385 | `DllMain` | `EngineX-Pro/dllmain.cpp:81` | — | ic yardimci |
| 386 | `SYSCALL` | `EngineX-Pro/stdafx.h:55` | — | ic yardimci |

## 8. Paket Zinciri Haritası

Hack fonksiyonu → client gerçek fonksiyonu → paket typedef → HEADER → server handler:

| Hack fonksiyonu | Proje | Client fonksiyonu | Paket (typedef) | Server karşılığı |
|---|---|---|---|---|
| `Network::SendAttackPacket / HookManager::SendAttackPacket` | HyperBot | `CPythonNetworkStream::SendAttackPacket` | `TPacketCGAttack` | CInputMain::Attack → battle.cpp |
| `GameFunctionsCustom::NetworkStreamSendAttackPacket` | C4US | `SendAttackPacket (sunucu header tablosu / OnClick yamasi)` | `TPacketCGAttack` | CInputMain::Attack → battle.cpp |
| `Network::SendCharacterStatePacket` | HyperBot | `CPythonNetworkStream::SendCharacterStatePacket` | `TPacketCGMove` | CInputMain::Move → SyncPosition |
| `GameFunctionsCustom::Boost` | C4US | `SendCharacterStatePacket (2 tickte bir)` | `TPacketCGMove` | CInputMain::Move → SyncPosition |
| `Network::SendUseSkillPacket` | HyperBot | `CPythonNetworkStream::SendUseSkillPacket` | `TPacketCGUseSkill` | CInputMain::UseSkill |
| `Network::SendPickUpItemPacket` | HyperBot | `CPythonNetworkStream::SendItemPickupPacket` | `TPacketCGItemPickup` | CInputMain::ItemPickup |
| `Network::SendItemUsePacket` | HyperBot | `CPythonNetworkStream::SendItemUsePacket` | `TPacketCGItemUse` | CInputMain::ItemUse |
| `Network::SendItemUseToItemPacket` | HyperBot | `CPythonNetworkStream::SendItemUseToItemPacket` | `TPacketCGItemUseToItem` | CInputMain::ItemUseToItem |
| `Network::SendOnClickPacket` | HyperBot | `CPythonNetworkStream::SendOnClickPacket` | `TPacketCGOnClick` | CInputMain::OnClick |
| `Network::SendTargetPacket` | HyperBot | `CPythonNetworkStream::SendTargetPacket` | `TPacketCGTarget` | CInputMain (dispatcher) |
| `Network::SendShootPacket` | HyperBot | `CPythonNetworkStream::SendShootPacket` | `TPacketCGShoot` | CInputMain::Shoot |
| `Network::SendAddFlyTargetingPacket` | HyperBot | `CPythonNetworkStream::SendAddFlyTargetingPacket` | `TPacketCGFlyTargeting` | dispatcher (fly target) |
| `Network::SendSyncPositionPacket` | HyperBot | `CPythonNetworkStream::SendSyncPositionPacket` | `TPacketCGSyncPosition` | CInputMain::SyncPosition |
| `Network::SendChatPacket` | HyperBot | `CPythonNetworkStream::SendChatPacket` | `TPacketCGChat` | CInputMain::Chat |
| `Network::SendRefinePacket` | HyperBot | `CPythonNetworkStream::SendRefinePacket` | `TPacketCGRefine` | CInputMain::Refine |
| `Network::SendGiveItemPacket` | HyperBot | `CPythonNetworkStream::SendGiveItemPacket` | `TPacketCGGiveItem` | dispatcher (item give) |
| `Network::SendScriptAnswerPacket` | HyperBot | `CPythonNetworkStream::SendScriptAnswerPacket` | `TPacketCGScriptAnswer` | dispatcher (script answer) |

## 9. Typedef Sözlüğü

Raporda geçen paket/temel typedef'ler (LegendySF Packet.h'lerden birebir):

**`TPacketCGAttack`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    BYTE	bType;
    DWORD	dwVictimVID;
    BYTE	bCRCMagicCubeProcPiece;
    BYTE	bCRCMagicCubeFilePiece;
} TPacketCGAttack;
```

**`TPacketCGMove`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	bHeader;
    BYTE	bFunc;
    BYTE	bArg;
    BYTE	bRot;
    LONG	lX;
    LONG	lY;
    DWORD	dwTime;
} TPacketCGMove;
```

**`TPacketCGUseSkill`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	bHeader;
    DWORD	dwVnum;
    DWORD	dwTargetVID;
} TPacketCGUseSkill;
```

**`TPacketCGChat`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    WORD	length;
    BYTE	type;
} TPacketCGChat;
```

**`TPacketCGItemUse`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    TItemPos	pos;
} TPacketCGItemUse;
```

**`TPacketCGOnClick`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    DWORD	vid;
} TPacketCGOnClick;
```

**`TPacketCGFlyTargeting`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	bHeader;
    DWORD	dwTargetVID;
    long	lX;
    long	lY;
} TPacketCGFlyTargeting;
```

**`TPacketCGShoot`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	bHeader;
    BYTE	bType;
} TPacketCGShoot;
```

**`TPacketCGTarget`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    DWORD	dwVID;
} TPacketCGTarget;
```

**`TPacketCGItemPickup`** (server, server: game/src/packet.h)

```cpp
typedef struct {
    BYTE	header;
    DWORD	vid;
} TPacketCGItemPickup;
```

**`TPacketCGSyncPosition`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	bHeader;
    WORD	wSize;
} TPacketCGSyncPosition;
```

**`TPacketCGScriptAnswer`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    BYTE	answer;
} TPacketCGScriptAnswer;
```

**`TPacketCGScriptButton`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    unsigned int	idx;
} TPacketCGScriptButton;
```

**`TPacketCGGiveItem`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	byHeader;
    DWORD	dwTargetVID;
    TItemPos	ItemPos;
    BYTE	byItemCount;
} TPacketCGGiveItem;
```

**`TPacketCGRefine`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    BYTE	pos;
    BYTE	type;
} TPacketCGRefine;
```

**`TPacketCGItemMove`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    TItemPos	pos;
    TItemPos	change_pos;
    BYTE	num;
} TPacketCGItemMove;
```

**`TPacketCGItemUseToItem`** (client, client: UserInterface/Packet.h)

```cpp
typedef struct {
    BYTE	header;
    TItemPos	source_pos;
    TItemPos	target_pos;
} TPacketCGItemUseToItem;
```

- **`TPixelPosition`** = `D3DXVECTOR3` (client: GameLib/MapType.h)
- **`LPCHARACTER`** = `DebugPtr<CHARACTER>` (server: game/src/typedef.h)

Ek temel typedef'ler (server `typedef.h`): `LPCHARACTER` = `CHARACTER*` (DebugPtr sarmalayıcılı), `LPDESC`, `TPixelPosition` (x,y,z float üçlüsü).

## 10. Uygulamalı Araştırma — Bununla Ne Yapılabilir?

### 10.1 Hareket hızı (kullanıcının Boost sorusu)

**Zincir:** `SCRIPT_SetPixelPosition` (lokal) + `SendCharacterStatePacket` (`TPacketCGMove`) → server `CInputMain::Move` → `SyncPosition`.

Oyun kanıtı (LegendySF client, `PythonNetworkStreamPhaseGame.cpp:1152-1192`):

```cpp
TPacketCGMove kStatePacket;
kStatePacket.bHeader = HEADER_CG_CHARACTER_MOVE;
kStatePacket.bFunc = eFunc;          // hareket tipi (walk/run)
kStatePacket.bArg  = uArg;
kStatePacket.bRot  = fDstRot/5.0f;   // yon 5 derece cozunurlukte
kStatePacket.lX    = long(c_rkPPosDst.x);
kStatePacket.lY    = long(c_rkPPosDst.y);
kStatePacket.dwTime = ELTimer_GetServerMSec();  // sunucu saati
// assert(kStatePacket.lX >= 0 && kStatePacket.lX < 204800)
// __LocalPositionToGlobalPosition(...)  → global koordinat
```

**Ne yapılabilir / nasıl çalışır:**

1. **Boost yöntemi (C4US, kanıtlandı):** rotasyona göre `sin/cos × MAIN_BOOST_SPEED` ile küçük adım hesaplar, `SCRIPT_SetPixelPosition` ile lokal taşır, **her 2 tick'te bir** state paketi yollar (sync bayrağı 0/1 dönüşümlü). Küçük adımlar sunucunun mesafe/yumuşaklık kontrolünü geçer; 'oyun atmaz' ve hızlı gidilir.
2. **Paket frekansı:** `TPacketCGMove` sunucuda mesafe kontrolüne girer; adım başına mesafe küçük tutulup frekans artırılırsa hız görünür şekilde artar (HyperBot `RunSpeedBoost` client değişkeniyle, `ShouldSend` rate-limit ile sunucu spam korumasını aşar).
3. **bRot/5 sınırlaması:** yön bilgisi 5° çözünürlükte gönderilir; hızlı yön değişimleri sunucuda yuvarlanır — diagonal kilitli hız artışı bu yüzden daha güvenli görünür.
4. **dwTime sunucu saati:** `ELTimer_GetServerMSec` ile doldurulur; geçmiş zaman/tekrar istismarı sunucu tarafında tespit edilir — bu yüzden Boost zamanı değiştirmez, sadece adım küçültür.
5. **Sinir değerleri:** `lX ∈ [0, 204800)` assert'i harita sınırıdır; aşan paket client'ta zaten düşer (assert), bu yüzden teleport denemeleri global koordinat çevirisiyle sınırlıdır.

### 10.2 Hasar (SendAttackPacket)

**Zincir:** WaitHack → `Network::SendAttackPacket` (HyperBot) veya `GameFunctionsCustom::NetworkStreamSendAttackPacket` (C4US) → `CPythonNetworkStream::SendAttackPacket` (`TPacketCGAttack` + CRC) → server `CInputMain::Attack` → `battle.cpp` `CalcMeleeDamage`.

**Kanıt (client, `PythonNetworkStreamPhaseGame.cpp:2599-2624`):**

```cpp
TPacketCGAttack kPacketAtk;
kPacketAtk.header = HEADER_CG_ATTACK;
kPacketAtk.bType  = uMotAttack;       // 0=normal, 1=combo
kPacketAtk.dwVictimVID = dwVIDVictim;
if (!SendSpecial(sizeof(kPacketAtk), &kPacketAtk)) ... // CRC magic cube ekler
return SendSequence();
```

**Server tarafı (`input_main.cpp:1750`):** `AssembleCRCMagicCube` doğrulaması → `CHARACTER_MANAGER::Find(dwVID)` → mesafe/kendine-vurma kontrolleri → `Attack` → hasar sunucuda hesaplanır. **Ne yapılabilir:** çoklu hedefe hızlı saldırı (WaitHack), menzil istismarı (Range Exploit pozisyon adımlama), sunucuya özel header uyarlaması (C4US tablo: SAMIAS2=0x3A, METINPL=0x52…), AELDRA'da OnClick +0x42 bayt yamasıyla anti-cheat bypass.

### 10.3 Hedef / Ok (Target + Fly)

`SendTargetPacket` hedef seçimi bildirir; `SendShootPacket` (HEADER_CG_SHOOT) ok atışı; `SendAddFlyTargetingPacket` mermi varış noktası. Botlar hedef VID + konum verisini oyunun `CInstanceBase` listesinden okuyup bu üçlüyle uzaktan saldırı üretir.

### 10.4 Item (toplama/kullanma)

`SendItemPickupPacket` (mesafe + sahiplik sunucuda kontrol edilir), `SendItemUsePacket` (`TItemPos{window_type, cell}`), `SendItemMovePacket`, `SendRefinePacket`. AutoItemPickup (HyperBot) `GroundItemData` listesinden beyaz-liste vnum filtresiyle toplar; C4US Inventory modülü bonus eşleme/refine akışlarını bu paketlerle kurar.

### 10.5 Sohbet / Spam

`SendChatPacket` → `TPacketCGChat{header, length, type}`; type NORMAL/SHOUT/PARTY/GUILD/WHISPER. C4US Spam modülü `GameFunctions::NetworkStreamSendChat` ile periyodik mesaj; sunucu rate-limit uygular,HyperBot `ShouldSend` istemci tarafında kısıtlar.

### 10.6 Beceri

`SendUseSkillPacket(dwVnum, dwTargetVID)` → `TPacketCGUseSkill`; sunucu seviye/MP/cooldown doğrular. Oto-buff ve SkillWH bu paketle çalışır; HyperBot `MiscHacks::AutoUsePassiveSkills` pasifleri periyodik açar.

### 10.7 Balık tutma

Oyunda `SetAttackKeyState(true)` balık modundayken `NEW_Fishing` başlatır (kanıt: `PythonPlayerInputKeyboard.cpp:6-17`). C4US Fish modülü tam olarak bu oyun davranışını paketlerle taklit eder.

## 11. Fonksiyon İndeksi

| Fonksiyon | Proje | Durum | Oyunda kanıt |
|---|---|---|---|
| `AutoItemPickup::Init` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::OnMenuFrame` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::PreIteration` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `AutoItemPickup::OnIteration` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::PostIteration` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::OnRenderWorld` | HyperBot | 🧩 SARMALAYICI | `SetDepth` |
| `AutoItemPickup::OnRenderScreen` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::IsValid` | HyperBot | 🧩 SARMALAYICI | `GetVirtualNumber` |
| `AutoItemPickup::PickUpTarget` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::AddNewTarget` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `AutoItemPickup::LoadItemsWhitelistFile` | HyperBot | 🧩 SARMALAYICI | `GetFileName`, `WriteError` |
| `AutoItemPickup::WriteItemsWhitelistFile` | HyperBot | 🧩 SARMALAYICI | `GetFileName`, `WriteError` |
| `AutoItemPickup::DumpItemsWhitelist` | HyperBot | ❌ YOK |  |
| `AutoItemPickup::AutoItemPickup` | HyperBot | ❌ YOK |  |
| `Target::m_vid` | HyperBot | ❌ YOK |  |
| `Target::m_vid` | HyperBot | ❌ YOK |  |
| `HookManager::HookManager` | HyperBot | 🧩 SARMALAYICI | `SetColor`, `WriteError` |
| `HookManager` | HyperBot | ❌ YOK |  |
| `Console::Console` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `Console` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `Console::SetColor` | HyperBot | ✅ OYUNDA | `client: EterPythonLib/PythonWindow.cpp:854` |
| `Console::WriteLine` | HyperBot | ❌ YOK |  |
| `Console::Write` | HyperBot | ✅ OYUNDA | `client: EterBase/FileBase.cpp:94` |
| `Console::WriteCmd` | HyperBot | 🧩 SARMALAYICI | `SetColor` |
| `Console::WriteInfo` | HyperBot | 🧩 SARMALAYICI | `SetColor` |
| `Console::WriteError` | HyperBot | ✅ OYUNDA | `client: EterPack/EterPack.cpp:168` |
| `Console::WriteDebug` | HyperBot | 🧩 SARMALAYICI | `SetColor` |
| `Console::WriteMultiColor` | HyperBot | 🧩 SARMALAYICI | `SetColor` |
| `Background::GlobalPosToMapInfo` | HyperBot | ❌ YOK |  |
| `Background::GetCurrentMapName` | HyperBot | ❌ YOK |  |
| `Background::GlobalToLocalPosition` | HyperBot | ❌ YOK |  |
| `Background::LocalToGlobalPosition` | HyperBot | ❌ YOK |  |
| `Background::GetTerrainHeight` | HyperBot | ✅ OYUNDA | `client: GameLib/MapManager.cpp:193` |
| `Background::IsBlockedCoord` | HyperBot | ❌ YOK |  |
| `Background::IsBlockedCoord` | HyperBot | ❌ YOK |  |
| `Background::IsAttrOn` | HyperBot | ❌ YOK |  |
| `Background::GetTerrainIndexFromWorldPos` | HyperBot | ❌ YOK |  |
| `Background::GetCurTerrainIndex` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Background::GetMinimapTerrainTexture` | HyperBot | ❌ YOK |  |
| `Background::GetCurMinimapTerrainTexture` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Background::GetMinimapTerrainArray` | HyperBot | ❌ YOK |  |
| `Background::GetResourcePointer` | HyperBot | ✅ OYUNDA | `client: EterLib/ResourceManager.cpp:271` |
| `Background::GetItemTexture` | HyperBot | 🧩 SARMALAYICI | `GetItem`, `GetResourcePointer`, `GetTexture` |
| `Background::GetD3DTexture` | HyperBot | ✅ OYUNDA | `client: EterGrnLib/Material.cpp:142` |
| `Background::ReloadResource` | HyperBot | ❌ YOK |  |
| `Background::SetViewDistance` | HyperBot | ❌ YOK |  |
| `Background::_GetTerrainNumFromCoord` | HyperBot | ❌ YOK |  |
| `Background::_GetTerrainPointer` | HyperBot | ❌ YOK |  |
| `Background::_IsAttrOn` | HyperBot | ❌ YOK |  |
| `CGraphicImageTexture::GetTexture` | HyperBot | ✅ OYUNDA | `client: PRTerrainLib/TextureSet.cpp:116` |
| `CGraphicImageTexture::GetWidth` | HyperBot | ❌ YOK |  |
| `CGraphicImageTexture::GetHeight` | HyperBot | ❌ YOK |  |
| `CGraphicImageTexture::GetSize` | HyperBot | ❌ YOK |  |
| `CGraphicImageTexture::GetPath` | HyperBot | ✅ OYUNDA | `client: EterBase/Filename.h:144` |
| `HookManager::BlockMovement` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstanceCollisionDetection.cpp:661` |
| `ConfigManager::ConfigManager` | HyperBot | ❌ YOK |  |
| `ConfigManager::CreateDump` | HyperBot | ❌ YOK |  |
| `ConfigManager::GetCheatDirectory` | HyperBot | ❌ YOK |  |
| `ConfigManager::GetFileName` | HyperBot | ✅ OYUNDA | `client: GameLib/Property.cpp:30` |
| `ConfigManager::WriteConfigToFile` | HyperBot | ❌ YOK |  |
| `ConfigManager::RegenerateConfigFile` | HyperBot | ❌ YOK |  |
| `ConfigManager::GetKeyValue` | HyperBot | ❌ YOK |  |
| `ConfigManager::IsValidValue` | HyperBot | ❌ YOK |  |
| `ConfigManager::GenerateConfigFile` | HyperBot | ❌ YOK |  |
| `ConfigManager::LoadConfigFromFile` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `ConfigManager::CreateMobsDump` | HyperBot | ❌ YOK |  |
| `ConfigManager::CreateItemsDump` | HyperBot | 🧩 SARMALAYICI | `GetRefineLevel`, `GetSubType`, `GetType` |
| `ConfigManager::LoadGameDirectory` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `HookManager::EndScene` | HyperBot | ✅ OYUNDA | `client: EterLib/StateManager.cpp:51` |
| `HookManager::Reset` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `HookManager::WndProc` | HyperBot | ❌ YOK |  |
| `HookManager::__ShowMapName` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:876` |
| `HookManager::SendAttackPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` |
| `HookManager::SendOnClickPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` |
| `HookManager::SendScriptAnswerPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` |
| `HookManager::SendGiveItemPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` |
| `HookManager::SendShootPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` |
| `HookManager::SendTargetPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` |
| `HookManager::SendAddFlyTargetingPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736` |
| `HookManager::SendFlyTargetingPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` |
| `HookManager::SendScriptButtonPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2312` |
| `HookManager::SendRefinePacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` |
| `HookManager::SendSyncPositionPacket` | HyperBot | ❌ YOK |  |
| `HookManager::SendCharacterStatePacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` |
| `HookManager::SendUseSkillPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191` |
| `Entity::GetRotationTo` | HyperBot | ❌ YOK |  |
| `Entity::GetRotationTo` | HyperBot | ❌ YOK |  |
| `Entity::GetDistanceTo` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Entity::GetDistanceTo` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Entity::IsCloseToPosition` | HyperBot | ❌ YOK |  |
| `Entity::HasEffect` | HyperBot | ❌ YOK |  |
| `Entity::IsSelectedTarget` | HyperBot | ❌ YOK |  |
| `Entity::IsMonster` | HyperBot | 🧩 SARMALAYICI | `IsEnemy`, `IsPC`, `IsStone` |
| `Entity::IsBoss` | HyperBot | ✅ OYUNDA | `server: game/src/char.cpp:8324` |
| `Entity::IsEnemy` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:301` |
| `Entity::IsPC` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:285` |
| `Entity::IsNPC` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:293` |
| `Entity::IsStone` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:309` |
| `Entity::IsAlive` | HyperBot | ❌ YOK |  |
| `Entity::IsStuned` | HyperBot | ❌ YOK |  |
| `Entity::IsWalking` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBaseMovement.cpp:193` |
| `Entity::IsBuilding` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:333` |
| `Entity::IsDoor` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:341` |
| `Entity::IsPolyPC` | HyperBot | 🧩 SARMALAYICI | `GetType` |
| `Entity::GetType` | HyperBot | ✅ OYUNDA | `client: GameLib/FlyTarget.cpp:73` |
| `Entity::GetPixelPosition` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstancePosition.cpp:83` |
| `Entity::GetRace` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstanceData.cpp:51` |
| `Entity::GetJob` | HyperBot | ✅ OYUNDA | `server: game/src/char.cpp:1838` |
| `Entity::GetName` | HyperBot | ❌ YOK |  |
| `Entity::GetVirtualNumber` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:2578` |
| `Entity::GetVID` | HyperBot | ❌ YOK |  |
| `Entity::GetRotation` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstanceRotation.cpp:109` |
| `Entity::GetLevel` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:228` |
| `Entity::GetEmpireID` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStream.cpp:803` |
| `Entity::GetBoundBox` | HyperBot | ✅ OYUNDA | `client: GameLib/DungeonBlock.cpp:177` |
| `Entity::GetBoundBoxTransformed` | HyperBot | 🧩 SARMALAYICI | `GetBoundBox`, `GetPixelPosition` |
| `Entity::IsGameMaster` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:516` |
| `Entity::IsAttacking` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBaseMovement.cpp:216` |
| `Entity::IsSuraRace` | HyperBot | 🧩 SARMALAYICI | `GetRace` |
| `Entity::IsWarriorRace` | HyperBot | 🧩 SARMALAYICI | `GetRace` |
| `Entity::IsAssassinRace` | HyperBot | 🧩 SARMALAYICI | `GetRace` |
| `Entity::IsShamanRace` | HyperBot | 🧩 SARMALAYICI | `GetRace` |
| `Entity::IsOfflineShop` | HyperBot | 🧩 SARMALAYICI | `GetType` |
| `Entity::IsPartyMember` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:638` |
| `Entity::IsPartyMember` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:638` |
| `Entity::GetEffectMap` | HyperBot | ❌ YOK |  |
| `Entity::SCRIPT_SetPixelPosition` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBaseTransform.cpp:8` |
| `Player::LookAtDestPixelPosition` | HyperBot | ❌ YOK |  |
| `Player::MoveToDestPixelPosition` | HyperBot | ❌ YOK |  |
| `Player::MoveFromDestPosition` | HyperBot | ❌ YOK |  |
| `Player::AttackToDestInstance` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Player::SetAttackKey` | HyperBot | ❌ YOK |  |
| `Player::DismountHorse` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:1068` |
| `Player::MountHorse` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:784` |
| `Player::IsMountingHorse` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:1050` |
| `Player::StopWalking` | HyperBot | ❌ YOK |  |
| `Player::StartWalking` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBaseMovement.cpp:149` |
| `Player::GetPickingPosition` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpScreen.cpp:582` |
| `Player::SetRotation` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstanceRotation.cpp:10` |
| `Player::ShortBlinkTo` | HyperBot | 🧩 SARMALAYICI | `GetBackground`, `GetPixelPosition`, `GetRotation` |
| `Player::IsBowMode` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:262` |
| `Player::GetBowRange` | HyperBot | ❌ YOK |  |
| `Player::SetTarget` | HyperBot | ✅ OYUNDA | `client: EterLib/Camera.cpp:235` |
| `Player::GetTarget` | HyperBot | ❌ YOK |  |
| `HyperGUI::HyperGUI` | HyperBot | ❌ YOK |  |
| `HyperGUI::Slide` | HyperBot | ❌ YOK |  |
| `HyperGUI::ClearAnimBuffer` | HyperBot | ❌ YOK |  |
| `HyperGUI::SetInitialPosition` | HyperBot | ❌ YOK |  |
| `HyperGUI::RenderDebug` | HyperBot | ❌ YOK |  |
| `RenderPlayers` | HyperBot | ❌ YOK |  |
| `HyperGUI::Render` | HyperBot | 🧩 SARMALAYICI | `IsConnected` |
| `HyperGUI::AnimateMainMenu` | HyperBot | ❌ YOK |  |
| `GameInformer::Init` | HyperBot | ❌ YOK |  |
| `GameInformer::OnMenuFrame` | HyperBot | ❌ YOK |  |
| `GameInformer::PreIteration` | HyperBot | 🧩 SARMALAYICI | `GetEmpireID`, `GetLevel`, `GetRace` |
| `GameInformer::OnIteration` | HyperBot | ❌ YOK |  |
| `GameInformer::PostIteration` | HyperBot | ❌ YOK |  |
| `GameInformer::OnRenderWorld` | HyperBot | ❌ YOK |  |
| `GameInformer::OnRenderScreen` | HyperBot | ❌ YOK |  |
| `GameInformer::IsValid` | HyperBot | ❌ YOK |  |
| `GameInformer::IsLocalSpectated` | HyperBot | ❌ YOK |  |
| `GameInformer::ShowLegacyInfoBox` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `GameInformer::GameInformer` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GameMainInstance` | HyperBot | ❌ YOK |  |
| `GameMainInstance` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetCursorEntity` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetSelectedEntity` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetEntity` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetEntity` | HyperBot | 🧩 SARMALAYICI | `GetVirtualNumber` |
| `GameMainInstance::GetEntity` | HyperBot | 🧩 SARMALAYICI | `GetType` |
| `GameMainInstance::GetEntity` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetEntities` | HyperBot | 🧩 SARMALAYICI | `GetType` |
| `GameMainInstance::GetItem` | HyperBot | ✅ OYUNDA | `client: EterPack/EterPack.cpp:1562` |
| `GameMainInstance::GetItem` | HyperBot | ✅ OYUNDA | `client: EterPack/EterPack.cpp:1562` |
| `GameMainInstance::GetItems` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetLocalPlayer` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetNetworkMgr` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetBackground` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:120` |
| `GameMainInstance::GetNonPlayerData` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetNonPlayerData` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetItemMapPtr` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetEntityMapPtr` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetGroundItemMapPtr` | HyperBot | ❌ YOK |  |
| `GameMainInstance::GetMobTableMapPtr` | HyperBot | ❌ YOK |  |
| `ICheatBase::ICheatBase` | HyperBot | ❌ YOK |  |
| `HookManager::IncreaseExternalForce` | HyperBot | ✅ OYUNDA | `client: GameLib/PhysicsObject.cpp:53` |
| `Item::GetItemSlot` | HyperBot | ❌ YOK |  |
| `Item::GetItemSlot` | HyperBot | 🧩 SARMALAYICI | `GetItem` |
| `Item::GetItemData` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonShop.cpp:65` |
| `Item::GetItemVID` | HyperBot | ❌ YOK |  |
| `Item::__GetItemVID` | HyperBot | ❌ YOK |  |
| `GroundItemData::GetPixelPosition` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstancePosition.cpp:83` |
| `GroundItemData::GetVirtualNumber` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:2578` |
| `GroundItemData::GetBoundBox` | HyperBot | ✅ OYUNDA | `client: GameLib/DungeonBlock.cpp:177` |
| `GroundItemData::GetBoundBoxTransformed` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `GroundItemData::GetRadius` | HyperBot | ❌ YOK |  |
| `GroundItemData::GetOwnerName` | HyperBot | ❌ YOK |  |
| `GroundItemData::GetDistanceTo` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `GroundItemData::CanBePickedUp` | HyperBot | ❌ YOK |  |
| `ItemData::GetNameW` | HyperBot | ❌ YOK |  |
| `ItemData::GetName` | HyperBot | ❌ YOK |  |
| `ItemData::GetDescryption` | HyperBot | ❌ YOK |  |
| `ItemData::GetIconPath` | HyperBot | ❌ YOK |  |
| `ItemData::GetModelPath` | HyperBot | ❌ YOK |  |
| `ItemData::GetType` | HyperBot | ✅ OYUNDA | `client: GameLib/FlyTarget.cpp:73` |
| `ItemData::GetSubType` | HyperBot | ✅ OYUNDA | `client: GameLib/ItemData.cpp:246` |
| `ItemData::GetRefineLevel` | HyperBot | ✅ OYUNDA | `server: game/src/item.cpp:1555` |
| `SItemPos::SItemPos` | HyperBot | ❌ YOK |  |
| `SItemPos::SItemPos` | HyperBot | ❌ YOK |  |
| `Math::RotatePoint` | HyperBot | ❌ YOK |  |
| `Math::GetDistance` | HyperBot | ✅ OYUNDA | `client: UserInterface/InstanceBase.cpp:2619` |
| `Math::CalcDeltaPoints` | HyperBot | ❌ YOK |  |
| `Memory::Memory` | HyperBot | 🧩 SARMALAYICI | `SetColor`, `WriteError` |
| `Memory::FindSignature` | HyperBot | ❌ YOK |  |
| `Memory::FindSignatures` | HyperBot | ❌ YOK |  |
| `Memory::GetAddress` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `Memory::GetPointer` | HyperBot | 🧩 SARMALAYICI | `WriteError` |
| `Memory::MapSignatures` | HyperBot | ❌ YOK |  |
| `Memory::CallVirtualFn` | HyperBot | ❌ YOK |  |
| `MiscHacks::Init` | HyperBot | ❌ YOK |  |
| `MiscHacks::OnMenuFrame` | HyperBot | 🧩 SARMALAYICI | `GetRace` |
| `MiscHacks::PreIteration` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition`, `GetRace` |
| `MiscHacks::OnIteration` | HyperBot | ❌ YOK |  |
| `MiscHacks::PostIteration` | HyperBot | ❌ YOK |  |
| `MiscHacks::OnRenderWorld` | HyperBot | ❌ YOK |  |
| `MiscHacks::OnRenderScreen` | HyperBot | ❌ YOK |  |
| `MiscHacks::IsValid` | HyperBot | ❌ YOK |  |
| `MiscHacks::RunSpeedBoost` | HyperBot | 🧩 SARMALAYICI | `GetBackground`, `GetRotation`, `IsWalking` |
| `MiscHacks::UnlockCamerZoom` | HyperBot | ❌ YOK |  |
| `MiscHacks::DisableFog` | HyperBot | ❌ YOK |  |
| `MiscHacks::AutoUsePassiveSkills` | HyperBot | 🧩 SARMALAYICI | `DismountHorse`, `IsMountingHorse`, `MountHorse` |
| `MiscHacks::MiscHacks` | HyperBot | ❌ YOK |  |
| `Network::SendRefinePacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:4095` |
| `Network::Recv` | HyperBot | ✅ OYUNDA | `client: EterLib/NetStream.cpp:718` |
| `Network::__Warp` | HyperBot | ❌ YOK |  |
| `Network::IsConnected` | HyperBot | ✅ OYUNDA | `server: game/src/log.cpp:50` |
| `Network::ConnectGameServer` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStream.cpp:499` |
| `Network::SetLoginInfo` | HyperBot | ✅ OYUNDA | `client: UserInterface/AccountConnector.cpp:25` |
| `Network::SelectAnswer` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonEventManager.cpp:898` |
| `Network::GetPacketsPerSec` | HyperBot | ❌ YOK |  |
| `Network::GetPacketsCount` | HyperBot | ❌ YOK |  |
| `Network::GetAvailablePackets` | HyperBot | ❌ YOK |  |
| `Network::GetMaxPacketsCount` | HyperBot | ❌ YOK |  |
| `Network::UpdatePacketSent` | HyperBot | ❌ YOK |  |
| `Network::GetTargetEntity` | HyperBot | ❌ YOK |  |
| `Network::Send` | HyperBot | ✅ OYUNDA | `client: EterLib/NetStream.cpp:758` |
| `Network::NotifyShowMap` | HyperBot | ❌ YOK |  |
| `Network::ShouldSend` | HyperBot | ❌ YOK |  |
| `Network::SendChatPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1206` |
| `Network::SendAttackPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2599` |
| `Network::SendPickUpItemPacket` | HyperBot | ❌ YOK |  |
| `Network::__SendHack` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` |
| `Network::SendAddFlyTargetingPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2736` |
| `Network::SendFlyTargetingPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2759` |
| `Network::SendSyncPositionPacket` | HyperBot | ❌ YOK |  |
| `Network::SendOnClickPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1666` |
| `Network::SendScriptAnswerPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2297` |
| `Network::SendGiveItemPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:3865` |
| `Network::SendItemUsePacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:486` |
| `Network::SendItemUseToItemPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGameItem.cpp:524` |
| `Network::SendShootPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2721` |
| `Network::SendUseSkillPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1191` |
| `Network::SendTargetPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2800` |
| `Network::SendCharacterStatePacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1152` |
| `HookManager::Send` | HyperBot | ✅ OYUNDA | `client: EterLib/NetStream.cpp:758` |
| `HookManager::Recv` | HyperBot | ✅ OYUNDA | `client: EterLib/NetStream.cpp:718` |
| `HookManager::RecvDamageInfoPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:2451` |
| `HookManager::OnScriptEventStart` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamEvent.cpp:15` |
| `TPacketGCItemDelDeprecate::count` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridCryptKeys::m_pStream` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridCryptKeys::iKeyStreamLen` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridCryptKeys::SPacketGCHybridCryptKeys` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridCryptKeys::GetFixedHeaderSize` | HyperBot | ✅ OYUNDA | `client: UserInterface/AccountConnector.cpp:388` |
| `SPacketGCHybridSDB::m_pStream` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridSDB::iSDBStreamLen` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridSDB::SPacketGCHybridSDB` | HyperBot | ❌ YOK |  |
| `SPacketGCHybridSDB::GetFixedHeaderSize` | HyperBot | ✅ OYUNDA | `client: UserInterface/AccountConnector.cpp:388` |
| `SPacketCGDragonSoulRefine::header` | HyperBot | ❌ YOK |  |
| `SPacketGCDragonSoulRefine::header` | HyperBot | ❌ YOK |  |
| `PacketSniffer::PrintASCII` | HyperBot | ❌ YOK |  |
| `PacketSniffer::DumpPacket` | HyperBot | ❌ YOK |  |
| `PacketSniffer::PacketSniffer` | HyperBot | ❌ YOK |  |
| `PacketSniffer::OnRecv` | HyperBot | ❌ YOK |  |
| `PacketSniffer::OnSend` | HyperBot | ❌ YOK |  |
| `PacketSniffer::SetSendFilter` | HyperBot | ❌ YOK |  |
| `PacketSniffer::SetRecvFilter` | HyperBot | ❌ YOK |  |
| `PacketSniffer::GetHeaderName` | HyperBot | ❌ YOK |  |
| `HookManager::ProcessTerrainCollision` | HyperBot | ✅ OYUNDA | `client: UserInterface/CameraProcedure.cpp:12` |
| `HookManager::RecvWhisperPacket` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1448` |
| `HookManager::RenderGame` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonApplication.cpp:168` |
| `RouteCreator` | HyperBot | ❌ YOK |  |
| `RouteCreator::Init` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnMenuFrame` | HyperBot | ❌ YOK |  |
| `RouteCreator::PreIteration` | HyperBot | 🧩 SARMALAYICI | `GetBackground`, `GetPixelPosition` |
| `RouteCreator::OnIteration` | HyperBot | ❌ YOK |  |
| `RouteCreator::PostIteration` | HyperBot | 🧩 SARMALAYICI | `Play` |
| `RouteCreator::OnRenderWorld` | HyperBot | 🧩 SARMALAYICI | `GetBackground` |
| `RouteCreator::OnRenderScreen` | HyperBot | ❌ YOK |  |
| `RouteCreator::IsValid` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnSend` | HyperBot | 🧩 SARMALAYICI | `GetItem`, `GetItemData`, `GetVirtualNumber` |
| `RouteCreator::OnRecv` | HyperBot | ❌ YOK |  |
| `RouteCreator::ShouldOpenScriptWindow` | HyperBot | ❌ YOK |  |
| `RouteCreator::StartRecording` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `RouteCreator::StopRecording` | HyperBot | ❌ YOK |  |
| `RouteCreator::Play` | HyperBot | ✅ OYUNDA | `client: MilesLib/SoundInstanceStream.cpp:45` |
| `RouteCreator::OnClickNPC` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnGiveItem` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnUseItem` | HyperBot | ✅ OYUNDA | `server: game/src/questnpc.cpp:280` |
| `RouteCreator::OnUseItemToAnotherItem` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnSendChatMsg` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnRefine` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnScriptButton` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnQuestConfirm` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnScriptSelectItem` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnQuestInputString` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnScriptAnswer` | HyperBot | ❌ YOK |  |
| `RouteCreator::OnPickupItem` | HyperBot | ✅ OYUNDA | `server: game/src/questnpc.cpp:966` |
| `RouteCreator::PerformAction` | HyperBot | 🧩 SARMALAYICI | `SendChatPacket`, `SendGiveItemPacket`, `SendItemUsePacket` |
| `RouteCreator::MoveToDestination` | HyperBot | 🧩 SARMALAYICI | `SCRIPT_SetPixelPosition` |
| `RecordData::RecordData` | HyperBot | 🧩 SARMALAYICI | `GetBackground` |
| `Screen::RenderLine3D` | HyperBot | ❌ YOK |  |
| `Screen::RenderCircle3D` | HyperBot | ❌ YOK |  |
| `Screen::RenderAABB3D` | HyperBot | ❌ YOK |  |
| `Screen::RenderCircleProgress3D` | HyperBot | ❌ YOK |  |
| `Screen::_RenderCircleProgress3D` | HyperBot | 🧩 SARMALAYICI | `GetBackground`, `GetTerrainHeight` |
| `Screen::SetDepth` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpExpandedImageInstance.cpp:143` |
| `Screen::RenderDrawList` | HyperBot | 🧩 SARMALAYICI | `SetRenderState` |
| `Screen::StartRender` | HyperBot | 🧩 SARMALAYICI | `SetRenderState`, `__CreatePDTVertexBufferList` |
| `Screen::EndRender` | HyperBot | 🧩 SARMALAYICI | `RestoreRenderState` |
| `Screen::UpdateWorldState` | HyperBot | ❌ YOK |  |
| `Screen::BackupRenderState` | HyperBot | ❌ YOK |  |
| `Screen::SetRenderState` | HyperBot | ✅ OYUNDA | `client: EterLib/StateManager.cpp:453` |
| `Screen::RestoreRenderState` | HyperBot | ✅ OYUNDA | `client: EterGrnLib/Material.cpp:46` |
| `Screen::_RenderLine` | HyperBot | ❌ YOK |  |
| `Screen::_RenderCircle` | HyperBot | 🧩 SARMALAYICI | `GetBackground`, `GetTerrainHeight` |
| `Screen::_RenderAABB` | HyperBot | ❌ YOK |  |
| `Screen::_SetPDTStream` | HyperBot | ❌ YOK |  |
| `Screen::_SetStreamSource` | HyperBot | ❌ YOK |  |
| `Screen::__CreatePDTVertexBufferList` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpDevice.cpp:616` |
| `Screen::__DestroyPDTVertexBufferList` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpDevice.cpp:604` |
| `Screen::_SetTexture` | HyperBot | ❌ YOK |  |
| `Screen::_SetVertexShader` | HyperBot | ❌ YOK |  |
| `Screen::DrawStringDbg` | HyperBot | ❌ YOK |  |
| `Screen::DrawString` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectFilled` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectFilled` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectGradient` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectGradient` | HyperBot | ❌ YOK |  |
| `Screen::DrawRoundedRectFilled` | HyperBot | ❌ YOK |  |
| `Screen::DrawRoundedRectFilled` | HyperBot | ❌ YOK |  |
| `Screen::DrawRoundedRect` | HyperBot | ❌ YOK |  |
| `Screen::DrawRoundedRect` | HyperBot | ❌ YOK |  |
| `Screen::DrawRect` | HyperBot | ❌ YOK |  |
| `Screen::DrawRect` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectOutlined` | HyperBot | ❌ YOK |  |
| `Screen::DrawRectOutlined` | HyperBot | ❌ YOK |  |
| `Screen::DrawCircleOutlined` | HyperBot | ❌ YOK |  |
| `Screen::DrawCircleProgressBar` | HyperBot | ❌ YOK |  |
| `Screen::DrawLine` | HyperBot | ❌ YOK |  |
| `Screen::DrawLine` | HyperBot | ❌ YOK |  |
| `Screen::DrawLine` | HyperBot | ❌ YOK |  |
| `Screen::DrawTriangleFilled` | HyperBot | ❌ YOK |  |
| `Screen::DrawTriangle` | HyperBot | ❌ YOK |  |
| `Screen::DrawCountingBar` | HyperBot | ❌ YOK |  |
| `Screen::DrawProgressBar` | HyperBot | ❌ YOK |  |
| `Screen::DrawImageRotated` | HyperBot | ❌ YOK |  |
| `Screen::DrawImage` | HyperBot | ❌ YOK |  |
| `Screen::GetTextSize` | HyperBot | ✅ OYUNDA | `client: EterPythonLib/PythonWindow.cpp:1018` |
| `Screen::DrawCircle` | HyperBot | ❌ YOK |  |
| `Screen::DrawCircleFilled` | HyperBot | ❌ YOK |  |
| `Screen::GetCursorPos` | HyperBot | ❌ YOK |  |
| `Screen::DrawLineGlow` | HyperBot | ❌ YOK |  |
| `Screen::m_dwVS` | HyperBot | ❌ YOK |  |
| `Screen::Screen` | HyperBot | 🧩 SARMALAYICI | `__DestroyPDTVertexBufferList` |
| `CStreamData::m_Stride` | HyperBot | ❌ YOK |  |
| `Clock::last_update` | HyperBot | ❌ YOK |  |
| `Clock::GetCurTime` | HyperBot | ❌ YOK |  |
| `Clock::Begin` | HyperBot | ❌ YOK |  |
| `Clock::End` | HyperBot | ❌ YOK |  |
| `Clock::Update` | HyperBot | ❌ YOK |  |
| `Clock::GetElapsedSinceUpdate` | HyperBot | ❌ YOK |  |
| `Clock::GetElapsed` | HyperBot | ❌ YOK |  |
| `Skill::GetSkillData` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonSkill.cpp:747` |
| `Skill::GetSkillDataMap` | HyperBot | ❌ YOK |  |
| `Skill::GetSelfBuffSkillList` | HyperBot | 🧩 SARMALAYICI | `GetSkillData` |
| `Skill::GetTargetBuffSkillList` | HyperBot | 🧩 SARMALAYICI | `GetSkillData` |
| `Skill::GetAttackSkillList` | HyperBot | 🧩 SARMALAYICI | `GetSkillData` |
| `Skill::GetSkillList` | HyperBot | 🧩 SARMALAYICI | `GetSkillData` |
| `SkillData::CanSelfBuff` | HyperBot | ❌ YOK |  |
| `SkillData::CanTargetBuff` | HyperBot | ❌ YOK |  |
| `SkillData::IsAttackSkill` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonSkill.cpp:1207` |
| `SkillData::GetTexture` | HyperBot | ✅ OYUNDA | `client: PRTerrainLib/TextureSet.cpp:116` |
| `Skill::IsSkillCoolTime` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonPlayer.cpp:1168` |
| `Skill::IsSkillActive` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonPlayer.cpp:1176` |
| `Skill::IsSkillReady` | HyperBot | 🧩 SARMALAYICI | `GetSkillData`, `IsSkillActive`, `IsSkillCoolTime` |
| `Skill::GetSkillIndex` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonPlayer.cpp:980` |
| `Skill::GetSkillSlot` | HyperBot | ❌ YOK |  |
| `Skill::UseSkill` | HyperBot | ✅ OYUNDA | `server: game/src/char_skill.cpp:98` |
| `Skill::IsSkillUsedByRace` | HyperBot | ❌ YOK |  |
| `Skill::IsSkillUsedByJob` | HyperBot | ❌ YOK |  |
| `HookManager::TestActorCollision` | HyperBot | ✅ OYUNDA | `client: GameLib/ActorInstanceCollisionDetection.cpp:555` |
| `HookManager::UpdateGame` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonApplication.cpp:321` |
| `InitOnAlive` | HyperBot | ❌ YOK |  |
| `HookManager::UpdateKeyboard` | HyperBot | ✅ OYUNDA | `client: EterLib/Input.cpp:88` |
| `WaitHack` | HyperBot | ❌ YOK |  |
| `WaitHack::Init` | HyperBot | ❌ YOK |  |
| `WaitHack::OnMenuFrame` | HyperBot | ❌ YOK |  |
| `WaitHack::PreIteration` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `WaitHack::OnIteration` | HyperBot | ❌ YOK |  |
| `WaitHack::PostIteration` | HyperBot | ❌ YOK |  |
| `WaitHack::OnRenderWorld` | HyperBot | 🧩 SARMALAYICI | `SetDepth` |
| `WaitHack::OnRenderScreen` | HyperBot | ❌ YOK |  |
| `WaitHack::IsValid` | HyperBot | 🧩 SARMALAYICI | `IsBoss`, `IsBuilding`, `IsDoor` |
| `WaitHack::GetTargetList` | HyperBot | ❌ YOK |  |
| `WaitHack::AttackTarget` | HyperBot | 🧩 SARMALAYICI | `IsAttacking`, `IsBowMode`, `SendAttackPacket` |
| `WaitHack::AddNewTarget` | HyperBot | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Target::m_target` | HyperBot | ❌ YOK |  |
| `Target::m_distance` | HyperBot | ❌ YOK |  |
| `HookManager::__SendHack` | HyperBot | ✅ OYUNDA | `client: UserInterface/PythonNetworkStreamPhaseGame.cpp:1094` |
| `BoundingBox::bot` | HyperBot | ❌ YOK |  |
| `BoundingBox::BoundingBox` | HyperBot | ❌ YOK |  |
| `BoundingBox::BoundingBox` | HyperBot | ❌ YOK |  |
| `BoundingBox::Zero` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetMin` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetMax` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetMinBot` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetMaxTop` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetSize` | HyperBot | ❌ YOK |  |
| `BoundingBox::GetCenter` | HyperBot | ❌ YOK |  |
| `BoundingBox::IsValid` | HyperBot | ❌ YOK |  |
| `Color::Color` | HyperBot | ✅ OYUNDA | `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` |
| `Color::GetU32` | HyperBot | ❌ YOK |  |
| `Color::Color` | HyperBot | ✅ OYUNDA | `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` |
| `Color::Color` | HyperBot | ✅ OYUNDA | `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` |
| `Color::Color` | HyperBot | ✅ OYUNDA | `client: SpeedTreeLib/SpeedGrassWrapper.cpp:140` |
| `Color::SetColor` | HyperBot | ✅ OYUNDA | `client: EterPythonLib/PythonWindow.cpp:854` |
| `Color::GetColor` | HyperBot | ✅ OYUNDA | `client: SphereLib/spherepack.cpp:388` |
| `Color::SetRawColor` | HyperBot | ❌ YOK |  |
| `Color::GetRawColor` | HyperBot | ❌ YOK |  |
| `Color::r` | HyperBot | ❌ YOK |  |
| `Color::g` | HyperBot | ❌ YOK |  |
| `Color::b` | HyperBot | ❌ YOK |  |
| `Color::a` | HyperBot | ❌ YOK |  |
| `Color::r` | HyperBot | ❌ YOK |  |
| `Color::g` | HyperBot | ❌ YOK |  |
| `Color::b` | HyperBot | ❌ YOK |  |
| `Color::a` | HyperBot | ❌ YOK |  |
| `Color::rBase` | HyperBot | ❌ YOK |  |
| `Color::gBase` | HyperBot | ❌ YOK |  |
| `Color::bBase` | HyperBot | ❌ YOK |  |
| `Color::aBase` | HyperBot | ❌ YOK |  |
| `Color::Base` | HyperBot | ❌ YOK |  |
| `Color::BaseAlpha` | HyperBot | ❌ YOK |  |
| `Color::Hue` | HyperBot | ❌ YOK |  |
| `Color::Saturation` | HyperBot | ❌ YOK |  |
| `Color::Brightness` | HyperBot | ❌ YOK |  |
| `Color::FromHSB` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Red` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Green` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Blue` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::LightBlue` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Orange` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Grey` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::DarkGrey` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Black` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::White` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Purple` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Pink` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::Yellow` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::ColdBlue` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `Color::FireRed` | HyperBot | 🧩 SARMALAYICI | `Color` |
| `MainThread` | HyperBot | ❌ YOK |  |
| `DllMain` | HyperBot | ❌ YOK |  |
| `easeInSine` | HyperBot | ❌ YOK |  |
| `easeOutSine` | HyperBot | ❌ YOK |  |
| `easeInOutSine` | HyperBot | ❌ YOK |  |
| `easeInQuad` | HyperBot | ❌ YOK |  |
| `easeOutQuad` | HyperBot | ❌ YOK |  |
| `easeInOutQuad` | HyperBot | ❌ YOK |  |
| `easeInCubic` | HyperBot | ❌ YOK |  |
| `easeOutCubic` | HyperBot | ❌ YOK |  |
| `easeInOutCubic` | HyperBot | ❌ YOK |  |
| `easeInQuart` | HyperBot | ❌ YOK |  |
| `easeOutQuart` | HyperBot | ❌ YOK |  |
| `easeInOutQuart` | HyperBot | ❌ YOK |  |
| `easeInQuint` | HyperBot | ❌ YOK |  |
| `easeOutQuint` | HyperBot | ❌ YOK |  |
| `easeInOutQuint` | HyperBot | ❌ YOK |  |
| `easeInExpo` | HyperBot | ❌ YOK |  |
| `easeOutExpo` | HyperBot | ❌ YOK |  |
| `easeInOutExpo` | HyperBot | ❌ YOK |  |
| `easeInCirc` | HyperBot | ❌ YOK |  |
| `easeOutCirc` | HyperBot | ❌ YOK |  |
| `easeInOutCirc` | HyperBot | ❌ YOK |  |
| `easeInBack` | HyperBot | ❌ YOK |  |
| `easeOutBack` | HyperBot | ❌ YOK |  |
| `easeInOutBack` | HyperBot | ❌ YOK |  |
| `easeInElastic` | HyperBot | ❌ YOK |  |
| `easeOutElastic` | HyperBot | ❌ YOK |  |
| `easeInOutElastic` | HyperBot | ❌ YOK |  |
| `easeInBounce` | HyperBot | ❌ YOK |  |
| `easeOutBounce` | HyperBot | ❌ YOK |  |
| `easeInOutBounce` | HyperBot | ❌ YOK |  |
| `GetEasingFunction` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::_impl` | HyperBot | ❌ YOK |  |
| `Matrix::Matrix` | HyperBot | ❌ YOK |  |
| `Matrix::Set` | HyperBot | ❌ YOK |  |
| `Matrix::Set` | HyperBot | ❌ YOK |  |
| `Matrix::Set` | HyperBot | ❌ YOK |  |
| `Matrix::AxisX` | HyperBot | ❌ YOK |  |
| `Matrix::AxisY` | HyperBot | ❌ YOK |  |
| `Matrix::AxisZ` | HyperBot | ❌ YOK |  |
| `Matrix::Pos` | HyperBot | ❌ YOK |  |
| `Matrix::Buff` | HyperBot | ❌ YOK |  |
| `Matrix::Buff` | HyperBot | ❌ YOK |  |
| `Matrix::Transform` | HyperBot | ✅ OYUNDA | `client: EffectLib/ParticleInstance.cpp:124` |
| `Matrix::Rotate` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpBase.cpp:414` |
| `Matrix::Identity` | HyperBot | ✅ OYUNDA | `client: EffectLib/ParticleSystemInstance.cpp:419` |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::MatrixCppImpl4x4` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Set` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Set` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Set` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::AxisX` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::AxisY` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::AxisZ` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Pos` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Buff` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Buff` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Transform` | HyperBot | ✅ OYUNDA | `client: EffectLib/ParticleInstance.cpp:124` |
| `MatrixCppImpl4x4::Rotate` | HyperBot | ✅ OYUNDA | `client: EterLib/GrpBase.cpp:414` |
| `MatrixCppImpl4x4::FlipZ` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Inverse` | HyperBot | ❌ YOK |  |
| `MatrixCppImpl4x4::Transpose` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `Quaternion::Quaternion` | HyperBot | ❌ YOK |  |
| `Quaternion::Set` | HyperBot | ❌ YOK |  |
| `Quaternion::FromMatrix` | HyperBot | ❌ YOK |  |
| `Quaternion::FromAxisAndAngle` | HyperBot | ❌ YOK |  |
| `Quaternion::FromEuler` | HyperBot | ❌ YOK |  |
| `Quaternion::GetEuler` | HyperBot | ❌ YOK |  |
| `Quaternion::Slerp` | HyperBot | ❌ YOK |  |
| `Quaternion::Lerp` | HyperBot | ❌ YOK |  |
| `Max` | HyperBot | ❌ YOK |  |
| `Min` | HyperBot | ❌ YOK |  |
| `Degree` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `w` | HyperBot | ❌ YOK |  |
| `Vec4::Set` | HyperBot | ❌ YOK |  |
| `Vec4::Length3` | HyperBot | ❌ YOK |  |
| `Vec4::Length3Sqr` | HyperBot | ❌ YOK |  |
| `Vec4::Length4` | HyperBot | ❌ YOK |  |
| `Vec4::Length4Sqr` | HyperBot | ❌ YOK |  |
| `Vec4::Normalize3` | HyperBot | ❌ YOK |  |
| `Vec4::Normalize3Safe` | HyperBot | ❌ YOK |  |
| `Vec4::Normalize4` | HyperBot | ❌ YOK |  |
| `Vec4::Cross` | HyperBot | ❌ YOK |  |
| `Vec4::Dot3` | HyperBot | ❌ YOK |  |
| `Vec4::Dot4` | HyperBot | ❌ YOK |  |
| `Vec4::Lerp` | HyperBot | ❌ YOK |  |
| `z` | HyperBot | ❌ YOK |  |
| `z` | HyperBot | ❌ YOK |  |
| `z` | HyperBot | ❌ YOK |  |
| `Vec3::Set` | HyperBot | ❌ YOK |  |
| `Vec3::Get` | HyperBot | ❌ YOK |  |
| `Vec3::Length` | HyperBot | ❌ YOK |  |
| `Vec3::LengthSqr` | HyperBot | ❌ YOK |  |
| `Vec3::Distance` | HyperBot | ❌ YOK |  |
| `Vec3::Normalize` | HyperBot | ❌ YOK |  |
| `Vec3::Normalized` | HyperBot | ❌ YOK |  |
| `Vec3::Cross` | HyperBot | ❌ YOK |  |
| `Vec3::Dot` | HyperBot | ❌ YOK |  |
| `Vec3::Lerp` | HyperBot | ❌ YOK |  |
| `y` | HyperBot | ❌ YOK |  |
| `y` | HyperBot | ❌ YOK |  |
| `y` | HyperBot | ❌ YOK |  |
| `Vec2::Set` | HyperBot | ❌ YOK |  |
| `Vec2::Length` | HyperBot | ❌ YOK |  |
| `Vec2::LengthSqr` | HyperBot | ❌ YOK |  |
| `Vec2::NormalizeSafe` | HyperBot | ❌ YOK |  |
| `Vec2::Normalize` | HyperBot | ❌ YOK |  |
| `Vec2::Dot` | HyperBot | ❌ YOK |  |
| `Vec2::Lerp` | HyperBot | ❌ YOK |  |
| `main` | HyperBot | ❌ YOK |  |
| `AVehHook::AVehHook` | C4US | ❌ YOK |  |
| `AVehHook` | C4US | ❌ YOK |  |
| `AVehHook::EventException` | C4US | ❌ YOK |  |
| `AVehHook::EventUnhandledException` | C4US | ❌ YOK |  |
| `AVehHook::Handler` | C4US | ❌ YOK |  |
| `AutoTalk::OnStart` | C4US | ❌ YOK |  |
| `AutoTalk::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `AutoTalk::OnUpdate` | C4US | ❌ YOK |  |
| `AutoTalk::OnRender` | C4US | ❌ YOK |  |
| `AutoTalk::OnTab1` | C4US | ❌ YOK |  |
| `AutoTalk::OnTabs` | C4US | ❌ YOK |  |
| `AutoTalk::OnMenu` | C4US | ❌ YOK |  |
| `TargetBuff::TargetBuff` | C4US | ❌ YOK |  |
| `Buff::SetJobRaceTextures` | C4US | ❌ YOK |  |
| `Buff::OnStart` | C4US | ❌ YOK |  |
| `Buff::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Buff::OnUpdate` | C4US | 🧩 SARMALAYICI | `GetRace`, `Check`, `begin` |
| `Buff::OnRender` | C4US | ❌ YOK |  |
| `Buff::OnTab1` | C4US | 🧩 SARMALAYICI | `begin`, `GetTargetVID`, `GetNameString` |
| `Buff::OnTabs` | C4US | ❌ YOK |  |
| `Buff::OnMenu` | C4US | ❌ YOK |  |
| `CRender::CRender` | C4US | ❌ YOK |  |
| `CRender` | C4US | ❌ YOK |  |
| `GenerateTexture` | C4US | ✅ OYUNDA | `client: EterLib/SkyBox.cpp:155` |
| `RestoreStateWithWorld::RestoreStateWithWorld` | C4US | 🧩 SARMALAYICI | `GetRenderState`, `GetTextureStageState`, `GetTransform` |
| `RestoreStateWithWorld::RestoreStateWithWorld` | C4US | 🧩 SARMALAYICI | `SetVertex`, `SetRenderState`, `SetTextureStageState` |
| `RestoreStateGame::RestoreStateGame` | C4US | 🧩 SARMALAYICI | `GetRenderState`, `GetTextureStageState`, `GetTransform` |
| `RestoreStateGame::RestoreStateGame` | C4US | 🧩 SARMALAYICI | `SetVertex`, `SetRenderState`, `SetTextureStageState` |
| `CRender::RenderSphere` | C4US | ✅ OYUNDA | `client: EterLib/GrpScreen.cpp:369` |
| `CRender::RenderBox` | C4US | 🧩 SARMALAYICI | `SetVertex`, `SetIndices`, `SetStreamSource` |
| `Clamp` | C4US | ❌ YOK |  |
| `CRender::Line3D` | C4US | 🧩 SARMALAYICI | `Lock`, `Unlock`, `SetVertex` |
| `CRender::Circle3D` | C4US | ❌ YOK |  |
| `CRender::Circle` | C4US | 🧩 SARMALAYICI | `SetVertex`, `DrawPrimitiveUP` |
| `CRender::Box3D` | C4US | 🧩 SARMALAYICI | `SetTexture`, `SetVertex`, `DrawPrimitiveUP` |
| `CRender::Cube3D` | C4US | 🧩 SARMALAYICI | `SetTexture`, `SetVertex`, `DrawPrimitiveUP` |
| `CRender::FilledCircle3D` | C4US | 🧩 SARMALAYICI | `SetTexture`, `SetRenderState`, `SetVertex` |
| `CRender::FrameRate` | C4US | ❌ YOK |  |
| `FollowTheWhiteRabbit` | C4US | ❌ YOK |  |
| `FindHookDestination` | C4US | ❌ YOK |  |
| `Configuration::OnStart` | C4US | ❌ YOK |  |
| `Configuration::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Configuration::OnUpdate` | C4US | ❌ YOK |  |
| `Configuration::OnRender` | C4US | ❌ YOK |  |
| `Configuration::OnTab1` | C4US | ❌ YOK |  |
| `Configuration::OnTab2` | C4US | ❌ YOK |  |
| `Configuration::OnTabs` | C4US | ❌ YOK |  |
| `Configuration::OnMenu` | C4US | ❌ YOK |  |
| `CryptExtension::Xor32Encrypt` | C4US | ❌ YOK |  |
| `CryptExtension::Xor32Decrypt` | C4US | ❌ YOK |  |
| `CryptExtension::base64_encode` | C4US | 🧩 SARMALAYICI | `string` |
| `CryptExtension::b64decode` | C4US | 🧩 SARMALAYICI | `size` |
| `string_format` | C4US | 🧩 SARMALAYICI | `string` |
| `ImGui::Combo` | C4US | 🧩 SARMALAYICI | `size` |
| `ImGui::Combo` | C4US | 🧩 SARMALAYICI | `size` |
| `ImGui::ListBox` | C4US | 🧩 SARMALAYICI | `size` |
| `ImGui::Selectable2` | C4US | 🧩 SARMALAYICI | `size` |
| `ImGui::DrawImagePos` | C4US | ❌ YOK |  |
| `ImGui::DrawImage` | C4US | ❌ YOK |  |
| `ImGui::ItemImage` | C4US | 🧩 SARMALAYICI | `to_string` |
| `ImGui::CenterHorizontal` | C4US | ❌ YOK |  |
| `ImGui::CenterVertical` | C4US | ❌ YOK |  |
| `ImGui::ImageAuto` | C4US | ❌ YOK |  |
| `ImGui::ImageSwitcher` | C4US | ❌ YOK |  |
| `ImGui::PopupButton` | C4US | ❌ YOK |  |
| `ImGui::Logo` | C4US | ❌ YOK |  |
| `ImGui::IconMenuButton` | C4US | ❌ YOK |  |
| `ImGui::IconButton` | C4US | ❌ YOK |  |
| `ImGui::IconButton2` | C4US | ❌ YOK |  |
| `ImGui::InputFloatMinMax` | C4US | ❌ YOK |  |
| `ImGui::Hotkey` | C4US | ❌ YOK |  |
| `Debug::OnStart` | C4US | ❌ YOK |  |
| `Debug::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Debug::OnUpdate` | C4US | ❌ YOK |  |
| `Debug::OnRender` | C4US | ❌ YOK |  |
| `Debug::Rozdzielacz` | C4US | ❌ YOK |  |
| `Debug::BuildShop` | C4US | ❌ YOK |  |
| `Debug::LoadTextureFromFile` | C4US | ❌ YOK |  |
| `Debug::OnTab1` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `to_string`, `GetItemIndex` |
| `Debug::OnTabs` | C4US | ❌ YOK |  |
| `Debug::OnMenu` | C4US | ❌ YOK |  |
| `Debug::DebugMsgBoxNoBlocking` | C4US | ❌ YOK |  |
| `GetStr` | C4US | ❌ YOK |  |
| `SItemPos::SItemPos` | C4US | ❌ YOK |  |
| `SItemPos::SItemPos` | C4US | ❌ YOK |  |
| `IAction::IAction` | C4US | ❌ YOK |  |
| `Action::Action` | C4US | 🧩 SARMALAYICI | `bind` |
| `Action::Action` | C4US | ❌ YOK |  |
| `Action::IsWaitAfter` | C4US | ❌ YOK |  |
| `Action::IsWaitBlock` | C4US | ❌ YOK |  |
| `Action::IsReady` | C4US | ❌ YOK |  |
| `Action::IsEnded` | C4US | ❌ YOK |  |
| `Action::GetFunctionPtr` | C4US | ❌ YOK |  |
| `Action::IsUniqueEquals` | C4US | ❌ YOK |  |
| `Action::Call` | C4US | ❌ YOK |  |
| `DelayActions::MakeSharedPtr` | C4US | ❌ YOK |  |
| `DelayActions::Append` | C4US | ❌ YOK |  |
| `DelayActions::AppendBlock` | C4US | 🧩 SARMALAYICI | `begin` |
| `DelayActions::AppendBlockUnique` | C4US | 🧩 SARMALAYICI | `begin` |
| `DelayActions::Update` | C4US | 🧩 SARMALAYICI | `begin` |
| `DelayActions::Clear` | C4US | 🧩 SARMALAYICI | `begin` |
| `DynamicTimer::CheckAutoSet` | C4US | 🧩 SARMALAYICI | `insert`, `make_pair` |
| `DynamicTimer::Check` | C4US | ✅ OYUNDA | `server: game/src/skill_power.cpp:8` |
| `DynamicTimer::SetTick` | C4US | ❌ YOK |  |
| `DynamicTimer::IsActive` | C4US | ❌ YOK |  |
| `Log::registerLogger` | C4US | ❌ YOK |  |
| `Log::log` | C4US | ❌ YOK |  |
| `ErrorLog::setLogLevel` | C4US | ❌ YOK |  |
| `ErrorLog::log` | C4US | ❌ YOK |  |
| `ErrorLog::push` | C4US | ❌ YOK |  |
| `ErrorLog::push` | C4US | ❌ YOK |  |
| `ErrorLog::pop` | C4US | ❌ YOK |  |
| `ErrorLog::singleton` | C4US | ❌ YOK |  |
| `Farm::TeleportToDestination` | C4US | ❌ YOK |  |
| `Farm::CheckClosestCoord` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `begin` |
| `Farm::OnStart` | C4US | 🧩 SARMALAYICI | `size`, `GetPixelPosition` |
| `Farm::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Farm::OnUpdate` | C4US | 🧩 SARMALAYICI | `IsDead`, `NEW_GetMainActorPtr`, `size` |
| `Farm::OnRender` | C4US | 🧩 SARMALAYICI | `begin` |
| `Farm::OnTab1` | C4US | 🧩 SARMALAYICI | `OnStop`, `GetPixelPosition`, `size` |
| `Farm::OnTabs` | C4US | ❌ YOK |  |
| `Farm::OnMenu` | C4US | ❌ YOK |  |
| `FileExtension::GetAppDataDirectory` | C4US | 🧩 SARMALAYICI | `string` |
| `FileExtension::GetCommonDataDirectory` | C4US | 🧩 SARMALAYICI | `string` |
| `FileExtension::GetDirectoryPathFromFilePatch` | C4US | ❌ YOK |  |
| `FileExtension::GetCurrentExeDirectory` | C4US | 🧩 SARMALAYICI | `string` |
| `FileExtension::ReadFileSize` | C4US | ❌ YOK |  |
| `FileExtension::ReadAllBytes` | C4US | ❌ YOK |  |
| `FileExtension::ReadAllBytes` | C4US | ❌ YOK |  |
| `FileExtension::CreateDirectoryPath` | C4US | 🧩 SARMALAYICI | `Read` |
| `FileExtension::Read` | C4US | ✅ OYUNDA | `client: EterBase/MappedFile.cpp:229` |
| `FileExtension::Write` | C4US | ✅ OYUNDA | `client: EterBase/FileBase.cpp:94` |
| `FileExtension::Write` | C4US | ✅ OYUNDA | `client: EterBase/FileBase.cpp:94` |
| `FileExtension::Append` | C4US | 🧩 SARMALAYICI | `Read` |
| `FileExtension::Read` | C4US | ✅ OYUNDA | `client: EterBase/MappedFile.cpp:229` |
| `FileExtension::ReadDirectory` | C4US | ❌ YOK |  |
| `FileExtension::GetExtensionFilePath` | C4US | ❌ YOK |  |
| `FileExtension::GetDirectoryFiles` | C4US | ❌ YOK |  |
| `Fish::OnStart` | C4US | 🧩 SARMALAYICI | `GetPixelPosition`, `OnStop` |
| `Fish::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Fish::OnUpdate` | C4US | ❌ YOK |  |
| `Fish::OnRender` | C4US | ❌ YOK |  |
| `Fish::OnTab1` | C4US | ❌ YOK |  |
| `Fish::OnTab2` | C4US | 🧩 SARMALAYICI | `begin`, `GetPixelPosition`, `to_string` |
| `Fish::OnTab3` | C4US | 🧩 SARMALAYICI | `begin` |
| `Fish::OnTab4` | C4US | 🧩 SARMALAYICI | `begin` |
| `Fish::OnTab5` | C4US | 🧩 SARMALAYICI | `begin` |
| `Fish::OnTabs` | C4US | ❌ YOK |  |
| `Fish::OnMenu` | C4US | ❌ YOK |  |
| `Fish::AppendCastDirect` | C4US | ❌ YOK |  |
| `Fish::AppendCastDirectString` | C4US | ❌ YOK |  |
| `Fish::CheckPosition` | C4US | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Fish::Cast` | C4US | 🧩 SARMALAYICI | `SendFishingPacket`, `GetRotation`, `SetAttackKeyState` |
| `Fish::Cast2` | C4US | 🧩 SARMALAYICI | `SendEmoticon`, `GetRotation` |
| `Fish::NewCast` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `begin` |
| `Fish::RefineRod` | C4US | 🧩 SARMALAYICI | `GetItemMetinSocket`, `GetItemIndex`, `SendItemUsePacket` |
| `Fish::BuyBait` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket`, `SendShopBuyPacket` |
| `Fish::SellItems` | C4US | 🧩 SARMALAYICI | `begin`, `SendGiveItemPacket`, `SendOnClickPacket` |
| `Fish::DropItems` | C4US | 🧩 SARMALAYICI | `begin`, `SendItemDropPacketNew` |
| `Fish::KillFishes` | C4US | 🧩 SARMALAYICI | `begin`, `SendItemUsePacket` |
| `Fish::UseBait` | C4US | 🧩 SARMALAYICI | `begin`, `SendItemUsePacket` |
| `Fish::ParseMessage` | C4US | 🧩 SARMALAYICI | `begin` |
| `GameFunctions::GetVIDByInstance` | C4US | 🧩 SARMALAYICI | `begin` |
| `GameFunctions::CharacterManagerGetInstancePtr` | C4US | 🧩 SARMALAYICI | `InstancePtr` |
| `GameFunctions::ItemManagerGetItemDataPointer` | C4US | 🧩 SARMALAYICI | `GetItemDataPointer` |
| `GameFunctions::ItemSelectItem` | C4US | ❌ YOK |  |
| `GameFunctions::ItemDataGetName` | C4US | 🧩 SARMALAYICI | `GetItemDataPointer` |
| `GameFunctions::PlayerGetMainCharacterIndex` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctions::PlayerGetStatus` | C4US | 🧩 SARMALAYICI | `GetStatus` |
| `GameFunctions::PlayerGetItemIndex` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctions::PlayerGetItemCount` | C4US | 🧩 SARMALAYICI | `GetItemCount` |
| `GameFunctions::PlayerGetName` | C4US | 🧩 SARMALAYICI | `GetName` |
| `GameFunctions::PlayerGetItemMetinSocket` | C4US | 🧩 SARMALAYICI | `GetItemMetinSocket` |
| `GameFunctions::PlayerGetItemAttribute` | C4US | 🧩 SARMALAYICI | `GetItemAttribute` |
| `GameFunctions::PlayerGetItemMetinSocket` | C4US | 🧩 SARMALAYICI | `GetItemMetinSocket` |
| `GameFunctions::PlayerGetRace` | C4US | 🧩 SARMALAYICI | `GetRace` |
| `GameFunctions::PlayerNEW_SetSingleDIKKeyState` | C4US | 🧩 SARMALAYICI | `NEW_SetSingleDIKKeyState` |
| `GameFunctions::PlayerClickSkillSlot` | C4US | 🧩 SARMALAYICI | `ClickSkillSlot` |
| `GameFunctions::PlayerIsSkillCoolTime` | C4US | 🧩 SARMALAYICI | `IsSkillCoolTime` |
| `GameFunctions::PlayerIsSkillActive` | C4US | 🧩 SARMALAYICI | `IsSkillActive` |
| `GameFunctions::PlayerGetTargetVID` | C4US | 🧩 SARMALAYICI | `GetTargetVID` |
| `GameFunctions::PlayerSetTarget` | C4US | 🧩 SARMALAYICI | `Target` |
| `GameFunctions::PlayerSetAttackKeyState` | C4US | 🧩 SARMALAYICI | `SetAttackKeyState` |
| `GameFunctions::Player__OnPressActor` | C4US | 🧩 SARMALAYICI | `__OnPressActor` |
| `GameFunctions::Player__OnClickActor` | C4US | 🧩 SARMALAYICI | `__OnClickActor` |
| `GameFunctions::PlayerNEW_GetMainActorPtr` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctions::PythonPlayerNEW_Fishing` | C4US | ❌ YOK |  |
| `GameFunctions::NetworkStreamSendItemUsePacket` | C4US | 🧩 SARMALAYICI | `ItemUse` |
| `GameFunctions::NetworkStreamSendItemUseToItemPacket` | C4US | 🧩 SARMALAYICI | `SendItemUseToItemPacket` |
| `GameFunctions::NetworkStreamSendChatPacket` | C4US | 🧩 SARMALAYICI | `ChatPacket` |
| `GameFunctions::NetworkStreamSendRefinePacket` | C4US | 🧩 SARMALAYICI | `SendRefinePacket` |
| `GameFunctions::NetworkStreamSendSendExchangeStartPacket` | C4US | 🧩 SARMALAYICI | `SendExchangeStartPacket` |
| `GameFunctions::NetworkStreamSendSendExchangeItemAddPacket` | C4US | 🧩 SARMALAYICI | `SendExchangeItemAddPacket` |
| `GameFunctions::NetworkStreamSendSendExchangeAcceptPacket` | C4US | 🧩 SARMALAYICI | `SendExchangeAcceptPacket` |
| `GameFunctions::NetworkStreamSendWhisperPacket` | C4US | 🧩 SARMALAYICI | `SendWhisperPacket` |
| `GameFunctions::NetworkStreamSendItemPickUpPacket` | C4US | 🧩 SARMALAYICI | `SendItemPickUpPacket` |
| `GameFunctions::NetworkStreamSendItemDropPacketNew` | C4US | 🧩 SARMALAYICI | `SendItemDropPacketNew` |
| `GameFunctions::NetworkStreamSendOnClickPacket` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket` |
| `GameFunctions::NetworkStreamSendShopSellPacketNew` | C4US | 🧩 SARMALAYICI | `SendShopSellPacketNew` |
| `GameFunctions::NetworkStreamSendShopBuyPacket` | C4US | 🧩 SARMALAYICI | `SendShopBuyPacket` |
| `GameFunctions::NetworkStreamSendShopEndPacket` | C4US | 🧩 SARMALAYICI | `SendShopEndPacket` |
| `GameFunctions::NetworkStreamSendGiveItemPacket` | C4US | 🧩 SARMALAYICI | `SendGiveItemPacket` |
| `GameFunctions::NetworkStreamSendItemMovePacket` | C4US | 🧩 SARMALAYICI | `SendItemMovePacket` |
| `GameFunctions::NetworkStreamConnectGameServer` | C4US | 🧩 SARMALAYICI | `ConnectGameServer` |
| `GameFunctions::NetworkStreamIsOnline` | C4US | 🧩 SARMALAYICI | `IsOnline` |
| `GameFunctions::NetworkStreamGetMainActorSkillGroup` | C4US | 🧩 SARMALAYICI | `GetMainActorSkillGroup` |
| `GameFunctions::NetworkStreamGetAccountCharacterSlotDataz` | C4US | 🧩 SARMALAYICI | `GetAccountCharacterSlotDataz` |
| `GameFunctions::NetworkStreamSendCommandPacket` | C4US | ❌ YOK |  |
| `GameFunctions::NetworkStreamConnect` | C4US | ❌ YOK |  |
| `GameFunctions::NetworkStreamSendScriptAnswerPacket` | C4US | 🧩 SARMALAYICI | `SendScriptAnswerPacket` |
| `GameFunctions::NetworkStreamServerCommand` | C4US | 🧩 SARMALAYICI | `ServerCommand` |
| `GameFunctions::NetworkStreamSendFishingPacket` | C4US | 🧩 SARMALAYICI | `SendFishingPacket` |
| `GameFunctions::NetworkStreamSendFishingQuitPacket` | C4US | ❌ YOK |  |
| `GameFunctions::NetworkStreamSendEmoticon` | C4US | 🧩 SARMALAYICI | `SendEmoticon` |
| `GameFunctions::NetworkStreamSendSpecial` | C4US | 🧩 SARMALAYICI | `SendSpecial` |
| `GameFunctions::NetworkStreamSendAttackPacket` | C4US | 🧩 SARMALAYICI | `SendAttackPacket` |
| `GameFunctions::NetworkStreamSendUseSkillPacket` | C4US | 🧩 SARMALAYICI | `SendUseSkillPacket` |
| `GameFunctions::NetworkStreamSendAddFlyTargetingPacket` | C4US | 🧩 SARMALAYICI | `SendAddFlyTargetingPacket` |
| `GameFunctions::NetworkStreamSendShootPacket` | C4US | 🧩 SARMALAYICI | `SendShootPacket` |
| `GameFunctions::NetworkStreamRecv` | C4US | 🧩 SARMALAYICI | `Recv` |
| `GameFunctions::NetworkStreamSend` | C4US | 🧩 SARMALAYICI | `Send` |
| `GameFunctions::NetworkStreamSendSequence` | C4US | 🧩 SARMALAYICI | `SendSequence` |
| `GameFunctions::NetworkStreamSendSyncPositionPacket` | C4US | 🧩 SARMALAYICI | `SendSequence` |
| `GameFunctions::NetworkStreamSendCharacterStatePacket` | C4US | 🧩 SARMALAYICI | `SendSequence` |
| `GameFunctions::NetworkStream__DirectEnterMode_Set` | C4US | 🧩 SARMALAYICI | `__DirectEnterMode_Set` |
| `GameFunctions::SelectInstancePython` | C4US | ❌ YOK |  |
| `GameFunctions::InstanceBase__SetAffect` | C4US | 🧩 SARMALAYICI | `__SetAffect` |
| `GameFunctions::InstanceBaseNEW_GetPixelPosition` | C4US | 🧩 SARMALAYICI | `GetPixelPosition` |
| `GameFunctions::InstanceBaseNEW_MoveToDestPixelPositionDirection` | C4US | 🧩 SARMALAYICI | `NEW_MoveToDestPixelPositionDirection` |
| `GameFunctions::InstanceBaseGetInstanceType` | C4US | 🧩 SARMALAYICI | `GetInstanceType` |
| `GameFunctions::InstanceBaseGetVirtualNumber` | C4US | 🧩 SARMALAYICI | `GetVirtualNumber` |
| `GameFunctions::InstanceBaseIsMountingHorse` | C4US | 🧩 SARMALAYICI | `IsMountingHorse` |
| `GameFunctions::InstanceBaseGetNameString` | C4US | 🧩 SARMALAYICI | `GetNameString` |
| `GameFunctions::InstanceBaseSCRIPT_SetPixelPosition` | C4US | 🧩 SARMALAYICI | `SetPixelPosition` |
| `GameFunctions::InstanceSetRotation` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctions::InstanceBaseGetRotation` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctions::InstanceIsWaiting` | C4US | ❌ YOK |  |
| `GameFunctions::InstanceBaseIsDead` | C4US | 🧩 SARMALAYICI | `Dead` |
| `GameFunctions::NonPlayerGetTable` | C4US | ❌ YOK |  |
| `GameFunctions::BackgroundLocalPositionToGlobalPosition` | C4US | 🧩 SARMALAYICI | `LocalPositionToGlobalPosition` |
| `GameFunctions::BackgroundGlobalPositionToMapInfo` | C4US | 🧩 SARMALAYICI | `GlobalPositionToMapInfo` |
| `GameFunctions::PyCallClassMemberFunc` | C4US | ❌ YOK |  |
| `GameFunctions::GetBackgroundHeight` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctions::ResourceManagerGetResourcePointer` | C4US | ❌ YOK |  |
| `GameFunctions::ResourceReload` | C4US | ❌ YOK |  |
| `GameFunctions::GraphicImageGetTexturePointer` | C4US | ❌ YOK |  |
| `GameFunctions::GraphicTextureGetD3DTexture` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::GetWindowWidth` | C4US | 🧩 SARMALAYICI | `GetClientRect` |
| `GameFunctionsCustom::GetWindowHeight` | C4US | 🧩 SARMALAYICI | `GetClientRect` |
| `GameFunctionsCustom::GetHpProcentageStatus` | C4US | 🧩 SARMALAYICI | `GetStatus` |
| `GameFunctionsCustom::GetMpProcentageStatus` | C4US | 🧩 SARMALAYICI | `GetStatus` |
| `GameFunctionsCustom::FindItemSlotInInventoryByName` | C4US | 🧩 SARMALAYICI | `GetItemIndex`, `GetItemDataPointer` |
| `GameFunctionsCustom::ItemSplitter` | C4US | 🧩 SARMALAYICI | `GetItemIndex`, `SendItemMovePacket` |
| `GameFunctionsCustom::PlayerGetName` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `GetNameString`, `GetNameString` |
| `GameFunctionsCustom::PlayerGetNameString` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `string`, `GetNameString` |
| `GameFunctionsCustom::GetCharSlotByName` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::PlayerIsInstance` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `GameFunctionsCustom::InstanceGetInstanceTypeByVID` | C4US | 🧩 SARMALAYICI | `GetInstancePtr`, `GetInstanceType` |
| `GameFunctionsCustom::InstanceIsDead` | C4US | 🧩 SARMALAYICI | `GetInstancePtr`, `IsDead` |
| `GameFunctionsCustom::PlayerIsDead` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `IsDead` |
| `GameFunctionsCustom::PlayerRevive` | C4US | 🧩 SARMALAYICI | `SendChatPacket` |
| `GameFunctionsCustom::PlayerIsMountingHorse` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `IsMountingHorse` |
| `GameFunctionsCustom::PlayerCanRefineRod` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::PlayerIsRodEquipped` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::PlayerIsPickAxeEquipped` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::PlayerIsBowEquipped` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::PlayerIsWeaponEquipped` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::PlayerGetPixelPosition` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `NEW_GetPixelPosition` |
| `GameFunctionsCustom::MountHorse` | C4US | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:784` |
| `GameFunctionsCustom::UnMountHorse` | C4US | 🧩 SARMALAYICI | `SendChatPacket` |
| `GameFunctionsCustom::UseAllItemVnumInInventory` | C4US | 🧩 SARMALAYICI | `GetItemIndex`, `SendItemUsePacket` |
| `GameFunctionsCustom::GetCloseObject` | C4US | 🧩 SARMALAYICI | `size`, `begin` |
| `GameFunctionsCustom::GetCloseObjectByVnum` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `GetVirtualNumber` |
| `GameFunctionsCustom::UseAllFishVnumInInventoryTillSize` | C4US | 🧩 SARMALAYICI | `begin`, `GetItemIndex`, `GetItemMetinSocket` |
| `GameFunctionsCustom::FindItemSlotsInInventory` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::FindItemSlotsInInventory` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::FindItemSlotInInventory` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::IsFullInventory` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::InventoryEquippedPercentage` | C4US | 🧩 SARMALAYICI | `GetItemIndex` |
| `GameFunctionsCustom::PlayerGetCharacterDistance` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `GetInstancePtr`, `GetDistance` |
| `GameFunctionsCustom::InstanceGetNameByVID` | C4US | 🧩 SARMALAYICI | `GetInstancePtr`, `GetNameString` |
| `GameFunctionsCustom::InstanceGetNameStringByVID` | C4US | 🧩 SARMALAYICI | `GetInstancePtr`, `string`, `GetNameString` |
| `GameFunctionsCustom::PlayerMoveToDestPixelPositionDirection` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `NEW_MoveToDestPixelPositionDirection` |
| `GameFunctionsCustom::PlayerIsMoreLessPosition` | C4US | 🧩 SARMALAYICI | `GetDistance` |
| `GameFunctionsCustom::PlayerIsMoreLessPosition` | C4US | 🧩 SARMALAYICI | `GetInstancePtr`, `NEW_GetPixelPosition`, `GetDistance` |
| `GameFunctionsCustom::GetCharacterVidByName` | C4US | 🧩 SARMALAYICI | `begin`, `GetNameString` |
| `GameFunctionsCustom::GetNPCVidByName` | C4US | 🧩 SARMALAYICI | `begin`, `GetNameString` |
| `GameFunctionsCustom::GetCharacterInstanceByName` | C4US | 🧩 SARMALAYICI | `begin`, `GetNameString` |
| `GameFunctionsCustom::GetCharacterVIDByName` | C4US | 🧩 SARMALAYICI | `begin`, `GetNameString` |
| `GameFunctionsCustom::GetObjectListCount` | C4US | 🧩 SARMALAYICI | `size` |
| `GameFunctionsCustom::GetObjectList` | C4US | 🧩 SARMALAYICI | `begin`, `NEW_GetMainActorPtr`, `IsDead` |
| `GameFunctionsCustom::DetectPlayer` | C4US | 🧩 SARMALAYICI | `begin`, `GetNameString`, `find` |
| `GameFunctionsCustom::GetGroundItemList` | C4US | 🧩 SARMALAYICI | `GetNameString`, `NEW_GetMainActorPtr`, `begin` |
| `GameFunctionsCustom::IsGroundItemsCanPickup` | C4US | 🧩 SARMALAYICI | `GetNameString`, `NEW_GetMainActorPtr`, `begin` |
| `GameFunctionsCustom::GetItemProtoList` | C4US | 🧩 SARMALAYICI | `begin`, `insert`, `make_pair` |
| `GameFunctionsCustom::GetItemProtoNames` | C4US | 🧩 SARMALAYICI | `begin`, `insert`, `make_pair` |
| `GameFunctionsCustom::InstanceBaseGetDistance` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition` |
| `GameFunctionsCustom::PlayerGetDistance` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `NEW_GetPixelPosition` |
| `GameFunctionsCustom::PlayerShowTargetArrow` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `GetInstancePtr`, `NEW_GetPixelPosition` |
| `GameFunctionsCustom::Boost` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `NEW_GetPixelPosition`, `GetRotation` |
| `GameFunctionsCustom::InstanceIsResource` | C4US | 🧩 SARMALAYICI | `GetVirtualNumber` |
| `GameFunctionsCustom::InstanceIsResource` | C4US | 🧩 SARMALAYICI | `GetVirtualNumber`, `GetInstancePtr` |
| `GameFunctionsCustom::GetObjectRank` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::InstanceIsBoss` | C4US | 🧩 SARMALAYICI | `GetVirtualNumber` |
| `GameFunctionsCustom::SendPacket` | C4US | 🧩 SARMALAYICI | `size`, `SendSequence` |
| `GameFunctionsCustom::GetTempPosition` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr` |
| `GameFunctionsCustom::GetD3DTexture` | C4US | ✅ OYUNDA | `client: EterGrnLib/Material.cpp:142` |
| `GameFunctionsCustom::PlayerGetRotation` | C4US | 🧩 SARMALAYICI | `GetRotation`, `NEW_GetMainActorPtr` |
| `GameFunctionsCustom::Teleport` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `SCRIPT_SetPixelPosition`, `SendCharacterStatePacket` |
| `GameFunctionsCustom::UseSkillSlot` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::PlayerDirectEnter` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::GetDegreeFromDirection` | C4US | ✅ OYUNDA | `client: UserInterface/InstanceBaseTransform.cpp:72` |
| `GameFunctionsCustom::GetDirectionFromDegree` | C4US | ❌ YOK |  |
| `GameFunctionsCustom::LookAtDestPixelPosition` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `GetInstancePtr`, `NEW_GetPixelPosition` |
| `GameFunctionsCustom::LookAtDestPixelPosition` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr`, `NEW_GetPixelPosition` |
| `GameFunctionsCustom::NetworkStreamSendAttackPacket` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendSpecial`, `SendSequence` |
| `GameFunctionsCustom::GetMapName` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr` |
| `GameFunctionsCustom::GlobalPositionToLocalPosition` | C4US | ✅ OYUNDA | `client: UserInterface/PythonBackground.cpp:709` |
| `GameFunctionsCustom::IsMapHaveInstance` | C4US | 🧩 SARMALAYICI | `begin` |
| `Globals::ReAddressingInstances` | C4US | 🧩 SARMALAYICI | `SetViewport` |
| `Globals::ReAddressingLocas` | C4US | ❌ YOK |  |
| `Globals::ReAddressingPython` | C4US | ❌ YOK |  |
| `Globals::ReDeclarationInstances` | C4US | ❌ YOK |  |
| `Globals::ReDeclarationLocals` | C4US | ❌ YOK |  |
| `AVehHook` | C4US | 🧩 SARMALAYICI | `find`, `insert` |
| `AVehHook` | C4US | 🧩 SARMALAYICI | `find`, `insert` |
| `HWBreakPointHook::hook` | C4US | ❌ YOK |  |
| `HWBreakPointHook::unHook` | C4US | ❌ YOK |  |
| `HWBreakPointHook::OnException` | C4US | ❌ YOK |  |
| `Hooks::NewCPythonApplicationRenderGame` | C4US | 🧩 SARMALAYICI | `GetTransform`, `begin` |
| `Hooks::NewCActorInstanceTestActorCollision` | C4US | ❌ YOK |  |
| `Hooks::NewCInstanceBaseAvoidObject` | C4US | ❌ YOK |  |
| `Hooks::NewCInstanceBaseBlockMovement` | C4US | ❌ YOK |  |
| `Hooks::NewCPhysicsObjectIncreaseExternalForce` | C4US | ❌ YOK |  |
| `Hooks::NewPyCallClassMemberFunc` | C4US | ❌ YOK |  |
| `Hooks::NewCPythonEventManagerRegisterEventSetFromString` | C4US | 🧩 SARMALAYICI | `SendScriptAnswerPacket` |
| `Hooks::NewCNetworkStreamRecv` | C4US | 🧩 SARMALAYICI | `__GlobalPositionToLocalPosition`, `GlobalPositionToLocalPosition`, `insert` |
| `Hooks::NewCNetworkStreamSend` | C4US | ❌ YOK |  |
| `Hooks::NewCNetworkStreamSendAeldra` | C4US | ❌ YOK |  |
| `Hooks::NewCPythonChatAppendChat` | C4US | ❌ YOK |  |
| `Hooks::NewCInputKeyboardUpdateKeyboard` | C4US | ❌ YOK |  |
| `Hooks::NewCResourceManagerGetResourcePointer` | C4US | ❌ YOK |  |
| `Hooks::NewScreenToClient` | C4US | ❌ YOK |  |
| `Hooks::NewDirectEndScene` | C4US | ❌ YOK |  |
| `Hooks::NewDirectReset` | C4US | ❌ YOK |  |
| `Hooks::Initialize` | C4US | ❌ YOK |  |
| `IAbstractModuleBase::IAbstractModuleBase` | C4US | ❌ YOK |  |
| `IAbstractModuleBase::IAbstractModuleBase` | C4US | ❌ YOK |  |
| `IatHook` | C4US | ❌ YOK |  |
| `m_origFunc` | C4US | ❌ YOK |  |
| `IatHook::hook` | C4US | ❌ YOK |  |
| `IatHook::unHook` | C4US | ❌ YOK |  |
| `IatHook::FindIatThunk` | C4US | ❌ YOK |  |
| `IatHook::FindIatThunkInModule` | C4US | ❌ YOK |  |
| `Inventory::OnStart` | C4US | ❌ YOK |  |
| `Inventory::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Inventory::map_compare` | C4US | 🧩 SARMALAYICI | `size`, `equal`, `begin` |
| `Inventory::Match` | C4US | 🧩 SARMALAYICI | `begin` |
| `Inventory::GetBonusTypeFromMap` | C4US | ❌ YOK |  |
| `Inventory::OnUpdate` | C4US | 🧩 SARMALAYICI | `GetItemAttribute`, `insert`, `make_pair` |
| `Inventory::OnRender` | C4US | ❌ YOK |  |
| `Inventory::GetItemIconPath` | C4US | 🧩 SARMALAYICI | `GetItemDataPointer` |
| `Inventory::OnTabbarRefine` | C4US | 🧩 SARMALAYICI | `SendRefinePacket` |
| `Inventory::OnTabbarActions` | C4US | 🧩 SARMALAYICI | `SendShopSellPacketNew`, `GetItemCount` |
| `Inventory::IDName` | C4US | 🧩 SARMALAYICI | `to_string` |
| `Inventory::OnTabbarBS` | C4US | 🧩 SARMALAYICI | `size`, `GetItemIndex`, `GetD3DTexture` |
| `Inventory::OnTab1` | C4US | 🧩 SARMALAYICI | `GetItemIndex`, `GetD3DTexture`, `to_string` |
| `Inventory::OnTabs` | C4US | ❌ YOK |  |
| `Inventory::OnMenu` | C4US | ❌ YOK |  |
| `Item::OnStart` | C4US | 🧩 SARMALAYICI | `OnStop` |
| `Item::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Item::OnRender` | C4US | ❌ YOK |  |
| `Item::OnTab1` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `insert` |
| `Item::OnTab2` | C4US | ❌ YOK |  |
| `Item::OnTabs` | C4US | ❌ YOK |  |
| `Item::OnMenu` | C4US | ❌ YOK |  |
| `Item::OnUpdate` | C4US | 🧩 SARMALAYICI | `begin`, `GetPixelPosition` |
| `Item::Slots` | C4US | 🧩 SARMALAYICI | `SendItemUsePacket` |
| `Item::Pickup` | C4US | 🧩 SARMALAYICI | `begin`, `GetPixelPosition`, `SendItemPickUpPacket` |
| `LogWindow::LogWindow` | C4US | ❌ YOK |  |
| `LogWindow::GetColor` | C4US | ✅ OYUNDA | `client: SphereLib/spherepack.cpp:388` |
| `LogWindow::Clear` | C4US | ❌ YOK |  |
| `LogWindow::Log` | C4US | 🧩 SARMALAYICI | `size`, `GetColor` |
| `LogWindow::Draw` | C4US | ✅ OYUNDA | `client: EterLib/LensFlare.cpp:524` |
| `Logger::AddString` | C4US | ❌ YOK |  |
| `Logger::Add` | C4US | ✅ OYUNDA | `client: EterLib/Decal.cpp:257` |
| `Logger::Draw` | C4US | ✅ OYUNDA | `client: EterLib/LensFlare.cpp:524` |
| `Main::SetJobRaceTextures` | C4US | ❌ YOK |  |
| `Main::OnStart` | C4US | 🧩 SARMALAYICI | `GetPixelPosition` |
| `Main::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Main::OnUpdate` | C4US | 🧩 SARMALAYICI | `GetRace`, `Revive`, `GetDistance` |
| `Main::OnRender` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr` |
| `Main::OnTab1` | C4US | 🧩 SARMALAYICI | `GetPixelPosition`, `SetAttackKeyState` |
| `Main::OnTab2` | C4US | 🧩 SARMALAYICI | `Time` |
| `Main::OnTab3` | C4US | ❌ YOK |  |
| `Main::OnTab4` | C4US | ❌ YOK |  |
| `Main::OnTabs` | C4US | ❌ YOK |  |
| `Main::OnMenu` | C4US | ❌ YOK |  |
| `Main::Revive` | C4US | ✅ OYUNDA | `client: GameLib/ActorInstance.cpp:538` |
| `Main::IsAttackMobDistance` | C4US | ❌ YOK |  |
| `Main::Skill` | C4US | ❌ YOK |  |
| `Main::WHCanAttack` | C4US | ❌ YOK |  |
| `Main::SwordWH` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `begin` |
| `Main::BowWH` | C4US | 🧩 SARMALAYICI | `begin`, `GetInstanceType`, `NEW_GetPixelPosition` |
| `Main::ResetSkillTimer` | C4US | ❌ YOK |  |
| `Main::SkillWH` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `GetInstanceType` |
| `Main::SkillWHx50` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `GetInstanceType` |
| `Main::Target` | C4US | ✅ OYUNDA | `server: game/src/questmanager.cpp:705` |
| `Main::WaitHack` | C4US | 🧩 SARMALAYICI | `Target` |
| `Main::Odpychaj` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `GetInstanceType` |
| `Main::Przyciagaj` | C4US | 🧩 SARMALAYICI | `size`, `begin`, `GetInstanceType` |
| `Main::Other` | C4US | 🧩 SARMALAYICI | `NEW_GetMainActorPtr` |
| `Main::MPPotion` | C4US | 🧩 SARMALAYICI | `SendItemUsePacket` |
| `Main::Potions` | C4US | ❌ YOK |  |
| `Main::HPPotion` | C4US | 🧩 SARMALAYICI | `SendItemUsePacket` |
| `MainCore::StartCrack` | C4US | ❌ YOK |  |
| `MainCore::Crack` | C4US | ❌ YOK |  |
| `MainCore::CheckMembers` | C4US | ❌ YOK |  |
| `MainCore::ConsoleOutput` | C4US | ❌ YOK |  |
| `MainCore::NetworkThread` | C4US | 🧩 SARMALAYICI | `SetRecvBufferSize`, `SetSendBufferSize` |
| `MainCore::Initialize` | C4US | ❌ YOK |  |
| `MainCore::UpdateLoop` | C4US | 🧩 SARMALAYICI | `begin`, `OnStop` |
| `MainDungs::CheckRelogDT` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket` |
| `MainDungs::DemonTowerStart` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket` |
| `MainDungs::AtyvaDemonTowerStart` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket` |
| `MainDungs::Dungeon175Start` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket` |
| `MainDungs::OnStart` | C4US | ❌ YOK |  |
| `MainDungs::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `MainDungs::Exit175` | C4US | ❌ YOK |  |
| `MainDungs::Restart` | C4US | ❌ YOK |  |
| `MainDungs::Teleport` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `begin` |
| `MainDungs::CheckCoords` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr` |
| `MainDungs::Update175` | C4US | 🧩 SARMALAYICI | `SendOnClickPacket`, `SendScriptAnswerPacket`, `NEW_GetPixelPosition` |
| `MainDungs::UpdateDT` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `GetInstancePtr` |
| `MainDungs::OnUpdate` | C4US | ❌ YOK |  |
| `MainDungs::OnRender` | C4US | ❌ YOK |  |
| `MainDungs::OnTab1` | C4US | 🧩 SARMALAYICI | `to_string`, `OnStop` |
| `MainDungs::OnTabs` | C4US | ❌ YOK |  |
| `MainDungs::OnMenu` | C4US | ❌ YOK |  |
| `ImageLoad` | C4US | ❌ YOK |  |
| `MainForm::SetImages` | C4US | 🧩 SARMALAYICI | `insert`, `make_pair` |
| `MainForm::Hotkey` | C4US | ❌ YOK |  |
| `GetKeyPressedTwice` | C4US | ❌ YOK |  |
| `rotateVector` | C4US | ❌ YOK |  |
| `rotateVectorX` | C4US | ❌ YOK |  |
| `rotateVectorY` | C4US | ❌ YOK |  |
| `GetMapFolder` | C4US | 🧩 SARMALAYICI | `to_string` |
| `MainForm::AddTab` | C4US | 🧩 SARMALAYICI | `begin` |
| `MainForm::AddMenu` | C4US | 🧩 SARMALAYICI | `begin` |
| `PositionToRadarPosition` | C4US | ❌ YOK |  |
| `SizeToZoom` | C4US | ❌ YOK |  |
| `MainForm::ShowRadar` | C4US | 🧩 SARMALAYICI | `NEW_GetPixelPosition`, `NEW_GetMainActorPtr`, `GetD3DTexture` |
| `MainForm::Menu` | C4US | 🧩 SARMALAYICI | `OnStop`, `begin` |
| `MainForm::Initialize` | C4US | 🧩 SARMALAYICI | `make_pair` |
| `WndProc` | C4US | ❌ YOK |  |
| `MathExtension::PointInCircle` | C4US | ❌ YOK |  |
| `MemAccessor::mem_copy` | C4US | ❌ YOK |  |
| `MemAccessor::safe_mem_write` | C4US | ❌ YOK |  |
| `MemAccessor::safe_mem_read` | C4US | ❌ YOK |  |
| `MemAccessor::mem_protect` | C4US | ❌ YOK |  |
| `PLH::TranslateProtection` | C4US | ❌ YOK |  |
| `PLH::TranslateProtection` | C4US | ❌ YOK |  |
| `MemoryExtension::ReadMemory` | C4US | ❌ YOK |  |
| `MemoryExtension::WriteMemory` | C4US | ❌ YOK |  |
| `MemoryExtension::MemSet` | C4US | ❌ YOK |  |
| `MemoryExtension::SetMemory` | C4US | ❌ YOK |  |
| `MemoryExtension::JmpHook` | C4US | ❌ YOK |  |
| `MemoryExtension::SetByte` | C4US | ❌ YOK |  |
| `MemoryExtension::GetByte` | C4US | ❌ YOK |  |
| `MemoryExtension::SetWord` | C4US | ❌ YOK |  |
| `MemoryExtension::GetWord` | C4US | ✅ OYUNDA | `server: db/src/Config.cpp:29` |
| `MemoryExtension::SetDword` | C4US | ❌ YOK |  |
| `MemoryExtension::GetDword` | C4US | ❌ YOK |  |
| `MemoryExtension::SetFloat` | C4US | ❌ YOK |  |
| `MemoryExtension::GetFloat` | C4US | ❌ YOK |  |
| `MemoryExtension::SetDouble` | C4US | ❌ YOK |  |
| `MemoryExtension::SetJmp` | C4US | ❌ YOK |  |
| `MemoryExtension::SetJg` | C4US | ❌ YOK |  |
| `MemoryExtension::SetJa` | C4US | ❌ YOK |  |
| `MemoryExtension::SetOp` | C4US | ❌ YOK |  |
| `MemoryExtension::SetRange` | C4US | ✅ OYUNDA | `client: EterLib/GrpLightManager.cpp:245` |
| `MemoryExtension::SetHook` | C4US | ❌ YOK |  |
| `MemoryExtension::HookThis` | C4US | ❌ YOK |  |
| `MemoryExtension::ErasePEHeader` | C4US | ❌ YOK |  |
| `PLH::findPattern` | C4US | ❌ YOK |  |
| `PLH::findPattern_rev` | C4US | ❌ YOK |  |
| `MiscExtension::ShowBalloon` | C4US | 🧩 SARMALAYICI | `size`, `LoadImage` |
| `MiscExtension::OpenWebiste` | C4US | ❌ YOK |  |
| `MiscExtension::PlayAlerSound` | C4US | ❌ YOK |  |
| `MiscExtension::UpdateBalloon` | C4US | ❌ YOK |  |
| `MiscExtension::FindTopWindow` | C4US | ❌ YOK |  |
| `MiscExtension::RandomString` | C4US | 🧩 SARMALAYICI | `begin` |
| `MiscExtension::RandomInt` | C4US | 🧩 SARMALAYICI | `time` |
| `MiscExtension::RandomFloat` | C4US | ❌ YOK |  |
| `EnumWindowsCallbackArgs::pid` | C4US | ❌ YOK |  |
| `MiscExtension::EnumWindowsCallback` | C4US | ❌ YOK |  |
| `MiscExtension::GetToplevelWindows` | C4US | ❌ YOK |  |
| `MiscExtension::CurrentDateTime` | C4US | 🧩 SARMALAYICI | `time`, `localtime` |
| `MiscExtension::CurrentDateTimeShort` | C4US | 🧩 SARMALAYICI | `time`, `localtime` |
| `MiscExtension::GetServerTime` | C4US | ✅ OYUNDA | `client: UserInterface/PythonApplication.cpp:1223` |
| `MiscExtension::CountDistanceTwoPoints` | C4US | ❌ YOK |  |
| `MiscExtension::CountDistanceTwoPoints` | C4US | ❌ YOK |  |
| `MiscExtension::AngleBetweenTwoPoints` | C4US | ❌ YOK |  |
| `MiscExtension::GetPercentPointBetweenTwoPoints` | C4US | ❌ YOK |  |
| `MiscExtension::GetPercentPointBetweenTwoPoints` | C4US | ❌ YOK |  |
| `MiscExtension::DivideTwoPointsByDistance` | C4US | ❌ YOK |  |
| `Network::GetHostName` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:6` |
| `Network::IsIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:33` |
| `Network::SetConnection` | C4US | ✅ OYUNDA | `client: UserInterface/PythonNetworkDatagram.cpp:76` |
| `Network::SetLocalIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:56` |
| `Network::SetIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:61` |
| `Network::SetIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:61` |
| `Network::SetDNS` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:71` |
| `Network::SetPort` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:79` |
| `Network::GetSize` | C4US | ❌ YOK |  |
| `Network::GetIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:89` |
| `Network::GetIP` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:89` |
| `Network::GetPort` | C4US | ✅ OYUNDA | `client: EterLib/NetAddress.cpp:102` |
| `Network::SetRecvBufferSize` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:37` |
| `Network::SetSendBufferSize` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:55` |
| `Network::RecvInternalBuffer` | C4US | ❌ YOK |  |
| `Network::SendInternalBuffer` | C4US | ❌ YOK |  |
| `Network::PopSendBuffer` | C4US | ❌ YOK |  |
| `Network::Process` | C4US | 🧩 SARMALAYICI | `OnConnectSuccess`, `time`, `OnConnectFailure` |
| `Network::Disconnect` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:357` |
| `Network::Initialize` | C4US | ❌ YOK |  |
| `Network::Clear` | C4US | ❌ YOK |  |
| `Network::Connect` | C4US | 🧩 SARMALAYICI | `OnRemoteDisconnect`, `SetConnection`, `OnConnectFailure` |
| `Network::ClearRecvBuffer` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:462` |
| `Network::GetRecvBufferSize` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:467` |
| `Network::Peek` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:472` |
| `Network::Peek` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:472` |
| `Network::Recv` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:718` |
| `Network::Recv` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:718` |
| `Network::GetSendBufferSize` | C4US | ❌ YOK |  |
| `Network::Send` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:758` |
| `Network::Peek` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:472` |
| `Network::Recv` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:718` |
| `Network::SendFlush` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:813` |
| `Network::Send` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:758` |
| `Network::IsOnline` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:826` |
| `Network::OnProcess` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:856` |
| `Network::OnRemoteDisconnect` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:861` |
| `Network::OnDisconnect` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:865` |
| `Network::OnConnectSuccess` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:869` |
| `Network::OnConnectFailure` | C4US | ✅ OYUNDA | `client: EterLib/NetStream.cpp:874` |
| `Network::Destroy` | C4US | ❌ YOK |  |
| `PacketHandler::CheckPacket` | C4US | ✅ OYUNDA | `client: UserInterface/PythonNetworkStream.cpp:528` |
| `PacketHandler::Process` | C4US | 🧩 SARMALAYICI | `CheckPacket` |
| `PacketHandler::SendHeartBeatResponse` | C4US | 🧩 SARMALAYICI | `Send` |
| `PacketHandler::RecvHeartBeatPacket` | C4US | 🧩 SARMALAYICI | `Recv` |
| `PacketHandler::SendAuthPacket` | C4US | 🧩 SARMALAYICI | `Send` |
| `PacketHandler::RecvAuthPacket` | C4US | 🧩 SARMALAYICI | `Recv` |
| `PacketSniffer::IsEnablePacketSend` | C4US | ❌ YOK |  |
| `PacketSniffer::IsEnablePacketRecv` | C4US | ❌ YOK |  |
| `PacketSniffer::IsEnableReturnAddressPacketSend` | C4US | ❌ YOK |  |
| `PacketSniffer::IsEnableReturnAddressPacketRecv` | C4US | ❌ YOK |  |
| `PacketSniffer::OnStart` | C4US | ❌ YOK |  |
| `PacketSniffer::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `PacketSniffer::OnUpdate` | C4US | ❌ YOK |  |
| `PacketSniffer::OnRender` | C4US | ❌ YOK |  |
| `PacketSniffer::OnTab1` | C4US | ❌ YOK |  |
| `PacketSniffer::OnTabs` | C4US | ❌ YOK |  |
| `PacketSniffer::OnMenu` | C4US | ❌ YOK |  |
| `PacketSniffer::ProcessSendPacket` | C4US | 🧩 SARMALAYICI | `to_string` |
| `PacketSniffer::ProcessRetPacket` | C4US | ❌ YOK |  |
| `PacketSniffer::ProcessRecvPacket` | C4US | 🧩 SARMALAYICI | `to_string` |
| `m_regionSize` | C4US | ❌ YOK |  |
| `PageAllocator` | C4US | ❌ YOK |  |
| `PageAllocator::getBlock` | C4US | ❌ YOK |  |
| `PatternScan::FindPattern` | C4US | 🧩 SARMALAYICI | `Search` |
| `PatternScan::FindPatternGlobal` | C4US | 🧩 SARMALAYICI | `Search` |
| `PatternScan::FindPattern2` | C4US | ❌ YOK |  |
| `PatternScan::Search` | C4US | ✅ OYUNDA | `server: db/src/Config.cpp:152` |
| `ProcessExtension::CreateThreadSafe` | C4US | ❌ YOK |  |
| `ProtectExtension::GetMacAdress` | C4US | ❌ YOK |  |
| `ProtectExtension::GetVolumeId` | C4US | ❌ YOK |  |
| `ProtectExtension::GetCpuId` | C4US | 🧩 SARMALAYICI | `to_string` |
| `ProtectExtension::GetMachineName` | C4US | ❌ YOK |  |
| `ProtectExtension::GetHWID` | C4US | ❌ YOK |  |
| `SetAdminPrivilege` | C4US | ❌ YOK |  |
| `GetPhysicalDriveSerialNumber` | C4US | ❌ YOK |  |
| `GetHardwareId` | C4US | 🧩 SARMALAYICI | `string` |
| `Protection::OnStart` | C4US | 🧩 SARMALAYICI | `OnStop` |
| `Protection::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Protection::OnTab1` | C4US | ❌ YOK |  |
| `Protection::OnTab2` | C4US | ❌ YOK |  |
| `Protection::OnTabs` | C4US | ❌ YOK |  |
| `Protection::OnMenu` | C4US | ❌ YOK |  |
| `Protection::OnRender` | C4US | ❌ YOK |  |
| `Protection::OnUpdate` | C4US | ❌ YOK |  |
| `PythonExtension::CheckImportNames` | C4US | 🧩 SARMALAYICI | `begin` |
| `PythonExtension::PyTuple_GetFloat` | C4US | ❌ YOK |  |
| `PythonExtension::PyTuple_GetInteger` | C4US | ❌ YOK |  |
| `PythonExtension::PyTuple_GetString` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonDoubleInt` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonInt` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonFloat` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonString0` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonString1` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonString2` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonInteger1` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonInteger2` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonInteger3` | C4US | ❌ YOK |  |
| `PythonExtension::GetPythonD3DVECTOR1` | C4US | ❌ YOK |  |
| `PythonExtension::CallPython` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonFloat1` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonString2` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonStringInt` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonInteger1` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonInteger2` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonInteger3` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonInteger4` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonInteger5` | C4US | ❌ YOK |  |
| `PythonExtension::CallPythonIntIntString` | C4US | ❌ YOK |  |
| `PythonGameFunctions::PlayerGetStatus` | C4US | 🧩 SARMALAYICI | `GetStatus` |
| `PythonScript::OnStart` | C4US | 🧩 SARMALAYICI | `string` |
| `PythonScript::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `PythonScript::OnUpdate` | C4US | ❌ YOK |  |
| `PythonScript::OnRender` | C4US | ❌ YOK |  |
| `PythonScript::OnTab1` | C4US | 🧩 SARMALAYICI | `size` |
| `PythonScript::OnTabs` | C4US | ❌ YOK |  |
| `PythonScript::OnMenu` | C4US | ❌ YOK |  |
| `Security::NewLoadLibraryA` | C4US | ❌ YOK |  |
| `Security::NewPy_InitModule4` | C4US | 🧩 SARMALAYICI | `insert` |
| `Security::NewGetThreadContext` | C4US | ❌ YOK |  |
| `Security::NewIsDebuggerPresent` | C4US | ❌ YOK |  |
| `Security::Initialize` | C4US | ❌ YOK |  |
| `Settings::LoadItemFilter` | C4US | 🧩 SARMALAYICI | `Read`, `find` |
| `Settings::SaveItemFilter` | C4US | 🧩 SARMALAYICI | `Write` |
| `Settings::LoadFarm` | C4US | 🧩 SARMALAYICI | `Read`, `find`, `size` |
| `Settings::SaveFarm` | C4US | 🧩 SARMALAYICI | `size`, `Write` |
| `Settings::LoadServerVariables` | C4US | 🧩 SARMALAYICI | `insert`, `make_pair` |
| `Settings::Load` | C4US | 🧩 SARMALAYICI | `Read`, `find` |
| `Settings::Save` | C4US | 🧩 SARMALAYICI | `Write` |
| `Settings::Remove` | C4US | ❌ YOK |  |
| `Singleton::Singleton` | C4US | ❌ YOK |  |
| `Singleton::Singleton` | C4US | ❌ YOK |  |
| `Singleton::Instance` | C4US | ❌ YOK |  |
| `Singleton::InstancePtr` | C4US | ✅ OYUNDA | `client: GameLib/Area.cpp:77` |
| `Singleton::instance` | C4US | ❌ YOK |  |
| `MyConnect` | C4US | ❌ YOK |  |
| `DLLAction` | C4US | ❌ YOK |  |
| `Spam::Clamp` | C4US | ❌ YOK |  |
| `Spam::GetTextColor` | C4US | ❌ YOK |  |
| `Spam::OnRender` | C4US | ❌ YOK |  |
| `Spam::OnStart` | C4US | ❌ YOK |  |
| `Spam::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Spam::OnUpdate` | C4US | 🧩 SARMALAYICI | `SendChatPacket`, `begin`, `GetNameString` |
| `Spam::OnTab1` | C4US | 🧩 SARMALAYICI | `Time`, `size` |
| `Spam::OnTabs` | C4US | ❌ YOK |  |
| `Spam::OnMenu` | C4US | ❌ YOK |  |
| `ExtWndProc` | C4US | ❌ YOK |  |
| `CSplash::WindowProc` | C4US | ❌ YOK |  |
| `CSplash::OnPaint` | C4US | 🧩 SARMALAYICI | `GetClientRect`, `SetBkMode`, `SetTextColor` |
| `CSplash::Init` | C4US | ❌ YOK |  |
| `CSplash::CSplash` | C4US | ❌ YOK |  |
| `CSplash::Start` | C4US | ❌ YOK |  |
| `CSplash::Start` | C4US | ❌ YOK |  |
| `CSplash::Start` | C4US | ❌ YOK |  |
| `CSplash` | C4US | ❌ YOK |  |
| `CSplash::RegAndCreateWindow` | C4US | ❌ YOK |  |
| `CSplash::DoLoop` | C4US | ❌ YOK |  |
| `CSplash::ShowSplash` | C4US | ❌ YOK |  |
| `CSplash::SetBitmap` | C4US | 🧩 SARMALAYICI | `LoadImage` |
| `CSplash::SetBitmap` | C4US | ❌ YOK |  |
| `CSplash::FreeResources` | C4US | 🧩 SARMALAYICI | `DeleteObject` |
| `CSplash::CloseSplash` | C4US | 🧩 SARMALAYICI | `SendMessage` |
| `CSplash::SetTransparentColor` | C4US | ❌ YOK |  |
| `CSplash::MakeTransparent` | C4US | ❌ YOK |  |
| `SplashThread` | C4US | ❌ YOK |  |
| `SplashScreen` | C4US | ❌ YOK |  |
| `Status::OnStart` | C4US | ❌ YOK |  |
| `Status::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Status::OnRender` | C4US | ❌ YOK |  |
| `Status::OnTab1` | C4US | ❌ YOK |  |
| `Status::OnTabs` | C4US | ❌ YOK |  |
| `Status::OnMenu` | C4US | ❌ YOK |  |
| `Status::OnUpdate` | C4US | 🧩 SARMALAYICI | `GetMainCharacterIndex`, `GetTargetVID`, `GetVirtualNumber` |
| `StopWatch::StopWatch` | C4US | ❌ YOK |  |
| `StopWatch::running` | C4US | ❌ YOK |  |
| `StopWatch::start` | C4US | ❌ YOK |  |
| `StopWatch::stop` | C4US | ❌ YOK |  |
| `StopWatch::nano` | C4US | ❌ YOK |  |
| `StopWatch::milli` | C4US | ❌ YOK |  |
| `StopWatch::milli_hp` | C4US | ❌ YOK |  |
| `StopWatch::sec` | C4US | ❌ YOK |  |
| `StopWatch::sec_hp` | C4US | ❌ YOK |  |
| `StringExtension::ToUpper` | C4US | 🧩 SARMALAYICI | `transform`, `begin` |
| `StringExtension::ConstCharJoin` | C4US | ❌ YOK |  |
| `StringExtension::ReplaceString` | C4US | 🧩 SARMALAYICI | `find`, `replace` |
| `StringExtension::Contains` | C4US | 🧩 SARMALAYICI | `transform`, `begin`, `find` |
| `StringExtension::ContainsW` | C4US | 🧩 SARMALAYICI | `find` |
| `StringExtension::Equals` | C4US | ❌ YOK |  |
| `StringExtension::BinToStrhex` | C4US | ❌ YOK |  |
| `StringExtension::MakeHexString` | C4US | ❌ YOK |  |
| `StringExtension::BYTEToHex` | C4US | ❌ YOK |  |
| `StringExtension::StringFormat` | C4US | 🧩 SARMALAYICI | `size` |
| `StringExtension::StringFormat2` | C4US | 🧩 SARMALAYICI | `size`, `reset`, `string` |
| `StringExtension::StringFormatChar` | C4US | 🧩 SARMALAYICI | `size`, `reset`, `string` |
| `StringExtension::BYTEToAsciiString` | C4US | 🧩 SARMALAYICI | `string` |
| `StringExtension::GetWideChar` | C4US | ❌ YOK |  |
| `StringExtension::GetLPWSTR` | C4US | ❌ YOK |  |
| `StringExtension::GetWCharFromString` | C4US | 🧩 SARMALAYICI | `begin` |
| `StringExtension::ConstCharFromWChar` | C4US | 🧩 SARMALAYICI | `begin` |
| `StringExtension::StringFromWChar` | C4US | 🧩 SARMALAYICI | `begin` |
| `StringExtension::StringFromWString` | C4US | 🧩 SARMALAYICI | `begin` |
| `StringExtension::Split` | C4US | 🧩 SARMALAYICI | `begin` |
| `StringExtension::Split2` | C4US | 🧩 SARMALAYICI | `find` |
| `StringExtension::DWORDToHexString` | C4US | ❌ YOK |  |
| `StringExtension::HexToBytes` | C4US | ❌ YOK |  |
| `StringExtension::UTF8ToANSI` | C4US | ❌ YOK |  |
| `StringExtension::UTF8ToANSI2` | C4US | ❌ YOK |  |
| `StringExtension::ASCIIToUTF8` | C4US | 🧩 SARMALAYICI | `size` |
| `StringExtension::UTF8ToASCII` | C4US | 🧩 SARMALAYICI | `size` |
| `StringExtension::ASCIIToUTF8` | C4US | 🧩 SARMALAYICI | `size` |
| `StringExtension::UTF8ToASCII` | C4US | 🧩 SARMALAYICI | `size` |
| `TAbstractSingleton::TAbstractSingleton` | C4US | ❌ YOK |  |
| `TAbstractSingleton::TAbstractSingleton` | C4US | ❌ YOK |  |
| `TAbstractSingleton::GetSingleton` | C4US | ✅ OYUNDA | `client: EterPack/EterPack.cpp:47` |
| `UID::UID` | C4US | ❌ YOK |  |
| `UID::singleton` | C4US | ❌ YOK |  |
| `VEHHook::Hook` | C4US | ❌ YOK |  |
| `VEHHook::Unhook` | C4US | ❌ YOK |  |
| `VEHHook::VEHHandler` | C4US | ❌ YOK |  |
| `VEHHook::AreInSamePage` | C4US | ❌ YOK |  |
| `VFuncSwapHook` | C4US | ❌ YOK |  |
| `m_userOrigMap` | C4US | ❌ YOK |  |
| `VFuncSwapHook::hook` | C4US | ❌ YOK |  |
| `VFuncSwapHook::unHook` | C4US | ❌ YOK |  |
| `VFuncSwapHook::countVFuncs` | C4US | ❌ YOK |  |
| `VTableSwapHook` | C4US | ❌ YOK |  |
| `VTableSwapHook` | C4US | ❌ YOK |  |
| `m_origVFuncs` | C4US | ❌ YOK |  |
| `VTableSwapHook::hook` | C4US | 🧩 SARMALAYICI | `reset` |
| `VTableSwapHook::unHook` | C4US | 🧩 SARMALAYICI | `reset` |
| `VTableSwapHook::countVFuncs` | C4US | ❌ YOK |  |
| `VTableSwapHook::getOriginals` | C4US | ❌ YOK |  |
| `Visuals::OnStart` | C4US | ❌ YOK |  |
| `Visuals::OnStop` | C4US | ✅ OYUNDA | `client: UserInterface/PythonPlayerEventHandler.cpp:88` |
| `Visuals::OnUpdate` | C4US | ❌ YOK |  |
| `Visuals::OnRender` | C4US | ❌ YOK |  |
| `Visuals::OnTab1` | C4US | ❌ YOK |  |
| `Visuals::OnTab2` | C4US | ❌ YOK |  |
| `Visuals::OnTabs` | C4US | ❌ YOK |  |
| `Visuals::OnMenu` | C4US | ❌ YOK |  |
| `dsf75sddc5s4d65c` | C4US | ❌ YOK |  |
| `ErrorTranslator` | C4US | ❌ YOK |  |
| `NewSleep` | C4US | ❌ YOK |  |
| `threadHookCheck` | C4US | ❌ YOK |  |
| `Initialize` | C4US | ❌ YOK |  |
| `LM_CreateFakeThread` | C4US | ❌ YOK |  |
| `DllMain` | C4US | ❌ YOK |  |
| `SYSCALL` | C4US | ❌ YOK |  |
