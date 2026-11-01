// shim_ucrt.c — llvm-mingw'un statik libc++'si UCRT'ye karsi derlendigi icin
// cektigi ucrt-only sembolleri gercek msvcrt.dll uzerinden karsilar.
// Amac: MaxExecutor.dll'in bagimliligini ESKI haliyle ayni birakmak
// (yalnizca msvcrt.dll + KERNEL32 + USER32) - Win7 dahi ek kurulum istemesin.
// Imzalar mingw-w64 header'lariyla birebir ayni (int __cdecl).
#include <stdarg.h>
#include <wchar.h>
#include <stdio.h>

int __cdecl __stdio_common_vswprintf(unsigned __int64 options, wchar_t *str,
                                     size_t len, const wchar_t *format,
                                     _locale_t locale, va_list valist)
{
    (void)options; (void)locale;
    if (!str || !len) return -1;
    int r = _vsnwprintf(str, len, format, valist);
    if (r < 0) return -1;
    if ((size_t)r >= len) { str[len - 1] = 0; return -1; }
    str[r] = 0;
    return r;
}

int __cdecl __stdio_common_vfwprintf(unsigned __int64 options, FILE *file,
                                     const wchar_t *format,
                                     _locale_t locale, va_list valist)
{
    (void)options; (void)locale;
    return vfwprintf(file, format, valist);
}

int __cdecl __stdio_common_vswprintf_s(unsigned __int64 options, wchar_t *str,
                                       size_t len, const wchar_t *format,
                                       _locale_t locale, va_list valist)
{
    (void)options; (void)locale;
    if (!str || !len) return -1;
    int r = _vsnwprintf(str, len, format, valist);
    if (r < 0) return -1;
    if ((size_t)r >= len) { str[0] = 0; return -1; }
    str[r] = 0;
    return r;
}
