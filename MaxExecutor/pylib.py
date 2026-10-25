# -*- coding: utf-8 -*-
"""
===========================================================================
 pylib.py — MaxExecutor Ana-Thread Komut Kutuphanesi (v1.0)
===========================================================================
 YUKLEME (DLL konsolunda BIR KEZ):
   load C:\MaxExec\pylib.py
   (cikti: WndProc komutu olarak kuyruga yazilir -> ANA THREAD'de exec olur)

 NEDEN GUVENLI:
   * Bu kutuphanedeki her fonksiyon MaxExecutor tarafindan ANA THREAD'de
     calistirilir (WndProc + PyRun_SimpleString). Metin2 client GIL'i ana
     thread'de tutar -> biz ana thread'deyken Python C-API'lerine dokunmak
     dogal olarak yaris-sizdir. (DEV_GIL_ANALYSIS.md RC1/RC9 kok-why)
   * Monkey-patch YOK, gc.get_objects() YOK, arka plan thread YOK.
   * mainStream yalniz YUKLEME ANINDA yakalanir (yukleme de ana thread'de).

 KOMUTLAR (DLL konsolundan cagrilan kisaltilmis arayuzler):
   login <id> <pwd>          maxlib.login(id,pwd)
   charlist                  maxlib.charlist()
   empire <1-3>              maxlib.empire(n)
   create <slot> <ad> <race> <shape>   maxlib.create(slot,ad,race,shape)
   enter <slot>              maxlib.enter(slot)
   status                    maxlib.status()
   raw <kod>                 serbest

 SONUC DOSYALARI: C:\MaxExec\results\last_*.txt
 LEGENDYSF KARSILIKLARI (detay: reports/DEV_LOGIN_FLOW.md):
   net.SetLoginInfo                PythonNetworkStream.cpp:512
   net.ConnectToAccountServer      PythonNetworkStreamModule.cpp:346
   net.GetAccountCharacterSlotData* PythonNetworkStreamModule.cpp:164/179
   net.SendSelectEmpirePacket      PythonNetworkStreamPhaseSelect.cpp:149
   net.SendCreateCharacterPacket   PythonNetworkStreamPhaseSelect.cpp:198
   net.DirectEnter                 PythonNetworkStream.cpp:499 (tek giris!)
===========================================================================
"""

import sys
import time
import os

RESULT_DIR = r'C:\MaxExec\results'

# MAIN_RACE degerleri (LegendySF: CLI/PythonPlayer.cpp:10-24)
RACE_TABLE = {
    0: ('Warrior', 'E'), 1: ('Ninja', 'K'), 2: ('Sura', 'E'), 3: ('Shaman', 'K'),
    4: ('Warrior', 'K'), 5: ('Ninja', 'E'), 6: ('Sura', 'K'), 7: ('Shaman', 'E'),
    8: ('Wolfman', 'E'),
}
JOB_NAMES = {0: 'Warrior', 1: 'Ninja', 2: 'Sura', 3: 'Shaman', 4: 'Wolfman'}
SLOT_COUNT = 5   # ENABLE_PLAYER_PER_ACCOUNT5 (LegendySF: CommonDefines.h:33)

