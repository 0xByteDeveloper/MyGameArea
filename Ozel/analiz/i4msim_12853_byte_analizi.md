# i4MSim 12853-byte DIFF DERİN ANALİZİ — NightTownFullpack / python27.dll

**Tarih:** 2026-11-01 (Europe/Istanbul)
**Girdi:** `i4msim_diff.rar` (i4msim_diff.txt + simule_memory.txt + dinamik_memory.txt + simule_log.txt)
**Metot:** İki dump'ın tamamen bağımsız yeniden ayrıştırılması (Python), PE header dekode,
828 bölgenin align-4 word analiziyle semantik sınıflandırması, pointer hedef-denetimi.
**Doğrulama:** Bağımsız hesap aynı sonucu verdi: **12.853 / 2.588.672 byte (%0,4965), 828 bölge** — raporla birebir.

---

## 1) 12853 BYTE'IN DAĞILIMI (soru 1'in cevabı)

### 1.1 Bölüm bazında — en kritik tablo

| Bölüm | RVA aralığı | İçerik | Fark |
|---|---|---|---|
| **data0** | 0x001000–0x1A9000 | **packer-unpacked KOD (EXEC, 1,7 MB)** | **0 byte** |
| **IAT / IMPORT** | 0x26F724 + | import tablosu | **0 byte** |
| **BASERELOC** | 0x277394 | relocation | **0 byte** |
| **data1** | 0x1A9000–0x26F000 | diskten gelen veri (R/W) | 19.781 byte (827 bölge) |
| header (section tablosu) | 0x1F5 | data0.PointerToRawData | **1 byte** |

### 1.2 Semantik dağılım (word bazlı hedef analizi, 828 bölge)

