# MaximumPyScript_Merged
# -*- coding: utf-8 -*-
#
# Metin2 Ultimate Controller v18-STABLE (MaxExecutor paketi)
# STABLE YAMALARI: RC12 tek-giris (NPC fix) | RC13 loading-recovery kilidi | RC14 GameWindow kaniti
# Kullanim: py exec(open('C:/MaximumPyScript_Merged.py').read())
#
# v17: İki sorun düzeltmesi:
#   - Sorun 1: Oyundan karakter seçime dönünce klavye çalışmıyor
#     → _loop()'da GAME→menü geçişinde SetFocus() çağır
#   - Sorun 2: İkinci login'de "Login..."de kalıyor
#     → KillFocus() KALDIRILDI (login response'u engelliyordu)
#     → LoginWindow'a SetFocus() SetText'ten ÖNCE çağır
#     → _login_success global'ini do_login başında resetle
#   - Hooklar: AKTIF (SetPhaseWindow + LoginWindow)
#   - Sahne: _tracked_phase_window'dan oku (GIL-safe)
#   - SHM komut okuma: AKTIF (shm.get_command)
#   - sd.detect(): SADECE _resolve_scene_from_window kullanilir (GIL-safe)
#
import sys
import time
import struct
import os

# ============================================================
#  SABITLER
# ============================================================
COMMAND_POLL       = 2.0   # Menu mode poll (was 0.3 - too aggressive, blocks keyboard)
RETRY_INTERVAL     = 600
MAX_CREATE_CHARS   = 4
MAX_RETRIES        = 3
CHAR_DATA_WAIT     = 4.0
CHAR_DATA_RETRIES  = 5
# CHAR_AUTO_REFRESH: KALDIRILDI - karakter seciminde auto-refresh GIL bloke eder
STEP_WAIT          = 1.5
SCENE_CHECK_INTERVAL = 0.5

# Oyun ici - TAMAMEN pasif
IN_GAME_POLL       = 10.0
CONNECT_CHECK_INT  = 5.0

SHM_SIZE       = 16384
LOG_BUF_SIZE   = 2048

OFF_MAGIC        = 0
OFF_VERSION      = 4
OFF_STATUS       = 8
OFF_COMMAND      = 12
OFF_PID          = 16
OFF_SCENE        = 20
OFF_CHAR_COUNT   = 24
OFF_ERROR        = 28
OFF_PARAM1       = 32
OFF_PARAM2       = 36
OFF_PARAM3       = 40
OFF_PARAM4       = 44
OFF_FLAGS        = 48
OFF_SRV_COUNT    = 52
OFF_CH_COUNT     = 56
OFF_SEL_SRV      = 60
OFF_SEL_CH       = 64
OFF_CR_RACE      = 68
OFF_CR_EMPIRE    = 72
OFF_CR_GENDER    = 76
OFF_CR_COUNT     = 80
OFF_TARGET_SLOT  = 84
OFF_AUTO_STATE   = 88
OFF_CHAR_STRATEGY= 92
OFF_SRV_NAMES    = 96
OFF_CH_NAMES     = 224
OFF_CHAR_INFO    = 352
OFF_CHAR_NAMES   = 416
OFF_CREATE_NAME  = 480
OFF_TARGET_NAME  = 544
OFF_USERNAME     = 608
OFF_PASSWORD     = 672
OFF_TARGET_JOB   = 736
OFF_CREATE_IF_EXISTS = 740
OFF_LOG_BUF      = 800
OFF_LOG_WPOS     = 2848
OFF_LOG_RPOS     = 2852

MAGIC   = 0x4D415831
VERSION = 14

ST_IDLE          = 0
ST_READY         = 1
ST_AT_SERVER_SEL = 10
ST_AT_LOGIN      = 20
ST_LOGGING_IN    = 21
ST_LOGIN_OK      = 22
ST_LOGIN_FAIL    = 23
ST_CONNECT_FAIL  = 24
ST_AT_CHAR_SEL   = 30
ST_CREATING_CHAR = 31
ST_CHAR_CREATED  = 32
ST_CHAR_FAIL     = 33
ST_AT_EMPIRE_SEL = 40
ST_EMPIRE_DONE   = 41
ST_AT_CHAR_CREATE= 42
ST_ENTERING_GAME = 50
ST_IN_GAME       = 51
ST_ENTER_FAIL    = 52
ST_STEP_SERVER   = 60
ST_STEP_LOGIN    = 61
ST_STEP_CHARSEL  = 62
ST_STEP_COMPLETE = 63
ST_ERROR         = 90
ST_BUSY          = 91
ST_MAINTENANCE   = 92
ST_RECOVERING    = 93

CMD_NONE         = 0
CMD_SELECT_SERVER= 1
CMD_LOGIN        = 2
CMD_SELECT_CHAR  = 3
CMD_CREATE_CHAR  = 4
CMD_ENTER_GAME   = 5
CMD_SELECT_EMPIRE= 6
CMD_REFRESH      = 7
CMD_AUTO_ALL     = 8
CMD_SCENE_CHANGE = 9
CMD_COMPLETE_ALL = 10
CMD_RESTART      = 11
CMD_STOP         = 99

ERR_NONE         = 0
ERR_TIMEOUT      = 1
ERR_LOGIN_FAIL   = 2
ERR_CONNECT_FAIL = 3
ERR_CHAR_FAIL    = 4
ERR_ENTER_FAIL   = 5
ERR_MAINTENANCE  = 6
ERR_SCENE_STUCK  = 7
ERR_NAME_TAKEN   = 8
ERR_UNKNOWN      = 99

SCENE_UNKNOWN    = 0
SCENE_LOGIN      = 1
SCENE_SERVER_SEL = 2
SCENE_CHAR_SEL   = 3
SCENE_EMPIRE_SEL = 4
SCENE_CHAR_CREATE= 5
SCENE_GAME       = 6
SCENE_LOADING    = 7

SCENE_NAMES = {
    SCENE_UNKNOWN:     'Unknown',
    SCENE_LOGIN:       'Login',
    SCENE_SERVER_SEL:  'Server Select',
    SCENE_CHAR_SEL:    'Character Select',
    SCENE_EMPIRE_SEL:  'Empire Select',
    SCENE_CHAR_CREATE: 'Character Create',
    SCENE_GAME:        'In Game',
    SCENE_LOADING:     'Loading',
}

FLAG_RECORDING   = 0x01
FLAG_AUTO_MODE   = 0x02
FLAG_RANDOM_NAME = 0x04
FLAG_HAS_ERROR   = 0x08

AUTO_IDLE        = 0
AUTO_RUNNING     = 1
AUTO_WAITING     = 2
AUTO_ERROR       = 3
AUTO_COMPLETE    = 4

STRAT_BY_SLOT     = 1
STRAT_BY_NAME     = 2
STRAT_MAX_LEVEL   = 3
STRAT_MIN_LEVEL   = 4
STRAT_BY_JOB      = 5
STRAT_FIRST_SLOT  = 6

JOB_NAMES = {
    0: 'Warrior', 1: 'Ninja', 2: 'Sura', 3: 'Shaman',
    4: 'Warrior', 5: 'Ninja', 6: 'Sura', 7: 'Shaman',
    8: 'Lycan',
}
GENDER_NAMES = {0:'M',1:'F',2:'M',3:'F',4:'F',5:'M',6:'F',7:'M',8:'M'}
EMPIRE_NAMES = {0:'None', 1:'Shinsoo', 2:'Chunjo', 3:'Jinno'}
RACE_TO_SLOT   = {0:0,4:0, 1:1,5:1, 2:2,6:2, 3:3,7:3, 8:0}
RACE_TO_GENDER = {0:0,1:1,2:0,3:1,4:1,5:0,6:1,7:0,8:0}

SLOT_ID   = 0
SLOT_NAME = 1
SLOT_RACE = 2
SLOT_LEVEL= 3

# ============================================================
#  LoginEventTracker GLOBALS
# ============================================================
_last_login_error = ""      # LOGIN_FAILURE C++ code (NOID, WRONGPWD)
_last_popup_msg = ""        # Localized popup message
_login_success = False
_event_history = []         # Last 50 events
_event_count = 0

# --- SceneTracker GLOBALS ---
_tracked_phase_window = None  # Set by SetPhaseWindow hook
_tracked_main_stream = None   # Set by SetPhaseWindow hook

# --- Login Failure Codes ---
LOGIN_FAILURE_CODES = {
    "ALREADY": "Already logged in",
    "NOID": "Account not found",
    "WRONGPWD": "Wrong password",
    "FULL": "Server full",
    "SHUTDOWN": "Server shutdown",
    "REPAIR": "Account repair",
    "BLOCK": "Account blocked",
    "WRONGMAT": "Wrong matrix card",
    "QUIT": "Too many failures - exit",
    "BESAMEKEY": "Duplicate login key",
    "NOTAVAIL": "Account not available",
    "NOBILL": "No billing",
    "BLKLOGIN": "Login blocked",
    "WEBBLK": "Web blocked",
    "BADSCLID": "Wrong social ID",
    "AGELIMIT": "Age/time limit",
}

# --- Phase Window to Scene Map ---
PHASE_WINDOW_MAP = {
    "LoginWindow": SCENE_LOGIN,
    "SelectCharacterWindow": SCENE_CHAR_SEL,
    "CreateCharacterWindow": SCENE_CHAR_CREATE,
    "SelectEmpireWindow": SCENE_EMPIRE_SEL,
    "ReselectEmpireWindow": SCENE_EMPIRE_SEL,
    "GameWindow": SCENE_GAME,
    "LogoWindow": SCENE_LOGIN,
    "LoadingWindow": SCENE_LOADING,
}