# ---------------------------------------------------------------------------
# iceri-yardimcilar
# ---------------------------------------------------------------------------
def _res_name(name):
    if not os.path.isdir(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    return os.path.join(RESULT_DIR, 'last_%s.txt' % name)

def _write(name, text):
    try:
        f = open(_res_name(name), 'w')
        f.write(text)
        f.close()
    except:
        pass

def _fmt_error(e):
    return '%s: %s' % (type(e).__name__, str(e))

# ---------------------------------------------------------------------------
# mainStream yakalama (yalniz YUKLEME ANINDA — ana thread'deyiz)
# ---------------------------------------------------------------------------
_MS = None          # MainStream ornegi (varsa)
_LOAD_NOTES = []

def _try_capture_mainstream():
    """__main__ globali -> sys.modules taramasi. (frame yuruyusu gerekmez:
    biz yuklemeyi ana thread'de yapiyoruz ve exec frame'i taze.)"""
    global _MS
    # 1) __main__ globali — bazi paketlerde prototype.py mainStream'i module
    #    globali olarak birakir
    try:
        import __main__
        ms = getattr(__main__, 'mainStream', None)
        if ms is not None:
            _MS = ms
            _LOAD_NOTES.append('mainStream: __main__ globalinden yakalandi')
            return
    except:
        pass
    # 2) sys.modules icinde networkmodule/MainStream ornegi taramasi
    #    (bu tarama gc DEGIL — sys.modules anahtar bakisi, ucuz ve guvenli)
    try:
        import networkmodule
        for attr in ('mainStream', 'stream', 'curStream'):
            ms = getattr(networkmodule, attr, None)
            if ms is not None:
                _MS = ms
                _LOAD_NOTES.append('mainStream: networkmodule.%s' % attr)
                return
    except:
        pass
    _LOAD_NOTES.append('mainStream: BULUNAMADI (net.* komutlari yine calisir)')

_try_capture_mainstream()

def _get_ms():
    return _MS

# ---------------------------------------------------------------------------
# SAHNE OKUMA (hooksuz) — pencere tip adindan
# ---------------------------------------------------------------------------
def _scene_name():
    """Donus: 'LoginWindow' / 'SelectCharacterWindow' / 'CreateCharacterWindow'
    / 'SelectEmpireWindow' / 'ReselectEmpireWindow' / 'LoadingWindow'
    / 'GameWindow' / '?'"""
    ms = _get_ms()
    if ms is not None:
        for attr in ('curPhaseWindow', 'phaseWindow', 'curWindow'):
            try:
                pw = getattr(ms, attr, None)
            except:
                pw = None
            if pw is not None:
                return type(pw).__name__
    # yedek: import edilmis intro modullerinden sekmeye calisma — YOK
    # (hooksuz, gc'siz); bunun yerine baglanti durumuyla yetin
    return '?'

# ---------------------------------------------------------------------------
# 1) LOGIN  (LegendySF §3: auth->key->game-login; client otomatik zincir)
# ---------------------------------------------------------------------------
def login(user, pwd):
    try:
        import net
        # mainStream bulunursa UI-yoluna en yakın doğru zincir:
        # SetLoginInfo + Connect (KEEP_ACCOUNT_CONNETION_ENABLE=1 -> auth'a baglanir)
        ms = _get_ms()
        net.SetLoginInfo(user, pwd)
        sent = None
        if ms is not None and hasattr(ms, 'Connect'):
            try:
                ms.Connect()
                sent = 'stream.Connect()'
            except:
                sent = None
        if sent is None:
            if hasattr(net, 'ConnectToAccountServer'):
                net.ConnectToAccountServer()
                sent = 'net.ConnectToAccountServer()'
            elif hasattr(net, 'Connect'):
                net.Connect()
                sent = 'net.Connect()'
            else:
                _write('login', 'HATA: baglanti glue bulunamadi\n')
                return
        _write('login', 'OK: SetLoginInfo + %s (id=%s)\n'
                        'Beklenen zincir: auth Login3 -> key -> game Login2 ->\n'
                        'TPacketGCEmpire(90) + LoginSuccess4(32) -> SelectCharacterWindow\n'
                        % (sent, user))
        _write('status', status_text())
    except Exception, e:
        _write('login', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 2) CHARLIST — 5 slot: isim/level/sinif/cinsiyet/guild (LegendySF §4b)
# ---------------------------------------------------------------------------
def charlist():
    try:
        import net
        lines = []
        count = 0
        empty_slots = []
        for i in range(SLOT_COUNT):
            try:
                pid = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)
            except:
                pid = 0
            if not pid:
                empty_slots.append(i)
                lines.append('[slot %d] BOS' % i)
                continue
            count += 1
            try:
                name  = net.GetAccountCharacterSlotDataString(i, net.ACCOUNT_CHARACTER_SLOT_NAME)
            except:
                name = '?'
            try:
                level = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
            except:
                level = -1
            try:
                race  = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_RACE)
            except:
                race = -1
            job = JOB_NAMES.get(race % 4, '?') if race >= 0 else '?'
            sex = RACE_TABLE.get(race, ('?', '?'))[1]
            try:
                guild = net.GetAccountCharacterSlotDataString(i, net.ACCOUNT_CHARACTER_SLOT_GUILD_NAME)
            except:
                guild = ''
            lines.append('[slot %d] %s  Lv.%d  %s(%s)  race=%d  guild=%s' %
                         (i, name, level, job, sex, race, guild))
        lines.append('---')
        lines.append('TOPLAM KARAKTER: %d / %d' % (count, SLOT_COUNT))
        lines.append('BOS SLOT(LAR): %s' % (str(empty_slots)))
        _write('charlist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('charlist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 3) EMPIRE / BAYRAK (LegendySF §5) — yalniz 0 karakterken anlamlidir
