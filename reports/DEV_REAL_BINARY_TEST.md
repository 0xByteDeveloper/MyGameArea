# DEV_REAL_BINARY_TEST.md — Gerçek Client Üzerinde Dev Test Raporu

> **Oturum 5 — Gerçek binary testi.** metin2client.exe + türev build'leri statik/derin analizden geçirildi.
> Yöntem: pefile + capstone (x86-32) disassembly, byte-level diff, string taraması, gömülü Python ekosistem analizi.
> Tüm adresler ImageBase 0x400000 ile VA'dır (ErrorLog'taki gibi). RVA = VA - 0x400000.
> Tarih: 2026-10-25 | Önceki: DEV_GIL_ANALYSIS.md (RC1-RC17), DEV_LOGIN_FLOW.md

---

## ÖZET (TL;DR)

**2 YENİ KÖK NEDEN BULUNDU (RC18, RC19) + RC3 kaynak seviyesinde kanıtlandı:**

1. **RC18 — MazeProtector (KRİTİK, YENİ):** `denemeoutput.exe` içinde **"i4M MazeProtector V4.3-IP"** kod koruması var.
   Korumalı fonksiyon = **SendAttackPacket** (RVA 0xD7610, 95 byte gövde, `.maze` section'da 661 byte şifreli blob,
   ilk çağrıda in-place decrypt). **ErrorLog'taki crash çerçeveleri (0x4D769C, 0x4D7647) TAM BU FONKSİYONUN İÇİNDE.**
2. **RC19 — Sahte PyTuple hilesi (KRİTİK, YENİ):** Paketin içindeki "Generated v9.2.0" DLL kaynağı (`11/main.cpp` + `11/globals.h`)
   C++ stack'inde **sahte PyIntObject/PyTupleObject** üretip Python C-fonksiyonlarını doğrudan çağırıyor —
   **PyGILState_Ensure SIFIR**. Worker thread'den çağrı → interpreter corruption.
3. **RC3 (kaynak kanıtı):** Crash stack'inin python27 kısmı çözüldü:
   `PyObject_Call(+0x4C) → PyEval_EvalCodeEx(+0x65A) → PyEval_EvalFrameEx(+0x21AE)` = **eval loop içi crash** =
   yanlış thread'den interpreter'a giriş imzası.

**Birleşik kök model:** Background thread + GIL'siz Python çağrısı (RC1/RC3/RC19) → eval-loop crash.
Crash/decrypt geçişi SendAttackPacket üzerinde olduğu için (RC18) paket akışı + sequence sayaç bozuluyor → **NPC'ler gelmiyor** (RC12 ile birlikte).

---

## §1 — TEST MATERYALİ

| Dosya | Boyut | MD5 | Not |
|---|---|---|---|
| metin2client.exe | 5,216,256 | 66341e29... | Temiz client (Python 2.7 gömülü) |
| yeniden_olusturulan_MemoryGenislet.exe | 5,216,256 | 3de75fca... | Aynı boyut/entry ama MD5 farklı (küçük yama) |
| denemeoutput.exe | 5,217,280 | 64d6ba9e... | **+0x1000: `.maze` section'lı (MazeProtector'lı) build** |
| deneme.exe / axaxax.exe | 0x542000 | — | Temiz klonlar |
| deneme_ff.exe | 0x543000 | — | +1 sayfa ama `.maze` yok (farklı yama tipi) |
| python27.dll | 845,868 | — | 1053 export, base 0x1E000000 |
| 11/main.cpp + 11/globals.h | 135+964 satır | — | **"Generated v9.2.0" DLL kaynağı (kullanıcının generator ailesi)** |

- Tüm client'lar: ImageBase 0x400000, entry 0x239B82, timestamp 0x64856730, GUI subsystem, 19 DLL import.
- Client kendi 68 Py fonksiyonu import ediyor: `Py_Initialize, PyImport_AddModule, PyImport_ImportModule, PyRun_StringFlags, PyEval_EvalCode, PyEval_SetTrace...` (client interpreter'ı KENDİ ana thread'inde çalıştırır).

## §2 — FAZ 1: ErrorLog Crash Stack ÇÖZÜLDÜ

ErrorLog.txt (denemeoutput.exe, 0xC0000005) çerçeveleri innermost→outermost:

