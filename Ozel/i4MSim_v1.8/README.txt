============================================================================
 i4MSim v1.8 - DLL yuklu-hal (process-dinamik) SIMULASYONU + HOOK TARAMASI
 i4MConsoleLoader / PEManualMapper motoru uzerine insa edildi
============================================================================

NE YAPAR?
  Diskteki DLL'i (python27.dll dahil herhangi bir DLL), hedef process'teki
  YUKLU HALINE cevirir (gercek Windows loader + packer unpack DAHIL) ve iki
  goruntuyu byte-byte karsilastirir. v1.8'e HOOK TARAMA katmani eklendi:
  inline-hook / IAT-hook / trampoline / enjekte-kod tespiti, sim'in urettigi
  "pristine" goruntu referans alinarak yapilir.

KOMUTLAR
  1 <dll yolu>   SIMULE ET
     Orn: 1 C:\Users\Admin\Desktop\NightTownFullpack\python27.dll
     -> arac kendini %TEMP%\i4MHost\metin2client.exe olarak kopyalayip
        oradan yukler (pack'in host-adi kontrolune karsi),
        gercek Windows loader (LoadLibraryEx) ile yukler,
        packer unpack'ini CALISTIRIR (TLS + DllMain),
        base..base+SizeOfImage TUM byte'lari yazar:
        -> C:\simule_memory.txt

  2 <pid>        CANLI DUMP
     Orn: 2 1234
     -> hedef process'te python27.dll'i bulur (snapshot; bulamazsa
        bellek-PE taramasi), base..end tum byte'lari okur:
        -> C:\dinamik_memory.txt

  3              KARSILASTIR (v1.8: semantik siniflandirmali)
     -> byte-byte karsilastirma + bolgeleri SEMANTIK etiketler:
        [HDR]  header
        [PK]   packer-unpacked KOD (diskte rawsize=0 olan EXEC bolum)
        [DS]   diskten gelen veri
        SEMANTIK (calisma-zamani dolum turleri):
          HPTR-ASLR      iki taraf da heap pointer -> ASLR yuzunden
                         YAPISAL olarak eslesemez (iki canli dump arasinda
                         bile farkli). Hook DEGIL, gurultu.
          HPTR-ASLR+T2   heap ptr + init turu karisik bolge
          T2-STAT        bir taraf image-statik ptr, digeri heap/kucuk
                         (init sirasinda turulen dolum)
          CNT            kucuk sayac/refcnt/bayrak degerleri
          PATH           ascii yol/string icerigi (host klasoru farki vb.)
          PKS            packer-kosmetik section-header alani
                         (rawsize=0 bolumun SizeOfRawData/PointerToRawData
                         alanlari - zararsiz, whitelist'li)
          VERI           diger
     -> VERDICT artik YAPISAL vs GURULTU ayrimi yapar:
        KOD(EXEC) + IAT + BASERELOC + header(yapisal) 0 fark ise:
          "[OK] LOADER-YAPISAL 0 FARK ... inline-hook / IAT-hook YOK"
        -> tam rapor: C:\i4msim_diff.txt

  4 <pid>        CANLI KENDI-GURULTUSU (v1.8)
     -> iki canli dump (1 sn arayla) karsilastirilir. Canli goruntu kendi
        kendinden bile farklisiyorsa (heap hareketi, sayaclar), sim-vs-canli
        diff'inin bir parcasinin "yakalanamaz taban-gurultu" oldugunun
        KANITIDIR. 2. dump kanit olarak C:\dinamik_memory_2.txt'ye yazilir.

  5 <dll yolu>   zorla MANUAL-MAP modu (PEManualMapper + TLS + DllMain)
  6 <dll yolu>   zorla GERCEK-LOADER modu (LoadLibraryEx)

  8 <pid>        HOOK TARAMA (v1.8)   [once '1' ile sim uretilmis olmali]
     (a) EXEC/KOD bolgelerinde sim-vs-canli byte diff
         -> python27.dll icinde byte-level INLINE-HOOK taramasi.
            Bu bolgeler sim'de tertemiz uretildigi icin 0 gurultu beklenir;
            1 byte fark bile mudahale anlamina gelir.
     (b) tum diff bolgelerindeki pointer-benzeri degerlerin CANLI
         hedef-denetimi (VirtualQueryEx ile):
           MODUL(xxx)                hedef bilinen modul -> OK
           HEAP/VERI                 normal heap (PyObject) -> OK
           EXEC-ANONIM(supheli!)     modul-disi calistirilabilir bellek
                                     -> TRAMPOLINE SUPHELISI
           IMAGE-EXEC modul-listesi-disi -> manuel-map suphelisi
         - python27-disi modullere isaret eden fark pointer'lari "bilgi"
           olarak listelenir (statik fonksiyon ptr'leri normaldir; isimlere
           bakilir: bilinmeyen bir DLL varsa supheli).
     (c) MODUL-DISI calistirilabilir bellek bolgeleri listesi
         (shellcode / manuel-map / injected DLL avi)
     (d) modul listesi (bilinmeyen DLL'ler gorunur)
     -> rapor: C:\i4msim_hookscan.txt

 help | quit

HOOK TESPIT KAPSAMI (v1.8)
  YAKALANIR:
    - python27.dll koduna yazilan inline hook (JMP/CALL patch)      -> 8(a)
    - python27.dll IAT/import girdilerinin yonlendirilmesi          -> 8(a)+3
    - PyMethodDef.ml_meth gibi STATIK fonksiyon pointerlarinin
      modul-disi exec bellege (trampoline) cevrilmesi               -> 8(b)
    - enjekte edilmis shellcode / manuel-map'lenmis modul           -> 8(c)
    - bilinmeyen DLL yuklenmesi                                     -> 8(d)
    - oyun-EXE (metin2client.exe) tarafindaki ayni saldirilar
      -> i4MConsoleLoader ile EXE goruntusu icin ayni yontem
  YAKALANMAZ (statik bellek-esleme nin dogal siniri):
    - tamamen HEAP icinde yasayan Python-level monkeypatch
      (sys.modules degisimi, fonksiyon objesi degisimi). Bunun kodu yine
      bir yerde calismak zorunda: o "bir yer" modul-disi EXEC ise 8(c)
      yakalar; sadece mevcut modullerin icindeyse kod-diff'i yakalar.

SONUC NASIL OKUNUR?
  [OK] 0 FARK                 -> simulasyon %100 birebir
  [OK] LOADER-YAPISAL 0 FARK  -> loader+packer+KOD katmani %100 uretildi;
                                 kalan fark tamami calisma-zamani gurultusu
                                 (HPTR-ASLR/CNT/PATH/PKS). KODDA mudahale YOK.
  [!!] YAPISAL fark VAR       -> ya unpack eksigi, ya canli tarafta hook.
                                 -> '8 <pid>' ile hook taramasi + raporu incele

NOTLAR
  - i4MSim.exe 32-bit'tir (python27.dll 32-bit); x86 Windows veya WOW64'te calisir.
  - C:\ kok dizinine yazamazsa otomatik %TEMP% altina yazar ve yolu soyler.
  - cmd1 feda-i process kullanir: cokerse ana arac etkilenmez, rc ile raporlar.
  - cmd2/4/8 icin metin2 CALISIYOR olmali; gerekirse araci yonetici olarak acin.
  - Antivirus feda-i process kopyasini (metin2client.exe) supheleyebilir;
    klasoru istisna listesine alin.

DERLEME (zig c++)
  zig c++ -target x86-windows-gnu -std=c++17 -O2 -fms-extensions -static
          -fno-ident -DWIN32_LEAN_AND_MEAN -DNOMINMAX -D_CRT_SECURE_NO_WARNINGS
          -DNDEBUG -Isrc src\main.cpp -o i4MSim.exe

v1.8 DEGISIKLIKLERI (v1.0 -> v1.8)
  + KOMUT 4: canli kendi-gurultusu (iki canli dump; taban-gurultu kaniti)
  + KOMUT 8: hook tarama (EXEC-diff, pointer-hedef denetimi, modul-disi
    EXEC taramasi, modul listesi; rapor: C:\i4msim_hookscan.txt)
  + KOMUT 3: SEMANTIK siniflandirma (HPTR-ASLR/T2-STAT/CNT/PATH/PKS/VERI)
    ve LOADER-YAPISAL ozet (EXEC/IAT/RELOC/PKS ayrimi)
  + VERDICT: "yapisal fark" vs "calisma-zamani gurultusu" ayrimi;
    packer-kosmetik header farklari (PKS) artik yanlis alarm uretmez
    (orn. NightTownFullpack python27.dll RVA 0x1F5 = data0.PointerToRawData)
  + ikili (x1/x2) image araliklari ayri ayri hesaplanir (farkli base'e dayanikli)
  - v1.7'deki init-tier (Py_Initialize simülasyonu) bu surumde YOKTUR; v1.8
    v1.0 tabanindan turetilmistir. Gerekirse v1.7 init-tier'i v1.8'e tasinacak.
============================================================================
