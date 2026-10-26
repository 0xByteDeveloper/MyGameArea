# -*- coding: utf-8 -*-
"""
===========================================================================
 pylib.py - MaxExecutor Ana-Thread Komut Kutuphanesi (v3.1)
===========================================================================
 v3.1 DEGISIKLIKLER (oturum 11 - saha testi 6 "PYTHON HATASI" sonrasi):
   * _write() artik raporlarini KONSOLA da basar ([CHARLIST]/[JOBLIST]/...
     etiketiyle). DLL v1.6 probe'u sys.stdout'u CONOUT$'a baglar; boylece
     charlist/joblist/newchar/mkchar/selchar/delchar cikislari KONSOLDA
     CANLI gorunur - results klasorune bakmak zorunda degilsin.
   * _log_game_error(): oyun hatasi (yanlis sifre vb.) aninda konsola da
     duser - [OYUN HATASI] satiri, lasterr yazmadan gorunur.
   * status(echo) parametresi: waitfor polling'i artik konsolu spam etmez.
   * lasterr DLL tarafindan pretty-print edildigi icin echo'suz yazar.
   * Konsola giden metinler ASCII'ye cekildi (CP857'de mojibake olmasin).
 v3.0 DEGISIKLIKLER (giris basarili sonrasi istekler - oturum 9):
   * OTO HATA IZLEME: LoginWindow.OnLoginFailure + SelectCharacterWindow
     OnCreateFailure/OnDeleteFailure/OnDeleteSuccess hook'lari (Python-seviye,
     kanitlanmis guvenli - LoginEventTracker/recorder v13-14 deseni).
     Yanlis sifre/arti kodlar results\last_error.txt'ye duser.
   * YENI KOMUTLAR:
       selchar <slot>     : karakter slotu sec (orn. 4. slot)
       newchar            : "karakter olustur" butonuna bas
       joblist            : sinif/cinsiyet tablosu + olusturma ekran durumu
       mkchar <ad> <race> : UI akisi - sinif gez + cinsiyet + isim + OLUSTUR
       empirelist         : bayrak listesi + mevcut empire
       empireui <1-3>     : bayrak sec + ILERLE (UI yolu - kanitlanmis)
       delchar <slot>     : karakter sil butonuna bas + kod dialogu ac
       delcode <kod>      : silme kodunu yaz + ONAYLA
   * login() raporuna "lasterr" ipucu eklendi.
 v2.0 DEGISIKLIKLER (saha testi 25.10 sonrasi):
   * mainStream artik FRAME YURUYUSU ile bulunur (sys._current_frames).
     __main__.mainStream bu client'ta YOK - calisan script
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
   HOOK NOTU: Python-seviye fonksiyon atamasi (class attr) - C++ tarafinda
   hook YOK; bu desen LoginEventTracker_GILSafe + recorder v13/v14'te
   saha-kanitli (0 ms GIL, sadece atama).
===========================================================================
"""

import sys
import time
import os

RESULT_DIR = r'C:\MaxExec\results'

# SURUM ISARETI - DLL v1.6 bunu okur (FIX-19). pylib.py degistirmeden bu
# satiri silme/degistirme! Eski pylib (v2.x) bu isarete sahip degil ve
# DLL acilista KOSKOCA uyar basar.
PYLIB_VERSION = '3.1'

RACE_TABLE = {
    0: ('Warrior', 'E'), 1: ('Ninja', 'K'), 2: ('Sura', 'E'), 3: ('Shaman', 'K'),
    4: ('Warrior', 'K'), 5: ('Ninja', 'E'), 6: ('Sura', 'K'), 7: ('Shaman', 'E'),
    8: ('Wolfman', 'E'),
}
JOB_NAMES = {0: 'Warrior', 1: 'Ninja', 2: 'Sura', 3: 'Shaman', 4: 'Wolfman'}
SLOT_COUNT = 5