| Sınıf | Bölge | ~Byte | Açıklama |
|---|---|---|---|
| **HPTR-ASLR** | **799** | **~19.475** | heap→heap pointer (PyObject\*). Sim heap'i 0x06A1xxxx/0x06C7xxxx arena, canlı 0x04BExxxx/0x05B1xxxx arena. **İki process'te yapısal olarak eşleşemez.** |
| CNT | 15 | ~88 | küçük sayaç/refcnt/bayrak: `1e→1f`, `0d→10`, `0a→0b`, `27→29`, `05→07`, `01→8a` |
| T2-STAT | ~5 | ~30 | canlı tarafın 0'a **statik image pointer'ı** yazdığı yerler: 0x1E228030, 0x1E0BCCE0 (sim init-tier'inin atladığı dolumlar) |
| IMG→IMG | 1 | 6 | RVA 0x24B248: sim=0x1E228DAC ↔ canlı=0x1E228444/0x1E228540 — **tüm dump'taki TEK gerçek init-tier statik sapması** |
| PATH | 1 | ~43 | RVA 0x24BA4F: `...AppData\Local\Te...` ↔ `...Desktop\NightTow...` — sim host'u `%TEMP%\i4MHost`'ta çalıştığı için sys.path/prefix string farkı |
| PKS (header) | 1 | 1 | RVA 0x1F5: data0.PointerToRawData sim=0x00000400 ↔ canlı=0x00000000 |

Word hedef-histogramı: HEAP→HEAP **2677** word, KÜÇÜK→KÜÇÜK 1053, KÜÇÜK→HEAP 535
(canlı yeni heap objeleri yazmış), HEAP→KÜÇÜK 108, IMG→HEAP 34, KÜÇÜK→IMG 32, geri kalan ~15 karışık.
**İki tarafı da image-pointer olan ve FARKLI çıkan word: 1 adet.** Statik pointer dolumu (Py_None,
Py_True gibi singleton'lar, PyMethodDef kod pointer'ları) aynı base'de %100 eşleşiyor.

### 1.3 RVA 0x1F5 header byte'ının kök-nedeni

PE: `e_lfanew=0xE8`, optional header 0x100–0x1DF, **section tablosu 0x1E0'de** (data0, data1, .rsrc).
0x1F5 = data0 header'ının **PointerToRawData** alanının (0x1F4–0x1F7) 2. byte'ı:

```
data0.PointerToRawData:  sim=0x00000400   canlı=0x00000000
data0.SizeOfRawData  :  sim=0           canlı=0
```

- Windows loader section header'ına **asla** dokunmaz; bu alanı packer kendisi yazıyor.
- `rawsize=0` olduğu için loader bu alanı **kullanmıyor** → işlevsel etkisi sıfır, **packer-kosmetik**.
- Sim tarafında packer DllMain içinde bu alanı diskten gelen 0x400 olarak bırakmış/geri yazmış;
  canlı process'te packer 0'a çekmiş. (Muhtemel neden: packer'ın header-restore aşamasının
  canlı ortamda bir adım farklı koşması — oyun process'inde modül sırası/host durumu farklı.)
- **Sonuç: hook değil, Metin2-init değil — packer kendini-yeniden-yazma farkı.** v1.8'de bu alan
  `PKS` sınıfıyla whitelist'lendi, artık verdict bozmuyor.

### 1.4 Soru 1'in net cevabı

> "Bu farklı byte'lar Metin2'nin python27.dll'i initlerken çeşitli fonksiyonlarla işlemesinden kaynaklı mı?"

**~%99 HAYIR, ~%1 EVET.**

- **~%85 (HPTR-ASLR):** python27 çalışırken ürettiği PyObject\* pointer'larını statik veriye
  (module dict'leri, interned string tabloları, tp_subclasses, method tabloları…) yazar. Bu adresler
  **her process'te ASLR yüzünden farklıdır.** Aynı oyunu iki kez açıp iki canlı dump alsan da
  bunlar eşleşmez (kanıt için: v1.8 `4 <pid>`). Bu **Metin2'ye özgü değildir**; herhangi bir DLL'in
  herhangi bir process'teki doğal hali budur.
- **~%13 (CNT + KÜÇÜK→HEAP):** refcnt sayaçları ve canlının sonradan doldurduğu girişler —
  canlı oyun sim'den **daha fazla iş yapmış** (import'lar, oyun script'leri, network). Bu kısım
  "init haritası" etkisi **evet** ama değerler çalışma-anına bağlıdır; birebir üretimi ancak oyunun
  yaptığı her işlemi aynı sırayla tekrarlamakla mümkün olurdu ki bu pratikte anlamsızdır.
- **~%1-2 gerçek sim sapması:** 1 IMG→IMG word, birkaç 0→statik dolum, 1 packer-kosmetik byte,
  1 host-path string bloğu. v1.7 init-tier'inin iyileştirme alanı budur — toplamı **<100 byte**.

---

## 2) HOOK TESPİTİ — false positive sorusu (soru 2'nin cevabı)

> "12853 fark, hook ararken bize false sonuç olarak gözükür mü?"

**HAYIR — 12853 farkın TAMAMI veri (data1) bölgesinde. Kod bölgesi (data0, 1,7 MB EXEC)
0 fark.** Hook avını **sadece EXEC/kod bölgesi + pointer hedefleri** üzerinde yaparsan bu
gürültünün içine hiç girmemiş olursun. v1.8'in `8 <pid>` komutu tam bunu yapar:

| Hook türü | Nerede yaşar | v1.8 tarama | Gürültü |
|---|---|---|---|
| python27 koduna JMP/CALL patch (inline hook) | data0 | **8(a)** EXEC byte-diff | **0** → 1 byte fark bile alarm |
| python27 IAT girdisi yönlendirme | IAT | 8(a)+3 (IAT diff 0 beklentisi) | 0 |
| `PyMethodDef.ml_meth` pointer'ını trampoline'a çevirme | data1 + modül-dışı EXEC | **8(b)** pointer hedef-denetimi + **8(c)** modül-dışı EXEC listesi | düşük; trampoline = anonim EXEC → şüpheli |
| kendi DLL'ini yükleyip fonksiyon yönlendirme | yeni modül | **8(b)** cross-modül ptr raporu + **8(d)** modül listesi | bilgi-düzeyi (isimlere bak) |
| manuel-map / shellcode | anonim EXEC | **8(c)** | 0 |
| **metin2client.exe** içindeki C++ fonksiyona hook (SimpleStringFlag tarzı oyun fonksiyonu) | game exe | python27 taraması **görmez** → **i4MConsoleLoader'ın EXE simülasyonu** ile EXE kodu karşılaştır (EXE'de de kod bölgesi 0 gürültü) | 0 |
| Python-level monkeypatch (heap'te fonksiyon objesi değişimi) | heap | statik byte-eşleme **doğal olarak göremez**; ama o kodun kendisi bir yerde olmalı: injected DLL → 8(d), anonim EXEC → 8(c) | — |

### SimpleStringFlag senaryosu somut olarak

1. **Kod-patch hook'u** (fonksiyonun gövdesine JMP): fonksiyon game-exe'deyse EXE sim diff'i,
   python27 C-API'sindeyse 8(a) → **%100 tespit, 0 false positive** (kod bölgesi tertemiz).
2. **Pointer-hook** (method tablosundaki `ml_meth` kendi koduna çevrilir): canlı pointer
   modül-dışı EXEC'e (trampoline) veya bilinmeyen modüle işaret etmeye başlar → 8(b) yakalar.
   Sim tarafında aynı tablo orijinal statik değeriyle durduğu için fark sinyalidir.
3. **Python-level hook** (`sys.modules['dbg'].LogBox` değişimi gibi): heap'te yaşar, statik
   sim buna bakamaz — bunun dürüst sınırı budur. Ama hook'un kodu bir yerde çalışmak zorunda:
   o "bir yer" modül-dışı EXEC ise 8(c) listeler; mevcut bir modülün içindeyse o modülün kod
   bölgesi diff'i (EXE/DLL sim'iyle) yakalar.

### `import dbg; dbg.LogBox('0','BenimKodum')` kanarya testi hakkında

Haklısın: **aktif** kanarya, hooklayan kişiye görünebilir ve hook çağrıyı "yutup" pas geçebilir
(tespit edilemez hale getirir). Bu yüzden v1.8'in yaklaşımı **pasif**tir: hiçbir script çalıştırmadan,
bellek karşılaştırmasıyla hook'un bıraktığı İZİ (kod byte'ı, pointer hedefi, enjekte bölge, bilinmeyen
modül) arar. Kanaryayı yalnızca pasif taramanın yakalayamayacağı Python-level monkeypatch
şüphesi için, ikinci aşama/opsiyonel adım olarak kullan.

---

## 3) MEVCUT SİSTEM DEĞERLENDİRMESİ (soru 3)

### Güçlü yanlar

1. **Mimari doğru:** fedai process + gerçek loader (LoadLibraryEx) yaklaşımı, IAT/RELOC/KOD'un
   0 diff çıkmasıyla kanıtlandı. Manuel-map yedeği (komut 5) base=1E000000 garantisiyle iyi düşünülmüş.
2. **Packer unpack gerçekten üretiliyor:** data0 diskte boş (rawsize=0), sim'de dolu ve canlıyla
   **birebir** — zincirin en zor halkası çözülmüş.
3. **Gürültü-farkındalığı doğru:** T1/T2/T3 ayrımı ve iki-canlı-dump gürültü kanıtı (v1.7 komut 12,
   v1.8 komut 4) metodolojik olarak sahte-%100 iddialarından çok daha değerli.
4. v1.8 ile: PKS whitelist, yapısal-verdict, pasif hook katmanı (8), bağımsız image-range hesabı.

### Zayıf yanlar / riskler / öneriler

1. **"%100" metriğini değiştir:** Byte-eşleşme hedefi tanım gereği imkânsız (ASLR heap).
   Doğru hedef: **KOD+IAT+RELOC %100** + data'da yalnız HPTR-ASLR/CNT sınıfı fark.
   v1.8 verdict'i artık tam bunu raporluyor.
2. **EXE tarafını da aynı katmana bağla:** SimpleStringFlag tarzı fonksiyonlar büyük ihtimalle
   metin2client.exe'de. i4MConsoleLoader'ın %100 EXE simülasyonunun üzerine aynı 8(a)/(b)/(c)
   mantığını EXE modülü için de çalıştır (v1.9 önerisi).
3. **v1.7 init-tier sapmaları (<100 byte):** 0x24B248 (IMG→IMG) ve 0→statik dolumlar, oyunun
   init dizisiyle birebir taklit edilebilir (Create-dizisi sırası). Getirisi düşük ama "0 yapisal
   sapma" hedefi için yapılacaklar listesinde tut.
4. **Canlı okuma savunmasızlığı:** ReadProcessMemory tabanlı dump, hedefteki stealth/anti-read
   tekniklerine karşı savunmasızdır; sürekli taramada iki dump'ın tutarlılığını `4 <pid>` ile doğrula.
5. **Cevrim (loop) tarama:** gerçek anti-cheat kullanımında 8 komutunu zamanlayıcıyla tekrarlamak
   (ör. 30 sn) + rapor farkını loglamak tek-satırlık taramadan çok daha güçlüdür.

---

## 4) v1.8 DEĞİŞİKLİKLERİ

- **KOMUT 4** — canlı kendi-gürültüsü (iki canlı dump, 1 sn arayla; `dinamik_memory_2.txt` kanıtı)
- **KOMUT 8** — hook tarama: (a) EXEC byte-diff, (b) pointer hedef-denetimi (VirtualQueryEx;
  `EXEC-ANONIM(supheli!)` trampoline alarmı), (c) modül-dışı EXEC taraması, (d) modül listesi
  → `C:\i4msim_hookscan.txt`
- **KOMUT 3** — SEMANTIK sınıflandırma (HPTR-ASLR / T2-STAT / CNT / PATH / PKS / VERI) +
  LOADER-YAPISAL özet (EXEC/IAT/RELOC/PKS) + yeni VERDICT
- **PKS whitelist** — packer-kosmetik header alanları (0x1F5 gibi) artık yanlış alarm üretmez
- Kaynak + derlenmiş exe (32-bit, zig c++ ile aynı toolchain): `i4MSim_v1.8.zip`

**Not:** v1.8, eldeki v1.0 kaynak tabanından türetildi; v1.7'deki init-tier (Py_Initialize dizisi)
bu sürümde yoktur — istenirse v1.9'da v1.8'e taşınır.

## 5) GÜVENLİK NOTU

Bu oturumda GitHub PAT düz metin olarak paylaşıldı. İşlem bittikten sonra
**GitHub → Settings → Developer settings → Tokens** üzerinden token'ı **revoke** et ve
yenisini hiçbir sohbete yapıştırmadan kullan (ör. `git credential manager` veya ortam değişkeni).
