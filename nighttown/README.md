# NightTownFullpack — Envanter & İlk Bulgular

**Kaynak:** Google Drive `1JaxWFkMID_7e9929_--yk20a7PqJ-aZE` (NightTownFullpack.rar, 1.1G)
**İndirme yöntemi:** `drive.usercontent.google.com/download?id=...&export=download&confirm=t&uuid=...`
(gdown rate-limit'e takıldı; doğrudan URL + virus-scan form parametreleri + HTTP 206 resume ile indirildi — 1,198,166,225 byte, RAR5 imzası doğrulandı)
**TAM arşiv GitHub limiti (100MB/dosya) nedeniyle repoya konulamadı** → yerelde `/home/z/my-project/game/NightTownFullpack/` (2908 öğe, açılmış hali 1.57GB)

## Kritik EXE'ler (nighttown/exes/)

| Dosya | Boyut | Not |
|---|---|---|
| metin2client.exe | 5,216,256 | Oyun istemcisi (ana hedef) |
| yeniden_olusturulan_MemoryGenislet.exe | 5,216,256 | **metin2client.exe ile BİREBİR AYNI BOYUT** → client'in yeniden derlenmiş/yamalı MemoryGenislet versiyonu |
| metin2client.exe_dump.exe | 193,868 | Dump ürünü küçük stub |
| python27.dll | 845,868 | **Client Python 2.7 gömülü** (crash log'unda stack'te görünüyor) |

## GIL/Crash Kanıtı (ErrorLog.txt)

```
Module: denemeoutput.exe   Exception: 0xc0000005 (access violation)
Stack: denemeoutput.exe (13 frame) → python27.dll (6 frame: 0x1e0eb707, 0x1e0ed98e, 0x1e0ee8fa, 0x1e09c601, 0x1e07a7dc, 0x1e086420)
```

- `denemeoutput.exe` = kullanıcının "test output" build'i
- Çökme **python27.dll içinden gelen çağrılarda** → arka plan thread'den interpreter'a girişin (Py_Initialize/PyRun sonra) crash ürettiği hipotezini DOĞRULUYOR
- DEV_GIL_ANALYSIS.md RC1 (arka-plan-thread API → GIL) bulgusuyla uyumlu; adresler Rust/IDA ile eşlenebilir (timestamp 0x64856730)

## Klasör Dagiımı (tam paket)

| Klasör | Boyut | GitHub'da? |
|---|---|---|
| pack/ | 1.3G | HAYIR (oyun kaynakları) |
| BGM/ | 77M | HAYIR |
| screenshot/, dmg/, mark/, miles/ | ~45M | HAYIR |
| **root *.py (73 script)** | 1.8M | EVET → scripts_root/ |
| **Modules/ (Bot modülleri)** | 940K | EVET |
| **OpenBot/, m2kmod/, HyperBot/, pyDetour/** | ~2.7M | EVET |
| **lib/ (py27 stdlib + accounts)** | 924K | EVET (accounts.save dahil) |
| Images/, upload/, Saves/, logs/ | seçmeli | logs/console.txt + ErrorLog.txt alındı |

## Script Envanteri (scripts_root/ — 73 dosya)

Bot ailesi: `123klo-fishbot.py`, `123klo-multihack.py`, `Fishbot.py`, `Fishbot - DaRealFreak.py`, `New Levelbot.py`, `Crap Levelbot.py`, `Questbot.py`, `Pickup.py`, `Instantpickup.py`
Hack ailesi: `zoomhack.py`, `vbmultihack.py`, `Teleporthack - Music.py`, `WalkToMobs.py`, `MetinFinder.py`, `vidscanner.py`, `yangbug.py`, `AntiFly.py`
Yardımcı: `WhisperSpammer.py`, `IngameCommands.py`, `ItemUse.py`, `DT Upper.py`, `Exp Donator.py`, `uisidebar.py`, `FileExtractor.py`, `ForButton.py`, `Bot-Settings.txt`

Modules/ bot modülleri: Alchemist, Bookreader, Buffbot, EQChanger, Fishbot, General, Info, Inventorymanager, Itemcreator, Itemstealer (+.pyc derlenmiş)

## Anti-Cheat / Hook İzleri

- `logs/console.txt`: **HookHunter** başlatılmış (2023-05-26), "Unable to open a handle to process 0" → hook taraması sistem seviyesinde çalışıyor
- `pyDetour/` = Python-side detour/hook kütüphanesi (hackme.py içerir)
- `RebirthGuard.log` = sunucu koruma modülü logu (kök dizinde)
- `mp_enc_v411/v412/v46_32.exe` = pack encoder versiyonları (pack yeniden paketleme yapılmış)

## xgodmod3 Bağlantısı

1. MaximumPyScript1.rar'daki kronolojide en yeni scriptler bu paketle aynı ekosistemde (deneme*.exe, target.exe, byteeklemekicindenemetestalani.exe vb. test build'leri burada)
2. ErrorLog stack'i → RC1 root-cause (GIL / yanlış thread'den interpreter erişimi) kanıtını güçlendiriyor
3. pyDetour + HookHunter karşılaştırması → hook tespiti mekanizması ayrıca incelenecek
4. lib/accounts.save → oyun içi hesap yapısı (executor giriş otomasyonu için kullanılabilir)