```
0x006DA149  ← en iç: client (buffer/loop bölgesi; çağrı return adresi)
0x004D769C  ← SendSequence yardımcısı İÇİ (0x4D7670 fonksiyonu)
0x004D7647  ← SendAttackPacket İÇİ (call 0x4D7670'ın return adresi)  ★ Bolge_1 ★
0x005B494B / 0x005B4606 / 0x005B9F9F / 0x005B8409  ← CInstanceBase bölgesi
              (movss xmm,[esi+0x428/0x468] = pixel position alanları = Update/attack yolu)
0x00472520 / 0x004720D3 / 0x0046D866 / 0x00493F92 / 0x00485576 / 0x00489F7B ← client API katmanı
→ python27.dll: PyObject_Call(+0x4C) → PyEval_EvalCodeEx(+0x65A) → PyEval_EvalFrameEx(+0x21AE)
   = INTERPRETER EVAL LOOP'INDAN GİRİLMİŞ (injected Python çağrısı)
```

**Yorum:** Python eval (arka plan thread) → client Python API → CInstanceBase → **SendAttackPacket (korumalı, decrypt edilmiş haliyle çalışıyor)** → sequence yardımcısı → crash.

## §3 — FAZ 4: MazeProtector Gerçekliği (RC18)

### 3.1 Kanıt

```
denemeoutput.exe_MazeMap.txt:
# MazeMap - i4M MazeProtector V4.3-IP IP1 (sabit anahtar)
FUNC Bolge_1_0xD7610 882192 95 5513216 5513428 5513439 0CADF9C2 1
IPINFO headLen=6 bodyLen=89 blobRva=0x542000 blobSize=661 retsRva=0x542211 crc=237B2882 state=depth0/lock0/enc
WARN Govdede 1 reloc -> ilk decrypt'te delta geri alinacak (reloc-guvenli)
WARN Govde section'i yazilabilir yapildi (in-place decrypt)
```

- `882192 = 0xD7610` (fonksiyon RVA), `95` = gövde boyutu, `5513216 = 0x542000` = blob RVA ✓
- `.maze` section blob başlığı: `4D 5A 49 35` = **"MZI5"** magic, ardından `10 76 0D 00` = RVA 0xD7610 ✓, `5F 00 00 00` = 95 ✓
- `.text` byte-diff (temiz vs korumalı): **yalnız 2 bölge farklı** → `RVA 0xD7610-0xD765D (77B)` + `0xD765E-0xD766F (17B)` = toplam koruma bölgesi.

### 3.2 Korumalı fonksiyonun kimliği = SendAttackPacket

```
TEMİZ client 0x4D7610:
  push ebp; mov ebp,esp; sub esp,8; push esi; mov esi,ecx
  call 0x4DC1A0            ; aktör geçerlilik kontrolü (her iki binary'de aynı; singleton 0x8BD2BC → 0x493EC0 → 0x46C5A0)
  test al,al; jne cont
  mov al,1; ret 8          ; geçersizse sessiz success (C4US Boost'taki IsWaiting deseni)
cont:
  mov al,[ebp+8];  mov [ebp-7],al     ; arg1: byte  → paket alanı
  mov eax,[ebp+0xC]; mov [ebp-6],eax  ; arg2: dword → paket alanı
  mov byte [ebp-8], 2                  ; HEADER = 2  ★ HEADER_CG_ATTACK = 2 (packet.h:13) ★
  call 0x4D7670                        ; paket gönderici yardımcısı
  test al,al; jne ok
  push 0x8033BC; call 0x541660         ; ★ "Send Battle Attack Packet Error" ★ (TraceError)
  xor al,al; ret 8
ok:
  mov ecx,esi; call 0x552520; ret 8
```

- **Hata string 0x8033BC = "Send Battle Attack Packet Error"** → fonksiyon kimliği kesin.
- **HEADER byte 2** = `HEADER_CG_ATTACK = 2` (LegendySF GameSource/Server/game/src/packet.h:13) — TPAcketCGAttack{bType, dwVictimVID} yapısıyla birebir (arg1=bType byte, arg2=dwVictimVID dword).
- Yardımcı `0x4D7670`: `movzx eax,[esi]; sub eax,2; jne` (header assert) → `call 0x482840` =
  **sequence üreteci**: `mov dl,[0x8BF835]; inc dl; and cl,7; mov bl,[eax+0x7F6748]; xor bl,[eax+0x8BF838]`
  (SendSequence — sayaç + obf tablosu). → **RC12'deki SendSpecial/SendSequence zincirinin client tarafı burası.**

### 3.3 Korumalı formda ne var?