# ---------------------------------------------------------------------------
def empire(n):
    try:
        if n not in (1, 2, 3):
            _write('empire', 'HATA: empire 1(A Shinsoo) 2(B Chunjo) 3(C Jinno) olmali, gelen=%s\n' % n)
            return
        import net
        net.SendSelectEmpirePacket(n)
        _write('empire', 'OK: TPacketCGEmpire(90) gonderildi empire=%d\n'
                         'Server cevabi: TPacketGCEmpire + LoginSuccess4 tazeleme ->\n'
                         'SelectCharacterWindow geri doner\n' % n)
    except Exception, e:
        _write('empire', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 4) CREATE (LegendySF §6) — statlar server'da JobInitialPoints'tan gelir,
#    client statlari ihmal edilir -> 0,0,0,0 gondermek zararsizdir.
#    HATA AYRIMI (hooksuz): create sonrasi slotu yokla:
#      charlist() -> slot doluysa OK; 30sn sonra hala bos -> failure(bType).
#      bType 1=isim alinmis, 0=genel ("karakteri yaratamazsin"); ayrica
#      DB'de hesap basina 30 sn create cooldown VARDIR (ClientManagerPlayer.cpp:839).
# ---------------------------------------------------------------------------
def create(slot, name, race, shape):
    try:
        if slot < 0 or slot >= SLOT_COUNT:
            _write('create', 'HATA: slot 0..%d olmali\n' % (SLOT_COUNT - 1))
            return
        if race not in RACE_TABLE:
            _write('create', 'HATA: race 0..8 olmali (0=ErWarr 1=KaNinja 2=ErSura 3=KaShaman '
                             '4=KaWarr 5=ErNinja 6=KaSura 7=ErShaman 8=Wolfman)\n')
            return
        if len(name) > 12:
            _write('create', 'HATA: isim > 12 karakter (server siniri: input_login.cpp:499-503)\n')
            return
        import net
        net.SendCreateCharacterPacket(slot, name, race, shape, 0, 0, 0, 0)
        job, sex = RACE_TABLE[race]
        _write('create', 'OK: TPacketCGCreateCharacter(4) gonderildi slot=%d ad=%s race=%d(%s-%s) shape=%d\n'
                         'Sonuc kontrolu: 30 sn sonra `charlist` — slot doluysa OK.\n'
                         'Dikkat: 30 sn create cooldown (anti-flood).\n'
                         % (slot, name, race, job, sex, shape))
    except Exception, e:
        _write('create', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 5) ENTER — TEK DirectEnter (LegendySF §7 + RC12 YASAGI)
# ---------------------------------------------------------------------------
def enter(slot):
    try:
        import net
        # UYARI: UI StartGame + DirectEnter CIFT GIRIS yapar -> NPC'ler yuklenmez.
        # YALNIZ DirectEnter: client kendi zincirini yürütür
        #   (2. login -> SetLoadingPhase -> SendSelectCharacterPacket -> LoadData
        #    -> StartGame -> SendEnterGamePacket -> PHASE_GAME)
        net.DirectEnter(slot)
        _write('enter', 'OK: DirectEnter(%d) gonderildi (TEK giris — UI StartGame CAGRILMADI)\n' % slot)
    except Exception, e:
        _write('enter', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 6) STATUS — sahne + baglanti + slot ozeti (hooksuz)
# ---------------------------------------------------------------------------
def status_text():
    try:
        import net
        try:
            conn = 1 if net.IsConnect() else 0
        except:
            conn = -1
    except:
        conn = -2
    scene = _scene_name()
    ms_state = 'yakalandi' if _MS is not None else 'yok'
    return 'SCENE=%s | CONN=%d | mainStream=%s | t=%s\n' % (
        scene, conn, ms_state, time.strftime('%H:%M:%S'))

def status():
    _write('status', status_text())

# ---------------------------------------------------------------------------
# modul kaydi — DLL snippet'leri `import maxlib; maxlib.login(...)` der;
# import makinesi sys.modules'a once bakar, buradaki nesneyi bulur.
# ---------------------------------------------------------------------------
import sys as _sys
import types as _types
try:
    _maxlib = _sys.modules.get('maxlib', None)
    if _maxlib is None:
        _maxlib = _types.ModuleType('maxlib')
    for _k, _v in globals().items():
        if _k.startswith('__'):
            continue
        setattr(_maxlib, _k, _v)
    _sys.modules['maxlib'] = _maxlib
except Exception, e:
    print '[maxlib] modul kaydi hatasi:', e

# ---------------------------------------------------------------------------
# yukleme raporu
# ---------------------------------------------------------------------------
_write('pylib_load',
       'pylib yuklendi (ANA THREAD)\n' +
       '\n'.join('- ' + n for n in _LOAD_NOTES) + '\n' +
       status_text())
print '[maxlib] yuklendi — komutlar: login/charlist/empire/create/enter/status'
