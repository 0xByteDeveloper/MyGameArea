import dbg
import app
import net
import ui
import snd
import wndMgr
import musicInfo
import systemSetting
import constInfo
import uiCommon
import time
import serverCommandParser
import ime
import uiScriptLocale
import os
import uitooltip
import binascii
import _winreg
import dates
import serverInfo
import ServerStateChecker
import uiGuild

if not app.ENABLE_PERFORMANCE_BOOST:
	import localeInfo
if app.ENABLE_PERFORMANCE_BOOST:
	import localeInfo as _localeInfo
	localeInfo = _localeInfo.localeInfo()

REG_PATH = dates.REG_PATH
used = 0

if app.ENABLE_MULTI_LANGUAGE_SYSTEM:
	LOCALE_LANG_DICT = {
		app.LOCALE_EN : { "name" : uiScriptLocale.LANGUAGE_EN, "locale" : "en", "code_page" : 1252, "position" : 0},
		app.LOCALE_PT : { "name" : uiScriptLocale.LANGUAGE_PT, "locale" : "pt", "code_page" : 1252, "position" : 0+30},
		app.LOCALE_ES : { "name" : uiScriptLocale.LANGUAGE_ES, "locale" : "es", "code_page" : 1252, "position" : 0+30*2},
		app.LOCALE_FR : { "name" : uiScriptLocale.LANGUAGE_FR, "locale" : "fr", "code_page" : 1252, "position" : 0+30*3},
		app.LOCALE_DE : { "name" : uiScriptLocale.LANGUAGE_DE, "locale" : "de", "code_page" : 1252, "position" : 0+30*4},
		app.LOCALE_RO : { "name" : uiScriptLocale.LANGUAGE_RO, "locale" : "ro", "code_page" : 1250, "position" : 0+30*5},
		app.LOCALE_PL : { "name" : uiScriptLocale.LANGUAGE_PL, "locale" : "pl", "code_page" : 1250, "position" : 0+30*6},
		app.LOCALE_IT : { "name" : uiScriptLocale.LANGUAGE_IT, "locale" : "it", "code_page" : 1252, "position" : 0+30*7},
		app.LOCALE_TR : { "name" : uiScriptLocale.LANGUAGE_TR, "locale" : "tr", "code_page" : 1254, "position" : 0+30*8},
		# app.LOCALE_CZ : { "name" : uiScriptLocale.LANGUAGE_CZ, "locale" : "cz", "code_page" : 1250, "position" : 0+30*9},
		# app.LOCALE_HU : { "name" : uiScriptLocale.LANGUAGE_HU, "locale" : "hu", "code_page" : 1250, "position" : 0+30*10},
	}

def set_reg(name, value):
    try:
        _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE)
        _winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
        _winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        return False

def get_reg(name):
    try:
        registry_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_READ)
        value, regtype = _winreg.QueryValueEx(registry_key, name)
        _winreg.CloseKey(registry_key)
        return str(value)
    except WindowsError:
        return None		

