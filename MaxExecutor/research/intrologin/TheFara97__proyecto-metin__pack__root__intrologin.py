# -*- coding: iso-8859-1 -*-

import ui
import net
import app
import wndMgr
import snd
import musicInfo
import systemSetting
import localeInfo
import constInfo
import ime
import uiCommon

if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
	import uiGuild

try:
	import _winreg
except ImportError:
	import winreg as _winreg

REG_PATH = r"SOFTWARE\Elvion"


class RegistryManager(object):
	"""Handles Windows registry operations for account storage."""
	
	@staticmethod
	def set_reg(name, value):
		"""Set a registry value."""
		try:
			_winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
			registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
			_winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
			_winreg.CloseKey(registry_key)
			return True
		except WindowsError:
			return False

	@staticmethod
	def get_reg(name):
		"""Get a registry value."""
		try:
			registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_READ)
			value, regtype = _winreg.QueryValueEx(registry_key, name)
			_winreg.CloseKey(registry_key)
			return str(value)
		except WindowsError:
			return None


class ChannelManager(object):
	"""Manages server channel configuration and connections."""
	
	CHANNEL_CONFIG = {
		"CH1": [31003, "Elvion.cc", "Channel 1"],
		"CH2": [31007, "Elvion.cc", "Channel 2"],
		"CH3": [31011, "Elvion.cc", "Channel 3"],
		"CH4": [31015, "Elvion.cc", "Channel 4"],
		#"CH5": [31019, "Elvion.cc", "Channel 5"],
		#"CH6": [31023, "Elvion.cc", "Channel 6"]
	}
	
	LOGIN_PORT = 31001
	SERVER_IP = "192.168.1.40"
	
	@classmethod
	def get_channel_port(cls, channel='CH1', value=0):
		"""Get port information for a specific channel."""
		if channel == "LOGIN":
			return cls.LOGIN_PORT
		elif channel == "LOGO":
			return cls.CHANNEL_CONFIG["CH1"][0]
		elif value == 2:
			config = cls.CHANNEL_CONFIG[channel]
			return "{}, {}".format(config[1], config[2])
		else:
			return cls.CHANNEL_CONFIG[channel][value]


class AccountManager(object):
	"""Manages saved account data."""
	
	MAX_ACCOUNTS = 10
	
	def __init__(self, registry_manager):
		self.registry = registry_manager
		
	def save_account(self, slot, username, password, pin):
		"""Save account credentials to registry."""
		if self.is_slot_occupied(slot):
			return False
			
		self.registry.set_reg("id_{}".format(slot), username)
		self.registry.set_reg("pwd_{}".format(slot), password)
		self.registry.set_reg("pin{}".format(slot), pin)
		return True
		
	def load_account(self, slot):
		"""Load account credentials from registry."""
		username = self.registry.get_reg("id_{}".format(slot))
		password = self.registry.get_reg("pwd_{}".format(slot))
		pin = self.registry.get_reg("pin{}".format(slot))
		
		if username:
			return {
				'username': username,
				'password': password,
				'pin': pin
			}
		return None
		
	def delete_account(self, slot):
		"""Delete account credentials from registry."""
		self.registry.set_reg("id_{}".format(slot), "")
		self.registry.set_reg("pwd_{}".format(slot), "")
		self.registry.set_reg("pin{}".format(slot), "")
		
	def is_slot_occupied(self, slot):
		"""Check if account slot is occupied."""
		return bool(self.registry.get_reg("id_{}".format(slot)))


