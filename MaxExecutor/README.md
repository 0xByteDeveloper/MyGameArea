# MaxExecutor — Ana-Thread Güvenli Python Executor (xgodmod4)

> **v2.7 / pylib v5.2 — UNIVERSAL LOGIN/SELSERVER (28-client GitHub araştırması, tam rapor: RESEARCH.md):** `login <id> <pwd> [3.alan]` — 3-parametreli login (PIN/guard/slot; kalan editline otomatik bulunur+raporlanır, verilirse doldurulur) · `selserver <srv> <ch> [ok]` — ok=0 OK'suz clientlar için; bölge/server/CH listbox + Marty channelButton dict + pw.SetChannel zinciri · `uiprobe` — login ekranı TAM envanteri (mimari + 3. alan + argüman önerisi → last_uiprobe.txt) · `relogin [id pwd [srv ch]]` + `relogin quick [slot]` — v2.3'te kaldırılan relogin'in universal dönüşü (TAM: logout→disconnect→login akışı; HIZLI: logout→selchar; state-machine DLL 150ms nabziyle) · 5 mimari desteklenir: resmi 2014 (14/28 dump) + Marty 5.3 gömülü + authSocket eski katman + çoklu-hesap container + PIN'li · pylib_embedded.h v5.2 yeniden üretildi. **NOT: paketteki MaxExecutor.dll v2.6 derlemesi — 3. parametre/relogin için v2.7 kaynak kodu derlenmeli (§3).**
>
> **v2.6 / pylib v5.0** — saha testi 16: **`slots` ÇOK-HÜCRELİ EŞYA** (`item.GetItemSize` ile w×h — kaplanan HÜCRE sayılır, oyunun göstergesiyle AYNI; harita 5 slot/satır, `o`=eşya-devamı) · `sellall`/`selljunk` **v5.0**: IsOpen-flicker kök nedeni kapandı (cur korunur — v4.9'da sonsuz faz ping-pongu '5 dk sonra tekrar satmaya çalışıyor'ydu) + **KARA LİSTE** (2 turda satılmayan bir daha denenmez, SATILAMAYANLAR isim+boyut listesiyle rapor) + **120sn hard limit** + **dükkan otomatik kapanır** (`SendShopEndPacket`) · `dropall` **v5.0**: aynı kara liste (3 tur) + ATILAMAYANLAR isim listesi + 120sn (sunucu paketleri yavaş işlerse eşyalar sonra tek tek düşer — normal) · **v5.1:** oto-pot (hp/mp) komutları paketten **KALDIRILDI**. Detay: KULLANIM.md üst bölümü.
>
> **v2.5 / pylib v4.9** — saha testi 15: **150ms hızlı nabız** (DLL her 150ms'de `maxlib._tick()` — döngüler ÇİFT KALP: DLL timer + ui penceresi; '1 tane sat/at sonra susma' kökten bitti) · `sellall`/`selljunk`/`dropall` **BURST** (45 slot/nabız — m2k kanıtı; 90 slot ~0.3sn + doğrulama turları) · `otp2` **IŞINLANA-IŞINLANA + ADIM** (SetPixelPosition sıçraması + MoveToDestPosition + 1-kare UP + SendCharacterPositionPacket → sendcharacterstate tetiklenir, geri atma yok) · `otp delay/step/stop` alt-komutları ('otp delay 1' ValueError bitti). Detay: KULLANIM.md üst bölümü.
>
> **v2.4 / pylib v4.8** — saha testi 14: `otp2` W+UP tuşu SÜREKLİ BASILI gerçek yürüyüş (SetRotation hedefe, sıçrama yok, varınca otomatik bırakır) · `slots` sayım düzeltmesi (TOPLAM = sekme×boyu = 90 + slot haritası `#=esya .=bos E=efsunlu`) · `selljunk`/`sellall` 1-arg kanıtlı satış paketi + sessiz dükkan bekleme + DURDUR (`selljunk 0`) · `dropall` 1-arg kanıtlı atma paketi + DURDUR (`dropall 0`) · [LIVE] spam bitti. Detay: KULLANIM.md üst bölümü.

> **v2.3 / pylib v4.7** — saha testi 13: speed/aspeed + chchange/relogin KALDIRILDI · warp LEGENDY yolu (sahne yeniden yüklenir) · otp1/otp2 ayrımı · slots/selljunk/sellall/dropall · dump C-modül API-stub + pack.Get sysmodules yolu. Detay: KULLANIM.md üst bölümü.

> **v2.2 / pylib v4.6** — saha testi 12: yeni komutlar (warp/antistun/antislow/combo/statdown/skillupui/statupui/efsun) + near metin-taşı fixi + speed döngüsü + antifly saldırısız + chchange SetLoginPhase yolu. Detay: KULLANIM.md üst bölümü.

> **v2.1 / pylib v4.5** — saha testi 11 kök-neden onarımı: v4.4'ün `ui_WindowBase` sıra hatası yüzünden HİÇ yüklenemeyip eski v3.2'ye sessizce düştüğü (`PYTHON HATASI` ailesi) düzeltildi; BootImport oturum-başına-1-kez + başarısızlık traceback'i `results\last_pylib_fail.txt`'ye yazıyor. Detay: KULLANIM.md üst bölümü.

> **Yöntem:** WndProc subclass + dosya kuyruk + ana-thread `PyRun_SimpleString`
> **Hook:** YOK · **Shared memory:** YOK · **Arka plan Python thread:** YOK
> **Sürüm:** v2.0 PLUSMAXGOD (pylib v4.4 — saha testi 10: fish temizliği,
> near geniş-tarama, ExitGame relogin/chchange, görsel tazeleme, puan/hız/
> binis/antifly/efsun komut ailesi, konsol çıkış kilidi)

---

## 1. NEDEN BU MİMARİ (kanıt zinciri)

`reports/DEV_GIL_ANALYSIS.md` 17 kök neden buldu; üç belirtinin (GIL hatası, render bozulması, NPC yüklenmeme) ortak kaynağı: **oyun API çağrılarının oyun ana thread'i DIŞINDA çalışması.**

Metin2 client'ın yapısı bunu zorunlu kılar:
- Client'ın gömülü Python'u (2.7) **ana thread'de** çalışır ve GIL'i bırakmaz.
- Bu yüzden **ana thread'de** çalışan her kod (WndProc dahil) Python C-API'lerine dokunduğunda GIL zaten elimizdedir → yarış yok, deadlock yok, heap bozulması yok.
- `CPythonApplication` mesaj pompası standart Windows pump'ıdır → `DispatchMessage` ana thread'de koşar → subclass ettiğimiz WndProc ana thread'de koşar.

| Eski mimari (MaximumPyScript) | MaxExecutor |
|---|---|
| `_thread.start_new_thread` kontrol döngüsü → `net.*`/UI çağrıları arka planda (RC1) | Tüm Python, ana thread'de tek noktadan |
| SHM `Control_<PID>` 16KB binary protokol (senkronsuz) | Dosya kuyruğu `C:\MaxExec\queue\*.cmd` (atomik MoveFile) |
| `gc.get_objects()` taramaları (RC2) | Hiç yok |
| UI `CallEvent` zincirleri (RC9/RC11) | Doğrudan paket glue'ları (`net.*`) |
| `StartGame()` + `DirectEnter()` çift giriş (RC12 → NPC yok) | `enter` komutu = TEK `net.DirectEnter` |
| Loading'de `SetSelectCharacterPhase()` recovery (RC13) | Yok — faz zorlaması hiçbir komutta yok |

## 2. DOSYALAR

| Dosya | Görev |
|---|---|
| `MaxExecutor.cpp` | DLL: konsol + pencere subclass + kuyruk dökücü (WndProc) — v2.7: login 3. argüman + selserver ok argümanı + uiprobe/relogin komutları |
| `PLUSMAXGOD_PyScript.py` | Ana-thread komut kütüphanesi (`maxlib`) **v5.2 UNIVERSAL** — giris (login/selserver/serverlist/uiprobe/relogin) + oyun-ici (stat/inv/tp/chat/...) + kesif (pyfiles/pydumpall/plusquest) |
| `RESEARCH.md` | **v5.2 araştırma raporu**: 28-client GitHub dump analizi — 5 login mimarisi, 3-parametre bulguları, files ailesi matrisi (kaynak linkli) |
| `pylib_embedded.h` | DLL içine gömülü pylib v5.2 kopyası (scripts/embed_pylib.py üretir) |
| `pylib.py` | Eski v3.2 adı — YEDEK yol olarak kabul edilir (BootImport otomatik yükseltir) |
| `MaximumPyScript_STABLE.py` | v17'nin cerrahi stabilize hali (geçiş dönemi için, SHM mimarisiyle — RC12/RC13/RC14 yamalı) |

## 3. DERLEME

1. Visual Studio → New Project → **Visual C++ → Windows Desktop → Dynamic-Link Library (DLL)**, adı `MaxExecutor`.
2. `MaxExecutor.cpp`'yi projeye ekle (önceki otomatik .cpp'yi sil).
3. Configuration: **Release / x86** (metin2client 32-bit ise; 64-bit client varsa x64).
4. Linker → Input: `user32.lib` varsayılan olarak zaten listede (Win32 GUI seti); yoksa ekle.
5. Derle → `MaxExecutor.dll`.

## 4. KURULUM

```
C:\MaxExec\
    PLUSMAXGOD_PyScript.py   <- gerekmez: DLL gömülü kopyayı otomatik yazar/yükseltir
    queue\            <- DLL kendisi açar
    results\          <- DLL kendisi açar
    dump\             <- v1.8: py dump + PLUSQuest_live.txt
```
DLL'i alışkanlık olduran loader'ınla (Kaynak.cpp v6 loader'ın veya mevcut loader'ın) oyuna enjekte et. Konsol açılır.

## 5. KULLANIM — xGODMOD2 akışının komut karşılığı

```
status                                   -> sahne/bağlantı snapshot (sonuc: results\last_status.txt)
                                            (pylib v4.1 otomatik yüklenir; load artık gerekmez)
uiprobe                                  -> v5.2: login ekrani TAM taramasi (mimari + 3. alan raporu)
selserver 0 0                            -> server+CH listbox + OK (resmi 2014 akisi)
                                            (ok=0: selserver 0 0 0 - OK yoksa/bazilmasin)
login <id> <pwd> [3.alan]                -> UI yolu (editline+buton) -> pw.Connect -> paket yolu
waitfor SelectCharacterWindow 30         -> karakter seçim ekranı geldi mi?
relogin [id pwd [srv ch]]                -> v5.2: TAM relogin akisi (tek komut)
relogin quick [slot]                     -> HIZLI: /logout -> selchar (baglanti korunur)
charlist                                 -> 5 slot: isim/level/sınıf/cinsiyet/guild (results\last_charlist.txt)
empire 1|2|3                             -> yalnız 0 karakter varken (Shinsoo=1 Chunjo=2 Jinno=3)
create <slot> <ad> <race> <shape>        -> race 0-8 (0=ErSavaçı 1=KadNinja 2=ErSura 3=KadŞaman
                                            4=KadSavaşçı 5=ErNinja 6=KadSura 7=ErŞaman 8=Wolfman)
                                            shape 0/1; statlar server'dan (JobInitialPoints)
charlist                                 -> 30 sn sonra tekrar: slot doluysa OK (create cooldown 30 sn!)
enter <slot>                             -> TEK net.DirectEnter — asla UI StartGame ile birlikte değil!
waitfor GameWindow 60                    -> oyun içi
```

### Hata takibi (hook'suz)
- Login hatası: client `OnLoginFailure(kod)` gösterir; senin tarafında ekran `LoginWindow`'da kalır + popup. Kod listesi `reports/DEV_LOGIN_FLOW.md` §3d.
- Create hatası: `create` sonrası `charlist` ile slotu yokla. Slot 30 sn sonra hâlâ boş → failure. Sebep ayrımı için UI popup metni ("Bu ismi zaten..." = bType 1, "Karakteri yaratamazsın." = bType 0).

### Beklenen davranış notları
- `waitfor`, bekleme süresince C++ tarafında uyur; Python'u her 700 ms'de bir TEK status snapshot'ıyla uyandırır → ana thread yükleme sırasında asla bloklanmaz.
- WndProc her mesajda en fazla 4 komut dosyası işler; kalan varsa yeniden mesaj atar → render'a nefes payı.
- `alive.txt` heartbeat'i her drain'de güncellenir (ana-thread nabzı).

## 6. BİLİNEN SINIRLAR (v1.0)

- `mainStream` yakalama `__main__` globali ya da `networkmodule` modülünden denenir; bulunamazsa `net.*` komutları çalışmaya devam eder, sadece `status`'un sahne alanı `?` olur.
- ~~UI-path login (`loginButton.CallEvent`) bilinçli olarak EKLENMEDİ~~ — **v5.2 güncellemesi:** login artık ÇOKLU YOLLUDUR: UI (editline+buton aday taraması) → `pw.Connect(id,pwd)` → paket (`stream`/`net`/`authSocket`). 28-client araştırması UI adlarının client'lar arası değiştiğini gösterdi — universal aday taraması bunu çözer.
- Executor hem auth hem oyun sunucusu adımlarını client'ın kendi C++ zincirine bırakır (biz yalnız tetikliyoruz) → handshake/şifreleme/versiyon/ping otomatik doğru.