# ============================================================
#  PYTHON 2/3
# ============================================================
try:
    unicode
except NameError:
    unicode = str

# ============================================================
#  MODULLER
# ============================================================
app_mod      = sys.modules.get('app', None)
chat_mod     = sys.modules.get('chat', None)
net_mod      = sys.modules.get('net', None)
dbg_mod      = sys.modules.get('dbg', None)
ui_mod       = sys.modules.get('ui', None)
uiCommon_mod = sys.modules.get('uiCommon', None)
player_mod   = sys.modules.get('player', None)

has_ctypes = False
try:
    import ctypes
    has_ctypes = True
except:
    pass
has_mmap = False
try:
    import mmap
    has_mmap = True
except:
    pass

# ============================================================
#  YARDIMCI
# ============================================================
def safe_str(v):
    if v is None: return ''
    if isinstance(v, str): return v
    if isinstance(v, unicode):
        for enc in ('cp1254','utf-8','latin-1'):
            try: return v.encode(enc)
            except: pass
        try: return v.encode('ascii','replace')
        except: return repr(v)
    try: return str(v)
    except: return '???'

def clean_text(v):
    s = safe_str(v)
    s = s.replace('\r',' ').replace('\n',' ')
    s = ' '.join(s.split())
    return s.strip()

def append_log(msg):
    """NO-OP: Tum loglama kaldirildi - GIL bloke eder."""
    pass

def _record_login_event(event_type, detail="", popup_msg=None):
    """Record event to LoginEventTracker globals."""
    global _last_login_error, _last_popup_msg, _login_success
    global _event_count, _event_history
    _event_count += 1
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    if event_type == "LOGIN_SUCCESS":
        _login_success = True
        _last_login_error = ""
    elif event_type.startswith("LOGIN_FAILURE"):
        _login_success = False
        _last_login_error = str(detail)
    elif event_type == "CONNECT_FAILURE":
        _login_success = False
    if popup_msg:
        _last_popup_msg = str(popup_msg)
    desc = LOGIN_FAILURE_CODES.get(detail, detail) if detail else detail
    _event_history.append((ts, event_type, detail, desc))
    if len(_event_history) > 50:
        _event_history.pop(0)

def make_random_name():
    try:
        import random as _r
        _r.seed(int(time.time()*1000) % 999999)
        pre = ['Ael','Zar','Kri','Myr','Vel','Xan','Dra','Fio','Lun','Ren',
               'Syl','Tyr','Vor','Ash','Bri','Cel','Dor','Eri','Fae','Gor']
        mid = ['ma','ri','lo','na','ke','si','da','ve','el','or',
               'in','ar','la','en','mi','ro','li','ta','ka','ze']
        suf = ['a','is','on','ia','el','ra','yn','ne','da','la']
        nm = _r.choice(pre)+_r.choice(mid)+_r.choice(suf)+str(_r.randint(10,999))
        if len(nm)>16: nm=nm[:16]
        return nm[0].upper()+nm[1:].lower()
    except:
        seed = int(time.time()*1000)%999999
        chars='abcdefghijklmnopqrstuvwxyz'
        nm=''
        v=seed
        for k in range(8):
            v=(v*1103515245+12345)%2147483647
            nm=nm+chars[v%26]
        v2=(v*1103515245+12345)%2147483647
        nm=nm+str(v2%900+100)
        return nm[0].upper()+nm[1:]

# ============================================================
#  LOCALE
# ============================================================
# LOCALE: KALDIRILDI - chat hook yok, login hooks ERROR_LOCALE dict kullanir
# build_locale_reverse / lookup_locale_key / get_locale_text gereksiz

# ============================================================
#  SHARED MEMORY
# ============================================================
class SharedMemoryManager(object):
    def __init__(self):
        self.shm = None
        self.shm_name = ''
        self.ready = False
        self._pBuf = None
        self._hMap = None
        self._log_lock = False

    def create(self):
        pid = os.getpid()
        self.shm_name = 'Control_%d' % pid
        try:
            if has_mmap:
                self.shm = mmap.mmap(-1, SHM_SIZE, self.shm_name)
                self.shm.seek(0)
                self.shm.write(b'\x00' * SHM_SIZE)
                self._w32(OFF_MAGIC, MAGIC)
                self._w32(OFF_VERSION, VERSION)
                self._w32(OFF_PID, pid)
                self._w32(OFF_STATUS, ST_IDLE)
                self._w32(OFF_COMMAND, CMD_NONE)
                self._w32(OFF_ERROR, ERR_NONE)
                self._w32(OFF_LOG_WPOS, 0)
                self._w32(OFF_LOG_RPOS, 0)
                self.ready = True
                append_log('SHM olusturuldu: %s (PID=%d)' % (self.shm_name, pid))
                return True
            elif has_ctypes:
                kernel32 = ctypes.windll.kernel32
                INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
                hMap = kernel32.CreateFileMappingA(
                    INVALID_HANDLE_VALUE, None, 0x04, 0, SHM_SIZE,
                    self.shm_name.encode('ascii'))
                if not hMap: return False
                self._hMap = hMap
                pBuf = kernel32.MapViewOfFile(hMap, 0xF001F, 0, 0, SHM_SIZE)
                if not pBuf: return False
                self._pBuf = pBuf
                ctypes.memset(pBuf, 0, SHM_SIZE)
                self._cw32(OFF_MAGIC, MAGIC)
                self._cw32(OFF_VERSION, VERSION)
                self._cw32(OFF_PID, pid)
                self._cw32(OFF_STATUS, ST_IDLE)
                self._cw32(OFF_COMMAND, CMD_NONE)
                self._cw32(OFF_ERROR, ERR_NONE)
                self._cw32(OFF_LOG_WPOS, 0)
                self._cw32(OFF_LOG_RPOS, 0)
                self.ready = True
                append_log('SHM (ctypes): %s (PID=%d)' % (self.shm_name, pid))
                return True
        except Exception:
            append_log('SHM HATA: %s' % str(sys.exc_info()[1]))
        return False

    def _w32(self,o,v):
        if self.shm:
            self.shm.seek(o)
            self.shm.write(struct.pack('<I', v & 0xFFFFFFFF))
    def _r32(self,o):
        if self.shm:
            self.shm.seek(o)
            d = self.shm.read(4)
            if len(d)==4: return struct.unpack('<I',d)[0]
        return 0
    def _wstr(self,o,s,ml):
        if self.shm:
            bs = safe_str(s)
            if isinstance(bs, unicode): bs = bs.encode('utf-8','replace')
            if len(bs)>=ml: bs = bs[:ml-1]
            bs = bs + b'\x00'*(ml-len(bs))
            self.shm.seek(o)
            self.shm.write(bs[:ml])
    def _rstr(self,o,ml):
        if self.shm:
            self.shm.seek(o)
            d = self.shm.read(ml)
            i = d.find(b'\x00')
            if i>=0: d = d[:i]
            try: return d.decode('utf-8','replace')
            except: return str(d)
        return ''
    def _cw32(self,o,v):
        if self._pBuf: ctypes.c_uint32.from_address(self._pBuf+o).value = v & 0xFFFFFFFF
    def _cr32(self,o):
        if self._pBuf: return ctypes.c_uint32.from_address(self._pBuf+o).value
        return 0
    def _cwstr(self,o,s,ml):
        if self._pBuf:
            bs = safe_str(s)
            if isinstance(bs, unicode): bs = bs.encode('utf-8','replace')
            if len(bs)>=ml: bs = bs[:ml-1]
            bs = bs + b'\x00'*(ml-len(bs))
            ctypes.memmove(self._pBuf+o, bs[:ml], ml)
    def _crstr(self,o,ml):
        if self._pBuf:
            buf = (ctypes.c_char*ml).from_address(self._pBuf+o)
            d = bytes(buf)
            i = d.find(b'\x00')
            if i>=0: d = d[:i]
            try: return d.decode('utf-8','replace')
            except: return str(d)
        return ''

    def w32(self,o,v):
        if self.shm: self._w32(o,v)
        elif self._pBuf: self._cw32(o,v)
    def r32(self,o):
        if self.shm: return self._r32(o)
        elif self._pBuf: return self._cr32(o)
        return 0
    def wstr(self,o,s,ml):
        if self.shm: self._wstr(o,s,ml)
        elif self._pBuf: self._cwstr(o,s,ml)
    def rstr(self,o,ml):
        if self.shm: return self._rstr(o,ml)
        elif self._pBuf: return self._crstr(o,ml)
        return ''

    def set_status(self,s): self.w32(OFF_STATUS,s)
    def get_command(self): return self.r32(OFF_COMMAND)
    def clear_command(self): self.w32(OFF_COMMAND, CMD_NONE)
    def set_error(self,e): self.w32(OFF_ERROR,e)
    def set_scene(self,s): self.w32(OFF_SCENE,s)
    def set_char_count(self,c): self.w32(OFF_CHAR_COUNT,c)
    def get_flags(self): return self.r32(OFF_FLAGS)
    def get_param(self,n): return self.r32(OFF_PARAM1+(n-1)*4)

    def write_log(self, msg):
        """NO-OP: SHM log yazma kaldirildi - byte-byte GIL bloke eder."""
        pass

    def write_server_name(self,i,n):
        if 0<=i<8: self.wstr(OFF_SRV_NAMES+i*16, n, 16)
    def write_channel_name(self,i,n):
        if 0<=i<8: self.wstr(OFF_CH_NAMES+i*16, n, 16)
    def write_char_info(self,slot,race,level,exists):
        if 0<=slot<4:
            off = OFF_CHAR_INFO+slot*16
            self.w32(off,race); self.w32(off+4,level); self.w32(off+8,exists)
    def write_char_name(self,slot,name):
        if 0<=slot<4: self.wstr(OFF_CHAR_NAMES+slot*16, name, 16)

    def close(self):
        try:
            if self.shm: self.shm.close(); self.shm=None
        except: pass
        try:
            if self._pBuf and self._hMap:
                k32 = ctypes.windll.kernel32
                k32.UnmapViewOfFile(self._pBuf)
                k32.CloseHandle(self._hMap)
                self._pBuf=None; self._hMap=None
        except: pass
        self.ready = False

