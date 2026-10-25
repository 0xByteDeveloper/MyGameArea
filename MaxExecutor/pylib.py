# -*- coding: utf-8 -*-
"""
===========================================================================
 pylib.py — MaxExecutor Ana-Thread Komut Kutuphanesi (v2.0)
===========================================================================
 v2.0 DEGISIKLIKLER (saha testi 25.10 sonrasi):
   * mainStream artik FRAME YURUYUSU ile bulunur (sys._current_frames).
     __main__.mainStream bu client'ta YOK — calisan script
     (MaximumPyScript_Merged_calisan) bunu kanitladi; ayni teknik.
   * SAHNE: LoginWindow + serverBoard -> 'LoginWindow+ServerList'
     (server isimleri listbox + CH listesi + OK butonu ekran!)
   * YENI selserver(srv, ch): serverList.SelectItem + channelList.SelectItem
     + serverSelectButton.CallEvent  (calisan scriptin birebir yolu)
   * login: UI YOLU ONCELIKLI (idEditLine/pwdEditLine/loginButton.CallEvent),
     yoksa paket yolu (net.SetLoginInfo + baglanti)
   * enter: UI senkron (SelectSlot) + TEK DirectEnter (RC12 yasagi)
 GIL NOTU: butun fonksiyonlar ana thread'de (drain icinde) calisir;
   sadece dict/attr okumalari + dosya yazimi var; gc.get_objects YOK.
===========================================================================
"""

import sys
import time
import os

RESULT_DIR = r'C:\MaxExec\results'

RACE_TABLE = {
    0: ('Warrior', 'E'), 1: ('Ninja', 'K'), 2: ('Sura', 'E'), 3: ('Shaman', 'K'),
    4: ('Warrior', 'K'), 5: ('Ninja', 'E'), 6: ('Sura', 'K'), 7: ('Shaman', 'E'),
    8: ('Wolfman', 'E'),
}
JOB_NAMES = {0: 'Warrior', 1: 'Ninja', 2: 'Sura', 3: 'Shaman', 4: 'Wolfman'}
SLOT_COUNT = 5

# ---------------------------------------------------------------------------
# yardimcilar
# ---------------------------------------------------------------------------
def _res_name(name):
    if not os.path.isdir(RESULT_DIR):
        try:
            os.makedirs(RESULT_DIR)
        except:
            pass
    return os.path.join(RESULT_DIR, 'last_%s.txt' % name)

def _write(name, text):
    try:
        f = open(_res_name(name), 'w')
        f.write(text)
        f.close()
        return True
    except:
        return False

def _fmt_error(e):
    return '%s: %s' % (type(e).__name__, str(e))

# ---------------------------------------------------------------------------
# mainStream — FRAME YURUYUSU (calisan script teknigi, hooksuz)
# ---------------------------------------------------------------------------
_MS_CACHE = None

def _find_ms_from_frames():
    """sys._current_frames() ile mainStream local'ini tara (~0.05ms GIL)."""
    global _MS_CACHE
    if _MS_CACHE is not None:
        return _MS_CACHE
    try:
        frames = sys._current_frames()
    except AttributeError:
        return None
    for tid in frames:
        f = frames[tid]
        depth = 0
        while f is not None and depth < 30:
            try:
                fl = f.f_locals
            except:
                break
            for nm in ('mainStream', 'stream', 'main_stream', 'appStream'):
                ms = fl.get(nm)
                if ms is not None and hasattr(ms, 'curPhaseWindow'):
                    _MS_CACHE = ms
                    return ms
            try:
                f = f.f_back
            except:
                break
            depth += 1
    return None

def _get_ms():
    return _find_ms_from_frames()

# ---------------------------------------------------------------------------
# sahne cozumleme (hooksuz — tip adi + attr okumasi)
# ---------------------------------------------------------------------------
def _phase_window():
    ms = _get_ms()
    if ms is None:
        return None, None
    for attr in ('curPhaseWindow', 'phaseWindow', 'curWindow'):
        try:
            pw = getattr(ms, attr, None)
        except:
            pw = None
        if pw is not None and pw != 0:
            return ms, pw
    return ms, None

def _scene_name():
    """'LoginWindow+ServerList' / 'LoginWindow' / 'SelectCharacterWindow' /
    'CreateCharacterWindow' / 'SelectEmpireWindow' / 'LoadingWindow' /
    'GameWindow' / '?'"""
    ms, pw = _phase_window()
    if pw is None:
        # yedek: baglanti varsa loading/game varsay
        try:
            import net
            if net.IsConnect():
                if sys.modules.get('game') is not None:
                    return 'GameWindow'
                return 'LoadingWindow'
        except:
            pass
        return '?'
    try:
        tn = type(pw).__name__
    except:
        return '?'
    if tn == 'LoginWindow':
        # serverBoard/serverList varsa BU EKRAN server listesi (kullanici: listbox+OK)
        for sb in ('serverBoard', 'serverList', 'channelList'):
            if getattr(pw, sb, None) is not None:
                return 'LoginWindow+ServerList'
        return 'LoginWindow'
    if tn == 'LogoWindow':
        return 'LoginWindow'
    return tn