class LoginWindow(ui.ScriptWindow):
	dropped  = 0

	def __init__(self, stream):
		print "NEW LOGIN WINDOW  ----------------------------------------------------------------------------"
		ui.ScriptWindow.__init__(self)
		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)
		self.stream = stream
		self.channels = None
		self.channelButton = None
		self.aID = None

		ServerStateChecker.Create(self)
		self.key = 0
		self.Channeldict = {}
		self.STATE_DICT ={
			0 : '|cffff0000...',
			1 : '|cff32cd32NORM',
			2 : '|cffdaa520BUSY',
			3 : '|cffff0000FULL'	}

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)

	if app.ENABLE_PERFORMANCE_BOOST:
		def BINARY_SetGuildBuildingList(self, obj):
			uiGuild.BUILDING_DATA_LIST = obj

	def Open(self):
		self.loginFailureMsgDict={
			"ALREADY"		: localeInfo.LOGIN_FAILURE_ALREAY,
			"NOID" 			: localeInfo.LOGIN_FAILURE_NOT_EXIST_ID,
			"WRONGPWD"		: localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"FULL"			: localeInfo.LOGIN_FAILURE_TOO_MANY_USER,
			"SHUTDOWN"		: localeInfo.LOGIN_FAILURE_SHUTDOWN,
			"REPAIR"		: localeInfo.LOGIN_FAILURE_REPAIR_ID,
			"BLOCK"			: localeInfo.LOGIN_FAILURE_BLOCK_ID,
			"WRONGMAT"		: localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT" 			: localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER_TRIPLE,
			"BESAMEKEY"		: localeInfo.LOGIN_FAILURE_BE_SAME_KEY,
			"NOTAVAIL"		: localeInfo.LOGIN_FAILURE_NOT_AVAIL,
			"NOBILL"		: localeInfo.LOGIN_FAILURE_NOBILL,
			"BLKLOGIN"		: localeInfo.LOGIN_FAILURE_BLOCK_LOGIN,
			"WEBBLK"		: localeInfo.LOGIN_FAILURE_WEB_BLOCK,
			"BADSCLID"	: localeInfo.LOGIN_FAILURE_WRONG_SOCIALID,
			"AGELIMIT"	: localeInfo.LOGIN_FAILURE_SHUTDOWN_TIME,
		}

		self.loginFailureFuncDict = {
			"WRONGPWD"    : localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"WRONGMAT"    : localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT"        : app.Exit,
		}

		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		self.SetWindowName("LoginWindow")
		self.__LoadScript(uiScriptLocale.LOCALE_UISCRIPT_PATH + "loginwindow.py")
		if musicInfo.loginMusic != "":
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/" + musicInfo.loginMusic)
		snd.SetSoundVolume(systemSetting.GetSoundVolume())
		ime.AddExceptKey(91)
		ime.AddExceptKey(93)
		self.SetChannel("CH1")
		self.idEditLine.SetFocus()
		self.pressKey()
		for aID in xrange(0, 9):
			if get_reg("%d_id" % aID):
				self.accountText[aID].SetText("f%d. %s" % (aID+1, binascii.a2b_base64("%s" % get_reg("%d_id" % aID))))
				self.accountText[aID].SetPackedFontColor(dates.COLOR_HOVER)
				self.accountBgSaveFull[aID].Show()
			else:
				self.accountText[aID].SetPackedFontColor(dates.COLOR_NORMAL)
				self.accountBgSaveFull[aID].Hide()
		self.Show()
		app.ShowCursor()

		if app.ENABLE_MULTI_LANGUAGE_SYSTEM:
			localeName = app.GetLocaleName()

			for i, k in LOCALE_LANG_DICT.items():
				if localeName in LOCALE_LANG_DICT[i]["locale"]:
					net.SetLanguage(i)
					break

	def Close(self):
		if musicInfo.loginMusic != "" and musicInfo.selectMusic != "":
			snd.FadeOutMusic("BGM/"+musicInfo.loginMusic)
		self.idEditLine.SetTabEvent(0)
		self.idEditLine.SetReturnEvent(0)
		self.pwdEditLine.SetReturnEvent(0)
		self.pwdEditLine.SetTabEvent(0)
		self.idEditLine = None
		self.pwdEditLine = None
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.Hide()
		app.HideCursor()
		ime.ClearExceptKey()

		ServerStateChecker.Initialize(self)

	def OnConnectFailure(self):
		snd.PlaySound("sound/ui/loginfail.wav")
		self.PopupNotifyMessage(localeInfo.LOGIN_CONNECT_FAILURE, self.EmptyFunc)

	def OnHandShake(self):
		snd.PlaySound("sound/ui/loginok.wav")
		self.PopupDisplayMessage(localeInfo.LOGIN_CONNECT_SUCCESS)

	def OnLoginStart(self):
		self.PopupDisplayMessage(localeInfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		try:
			loginFailureMsg = self.loginFailureMsgDict[error]
		except KeyError:
			loginFailureMsg = localeInfo.LOGIN_FAILURE_UNKNOWN  + error
		loginFailureFunc = self.loginFailureFuncDict.get(error, self.EmptyFunc)
		self.PopupNotifyMessage(loginFailureMsg, loginFailureFunc)
		snd.PlaySound("sound/ui/loginfail.wav")

	def OnCloseQuestionDialog(self):
		self.questionDialog.Close()
		self.questionDialog = None
		return True

	def __LoadScript(self, fileName):
		try:
			ui.PythonScriptLoader().LoadScriptFile(self, fileName)
			self.loginBoard						= self.GetChild("LoginBoard")
			self.loginButton					= self.GetChild("LoginButton")
			self.idEditLines					= self.GetChild("id_editline_s")
			self.pwdEditLines					= self.GetChild("pwd_editlines")
			self.accountSaveBoardSave			= self.GetChild("accountLog")
			self.accountSaveBoardSave.Show()
			self.accountText = {
				0 : self.GetChild("account_1"),
				1 : self.GetChild("account_2"),
				2 : self.GetChild("account_3"),
				3 : self.GetChild("account_4"),
				4 : self.GetChild("account_5"),
				5 : self.GetChild("account_6"),
				6 : self.GetChild("account_7"),
				7 : self.GetChild("account_8"),
				8 : self.GetChild("account_9")}
			self.accountBgSaveFull = {
				0 : self.GetChild("bg_account_save_full_1"),
				1 : self.GetChild("bg_account_save_full_2"),
				2 : self.GetChild("bg_account_save_full_3"),
				3 : self.GetChild("bg_account_save_full_4"),
				4 : self.GetChild("bg_account_save_full_5"),
				5 : self.GetChild("bg_account_save_full_6"),
				6 : self.GetChild("bg_account_save_full_7"),
				7 : self.GetChild("bg_account_save_full_8"),
				8 : self.GetChild("bg_account_save_full_9")}
			self.channelBoard					= self.GetChild("channelBoard")
			self.langBoard					= self.GetChild("boardLang")
		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.BindObject")
		self.LoginInputs()
		self.ChannelSelectFunction()
		self.clickOnTextLinks()
		self.saveAccountChenars()
		if app.ENABLE_MULTI_LANGUAGE_SYSTEM:
			self.boardLangFunction()
		self.loginButton.SetEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.toolTipSaveButton = uitooltip.ToolTip()

		self.AddChannel("CH1", dates.IP, dates.CH1)
		self.AddChannel("CH2", dates.IP, dates.CH2)
		self.AddChannel("CH3", dates.IP, dates.CH3)
		self.AddChannel("CH4", dates.IP, dates.CH4)
		self.AddChannel("CH5", dates.IP, dates.CH5)
		self.AddChannel("CH6", dates.IP, dates.CH6)
		self.Request()

	if app.ENABLE_MULTI_LANGUAGE_SYSTEM:
		def boardLangFunction(self):
			self.langButton = {}
			tab = 0

			languageList = LOCALE_LANG_DICT
			if not LOCALE_LANG_DICT:
				return

			for i, k in enumerate(languageList):
				self.langButton[tab] = ui.Button()
				self.langButton[tab].SetParent(self.langBoard)
				self.langButton[tab].SetPosition(LOCALE_LANG_DICT[k]["position"],0)
				self.langButton[tab].SetUpVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_normal.tga" % LOCALE_LANG_DICT[k]["locale"])
				self.langButton[tab].SetOverVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_hover.tga" % LOCALE_LANG_DICT[k]["locale"])
				self.langButton[tab].SetDownVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_hover.tga" % LOCALE_LANG_DICT[k]["locale"])
				self.langButton[tab].SetEvent(ui.__mem_func__(self.__QuestionChangeLanguage),k)
				self.langButton[tab].Show()
				# for (tab, langButton) in self.langButton.items():
					# langButton.SetEvent(ui.__mem_func__(self.__QuestionChangeLanguage),tab)
				tab += 1
			
			self.slotLangSelect = (
				self.langButton[0],
				self.langButton[1],
				self.langButton[2],
				self.langButton[3],
				self.langButton[4],
				self.langButton[5],
				self.langButton[6],
				self.langButton[7],
				self.langButton[8],
			)

		def __QuestionChangeLanguage(self, index):

			testChange = ""
			if index == app.LOCALE_EN:
				testChange = "Do you want to change current language in EN?"
			elif index == app.LOCALE_PT:
				testChange = "Do you want to change current language in PT?"
			elif index == app.LOCALE_ES:
				testChange = "Do you want to change current language in ES?"
			elif index == app.LOCALE_FR:
				testChange = "Do you want to change current language in FR?"
			elif index == app.LOCALE_DE:
				testChange = "Do you want to change current language in DE?"
			elif index == app.LOCALE_RO:
				testChange = "Do you want to change current language in RO?"
			elif index == app.LOCALE_PL:
				testChange = "Do you want to change current language in PL?"
			elif index == app.LOCALE_IT:
				testChange = "Do you want to change current language in IT?"
			elif index == app.LOCALE_TR:
				testChange = "Do you want to change current language in TR?"
			
			self.questionDialog = uiCommon.QuestionDialog()
			self.questionDialog.SetText(testChange)
			self.questionDialog.SetAcceptEvent(lambda lang = index: self.OnClickLanguageButton(lang))
			self.questionDialog.SetCancelEvent(lambda lang = index: self.__QuestionChangeLanguageCancel())
			self.questionDialog.Open()
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

		def OnClickLanguageButton(self, lang):

			locale = LOCALE_LANG_DICT[lang]["locale"]
			code_page = LOCALE_LANG_DICT[lang]["code_page"]

			if self.__SaveLoca(code_page, locale):
				self.OnCloseQuestionDialog()
				net.SendChangeLanguagePacket(lang)
				# net.ExitGameLanguageChange() # ReloadModule
				net.ExitGame()
				app.Exit()

		def __SaveLoca(self, code_page, locale):
			if app.SetLoca(code_page, locale):
				return True

			return False

		def OnCloseQuestionDialog(self):
			if not self.questionDialog:
				return

			self.questionDialog.Close()
			self.questionDialog = None
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

		def __QuestionChangeLanguageCancel(self):
			self.OnCloseQuestionDialog()

		def OnCloseQuestionDialog(self):
			if not self.questionDialog:
				return
			
			self.questionDialog.Close()
			self.questionDialog = None
			constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)
			
		def __QuestionChangeLanguageCancel(self):
			self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return
		
		self.questionDialog.Close()
		self.questionDialog = None
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def AddChannel(self, name, ip, port):
		# ip = dates.IP
		# port = dates.CH1
		self.key = self.key+1
		self.Channeldict[name] = {"key": self.key, "port": port, "ip": ip, "state" : self.GetNone()}
		ServerStateChecker.AddChannel(self.key, ip, port)

	def GetNameByKey(self, key):
		for k in self.Channeldict:
			if(self.Channeldict[k]["key"] == key):
				return k
		return "NONE"

	def Request(self):
		ServerStateChecker.Request()

	def GetNone(self):
		return self.STATE_DICT[0]

	def GetState(self, name):
		try:
			return self.Channeldict[name]["state"]
		except:
			return self.GetNone()

	def IsOnline(self, name):
		if(self.GetState(name) != self.GetNone()):
			return True
		return False

	def NotifyChannelState(self, key, state):
		try:
			stateName=self.STATE_DICT[state]
		except:
			stateName=self.GetNone()
		name = self.GetNameByKey(key)
		if(name != "NONE"):
			self.Channeldict[name]["state"] = stateName

	def SetChannel(self, ch):
		self.SetChannelInfo(ch)
		self.stream.SetConnectInfo(dates.IP, self.ChannelPort(ch, 0), dates.IP, self.ChannelPort("LOGIN"))
		net.SetMarkServer(dates.IP, self.ChannelPort("LOGO"))
		app.SetGuildMarkPath("10.tga")
		app.SetGuildSymbolPath("10")
		net.SetServerInfo(self.ChannelPort(ch, 2))

	def SetChannelInfo(self, ch):
		self.channels = str(ch)

	def GetChannel(self):
		return self.channels

	def ChannelPort(self, ch="CH1", value=0):
		channel = {
			"CH1"    :    [dates.CH1, "Ch1", dates.NAME],
			"CH2"    :    [dates.CH2, "Ch2", dates.NAME],
			"CH3"    :    [dates.CH3, "Ch3", dates.NAME],
			"CH4"    :    [dates.CH4, "Ch4", dates.NAME],
			"CH5"    :    [dates.CH3, "Ch5", dates.NAME],
			"CH6"    :    [dates.CH4, "Ch6", dates.NAME]}

		if ch == "LOGIN":
			return dates.AUTH
		elif ch == "LOGO":
			return channel["CH1"][0]
		elif value == 2:
			return "%s, %s" % (channel[ch][1], channel[ch][2])
		else:
			return channel[ch][value]

	def Connect(self, id, pwd):
		if constInfo.SEQUENCE_PACKET_ENABLE:
			net.SetPacketSequenceMode()
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeInfo.LOGIN_CONNETING, self.EmptyFunc, localeInfo.UI_CANCEL)
		if os.path.exists('D:\\ymir work'):
			self.OnLoginFailure("YMIR_WORK")
			return 
		self.stream.SetLoginInfo(id, pwd)
		self.stream.Connect()

	def PopupDisplayMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, self.EmptyFunc)

	def PopupNotifyMessage(self, msg, func=0):
		if not func:
			func = self.EmptyFunc
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeInfo.UI_OK)

	def OnPressExitKey(self):
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.stream.SetPhaseWindow(0)
		return True

	def OnUpdate(self):
		self.descritonOverButtons()
		ServerStateChecker.Update()

		if self.IsOnline("CH1") is True:
			self.SlotState[0].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[0].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[0].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[0].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH2") is True:
			self.SlotState[1].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[1].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[1].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[1].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH3") is True:
			self.SlotState[2].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[2].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[2].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[2].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH4") is True:
			self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[3].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[3].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH5") is True:
			self.SlotState[4].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[4].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[4].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[4].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH6") is True:
			self.SlotState[5].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[5].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[5].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[5].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")

	def EmptyFunc(self):
		pass

	def __OnClickLoginButton(self):
		id = self.idEditLine.GetText()
		pwd = self.pwdEditLine.GetText()
		if len(id)==0:
			self.PopupNotifyMessage(localeInfo.LOGIN_INPUT_ID, self.EmptyFunc)
			return
		if len(pwd)==0:
			self.PopupNotifyMessage(localeInfo.LOGIN_INPUT_PASSWORD, self.EmptyFunc)
			return
		self.Connect(id, pwd)

	def LoginInputs(self):
		self.idEditLine = ui.SpecialEditLine()
		self.idEditLine.SetParent(self.idEditLines)
		self.idEditLine.SetPosition(32,-22)
		self.idEditLine.SetMax(35)
		self.idEditLine.SetIMEFlag(0)
		self.idEditLine.SetPackedFontColor(dates.COLOR_HOVER)
		self.idEditLine.Show()
		self.pwdEditLine = ui.SpecialEditLine()
		self.pwdEditLine.SetParent(self.pwdEditLines)
		self.pwdEditLine.SetPosition(32,-22)
		self.pwdEditLine.SetMax(35)
		self.pwdEditLine.SetIMEFlag(0)
		self.pwdEditLine.SetSecret(1)
		self.pwdEditLine.SetPackedFontColor(dates.COLOR_HOVER)
		self.pwdEditLine.Show()
		self.idEditLine.SetReturnEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.idEditLine.SetTabEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.pwdEditLine.SetReturnEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.pwdEditLine.SetTabEvent(ui.__mem_func__(self.idEditLine.SetFocus))

	def ChannelSelectFunction(self):
		self.channelSelect = {}
		self.button_text = {}
		self.StateChannel = {}
		self.StateChannelIcon = {}
		tab = 0
		buttons_info = [
			[[0,0,"Channel1"]],
			[[71+10,0,"Channel2"]],
			[[142+20,0,"Channel3"]],
			[[0,35,"Channel4"]],
			[[71+10,35,"Channel5"]],
			[[142+20,35,"Channel6"]]
		]
		for a in buttons_info:
			self.StateChannelIcon[tab] = ui.ImageBox()
			self.StateChannelIcon[tab].SetParent(self.channelBoard)
			self.StateChannelIcon[tab].SetPosition(a[0][0],a[0][1])
			self.StateChannelIcon[tab].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
			self.StateChannelIcon[tab].Show()
			self.channelSelect[tab] = ui.RadioButton() 
			self.channelSelect[tab].SetParent(self.StateChannelIcon[tab])
			self.channelSelect[tab].SetPosition(0,0)
			self.channelSelect[tab].SetUpVisual(ui.PATCH_COMMON+"/select-o-empty.tga")
			self.channelSelect[tab].SetOverVisual(ui.PATCH_COMMON+"/select-o-full.tga")
			self.channelSelect[tab].SetDownVisual(ui.PATCH_COMMON+"/select-o-full.tga")
			self.channelSelect[tab].Show()
			self.button_text[tab] = ui.TextLine()
			self.button_text[tab].SetParent(self.StateChannelIcon[tab])
			self.button_text[tab].SetPosition(18,-5)
			self.button_text[tab].SetHorizontalAlignLeft()
			self.button_text[tab].SetText(a[0][2])
			self.button_text[tab].SetPackedFontColor(dates.COLOR_HOVER)
			self.button_text[tab].Show()
			self.StateChannel[tab] = ui.TextLine()
			self.StateChannel[tab].SetParent(self.StateChannelIcon[tab])
			self.StateChannel[tab].SetPosition(20,5)
			self.StateChannel[tab].SetText(self.STATE_DICT[0])
			self.StateChannel[tab].SetHorizontalAlignLeft()
			self.StateChannel[tab].Show()
			tab +=1
		self.Slot1 = (
			self.channelSelect[0],
			self.channelSelect[1],
			self.channelSelect[2],
			self.channelSelect[3],
			self.channelSelect[4],
			self.channelSelect[5],
		)
		self.Slot1_1 = (
			self.button_text[0],
			self.button_text[1],
			self.button_text[2],
			self.button_text[3],
			self.button_text[4],
			self.button_text[5],
		)
		self.SlotState = (
			self.StateChannel[0],
			self.StateChannel[1],
			self.StateChannel[2],
			self.StateChannel[3],
			self.StateChannel[4],
			self.StateChannel[5],
		)

		self.SlotStateIcon = (
			self.StateChannelIcon[0],
			self.StateChannelIcon[1],
			self.StateChannelIcon[2],
			self.StateChannelIcon[3],
			self.StateChannelIcon[4],
			self.StateChannelIcon[5],
		)

		self.Slot1[0].SetEvent((lambda : self.OpenEvents(0,1)))
		self.Slot1[0].Down()
		self.Slot1[1].SetEvent((lambda : self.OpenEvents(1,2)))
		self.Slot1[2].SetEvent((lambda : self.OpenEvents(2,3)))
		self.Slot1[3].SetEvent((lambda : self.OpenEvents(3,4)))
		self.Slot1[4].SetEvent((lambda : self.OpenEvents(4,5)))
		self.Slot1[5].SetEvent((lambda : self.OpenEvents(5,6)))

		if self.IsOnline("CH1") is True:
			self.SlotState[0].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[0].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[0].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[0].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH2") is True:
			self.SlotState[1].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[1].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[1].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[1].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH3") is True:
			self.SlotState[2].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[2].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[2].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[2].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH4") is True:
			self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[3].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[3].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH5") is True:
			self.SlotState[4].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[4].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[4].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[4].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")
		if self.IsOnline("CH6") is True:
			self.SlotState[5].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[5].LoadImage(ui.PATCH_COMMON+"/icon-online.tga")
		else:
			self.SlotState[5].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[5].LoadImage(ui.PATCH_COMMON+"/icon-offline.tga")

	def OpenEvents(self,index,arg):
		for btn in self.Slot1:
			btn.SetUp()
		self.Slot1[index].Down()
		if index == 0:
			self.SetChannel("CH%s" % arg)
		if index == 1:
			self.SetChannel("CH%s" % arg)
		if index == 2:
			self.SetChannel("CH%s" % arg)
		if index == 3:
			self.SetChannel("CH%s" % arg)
		if index == 4:
			self.SetChannel("CH%s" % arg)
		if index == 5:
			self.SetChannel("CH%s" % arg)

	def clickOnTextLinks(self):
		self.ForgotButton = ui.TextLink()
		self.ForgotButton.SetParent(self.loginBoard)
		self.ForgotButton.SetPosition(0,115)
		self.ForgotButton.SetText(uiScriptLocale.LOGIN_INTERFACE_PW_LOST)
		self.ForgotButton.SetEvent(ui.__mem_func__(self.__OnClickForgotButton))
		self.ForgotButton.Show()

	def __OnClickForgotButton(self):
		os.system("start " + dates.BTN_LINK)

	def saveAccountChenars(self):
		self.chenar = {}
		self.loginSaveButton = {}
		self.deleteButton = {}
		self.saveButton = {}
		self.iconSave = {}
		tab = 0
		chenars =[
			[[0,60,0]],
			[[90,150,0]],
			[[180,240,0]],
			[[0,60,40]],
			[[90,150,40]],
			[[180,240,40]],
			[[0,60,80]],
			[[90,150,80]],
			[[180,240,80]]
		]
		for a in chenars:
			self.loginSaveButton[tab] = ui.Button()
			self.loginSaveButton[tab].SetParent(self.accountSaveBoardSave)
			self.loginSaveButton[tab].SetPosition(a[0][0],a[0][2])
			self.loginSaveButton[tab].SetUpVisual(dates.PATCH_LOGIN+"/select-account-btn-normal.tga")
			self.loginSaveButton[tab].SetOverVisual(dates.PATCH_LOGIN+"/select-account-btn-over.tga")
			self.loginSaveButton[tab].SetDownVisual(dates.PATCH_LOGIN+"/select-account-btn-normal.tga")
			self.loginSaveButton[tab].Show()
			self.saveButton[tab] = ui.Button()
			self.saveButton[tab].SetParent(self.accountSaveBoardSave)
			self.saveButton[tab].SetPosition(a[0][0],a[0][2])
			self.saveButton[tab].SetUpVisual(dates.PATCH_LOGIN+"/select-account-btn-normal.tga")
			self.saveButton[tab].SetOverVisual(dates.PATCH_LOGIN+"/select-account-btn-over.tga")
			self.saveButton[tab].SetDownVisual(dates.PATCH_LOGIN+"/select-account-btn-normal.tga")
			self.saveButton[tab].Show()
			self.deleteButton[tab] = ui.Button()
			self.deleteButton[tab].SetParent(self.accountSaveBoardSave)
			self.deleteButton[tab].SetPosition(a[0][1]+15,a[0][2]+25)
			self.deleteButton[tab].SetUpVisual(ui.PATCH_COMMON+"/toggle-clear-normal.tga")
			self.deleteButton[tab].SetOverVisual(ui.PATCH_COMMON+"/toggle-clear-over.tga")
			self.deleteButton[tab].SetDownVisual(ui.PATCH_COMMON+"/toggle-clear-normal.tga")
			self.deleteButton[tab].Show()
			for (tab, loginSaveButton) in self.loginSaveButton.items():
				if get_reg("%d_id" % tab) == "" or get_reg("%d_id" % tab) == None:
					loginSaveButton.Hide()
				loginSaveButton.SetEvent(ui.__mem_func__(self.autoLogin),tab)
			for (tab, saveButton) in self.saveButton.items():
				if get_reg("%d_id" % tab):
					saveButton.Hide()
				saveButton.SetEvent(ui.__mem_func__(self.saveAccountFunction),tab)
			for (tab, deleteButton) in self.deleteButton.items():
				if get_reg("%d_id" % tab) == "" or get_reg("%d_id" % tab) == None:
					deleteButton.Hide()
				deleteButton.SetEvent(ui.__mem_func__(self.deleteAccountFunction),tab)
			tab +=1

		self.slotLoginSaveBtn = (
			self.loginSaveButton[0],
			self.loginSaveButton[1],
			self.loginSaveButton[2],
			self.loginSaveButton[3],
			self.loginSaveButton[4],
			self.loginSaveButton[5],
			self.loginSaveButton[6],
			self.loginSaveButton[7],
			self.loginSaveButton[8],
		)

		self.slotSaveBtn = (
			self.saveButton[0],
			self.saveButton[1],
			self.saveButton[2],
			self.saveButton[3],
			self.saveButton[4],
			self.saveButton[5],
			self.saveButton[6],
			self.saveButton[7],
			self.saveButton[8],
		)

		self.slotDeleteBtn = (
			self.deleteButton[0],
			self.deleteButton[1],
			self.deleteButton[2],
			self.deleteButton[3],
			self.deleteButton[4],
			self.deleteButton[5],
			self.deleteButton[6],
			self.deleteButton[7],
			self.deleteButton[8],
		)

	def deleteAccountFunction(self,index):
		if index == 0:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index == 1:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index == 2:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==3:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==4:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==5:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==6:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==7:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
		if index ==8:
			if get_reg("%d_id" % index):
				set_reg("%d_id" % index, "")
				set_reg("%d_pwd" % index, "")
				self.accountText[index].SetText(uiScriptLocale.LOGIN_INTERFACE_SAVE_EMPTY)
				self.idEditLine.SetText("")
				self.pwdEditLine.SetText("")
				self.slotSaveBtn[index].Show()
				self.slotDeleteBtn[index].Hide()
				self.slotLoginSaveBtn[index].Hide()
				self.accountBgSaveFull[index].Hide()
			else:
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_DELETE_FAIL, self.EmptyFunc)

	def saveAccountFunction(self,index):
		if self.idEditLine.GetText() == "" or self.pwdEditLine.GetText() == "":
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_FAIL, self.EmptyFunc)
			return
		if index == 0:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f1." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 1:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f2." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 2:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f3." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 3:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f4." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 4:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f5." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 5:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f6." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 6:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f7." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 7:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f8." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 8:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText("f9." + self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()

	def pressKey(self):
		onPressKeyDict = {}
		onPressKeyDict[app.DIK_F1]	= lambda : self.autoLogin(6)
		onPressKeyDict[app.DIK_F2]	= lambda : self.autoLogin(1)
		onPressKeyDict[app.DIK_F3]	= lambda : self.autoLogin(2)
		onPressKeyDict[app.DIK_F4]	= lambda : self.autoLogin(3)
		onPressKeyDict[app.DIK_F5]	= lambda : self.autoLogin(4)
		onPressKeyDict[app.DIK_F6]	= lambda : self.autoLogin(0)
		onPressKeyDict[app.DIK_F7]	= lambda : self.autoLogin(6)
		onPressKeyDict[app.DIK_F8]	= lambda : self.autoLogin(7)
		onPressKeyDict[app.DIK_F9]	= lambda : self.autoLogin(8)
		self.onPressKeyDict = onPressKeyDict

	def OnKeyDown(self, key):
		try:
			self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise
		return True

	def autoLogin(self,index):
		if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SLOT_EMPTY, self.EmptyFunc)
			return
		if index == 0:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 1:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 2:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 3:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 4:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 5:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 6:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 7:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()
		elif index == 8:
			if get_reg("%d_id" % index):
				self.idEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % index)))
				self.pwdEditLine.SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_pwd" % index)))
				self.pwdEditLine.SetPlaceHolderText("***********************")
				self.__OnClickLoginButton()

	def descritonOverButtons(self):
		if self.saveButton[0].IsIn() ^ self.saveButton[1].IsIn() ^ self.saveButton[2].IsIn() ^ self.saveButton[3].IsIn() ^ self.saveButton[4].IsIn() ^ self.saveButton[5].IsIn() ^ self.saveButton[6].IsIn() ^ self.saveButton[7].IsIn() ^ self.saveButton[8].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_SAVE_BUTTON, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		elif self.deleteButton[0].IsIn() ^ self.deleteButton[1].IsIn() ^ self.deleteButton[2].IsIn() ^ self.deleteButton[3].IsIn() ^ self.deleteButton[4].IsIn() ^ self.deleteButton[5].IsIn() ^ self.deleteButton[6].IsIn() ^ self.deleteButton[7].IsIn() ^ self.deleteButton[8].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_DELETE_BUTTON, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		elif self.loginSaveButton[0].IsIn() ^ self.loginSaveButton[1].IsIn() ^ self.loginSaveButton[2].IsIn() ^ self.loginSaveButton[3].IsIn() ^ self.loginSaveButton[4].IsIn() ^ self.loginSaveButton[5].IsIn() ^ self.loginSaveButton[6].IsIn() ^ self.loginSaveButton[7].IsIn() ^ self.loginSaveButton[8].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_LOGIN_SAVE_BUTTON, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		elif self.channelSelect[0].IsIn() ^ self.channelSelect[1].IsIn() ^ self.channelSelect[2].IsIn() ^ self.channelSelect[3].IsIn() ^ self.channelSelect[4].IsIn() ^ self.channelSelect[5].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_SELECT_CHANNEL, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		else:
			self.toolTipSaveButton.HideToolTip()