# ============================================================
#  RECORDER v9 - LoginWindow hooks + PopupNotifyMessage, NO chat hook
# ============================================================
class Recorder(object):
    """
    v9 Hook kurallari:
      - chat.AppendChat: TAMAMEN KALDIRILDI
      - LoginWindow hooks: SADECE login ekrani sirasinda aktif
      - PopupNotifyMessage: POPUP mesajini yakalar, LOGIN_FAILURE kodunu EZMEZ
      - Oyun icinde: HIC hook aktif degil
    """
    def __init__(self, shm):
        self.shm = shm
        self.login_result = {'status':'','error':'','msg':''}
        self._login_hooks = {}

    def setup(self):
        self._log('Recorder v9 kuruldu (no locale, no chat hook)')

    def _log(self, msg):
        """NO-OP: Recorder log kaldirildi."""
        pass

    def record_event(self, etype, detail, text=None):
        """NO-OP: Event recording kaldirildi - sadece _record_login_event global'leri gunceller."""
        pass

    # ---- LOGIN HOOKS ----
    def hook_login_window(self, lw):
        if not lw: return
        lid = id(lw)
        if lid in self._login_hooks: return
        self._login_hooks[lid] = {'orig':{}, 'lw':lw}
        rec = self
        if hasattr(lw,'OnLoginFailure'):
            orig = lw.OnLoginFailure
            if not getattr(orig,'_mxh',False):
                self._login_hooks[lid]['orig']['OnLoginFailure'] = orig
                def _h(error, _o=orig):
                    try:
                        global _last_login_error
                        es = safe_str(error)
                        _last_login_error = es
                        desc = LOGIN_FAILURE_CODES.get(es, es)
                        rec.login_result = {'status':'FAILED','error':es,'msg':desc}
                        _record_login_event('LOGIN_FAILURE', es)
                    except: pass
                    return _o(error)
                _h._mxh = True
                lw.OnLoginFailure = _h
        if hasattr(lw,'OnConnectFailure'):
            orig = lw.OnConnectFailure
            if not getattr(orig,'_mxh',False):
                self._login_hooks[lid]['orig']['OnConnectFailure'] = orig
                def _h(_o=orig):
                    try:
                        rec.login_result = {'status':'CONNECT_FAILED','error':'CONNECT',
                                            'msg':'Connect failed'}
                        _record_login_event('CONNECT_FAILURE', 'CONNECT')
                    except: pass
                    return _o()
                _h._mxh = True
                lw.OnConnectFailure = _h
        if hasattr(lw,'OnHandShake'):
            orig = lw.OnHandShake
            if not getattr(orig,'_mxh',False):
                self._login_hooks[lid]['orig']['OnHandShake'] = orig
                def _h(_o=orig):
                    try:
                        global _login_success, _last_login_error
                        _login_success = True
                        _last_login_error = ""
                        rec.login_result['status'] = 'HANDSHAKE'
                        _record_login_event('LOGIN_SUCCESS', 'OK')
                    except: pass
                    return _o()
                _h._mxh = True
                lw.OnHandShake = _h
        # ---- PopupNotifyMessage hook (POPUP, LOGIN_FAILURE kodunu EZMEZ) ----
        if hasattr(lw, 'PopupNotifyMessage'):
            orig = lw.PopupNotifyMessage
            if not getattr(orig, '_mxh', False):
                self._login_hooks[lid]['orig']['PopupNotifyMessage'] = orig
                def _h_popup(msg, func=None, _o=orig):
                    try:
                        global _last_popup_msg
                        _last_popup_msg = safe_str(msg)[:120]
                        _record_login_event('POPUP', safe_str(msg)[:120], popup_msg=safe_str(msg)[:120])
                    except: pass
                    if func is not None:
                        return _o(msg, func)
                    return _o(msg)
                _h_popup._mxh = True
                lw.PopupNotifyMessage = _h_popup

    def _remove_login_hooks(self):
        for lid, data in self._login_hooks.items():
            lw = data.get('lw')
            for attr, orig in data.get('orig',{}).items():
                try: setattr(lw, attr, orig)
                except: pass
        self._login_hooks.clear()
        self._log('LoginWindow hooklari kaldirildi')

    # ---- OYUN/MENU GECIS ----
    def prepare_for_game(self):
        """Oyuna girmeden once: Login hook'lari birak (chat hook yok)"""
        self._log('OYUN MODU: Hooklar kaldirildi')

    def prepare_for_menu(self):
        """Oyundan cikinca: (chat hook YOK, hicbir sey yapma)"""
        self._log('MENU MODU')

    def full_reset(self):
        self._remove_login_hooks()
        self.login_result = {'status':'','error':'','msg':''}
        self._log('Recorder tam reset')

# ============================================================
#  SetPhaseWindow HOOK KURULUMU
# ============================================================
def install_phase_window_hook():
    """
    MainStream.SetPhaseWindow'u monkey-patch et.
    v12'de klavye calisti → hook sucsuz!
    """
    global _tracked_main_stream

    nw_mod = sys.modules.get('networkModule', None)
    if nw_mod is None:
        for name in ('networkmodule', 'NetworkModule'):
            nw_mod = sys.modules.get(name, None)
            if nw_mod:
                break
    if nw_mod is None:
        return False

    MainStreamClass = getattr(nw_mod, 'MainStream', None)
    if MainStreamClass is None:
        return False

    orig = getattr(MainStreamClass, 'SetPhaseWindow', None)
    if orig is None:
        return False

    if getattr(orig, '_mxh_hooked', False):
        return True

    def _hooked_set_phase(self_ms, new_phase_window):
        global _tracked_phase_window, _tracked_main_stream
        _tracked_phase_window = new_phase_window
        _tracked_main_stream = self_ms
        return orig(self_ms, new_phase_window)

    _hooked_set_phase._mxh_hooked = True
    _hooked_set_phase._mxh_orig = orig

    try:
        MainStreamClass.SetPhaseWindow = _hooked_set_phase
        return True
    except:
        return False

# ============================================================
#  Frame Stack Scanner - MainStream local finder
# ============================================================
def _find_mainstream_from_frames():
    """
    sys._current_frames() ile tum thread frame'lerini tara.
    mainStream local degiskenini bul.
    GIL: ~0.05ms
    """
    global _tracked_main_stream
    try:
        frames = sys._current_frames()
    except AttributeError:
        return None
    for tid, frame in frames.items():
        f = frame
        depth = 0
        while f and depth < 30:
            try:
                f_locals = f.f_locals
            except:
                break
            ms = f_locals.get('mainStream')
            if ms is not None and hasattr(ms, 'curPhaseWindow'):
                _tracked_main_stream = ms
                return ms
            for name in ('stream', 'main_stream', 'appStream'):
                ms = f_locals.get(name)
                if ms is not None and hasattr(ms, 'curPhaseWindow'):
                    _tracked_main_stream = ms
                    return ms
            try:
                f = f.f_back
            except:
                break
            depth += 1
    return None