# olusturma ekrani donusumleri (MaximumPyScript_Merged_calisan'dan - kanitli)
EMPIRE_NAMES    = {0: 'None', 1: 'Shinsoo', 2: 'Chunjo', 3: 'Jinno'}
RACE_TO_SLOT    = {0: 0, 4: 0, 1: 1, 5: 1, 2: 2, 6: 2, 3: 3, 7: 3, 8: 0}
RACE_TO_GENDER  = {0: 0, 1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0, 8: 0}

# oyun hata kodlari (LoginEventTracker_GILSafe'dan - client'in kendi kodlari)
LOGIN_FAILURE_CODES = {
    'ALREADY':  'Hesap zaten giris yapmis',   'NOID':     'Boyle bir hesap yok',
    'WRONGPWD': 'Yanlis sifre',               'FULL':     'Server dolu',
    'SHUTDOWN': 'Server kapali/bakimda',      'REPAIR':   'Hesap tamir asamasinda',
    'BLOCK':    'Hesap engellendi',           'QUIT':     'Cok fazla hatali deneme',
    'BESAMEKEY':'Cift login anahtari',        'NOTAVAIL': 'Hesap kullanilamaz',
    'NOBILL':   'Abonelik/bakiye yok',        'BLKLOGIN': 'Giris engellendi',
    'WEBBLK':   'Web uzerinden engellendi',   'BADSCLID': 'Yanlis sosyal ID',
    'AGELIMIT': 'Yas/saat sinirlamasi',       'VERSION':  'Client versiyon uyumsuz',
}
CREATE_FAIL_CODES = {0: 'karakter yaratilamaz', 1: 'isim zaten mevcut'}

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

def _write(name, text, echo=True):
    """Sonucu results\last_<ad>.txt'ye yazar; echo=True ise KONSOLA da basar.
    (DLL v1.6 probe'u sys.stdout'u CONOUT$'a baglayinca canli gorunur -
    FIX-28. Yazma/yazdirma hatalari yutulur, komut zinciri bozulmaz.)"""
    try:
        f = open(_res_name(name), 'w')
        f.write(text)
        f.close()
    except:
        pass
    if echo:
        try:
            _ls = text.rstrip('\n').split('\n')
            sys.stdout.write('[%s] %s\n' % (name.upper(), _ls[0]))
            for _l in _ls[1:]:
                sys.stdout.write('%s\n' % _l)
        except:
            pass

def _fmt_error(e):
    return '%s: %s' % (type(e).__name__, str(e))

# ---------------------------------------------------------------------------
# OTO HATA IZLEME - oyun hatalarini results\last_error.txt'ye dusurur
# (LoginEventTracker_GILSafe + recorder v13/v14'te saha-kanitli desen)
# ---------------------------------------------------------------------------
_HOOKS_OK = []

def _log_game_error(kind, detail):
    try:
        f = open(_res_name('error'), 'a')
        f.write('[%s] %s: %s\n' % (time.strftime('%H:%M:%S'), kind, detail))
        f.close()
    except:
        pass
    # v3.1: canli bildirim - hata olur olmaz konsola duser (lasterr'siz)
    try:
        sys.stdout.write('[OYUN HATASI] %s: %s\n' % (kind, detail))
    except:
        pass

