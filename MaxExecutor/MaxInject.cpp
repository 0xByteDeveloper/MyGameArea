// ============================================================================
//  MaxInject.cpp — MaxExecutor.dll enjectoru (32-bit, LoadLibrary yolu)
// ============================================================================
//  Kullanim:
//    MaxInject.exe                            -> metin2client.exe'yi otomatik bulur
//    MaxInject.exe metin2client.exe           -> isimle ara
//    MaxInject.exe 1234                       -> PID ile bagla
//    MaxInject.exe metin2.exe C:\MaxExec\MaxExecutor.dll
//
//  Yontem: CreateRemoteThread(LoadLibraryA). Hook Hunter'in taradigi
//  inline hook'larla karismaz; DLL LoadLibrary yoluyla yuklenir (standart yol).
// ============================================================================

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <tlhelp32.h>
#include <stdio.h>
#include <string>

static DWORD FindPidByName(const char* name)
{
    HANDLE snap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (snap == INVALID_HANDLE_VALUE) return 0;
    PROCESSENTRY32W pe; pe.dwSize = sizeof(pe);
    DWORD pid = 0;
    wchar_t wname[260];
    int wn = MultiByteToWideChar(CP_ACP, 0, name, -1, wname, 260);
    if (Process32FirstW(snap, &pe))
    {
        do
        {
            if (wn > 0 && lstrcmpiW(pe.szExeFile, wname) == 0) { pid = pe.th32ProcessID; break; }
        } while (Process32NextW(snap, &pe));
    }
    CloseHandle(snap);
    return pid;
}

static bool Inject(DWORD pid, const char* dllPath)
{
    HANDLE hProc = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION |
                               PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ,
                               FALSE, pid);
    if (!hProc) { printf("[!] OpenProcess(%lu) basarisiz: %lu\n", (unsigned long)pid, (unsigned long)GetLastError()); return false; }

    SIZE_T len = strlen(dllPath) + 1;
    LPVOID remote = VirtualAllocEx(hProc, NULL, len, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remote) { printf("[!] VirtualAllocEx basarisiz: %lu\n", (unsigned long)GetLastError()); CloseHandle(hProc); return false; }

    if (!WriteProcessMemory(hProc, remote, dllPath, len, NULL))
    { printf("[!] WriteProcessMemory basarisiz: %lu\n", (unsigned long)GetLastError()); CloseHandle(hProc); return false; }

    LPTHREAD_START_ROUTINE loadLib =
        (LPTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandleA("kernel32.dll"), "LoadLibraryA");
    if (!loadLib) { printf("[!] LoadLibraryA adresi alinamadi\n"); CloseHandle(hProc); return false; }

    HANDLE hThread = CreateRemoteThread(hProc, NULL, 0, loadLib, remote, 0, NULL);
    if (!hThread) { printf("[!] CreateRemoteThread basarisiz: %lu\n", (unsigned long)GetLastError()); CloseHandle(hProc); return false; }

    printf("[+] RemoteThread baslatildi. DLL yuklemesi bekleniyor...\n");
    WaitForSingleObject(hThread, 8000);
    DWORD exitCode = 0;
    GetExitCodeThread(hThread, &exitCode);
    CloseHandle(hThread);
    VirtualFreeEx(hProc, remote, 0, MEM_RELEASE);
    CloseHandle(hProc);

    if (exitCode) { printf("[+] DLL yuklendi (module=0x%08lX). MaxExecutor konsolu acilmis olmali.\n", (unsigned long)exitCode); return true; }
    printf("[!] Thread donus degeri 0 — DLL yuklenmemis olabilir (yol/erisim kontrol et).\n");
    return false;
}

int main(int argc, char** argv)
{
    printf("=== MaxInject — MaxExecutor.dll enjectoru (ana-thread guvenli executor) ===\n");
    const char* target = (argc >= 2 && argv[1][0] && !(argv[1][0] >= '0' && argv[1][0] <= '9')) ? argv[1] : "metin2client.exe";
    const char* dll    = (argc >= 3) ? argv[2] : "C:\\MaxExec\\MaxExecutor.dll";

    DWORD pid = 0;
    if (argc >= 2 && argv[1][0] >= '0' && argv[1][0] <= '9')
        pid = (DWORD)atoi(argv[1]);
    else
        pid = FindPidByName(target);

    if (!pid)
    {
        printf("[!] '%s' sureci bulunamadi. Oyunu acip tekrar dene, ya da PID ver:\n", target);
        printf("    MaxInject.exe <PID> [dll-yolu]\n");
        return 1;
    }

    char fullPath[MAX_PATH];
    if (GetFullPathNameA(dll, MAX_PATH, fullPath, NULL)) dll = fullPath;

    printf("[i] Hedef PID=%lu (%s)\n[i] DLL   = %s\n", (unsigned long)pid, target, dll);
    if (Inject(pid, dll)) return 0;
    return 2;
}
