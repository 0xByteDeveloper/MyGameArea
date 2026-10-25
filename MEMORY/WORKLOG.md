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