def _install_error_hooks():
    """Python-seviye class hook'lari (idempotent - _mx_hooked bayragi).
    Kurulamayan modul varsa sessiz gecer; status() her cagrida tekrar dener."""
    try:
        # 1) LoginWindow.OnLoginFailure(error) - yanlis sifre vb.
        intro = sys.modules.get('introLogin', None) or sys.modules.get('intrologin', None)
        if intro is not None:
            LW = getattr(intro, 'LoginWindow', None)
            orig = getattr(LW, 'OnLoginFailure', None) if LW is not None else None
            if orig is not None and not getattr(orig, '_mx_hooked', False):
                def _h_login_fail(self_lw, *a, **kw):
                    try:
                        code = a[0] if a else '?'
                        _log_game_error('LOGIN_FAILURE',
                                        '%s (%s)' % (code, LOGIN_FAILURE_CODES.get(code, 'bilinmeyen')))
                    except:
                        pass
                    return orig(self_lw, *a, **kw)
                _h_login_fail._mx_hooked = True
                _h_login_fail._mx_orig = orig
                LW.OnLoginFailure = _h_login_fail
                _HOOKS_OK.append('OnLoginFailure')
        # 2) SelectCharacterWindow create/delete sonuclari
        isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
        if isel is not None:
            SW = getattr(isel, 'SelectCharacterWindow', None)
            if SW is not None:
                for mname, kind, mtable in (
                        ('OnCreateFailure', 'CREATE_FAILURE', CREATE_FAIL_CODES),
                        ('OnDeleteFailure', 'DELETE_FAILURE', None),
                        ('OnDeleteSuccess', 'DELETE_SUCCESS', None)):
                    orig = getattr(SW, mname, None)
                    if orig is None or getattr(orig, '_mx_hooked', False):
                        continue
                    def _mk(orig=orig, mname=mname, kind=kind, mtable=mtable):
                        def _h(self_sw, *a, **kw):
                            try:
                                code = a[0] if a else ''
                                desc = mtable.get(code, '') if mtable else ''
                                _log_game_error(kind, '%s %s' % (code, desc))
                            except:
                                pass
                            return orig(self_sw, *a, **kw)
                        _h._mx_hooked = True
                        _h._mx_orig = orig
                        return _h
                    try:
                        setattr(SW, mname, _mk())
                        _HOOKS_OK.append(mname)
                    except:
                        pass
    except:
        pass

def lasterr_text():
    """last_error.txt icerigi (DLL komutu bunu okur; pylib yedek yazar)."""
    try:
        f = open(_res_name('error'), 'r')
        data = f.read()
        f.close()
        return data if data.strip() else 'henuz oyun hatasi yakalanmadi\n'
    except:
        return 'henuz oyun hatasi yaklanmadi\n'

def lasterr():
    # v3.1: echo'suz - DLL komutu last_error.txt'yi zaten pretty-print eder
    _write('lasterr', lasterr_text(), echo=False)

# ---------------------------------------------------------------------------
# mainStream - FRAME YURUYUSU (calisan script teknigi, hooksuz)
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
# sahne cozumleme (hooksuz - tip adi + attr okumasi)
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
# 1) SERVERLIST - sunucu listesi oku (kullanici: "ilk listbox server isimleri")
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
# 2) SELSERVER - server+CH sec, OK butonuna bas (calisan scriptin yolu)
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
# 3) LOGIN - UI yolu once (calisan script), paket yolu yedek
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
        log.append('Sonuc takibi: lasterr (yanlis sifre = LOGIN_FAILURE: WRONGPWD yakalanir)')
        _write('login', '\n'.join(log) + '\n')
        _write('status', status_text())
    except Exception, e:
        _write('login', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 4) CHARLIST - 5 slot tablosu (net slot data)
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
# 5) EMPIRE (ilk karakter icin) - paket yolu
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
# 6) CREATE - paket yolu (statlar server'da; 30 sn cooldown var)
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
# 7) ENTER - UI senkron + TEK DirectEnter (RC12: cift giris NPC'leri oldurur)
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
            log.append('OK: DirectEnter(%d) - TEK giris (UI StartGame CAGRILMADI)' % slot)
            log.append('Beklenen: waitfor GameWindow 60')
            _write('enter', '\n'.join(log) + '\n')
        except Exception, e:
            _write('enter', 'HATA DirectEnter: ' + _fmt_error(e) + '\n')
    except Exception, e:
        _write('enter', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 9) SELCHAR - karakter slotu sec (orn. 4. slotu secmek)
