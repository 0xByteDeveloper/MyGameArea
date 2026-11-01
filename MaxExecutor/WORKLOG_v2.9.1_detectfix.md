# WORKLOG — Oturum 25 (2 Kasım 2026): SAHA RAR ANALİZİ + v2.9.1 DETECT-TAMİRİ
**MaxExecutor v2.9.1 + pylib v5.4 (değişmedi) — "detect kuyruğa yazıldı ama hiç çalışmadı" vakasının 4 kök nedeni ve kalıcı çözümü**

> Kullanıcı mesajı: v2.9 konsol çıktısı + `MaxExec_klasör_resultlar.rar` (C:\MaxExec saha klasörü: queue/, results/, maxexec.log, binary'ler, dok'lar). Konsolda `detect` iki kez yazılmış; her ikisi de "kuyruga yazildi" demiş, çıktı gelmemiş. Ayrıca banner'da tekrarlayan `PYLIB ESI: diskteki PLUSMAXGOD_PyScript.py = v2.x/3.x (isaret yok/eski)` alarmı.

---

## 1. RAR ADLİ ANALİZİ — BULGULAR (kanıt dosyası → bulgu)

| Kanıt | Bulgu |
|---|---|
| `queue/c_692628421_0003.cmd` + `c_692676421_0004.cmd` | İki `detect` komutu **hâlâ kuyrukta** — içeriği sağlam (pylib yükseltme sarmalayıcı + `maxlib.matrix()`), ama **hiç çalıştırılmamışlar** |
| `maxexec.log` 20:30 oturumu | `oyun penceresi 20 sn icinde bulunamadi` — DLL oyuna bağlanamamış; DrainQueue (kuyruk çalıştırıcı) pencere bulununca devreye girdiği için komutlar asla işlenmedi |
| Konsol görüntüsü | `oyun penceresi: BULUNAMADI (hwnd=00000000)` — kullanıcı pencere yokken komut yazmış; eski DLL "kuyruga yazildi" deyip **sessizce yutuyordu** |
| `maxexec.log` v2.7(19:29) / v2.7(19:40) / v2.9(22:47) oturumları | Hepsinde aynı SAHTE alarm: `UYARI: pylib ESI v2.x/3.x (isaret yok/eski)` — oysa `last_pylib_load.txt`: `PLUSMAXGOD_PyScript v5.9 yuklendi (ANA THREAD)` |
| Ölçüm | v5.4 pylib'de `PYLIB_VERSION` işareti **22628. baytta**; eski `ReadPylibVersion` **yalnızca ilk 16KB'yi** okuyordu → sürüm ASLA okunamıyor → sahte alarm |
| `last_pylib_load.txt` + 23:26 `pylib sync: v5.9 diske yazildi` + RAR'daki pylib = v5.4 | Klasörde binary/pylib KARIŞIKLIĞI: kullanıcı sahte alarm yüzünden v5.9'un üstüne v5.4 kopyalamış; log'da v2.5/v2.7/v2.8/v2.9 karışık oturumlar; DllMain log dizgisi bayattı ("v2.5" yazıyordu) |
| `last_error.txt` 19:40:15 | `LOGIN_FAILURE: NOID (Boyle bir hesap yok)` — `login.dat`'taki `admin` hesabı Romania sunucusunda yok (araç hatası değil) |
| `DrainQueue` kodu | Tüm `queue\*.cmd`'yi çalıştırıp SİLER → kuyrukta bekleyen bayat komutlar yeni oturumda pencere bulununca **kendiliğinden çalışacaktı** (bayat `dropall/sellall` sürprizi riski) |

## 2. SAHRA TEŞHİSİ — RAR MATRİS CEVABINI ZATEN İÇERİYOR

`detect` çalışmasa da saha dosyaları sunucunun matrisini KESİN söylüyor:

```
last_serverlist.txt : "01. Romania" (tek server) + CH1..CH4 listbox + serverSelectButton (OK VAR)
last_server.txt     : serverList.SelectItem(0) OK | channelList.SelectItem(0) OK | serverSelectButton.CallEvent() OK
last_login.txt      : UI yolu OK (idEditLine + pwdEditLine + loginButton.CallEvent)
last_enter.txt      : SelectSlot(0) + StartGame() OK
last_stat.txt       : OYUN İÇİ — staple lv100, Ninja-E, Jinno (empire 3), HP 3445/5593
last_123klohp.txt   : pot %90 AKTİF, slot 4 eşleşti, tek-yol kalp OK
```