class LoginWindow(ui.ScriptWindow):
	"""Main login window class with improved structure and functionality."""

	IS_TEST = net.IsTest()
	
	def __init__(self, stream):
		super(LoginWindow, self).__init__()
		self._setup_network(stream)
		self._initialize_managers()
		self._initialize_attributes()
		
	def _setup_network(self, stream):
		"""Setup network phase and handlers."""
		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)
		self.stream = stream
		
	def _initialize_managers(self):
		"""Initialize manager objects."""
		self.registry_manager = RegistryManager()
		self.account_manager = AccountManager(self.registry_manager)
		self.channel_manager = ChannelManager()
		
	def _initialize_attributes(self):
		"""Initialize all class attributes."""
		
		self.account_label = {i: None for i in range(5)}
		self.position_label = [30, 70, 110, 150, 190]
		
		self.channel_button = None
		
		if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
			self.loading_prob = False
			
		self._init_ui_components()
		
	def _init_ui_components(self):
		"""Initialize UI component references."""
		self.id_edit_line = None
		self.pwd_edit_line = None
		self.pin_edit_line = None
		self.login_button = None
		self.exit_button = None
		self.channel_button = {}
		self.bg_dark = None
		self.account_data = {}
		self.languageButtonDict = {}
		self.questionDialog = None
		
		# Login failure dictionaries
		self.login_failure_msg_dict = {}
		self.login_failure_func_dict = {}

	def __del__(self):
		super(LoginWindow, self).__del__()
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)

	if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
		def BINARY_SetGuildBuildingList(self, obj):
			"""Set guild building data list."""
			uiGuild.BUILDING_DATA_LIST = obj
			
		def GameLoaded(self):
			"""Handle game loaded event."""
			constInfo.isGameLoaded = True
			
			if self.loading_prob:
				self.stream.popupWindow.Close()
				self._on_click_login_button()

	def Open(self):
		"""Open and initialize the login window."""
		self._setup_login_failure_messages()
		self._setup_window_properties()
		self._load_ui_script()
		self._setup_audio()
		self._setup_input_handling()
		self._initialize_display()
		
	def _setup_login_failure_messages(self):
		"""Setup login failure message dictionaries."""
		self.login_failure_msg_dict = {
			"ALREADY": localeInfo.LOGIN_FAILURE_ALREAY,
			"NOID": localeInfo.LOGIN_FAILURE_NOT_EXIST_ID,
			"WRONGPWD": localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"FULL": localeInfo.LOGIN_FAILURE_TOO_MANY_USER,
			"SHUTDOWN": localeInfo.LOGIN_FAILURE_SHUTDOWN,
			"REPAIR": localeInfo.LOGIN_FAILURE_REPAIR_ID,
			"BLOCK": localeInfo.LOGIN_FAILURE_BLOCK_ID,
			"WRONGMAT": localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT": localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE,
			"BESAMEKEY": localeInfo.LOGIN_FAILURE_BE_SAME_KEY,
			"NOTAVAIL": localeInfo.LOGIN_FAILURE_NOT_AVAIL,
			"NOBILL": localeInfo.LOGIN_FAILURE_NOBILL,
			"BLKLOGIN": localeInfo.LOGIN_FAILURE_BLOCK_LOGIN,
			"WEBBLK": localeInfo.LOGIN_FAILURE_WEB_BLOCK,
			"NOPIN": localeInfo.LOGIN_FAILURE_PIN,
		}

		if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
			self.login_failure_msg_dict.update({
				"LOADING_IN_PROGRESS": localeInfo.LOGIN_FAILURE_LOADING_IN_PROGRESS,
			})

		self.login_failure_func_dict = {
			"WRONGPWD": localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"WRONGMAT": localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT": app.Exit,
		}

		# Add optional features
		if app.ENABLE_HWID_SYSTEM:
			self.login_failure_msg_dict.update({"HWID": localeInfo.LOGIN_FAILURE_HWID})
			self.login_failure_func_dict.update({"HWID": app.Exit})

		if app.CHECK_CLIENT_VERSION:
			self.login_failure_msg_dict.update({"VERSION": localeInfo.LOGIN_WRONG_VERSION})
			self.login_failure_func_dict.update({"VERSION": app.Exit})
			
	def _setup_window_properties(self):
		"""Setup basic window properties."""
		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		self.SetWindowName("LoginWindow")
		
	def _load_ui_script(self):
		"""Load the UI script and bind components."""
		self._load_script("elvion/game/login/loginwindow.py")
		self._check_accounts()
		
	def _setup_audio(self):
		"""Setup background music and sound."""
		if musicInfo.loginMusic != "":
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("content/sound/BGM/" + musicInfo.loginMusic)

		snd.SetSoundVolume(systemSetting.GetSoundVolume())
		
	def _setup_input_handling(self):
		"""Setup input handling and exceptions."""
		ime.AddExceptKey(91)
		ime.AddExceptKey(93)
		
	def _initialize_display(self):
		"""Initialize display state."""
		self.SetChannel("CH1")
		self.Show()
		app.ShowCursor()

		if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
			net.LoadResourcesInCache()

	def Close(self):
		"""Close the login window and cleanup."""
		self._cleanup_audio()
		self._cleanup_ui()
		self._cleanup_input()
		
	def _cleanup_audio(self):
		"""Cleanup audio resources."""
		if musicInfo.loginMusic != "" and musicInfo.selectMusic != "":
			snd.FadeOutMusic("content/sound/BGM/" + musicInfo.loginMusic)
			
	def _cleanup_ui(self):
		"""Cleanup UI resources."""
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.Hide()
		app.HideCursor()
		
	def _cleanup_input(self):
		"""Cleanup input handling."""
		ime.ClearExceptKey()

	def SetIDEditLineFocus(self):
		"""Set focus to ID edit line."""
		if self.id_edit_line is not None:
			self.id_edit_line.SetFocus()

	def SetPasswordEditLineFocus(self):
		"""Set focus to password edit line and clear fields."""
		if self.id_edit_line is not None:
			self.id_edit_line.SetText("")
			self.id_edit_line.SetFocus()
			
		if self.pwd_edit_line is not None:
			self.pwd_edit_line.SetText("")
			
		if self.pin_edit_line is not None:
			self.pin_edit_line.SetText("")

	def SetPinEditLineFocus(self):
		"""Set focus to PIN edit line."""
		if self.pin_edit_line is not None:
			self.pin_edit_line.SetFocus()

	def OnConnectFailure(self):
		"""Handle connection failure."""
		snd.PlaySound("sound/ui/loginfail.wav")
		self.PopupNotifyMessage(localeInfo.LOGIN_CONNECT_FAILURE, self.EmptyFunc)

	def OnHandShake(self):
		"""Handle successful handshake."""
		snd.PlaySound("sound/ui/loginok.wav")
		self.PopupDisplayMessage(localeInfo.LOGIN_CONNECT_SUCCESS)

	def OnLoginStart(self):
		"""Handle login start."""
		self.PopupDisplayMessage(localeInfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		"""Handle login failure with error message."""
		try:
			login_failure_msg = self.login_failure_msg_dict[error]
		except KeyError:
			if error == "INACTIVE":
				login_failure_msg = localeInfo.INTROLOGIN_CONFIRM_MAIL
			else:
				login_failure_msg = localeInfo.LOGIN_FAILURE_UNKNOWN + error

		login_failure_func = self.login_failure_func_dict.get(error, self.EmptyFunc)
		self.PopupNotifyMessage(login_failure_msg, login_failure_func)
		snd.PlaySound("sound/ui/loginfail.wav")

	def _load_script(self, file_name):
		"""Load UI script and bind all components."""
		py_scr_loader = ui.PythonScriptLoader()
		py_scr_loader.LoadScriptFile(self, file_name)

		self._bind_basic_components()
		
		self._bind_channel_buttons()
		
		self._bind_account_components()
		
		self._setup_all_events()
		
	def _bind_basic_components(self):
		"""Bind basic UI components."""
		gc = self.GetChild
		
		self.id_edit_line = gc("id")
		self.pwd_edit_line = gc("pwd")
		self.pin_edit_line = gc("pin")
		self.login_button = gc("login_button")
		self.exit_button = gc("exit_button")
		self.bg_dark = gc("dark_background")
		self.languageButtonDict = {}
		try:
			self.languageButtonDict = {
				"en": gc("language_eu_button"),
				"de": gc("language_de_button"),
				"cz": gc("language_cz_button"),
				"it": gc("language_it_button"),
				"tr": gc("language_tr_button"),
				"ro": gc("language_ro_button"),
				"pl": gc("language_pl_button"),
				"pt": gc("language_pt_button"),
				"hu": gc("language_hu_button"),
				"fr": gc("language_fr_button"),
				"es": gc("language_es_button"),
			}
		except Exception as e:
			import dbg
			dbg.TraceError("Failed to load language buttons: %s" % str(e))
		
	def _bind_channel_buttons(self):
		"""Bind channel selection buttons."""
		gc = self.GetChild
		
		self.channel_button = {
			"CH1": gc("ch1"),
			"CH2": gc("ch2"),
			"CH3": gc("ch3"),
			"CH4": gc("ch4"),
			#"CH5": gc("ch5"),
			#"CH6": gc("ch6")
		}
		
	def _bind_account_components(self):
		"""Bind account management components."""
		gc = self.GetChild
		
		self.account_data = {}
		for i in range(6):
			self.account_data[i] = [
				[gc("load_button_{}".format(i)), 
				gc("save_button_{}".format(i)), 
				gc("delete_button_{}".format(i))],
				gc("account_{}_text".format(i))
			]
			
	def _setup_all_events(self):
		"""Setup all UI event handlers."""
		self._setup_channel_events()
		self._setup_account_events()
		self._setup_button_events()
		self._setup_edit_line_events()
		
	def _setup_channel_events(self):
		"""Setup channel button events."""
		for channel_id, channel_button in self.channel_button.items():
			channel_button.SetEvent(ui.__mem_func__(self.SetChannel), channel_id)
			
	def _setup_account_events(self):
		"""Setup account management events."""
		for key, item in self.account_data.iteritems():
			if isinstance(item[0], list):
				item[0][0].SetEvent(ui.__mem_func__(self.LoadAccount), key)
				item[0][1].SetEvent(ui.__mem_func__(self.SaveAccount), key)
				item[0][2].SetEvent(ui.__mem_func__(self.DeleteAccount), key)
				
	def _setup_button_events(self):
		"""Setup main button events."""
		self.login_button.SetEvent(ui.__mem_func__(self._on_click_login_button))
		self.exit_button.SetEvent(ui.__mem_func__(self.OnPressExitKey))
		
		# Setup language button events
		locale_name = app.GetLocaleName()
		for key, button in self.languageButtonDict.items():
			button.SetEvent(ui.__mem_func__(self.__QuestionChangeLanguage), key)
			if locale_name == key:
				button.Down()
				button.Disable()
		
	def _setup_edit_line_events(self):
		"""Setup edit line events."""
		self.id_edit_line.SetReturnEvent(ui.__mem_func__(self.pwd_edit_line.SetFocus))
		self.id_edit_line.SetTabEvent(ui.__mem_func__(self.pwd_edit_line.SetFocus))
		self.pwd_edit_line.SetReturnEvent(ui.__mem_func__(self._on_click_login_button))
		self.pwd_edit_line.SetTabEvent(ui.__mem_func__(self.pin_edit_line.SetFocus))
		self.pin_edit_line.SetReturnEvent(ui.__mem_func__(self._on_click_login_button))
		self.pin_edit_line.SetTabEvent(ui.__mem_func__(self.id_edit_line.SetFocus))

	def SetChannel(self, channel):
		"""Set the selected channel."""
		for channel_button in self.channel_button.values():
			channel_button.SetUp()
			
		self.channel_button[channel].Down()
		
		self._configure_channel_connection(channel)
		
	def _configure_channel_connection(self, channel):
		"""Configure connection settings for selected channel."""
		server_ip = self.channel_manager.SERVER_IP
		channel_port = self.channel_manager.get_channel_port(channel, 0)
		login_port = self.channel_manager.get_channel_port("LOGIN")
		logo_port = self.channel_manager.get_channel_port("LOGO")
		server_info = self.channel_manager.get_channel_port(channel, 2)
		
		self.stream.SetConnectInfo(server_ip, channel_port, server_ip, login_port)
		net.SetMarkServer(server_ip, logo_port)
		app.SetGuildMarkPath("10.tga")
		app.SetGuildSymbolPath("10")
		net.SetServerInfo(server_info)

	def Connect(self, username, password, pin):
		"""Connect to server with credentials."""
		if constInfo.SEQUENCE_PACKET_ENABLE:
			net.SetPacketSequenceMode()

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeInfo.LOGIN_CONNETING, self.EmptyFunc, localeInfo.UI_CANCEL)

		net.SetVersionId(constInfo.CLIENT_VERSION)
		self.stream.SetLoginInfo(username, password, pin)
		self.stream.Connect()

	def PopupDisplayMessage(self, msg):
		"""Display a popup message."""
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg)

	def PopupNotifyMessage(self, msg, func=None):
		"""Display a notification popup with callback."""
		if func is None:
			func = self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeInfo.UI_OK)

	def OnPressExitKey(self):
		"""Handle exit key press."""
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.stream.SetPhaseWindow(0)
		return True

	def EmptyFunc(self):
		"""Empty function for default callbacks."""
		pass

	def _on_click_login_button(self):
		"""Handle login button click."""
		if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
			if not constInfo.isGameLoaded:
				self.PopupNotifyMessage(
					self.login_failure_msg_dict["LOADING_IN_PROGRESS"], 
					self.EmptyFunc
				)
				self.loading_prob = True
				return

		credentials = self._get_login_credentials()
		validation_result = self._validate_credentials(credentials)
		
		if validation_result:
			self.PopupNotifyMessage(validation_result['message'], validation_result.get('callback', self.EmptyFunc))
			return

		self.Connect(credentials['username'], credentials['password'], credentials['pin'])
		
	def _get_login_credentials(self):
		"""Get login credentials from input fields."""
		return {
			'username': self.id_edit_line.GetText(),
			'password': self.pwd_edit_line.GetText(),
			'pin': self.pin_edit_line.GetText()
		}
		
	def _validate_credentials(self, credentials):
		"""Validate login credentials."""
		if not credentials['username']:
			return {'message': localeInfo.LOGIN_INPUT_ID}
			
		if not credentials['password']:
			return {'message': localeInfo.LOGIN_INPUT_PASSWORD}
			
		if not credentials['pin']:
			return {
				'message': localeInfo.LOGIN_INPUT_PIN,
				'callback': self.SetPinEditLineFocus
			}
			
		return None

	def _check_accounts(self):
		"""Check and update account display."""
		for i in range(6):
			if self.account_manager.is_slot_occupied(i):
				username = self.account_manager.registry.get_reg("id_{}".format(i))
				self.account_data[i][1].SetText(str(username))
				self.account_data[i][0][1].Hide()
				self.account_data[i][0][0].Show()
			else:
				self.account_data[i][1].SetText(localeInfo.INTROLOGIN_NOT_SAVED)
				self.account_data[i][0][1].Show()
				self.account_data[i][0][0].Hide()

	def OnUpdate(self):
		"""Update loop for UI state management."""
		if not self.stream.popupWindow or not self.stream.popupWindow.IsShow():
			self.bg_dark.Hide()
			
		if self.stream.popupWindow.IsShow() and not self.bg_dark.IsShow():
			self.bg_dark.Show()

	def DeleteAccount(self, key):
		"""Delete saved account."""
		if self.account_manager.is_slot_occupied(key):
			self.account_manager.delete_account(key)
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_ACCOUNT_DELETED)
		else:
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_NO_ACCOUNT)
			
		self._check_accounts()

	def LoadAccount(self, key):
		"""Load saved account and attempt login."""
		account_data = self.account_manager.load_account(key)
		
		if account_data:
			self._populate_login_fields(account_data)
			
			if app.ENABLE_PERFORMANCE_IMPROVEMENTS_NEW:
				if not constInfo.isGameLoaded:
					self.PopupNotifyMessage(
						self.login_failure_msg_dict["LOADING_IN_PROGRESS"], 
						self.EmptyFunc
					)
					self.loading_prob = True
					return
					
			self.Connect(account_data['username'], account_data['password'], account_data['pin'])
		else:
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_ACCOUNT_NOT_LOADED)
			
	def _populate_login_fields(self, account_data):
		"""Populate login fields with account data."""
		self.id_edit_line.SetText(str(account_data['username']))
		self.pwd_edit_line.SetText(str(account_data['password']))
		self.pin_edit_line.SetText(str(account_data['pin']))
		self.pwd_edit_line.SetFocus()

	def SaveAccount(self, key):
		"""Save current login credentials."""
		if self.account_manager.is_slot_occupied(key):
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_ACCOUNT_REQUIRED)
			return
		
		credentials = self._get_login_credentials()
		
		if not credentials['username'] or not credentials['password']:
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_ENTER_CREDENTIALS)
			return
		
		success = self.account_manager.save_account(
			key, credentials['username'], credentials['password'], credentials['pin']
		)
		
		if success:
			self.PopupNotifyMessage(localeInfo.INTROLOGIN_SAVED)
			self._check_accounts()
		else:
			self.PopupNotifyMessage("Failed to save account")
			
	def GetIndexByName(self, lang):
		"""Get language index by name."""
		langCode = {
			"en": 0,
			"de": 1,
			"cz": 2,
			"it": 3,
			"tr": 4,
			"ro": 5,
			"pl": 6,
			"pt": 7,
			"hu": 8,
			"fr": 9,
			"es": 10,
		}
		
		try:
			return langCode[lang]
		except:
			return 0
	
	def GetCodePage(self, lang):
		"""Get code page for language."""
		codePageDict = {
			"en": 1252,
			"de": 1252,
			"cz": 1250,
			"it": 1252,
			"tr": 1254,
			"ro": 1250,
			"pl": 1250,
			"pt": 1252,
			"hu": 1250,
			"fr": 1252,
			"es": 1252,
		}
		
		try:
			return codePageDict[lang]
		except:
			return 1252
	
	def __QuestionChangeLanguage(self, lang):
		"""Ask user to confirm language change."""
		import dbg
		dbg.TraceError("Language button clicked: %s (current: %s)" % (lang, app.GetLocaleName()))
	
		if app.GetLocaleName() == lang:
			return
		
		self.questionDialog = uiCommon.QuestionDialog()
		self.questionDialog.SetText("Do you want to change the language?")
		self.questionDialog.SetAcceptEvent(lambda arg=lang: self.OnClickLanguageButton(arg))
		self.questionDialog.SetCancelEvent(lambda arg=lang: self.__QuestionChangeLanguageCancel(arg))
		self.questionDialog.Open()
		
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)
	
	def __QuestionChangeLanguageCancel(self, lang):
		"""Cancel language change."""
		self.OnCloseQuestionDialog()
	
	def OnClickLanguageButton(self, lang):
		"""Change language and restart client."""
		if app.GetLocaleName() != lang:
			with open("_cfg/locale.cfg", "w+") as localeConfig:
				localeConfig.write("10022 %d %s" % (self.GetCodePage(lang), str(lang)))
			
			app.SetDefaultCodePage(self.GetCodePage(lang))
			app.ForceSetLocale(lang, "locale/%s" % (lang))
			
			self.OnCloseQuestionDialog()
			app.ShellExecute("Elvion.exe")  # Update to your exe name
			app.Exit()
	
	def OnCloseQuestionDialog(self):
		"""Close question dialog."""
		if not hasattr(self, 'questionDialog') or not self.questionDialog:
			return
		
		self.questionDialog.Close()
		self.questionDialog = None
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)