# ---------------------------------------------------------------------------
def selchar(slot):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('selchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'istenen slot=%d' % slot]
        try:
            sw.SelectSlot(slot)
            log.append('OK: SelectSlot(%d)' % slot)
        except Exception, e:
            log.append('UYARI: SelectSlot hatasi (%s) - slot attr atanacak' % _fmt_error(e))
            try:
                sw.slot = slot
                log.append('OK: slot=%d attr atandi' % slot)
            except Exception, e2:
                _write('selchar', '\n'.join(log + ['HATA: slot attr de atilanamadi ' + _fmt_error(e2)]) + '\n')
                return
        time.sleep(0.3)
        try:
            cn = getattr(sw, 'CharacterName', None)
            if cn is not None and hasattr(cn, 'GetText'):
                log.append('secilen karakter: %s' % cn.GetText())
        except:
            pass
        log.append('Kontrol: charlist (slot isaretlenmis olmali)')
        _write('selchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('selchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 10) NEWCHAR - "karakter olustur" butonuna bas
# (btnCreate instance attr None olabilir - ElementDictionary + dir() yedekli,
#  kanitlanmis _click_create_button deseni)
# ---------------------------------------------------------------------------
def newchar():
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('newchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        btn = None
        for attr in ('btnCreate', 'createButton', 'btn_create'):
            b = getattr(sw, attr, None)
            if b is not None and hasattr(b, 'CallEvent'):
                btn = b
                log.append('buton attr: %s' % attr)
                break
        if btn is None:
            ed = getattr(sw, 'ElementDictionary', None) or {}
            for key in ('create_button', 'btnCreate', 'CreateButton'):
                b = ed.get(key, None)
                if b is not None and hasattr(b, 'CallEvent'):
                    btn = b
                    log.append('buton (ElementDictionary): %s' % key)
                    break
        if btn is None:
            for a in dir(sw):
                if 'reate' in a and ('utton' in a or 'utton' in a.lower()):
                    try:
                        b = getattr(sw, a)
                    except:
                        continue
                    if b is not None and hasattr(b, 'CallEvent'):
                        btn = b
                        log.append('aday buton: %s' % a)
                        break
        if btn is None:
            extra = ['HATA: create butonu bulunamadi!']
            try:
                for a in dir(sw):
                    if 'reate' in a or 'utton' in a:
                        extra.append('  aday attr: %s = %s' % (a, type(getattr(sw, a)).__name__))
            except:
                pass
            _write('newchar', '\n'.join(log + extra) + '\n')
            return
        btn.CallEvent()
        log.append('OK: create butonuna basildi')
        log.append('Beklenen: bayrak ekrani (ilk karakter) VEYA olusturma ekrani')
        log.append('Sonraki: status -> empireui <1-3> VEYA mkchar <ad> <race>')
        _write('newchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('newchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 11) JOBLIST - sinif/cinsiyet tablosu + olusturma ekran durumu
# ---------------------------------------------------------------------------
def joblist():
    try:
        lines = ['SCENE=%s' % _scene_name(), '', 'race tablosu (mkchar <ad> <race>):']
        for r in sorted(RACE_TABLE):
            job, sex = RACE_TABLE[r]
            lines.append('  race %d = %s (%s)' % (r, job, 'Erkek' if sex == 'E' else 'Kadin'))
        ccw = _pw_by_type('CreateCharacterWindow')
        if ccw is not None:
            lines.append('')
            lines.append('olusturma ekrani ACIK:')
            lines.append('  mevcut slot(idx) = %s' % str(getattr(ccw, 'slot', '?')))
            lines.append('  gender           = %s' % str(getattr(ccw, 'gender', '?')))
            try:
                edn = getattr(ccw, 'editCharacterName', None)
                if edn is not None and hasattr(edn, 'GetText'):
                    lines.append('  isim kutusu      = "%s"' % edn.GetText())
            except:
                pass
            try:
                gbl = getattr(ccw, 'genderButtonList', [])
                lines.append('  genderButtonList = %d buton' % len(gbl))
            except:
                pass
        else:
            lines.append('')
            lines.append('(olusturma ekrani kapali - newchar ile ac)')
        _write('joblist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('joblist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 12) MKCHAR - UI akisiyla karakter olustur (sinif gez + cinsiyet + isim + OLUSTUR)
# (kanitlanmis do_create_character deseni; paket yolu yedek)
# ---------------------------------------------------------------------------
def mkchar(name, race):
    try:
        if race not in RACE_TABLE:
            _write('mkchar', 'HATA: race 0..8 (joblist yaz)\n')
            return
        if len(name) > 12:
            _write('mkchar', 'HATA: isim > 12 karakter\n')
            return
        log = ['SCENE=%s' % _scene_name(),
               'hedef: ad=%s race=%d (%s-%s)' % (name, race,
                                                 RACE_TABLE[race][0], RACE_TABLE[race][1])]
        ccw = _pw_by_type('CreateCharacterWindow')
        if ccw is None:
            _write('mkchar', '\n'.join(log + ['HATA: CreateCharacterWindow acik degil - once newchar']) + '\n')
            return
        # a) sinif slotuna gez (Warrior->Ninja->Sura->Shaman)
        target_slot = RACE_TO_SLOT.get(race, 3)
        target_gender = RACE_TO_GENDER.get(race, 0)
        cur = getattr(ccw, 'slot', 0)
        log.append('sinif slotu: %d -> %d' % (cur, target_slot))
        try:
            cur = int(cur)
        except:
            cur = 0
        if cur != target_slot:
            incr = getattr(ccw, '_CreateCharacterWindow__IncreaseSlotIndex', None)
            if incr is not None:
                steps = (target_slot - cur) % 4
                for s in range(steps):
                    try:
                        incr()
                        time.sleep(1.0)
                        if int(getattr(ccw, 'slot', -1)) == target_slot:
                            break
                    except:
                        break
            try:
                ccw.slot = target_slot
            except:
                pass
            log.append('OK: sinif slotu = %d' % target_slot)
        # b) cinsiyet
        sel_g = getattr(ccw, '_CreateCharacterWindow__SelectGender', None)
        if sel_g is not None:
            try:
                sel_g(target_gender)
                time.sleep(0.3)
                log.append('OK: __SelectGender(%d)' % target_gender)
            except:
                pass
        try:
            ccw.gender = target_gender
        except:
            pass
        gbl = getattr(ccw, 'genderButtonList', None) or []
        if len(gbl) > target_gender:
            try:
                gbl[target_gender].CallEvent()
                time.sleep(0.3)
                log.append('OK: genderButtonList[%d].CallEvent()' % target_gender)
            except:
                pass
        sbl = getattr(ccw, 'shapeButtonList', None) or []
        if len(sbl) > target_gender:
            try:
                sbl[target_gender].CallEvent()
            except:
                pass
        # c) isim
        edn = getattr(ccw, 'editCharacterName', None)
        if edn is not None and hasattr(edn, 'SetText'):
            edn.SetText(name)
            log.append('OK: isim = "%s"' % name)
        else:
            log.append('UYARI: editCharacterName bulunamadi!')
        # d) OLUSTUR butonu (enter)
        btn = None
        for attr in ('btnCreate', 'createButton', 'btn_create'):
            b = getattr(ccw, attr, None)
            if b is not None and hasattr(b, 'CallEvent'):
                btn = b
                break
        if btn is None:
            ed = getattr(ccw, 'ElementDictionary', None) or {}
            for key in ('create_button', 'btnCreate', 'CreateButton'):
                b = ed.get(key, None)
                if b is not None and hasattr(b, 'CallEvent'):
                    btn = b
                    break
        if btn is not None:
            btn.CallEvent()
            log.append('OK: OLUSTUR butonuna basildi')
        else:
            log.append('UYARI: olustur butonu bulunamadi - sadece paket yolu')
        # e) paket yolu yedek (UI butonu yetmezse sunucuya gider)
        time.sleep(1.0)
        slot = -1
        try:
            import net
            for i in range(SLOT_COUNT):
                pid = 0
                try:
                    pid = net.GetAccountCharacterSlotDataInteger(i, net.ACCOUNT_CHARACTER_SLOT_ID)
                except:
                    pid = 0
                if not pid:
                    slot = i
                    break
        except:
            pass
        if slot < 0:
            slot = 0
        try:
            import net
            use_emp = 0
            try:
                eid = net.GetEmpireID()
                if eid > 0:
                    use_emp = eid
            except:
                pass
            net.SendCreateCharacterPacket(slot, name, race, target_gender, use_emp, 0, 0, 0)
            log.append('OK: SendCreateCharacterPacket(slot=%d, race=%d, shape=%d)' % (slot, race, target_gender))
            log.append('NOT: UI butonu + paket ikisi de gonderildi (cift kayit riski dusuk;')
            log.append('     server ayni isim/second reddeder - 30 sn sonra charlist ile kontrol)')
        except Exception, e2:
            log.append('UYARI: paket yolu hatasi: %s' % _fmt_error(e2))
        log.append('Kontrol: waitfor SelectCharacterWindow 15 -> charlist')
        log.append('Hata olursa: lasterr (CREATE_FAILURE yakalanir)')
        _write('mkchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('mkchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 13) EMPIRELIST - bayrak listesi + mevcut empire
# ---------------------------------------------------------------------------
def empirelist():
    try:
        lines = ['SCENE=%s' % _scene_name()]
        try:
            import net
            eid = net.GetEmpireID()
            lines.append('hesabin empire\'i: %d (%s)' % (eid, EMPIRE_NAMES.get(eid, '?')))
        except Exception, e:
            lines.append('net.GetEmpireID okunamadi: %s' % _fmt_error(e))
        ew = _pw_by_type('SelectEmpireWindow', 'ReselectEmpireWindow')
        if ew is None:
            lines.append('(bayrak ekrani acik degil)')
        else:
            lines.append('bayrak ekrani ACIK (%s):' % type(ew).__name__)
            try:
                lines.append('  empireID = %s' % str(getattr(ew, 'empireID', '?')))
            except:
                pass
            try:
                ed = getattr(ew, 'ElementDictionary', None) or {}
                cnt = 0
                for key, obj in ed.items():
                    try:
                        if type(obj).__name__ == 'EmpireButton':
                            cnt += 1
                            lines.append('  EmpireButton: key=%s arg=%s' % (key, str(getattr(obj, 'arg', '?'))))
                    except:
                        pass
                if cnt == 0:
                    lines.append('  (ElementDictionary\'de EmpireButton yok - OnSelectEmpire ile secilecek)')
            except:
                pass
        lines.append('')
        lines.append('bayrak tablosu: 1=Shinsoo (kirmizi) 2=Chunjo (sari) 3=Jinno (mavi)')
        try:
            isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
            if isel is not None:
                en = getattr(isel, 'EMPIRE_NAME', None)
                if en:
                    lines.append('client isimleri: %s' % str(en))
        except:
            pass
        _write('empirelist', '\n'.join(lines) + '\n')
    except Exception, e:
        _write('empirelist', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 14) EMPIREUI - bayrak sec + ILERLE (kanitlanmis do_select_empire deseni)
# ---------------------------------------------------------------------------
def empireui(n):
    try:
        if n not in (1, 2, 3):
            _write('empireui', 'HATA: empire 1/2/3\n')
            return
        ew = _pw_by_type('SelectEmpireWindow', 'ReselectEmpireWindow')
        if ew is None:
            _write('empireui', 'HATA: bayrak ekrani acik degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'hedef empire=%d (%s)' % (n, EMPIRE_NAMES.get(n, '?'))]
        # a) OnSelectEmpire - bayragi isaretle
        try:
            ew.OnSelectEmpire(n)
            time.sleep(0.5)
            log.append('OK: OnSelectEmpire(%d)' % n)
        except Exception, e:
            log.append('UYARI: OnSelectEmpire hatasi: %s' % _fmt_error(e))
        try:
            ew.empireID = n
            log.append('OK: empireID=%d atandi' % n)
        except:
            pass
        # b) EmpireButton'a tikla (ElementDictionary, arg eslesmeli)
        clicked = False
        try:
            ed = getattr(ew, 'ElementDictionary', None) or {}
            for key, obj in ed.items():
                try:
                    if type(obj).__name__ == 'EmpireButton' and getattr(obj, 'arg', -1) == n:
                        obj.CallEvent()
                        clicked = True
                        time.sleep(1.0)
                        log.append('OK: EmpireButton(%s).CallEvent()' % key)
                        break
                except:
                    pass
        except:
            pass
        if not clicked:
            log.append('(EmpireButton bulunamadi/eslesmedi - OnSelectEmpire yeterli olabilir)')
        # c) ILERLE - ClickSelectButton
        done = False
        try:
            ew.ClickSelectButton()
            done = True
            log.append('OK: ClickSelectButton() - ilerlendi')
        except Exception, e:
            log.append('UYARI: ClickSelectButton hatasi: %s' % _fmt_error(e))
        if not done:
            try:
                ed = getattr(ew, 'ElementDictionary', None) or {}
                sb = ed.get('select_button', None)
                if sb is not None and hasattr(sb, 'CallEvent'):
                    sb.CallEvent()
                    log.append('OK: select_button.CallEvent() - ilerlendi')
            except:
                pass
        # d) paket yolu yedegi (ekran gecmezse)
        time.sleep(1.5)
        scene_now = _scene_name()
        log.append('simdi sahne: %s' % scene_now)
        if 'Empire' in scene_now:
            try:
                import net
                net.SendSelectEmpirePacket(n)
                log.append('YEDEK: SendSelectEmpirePacket(%d) gonderildi' % n)
            except Exception, e:
                log.append('UYARI: paket yolu hatasi: %s' % _fmt_error(e))
        log.append('Beklenen: olusturma ekrani (yoksa bayrak kayitliyse direkt olusturma)')
        log.append('Sonraki: status -> mkchar <ad> <race>')
        _write('empireui', '\n'.join(log) + '\n')
    except Exception, e:
        _write('empireui', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 15) DELCHAR - karakter sil akisi: slot sec + silme sorusu + kod dialogu AC
# (kanitlanmis chardeleter v8 deseni - CallEvent YOK, dogrudan metodlar)
# ---------------------------------------------------------------------------
def delchar(slot):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('delchar', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name(), 'hedef slot=%d' % slot]
        # dialog temizligi (once acik kalan kutular kapat)
        try:
            pib = getattr(sw, 'privateInputBoard', None)
            if pib is not None:
                try:
                    sw.CancelInputPrivateCode()
                except:
                    pass
                log.append('eski kod dialogu kapatildi')
        except:
            pass
        # 1) slot sec
        try:
            sw.SelectSlot(slot)
            log.append('OK: SelectSlot(%d)' % slot)
        except Exception, e:
            log.append('UYARI: SelectSlot hatasi: %s' % _fmt_error(e))
        time.sleep(0.5)
        # 2) silme sorusu dialogu
        try:
            sw.PopupDeleteQuestion()
            log.append('OK: PopupDeleteQuestion() - "karakteri sil" sorusu')
        except Exception, e:
            log.append('UYARI: PopupDeleteQuestion hatasi: %s' % _fmt_error(e))
        time.sleep(0.5)
        # 3) kod dialogu
        try:
            sw.InputPrivateCode()
            log.append('OK: InputPrivateCode() - kod dialogu ACILDI')
            log.append('SONRA: delcode <silme-kodu> yaz')
        except Exception, e:
            log.append('HATA: InputPrivateCode hatasi: %s' % _fmt_error(e))
        # NOT_NEED_DELETE_CODE bayragi (kod istemeyen serverlar)
        try:
            isel = sys.modules.get('introSelect', None) or sys.modules.get('introselect', None)
            if isel is not None:
                if getattr(isel, 'NOT_NEED_DELETE_CODE', False):
                    log.append('NOT: bu server silme kodu istemiyor olabilir (NOT_NEED_DELETE_CODE=1)')
        except:
            pass
        _write('delchar', '\n'.join(log) + '\n')
    except Exception, e:
        _write('delchar', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# 16) DELCODE - silme kodunu yaz + ONAYLA (chardeleter v8 - inputValue EditLine)
# ---------------------------------------------------------------------------
def delcode(code):
    try:
        sw = _pw_by_type('SelectCharacterWindow')
        if sw is None:
            _write('delcode', 'HATA: SelectCharacterWindow sahnesinde degil (SCENE=%s)\n' % _scene_name())
            return
        log = ['SCENE=%s' % _scene_name()]
        pib = getattr(sw, 'privateInputBoard', None)
        if pib is None:
            try:
                sw.InputPrivateCode()
                time.sleep(0.5)
            except:
                pass
            pib = getattr(sw, 'privateInputBoard', None)
        if pib is None:
            _write('delcode', '\n'.join(log + ['HATA: kod dialogu acik degil - once delchar <slot>']) + '\n')
            return
        log.append('kod dialogu: %s' % type(pib).__name__)
        # EditLine bul (inputValue oncelikli - chardeleter kaniti)
        edit = None
        for attr in ('inputValue', 'inputBoard', 'editLine', 'edit', 'input', 'textEdit'):
            obj = getattr(pib, attr, None)
            if obj is not None and hasattr(obj, 'SetText') and hasattr(obj, 'GetText'):
                tn = type(obj).__name__
                if 'Button' not in tn and 'TextLine' not in tn:
                    edit = obj
                    log.append('EditLine: %s (%s)' % (attr, tn))
                    break
        if edit is None:
            try:
                for attr in dir(pib):
                    if attr.startswith('__'):
                        continue
                    try:
                        obj = getattr(pib, attr)
                    except:
                        continue
                    if obj is not None and hasattr(obj, 'SetText') and hasattr(obj, 'GetText'):
                        tn = type(obj).__name__
                        if 'Button' not in tn and 'TextLine' not in tn:
                            edit = obj
                            log.append('EditLine (dir): %s (%s)' % (attr, tn))
                            break
            except:
                pass
        if edit is None:
            _write('delcode', '\n'.join(log + ['HATA: kod giris kutusu bulunamadi!']) + '\n')
            return
        edit.SetText(str(code))
        try:
            wr = edit.GetText()
            log.append('OK: kod yazildi: "%s"' % wr)
        except:
            log.append('OK: kod yazildi')
        time.sleep(0.3)
        # ONAYLA
        try:
            sw.AcceptInputPrivateCode()
            log.append('OK: AcceptInputPrivateCode() - ONAYLANDI')
        except Exception, e:
            log.append('HATA: AcceptInputPrivateCode hatasi: %s' % _fmt_error(e))
        time.sleep(1.0)
        log.append('Sonuc: lasterr (DELETE_SUCCESS/DELETE_FAILURE) + charlist')
        _write('delcode', '\n'.join(log) + '\n')
    except Exception, e:
        _write('delcode', 'HATA ' + _fmt_error(e) + '\n')
# ---------------------------------------------------------------------------
# 8) STATUS - sahne + baglanti + stream bilgisi (+ lazy hook kurulumu)
# ---------------------------------------------------------------------------
def status_text():
    if len(_HOOKS_OK) < 4:
        _install_error_hooks()   # moduller sonra yuklenmis olabilir - tekrar dene
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

def status(echo=True):
    # v3.1: waitfor polling'i echo=0 ile cagirir - konsol spami olmaz
    _write('status', status_text(), echo=echo)

# ---------------------------------------------------------------------------
# modul kaydi - DLL snippet'leri `import maxlib; maxlib.xxx()` der
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
_install_error_hooks()   # oto hata izleme - yanlis sifre vb. last_error.txt'ye
_write('pylib_load',
       'pylib v%s yuklendi (ANA THREAD)' % PYLIB_VERSION + chr(10) +
       'hata izleme hooklari: %s' % (', '.join(_HOOKS_OK) if _HOOKS_OK else 'henuz kurulamadi (status ile tekrar denenir)') + chr(10)
       + status_text())
try:
    sys.stdout.write('[MAXLIB] pylib v%s aktif - komutlar hazir (DLL v1.6 cifti)' % PYLIB_VERSION + chr(10))
except:
    pass