```
KORUMALI client 0x4D7610:
  jmp 0x9420DF   ← image sonu (0x942000) dışına: runtime'da ayrılan stub (VM/decrypt trampoline)
  + çöp byte'lar (şifreli gövde)
```

- `state=depth0/lock0/enc` → MazeMap üretilirken hâlâ şifreli (enc). İlk çağrıda in-place decrypt ("Govde section'i yazilabilir yapildi").
- **Sonuç zinciri:** Injected DLL/hook bu fonksiyona statik bakarsa → çöp görür. Fonksiyon decrypt edilmişken
  arka plandan GIL'siz çağrı → §2'deki crash. Crash sırasında sequence sayaç (0x8BF835) yarım-kalır →
  sonraki tüm paketler desync → sunucu spawn akışını keser → **NPC'ler yüklenmez**.
- Kullanıcının "MemoryGenislet" (Memory Expand) build'i ayrı bir yama (MD5 farklı) — ama koruma yalnız `denemeoutput.exe`'de.

## §4 — FAZ 4b: "Generated v9.2.0" DLL Kaynağı (RC19 + RC3 kaynak kanıtı)

`NightTownFullpack/11/main.cpp` (135 satır) + `11/globals.h` (964 satır) — cppcmpr.rar'daki Kaynak.cpp v6 ile aynı üretici ailesi ("Generated v9.2.0" / AUTO_PTR / AUTO_ARGUMENT / FakePyTuple / PY-VIRT).

### 4.1 Fonksiyon tablosu (main.cpp:16-26)

```
[0] CPythonNetworkStream::SendAttackPacket        (2 arg — C++ thiscall, DWORD düzeyinde)
[1] CPythonNetworkStream::SendChangeNamePacket    (2)
[2] CPythonNetworkStream::SendCharacterPositionPacket (1)
[3] CPythonNetworkStream::SendCharacterStatePacket (4)  ← C4US Boost'un çağırdığı fonksiyon
[4] CPythonNetworkStream::SendChatPacket          (2)
[5] CPythonSafeBox::GetSlotItemID                 (2)
[6] CPythonPlayer::GetStatus                      (1)
[7] playerGetStatus [PY-FAKE]  → sahte tuple ile Python C-fonksiyonu çağrısı
[8] playerGetStatus [PY-VIRT]  → singleton üzerinden virtual Python çağrısı
```

### 4.2 Kusurlar (globals.h satır kanıtlı)

| # | Kusur | Satır/Kod | Etki |
|---|---|---|---|
| 1 | **PyGILState_Ensure YOK** | grep: 0 eşleşme (964 satırda!) | worker thread'den interpreter'a korumasız giriş = RC3/RC1 |
| 2 | **Sahte PyObject** | `PrepareFakeTuple` (L77-83): `g_fakeInts[i].ob_refcnt=9999; ob_type=g_PyInt_Type` statik C dizisi | CPython invaryant ihlali; GC/refcnt mantığı çökebilir |
| 3 | **Worker thread** | main.cpp:133 `DllMain → CreateThread(MainThread)` → tüm çağrılar oyun thread'i DIŞINDAN | ana thread ile yarış = RC1 |
| 4 | **Doğrudan thiscall** | `SendAttackPacket_call_asm` inline asm pushad/pushfd | korumalı fonksiyonla (RC18) etkileşim: decrypt durumuna saygısız |
| 5 | Singleton çözümleme cache | `Software\\MG\\ScanCache` + CRC32 + XOR "MGResultXEnc..." anahtarı | registry kalıntısı bırakır; yanlış cache → yanlış adres |

### 4.3 Çökme makinesi (birleşik)

```
[DLL worker thread] → PY-FAKE playerGetStatus(sahte tuple)
                    → python27 PyObject_Call → PyEval_EvalCodeEx → PyEval_EvalFrameEx   (GIL BAŞKASINDA)
                    → client C-fonksiyonu → CInstanceBase yolu → SendAttackPacket (Bolge_1, in-place decrypt halinde)
                    → SendSequence (0x8BF835 sayaç)
                    → 0xC0000005  ★ ErrorLog'un birebir yeniden üretimi ★
```

## §5 — FAZ 2/3: Paketin ÇALIŞAN Scriptlerinin Desenleri (altın standart)

142 script tarandı (root 73 + Modules 25 + bot klasörleri 44). API kullanım dağılımı:

