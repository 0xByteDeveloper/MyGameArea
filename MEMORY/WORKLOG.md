# WORKLOG — Append-Only Oturum Günlüğü

> KURAL: Her oturum / her büyük adım buraya EKLENİR (asla üstüne yazılmaz). En yeni en altta.

---

## Oturum 1-2 (özet — önceki sandbox'lardan)

- HyperBot-Nerwia2 indirildi, tarandı → FULL_System.json → push (commit 72acae2)
- C4USMultiHack-Metin2 indirildi, tarandı → FULL_System_A1.json → push (commit 6392709)
- DEV_MVP_WEB.json üretildi (1.34 MB, 1350 fonksiyon) → push edildi
- Kullanıcı geri bildirimi: "basit yapmışsın, ben senden hardcode istedim" → JSON iptal, BÜYÜK MD formatına geçildi
- LegendySF-V2 klonlandı, LegendySF index kuruldu (15.312 def, 1.232 typedef, 59 server handler)

---

## Oturum 3 — GOD MOD (2026-10-25)

### Adım 3.1 — Bağ yeniden kurulumu
- Sandbox yeniden kurulmuş: LegendySF-V2 yeniden klonlandı (73.679 dosya), MyGameArea pull'landı.
- Rar'lar açıldı → /home/z/my-project/extracted/ (win32apiMetin2Py, cppcmpr, MaximumPyScript1 = 77 dosya)
- Oyun indirimi başlatıldı (Google Drive 1.20 GB → metin2_game.bin)

### Adım 3.2 — Paralel derin araştırma (2 agent)
- **Agent A (script/GIL):** 77 script kronolojik dizildi, 17 kök neden (RC1-RC17) dosya:satır kanıtlı bulundu. Kritik: RC12 çift-giriş (StartGame+DirectEnter) = NPC yüklenmeme; RC1 background-thread API çağrıları = GIL.
- **Agent B (LegendySF login):** login→select→empire→create→enter zinciri uçtan uca dosya:satır+packet struct+server handler ile çözüldü. 5 slot, MAIN_RACE 0-8, hata kodları, 30sn cooldown, versiyon kontrolü, CRC yalnız PHASE_SELECT'te kurulur (login'e etkisiz).

### Adım 3.3 — Hafıza yapısı kuruldu
- MEMORY/GOD_MOD_MAP.md + uploads/ (5 orijinal dosya) repoya eklendi, push edildi.

### Adım 3.4 — Raporlar ve kod (BU OTURUMDA ÜRETİLENLER)
- reports/DEV_LOGIN_FLOW.md (xGODMOD2 büyük rapor)
- reports/DEV_GIL_ANALYSIS.md (xgodmod3 büyük rapor)
- MaxExecutor/MaxExecutor.cpp (xgodmod4 — WndProc ana-thread executor, hook yok SHM yok)
- MaxExecutor/pylib.py (komut kütüphanesi, hook yok)
- MaxExecutor/README.md
- MaxExecutor/MaximumPyScript_STABLE.py (v17 cerrahi stabilize: çift-giriş kaldırıldı, recovery gate'lendi)

### Durum
- Oyun indirmesi devam ediyor (arka plan)
- Push'lar: her büyük adımda bir commit

### Adım 3.5 — Üretilen teslimatlar (devam)
- reports/DEV_LOGIN_FLOW.md push (commit 72ddff7): 691 satır, §0-§11 — faz sistemi, handshake, auth+game login, slot tablosu API, empire, create hata dalları, enter-game, anti-cheat, durum makinesi, e2e diyagram, fonksiyon indeksi
- reports/DEV_GIL_ANALYSIS.md push (commit 8b4c27b): 23 sürüm kronolojisi, RC1-RC17 kök nedenler (satır kanıtlı), C++ injection mekanizmaları, log kanıtları
- MaxExecutor/MaxExecutor.cpp: WndProc subclass + dosya kuyruk + ana-thread PyRun_SimpleString; worker Python'a hiç dokunmaz; drain'de max 4 komut + heartbeat
- MaxExecutor/pylib.py: maxlib modülü (login/charlist/empire/create/enter/status) — hooksuz, gc'siz, mainStream yalnız yükleme anında yakalanır
- MaxExecutor/README.md: derleme + kurulum + xGODMOD2 akış komut eşlemesi
- MaxExecutor/MaximumPyScript_STABLE.py: v17 + 3 cerrahi yama (RC12 tek-giriş, RC13 recovery kilidi, RC14 GameWindow kanıtı) — scripts/patch_stable.py anchor-doğrulamalı uyguladı, tüm kontroller OK
- Google Drive indirme: rate-limit; yavaş retry döngüsü arka planda (scripts/download_retry_slow.sh)

---

## Oturum 4 — NightTownFullpack İndirildi + Repo'ya alındı (2026-10-25)

### Adım 4.1 — Kullanıcının verdiği doğrudan URL ile indirme (x3 TAMAMLANDI)
- Kullanıcı URL verdi: `https://drive.usercontent.google.com/download?id=1JaxWFkMID_7e9929_--yk20a7PqJ-aZE&export=download`
- gdown yolunu terk ettik: virus-scan HTML'inden `confirm=t&uuid=...` form parametreleri çekildi
- `curl -C -` resume ile HTTP 206 → kalan 371MB 13.5 sn'de tamamlandı
- **NightTownFullpack.rar = 1,198,166,225 byte, RAR5 imza doğrulandı** → /home/z/my-project/game/
- İlk script'li arka plan denemesi 826MB'da sandbox tarafından öldürüldü → foreground curl ile çözüldü (ders: büyük indirmeler foreground yapılmalı)

### Adım 4.2 — Açma + envanter
- unrar x → 2908 öğe, 1.57GB → /home/z/my-project/game/NightTownFullpack/
- Kritik: metin2client.exe (5,216,256) = yeniden_olusturulan_MemoryGenislet.exe ile aynı boyut (yamalı rebuild)
- python27.dll (845,868) → client Python 2.7 gömülü (bilgi teyit edildi)
- **ErrorLog.txt: denemeoutput.exe 0xc0000005, stack'te 13 exe + 6 python27.dll frame** → RC1 GIL hipotezini güçlendiren GERÇEK crash kanıtı
- logs/console.txt: HookHunter anti-cheat aktif; pyDetour/ = Python detour kütüphanesi
- 73 root script + Modules/ + HyperBot/ + OpenBot/ + m2kmod/ + lib/ + accounts.save

### Adım 4.3 — Repo'ya alma (persistence protokolü)
- nighttown/ oluşturuldu: exes/ + scripts_root/ (73 py) + Modules/ + HyperBot/ + pyDetour/ + m2kmod/ + lib/ + logs/ + ErrorLog.txt + config/
- nighttown/README.md = tam envanter + GIL kanıt analizi + klasör boyut tablosu
- 1.1GB tam rar GitHub 100MB limiti nedeniyle repoya konulamadı (yerelde duruyor) — README'de belirtildi
- GOD_MOD_MAP.md X3 bölümü TAMAMLANDI olarak güncellendi
