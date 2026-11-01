# Ozel — i4M araçları özel çalışma alanı

Bu klasör, i4MSim / i4MConsoleLoader hattına ait özel analizleri, sürümleri ve worklog'ları tutar.

## İçerik

| Yol | Açıklama |
|---|---|
| `worklog/` | Oturum worklog'ları (tarih başına) |
| `analiz/i4msim_12853_byte_analizi.md` | NightTownFullpack python27.dll sim-vs-canlı 12.853-byte diff'inin derin analizi (3 sorunun cevabı) |
| `analiz/analysis_result.json` | Aynı analizin makine-okunur çıktısı |
| `i4MSim_v1.8.zip` | **i4MSim v1.8** — kaynak kod + derlenmiş exe (32-bit) + README |
| `i4MSim_v1.8/` | Aynı paketin klasör hali (inceleme için) |

## i4MSim v1.8 özet

- `1 <dll>` simülasyon (gerçek loader + packer unpack, fedai process)
- `2 <pid>` canlı dump · `3` semantik karşılaştırma (HPTR-ASLR/CNT/PATH/PKS + LOADER-YAPISAL verdict)
- `4 <pid>` canlı kendi-gürültüsü · `8 <pid>` **hook tarama** (EXEC-diff, trampoline/pointer hedef
  denetimi, modül-dışı EXEC, modül listesi) → `C:\i4msim_hookscan.txt`
- Derleme: `zig c++ -target x86-windows-gnu ...` (README içinde tam komut)

## Kritik bulgu (2026-11-01)

NightTownFullpack python27.dll sim-vs-canlı diff'inde **kod (data0), IAT ve BASERELOC 0 fark**;
12.853 byte'lık farkın tamamı data1'deki runtime gürültüsü (ASLR heap pointer'ları, sayaçlar,
1 packer-kosmetik header byte). Yani: **hook ararken bu gürültü false positive üretmez** —
EXEC bölgesi + pointer-hedef taraması (v1.8 komut 8) kullanılmalı.