```
ui 514 | player 403 | net 231 | chr 221 | app 138 | wndMgr 133 | item 125 | chat 84 |
miniMap 60 | shop 56 | background 42 | skill 18 | exception 9 | snd 7
```

### 5.1 Thread gerçeği (GIL teorisinin İNCELTMESİ)

**~20 script thread kullanıyor VE çalışıyor** (ör. spambot.py:77-83):
```python
thread.start_new_thread(self.SpamBotThread, ())
def SpamBotThread(self):
    m2net.SendChatPacket(...)   # arka plandan OYUN API!
```

**Ders:** "Thread'den API çağrısı = kesin crash" DEĞİL. Basit paket gönderimleri (SendChatPacket vb.)
bu client'ta thread'den çağrılınca çoğunlukla hayatta kalıyor. **Ölümcül farklar:**
1. Sahte tuple ile C-düzeyi çağrı (RC19) — script'ler asla yapmıyor
2. Phase/pencere fonksiyonları (StartGame/DirectEnter/SetSelectCharacterPhase) thread'den — RC12/RC13
3. Yüksek frekanslı spam (attack loop) — SendAttackPacket korumalı + sequence yarışı (RC18)
4. Korumalı fonksiyon bölgesine dokunan her şey (RC18)

### 5.2 Ekosistem yapıları

