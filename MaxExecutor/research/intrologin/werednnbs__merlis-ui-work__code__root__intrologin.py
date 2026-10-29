import app
import net
import ui
import snd
import wndMgr
import musicInfo
import systemSetting
import localeInfo
import constInfo
import ime
import uiScriptLocale
import os
import uitooltip
import binascii
import _winreg
import dates
import serverInfo
import ServerStateChecker

REG_PATH = dates.REG_PATH
used = 0

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
		for aID in xrange(0, 6):
			if get_reg("%d_id" % aID):
				self.accountText[aID].SetText("%s" % binascii.a2b_base64("%s" % get_reg("%d_id" % aID)))
				self.accountText[aID].SetPackedFontColor(dates.COLOR_HOVER)
				self.accountBgSaveFull[aID].Show()
			else:
				self.accountText[aID].SetPackedFontColor(dates.COLOR_NORMAL)
				self.accountBgSaveFull[aID].Hide()
		self.Show()
		app.ShowCursor()

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
				5 : self.GetChild("account_6")}
			self.accountBgSaveFull = {
				0 : self.GetChild("bg_account_save_full_1"),
				1 : self.GetChild("bg_account_save_full_2"),
				2 : self.GetChild("bg_account_save_full_3"),
				3 : self.GetChild("bg_account_save_full_4"),
				4 : self.GetChild("bg_account_save_full_5"),
				5 : self.GetChild("bg_account_save_full_6")}
			self.channelBoard					= self.GetChild("channelBoard")
			self.langBoard					= self.GetChild("boardLang")
		except:
			import exception
			exception.Abort("LoginWindow.__LoadScript.BindObject")
		self.LoginInputs()
		self.ChannelSelectFunction()
		self.clickOnTextLinks()
		self.saveAccountChenars()
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

	def boardLangFunction(self):

		self.langButton = {}
		# self.landFlagButton = {}
		# self.landTextTitleButton = {}

		tab = 0
		langars =[
		[[20,"de"]],
		[[50,"en"]],
		[[80,"tr"]],
		[[110,"ro"]],
		[[140,"pl"]],
		[[170,"pt"]],
		[[200,"fr"]],
		[[230,"es"]],
		[[260,"it"]]]

		# self.titleTextLang = ui.TextLine()
		# self.titleTextLang.SetParent(self.DropDownBoard)
		# self.titleTextLang.SetPosition(0,0)
		# self.titleTextLang.SetText("en")
		# self.titleTextLang.SetPackedFontColor(dates.COLOR_NORMAL)
		# self.titleTextLang.Show()
		# self.dropDownBg = ui.ImageBox()
		# self.dropDownBg.SetParent(self.DropDownBoard)
		# self.dropDownBg.SetPosition(0,20)
		# self.dropDownBg.LoadImage(dates.PATCH_LOGIN+"/bg-dropdown.tga")
		# self.dropDownBg.Hide()
		# self.dropDownButton = ui.Button()
		# self.dropDownButton.SetParent(self.DropDownBoard)
		# self.dropDownButton.SetPosition(120,0)
		# self.dropDownButton.SetUpVisual(dates.PATCH_LOGIN+"/drop-down-botton-normal.tga")
		# self.dropDownButton.SetOverVisual(dates.PATCH_LOGIN+"/drop-down-botton-over.tga")
		# self.dropDownButton.SetDownVisual(dates.PATCH_LOGIN+"/drop-down-botton-normal.tga")
		# self.dropDownButton.SetEvent(ui.__mem_func__(self.dropDownButtonFuntion))
		# self.dropDownButton.Show()
		# self.textLangTitle = ui.TextLine()
		# self.textLangTitle.SetParent(self.DropDownBoard)
		# self.textLangTitle.SetPosition(105,-2)
		# self.textLangTitle.SetText("en")
		# self.textLangTitle.SetPackedFontColor(dates.COLOR_NORMAL)
		# self.textLangTitle.Show()

		for a in langars:
			self.langButton[tab] = ui.Button()
			self.langButton[tab].SetParent(self.langBoard)
			self.langButton[tab].SetPosition(a[0][0],0)
			self.langButton[tab].SetUpVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_normal.tga" % a[0][1])
			self.langButton[tab].SetOverVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_hover.tga" % a[0][1])
			self.langButton[tab].SetDownVisual(dates.PATCH_CHAT_FLAG+"/flag_%s_normal.tga" % a[0][1])
			self.langButton[tab].Show()
			# self.landFlagButton[tab] = ui.ImageBox()
			# self.landFlagButton[tab].SetParent(self.langButton[tab])
			# self.landFlagButton[tab].SetPosition(12,4)
			# self.landFlagButton[tab].LoadImage(dates.PATCH_CHAT_FLAG+"/flag_%s.tga" % a[0][2])
			# self.landFlagButton[tab].Show()
			# self.landTextTitleButton[tab] = ui.TextLine()
			# self.landTextTitleButton[tab].SetParent(self.langButton[tab])
			# self.landTextTitleButton[tab].SetPosition(50,8)
			# self.landTextTitleButton[tab].SetText(a[0][1])
			# self.landTextTitleButton[tab].SetPackedFontColor(dates.COLOR_HOVER)
			# self.landTextTitleButton[tab].Show()
			for (tab, langButton) in self.langButton.items():
			 	langButton.SetEvent(ui.__mem_func__(self.langButtonFunction),tab)
			tab +=1

	def langButtonFunction():
		pass

	# def dropDownButtonFuntion(self):
	# 	if self.dropped == 1:
	# 		self.dropDownBg.Hide()
	# 		self.dropped = 0
	# 	else:
	# 		self.dropDownBg.Show()
	# 		self.dropped = 1

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
			"CH3"    :    [dates.CH3, "Ch3", dates.NAME],
			"CH4"    :    [dates.CH4, "Ch4", dates.NAME]}

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
			# self.SlotState[0].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[0].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[0].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[0].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH2") is True:
			# self.SlotState[1].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[1].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[1].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[1].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH3") is True:
			# self.SlotState[2].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[2].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[2].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[2].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH4") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[3].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[3].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH5") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[4].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[4].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH6") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[5].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[5].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		# if self.IsOnline("CH5") is True:
		# 	self.SlotState[4].SetText(self.STATE_DICT[1])
		# else:
		# 	self.SlotState[5].SetText(self.STATE_DICT[0])
		# if self.IsOnline("CH6") is True:
		# 	self.SlotState[5].SetText(self.STATE_DICT[1])
		# else:
		# 	self.SlotState[5].SetText(self.STATE_DICT[0])

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
		self.idEditLine.SetPosition(10,-15)
		self.idEditLine.SetSize(266,33)
		self.idEditLine.SetMax(35)
		self.idEditLine.SetIMEFlag(0)
		self.idEditLine.SetPlaceHolderText(uiScriptLocale.LOGIN_INTERFACE_TEXT_INPUT_ID)
		self.idEditLine.SetPlaceHolderTextColor(0xff5d4d4b)
		self.idEditLine.SetPackedFontColor(dates.COLOR_HOVER)
		self.idEditLine.Show()
		self.pwdEditLine = ui.SpecialEditLine()
		self.pwdEditLine.SetParent(self.pwdEditLines)
		self.pwdEditLine.SetPosition(10,-15)
		self.pwdEditLine.SetSize(266,33)
		self.pwdEditLine.SetMax(35)
		self.pwdEditLine.SetIMEFlag(0)
		self.pwdEditLine.SetSecret(1)
		self.pwdEditLine.SetPlaceHolderText(uiScriptLocale.LOGIN_INTERFACE_TEXT_INPUT_PASS)
		self.pwdEditLine.SetPlaceHolderTextColor(0xff5d4d4b)
		self.pwdEditLine.SetPackedFontColor(dates.COLOR_HOVER)
		self.pwdEditLine.Show()
		self.idEditLine.SetReturnEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.idEditLine.SetTabEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.pwdEditLine.SetReturnEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.pwdEditLine.SetTabEvent(ui.__mem_func__(self.idEditLine.SetFocus))

	def ChannelSelectFunction(self):
		self.channelSelect = {}
		self.button_text = {}
		self.ShowChannel = {}
		# self.StateChannel = {}
		self.StateChannelIcon = {}
		tab = 0
		buttons_info = [
			[[0,0,"CH1","Channel1"]],
			[[71,0,"CH2","Channel2"]],
			[[142,0,"CH3","Channel3"]],
			[[0,30,"CH4","Channel4"]],
			[[71,30,"CH5","Channel5"]],
			[[142,30,"CH6","Channel6"]]
		]
		for a in buttons_info:
			self.channelSelect[tab] = ui.RadioButton() 
			self.channelSelect[tab].SetParent(self.channelBoard)
			self.channelSelect[tab].SetPosition(a[0][0],a[0][1])
			self.channelSelect[tab].SetUpVisual(dates.PATCH_LOGIN+"/select-btn-empty.tga")
			self.channelSelect[tab].SetOverVisual(dates.PATCH_LOGIN+"/select-btn-full.tga")
			self.channelSelect[tab].SetDownVisual(dates.PATCH_LOGIN+"/select-btn-full.tga")
			self.channelSelect[tab].Show()
			self.StateChannelIcon[tab] = ui.ImageBox()
			self.StateChannelIcon[tab].SetParent(self.channelSelect[tab])
			self.StateChannelIcon[tab].SetPosition(0,22)
			self.StateChannelIcon[tab].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
			self.StateChannelIcon[tab].Show()
			self.button_text[tab] = ui.TextLine()
			self.button_text[tab].SetParent(self.channelSelect[tab])
			self.button_text[tab].SetPosition(34,5)
			self.button_text[tab].SetHorizontalAlignCenter()
			self.button_text[tab].SetText(a[0][3])
			self.button_text[tab].SetPackedFontColor(dates.COLOR_HOVER)
			self.button_text[tab].Show()
			self.ShowChannel[tab] = ui.TextLine()
			self.ShowChannel[tab].SetParent(self.loginBoard)
			self.ShowChannel[tab].SetPosition(10,70)
			self.ShowChannel[tab].SetPackedFontColor(dates.COLOR_NORMAL)
			self.ShowChannel[tab].SetText(uiScriptLocale.LOGIN_INTERFACE_CHANNEL_SELECTED + a[0][2])
			self.ShowChannel[tab].Hide()
			# self.StateChannel[tab] = ui.TextLine()
			# self.StateChannel[tab].SetParent(self.StateChannelIcon[tab])
			# self.StateChannel[tab].SetPosition(36,40)
			# self.StateChannel[tab].SetText(self.STATE_DICT[0])
			# self.StateChannel[tab].SetPackedFontColor(dates.COLOR_NORMAL)
			# self.StateChannel[tab].SetHorizontalAlignCenter()
			# self.StateChannel[tab].Show()
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
		self.SlotShow = (
			self.ShowChannel[0],
			self.ShowChannel[1],
			self.ShowChannel[2],
			self.ShowChannel[3],
			self.ShowChannel[4],
			self.ShowChannel[5],
		)

		# self.Slotname = (
		# 	self.nameChannel[0],
		# 	self.nameChannel[1],
		# 	self.nameChannel[2],
		# 	self.nameChannel[3],
		# )

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
		self.SlotShow[0].Show()
		self.Slot1_1[0].SetPackedFontColor(dates.COLOR_HOVER)
		self.Slot1_1[1].SetPackedFontColor(dates.COLOR_NORMAL)
		self.Slot1_1[2].SetPackedFontColor(dates.COLOR_NORMAL)
		self.Slot1_1[3].SetPackedFontColor(dates.COLOR_NORMAL)
		self.Slot1_1[4].SetPackedFontColor(dates.COLOR_NORMAL)
		self.Slot1_1[5].SetPackedFontColor(dates.COLOR_NORMAL)
		self.Slot1[1].SetEvent((lambda : self.OpenEvents(1,2)))
		self.Slot1[2].SetEvent((lambda : self.OpenEvents(2,3)))
		self.Slot1[3].SetEvent((lambda : self.OpenEvents(3,4)))
		self.Slot1[4].SetEvent((lambda : self.OpenEvents(4,5)))
		self.Slot1[5].SetEvent((lambda : self.OpenEvents(5,6)))

		if self.IsOnline("CH1") is True:
			# self.SlotState[0].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[0].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[0].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[0].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH2") is True:
			# self.SlotState[1].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[1].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[1].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[1].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH3") is True:
			# self.SlotState[2].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[2].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[2].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[2].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH4") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[3].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[3].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH5") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[4].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[4].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")
		if self.IsOnline("CH6") is True:
			# self.SlotState[3].SetText(self.STATE_DICT[1])
			self.SlotStateIcon[5].LoadImage(dates.PATCH_LOGIN+"/icon-online.tga")
		else:
			# self.SlotState[3].SetText(self.STATE_DICT[0])
			self.SlotStateIcon[5].LoadImage(dates.PATCH_LOGIN+"/icon-offline.tga")

	def OpenEvents(self,index,arg):
		for btn in self.Slot1:
			btn.SetUp()
			for ex in self.Slot1_1:
				ex.SetPackedFontColor(dates.COLOR_NORMAL)
			for ex1 in self.SlotShow:
				ex1.Hide()
		self.Slot1[index].Down()
		self.Slot1_1[index].SetPackedFontColor(dates.COLOR_HOVER)
		self.SlotShow[index].Show()
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
		self.ForgotButton.SetPosition(10,135)
		self.ForgotButton.SetText(uiScriptLocale.LOGIN_INTERFACE_PW_LOST)
		self.ForgotButton.SetEvent(ui.__mem_func__(self.__OnClickForgotButton))
		self.ForgotButton.Show()

	def __OnClickForgotButton(self):
		os.system("start " + dates.BTN_LINK)

	def saveAccountChenars(self):
		self.chenar = {}
		# self.keys = {}
		self.loginSaveButton = {}
		self.deleteButton = {}
		self.saveButton = {}
		self.iconSave = {}
		tab = 0
		chenars =[
		[[34,30+20,19]],
		[[105,101+20,19]],
		[[176,172+20,19]],
		[[34,30+20,50]],
		[[105,101+20,50]],
		[[176,172+20,50]]]
		for a in chenars:
			# self.iconSave[tab] = ui.ImageBox()
			# self.iconSave[tab].SetParent(self.accountSaveBoardSave)
			# self.iconSave[tab].LoadImage(dates.PATCH_LOGIN+"/select-account-empty.tga")
			# self.iconSave[tab].SetPosition(a[0][0],a[0][1])
			# self.iconSave[tab].Show()
			# self.keys[tab] = ui.TextLine()
			# self.keys[tab].SetParent(self.iconSave[tab])
			# self.keys[tab].SetPosition(13,12)
			# self.keys[tab].SetText(a[0][2])
			# self.keys[tab].SetPackedFontColor(dates.COLOR_NORMAL)
			# self.keys[tab].SetFontName(dates.SIZE_FONT)
			# self.keys[tab].Show()
			self.loginSaveButton[tab] = ui.Button()
			self.loginSaveButton[tab].SetParent(self.accountSaveBoardSave)
			self.loginSaveButton[tab].SetPosition(a[0][0],a[0][2])
			self.loginSaveButton[tab].SetUpVisual(dates.PATCH_LOGIN+"/account-empty.tga")
			self.loginSaveButton[tab].SetOverVisual(dates.PATCH_LOGIN+"/account-select-over.tga")
			self.loginSaveButton[tab].SetDownVisual(dates.PATCH_LOGIN+"/account-empty.tga")
			self.loginSaveButton[tab].Show()
			self.saveButton[tab] = ui.Button()
			self.saveButton[tab].SetParent(self.accountSaveBoardSave)
			self.saveButton[tab].SetPosition(a[0][0],a[0][2])
			self.saveButton[tab].SetUpVisual(dates.PATCH_LOGIN+"/account-empty.tga")
			self.saveButton[tab].SetOverVisual(dates.PATCH_LOGIN+"/account-select-over.tga")
			self.saveButton[tab].SetDownVisual(dates.PATCH_LOGIN+"/account-empty.tga")
			self.saveButton[tab].Show()
			self.deleteButton[tab] = ui.Button()
			self.deleteButton[tab].SetParent(self.accountSaveBoardSave)
			self.deleteButton[tab].SetPosition(a[0][1],a[0][2])
			self.deleteButton[tab].SetUpVisual(dates.PATCH_LOGIN+"/account-clear-over.tga")
			self.deleteButton[tab].SetOverVisual(dates.PATCH_LOGIN+"/account-clear-over.tga")
			self.deleteButton[tab].SetDownVisual(dates.PATCH_LOGIN+"/account-empty.tga")
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
		)

		self.slotSaveBtn = (
			self.saveButton[0],
			self.saveButton[1],
			self.saveButton[2],
			self.saveButton[3],
			self.saveButton[4],
			self.saveButton[5],
		)

		self.slotDeleteBtn = (
			self.deleteButton[0],
			self.deleteButton[1],
			self.deleteButton[2],
			self.deleteButton[3],
			self.deleteButton[4],
			self.deleteButton[5],
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
				self.accountText[index].SetText(self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.iconSave[0].LoadImage(dates.PATCH_LOGIN+"/icon-save-full.tga")
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.slotIconSave[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 1:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText(self.idEditLine.GetText())
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
				self.accountText[index].SetText(self.idEditLine.GetText())
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
				self.accountText[index].SetText(self.idEditLine.GetText())
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()
		if index == 4:
			if get_reg("%d_id" % index) == "" or get_reg("%d_id" % index) == None:
				set_reg("%d_id" % index, str(binascii.b2a_base64(self.idEditLine.GetText())))
				set_reg("%d_pwd" % index, str(binascii.b2a_base64(self.pwdEditLine.GetText())))
				self.accountText[index].SetText(self.idEditLine.GetText())
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
				self.accountText[index].SetText(self.idEditLine.GetText())
				self.accountText[index].SetPackedFontColor(dates.COLOR_HOVER)
				self.PopupNotifyMessage(uiScriptLocale.LOGIN_INTERFACE_SAVE_SUCCES, self.EmptyFunc)
				self.slotSaveBtn[index].Hide()
				self.slotDeleteBtn[index].Show()
				self.slotLoginSaveBtn[index].Show()
				self.accountBgSaveFull[index].Show()

	def pressKey(self):
		onPressKeyDict = {}
		onPressKeyDict[app.DIK_F1]	= lambda : self.autoLogin(0)
		onPressKeyDict[app.DIK_F2]	= lambda : self.autoLogin(1)
		onPressKeyDict[app.DIK_F3]	= lambda : self.autoLogin(2)
		onPressKeyDict[app.DIK_F4]	= lambda : self.autoLogin(3)
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

	def descritonOverButtons(self):
		if self.saveButton[0].IsIn() ^ self.saveButton[1].IsIn() ^ self.saveButton[2].IsIn() ^ self.saveButton[3].IsIn() ^ self.saveButton[4].IsIn() ^ self.saveButton[5].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_SAVE_BUTTON, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		elif self.deleteButton[0].IsIn() ^ self.deleteButton[1].IsIn() ^ self.deleteButton[2].IsIn() ^ self.deleteButton[3].IsIn() ^ self.deleteButton[4].IsIn() ^ self.deleteButton[5].IsIn():
			self.toolTipSaveButton.ClearToolTip()
			self.toolTipSaveButton.AutoAppendTextLine(uiScriptLocale.LOGIN_INTERFACE_DELETE_BUTTON, dates.COLOR_HOVER)
			self.toolTipSaveButton.AlignHorizonalCenter()
			self.toolTipSaveButton.ShowToolTip()
		elif self.loginSaveButton[0].IsIn() ^ self.loginSaveButton[1].IsIn() ^ self.loginSaveButton[2].IsIn() ^ self.loginSaveButton[3].IsIn() ^ self.loginSaveButton[4].IsIn() ^ self.loginSaveButton[5].IsIn():
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