# ============================================================
#  SCENE DETECTOR v8 - HOOK + FRAME SCAN (NO gc.get_objects)
# ============================================================
class SceneDetector(object):
    """
    v8: gc.get_objects() TAMAMEN KALDIRILDI.
    3 yontem:
      1. SetPhaseWindow hook -> _tracked_phase_window
      2. sys._current_frames() -> mainStream local -> curPhaseWindow
      3. net.IsConnect() -> in-game / loading fallback
    """
    def __init__(self):
        self.current_scene = SCENE_UNKNOWN
        self._in_game = False
        self._hook_installed = False
        self._net_mod = None

    def _ensure_net(self):
        if self._net_mod is None:
            self._net_mod = sys.modules.get('net', None)

    def _resolve_scene_from_window(self, phase_window):
        """curPhaseWindow objesinden sahne cozumle. GIL-SAFE v14:
        IsShow() cagrisi KALDIRILDI - C++ metodu GIL bloke ediyordu.
        Sadece type name oku (Python attribute, ~0ms GIL).
        """
        type_name = ''
        try:
            type_name = type(phase_window).__name__
        except:
            pass
        if not type_name:
            return SCENE_UNKNOWN

        if type_name == 'LoginWindow':
            # v14: sb.IsShow() KALDIRILDI - sadece type name'e bak
            # serverBoard varsa server sel, yoksa login
            try:
                sb = getattr(phase_window, 'serverBoard', None)
                if sb is not None:
                    return SCENE_SERVER_SEL
            except:
                pass
            return SCENE_LOGIN
        elif type_name == 'SelectCharacterWindow':
            return SCENE_CHAR_SEL
        elif type_name == 'CreateCharacterWindow':
            return SCENE_CHAR_CREATE
        elif type_name in ('SelectEmpireWindow', 'ReselectEmpireWindow'):
            return SCENE_EMPIRE_SEL
        elif type_name == 'GameWindow':
            return SCENE_GAME
        elif type_name == 'LogoWindow':
            return SCENE_LOGIN
        elif type_name == 'LoadingWindow':
            return SCENE_LOADING
        return SCENE_UNKNOWN

    def detect(self):
        global _tracked_phase_window

        self._ensure_net()

        # 1. If in_game, check net.IsConnect()
        if self._in_game:
            try:
                if self._net_mod and self._net_mod.IsConnect():
                    self.current_scene = SCENE_GAME
                    return SCENE_GAME
                else:
                    self._in_game = False
            except:
                self._in_game = False

        # 2. Hook tracking (en hizli, 0ms) - SADECE bu kullanilir
        if _tracked_phase_window is not None:
            scene = self._resolve_scene_from_window(_tracked_phase_window)
            if scene != SCENE_UNKNOWN:
                self.current_scene = scene
                return scene

        # 3. Frame scan - SADECE hook hic kurulmadiysa (fallback)
        #    Normalde hook kurulduysa buraya ASLA gelmez
        if _tracked_main_stream is None:
            ms = _find_mainstream_from_frames()
        else:
            ms = _tracked_main_stream
        if ms is not None:
            try:
                pw = getattr(ms, 'curPhaseWindow', None)
                if pw is not None and pw != 0:
                    _tracked_phase_window = pw
                    scene = self._resolve_scene_from_window(pw)
                    if scene != SCENE_UNKNOWN:
                        self.current_scene = scene
                        return scene
            except:
                pass

        # 4. net.IsConnect() fallback
        try:
            if self._net_mod and self._net_mod.IsConnect():
                game_mod = sys.modules.get('game', None) or sys.modules.get('introGame', None)
                if game_mod:
                    self.current_scene = SCENE_GAME
                    return self.current_scene
                self.current_scene = SCENE_LOADING
                return self.current_scene
        except:
            pass

        self.current_scene = SCENE_UNKNOWN
        return self.current_scene

    def force_scan(self):
        """Force re-detection on next call."""
        pass  # Hook-based, always fresh

    def mark_in_game(self):
        self._in_game = True
        self.current_scene = SCENE_GAME

    def mark_left_game(self):
        self._in_game = False

    def is_in_game(self):
        return self._in_game

    def get_login_window(self):
        """LoginWindow'u _tracked_phase_window'dan bul."""
        global _tracked_phase_window
        if _tracked_phase_window is not None:
            try:
                tn = type(_tracked_phase_window).__name__
                if tn == 'LoginWindow':
                    return _tracked_phase_window
            except:
                pass
        # Fallback: frame scan
        ms = _tracked_main_stream or _find_mainstream_from_frames()
        if ms:
            try:
                pw = getattr(ms, 'curPhaseWindow', None)
                if pw and type(pw).__name__ == 'LoginWindow':
                    return pw
            except:
                pass
        return None

    def get_select_window(self):
        """SelectCharacterWindow'u _tracked_phase_window'dan bul."""
        global _tracked_phase_window
        if _tracked_phase_window is not None:
            try:
                tn = type(_tracked_phase_window).__name__
                if tn == 'SelectCharacterWindow':
                    return _tracked_phase_window
            except:
                pass
        ms = _tracked_main_stream or _find_mainstream_from_frames()
        if ms:
            try:
                pw = getattr(ms, 'curPhaseWindow', None)
                if pw and type(pw).__name__ == 'SelectCharacterWindow':
                    return pw
            except:
                pass
        return None

    def get_empire_window(self):
        """EmpireWindow'u _tracked_phase_window'dan bul."""
        global _tracked_phase_window
        if _tracked_phase_window is not None:
            try:
                tn = type(_tracked_phase_window).__name__
                if tn in ('SelectEmpireWindow', 'ReselectEmpireWindow'):
                    return _tracked_phase_window
            except:
                pass
        ms = _tracked_main_stream or _find_mainstream_from_frames()
        if ms:
            try:
                pw = getattr(ms, 'curPhaseWindow', None)
                if pw and type(pw).__name__ in ('SelectEmpireWindow', 'ReselectEmpireWindow'):
                    return pw
            except:
                pass
        return None

    def get_create_window(self):
        """CreateCharacterWindow'u _tracked_phase_window'dan bul."""
        global _tracked_phase_window
        if _tracked_phase_window is not None:
            try:
                tn = type(_tracked_phase_window).__name__
                if tn == 'CreateCharacterWindow':
                    return _tracked_phase_window
            except:
                pass
        ms = _tracked_main_stream or _find_mainstream_from_frames()
        if ms:
            try:
                pw = getattr(ms, 'curPhaseWindow', None)
                if pw and type(pw).__name__ == 'CreateCharacterWindow':
                    return pw
            except:
                pass
        return None

    def get_stream(self):
        """MainStream'i _tracked_main_stream'ten bul."""
        global _tracked_main_stream
        if _tracked_main_stream is not None:
            return _tracked_main_stream
        return _find_mainstream_from_frames()

# ============================================================
#  CHARACTER MANAGER
# ============================================================
class CharacterManager(object):
    def __init__(self, shm, rec, sd):
        self.shm = shm
        self.rec = rec
        self.sd = sd
        self.characters = []
        self.empty_slots = []
        self.char_count = 0

    def refresh(self, wait_secs=0, retries=1):
        if wait_secs > 0: time.sleep(wait_secs)
        best_count = 0
        best_chars = []
        best_empty = []
        for attempt in range(max(1, retries)):
            chars = []
            empties = []
            if not net_mod: break
            for i in range(4):
                # v16: GIL yield - her slot arasinda GIL'i serbest birak
                time.sleep(0)
                cid = 0
                try: cid = net_mod.GetAccountCharacterSlotDataInteger(i, SLOT_ID)
                except: pass
                if cid == 0:
                    empties.append(i)
                    continue
                name = '?'
                try: name = net_mod.GetAccountCharacterSlotDataString(i, SLOT_NAME)
                except: pass
                race = 0
                try: race = net_mod.GetAccountCharacterSlotDataInteger(i, SLOT_RACE)
                except: pass
                level = 0
                try: level = net_mod.GetAccountCharacterSlotDataInteger(i, SLOT_LEVEL)
                except: pass
                chars.append({
                    'slot':i,'id':cid,'name':safe_str(name),
                    'race':race,'level':level,
                    'job':JOB_NAMES.get(race,'?'),
                    'gender':GENDER_NAMES.get(race,'?'),
                })
            if len(chars)>best_count:
                best_count=len(chars); best_chars=chars; best_empty=empties
            if len(chars)>0 or attempt>=retries-1: break
            time.sleep(1.0)
        self.characters = best_chars
        self.empty_slots = best_empty if best_chars else list(range(4))
        self.char_count = len(best_chars)
        if self.shm.ready:
            self.shm.set_char_count(self.char_count)
            for i in range(4):
                found = False
                for c in best_chars:
                    if c['slot']==i:
                        self.shm.write_char_name(i, c['name'])
                        self.shm.write_char_info(i, c['race'], c['level'], 1)
                        found = True
                        break
                if not found:
                    self.shm.write_char_name(i, '')
                    self.shm.write_char_info(i, 0, 0, 0)

    def clear(self):
        self.characters = []
        self.empty_slots = list(range(4))
        self.char_count = 0
        if self.shm.ready:
            self.shm.set_char_count(0)
            for i in range(4):
                self.shm.write_char_name(i, '')
                self.shm.write_char_info(i, 0, 0, 0)

    def find_by_name(self, name):
        nl = safe_str(name).lower()
        for c in self.characters:
            if c['name'].lower() == nl: return c
        return None

    def find_by_slot(self, slot):
        for c in self.characters:
            if c['slot'] == slot: return c
        return None

    def get_next_empty_slot(self):
        if self.empty_slots: return self.empty_slots[0]
        return -1

    def select_by_strategy(self, strategy, param_slot, param_name, param_job):
        if not self.characters: return None
        if strategy == STRAT_BY_SLOT:
            c = self.find_by_slot(param_slot)
            return c if c else self.characters[0]
        elif strategy == STRAT_BY_NAME:
            c = self.find_by_name(param_name)
            return c if c else self.characters[0]
        elif strategy == STRAT_MAX_LEVEL:
            best = None
            for c in self.characters:
                if best is None or c['level']>best['level']: best=c
            return best
        elif strategy == STRAT_MIN_LEVEL:
            best = None
            for c in self.characters:
                if best is None or c['level']<best['level']: best=c
            return best
        elif strategy == STRAT_BY_JOB:
            job_name = safe_str(param_job).strip()
            if not job_name: job_name = 'Ninja'
            for c in self.characters:
                if c['job'].lower() == job_name.lower():
                    return c
            return self.characters[0]
        elif strategy == STRAT_FIRST_SLOT:
            return self.characters[0]
        return self.characters[0] if self.characters else None