**SONUÇ: Romania sunucusu = TIP1** (server seçme ekranı AYRI + OK butonu VAR, login ekranı AYRI) + **M1 resmi 2014** mimarisi; BÖLGE bayrağı yok (tek bölge), +M5 PIN yok. Giriş zinciri uçtan uca KANITLANDI (serverlist→selserver→login→charlist→enter→oyun içi→pot). Doğru akış: `status → serverlist → selserver 0 0 → login <id> <pwd> → charlist → selchar 0 → enter 0` veya TEK KOMUT `auto <id> <pwd>`.

## 3. v2.9.1 DLL — 4 KALICI FIX (sadece MaxExecutor.cpp değişti; pylib v5.4 AYNEN)

| FIX | Ne yapıyor | Saha ilacı |
|---|---|---|
| **FIX-41a** | `ReadPylibVersion` TAM DOSYA tarar (4MB sınır, malloc/free; erken dönüşlerde sızıntı yok) | `PYLIB ESI` SAHTE alarmı kökten bitti → doğrusu: `PLUSMAXGOD_PyScript.py : v5.4 (uyumlu)` |
| **FIX-41b** | (1) Pencere 20 sn'de bulunamazsa `LateHookThread` 30 dk'ye kadar her 2 sn'de yeniden dener; bulununca timer kurulur + kuyruk tetiklenir + `oyun penceresi SONRADAN bulundu` satırı. (2) hwnd=0 iken komut yazılınca: `!! UYARI: ... kuyrukta BEKLEMEDE, simdi CALISMAZ` | detect vakasının birebir ilacı; bekleyen komutlar pencere gelince otomatik akar |
| **FIX-41c** | `QuarantineStaleQueue`: boot'ta önceki oturumun `queue\*.cmd`'leri `queue\eski\`'ye ARŞİVLENİR (silinmez) + log/konsol satırı | Bayat `dropall/sellall` yeni oturumda kendiliğinden ÇALIŞMAZ |
| **FIX-41d** | `g_hSelfMod` + `GetModuleFileNameA`: DLL açılışta KENDİ tam yolunu yazar (konsol + log: `DLL yolu : ...`); bayat DllMain "v2.5" dizgisi v2.9.1 yapıldı | Karışık eski binary vakası: hangisi yüklüyse yolu orada |

Diğer dizgi tazelikleri: konsol başlığı + banner + ESI metni `v2.9.1`.

## 4. DERLEME + DOĞRULAMA

- Araç: **llvm-mingw 20250114 (clang 19.1.7)**, hedef i686-w64-mingw32; `shim_ucrt.o` ile msvcrt-os bağlama (Win7 uyumlu bağımlılık KORUNDU: msvcrt + kernel32 + user32)
- `MaxExecutor.dll` 454144 byte (stripped) — string kanıtı: `MaxExecutor v2.9.1 PLUSMAXGOD yuklendi`, `FIX-41c ... queue\eski\`, `DLL yolu: %s (v2.9.1)`, `... FIX-41b: arka planda aramaya devam edecek (30 dk)`
- `MaxInject.exe` 13824 byte (kaynak değişmedi, yeniden derlendi+stripped)
- pylib v5.4: **tek bayt değişmedi** (saha testi bu sürümle kanıtlandı); `pylib_embedded.h` YOK (v2.9 kararırı: disktekı tek kaynak)

## 5. PAKET + REPO

- `MaxExecutor_bundle_v2.9.1_detectfix.zip` (12 dosya: dll+exe+py+2 cpp+shim_ucrt.c+README+KULLANIM+RESEARCH+PLUSQuest+FIX-NOTU_v2.9.1+WORKLOG) → `download/` + repo
- README.md / KULLANIM.md: v2.9.1 blokları + banner kontrolü + "DLL yolu" satırı açıklaması
- FIX-NOTU_v2.9.1.txt: kullanıcının C:\MaxExec'ine konacak saha notu (bulgular + 4 fix + kurulum + test formülü)

## 6. SONRAKİ ADIMLAR

1. Kullanıcı: v2.9.1 DLL+EXE'yi C:\MaxExec'e kopyala (oyun KAPALIYKEN), oyunu aç, `MaxInject.exe` çalıştır, banner'da **v2.9.1** + **DLL yolu** satırını gör → `detect` yaz → `results\last_matrix.txt` + konsol [MATRIX] bloğu
2. `detect` çıktısını paylaş (beklenen: TIP1 / M1 / tek bölge) — sınıflandırma sahada teyit edilsin
3. İkinci bir sunucuda da `detect` alınırsa TIP2a/TIP2b/M2 varyantlarının saha örnekleri birikmiş olur
4. Öneri (sonraki oturum): `relogin`'in `_MATRIX` globalini kullanarak TIP-farkındalı akış (TIP1'de selserver adımını login'den ÖNCE yapmak)