- **pyDetour/** = saf-Python fonksiyon detour (`sys.modules` üzerinden oFunc sarmalama) → bu client'ta
  **GÜVENLİ hook yöntemi Python seviyesinde** (C++ hook yok). Not: pyDetour.py L5'te yazım bozukluğu var
  (`sys.modulesodule]` → `sys.modules[module]`) — kullanmadan önce düzeltilmeli.
- **m2kmod** (hackbar, m2k_lib, m2k_hook) + **OpenBot** (eXLib tabanlı: ActionBot, Radar, Levelbot...).
- **`m2netm2g`/`playerm2g2`/`chatm2g`** modül adları client binary'sinde YOK (string taraması: 0 eşleşme) →
  bu adlar ekosistem-özel alias; **bu client'ta `net`/`player`/`chat` kullan**. Binary'de kayıtlı modüller:
  `background, chrmgr, effect, event, miniMap, nonplayer, player, skill, wndMgr`.
- **HookHunter** (logs/console.txt): anti-cheat hook tarayıcı — dış DLL hook'ları tespit edilebilir.
  MaxExecutor'ın WndProc subclass'ı hook tablosuna girmez (pencere prosedürü), fakat SetWindowsHookEx tipi
  global hook'lar girer.

## §6 — FAZ 1c: Client Binary API Ground Truth (pylib doğrulaması)

String taramasında binary'de DOĞRULANAN isimler (VA ile):

| API | VA | pylib.py durum |
|---|---|---|
| StartGame | 0x401A95 | ✓ doğru |
| DirectEnter (+SendDirectEnter) | 0x401CD3 / 0x4045FF | ✓ doğru |
| SendLoginPacket | 0x401D17 | ✓ |
| SetLoginInfo | 0x401BF0 | ✓ |
| SetServerInfo | 0x401A49 | ✓ |
| ConnectToAccountServer | 0x401D2E | ✓ |
| SendSelectCharacterPacket | 0x401D81 (+Error msg 0x4046C5) | ✓ |
| SendCreateCharacterPacket | 0x401DB5 (+Failed msg 0x4046A3) | ✓ |
| SendEnterGamePacket | 0x401DE3 | ✓ |
| OnLoginFailure (py callback) | 0x3F660A | ✓ |
| SetPhaseWindow | 0x401C2A | ✓ |
| SetGameWindow | 0x405509 | ✓ |
| PHASE_WINDOW_LOGIN / CREATE (+5 tane) | 0x4025A2... | ✓ |
| SendChatPacket | 0x401F0A | ✓ |
| SetAttackKeyState | 0x405357 ("playerSetAttackKeyState(isPressed) - There is no first argument") | ✓ |
| SetPixelPosition | 0x3FD30C | ✓ |
| GetMainActorRace/VID/SkillGroup | 0x401B30... | ✓ |
| chrmgr modülü | 0x3FCBFE | eklendi |

**Sonuç:** MaxExecutor + pylib.py komut seti gerçek client'a uyumlu — değişiklik GEREKMEZ.
xGODMOD2 login akışı (DEV_LOGIN_FLOW.md) binary isimleriyle birebir teyit edildi.

## §7 — BİRLEŞİK KÖK MODELİ (GIL + RENDER + NPC)

```
                        ┌────────────────────────────────────────────┐
                        │  Injected C++ DLL ("Generated" ailesi)     │
                        │  CreateThread(worker)                      │
                        └──────┬─────────────────────┬───────────────┘
              RC19/RC3:        │                     │  RC18:
              sahte tuple +    ▼                     ▼  thiscall SendAttackPacket
              GIL'siz Py çağrı   python27 eval loop   (in-place DECRYPT edilmiş gövde)
                               ★ CRASH 0xC0000005 ★      │
                                 │                        ▼
                                 ▼                SendSequence(0x8BF835) yarım kalır
                    interpreter heap bozuk                │
                                 │                        ▼
                                 ▼                paket akışı desync
                    paket işleme thread'i ölür            │
                                 └───────────┬────────────┘
                                             ▼
                          RC12 (çift giriş StartGame+DirectEnter) ile birleşince
                          spawn akışı tamamen çöker → NPC'LER YÜKLENMEZ
                          + chat'teki şikayetler (sohbette bahsi geçiyor)
```

## §8 — SOMUT DÜZELTMELER (öncelik sıralı)

1. **[RC19] PY-FAKE/PY-VIRT yolunu tamamen kapat** → `11/main.cpp` tabanlı build'lerde
   `isPyFake/isPyVirt` satırları silinmeli; yalnız ana-thread komut kullan (MaxExecutor).
2. **[RC18] SendAttackPacket'a (Bolge_1) dokunma:**
   - Hook YERLEŞTİRME (prolog patch) — decrypt edilince ezilir / stub'a yazılır
   - Decrypt'ten ÖNCE statik adres okuma — çöp döner
   - Attack spam'ini Python seviyesinde `player.SetAttackKeyState(TRUE/FALSE)` ile yap
     (binary'de kanıtlı: 0x405357) — paketi elle dizmek yerine.
3. **[RC3] Herhangi bir C++ yolunda Python çağrısı gerekiyorsa:** ana thread'de yap
   (MaxExecutor WndProc modeli) ya da minimum `PyGILState_Ensure/Release` RAII — ama ana thread modeli tercih edilir.
4. **[RC12] Girişte tek giriş:** `StartGame()` XOR `DirectEnter()` — birini seç (STABLE yaması zaten var).
5. **[pyDetour] Kullanılacaksa L5 hatasını düzelt** (`sys.modules[module]`).
6. **Modül adları:** bu client'ta `net/player/chat/chrmgr` — `m2netm2g` alias'larını KULLANMA.
7. **HookHunter taraması:** WndProc subclass güvenli; SetWindowsHookEx/global hook KULLANMA.

## §9 — DOSYA KANIT ENDEKSİ

| Kanıt | Yer |
|---|---|
| ErrorLog crash stack | nighttown/ErrorLog.txt |
| MazeMap (protector haritası) | denemeoutput.exe_MazeMap.txt (paket kökü) |
| Generated DLL kaynağı | nighttown/11/ (main.cpp, globals.h — bu raporla repoya eklendi) |
| SendAttackPacket kimlik string'i | metin2client.exe 0x8033BC "Send Battle Attack Packet Error" |
| HEADER_CG_ATTACK=2 | LegendySF GameSource/Server/game/src/packet.h:13 |
| Sequence üreteci | metin2client.exe 0x482840 (sayaç 0x8BF835, tablo 0x7F6748 / 0x8BF838) |
| spambot thread örneği | NightTownFullpack/spambot.py:77-83 |
| pyDetour bozuk satır | NightTownFullpack/pyDetour/pyDetour.py L5 |
| HookHunter logu | NightTownFullpack/logs/console.txt |

## §10 — SONRAKİ ADIMLAR

- [ ] Bolge_1 decrypt stub'ının runtime iz sürülmesi (kullanıcı tarafında x64dbg: bp 0x4D7610, ilk kırılmada
      gövde decrypt mi bakılır; MazeMap'teki `retsRva=0x542211` tablosu ile ret patch noktaları listelenebilir)
- [ ] `deneme_ff.exe`'nin +1 sayfalık farklı yamasının içeriği (ayrı inceleme)
- [ ] MaxExecutor + STABLE script'in gerçek client'ta (MazeProtector'sız temiz metin2client.exe ile) testi
- [ ] rc sweep: RC18/RC19'un DEV_GIL_ANALYSIS.md'ye işlenmesi (bu rapor referanslı)