# ============================================================
#  ACTION EXECUTOR v8
# ============================================================
class ActionExecutor(object):
    def __init__(self, shm, rec, sd, cm):
        self.shm = shm
        self.rec = rec
        self.sd = sd
        self.cm = cm

    def _log(self, msg):
        """NO-OP: ActionExecutor log kaldirildi."""
        pass

    def _get_scene_safe(self):
        """v16: GIL-safe sahne oku - sd.detect() YERINE kullan.
        sd.detect() sys._current_frames() ve net.IsConnect() cagirabilir (GIL bloke).
        Bunun yerine _tracked_phase_window'dan direkt oku.
        """
        global _tracked_phase_window
        scene = SCENE_UNKNOWN
        if _tracked_phase_window is not None:
            try: scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
            except: pass
        return scene

    def _wait_scene(self, targets, timeout=15):
        start = time.time()
        while time.time()-start < timeout:
            scene = self._get_scene_safe()
            self.shm.set_scene(scene)
            if isinstance(targets, (list,tuple)):
                if scene in targets: return scene
            else:
                if scene == targets: return scene
            time.sleep(SCENE_CHECK_INTERVAL)
        return SCENE_UNKNOWN

    def _verify_scene(self, expected, timeout=5):
        """v16: sd.detect() YERINE _resolve_scene_from_window (GIL-safe)."""
        global _tracked_phase_window
        start = time.time()
        while time.time()-start < timeout:
            scene = SCENE_UNKNOWN
            if _tracked_phase_window is not None:
                try: scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
                except: pass
            self.shm.set_scene(scene)
            if isinstance(expected, (list,tuple)):
                if scene in expected: return True
            else:
                if scene == expected: return True
            time.sleep(SCENE_CHECK_INTERVAL)
        return False

    def _update_server_info(self, lw):
        if not lw: return
        try:
            sl = getattr(lw,'serverList',None)
            if sl and hasattr(sl,'GetItemCount'):
                sc = sl.GetItemCount()
                self.shm.w32(OFF_SRV_COUNT, sc)
                for i in range(min(sc,8)):
                    try: self.shm.write_server_name(i, safe_str(sl.GetItemText(i)))
                    except: pass
        except: pass
        try:
            cl = getattr(lw,'channelList',None)
            if cl and hasattr(cl,'GetItemCount'):
                cc = cl.GetItemCount()
                self.shm.w32(OFF_CH_COUNT, cc)
                for i in range(min(cc,8)):
                    try: self.shm.write_channel_name(i, safe_str(cl.GetItemText(i)))
                    except: pass
        except: pass

    def do_select_server(self, srv, ch):
        self._log('Server/CH: srv=%d ch=%d' % (srv, ch))
        self.shm.set_status(ST_STEP_SERVER)
        lw = self.sd.get_login_window()
        if not lw:
            self._log('LoginWindow YOK!')
            self.shm.set_error(ERR_SCENE_STUCK)
            return False
        self._update_server_info(lw)
        sl = getattr(lw,'serverList',None)
        if not sl or not hasattr(sl,'SelectItem'):
            self._log('serverList YOK!')
            return False
        try:
            sl.SelectItem(srv)
            self._log('Server SelectItem(%d) OK' % srv)
        except Exception:
            self._log('Server HATA: %s' % str(sys.exc_info()[1]))
            return False
        time.sleep(0.3)
        cl = getattr(lw,'channelList',None)
        if cl and hasattr(cl,'SelectItem'):
            try:
                cl.SelectItem(ch)
                self._log('Channel SelectItem(%d) OK' % ch)
            except: pass
        time.sleep(0.3)
        btn = getattr(lw,'serverSelectButton',None)
        if btn and hasattr(btn,'CallEvent'):
            try:
                btn.CallEvent()
                self._log('serverSelectButton OK')
            except Exception:
                self._log('serverSelectButton HATA: %s' % str(sys.exc_info()[1]))
                return False
        else:
            self._log('serverSelectButton YOK!')
            return False
        self.shm.w32(OFF_SEL_SRV, srv)
        self.shm.w32(OFF_SEL_CH, ch)
        self.rec.record_event('SERVER_SELECT','srv=%d ch=%d'%(srv,ch),None)
        time.sleep(STEP_WAIT)
        if not self._verify_scene(SCENE_LOGIN, timeout=5):
            self._log('Login ekranina gecilemedi!')
            return False
        self._log('Login ekranina gecildi')
        return True

    def do_login(self, username, password):
        self._log('Login: %s / ****' % username)
        self.shm.set_status(ST_STEP_LOGIN)
        self.rec.login_result = {'status':'','error':'','msg':''}
        # v17: _login_success global'ini resetle - ikinci loginde eski deger kaliyordu
        global _login_success
        _login_success = False
        self.cm.clear()
        if not self._verify_scene(SCENE_LOGIN, timeout=5):
            # v16: sd.detect() YERINE _resolve_scene_from_window
            scene = SCENE_UNKNOWN
            if _tracked_phase_window is not None:
                try: scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
                except: pass
            if scene == SCENE_SERVER_SEL:
                self.shm.set_status(ST_AT_SERVER_SEL)
                return False
        lw = self.sd.get_login_window()
        if not lw:
            self.shm.set_status(ST_LOGIN_FAIL)
            self.shm.set_error(ERR_UNKNOWN)
            return False
        self.rec.hook_login_window(lw)

        # v17: CRITICAL - LoginWindow'a SetFocus() cagir SetText'ten ONCE
        # Ikinci loginde LoginWindow focus'u kaybetmis olabilir, SetText calismaz
        try:
            if hasattr(lw, 'SetFocus'):
                lw.SetFocus()
                self._log('LoginWindow.SetFocus() OK')
        except: pass
        time.sleep(0.1)

        ide = getattr(lw,'idEditLine',None)
        if not ide or not hasattr(ide,'SetText'):
            self.shm.set_status(ST_LOGIN_FAIL)
            return False
        try: ide.SetText(username)
        except:
            self.shm.set_status(ST_LOGIN_FAIL)
            return False
        pwe = getattr(lw,'pwdEditLine',None)
        if not pwe or not hasattr(pwe,'SetText'):
            self.shm.set_status(ST_LOGIN_FAIL)
            return False
        try: pwe.SetText(password)
        except:
            self.shm.set_status(ST_LOGIN_FAIL)
            return False
        time.sleep(0.3)
        lbtn = getattr(lw,'loginButton',None)
        if not lbtn or not hasattr(lbtn,'CallEvent'):
            self.shm.set_status(ST_LOGIN_FAIL)
            return False
        try:
            lbtn.CallEvent()
            self._log('loginButton OK')
        except:
            self.shm.set_status(ST_LOGIN_FAIL)
            return False

        # v17: KillFocus() KALDIRILDI!
        # v16'da KillFocus() ikinci loginde login response'unu engelliyordu.
        # CallEvent sonrasi sadece GIL'i serbest birak - oyun focus'u kendisi transfer etsin
        time.sleep(1.0)

        self.shm.set_status(ST_LOGGING_IN)
        self.rec.record_event('LOGIN_ATTEMPT', username, None)
        self._log('Login bekleniyor (30s)...')
        start = time.time()
        while time.time()-start < 30:
            time.sleep(0.5)
            rs = self.rec.login_result.get('status','')
            if rs == 'FAILED':
                self._log('LOGIN BASARISIZ: %s' % self.rec.login_result.get('msg',''))
                self.shm.set_status(ST_LOGIN_FAIL)
                self.shm.set_error(ERR_LOGIN_FAIL)
                return False
            if rs == 'CONNECT_FAILED':
                self._log('BAGLANTI HATASI: %s' % self.rec.login_result.get('msg',''))
                self.shm.set_status(ST_CONNECT_FAIL)
                self.shm.set_error(ERR_CONNECT_FAIL)
                return False
            # v16: sd.detect() YERINE _resolve_scene_from_window (GIL-safe)
            scene = SCENE_UNKNOWN
            if _tracked_phase_window is not None:
                try: scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
                except: pass
            self.shm.set_scene(scene)
            if scene in (SCENE_CHAR_SEL, SCENE_EMPIRE_SEL, SCENE_CHAR_CREATE):
                self._log('LOGIN OK -> scene=%d' % scene)
                self.shm.set_status(ST_LOGIN_OK)
                self.shm.set_error(ERR_NONE)
                # v16: DEBUG - login success yorumda
                # self.rec.record_event('LOGIN_SUCCESS','OK',None)

                # v17: Yeni pencereye SetFocus() cagir - klavye focus'u transfer et
                if scene == SCENE_CHAR_SEL:
                    sw = self.sd.get_select_window()
                    if sw:
                        try:
                            if hasattr(sw, 'SetFocus'):
                                sw.SetFocus()
                                self._log('SelectCharWindow.SetFocus() OK')
                        except: pass
                        time.sleep(0.5)
                elif scene == SCENE_CHAR_CREATE:
                    cw = self.sd.get_create_window()
                    if cw:
                        try:
                            if hasattr(cw, 'SetFocus'):
                                cw.SetFocus()
                                self._log('CreateCharWindow.SetFocus() OK')
                        except: pass
                        time.sleep(0.5)
                elif scene == SCENE_EMPIRE_SEL:
                    ew = self.sd.get_empire_window()
                    if ew:
                        try:
                            if hasattr(ew, 'SetFocus'):
                                ew.SetFocus()
                                self._log('EmpireWindow.SetFocus() OK')
                        except: pass
                        time.sleep(0.5)

                self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
                # v16: DEBUG - karakter sayisi yorumda
                # self._log('Karakter sayisi: %d' % self.cm.char_count)
                return True
            try:
                if hasattr(lw,'isStartError') and lw.isStartError:
                    self.shm.set_status(ST_LOGIN_FAIL)
                    self.shm.set_error(ERR_LOGIN_FAIL)
                    return False
            except: pass
        self._log('LOGIN TIMEOUT')
        self.shm.set_status(ST_LOGIN_FAIL)
        self.shm.set_error(ERR_TIMEOUT)
        return False

    def do_select_empire(self, empire_id):
        self._log('Empire: %d (%s)' % (empire_id, EMPIRE_NAMES.get(empire_id,'?')))
        self.shm.set_status(ST_AT_EMPIRE_SEL)
        scene = self._get_scene_safe()
        self.shm.set_scene(scene)
        if scene == SCENE_CHAR_SEL:
            sw = self.sd.get_select_window()
            if sw: self._click_create_button(sw)
            time.sleep(2)
            scene = self._get_scene_safe()
            self.shm.set_scene(scene)
        if scene == SCENE_EMPIRE_SEL:
            ew = self.sd.get_empire_window()
            if ew:
                try:
                    ew.OnSelectEmpire(empire_id)
                    time.sleep(0.5)
                except: pass
                try: ew.empireID = empire_id
                except: pass
                # v8: NO gc.get_objects() - find EmpireButton via _tracked_phase_window
                if not self.sd.is_in_game():
                    try:
                        pw = _tracked_phase_window
                        if pw is not None:
                            # Walk phase window children to find EmpireButton
                            ed = getattr(pw, 'ElementDictionary', {})
                            if ed:
                                for key, obj in ed.items():
                                    try:
                                        if type(obj).__name__ == 'EmpireButton':
                                            if getattr(obj,'arg',-1)==empire_id and obj.IsShow():
                                                obj.CallEvent()
                                                time.sleep(1)
                                                break
                                    except: pass
                            # Also try direct attribute scan
                            for attr in ('empireButtonList', 'btnList'):
                                bl = getattr(pw, attr, None)
                                if bl:
                                    for obj in bl:
                                        try:
                                            if type(obj).__name__ == 'EmpireButton':
                                                if getattr(obj,'arg',-1)==empire_id and obj.IsShow():
                                                    obj.CallEvent()
                                                    time.sleep(1)
                                                    break
                                        except: pass
                    except: pass
                try:
                    ew.ClickSelectButton()
                    self._log('ClickSelectButton OK')
                    time.sleep(2)
                except:
                    try:
                        ed = getattr(ew,'ElementDictionary',{})
                        sb = ed.get('select_button',None)
                        if sb and hasattr(sb,'CallEvent'):
                            sb.CallEvent()
                            time.sleep(2)
                    except: pass
            result = self._wait_scene([SCENE_CHAR_SEL, SCENE_CHAR_CREATE], timeout=10)
            if result != SCENE_UNKNOWN:
                self.shm.set_status(ST_EMPIRE_DONE)
                self.rec.record_event('EMPIRE_SELECT','%d'%empire_id, None)
                return True
            try:
                net_mod.SendSelectEmpirePacket(empire_id)
                time.sleep(3)
            except: pass
        self.shm.set_status(ST_EMPIRE_DONE)
        return True

    def _click_create_button(self, sw):
        create_btn = None
        for attr in ('btnCreate','createButton','btn_create'):
            b = getattr(sw, attr, None)
            if b and hasattr(b,'CallEvent'):
                create_btn = b
                break
        if not create_btn:
            ed = getattr(sw,'ElementDictionary',{})
            for key in ('create_button','btnCreate','CreateButton'):
                b = ed.get(key,None)
                if b and hasattr(b,'CallEvent'):
                    create_btn = b
                    break
        if create_btn:
            try:
                create_btn.CallEvent()
                self._log('Create buton OK')
            except: pass

    def do_create_character(self, race, empire, name=None, slot=-1):
        if not name: name = make_random_name()
        if slot < 0: slot = self.cm.get_next_empty_slot()
        if slot < 0:
            self._log('Bos slot yok!')
            return False
        target_job_slot = RACE_TO_SLOT.get(race, 3)
        target_gender = RACE_TO_GENDER.get(race, 1)
        self._log('Karakter: slot=%d name=%s race=%d emp=%d' % (slot,name,race,empire))
        self.shm.set_status(ST_CREATING_CHAR)
        pre_count = self.cm.char_count
        scene = self._get_scene_safe()
        self.shm.set_scene(scene)
        need_empire = False
        if pre_count == 0:
            try:
                eid = net_mod.GetEmpireID()
                if eid == 0: need_empire = True
            except: need_empire = True
        if need_empire:
            self._log('Ilk karakter - Empire secimi')
            self.do_select_empire(empire)
            time.sleep(2)
            scene = self._get_scene_safe()
            self.shm.set_scene(scene)
        if scene == SCENE_CHAR_SEL:
            sw = self.sd.get_select_window()
            if sw: self._click_create_button(sw)
            time.sleep(2)
            scene = self._get_scene_safe()
            if scene == SCENE_EMPIRE_SEL:
                self.do_select_empire(empire)
                time.sleep(2)
                scene = self._get_scene_safe()
                self.shm.set_scene(scene)
        if scene == SCENE_CHAR_CREATE:
            ccw = self.sd.get_create_window()
            if ccw:
                cur_slot = getattr(ccw,'slot',0)
                incr = getattr(ccw,'_CreateCharacterWindow__IncreaseSlotIndex',None)
                if incr:
                    steps = (target_job_slot - cur_slot) % 4
                    for step in range(steps):
                        try:
                            incr()
                            time.sleep(1.5)
                            if getattr(ccw,'slot',-1)==target_job_slot: break
                        except: break
                else:
                    try: ccw.slot = target_job_slot
                    except: pass
                sel_gender = getattr(ccw,'_CreateCharacterWindow__SelectGender',None)
                if sel_gender:
                    try: sel_gender(target_gender); time.sleep(0.3)
                    except: pass
                try: ccw.gender = target_gender
                except: pass
                gbl = getattr(ccw,'genderButtonList',[])
                if len(gbl)>target_gender:
                    try: gbl[target_gender].CallEvent()
                    except: pass
                sbl = getattr(ccw,'shapeButtonList',[])
                if len(sbl)>target_gender:
                    try: sbl[target_gender].CallEvent()
                    except: pass
                edn = getattr(ccw,'editCharacterName',None)
                if edn and hasattr(edn,'SetText'):
                    try: edn.SetText(name)
                    except: pass
                btn_create = getattr(ccw,'btnCreate',None)
                if btn_create and hasattr(btn_create,'CallEvent'):
                    try: btn_create.CallEvent(); self._log('btnCreate OK')
                    except: pass
                time.sleep(2)
        try:
            use_emp = empire
            try:
                eid = net_mod.GetEmpireID()
                if eid > 0: use_emp = eid
            except: pass
            net_mod.SendCreateCharacterPacket(slot, name, race, use_emp)
            self._log('SendCreateCharacterPacket OK')
        except:
            self._log('SendCreateCharacterPacket HATA: %s' % str(sys.exc_info()[1]))
        time.sleep(3)
        scene = self._get_scene_safe()
        if scene == SCENE_CHAR_CREATE:
            stm = self.sd.get_stream()
            if stm and hasattr(stm,'SetSelectCharacterPhase'):
                try: stm.SetSelectCharacterPhase(); time.sleep(2)
                except: pass
        self._log('Olusturma bekleniyor (20s)...')
        start = time.time()
        while time.time()-start < 20:
            time.sleep(1.5)
            self.cm.refresh(wait_secs=0, retries=1)
            if self.cm.char_count > pre_count:
                self._log('KARAKTER OLUSTU! %d -> %d' % (pre_count, self.cm.char_count))
                self.shm.set_status(ST_CHAR_CREATED)
                return True
        retry_name = make_random_name()
        self._log('Tekrar: %s' % retry_name)
        try:
            use_emp = empire
            try:
                eid = net_mod.GetEmpireID()
                if eid > 0: use_emp = eid
            except: pass
            net_mod.SendCreateCharacterPacket(slot, retry_name, race, use_emp)
            start2 = time.time()
            while time.time()-start2 < 15:
                time.sleep(1.5)
                self.cm.refresh(wait_secs=0, retries=1)
                if self.cm.char_count > pre_count:
                    self._log('KARAKTER OLUSTU (2)!')
                    self.shm.set_status(ST_CHAR_CREATED)
                    return True
        except: pass
        self._log('Olusturma BASARISIZ')
        self.shm.set_status(ST_CHAR_FAIL)
        self.shm.set_error(ERR_CHAR_FAIL)
        return False

    def do_enter_game(self, slot=-1, target_name='', strategy=STRAT_FIRST_SLOT, param_job=''):
        self._log('Oyuna giris: slot=%d name=%s strat=%d' % (slot, target_name, strategy))
        self.shm.set_status(ST_ENTERING_GAME)
        self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
        if not self.cm.characters:
            self._log('Karakter yok!')
            self.shm.set_status(ST_ENTER_FAIL)
            self.shm.set_error(ERR_ENTER_FAIL)
            return False
        target = self.cm.select_by_strategy(strategy, slot, target_name, param_job)
        if not target: target = self.cm.characters[0]
        sl = target['slot']
        self._log('Secilen: [%d] %s Lv.%d %s(%s)' % (
            sl, target['name'], target['level'], target['job'], target['gender']))
        # === STABLE RC12 FIX (MaxExecutor paketi) ===
        # CIFT GIRIS YASAGI: UI yolu (SelectSlot+StartGame) select+enter paketlerini
        # yollar; DirectEnter AYNI diziyi 0.1sn sonra tekrar yollar. Ikinci giris
        # PHASE_SELECT->LOADING gecisini bozar -> NPC'ler yuklenmez.
        # LegendySF kaniti: introselect.py:765 yalniz DirectEnter; introloading.py:147
        # select paketini kendi yollar. YALNIZ paket yolu kullanilir.
        try:
            net_mod.DirectEnter(sl)
            self._log('DirectEnter(%d) OK' % sl)
        except:
            self._log('DirectEnter HATA: %s' % str(sys.exc_info()[1]))
        self.rec.record_event('ENTER_GAME','slot=%d name=%s'%(sl,target['name']),None)
        # === v8: OYUNA GIRMEDEN ONCE HOOKLARI KALDIR ===
        self.rec.prepare_for_game()
        self.sd.mark_in_game()
        self.shm.set_scene(SCENE_GAME)
        time.sleep(0.5)
        self._log('Oyuna giris bekleniyor (30s)...')
        start = time.time()
        while time.time()-start < 30:
            time.sleep(2.0)
            try:
                # === STABLE RC14 FIX: oyunda-kaniti = GameWindow (hook globali) ===
                # sys.modules.get('game') eski import'tan var olabilir -> yanlis
                # pozitif; spawn patlamasi ortasina komut dusmesin.
                if self._get_scene_safe() == SCENE_GAME:
                    self._log('OYUNA GIRILDI! (GameWindow kaniti)')
                    self.shm.set_status(ST_IN_GAME)
                    self.shm.set_error(ERR_NONE)
                    return True
            except: pass
        self.rec.prepare_for_menu()
        self.sd.mark_left_game()
        self._log('Oyuna giris TIMEOUT')
        self.shm.set_status(ST_ENTER_FAIL)
        self.shm.set_error(ERR_TIMEOUT)
        return False

    def do_scene_change(self, target_id):
        self.sd.mark_left_game()
        self.rec.prepare_for_menu()
        stm = self.sd.get_stream()
        if not stm: return False
        smap = {1:'SetCreateCharacterPhase',2:'SetSelectCharacterPhase',
                3:'SetSelectEmpirePhase',4:'SetLoginPhase'}
        mn = smap.get(target_id, None)
        if not mn or not hasattr(stm, mn): return False
        try:
            getattr(stm, mn)()
            time.sleep(1)
            return True
        except: return False

    def do_recovery(self, target):
        # === STABLE RC13 FIX: yukleme/oyun sirasinda faz zorlama YASAK ===
        # Scene tespiti hook-tabanli; yanlis/yalnış algida LoadingWindow'dayken
        # SetSelectCharacterPhase cagrilsa yukleme iptal olur -> NPC yok.
        try:
            cur = self._get_scene_safe()
        except:
            cur = SCENE_UNKNOWN
        if cur in (SCENE_LOADING, SCENE_GAME):
            self._log('Recovery RED: sahne=%s (yukleme/oyun sirasinda Set*Phase tehlikeli)' % cur)
            return False
        self.shm.set_status(ST_RECOVERING)
        self.sd.mark_left_game()
        self.rec.prepare_for_menu()
        stm = self.sd.get_stream()
        if not stm: return False
        if target == SCENE_CHAR_SEL:
            if hasattr(stm,'SetSelectCharacterPhase'):
                try:
                    stm.SetSelectCharacterPhase()
                    time.sleep(2)
                    return self._get_scene_safe() == SCENE_CHAR_SEL
                except: pass
        if target in (SCENE_LOGIN, SCENE_SERVER_SEL):
            if hasattr(stm,'SetLoginPhase'):
                try:
                    stm.SetLoginPhase()
                    time.sleep(2)
                    return True
                except: pass
        return False

    def do_complete_all(self):
        self._log('=== TAMAMLA BASLATILDI ===')
        self.shm.w32(OFF_AUTO_STATE, AUTO_RUNNING)
        srv = self.shm.r32(OFF_SEL_SRV)
        ch = self.shm.r32(OFF_SEL_CH)
        user = self.shm.rstr(OFF_USERNAME, 64)
        pwd = self.shm.rstr(OFF_PASSWORD, 64)
        cr_race = self.shm.r32(OFF_CR_RACE)
        cr_emp = self.shm.r32(OFF_CR_EMPIRE)
        cr_count = self.shm.r32(OFF_CR_COUNT)
        tgt_slot = self.shm.r32(OFF_TARGET_SLOT)
        tgt_name = self.shm.rstr(OFF_TARGET_NAME, 64)
        cr_name = self.shm.rstr(OFF_CREATE_NAME, 64)
        strategy = self.shm.r32(OFF_CHAR_STRATEGY)
        create_if_exists = self.shm.r32(OFF_CREATE_IF_EXISTS)
        flags = self.shm.get_flags()
        rnd_name = (flags & FLAG_RANDOM_NAME) != 0
        if cr_emp == 0: cr_emp = 1
        if cr_race == 0: cr_race = 3
        if strategy == 0: strategy = STRAT_FIRST_SLOT
        param4 = self.shm.get_param(4)
        job_names_list = ['Warrior','Ninja','Sura','Shaman','Lycan']
        tgt_job = ''
        if strategy == STRAT_BY_JOB and param4 < len(job_names_list):
            tgt_job = job_names_list[param4]
        self._log('TAMAMLA: srv=%d ch=%d user=%s strat=%d race=%d emp=%d count=%d' % (
            srv, ch, user, strategy, cr_race, cr_emp, cr_count))
        retry = 0
        while retry < MAX_RETRIES:
            scene = self._get_scene_safe()
            self.shm.set_scene(scene)
            self._log('ADIM: Sahne=%d' % scene)
            if scene in (SCENE_SERVER_SEL, SCENE_UNKNOWN):
                self.shm.set_status(ST_STEP_SERVER)
                lw = self.sd.get_login_window()
                if lw:
                    sb = getattr(lw,'serverBoard',None)
                    if sb and hasattr(sb,'IsShow') and sb.IsShow():
                        if not self.do_select_server(srv, ch):
                            retry += 1
                            time.sleep(10)
                            continue
                time.sleep(STEP_WAIT)
                scene = self._get_scene_safe()
                self.shm.set_scene(scene)
            if scene == SCENE_LOGIN:
                self.shm.set_status(ST_STEP_LOGIN)
                if not user:
                    self.shm.set_status(ST_AT_LOGIN)
                    self.shm.w32(OFF_AUTO_STATE, AUTO_WAITING)
                    return
                if not self.do_login(user, pwd):
                    err = self.shm.r32(OFF_ERROR)
                    if err in (ERR_CONNECT_FAIL, ERR_MAINTENANCE):
                        self._log('Bakim, %d dk sonra tekrar' % (RETRY_INTERVAL//60))
                        self.shm.set_status(ST_MAINTENANCE)
                        time.sleep(RETRY_INTERVAL)
                        retry += 1
                        continue
                    time.sleep(10)
                    retry += 1
                    continue
                time.sleep(STEP_WAIT)
                scene = self._get_scene_safe()
                self.shm.set_scene(scene)
            if scene == SCENE_EMPIRE_SEL:
                self.do_select_empire(cr_emp)
                time.sleep(STEP_WAIT)
                scene = self._get_scene_safe()
                self.shm.set_scene(scene)
            if scene in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE):
                self.shm.set_status(ST_STEP_CHARSEL)
                self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
                should_create = False
                # v16: DEBUG - karakter sayisi yorumda
                # if self.cm.char_count == 0:
                if False:  # v16: DEBUG - karakter sayisi kontrolu kapatildi
                    should_create = True
                elif create_if_exists and cr_count > 0:
                    if self.cm.char_count < MAX_CREATE_CHARS:
                        should_create = True
                if should_create:
                    needed = max(1,cr_count) if self.cm.char_count==0 else cr_count
                    avail = MAX_CREATE_CHARS - self.cm.char_count
                    actual = min(needed, avail)
                    self._log('Olusturulacak: %d' % actual)
                    for ci in range(actual):
                        self.cm.refresh(wait_secs=0, retries=3)
                        if self.cm.char_count >= MAX_CREATE_CHARS: break
                        cn = cr_name if (not rnd_name and ci==0 and cr_name) else make_random_name()
                        if not self.do_create_character(cr_race, cr_emp, cn):
                            self.do_recovery(SCENE_CHAR_SEL)
                            time.sleep(2)
                            cn2 = make_random_name()
                            if not self.do_create_character(cr_race, cr_emp, cn2): break
                        time.sleep(STEP_WAIT)
                    scene = self._get_scene_safe()
                    if scene not in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE):
                        self.do_recovery(SCENE_CHAR_SEL)
                        time.sleep(2)
                    self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
                if self.cm.char_count == 0:
                    self._log('Karakter yok!')
                    self.shm.set_status(ST_ERROR)
                    self.shm.set_error(ERR_CHAR_FAIL)
                    self.shm.w32(OFF_AUTO_STATE, AUTO_ERROR)
                    return
            scene = self._get_scene_safe()
            if scene != SCENE_CHAR_SEL:
                self.do_recovery(SCENE_CHAR_SEL)
                time.sleep(2)
                self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
            if self.do_enter_game(tgt_slot, tgt_name, strategy, tgt_job):
                self._log('=== TAMAMLA BASARILI ===')
                self.shm.set_status(ST_STEP_COMPLETE)
                self.shm.w32(OFF_AUTO_STATE, AUTO_COMPLETE)
                return
            self.do_recovery(SCENE_CHAR_SEL)
            time.sleep(3)
            self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
            if self.do_enter_game(tgt_slot, tgt_name, strategy, tgt_job):
                self.shm.set_status(ST_STEP_COMPLETE)
                self.shm.w32(OFF_AUTO_STATE, AUTO_COMPLETE)
                return
            retry += 1
            continue
        self._log('=== TAMAMLA MAX RETRY ===')
        self.shm.set_status(ST_ERROR)
        self.shm.w32(OFF_AUTO_STATE, AUTO_ERROR)

