# -*- coding: utf-8 -*-
"""
===========================================================================
 PLUSMAXGOD_PyScript.py - MaxExecutor Ana-Thread Komut Kutuphanesi (v4.0)
 "PLUSMAXGOD" SURUMU - pylib v3.2'nin tamami + oyun-ici + kesif komutlari
===========================================================================
 v4.0 DEGISIKLIKLER (oturum 13 - "hepsi calisti" sonrasi GOD MOD genisleme):
   Diskteki dosya adi: pylib.py -> PLUSMAXGOD_PyScript.py (DLL v1.8 cifti;
   eski pylib.py hala YEDEK olarak kabul edilir - BootImport once yenisini
   dener, bulamazsa pylib.py'yi yukler ve surum guard'i uyari basar).

   A) OYUN-ICI KOMUTLAR (kanit: nighttown koleksiyonu 4000+ kullanim +
      cycu.py - kullanici ekosisteminde birebir dogrulanmis API'ler):
      stat()          : seviye/HP/SP/EXP/race/grup/empire/hiz raporu
                        (player.GetStatus + net.GetMainActorRace - cycu)
      pos()           : x/y/z + harita adi (chr.GetPixelPosition - cycu +
                        background.GetCurrentMapName - 34 kanitli kullanim)
      inv(page)       : envanter raporu (player.GetItemIndex 267 kanit +
                        player.INVENTORY_PAGE_SIZE sabiti 147 kanit +
                        item.SelectItem/GetItemName 300/171 kanit)
      equip()         : ekipman raporu (EQUIPMENT_BASE_INDEX slotlari)
      skill()         : beceri raporu (player.GetSkillLevel/GetSkillGrade/
                        IsSkillCoolTime + skill.GetSkillName - kanitli)
      near()          : yakin varlik taramasi VID sweep (chr.GetInstanceType
                        57 kanit + chr.GetNameByVID 52 kanit +
                        nonplayer.GetLevelByVID kanit)
      chat <mesaj>    : net.SendChatPacket (cycu + 117 kanit)
      whisper <k> <m> : net.SendWhisperPacket (9 kanit)
      ride/revive/logout/back : cycu-kanitli hizli eylemler
      zoom <mesafe>   : app.SetCameraMaxDistance (cycu + 13 kanit)
      use <slot>      : net.SendItemUsePacket(slot) (218 kanit!)
      pickup          : player.PickCloseItem (15 kanit)
      drop <slot> <n> : net.SendItemDropPacketNew (cycu; DESTRUKTIF!)
      goto <x> <y>    : chr.MoveToDestPosition(vid,x,y) YURUYUS (36 kanit)
      tp <x> <y>      : chr.SetPixelPosition(x,y) ISINLAMA (211 kanit!)
      key <DIK> <0/1> : player.SetSingleDIKKeyState (368 kanit!)
      attack <0/1>    : player.SetAttackKeyState (100 kanit)

   B) KESIF KOMUTLARI (eski_ai_sohbet'deki 5 yontem, GOD MOD ile dogrulanmis:
      app.GetFileList bu istemcide 0 kullanim - aday olarak denenir;
      app.OpenTextFile ise KANITLI dosya okuma yolu - 24 kanit + cycu):
      pyfiles         : 5 yontemle py dosyalarini bulur (app.GetFileList /
                        sys.modules / pkgutil / disk taramasi / import-probe)
      pydump <ad>     : tek py dosyasini dump\ klasorune doker
      pydumpall       : bulunan BUTUN py'leri dump\ klasorune + INDEX.txt
      pyscan <modul>  : modulun fonksiyonlarini argumanlariyla listeler
      plusquest       : yuklu TUM modulleri tarar -> dump\PLUSQuest_live.txt
                        (pyscanall takma adi ayni isi yapar)

 v3.2 DEGISIKLIKLER (saha testi 7 "enter takiliyor + sahte CREATE_FAILURE"):
   * enter(): UI START yolu ONCELIKLI - SelectSlot + StartGame()/startButton
     (MaximumPyScript_Merged_calisan yolu + kullanici dogrulamasi). Saha
     kaniti: DirectEnter YENI olusan karakterde server tarafindan reddediliyor
     (loading acilip login ekranina geri atiyor), eski karakterde calisiyor.
     DirectEnter artik sadece UI yolu bulunamazsa YEDEK.
   * mkchar(): paket yolu artik SADECE OLUSTUR butonu bulunamazsa yollanir.
     Kanit: cift paket (buton + direkt) -> 1 basari + 1 CREATE_FAILURE: 0
     ("0 karakter yaratilamaz") - karakter zaten olusmustu, 2. paket
     reddedildi. Sahte hata kokten biter.
   * enter(): UI yolu secildiginde DirectEnter CAGRILMAZ (RC12 cift-giris
     yasagi: UI StartGame paketi kendisi yollar, ustune bir de DirectEnter
     NPC yukleme hatasi yapar).
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
DUMP_DIR   = r'C:\MaxExec\dump'   # v4.0: py dump + PLUSQuest_live buraya

# SURUM ISARETI - DLL v1.8 bunu okur (FIX-19). PLUSMAXGOD_PyScript.py
# degistirmeden bu satiri silme/degistirme! Eski pylib (v3.x) major 3
# oldugu icin DLL v1.8 acilista KOSKOCA uyar basar.
PYLIB_VERSION = '4.0'

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

def _dump_name(name):
    """v4.0: dump klasoru yolu (olusturur). py dump + PLUSQuest_live buraya."""
    if not os.path.isdir(DUMP_DIR):
        try:
            os.makedirs(DUMP_DIR)
        except:
            pass
    return os.path.join(DUMP_DIR, name)

def _ingame():
    """v4.0: oyunda miyiz? (cycu.py kanitli desen: GetPixelPosition 'None'
    donmuyorsa ana aktor var demektir). Menulerde/loading'de False."""
    try:
        import net, chr
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            return False
        if not vid or vid <= 0:
            return False
        p = chr.GetPixelPosition(vid)
        if p is None or str(p) == 'None':
            return False
        try:
            if len(p) < 2:
                return False
        except:
            return False
        return True
    except:
        return False

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
# 7) ENTER - UI START yolu ONCELIKLI (v3.2 - saha testi 7 fix)
#    Saha kaniti: DirectEnter yeni olusan karakterde server tarafindan
#    reddediliyor (loading acilip login ekranina geri atiyor), eski
#    karakterde calisiyor. Calisan script + kullanici dogrulamasi: once
#    SelectSlot + StartGame. DirectEnter YEDEK (UI yolu bulunamazsa).
#    RC12 cift-giris yasagi korunur: UI StartGame paketi kendisi yollar,
#    ustune bir de DirectEnter cagirmak NPC yukleme hatasi yapar.
# ---------------------------------------------------------------------------
def enter(slot):
    try:
        log = []
        sw = _pw_by_type('SelectCharacterWindow')
        ui_ok = False
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
            # a) StartGame metodu (start butonunun handler'i - calisan script yolu)
            try:
                if hasattr(sw, 'StartGame'):
                    sw.StartGame()
                    log.append('OK: StartGame() - UI giris yolu')
                    ui_ok = True
            except:
                pass
            # b) start butonu attr'si
            if not ui_ok:
                for attr in ('startButton', 'btnStart', 'btn_start', 'StartButton'):
                    b = getattr(sw, attr, None)
                    if b is not None and hasattr(b, 'CallEvent'):
                        b.CallEvent()
                        log.append('OK: %s.CallEvent() - UI giris yolu' % attr)
                        ui_ok = True
                        break
            # c) ElementDictionary yedegi
            if not ui_ok:
                ed = getattr(sw, 'ElementDictionary', None) or {}
                for key in ('start_button', 'btnStart', 'startButton'):
                    b = ed.get(key, None)
                    if b is not None and hasattr(b, 'CallEvent'):
                        b.CallEvent()
                        log.append('OK: start butonu (ElementDictionary: %s)' % key)
                        ui_ok = True
                        break
        if ui_ok:
            log.append('NOT: DirectEnter cagrilmadi (UI paketi kendisi yollar - cift giris yasagi)')
            log.append('Beklenen: waitfor GameWindow 60')
            _write('enter', '\n'.join(log) + '\n')
            return
        # d) YEDEK: UI yolu bulunamadiysa paket yolu (eski davranis)
        if sw is None:
            log.append('UYARI: SelectCharacterWindow bulunamadi (SCENE=%s) - paket yolu' % _scene_name())
        else:
            log.append('UYARI: StartGame/start butonu bulunamadi - paket yolu')
        try:
            import net
            net.DirectEnter(slot)
            log.append('OK: DirectEnter(%d) - YEDEK paket yolu' % slot)
            log.append('Beklenen: waitfor GameWindow 60')
        except Exception, e:
            log.append('HATA DirectEnter: ' + _fmt_error(e))
        _write('enter', '\n'.join(log) + '\n')
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
# (v3.2 fix: paket yolu SADECE buton bulunamazsa - cift paket sahte
#  CREATE_FAILURE uretir; saha testi 7 kaniti)
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
        # e) paket yolu SADECE buton bulunamadiysa (v3.2 fix)
        #    UI OLUSTUR butonu paketi KENDISI yollar (kanit: cift paket ->
        #    1 basari + 1 CREATE_FAILURE: 0 - karakter zaten olusmustu, 2.
        #    paket reddedildi). Buton bastiktan sonra bir de paket yollamak
        #    SAHTE hata uretir - artik yollanmiyor.
        if btn is None:
            log.append('UYARI: buton yok - paket yolu deneniyor')
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
                log.append('OK: SendCreateCharacterPacket(slot=%d, race=%d, shape=%d) - paket yolu' % (slot, race, target_gender))
            except Exception, e2:
                log.append('HATA: paket yolu hatasi: %s' % _fmt_error(e2))
        else:
            log.append('OK: paket yolu atlandi (buton kendisi yollar - cift paket sahte CREATE_FAILURE yapar)')
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