def _pw_by_type(*tnames):
    """sahne penceresini tip adiyla getir (None olabilir)."""
    ms, pw = _phase_window()
    if pw is None:
        return None
    try:
        if type(pw).__name__ in tnames:
            return pw
    except:
        pass
    return None

# ---------------------------------------------------------------------------
# 1) SERVERLIST — sunucu listesi oku (kullanici: "ilk listbox server isimleri")
# ---------------------------------------------------------------------------
def serverlist():
    try:
        pw = _pw_by_type('LoginWindow')
        if pw is None:
            _write('server', 'HATA: LoginWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        lines = ['SCENE=%s' % _scene_name()]
        sl = getattr(pw, 'serverList', None)
        if sl is None:
            lines.append('serverList attr YOK! LoginWindow attr listesi asagida:')
            for a in dir(pw):
                if 'erver' in a or 'hannel' in a:
                    lines.append('  aday attr: %s = %s' % (a, type(getattr(pw, a)).__name__))
        else:
            n = -1
            try:
                n = sl.GetItemCount()
            except:
                try:
                    n = len(sl.itemList)
                except:
                    pass
            lines.append('server adedi: %s' % str(n))
            if n and n > 0:
                for i in range(min(n, 32)):
                    try:
                        lines.append('  [%d] %s' % (i, sl.GetItemText(i)))
                    except:
                        lines.append('  [%d] (isim okunamadi - GetItemText yok)' % i)
                        break
        _write('server', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('server', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 2) SELSERVER — server+CH sec, OK butonuna bas (calisan scriptin yolu)
# ---------------------------------------------------------------------------
def selserver(srv, ch):
    try:
        pw = _pw_by_type('LoginWindow')
        if pw is None:
            _write('server', 'HATA: LoginWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        sl = getattr(pw, 'serverList', None)
        if sl is None or not hasattr(sl, 'SelectItem'):
            _write('server', '\n'.join(log + ['HATA: serverList.SelectItem YOK! (once `serverlist` yaz)']) + '\n')
            return
        sl.SelectItem(srv)
        log.append('OK: serverList.SelectItem(%d)' % srv)
        time.sleep(0.3)
        cl = getattr(pw, 'channelList', None)
        if cl is not None and hasattr(cl, 'SelectItem'):
            try:
                cl.SelectItem(ch)
                log.append('OK: channelList.SelectItem(%d)' % ch)
                time.sleep(0.3)
            except Exception, e2:
                log.append('UYARI: channel secilemedi (%s)' % _fmt_error(e2))
        else:
            log.append('UYARI: channelList yok (bazi clientlarda server secince dolar)')
        btn = getattr(pw, 'serverSelectButton', None)
        if btn is None:
            # aday tara
            for a in dir(pw):
                if 'elect' in a and 'utton' in a:
                    btn = getattr(pw, a)
                    log.append('aday buton attr: %s' % a)
                    break
        if btn is not None and hasattr(btn, 'CallEvent'):
            btn.CallEvent()
            log.append('OK: serverSelectButton.CallEvent() -> login ekranina gecmeli')
        else:
            _write('server', '\n'.join(log + ['HATA: OK butonu bulunamadi!']) + '\n')
            return
        _write('server', '\n'.join(log) + '\n')
    except Exception, e:
        _write('server', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 3) LOGIN — UI yolu once (calisan script), paket yolu yedek
# ---------------------------------------------------------------------------
def login(user, pwd):
    try:
        log = ['SCENE=%s' % _scene_name()]
        pw = _pw_by_type('LoginWindow')
        ui_ok = False
        if pw is not None:
            ide = getattr(pw, 'idEditLine', None)
            pwe = getattr(pw, 'pwdEditLine', None)
            lbtn = getattr(pw, 'loginButton', None)
            if ide is not None and pwe is not None and lbtn is not None and hasattr(lbtn, 'CallEvent'):
                ide.SetText(user)
                pwe.SetText(pwd)
                time.sleep(0.3)
                lbtn.CallEvent()
                ui_ok = True
                log.append('OK: UI yolu (idEditLine+pwdEditLine+loginButton.CallEvent)')
        if not ui_ok:
            import net
            net.SetLoginInfo(user, pwd)
            sent = None
            ms = _get_ms()
            if ms is not None and hasattr(ms, 'Connect'):
                try:
                    ms.Connect()
                    sent = 'stream.Connect()'
                except:
                    sent = None
            if sent is None and hasattr(net, 'ConnectToAccountServer'):
                try:
                    net.ConnectToAccountServer()
                    sent = 'net.ConnectToAccountServer()'
                except Exception, e2:
                    _write('login', '\n'.join(log + ['HATA Connect: ' + _fmt_error(e2)]) + '\n')
                    return
            log.append('OK: paket yolu (SetLoginInfo + %s)' % (sent or 'baglanti yok!'))
        log.append('Beklenen: waitfor SelectCharacterWindow 30')
        _write('login', '\n'.join(log) + '\n')
        _write('status', status_text())
    except Exception, e:
        _write('login', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 4) CHARLIST — 5 slot tablosu (net slot data)
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
                name = net.GetAccountCharacterSlotDataString(i, net.ACCOUNT_CHARACTER_SLOT_NAME)
            except:
                name = '?'
            try:
                level = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_LEVEL)
            except:
                level = -1
            try:
                race = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_RACE)
            except:
                race = -1
            job = JOB_NAMES.get(race % 4, '?') if race >= 0 else '?'
            sex = RACE_TABLE.get(race, ('?', '?'))[1]
            lines.append('[slot %d] %s  Lv.%d  %s(%s)  race=%d' % (i, name, level, job, sex, race))
        lines.append('---')
        lines.append('TOPLAM: %d / %d | BOS: %s' % (count, SLOT_COUNT, str(empty_slots)))
        _write('charlist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('charlist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 5) EMPIRE (ilk karakter icin) — paket yolu
# ---------------------------------------------------------------------------
def empire(n):
    try:
        if n not in (1, 2, 3):
            _write('empire', 'HATA: empire 1/2/3 olmali\n')
            return
        import net
        net.SendSelectEmpirePacket(n)
        _write('empire', 'OK: empire=%d gonderildi (cevap: SelectCharacterWindow tazelenir)\n' % n)
    except Exception, e:
        _write('empire', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 6) CREATE — paket yolu (statlar server'da; 30 sn cooldown var)
# ---------------------------------------------------------------------------
def create(slot, name, race, shape):
    try:
        if slot < 0 or slot >= SLOT_COUNT:
            _write('create', 'HATA: slot 0..%d\n' % (SLOT_COUNT - 1))
            return
        if race not in RACE_TABLE:
            _write('create', 'HATA: race 0..8\n')
            return
        if len(name) > 12:
            _write('create', 'HATA: isim > 12 karakter\n')
            return
        import net
        net.SendCreateCharacterPacket(slot, name, race, shape, 0, 0, 0, 0)
        job, sex = RACE_TABLE[race]
        _write('create', 'OK: slot=%d ad=%s race=%d(%s-%s) shape=%d\n'
                         'Kontrol: 30 sn sonra charlist (create cooldown 30sn)\n'
                         % (slot, name, race, job, sex, shape))
    except Exception, e:
        _write('create', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 7) ENTER — UI senkron + TEK DirectEnter (RC12: cift giris NPC'leri oldurur)
# ---------------------------------------------------------------------------
def enter(slot):
    try:
        log = []
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is not None:
            try:
                if hasattr(sw, 'SelectSlot'):
                    sw.SelectSlot(slot)
                    log.append('OK: SelectSlot(%d)' % slot)
            except:
                pass
            try:
                sw.slot = slot
            except:
                pass
        try:
            import net
            net.DirectEnter(slot)
            log.append('OK: DirectEnter(%d) — TEK giris (UI StartGame CAGRILMADI)' % slot)
            log.append('Beklenen: waitfor GameWindow 60')
            _write('enter', '\n'.join(log) + '\n')
        except Exception, e:
            _write('enter', 'HATA DirectEnter: ' + _fmt_error(e) + '\n')
    except Exception, e:
        _write('enter', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 8) STATUS — sahne + baglanti + stream bilgisi
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
    ms = _get_ms()
    return 'SCENE=%s | CONN=%d | stream=%s | t=%s\n' % (
        scene, conn,
        'yakalandi' if ms is not None else 'YOK',
        time.strftime('%H:%M:%S'))

def status():
    _write('status', status_text())

# ---------------------------------------------------------------------------
# modul kaydi — DLL snippet'leri `import maxlib; maxlib.xxx()` der
# ---------------------------------------------------------------------------
import types as _types
import sys as _sys
_maxlib = _sys.modules.get('maxlib', None)
if _maxlib is None:
    _maxlib = _types.ModuleType('maxlib')
for _k, _v in globals().items():
    if _k.startswith('__'):
        continue
    setattr(_maxlib, _k, _v)
_sys.modules['maxlib'] = _maxlib

# ---------------------------------------------------------------------------
# yukleme raporu
# ---------------------------------------------------------------------------
_write('pylib_load',
       'pylib v2.0 yuklendi (ANA THREAD)\n' + status_text())
print '[maxlib] v2.0 yuklendi — selserver/login/charlist/empire/create/enter/status/serverlist'