# ============================================================
#  ANA KONTROL v8
# ============================================================
class MaximumController(object):
    def __init__(self):
        self.shm = SharedMemoryManager()
        self.rec = Recorder(self.shm)
        self.sd = SceneDetector()
        self.cm = CharacterManager(self.shm, self.rec, self.sd)
        self.ae = ActionExecutor(self.shm, self.rec, self.sd, self.cm)
        self.running = False
        self._last_connect_check = 0

    def start(self):
        if hasattr(sys, '_max_running') and sys._max_running:
            sys._max_stop = True
            time.sleep(0.5)
        sys._max_running = True
        sys._max_stop = False
        # v14: Hook kur + SHM olustur + ilk sahne oku (hook'tan)
        install_phase_window_hook()
        if not self.shm.create():
            return
        self.rec.setup()
        # v14: Ilk sahne - hook'tan oku (sd.detect YOK - GIL bloke eder)
        if _tracked_phase_window is not None:
            try:
                scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
                self.shm.set_scene(scene)
            except:
                pass
        self.shm.set_status(ST_READY)
        self.running = True
        self._loop()

    def _loop(self):
        """v17 GIL-SAFE döngü + Focus Fix:
        1. SetPhaseWindow hook'tan sahne oku (Python attribute, ~0ms)
        2. SHM'ye sahne yaz (mmap int write, ~0.001ms)
        3. SHM'den komut oku (mmap int read, ~0.001ms)
        4. Scene-based sleep (GIL serbest)
        5. v17: GAME→menü geçişinde SetFocus() çağır (klavye fix)
        """
        scene = SCENE_UNKNOWN
        prev_scene = SCENE_UNKNOWN
        while self.running:
            if getattr(sys, '_max_stop', False): break

            # 1. SAHNE OKU - hook'tan (GIL: ~0ms)
            if _tracked_phase_window is not None:
                try:
                    scene = self.sd._resolve_scene_from_window(_tracked_phase_window)
                except:
                    scene = SCENE_UNKNOWN

            # 2. SHM SAHNE YAZ (GIL: ~0.001ms)
            self.shm.set_scene(scene)

            # v17: SAHNE GECISI - GAME→menü veya herhangi→CHAR_SEL
            # Oyundan karakter seçime dönünce klavye çalışmıyordu çünkü
            # focus yeni pencereye transfer olmuyordu. SetFocus() ile düzelt.
            if prev_scene == SCENE_GAME and scene in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE, SCENE_EMPIRE_SEL, SCENE_LOGIN, SCENE_SERVER_SEL):
                if _tracked_phase_window is not None:
                    try:
                        if hasattr(_tracked_phase_window, 'SetFocus'):
                            _tracked_phase_window.SetFocus()
                    except: pass
                    # GIL'i serbest bırak - oyun focus değişikliğini işlesin
                    time.sleep(0.3)
            prev_scene = scene

            # 3. SHM DURUM YAZ (scene bazli)
            if scene == SCENE_LOGIN:
                self.shm.set_status(ST_READY)
            elif scene == SCENE_SERVER_SEL:
                self.shm.set_status(ST_AT_SERVER_SEL)
            elif scene == SCENE_CHAR_SEL:
                self.shm.set_status(ST_AT_CHAR_SEL)
            elif scene == SCENE_CHAR_CREATE:
                self.shm.set_status(ST_AT_CHAR_CREATE)
            elif scene == SCENE_EMPIRE_SEL:
                self.shm.set_status(ST_AT_EMPIRE_SEL)
            elif scene == SCENE_GAME:
                self.shm.set_status(ST_IN_GAME)

            # 4. SHM KOMUT OKU (GIL: ~0.001ms)
            cmd = self.shm.get_command()
            if cmd != CMD_NONE:
                self.shm.clear_command()
                self._cmd(cmd)

            # 5. SAHNE BAZLI UYKU (GIL tamamen serbest)
            if scene in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE, SCENE_EMPIRE_SEL):
                time.sleep(5.0)   # Karakter secim: 5s derin uyku
            elif scene == SCENE_GAME:
                time.sleep(10.0)  # Oyun ici: 10s
            elif scene == SCENE_LOGIN:
                time.sleep(2.0)   # Login: 2s
            else:
                time.sleep(COMMAND_POLL)  # 2s (unknown, loading)

        self.running = False
        sys._max_running = False
        sys._max_stop = False
        self.rec.full_reset()
        self.shm.set_status(ST_IDLE)
        self.shm.close()
        append_log('KAPATILDI')

    def _log(self, msg):
        """NO-OP: Controller log kaldirildi."""
        pass

    def _full_reset(self):
        self._log('=== TAM RESET ===')
        self.rec.full_reset()
        self.sd.force_scan()
        self.sd.mark_left_game()
        self.cm.clear()
        self.shm.set_status(ST_READY)
        self.shm.set_error(ERR_NONE)
        self.shm.w32(OFF_AUTO_STATE, AUTO_IDLE)
        scene = self.ae._get_scene_safe()
        self.shm.set_scene(scene)
        lw = self.sd.get_login_window()
        if lw: self.ae._update_server_info(lw)
        self._log('Reset tamamlandi - scene=%d' % scene)

    def _cmd(self, cmd):
        append_log('Komut: %d' % cmd)
        if cmd == CMD_SELECT_SERVER:
            self.ae.do_select_server(self.shm.get_param(1), self.shm.get_param(2))
        elif cmd == CMD_LOGIN:
            self.ae.do_login(self.shm.rstr(OFF_USERNAME,64), self.shm.rstr(OFF_PASSWORD,64))
        elif cmd == CMD_SELECT_CHAR:
            self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
        elif cmd == CMD_CREATE_CHAR:
            race = self.shm.get_param(1)
            emp = self.shm.get_param(2)
            count = self.shm.get_param(3)
            name = self.shm.rstr(OFF_CREATE_NAME, 64)
            flags = self.shm.get_flags()
            rnd = (flags & FLAG_RANDOM_NAME) != 0
            if count <= 0: count = 1
            if emp == 0: emp = 1
            self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
            avail = MAX_CREATE_CHARS - self.cm.char_count
            if avail <= 0:
                self.ae._log('Max karakter!')
                return
            actual = min(count, avail)
            for i in range(actual):
                self.cm.refresh(wait_secs=0, retries=3)
                if self.cm.char_count >= MAX_CREATE_CHARS: break
                cn = name if (not rnd and i==0 and name) else make_random_name()
                self.ae.do_create_character(race, emp, cn)
                time.sleep(1)
                scene = self.ae._get_scene_safe()
                if scene not in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE):
                    self.ae.do_recovery(SCENE_CHAR_SEL)
                    time.sleep(2)
        elif cmd == CMD_ENTER_GAME:
            slot = self.shm.get_param(1)
            name = self.shm.rstr(OFF_TARGET_NAME, 64)
            strat = self.shm.r32(OFF_CHAR_STRATEGY)
            if strat == 0: strat = STRAT_FIRST_SLOT
            self.ae.do_enter_game(slot, name, strat)
        elif cmd == CMD_SELECT_EMPIRE:
            self.ae.do_select_empire(self.shm.get_param(1))
        elif cmd == CMD_REFRESH:
            self.sd.force_scan()
            scene = self.ae._get_scene_safe()
            self.shm.set_scene(scene)
            if scene in (SCENE_CHAR_SEL, SCENE_CHAR_CREATE):
                self.cm.refresh(wait_secs=CHAR_DATA_WAIT, retries=CHAR_DATA_RETRIES)
            lw = self.sd.get_login_window()
            if lw: self.ae._update_server_info(lw)
            self.shm.set_status(ST_READY)
        elif cmd == CMD_AUTO_ALL:
            self.ae.do_complete_all()
        elif cmd == CMD_COMPLETE_ALL:
            self.ae.do_complete_all()
        elif cmd == CMD_SCENE_CHANGE:
            self.ae.do_scene_change(self.shm.get_param(1))
        elif cmd == CMD_RESTART:
            self._full_reset()
        elif cmd == CMD_STOP:
            self.running = False