# ===========================================================================
# v4.0 - OYUN-ICI KOMUTLAR (oyunda iken; `waitfor GameWindow 60` sonrasi)
# Kanit havuzu: nighttown koleksiyonu (4000+ kullanim, kullanici ekosistemi)
# + cycu.py. Her komut _ingame() guard'i ile baslar; menu ekraninda nazik
# hata verir. Butun raporlar results\last_<ad>.txt'ye + konsola duser.
# ===========================================================================

# ---------------------------------------------------------------------------
# stat() - karakter durumu (cycu.py kanitlari: player.GetStatus(LEVEL/HP/
# MAX_HP/SP/MAX_SP/EXP/NEXT_EXP), net.GetMainActorRace/SkillGroup, GetName)
# ---------------------------------------------------------------------------
def stat():
    try:
        if not _ingame():
            _write('stat', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player, net, chr
        L = ['SCENE=%s' % _scene_name()]
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            pass
        try:
            L.append('ad        = %s' % str(player.GetName()))
        except:
            try:
                L.append('ad        = %s' % str(chr.GetNameByVID(vid)))
            except:
                pass
        def _gs(cname):
            try:
                c = getattr(player, cname, None)
                if c is None:
                    return None
                return player.GetStatus(c)
            except:
                return None
        lvl = _gs('LEVEL');   hp = _gs('HP');      mhp = _gs('MAX_HP')
        sp  = _gs('SP');      msp = _gs('MAX_SP')
        ex  = _gs('EXP');     nex = _gs('NEXT_EXP')
        spd = _gs('MOVING_SPEED')
        if lvl is not None: L.append('seviye    = %s' % str(lvl))
        if hp is not None and mhp is not None:
            L.append('HP        = %s / %s  (%d%%)' % (str(hp), str(mhp), _pct(hp, mhp)))
        if sp is not None and msp is not None:
            L.append('SP        = %s / %s  (%d%%)' % (str(sp), str(msp), _pct(sp, msp)))
        if ex is not None and nex is not None:
            L.append('EXP       = %s / %s  (%d%%)' % (str(ex), str(nex), _pct(ex, nex)))
        if spd is not None: L.append('hiz       = %s (MOVING_SPEED)' % str(spd))
        try:
            r = net.GetMainActorRace()
            L.append('race      = %s (%s-%s)' % (str(r), RACE_TABLE.get(r, ('?', '?'))[0], RACE_TABLE.get(r, ('?', '?'))[1]))
        except:
            pass
        try:
            L.append('skill grup= %s' % str(net.GetMainActorSkillGroup()))
        except:
            pass
        try:
            e = net.GetEmpireID()
            L.append('empire    = %d (%s)' % (e, EMPIRE_NAMES.get(e, '?')))
        except:
            pass
        try:
            L.append('biniyor   = %s' % ('evet' if player.IsMountingHorse() else 'hayir'))
        except:
            pass
        L.append('pozisyon  : pos yaz | beceriler: skill yaz')
        _write('stat', '\n'.join(L) + '\n')
    except Exception, e:
        _write('stat', 'HATA ' + _fmt_error(e) + '\n')

def _pct(v, m):
    try:
        fm = float(m)
        if fm <= 0:
            return 0
        return int(float(v) / fm * 100.0)
    except:
        return 0

# ---------------------------------------------------------------------------
# pos() - pozisyon + harita (chr.GetPixelPosition - cycu kaniti;
# background.GetCurrentMapName - nighttown'da 34 kanitli kullanim)
# ---------------------------------------------------------------------------
def pos():
    try:
        if not _ingame():
            _write('pos', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import net, chr, background, player
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            pass
        p = None
        try:
            p = chr.GetPixelPosition(vid)
        except:
            pass
        if p is None or str(p) == 'None':
            try:
                p = player.GetMainCharacterPosition()
            except:
                pass
        if p is None or str(p) == 'None':
            _write('pos', 'HATA: pozisyon okunamadi\n')
            return
        x, y, z = 0, 0, 0
        try:
            x = int(p[0]); y = int(p[1]); z = int(p[2])
        except:
            pass
        L = ['vid    = %s' % str(vid),
             'x      = %d' % x,
             'y      = %d' % y,
             'z      = %d' % z,
             'metre  = (%d, %d)   [client koordinat /100]' % (x // 100, y // 100)]
        mname = ''
        try:
            mname = str(background.GetCurrentMapName())
        except:
            pass
        L.append('harita = %s' % (mname or '?'))
        L.append('isinlanma: tp %d %d | yuruyus: goto %d %d' % (x, y, x, y))
        _write('pos', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pos', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# inv(page) - envanter raporu (player.GetItemIndex 267 kanit +
# player.INVENTORY_PAGE_SIZE 147 kanit + player.GetItemCount 44 kanit +
# item.SelectItem/GetItemName 300/171 kanit)
# ---------------------------------------------------------------------------
def inv(page=0):
    try:
        if not _ingame():
            _write('inv', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player, item
        try:
            page = int(page)
        except:
            page = 0
        psize = 45
        try:
            psize = int(player.INVENTORY_PAGE_SIZE)
        except:
            psize = 45
        base = page * psize
        L = ['envanter sayfa %d  slotlar %d..%d  (INVENTORY_PAGE_SIZE=%d)' % (page, base, base + psize - 1, psize)]
        n = 0
        for i in range(base, base + psize):
            vnum = 0
            try:
                vnum = int(player.GetItemIndex(i))
            except:
                vnum = 0
            if vnum <= 0:
                continue
            n += 1
            cnt = ''
            try:
                c = int(player.GetItemCount(i))
                if c > 1:
                    cnt = ' x%d' % c
            except:
                pass
            iname = _item_name(vnum)
            L.append('  [%3d] vnum=%-7d %s%s' % (i, vnum, iname, cnt))
        L.append('---')
        L.append('dolu slot: %d / %d (bu sayfa)' % (n, psize))
        if n == psize:
            L.append('sayfa dolu gorunuyor - diger sayfa: inv %d' % (page + 1))
        L.append('ekipman: equip | kullan: use <slot> | birak: drop <slot> <adet>')
        _write('inv', '\n'.join(L) + '\n')
    except Exception, e:
        _write('inv', 'HATA ' + _fmt_error(e) + '\n')

def _item_name(vnum):
    """item.SelectItem + GetItemName (300/171 kanit) - isim okunamazsa vnum."""
    try:
        import item
        item.SelectItem(vnum)
        s = str(item.GetItemName())
        return s if s else ('vnum %d' % vnum)
    except:
        return ('vnum %d' % vnum)

# ---------------------------------------------------------------------------
# equip() - ekipman raporu (EQUIPMENT_BASE_INDEX = envanter sonrasi slotlar)
# ---------------------------------------------------------------------------
def equip():
    try:
        if not _ingame():
            _write('equip', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player
        eb = 90
        try:
            eb = int(player.EQUIPMENT_BASE_INDEX)
        except:
            eb = 90
        L = ['ekipman (EQUIPMENT_BASE_INDEX=%d, %d slot)' % (eb, 20)]
        n = 0
        for i in range(eb, eb + 20):
            vnum = 0
            try:
                vnum = int(player.GetItemIndex(i))
            except:
                vnum = 0
            if vnum <= 0:
                continue
            n += 1
            iname = _item_name(vnum)
            L.append('  [%3d] vnum=%-7d %s' % (i, vnum, iname))
        L.append('---')
        L.append('giyili esya: %d' % n)
        _write('equip', '\n'.join(L) + '\n')
    except Exception, e:
        _write('equip', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# skill() - beceri raporu (player.GetSkillLevel/GetSkillGrade/IsSkillCoolTime
# + skill.GetSkillName - nighttown kanitli; slot taramasi + index taramasi)
# ---------------------------------------------------------------------------
def _skill_line(L, slot, idx):
    nm = ''
    try:
        import skill
        nm = str(skill.GetSkillName(idx))
    except:
        pass
    lv = ''
    try:
        import player as _player
        lv = ' Lv%s' % str(int(_player.GetSkillLevel(idx)))
    except:
        pass
    gr = ''
    try:
        import player as _player
        g = int(_player.GetSkillGrade(idx))
        if g > 0:
            gr = ' G%s' % str(g)
    except:
        pass
    cd = ''
    if slot is not None:
        try:
            import player as _player
            cd = '  [CD]' if _player.IsSkillCoolTime(slot) else ''
        except:
            pass
    L.append('  slot=%-3s idx=%-4d %s%s%s%s' % (str(slot if slot is not None else '-'), idx, nm, lv, gr, cd))

def skill():
    try:
        if not _ingame():
            _write('skill', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import player, net
        L = ['SCENE=%s' % _scene_name()]
        race = -1
        grp = -1
        try:
            race = net.GetMainActorRace()
        except:
            pass
        try:
            grp = net.GetMainActorSkillGroup()
        except:
            pass
        L.append('race=%s (%s) | skill grubu=%s' % (str(race), RACE_TABLE.get(race, ('?', '?'))[0], str(grp)))
        found = False
        # A) slot -> index yolu (player.GetSkillIndex varsa - slot bazli CD de verir)
        try:
            for slot in range(1, 33):
                try:
                    idx = int(player.GetSkillIndex(slot))
                except:
                    break
                if idx <= 0:
                    continue
                found = True
                _skill_line(L, slot, idx)
        except:
            pass
        # B) index taramasi (ogrenilmis beceriler: GetSkillLevel > 0)
        if not found:
            L.append('(GetSkillIndex yok - ogrenilmis beceri taramasi:)')
            for idx in range(1, 130):
                try:
                    if int(player.GetSkillLevel(idx)) > 0:
                        _skill_line(L, None, idx)
                except:
                    continue
        L.append('kullanim: player.ClickSkillSlot(<slot>) + IsSkillCoolTime - cycu kanitli')
        _write('skill', '\n'.join(L) + '\n')
    except Exception, e:
        _write('skill', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# near() - yakin varlik taramasi (VID sweep + chr.GetInstanceType 57 kanit +
# chr.GetNameByVID 52 kanit + nonplayer.GetLevelByVID kanit).
# NOT: GetInstanceList bu istemcide 0 kanit (eski AI'nin onerdigi yok) -
# GOD MOD yontemi: 1..2000 VID gezinmesi, tek komutta <10ms.
# ---------------------------------------------------------------------------
def near():
    try:
        if not _ingame():
            _write('near', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import net, chr, nonplayer, player
        vid = 0
        try:
            vid = net.GetMainActorVID()
        except:
            pass
        if vid <= 0:
            try:
                vid = int(player.GetMainCharacterIndex())
            except:
                vid = 0
        myp = chr.GetPixelPosition(vid)
        mx, my = int(myp[0]), int(myp[1])
        tnames = {}
        for c in ('INSTANCE_TYPE_PLAYER', 'INSTANCE_TYPE_NPC', 'INSTANCE_TYPE_ENEMY',
                  'INSTANCE_TYPE_BUILDING', 'INSTANCE_TYPE_OBJECT', 'INSTANCE_TYPE_GATE'):
            try:
                v = int(getattr(chr, c))
                tnames[v] = c.replace('INSTANCE_TYPE_', '')
            except:
                pass
        rows = []
        for v in range(1, 2001):
            if v == vid:
                continue
            try:
                p = chr.GetPixelPosition(v)
                if p is None or str(p) == 'None':
                    continue
                px, py = int(p[0]), int(p[1])
                if px == 0 and py == 0:
                    continue
            except:
                continue
            dx = px - mx; dy = py - my
            d2 = dx * dx + dy * dy
            if d2 > 100000000:
                continue
            rows.append((d2, v, dx, dy))
        rows.sort()
        L = ['benim vid=%d  konum=(%d,%d)  yariicap=10000  bulunan=%d' % (vid, mx, my, len(rows))]
        tc = {}
        for d2, v, dx, dy in rows[:40]:
            tl = '?'
            try:
                t = int(chr.GetInstanceType(v))
                tl = tnames.get(t, str(t))
            except:
                pass
            tc[tl] = tc.get(tl, 0) + 1
            nm = ''
            try:
                nm = str(chr.GetNameByVID(v))
            except:
                pass
            lv = ''
            if tl in ('NPC', 'ENEMY'):
                try:
                    lv = ' Lv%s' % str(nonplayer.GetLevelByVID(v))
                except:
                    pass
            L.append('  vid=%-6d %-7s dist=%-6d d=(%d,%d) %s%s' % (v, tl, int(d2 ** 0.5), dx, dy, nm, lv))
        if len(rows) > 40:
            L.append('  ... +%d varlik daha (yakinlik sirali)' % (len(rows) - 40))
        L.append('---')
        L.append('tip sayilari: %s' % ', '.join(['%s=%d' % (k, tc[k]) for k in tc]))
        L.append('secme: chr.SelectInstance(<vid>) | isim: GetNameByVID - kanitli')
        _write('near', '\n'.join(L) + '\n')
    except Exception, e:
        _write('near', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# chat / whisper - sohbet (net.SendChatPacket cycu + 117 kanit;
# net.SendWhisperPacket 9 kanit). Slash komutlari da chat ile gider.
# ---------------------------------------------------------------------------
def chat(msg):
    try:
        if not _ingame():
            _write('chat', 'HATA: oyunda degilsin (once waitfor GameWindow 60)\n')
            return
        import net
        s = str(msg)
        net.SendChatPacket(s)
        tag = ' (slash komutu)' if s.startswith('/') else ''
        _write('chat', 'OK gonderildi: "%s"%s' % (s[:80], tag))
    except Exception, e:
        _write('chat', 'HATA ' + _fmt_error(e) + '\n')

def whisper(who, msg):
    try:
        if not _ingame():
            _write('whisper', 'HATA: oyunda degilsin\n')
            return
        import net
        net.SendWhisperPacket(str(who), str(msg))
        _write('whisper', 'OK -> %s: "%s"' % (str(who)[:24], str(msg)[:80]))
    except Exception, e:
        _write('whisper', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# HIZLI EYLEMLER (cycu.py kanitlari)
# ---------------------------------------------------------------------------
def ride():
    chat('/ride')            # cycu: net.SendChatPacket('/ride')

def revive():
    try:
        if not _ingame():
            _write('revive', 'HATA: oyunda degilsin\n')
            return
        import chr
        chr.Revive()
        _write('revive', 'OK: chr.Revive() - hayata dondun (cycu kaniti)')
    except Exception, e:
        _write('revive', 'HATA ' + _fmt_error(e) + '\n')

def logout():
    chat('/logout')          # cycu: '/logout' -> sonraki: waitfor SelectCharacterWindow

def back():
    chat('/phase_select')    # cycu: '/phase_select' -> karakter secim ekranina donus

def zoom(dist):
    try:
        d = int(dist)
        import app
        app.SetCameraMaxDistance(d)
        _write('zoom', 'OK: app.SetCameraMaxDistance(%d) (cycu kaniti: 12000)' % d)
    except Exception, e:
        _write('zoom', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# ESYA ISLEMLERI (net.SendItemUsePacket 218 kanit; player.PickCloseItem 15
# kanit; net.SendItemDropPacketNew cycu kaniti - DESTRUKTIF!)
# ---------------------------------------------------------------------------
def use(slot):
    try:
        if not _ingame():
            _write('use', 'HATA: oyunda degilsin\n')
            return
        import net
        s = int(slot)
        net.SendItemUsePacket(s)
        _write('use', 'OK: net.SendItemUsePacket(%d) - slot inv raporundaki numara' % s)
    except Exception, e:
        _write('use', 'HATA ' + _fmt_error(e) + '\n')

def pickup():
    try:
        if not _ingame():
            _write('pickup', 'HATA: oyunda degilsin\n')
            return
        import player
        player.PickCloseItem()
        _write('pickup', 'OK: player.PickCloseItem() - en yakin esya alindi')
    except Exception, e:
        _write('pickup', 'HATA ' + _fmt_error(e) + '\n')

def drop(slot, count):
    try:
        if not _ingame():
            _write('drop', 'HATA: oyunda degilsin\n')
            return
        import net
        s = int(slot); c = int(count)
        net.SendItemDropPacketNew(s, c)
        _write('drop', 'OK: net.SendItemDropPacketNew(%d, %d) - YERDE, geri alinabilir mi kontrol et!' % (s, c))
    except Exception, e:
        _write('drop', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# HAREKET (chr.MoveToDestPosition 36 kanit - yuruyus; chr.SetPixelPosition
# 211 kanit - isinlama, 2-arg desen: chr.SetPixelPosition(x, y))
# ---------------------------------------------------------------------------
def goto(x, y):
    try:
        if not _ingame():
            _write('goto', 'HATA: oyunda degilsin\n')
            return
        import player, chr, net
        vid = 0
        try:
            vid = int(player.GetMainCharacterIndex())
        except:
            try:
                vid = int(net.GetMainActorVID())
            except:
                vid = 0
        chr.MoveToDestPosition(vid, int(x), int(y))
        _write('goto', 'OK: chr.MoveToDestPosition(vid=%d, %d, %d) - yuruyus basladi (36 kanit)' % (vid, int(x), int(y)))
    except Exception, e:
        _write('goto', 'HATA ' + _fmt_error(e) + '\n')

def tp(x, y):
    try:
        if not _ingame():
            _write('tp', 'HATA: oyunda degilsin\n')
            return
        import chr
        chr.SetPixelPosition(int(x), int(y))
        _write('tp', 'OK: chr.SetPixelPosition(%d, %d) - isinlanma (211 kanit; 2-arg desen)' % (int(x), int(y)))
        pos()
    except Exception, e:
        _write('tp', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# GIRDI SIMULASYONU (player.SetSingleDIKKeyState 368 kanit!
# player.SetAttackKeyState 100 kanit) - key/attack
# ---------------------------------------------------------------------------
def key(dikname, down):
    try:
        import app, player
        code = None
        try:
            code = int(dikname)
        except:
            code = getattr(app, 'DIK_' + str(dikname).upper(), None)
        if code is None:
            _write('key', 'HATA: DIK_%s bulunamadi (bilinenler: UP DOWN LEFT RIGHT SPACE LSHIFT W A S D B F5)\n' % str(dikname).upper())
            return
        st = 1 if (int(down) if str(down).isdigit() else 1) else 0
        player.SetSingleDIKKeyState(code, st)
        _write('key', 'OK: SetSingleDIKKeyState(DIK_%s=%s, %s)' % (str(dikname).upper(), str(code), 'BASILI' if st else 'birakildi'))
    except Exception, e:
        _write('key', 'HATA ' + _fmt_error(e) + '\n')

def attack(mode):
    try:
        if not _ingame():
            _write('attack', 'HATA: oyunda degilsin\n')
            return
        import player
        m = 1 if (int(mode) if str(mode).isdigit() else 1) else 0
        player.SetAttackKeyState(m)
        _write('attack', 'OK: SetAttackKeyState(%d) - %s (100 kanit)' % (m, 'SALDIRI BASILI' if m else 'birakildi'))
    except Exception, e:
        _write('attack', 'HATA ' + _fmt_error(e) + '\n')

# ===========================================================================
# v4.0 - KESIF KOMUTLARI (oyundaki Python dosyalarini bulma + dokme + tarama)
# ESKI AI DOGRULARI/YANLISLARI (eski_ai_sohbet.txt) - GOD MOD hukmu:
#   * app.GetFileList("*.py"): eski AI "en iyi yontem" dedi - AMA nighttown
#     koleksiyonunda 0 kullanim -> bu istemcide YOK olabilir. Aday olarak
#     denenir, yoksa diger yontemler devreye girer.
#   * app.OpenTextFile + GetTextFileLineCount + GetTextFileLine: KANITLI
#     (cycu.py + 24 kullanim; kullanici serverinfo.py okumayi dogruladi).
#     Pack sifreli olsa bile okur - ASIL okuma yolu bu.
#   * sys.modules: dogru - yuklu modulleri verir (bedava, risksiz).
#   * pkgutil.iter_modules: embedded importer'da genelde calismaz - denemesi
#     bedava, notla raporlanir.
#   * os.listdir: root.eix sifrelis diskte yoksa bos doner; AMMA client
#     klasoru (nighttown: workspace'te veya temp/tmp'te - kullanici notu)
#     taranarak script/modul koleksiyonlari yakalanir.
# ===========================================================================

_KNOWN_CLIENT_MODULES = (
    # C modulleri (dahili)
    'app', 'net', 'player', 'chr', 'item', 'nonplayer', 'background', 'skill',
    'chat', 'guild', 'messenger', 'quest', 'event', 'wndMgr', 'grp', 'grpText',
    'grpImage', 'ime', 'snd', 'effect', 'fly', 'mood', 'dbg', 'exception',
    'miniMap', 'web', 'profiler', 'pack', 'filer',
    # python tarafli client modulleri (case varyantlariyla)
    'system', 'systemhide', 'constInfo', 'constinfo', 'localeInfo', 'localeinfo',
    'serverInfo', 'serverinfo', 'ServerInfo', 'colorInfo', 'playerSettingModule',
    'playersettingmodule', 'itemdata', 'ui', 'uiScript', 'uiCommon', 'uiTip',
    'uiSystem', 'uiInventory', 'uiCharacter', 'uiTarget', 'uiChat', 'uiGuild',
    'uiMessenger', 'uiQuest', 'uiPrivateShop', 'uiShop', 'uiExchange',
    'uiOption', 'uiHelp', 'uiMap', 'uiAffect', 'uiMiniMap', 'uiGameOption',
    'uiWhisper', 'uiDragonSoul', 'uiPet', 'interfacemodule', 'interfaceModule',
    'game', 'introLogin', 'intrologin', 'introSelect', 'introselect',
    'introCreate', 'introcreate', 'introLoading', 'introloading',
    'introLogo', 'intrologo', 'introEmpire', 'introempire',
    # kullanici ekosistemi (nighttown)
    'm2kmod', 'pyDetour', 'switchbot', 'hackbar',
)

def _discover_pyfiles():
    """5 yontemi de calistirir; dict dondurur. Hepsi guard'li - hata notlara."""
    res = {'app.GetFileList': [], 'sys.modules': [], 'pkgutil': [],
           'disk': [], 'probe': [], 'notlar': [], 'getfilelist_var': False}
    # --- [1] app.GetFileList (eski AI'nin "en iyi" dedigi; bu client'ta 0 kanit)
    try:
        import app
        if hasattr(app, 'GetFileList'):
            res['getfilelist_var'] = True
            try:
                fl = app.GetFileList('*.py')
                for f in fl:
                    try:
                        res['app.GetFileList'].append(str(f))
                    except:
                        pass
            except Exception, e:
                res['notlar'].append('app.GetFileList VAR ama cagri hatasi: ' + _fmt_error(e))
        else:
            res['notlar'].append('app.GetFileList BU ISTEMCIDE YOK (beklenen: 0 kanit) - OpenTextFile yolu kullanilacak')
    except Exception, e:
        res['notlar'].append('app modulu yok?: ' + _fmt_error(e))
    # --- [2] sys.modules (yuklu moduller - eski AI dogru soylemisti)
    try:
        for k in sys.modules.keys():
            try:
                if k and '.' not in k and not k.startswith('_'):
                    res['sys.modules'].append(str(k))
            except:
                pass
        res['sys.modules'].sort()
    except:
        pass
    # --- [3] pkgutil.iter_modules (embedded importer desteklemeyebilir)
    try:
        import pkgutil
        cnt = 0
        for mi in pkgutil.iter_modules():
            try:
                n = getattr(mi, 'name', None) or str(mi)
                res['pkgutil'].append(str(n))
                cnt += 1
                if cnt > 500:
                    break
            except:
                pass
        res['pkgutil'].sort()
    except Exception, e:
        res['notlar'].append('pkgutil.iter_modules kullanilamadi (%s) - embedded importer desteklemiyor olabilir (beklenen)' % _fmt_error(e))
    # --- [4] disk taramasi (cwd + sys.path + TEMP/TMP - kullanici notu:
    #      nighttown workspace'te, degilse temp/tmp'te)
    roots = []
    try:
        roots.append(str(os.getcwd()))
    except:
        pass
    for p in sys.path:
        try:
            if p and os.path.isdir(str(p)):
                roots.append(str(p))
        except:
            pass
    for envk in ('TEMP', 'TMP'):
        try:
            v = os.environ.get(envk, '')
            if v and os.path.isdir(v):
                roots.append(v)
        except:
            pass
    seen = []
    for r in roots:
        if r not in seen:
            seen.append(r)
    disk = []
    try:
        for r in seen[:40]:
            try:
                for fn in os.listdir(r):
                    try:
                        if str(fn).lower().endswith('.py') and str(fn) not in disk:
                            full = os.path.join(r, str(fn))
                            try:
                                if os.path.isfile(full):
                                    disk.append(str(fn))
                            except:
                                disk.append(str(fn))
                    except:
                        pass
            except:
                pass
    except:
        pass
    disk.sort()
    res['disk'] = disk
    res['roots'] = seen
    # --- [5] import-probe (bilinen metin2 modulleri - import denemesi bedava)
    for mname in _KNOWN_CLIENT_MODULES:
        try:
            if mname in sys.modules:
                res['probe'].append(mname)
                continue
            __import__(mname)
            res['probe'].append(mname)
        except:
            pass
    return res

def pyfiles():
    try:
        disc = _discover_pyfiles()
        L = ['py dosyasi kesif raporu (5 yontem)  t=' + time.strftime('%H:%M:%S'), '']
        gfl = disc.get('app.GetFileList', [])
        L.append('[1] app.GetFileList("*.py") - %s' % ('VAR' if disc.get('getfilelist_var') else 'BU ISTEMCIDE YOK (0 kanit - eski AI yanildi)'))
        if gfl:
            for f in gfl[:60]:
                L.append('    ' + f)
            if len(gfl) > 60:
                L.append('    ... +%d daha' % (len(gfl) - 60))
        L.append('')
        sm = disc.get('sys.modules', [])
        L.append('[2] sys.modules (yuklu moduller): %d' % len(sm))
        if sm:
            L.append('    ' + ', '.join(sm[:90]))
        L.append('')
        pk = disc.get('pkgutil', [])
        L.append('[3] pkgutil.iter_modules: %s' % ('%d modul' % len(pk) if pk else 'bos/kullanilamaz (embedded importer - beklenen)'))
        if pk:
            L.append('    ' + ', '.join(pk[:80]))
        L.append('')
        dk = disc.get('disk', [])
        L.append('[4] disk taramasi (cwd + sys.path + TEMP/TMP): %d dosya' % len(dk))
        try:
            for r in disc.get('roots', [])[:12]:
                L.append('    tarama yolu: %s' % r)
        except:
            pass
        if dk:
            for f in dk[:60]:
                L.append('    ' + f)
            if len(dk) > 60:
                L.append('    ... +%d daha' % (len(dk) - 60))
        L.append('')
        pr = disc.get('probe', [])
        L.append('[5] import-probe (bilinen moduller): %d bulundu' % len(pr))
        if pr:
            L.append('    ' + ', '.join(pr))
        L.append('')
        for n in disc.get('notlar', []):
            L.append('NOT: ' + n)
        L.append('')
        L.append('SONRAKI: pydump <ad> (tek dosya) | pydumpall (hepsi) | pyscan <modul> | plusquest')
        _write('pyfiles', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pyfiles', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pydump(name) - tek dosyayi pack'ten/duzenden okuyup dump\ klasorune doker
# (app.OpenTextFile kanitli yolu - cycu GetTextFileTuple deseni)
# ---------------------------------------------------------------------------
def pydump(name=None):
    try:
        import app
        if not name:
            _write('pydump', 'kullanim: pydump <dosya-ad>  (orn. pydump intrologin | adaylar: pyfiles)\n')
            return
        nm = str(name).strip()
        base = nm[:-3] if nm.lower().endswith('.py') else nm
        cands = [nm, base + '.py', base.lower() + '.py', 'root/' + base + '.py']
        handle = None
        used = None
        for c in cands:
            try:
                h = app.OpenTextFile(c)
                if h:
                    handle = h
                    used = c
                    break
            except:
                pass
        if handle is None:
            _write('pydump', 'HATA: acilamadi: %s (denenenler: %s)\nNot: pack icinden okuma icin dosya adini pyfiles/INDEX listesinden al\n' % (nm, ', '.join(cands)))
            return
        n = 0
        try:
            n = int(app.GetTextFileLineCount(handle))
        except:
            n = 0
        cap = 12000
        ln = []
        for i in range(min(n, cap)):
            try:
                ln.append(app.GetTextFileLine(handle, i))
            except:
                ln.append('')
        text = '\n'.join(ln) + '\n'
        safe = ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in base]) or 'adsiz'
        try:
            f = open(_dump_name(safe + '.py'), 'w')
            f.write(text)
            f.close()
        except Exception, e2:
            _write('pydump', 'HATA yazma: %s\n' % _fmt_error(e2))
            return
        L = ['OK: %s -> dump\\%s.py  (%d satir, %d byte)' % (used, safe, len(ln), len(text)),
             '--- ilk 40 satir ---']
        L.extend(ln[:40])
        if len(ln) > 40:
            L.append('... (%d satir daha - tam dosya dump klasorunde)' % (len(ln) - 40))
        _write('pydump', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pydump', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pydumpall() - bulunan TUM py dosyalarini dump\ klasorune + INDEX.txt
# ---------------------------------------------------------------------------
def pydumpall():
    try:
        import app
        disc = _discover_pyfiles()
        files = []
        for k in ('app.GetFileList', 'disk', 'probe'):
            for f in disc.get(k, []):
                if f and f not in files:
                    files.append(str(f))
        cap = 800
        files = files[:cap]
        idx = ['PLUSMAXGOD pydumpall INDEX  t=' + time.strftime('%Y-%m-%d %H:%M:%S'),
               'kaynaklar: app.GetFileList=%d  disk=%d  probe=%d  |  birlesik hedef=%d (cap %d)' % (
                   len(disc.get('app.GetFileList', [])), len(disc.get('disk', [])),
                   len(disc.get('probe', [])), len(files), cap),
               '']
        if disc.get('notlar'):
            for n in disc['notlar']:
                idx.append('NOT: ' + n)
            idx.append('')
        okc = 0
        errc = 0
        errs = []
        c = 0
        for fname in files:
            c += 1
            if (c % 25) == 0:
                try:
                    sys.stdout.write('[PYDUMPALL] ilerleme %d/%d\n' % (c, len(files)))
                except:
                    pass
            base = fname[:-3] if fname.lower().endswith('.py') else fname
            handle = None
            used = None
            for cd in (fname, base + '.py'):
                try:
                    h = app.OpenTextFile(cd)
                    if h:
                        handle = h
                        used = cd
                        break
                except:
                    pass
            if handle is None:
                try:
                    f2 = open(fname, 'r')
                    data = f2.read()
                    f2.close()
                    used = fname + ' (disk open)'
                    ln = data.split('\n')
                    n = len(ln)
                except:
                    errc += 1
                    errs.append(fname)
                    idx.append('OKUNAMADI      %s' % fname)
                    continue
            else:
                try:
                    n = int(app.GetTextFileLineCount(handle))
                except:
                    n = 0
                ln = []
                for i in range(min(n, 12000)):
                    try:
                        ln.append(app.GetTextFileLine(handle, i))
                    except:
                        ln.append('')
            safe = ''.join([ch if (ch.isalnum() or ch in '._-') else '_' for ch in base]) or 'adsiz'
            try:
                f = open(_dump_name(safe + '.py'), 'w')
                f.write('\n'.join(ln) + '\n')
                f.close()
                okc += 1
                idx.append('OK %6d satir  %-30s (kaynak: %s)' % (len(ln), safe + '.py', used))
            except:
                errc += 1
                errs.append(fname)
                idx.append('YAZILAMADI     %s' % fname)
        idx.append('')
        idx.append('ozet: %d OK, %d hata  |  klasor: C:\\MaxExec\\dump' % (okc, errc))
        if errs:
            idx.append('hatalilar: ' + ', '.join(errs[:24]))
        try:
            f = open(_dump_name('INDEX.txt'), 'w')
            f.write('\n'.join(idx) + '\n')
            f.close()
        except:
            pass
        L = ['hedef: %d dosya (app.GetFileList=%d disk=%d probe=%d)' % (
                 len(files), len(disc.get('app.GetFileList', [])),
                 len(disc.get('disk', [])), len(disc.get('probe', []))),
             'ozet: %d OK, %d hata' % (okc, errc),
             'INDEX: C:\\MaxExec\\dump\\INDEX.txt',
             'SONRAKI ADIM: dump klasorunu zipleyip AI\'ya gonder -> PLUSQuest.md guncellenir']
        _write('pydumpall', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pydumpall', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# pyscan(modul) - yuklu modulun fonksiyonlarini argumanlariyla listeler
# (eski AI'nin dir()/globals() onerisi - GOD MOD ile arguman cikarimina
#  yukseltildi: py2 func_code / py3 __code__, C fonksiyonlari isaretlenir)
# ---------------------------------------------------------------------------
def pyscan(modname=None):
    try:
        if not modname:
            _write('pyscan', 'kullanim: pyscan <modul-ad>  (orn. pyscan player | adaylar: pyfiles)\n')
            return
        mn = str(modname).strip()
        mod = sys.modules.get(mn, None)
        if mod is None:
            try:
                mod = __import__(mn)
            except Exception, e:
                _write('pyscan', 'HATA: modul yuklu degil/icebilirmedi: %s (%s)\nIpucu: pyfiles yaz; hepsi icin plusquest\n' % (mn, _fmt_error(e)))
                return
        L = ['modul : %s' % mn,
             'tip   : %s' % type(mod).__name__,
             'dosya : %s' % str(getattr(mod, '__file__', 'dahili/C-modulu')),
             '']
        names = []
        try:
            names = dir(mod)
        except:
            pass
        ncall = 0
        for n in names:
            if n.startswith('__'):
                continue
            try:
                obj = getattr(mod, n)
            except:
                continue
            tn = type(obj).__name__
            sig = ''
            if callable(obj) or tn == 'builtin_function_or_method':
                ncall += 1
                code = None
                try:
                    code = getattr(obj, 'func_code', None)
                except:
                    code = None
                if code is None:
                    try:
                        code = getattr(obj, '__code__', None)
                    except:
                        code = None
                if code is not None:
                    try:
                        k = int(code.co_argcount)
                        sig = '(%s)' % ', '.join(list(code.co_varnames[:k]))
                    except:
                        sig = '(?)'
                else:
                    sig = '(C-fonksiyonu: argumanlar PLUSQuest.md katalogunda)'
            L.append('  %-34s %-26s %s' % (n, tn, sig))
        L.append('')
        L.append('ozet: %d attr, %d callable' % (len(names), ncall))
        _write('pyscan', '\n'.join(L) + '\n')
    except Exception, e:
        _write('pyscan', 'HATA ' + _fmt_error(e) + '\n')

# ---------------------------------------------------------------------------
# plusquest() - yuklu TUM modulleri tarar -> dump\PLUSQuest_live.txt
# (eski AI'nin "sys.modules + dir()" fikrinin GOD MOD uygulamasi:
#  tum moduller, siniflandirilmis, dosyaya dokulen, AI'ya gonderilebilir)
# ---------------------------------------------------------------------------
def plusquest():
    try:
        L = ['=' * 72,
             'PLUSQuest_live - yuklu modullerin CANLI fonksiyon katalogu',
             'uretim: PLUSMAXGOD_PyScript.py v%s  t=%s' % (PYLIB_VERSION, time.strftime('%Y-%m-%d %H:%M:%S')),
             'python: %s' % str(sys.version).split()[0],
             'oyun ici: %s' % ('EVET - tam katalog' if _ingame() else 'HAYIR (menusun: oyunda daha fazla modul yuklenir, oyundayken tekrar calistir)'),
             '=' * 72, '']
        mods = []
        try:
            mods = sorted([m for m in sys.modules.keys() if m and '.' not in m and not m.startswith('_')])
        except:
            pass
        mods = mods[:250]
        tot = 0
        for mn in mods:
            mod = sys.modules.get(mn)
            if mod is None:
                continue
            try:
                names = dir(mod)
            except:
                names = []
            L.append('== %s (%s) ==' % (mn, str(getattr(mod, '__file__', 'dahili/C'))))
            c = 0
            for n in names[:500]:
                if n.startswith('__'):
                    continue
                try:
                    obj = getattr(mod, n)
                except:
                    continue
                tn = type(obj).__name__
                sig = ''
                if callable(obj):
                    code = None
                    try:
                        code = getattr(obj, 'func_code', None) or getattr(obj, '__code__', None)
                    except:
                        code = None
                    if code is not None:
                        try:
                            sig = '(%s)' % ', '.join(list(code.co_varnames[:int(code.co_argcount)]))
                        except:
                            sig = '(?)'
                    else:
                        sig = '(C)'
                L.append('   %-32s %-24s %s' % (n, tn, sig))
                c += 1
                tot += 1
            if len(names) > 500:
                L.append('   ... +%d attr daha' % (len(names) - 500))
            L.append('')
        L.append('ozet: %d modul, %d attr listelendi' % (len(mods), tot))
        out = _dump_name('PLUSQuest_live.txt')
        try:
            f = open(out, 'w')
            f.write('\n'.join(L) + '\n')
            f.close()
        except Exception, e2:
            _write('plusquest', 'HATA yazma: %s\n' % _fmt_error(e2))
            return
        _write('plusquest', 'OK: %d modul, %d attr -> %s\nSONRAKI: bu dosyayi AI\'ya gonder -> PLUSQuest.md kataloguna islenir\n' % (len(mods), tot, out))
    except Exception, e:
        _write('plusquest', 'HATA ' + _fmt_error(e) + '\n')

pyscanall = plusquest   # takma ad - ayni isi yapar

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
       'PLUSMAXGOD_PyScript v%s yuklendi (ANA THREAD)' % PYLIB_VERSION + chr(10) +
       'yeni v4.0 komutlari: stat pos inv equip skill near chat whisper ride revive logout back zoom use pickup drop goto tp key attack | kesif: pyfiles pydump pydumpall pyscan plusquest' + chr(10) +
       'hata izleme hooklari: %s' % (', '.join(_HOOKS_OK) if _HOOKS_OK else 'henuz kurulamadi (status ile tekrar denenir)') + chr(10)
       + status_text())
try:
    sys.stdout.write('[MAXLIB] PLUSMAXGOD_PyScript v%s aktif - DLL v1.8 cifti (help: oyun konsolunda)' % PYLIB_VERSION + chr(10))
except:
    pass