# ============================================================
#  CALL INTERFACE: loginevent (sys.modules)
# ============================================================
class _LoginEventModule(object):
    pass

_le_mod = _LoginEventModule()

def _le_GetLastEvent():
    try:
        if _event_history:
            t, ev, code, desc = _event_history[-1]
            return '%s|%s' % (ev, code) if code else ev
        return 'NONE'
    except:
        return 'NONE'

_le_mod.GetLastEvent = _le_GetLastEvent
_le_mod.GetLastErrorCode = lambda: _last_login_error or ''
_le_mod.GetLastErrorDesc = lambda: LOGIN_FAILURE_CODES.get(_last_login_error, _last_login_error) if _last_login_error else ''
_le_mod.GetPopupMessage = lambda: _last_popup_msg or ''
_le_mod.IsSuccess = lambda: 1 if _login_success else 0
_le_mod.GetEventCount = lambda: _event_count
_le_mod.GetHistory = lambda: '\n'.join('%s|%s|%s|%s'%(t,ev,code,desc) for t,ev,code,desc in _event_history[-10:])
_le_mod.GetScene = lambda: '%d|%s' % (_ctrl.sd.current_scene, SCENE_NAMES.get(_ctrl.sd.current_scene, '?')) if hasattr(sys, '_max_running') and sys._max_running else '0|?'
_le_mod.GetSceneID = lambda: _ctrl.sd.current_scene if hasattr(sys, '_max_running') and sys._max_running else 0
_le_mod.GetSceneName = lambda: SCENE_NAMES.get(_ctrl.sd.current_scene, 'UNKNOWN') if hasattr(sys, '_max_running') and sys._max_running else 'UNKNOWN'
_le_mod.LOGIN_FAILURE_CODES = LOGIN_FAILURE_CODES
_le_mod.SCENE_NAMES = SCENE_NAMES

sys.modules['loginevent'] = _le_mod

# ============================================================
#  BASLAT
# ============================================================
_ctrl = MaximumController()
try:
    import thread as _thread
    _thread.start_new_thread(_ctrl.start, ())
    append_log('Thread baslatildi')
except:
    try:
        import threading
        t = threading.Thread(target=_ctrl.start)
        t.daemon = True
        t.start()
        append_log('Threading baslatildi')
    except:
        _ctrl.start()
