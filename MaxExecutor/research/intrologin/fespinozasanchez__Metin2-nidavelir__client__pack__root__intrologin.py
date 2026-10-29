import os
import time
import app
import net
import ui
import snd
import wndMgr
import dbg
import ime
import musicInfo
import systemSetting
import localeInfo
import constInfo
import uiScriptLocale
import serverInfo
import serverCommandParser
import ServerStateChecker
import uiCommon
import grp
import _winreg
from _weakref import proxy

REG_PATH = r"SOFTWARE\Metin2\Nidavelir"

REGISTER_LINK = "https://discord.com/invite/nidavelir2"
FORGOT_PW_LINK = "https://nidavelir2.to"

LANGUAGE = 0

def set_reg(name, value):
	try:
		_winreg.CreateKey(_winreg.HKEY_CURRENT_USER, REG_PATH)
		with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_WRITE) as registry_key:
			_winreg.SetValueEx(registry_key, name, 0, _winreg.REG_SZ, value)
		return True
	except WindowsError:
		return False

def get_reg(name):
	try:
		with _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, REG_PATH, 0, _winreg.KEY_READ) as registry_key:
			value, _ = _winreg.QueryValueEx(registry_key, name)
			return str(value)
	except WindowsError:
		return None

class LoginWindow(ui.ScriptWindow):
	def __init__(self, stream):
		ui.ScriptWindow.__init__(self)
		self.stream = stream
		self.isDown = False
		self.onPressKeyDict = {}
		self.language_list = []
		self.language_popup = None

		net.SetPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(self)

	def __del__(self):
		net.ClearPhaseWindow(net.PHASE_WINDOW_LOGIN, self)
		net.SetAccountConnectorHandler(0)
		ui.ScriptWindow.__del__(self)

	def Open(self):
		ServerStateChecker.Create(self)
		self.__BuildFailureDicts()
		self.__BuildKeyDict()
		self.SetSize(wndMgr.GetScreenWidth(), wndMgr.GetScreenHeight())
		self.SetWindowName("LoginWindow")
		self.__LoadScript("UIScript/loginwindow.py")

		self.__PlayLoginMusic()
		self.__InitIME()

		self.SetChannel(0)
		self.CheckAccount()

		self.Show()
		app.ShowCursor()

	def Close(self):
		if musicInfo.loginMusic and musicInfo.selectMusic:
			snd.FadeOutMusic("BGM/" + musicInfo.loginMusic)

		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
			
		self.language_popup = None

		self.Hide()
		app.HideCursor()
		ime.ClearExceptKey()

	def __BuildFailureDicts(self):
		self.loginFailureMsgDict = {
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
			"BADSCLID": localeInfo.LOGIN_FAILURE_WRONG_SOCIALID,
			"AGELIMIT": localeInfo.LOGIN_FAILURE_SHUTDOWN_TIME,
			"CSHIELD": localeInfo.LOGIN_FAILURE_WRONG_CSHIELD_VERSION,
			"CS_HWID": localeInfo.LOGIN_FAILURE_CSHIELD_HWID,
		}

		self.loginFailureFuncDict = {
			"CSHIELD": app.Exit,
			"WRONGPWD": localeInfo.LOGIN_FAILURE_WRONG_PASSWORD,
			"WRONGMAT": localeInfo.LOGIN_FAILURE_WRONG_MATRIX_CARD_NUMBER,
			"QUIT": app.Exit,
		}

	def __BuildKeyDict(self):
		for i in xrange(4):
			self.onPressKeyDict[getattr(app, "DIK_F%d" % (i + 1))] = lambda idx=i: self.LoadAccount(idx)

	def OnKeyDown(self, key):
		if key in self.onPressKeyDict:
			self.onPressKeyDict[key]()
		return True

	def OnConnectFailure(self):
		snd.PlaySound("sound/ui/loginfail.wav")
		self.PopupNotifyMessage(localeInfo.LOGIN_CONNECT_FAILURE)

	def OnHandShake(self):
		snd.PlaySound("sound/ui/loginok.wav")
		self.PopupDisplayMessage(localeInfo.LOGIN_CONNECT_SUCCESS)
		constInfo.ACCOUNT_NAME = str(self.idEditLine.GetText())

	def OnLoginStart(self):
		self.PopupDisplayMessage(localeInfo.LOGIN_PROCESSING)

	def OnLoginFailure(self, error):
		ServerStateChecker.Request()
		msg = self.loginFailureMsgDict.get(error, localeInfo.LOGIN_FAILURE_UNKNOWN + error)
		func = self.loginFailureFuncDict.get(error, self.EmptyFunc)
		self.PopupNotifyMessage(msg, func)
		snd.PlaySound("sound/ui/loginfail.wav")

	def __PlayLoginMusic(self):
		if musicInfo.loginMusic:
			snd.SetMusicVolume(systemSetting.GetMusicVolume())
			snd.FadeInMusic("BGM/" + musicInfo.loginMusic)
		snd.SetSoundVolume(systemSetting.GetSoundVolume())

	def __InitIME(self):
		ime.AddExceptKey(91)
		ime.AddExceptKey(93)

	def __LoadScript(self, fileName):
		import exception
		try:
			ui.PythonScriptLoader().LoadScriptFile(self, fileName)
		except:
			exception.Abort("LoginWindow.__LoadScript.LoadObject")

		try:
			self.idEditLine  = self.GetChild("id")
			self.pwdEditLine = self.GetChild("pwd")
			self.loginButton = self.GetChild("login_button")
			self.exitButton = self.GetChild("exit_button")
			
			self.registerButton = self.GetChild("register_button")
			self.forgotPWButton = self.GetChild("forgot_pw_button")
			
			self.boardChannel = self.GetChild("Board_Channel")

			self.channelButton = dict(
				(i, self.GetChild("channel_button_%d" % (i + 1)))
				for i in xrange(10)
			)

			self.accountData = dict(
				(i, [
					[self.GetChild("f%d_delete_button" % (i + 1)),
					 self.GetChild("f%d_save_button" % (i + 1)),
					 self.GetChild("f%d_login_button" % (i + 1))],
					self.GetChild("f%d_account_text" % (i + 1))
				])
				for i in xrange(6)
			)
		except:
			exception.Abort("LoginWindow.__LoadScript.BindObject")

		rectWindow = ui.Window()
		rectWindow.SetParent(self.boardChannel)
		rectWindow.SetPosition(0, 96)
		rectWindow.SetSize(239, 261)
		rectWindow.SetWindowHorizontalAlignCenter()
		rectWindow.OnMouseWheel = ui.__mem_func__(self.__OnMouseWheelCategory)
		rectWindow.Show()
		self.rectWindow = rectWindow

		scrollbarWindow = ui.Window()
		scrollbarWindow.SetParent(self.boardChannel)
		scrollbarWindow.SetPosition(self.boardChannel.GetWidth() - 14, 35 + 61)
		scrollbarWindow.SetSize(7, self.boardChannel.GetHeight() - 60 - 83+ 45)
		scrollbarWindow.Show()
		self.scrollbarWindow = scrollbarWindow

		scrollBar = ui.ScrollbarNewDyn()
		scrollBar.SetParent(self.scrollbarWindow)
		scrollBar.SetPosition(0, 0)
		scrollBar.SetSize(7, scrollbarWindow.GetHeight())
		scrollBar.SetScrollEvent(self.OnScrollDyn)
		scrollBar.SetScrollSpeed(25)
		scrollBar.SetColors(
			base=grp.GenerateColor(0.03, 0.02, 0.02, 0.92),
			border=grp.GenerateColor(0.05, 0.04, 0.04, 0.35),
			thumb=grp.GenerateColor(0.90, 0.74, 0.49, 1.00),
		)
		scrollBar.Show()
		self.scrollBar = scrollBar

		## Language
		self.__LoadLocaleListFile()
		self.langlist = ["en","ro","de","tr","pl","es", "hu", "pt", "fr", "it", "dk", "cz"]
		for lang in self.langlist:
			flag = self.GetChild("flag_%s" % lang)
			if not flag:
				continue

			visualPath = "d:/ymir work/ui/login/login_interface/country_flags/%s_02.png" % lang
			if app.GetLocaleName() == lang:
				flag.SetUpVisual(visualPath)
				flag.SetOverVisual(visualPath)
				flag.SetDownVisual(visualPath)
			else:
				flag.SAFE_SetEvent(self.__ClickLanguage, lang)

		for chID, button in self.channelButton.iteritems():
			button.SetEvent(ui.__mem_func__(self.SetChannel), chID)
			self.GetChild("ch%d_online" % int(chID+1)).Hide()
			button.SetParent(self.rectWindow)
			button.SetClippingMaskWindow(self.rectWindow)

		for key, (buttons, _) in self.accountData.iteritems():
			buttons[0].SetEvent(ui.__mem_func__(self.DeleteAccount), key)
			buttons[1].SetEvent(ui.__mem_func__(self.SaveAccount), key)
			buttons[2].SetEvent(ui.__mem_func__(self.LoadAccount), key)

		self.idEditLine.SetReturnEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.idEditLine.SetTabEvent(ui.__mem_func__(self.pwdEditLine.SetFocus))
		self.pwdEditLine.SetReturnEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.pwdEditLine.SetTabEvent(ui.__mem_func__(self.idEditLine.SetFocus))
		self.idEditLine.SetFocus()

		self.loginButton.SetEvent(ui.__mem_func__(self.__OnClickLoginButton))
		self.exitButton.SetEvent(ui.__mem_func__(self.ExitWindow))

		self.registerButton.SetEvent(ui.__mem_func__(self.OpenLink), REGISTER_LINK)
		self.forgotPWButton.SetEvent(ui.__mem_func__(self.OpenLink), FORGOT_PW_LINK)

		self.__InitChannelScroll()
		
		self.__RefreshServerStateList()
		ServerStateChecker.Request()

	def __InitChannelScroll(self):
		self.channelBtns = [btn for i, btn in sorted(self.channelButton.iteritems(), key=lambda x: x[0]) if btn]

		self.scrollOffset = 0
		self.isScrolling = False
		self.itemHeight = self.channelBtns[0].GetHeight()

		self.ChangeScrollbar()

	def __OnMouseWheelCategory(self, length):
		self.scrollBar.OnMouseWheel(length)
		return True

	def OnMouseWheel(self, length):
		if not self.scrollBar or not self.scrollBar.IsShow():
			return False

		return self.UpdateScrollbar((length * 0.01) * 28)
		
	def GetTotalHeight(self):
		return len(self.channelBtns) * self.itemHeight
		
	def OnScrollDyn(self, position):
		visibleHeight = self.rectWindow.GetHeight()
		visible_items = max(1, int(round(float(visibleHeight) / float(self.itemHeight))))
		total_items = len(self.channelBtns)

		max_scroll = max(0, total_items - visible_items)
		scroll_index = int(position * max_scroll + 0.5)

		self.scrollOffset = -scroll_index * self.itemHeight

		for i, button in enumerate(self.channelBtns):
			new_y = (i - scroll_index) * self.itemHeight
			button.SetPosition(0, new_y)

		self.UpdateScrollbar()

	def UpdateScrollbar(self, val=0):
		if self.isScrolling:
			return
		self.isScrolling = True
		try:
			totalHeight = self.GetTotalHeight()
			visibleHeight = self.rectWindow.GetHeight()

			self.scrollOffset += val
			self.scrollOffset = min(0, max(self.scrollOffset, visibleHeight - totalHeight))
			self.ChangeScrollbar()
		finally:
			self.isScrolling = False

	def ChangeScrollbar(self):
		if self.isScrolling:
			return

		scrollBoardHeight = self.GetTotalHeight()
		selfHeight = self.scrollbarWindow.GetHeight()

		if scrollBoardHeight <= selfHeight:
			self.scrollBar.Hide()
		else:
			self.scrollBar.SetScale(selfHeight, scrollBoardHeight)

			new_pos = self.GetNewScrollBarPosition()
			if new_pos != 0:
				self.scrollBar.SetPos(new_pos)
			else:
				pos_scale = 0.0
				den = float(scrollBoardHeight - selfHeight)
				if den > 0.0:
					pos_scale = abs(self.scrollbarWindow.GetLocalPosition()[1]) / den
				self.scrollBar.SetPosScale(pos_scale)

			self.scrollBar.Show()

		self.ScrollContent()

	def ScrollContent(self):
		for i, button in enumerate(self.channelBtns):
			new_y = (i * self.itemHeight) + self.scrollOffset
			button.SetPosition(0, new_y)
		
	def GetNewScrollBarPosition(self):
		totalHeight = self.GetTotalHeight()
		visibleHeight = self.rectWindow.GetHeight()
		if totalHeight <= visibleHeight:
			return 0

		progress = float(abs(self.scrollOffset)) / float(totalHeight - visibleHeight)
		try:
			middle_h = self.scrollBar.middleBar.GetHeight()
		except:
			middle_h = 0

		max_middle_pos = self.scrollbarWindow.GetHeight() - middle_h - 2
		return int(progress * max_middle_pos) + 1

	def OnUpdate(self):
		ServerStateChecker.Update()

	def ChangeLanguage(self, langName):
		if not langName in self.langlist:
			return

		localeCfg = open("locale.cfg", "w+")
		localeCfg.write(str("10022 1250")+" "+langName)
		localeCfg.close()
		os.system('start Metin2Release.exe')
		app.Exit()

	def LoadAccount(self, key):
		if get_reg("id_%d" % key):
			self.idEditLine.SetText(str(get_reg("id_%d" % key)))
			self.pwdEditLine.SetText(str(get_reg("pwd_%d" % key)))
			self.pwdEditLine.SetFocus()
			self.__OnClickLoginButton()
		else:
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_N_S)

	def SaveAccount(self, key):
		if get_reg("id_%d" % key):
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_N_S_D)
			return
		
		if self.idEditLine.GetText() == "" or self.pwdEditLine.GetText() == "":
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_SAVE)
			return
		
		set_reg("id_%d" % key, self.idEditLine.GetText())
		set_reg("pwd_%d" % key, self.pwdEditLine.GetText())
		self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_SAVED)
		self.CheckAccount()

	def CheckAccount(self):
		for i in xrange(len(self.accountData)):
			reg_value = get_reg("id_%d" % i)
			if reg_value:
				prefix = "F%d - " % (i + 1)
				self.accountData[i][1].SetText(prefix + str(reg_value))
				self.accountData[i][0][1].Hide()
				self.accountData[i][0][0].Show()
			else:
				self.accountData[i][1].SetText(uiScriptLocale.LOGIN_ACCOUNT_EMPTY)
				self.accountData[i][0][1].Show()
				self.accountData[i][0][0].Hide()
			self.accountData[i][1].SetPackedFontColor(0xffe3c09e)

	def DeleteAccount(self, key):
		import uiCommon
		self.questionDialog = uiCommon.QuestionDialog()
		self.questionDialog.SetText(uiScriptLocale.LOGIN_ACCOUNT_ASK_DELETE)
		self.questionDialog.SetAcceptEvent(lambda arg=key: self.AcceptDeleteAccount(arg))
		self.questionDialog.SetCancelEvent(ui.__mem_func__(self.CancelDeleteAccount))
		self.questionDialog.Open()
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(1)

	def AcceptDeleteAccount(self, key):
		if get_reg("id_%d" % key):
			set_reg("id_%d" % key, "")
			set_reg("pwd_%d" % key, "")
			self.OnCloseQuestionDialog()
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_DELETE)
		else:
			self.PopupNotifyMessage(uiScriptLocale.LOGIN_ACCOUNT_D_S)

		self.CheckAccount()

	def CancelDeleteAccount(self):
		self.OnCloseQuestionDialog()

	def OnCloseQuestionDialog(self):
		if not self.questionDialog:
			return
		self.questionDialog.Close()
		self.questionDialog = None
		constInfo.SET_ITEM_QUESTION_DIALOG_STATUS(0)

	def SetChannel(self, ch):
		for button in self.channelButton.itervalues():
			button.SetUp()

		if ch in self.channelButton:
			self.channelButton[ch].Down()

		host = serverInfo.SRV1["host"]
		login_port = self.get_port("LOGIN")
		logo_port = self.get_port("LOGO")
		channel_port = self.get_port(ch)
		server_info = self.get_port(ch, info=True)

		self.stream.SetConnectInfo(host, channel_port, host, login_port)
		net.SetMarkServer(host, logo_port)
		app.SetGuildMarkPath("10.tga")
		app.SetGuildSymbolPath("10")
		net.SetServerInfo(server_info)

	def get_port(self, ch, info=False):
		try:
			if ch == "LOGIN":
				return serverInfo.SRV_LIST[0][0][1]
			elif ch == "LOGO":
				return serverInfo.SRV_LIST[0][0][3][0][2]
			elif isinstance(ch, int):
				if info:
					return "{}{}, CH{}".format(serverInfo.SRV_LIST[0][0][0], "", ch + 1)
				return serverInfo.SRV_LIST[0][0][3][ch][2]
		except (IndexError, KeyError, TypeError):
			dbg.TraceError("[ERROR] Invalid channel access:", ch)
			return 0 

	def Connect(self, id, pwd):
		if constInfo.SEQUENCE_PACKET_ENABLE:
			net.SetPacketSequenceMode()
			
		constInfo.LastAccount = id.lower()

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(localeInfo.LOGIN_CONNETING, self.EmptyFunc, localeInfo.UI_CANCEL)

		self.stream.SetLoginInfo(id, pwd)
		self.stream.Connect()
		
	def PopupDisplayMessage(self, msg):
		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg)

	def PopupNotifyMessage(self, msg, func=0):
		if not func:
			func = self.EmptyFunc

		self.stream.popupWindow.Close()
		self.stream.popupWindow.Open(msg, func, localeInfo.UI_OK)

	def OnPressExitKey(self):
		self.ExitWindow()
		return TRUE
		
	def ExitWindow(self):
		if self.stream.popupWindow:
			self.stream.popupWindow.Close()
		self.stream.SetPhaseWindow(0)
		return TRUE

	def __GetRegionID(self):
		return 0

	def __GetServerID(self):
		return 0

	def __GetChannelID(self):
		return self.channelList.GetSelectedItem()

	def EmptyFunc(self):
		pass

	def NotifyChannelState(self, key, state):
		serverInfo.SERVER_STATE_TABLE[key] = state
		
		serverIndex = self.__GetServerID()
		if (key / 10) == serverIndex:
			try:
				stateName = serverInfo.STATE_DICT[state]
				stateNameText = serverInfo.STATE_DICT[state]
			except:
				stateName = serverInfo.STATE_NONE
				stateNameText = serverInfo.STATE_TEXT_NONE

			channelIndex = key % 10
			channelName = serverInfo.SRV_LIST[0][serverIndex][3][channelIndex][0]

			if state >= 1:
				self.GetChild("ch%d_online" % (int(channelIndex)+1)).Show()
				self.GetChild("ch%d_offline" % (int(channelIndex)+1)).Hide()
				
	def __RequestServerStateList(self):
		serverIndex = self.__GetServerID()
		channelData = None

		try:
			channelData = serverInfo.SRV_LIST[0][serverIndex][3]
		except:
			print "LoginWindow::__RequestServerStateList"
			return

		ServerStateChecker.Request()

	def __RefreshServerStateList(self):
		serverIndex = self.__GetServerID()
		channelData = None
		try:
			channelData = serverInfo.SRV_LIST[0][0][3]
		except:
			print "LoginWindow::__RefreshServerStateList"
			return
			
		for index, channel in enumerate(channelData):
			ServerStateChecker.AddChannel(index, channel[1], channel[2])
			stateName = serverInfo.STATE_NONE

	def OpenLink(self, link):
		os.system('@echo off && explorer ' + link)
		return TRUE

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

	def __LoadLocaleListFile(self):
		try:
			with open("locale_list.txt", "rt") as file:
				lines = file.readlines()
		except:
			import dbg
			dbg.LogBox("__LoadLocaleListFile error locale_list.txt")
			app.Abort()

		lineIndex = 1
		for line in lines:
			try:
				tokens = line[:-1].split(" ")
				if len(tokens) == 3:
					name = tokens[0]
					code_page = tokens[1]
					locale = tokens[2]

					if locale in uiScriptLocale.LOCALE_NAME_DICT:
						name = uiScriptLocale.LOCALE_NAME_DICT[locale]

					self.language_list.append({"name" : name, "code_page" : code_page, "locale" : locale})
				else:
					raise RuntimeError, "Unknown TokenSize"

				lineIndex += 1
			except:
				import dbg
				dbg.LogBox("%s: line(%d): %s" % ("locale_list.txt", lineIndex, line), "Error")
				raise

	def __SaveLoca(self, code_page, locale):
		try:
			with open("loca.cfg", "wt") as file:
				file.write("{} {}".format(code_page, locale))
		except:
			import dbg
			dbg.LogBox("__SaveLoca error")
			app.Abort()

	def __ClickLanguage(self, lang):
		for item in self.language_list:
			if item["locale"] == lang:
				self.__SaveLoca(item["code_page"], item["locale"])
				app.SetReloadLocale(item["locale"] != app.GetLocaleName())

		if not self.language_popup:
			self.language_popup = uiCommon.PopupDialog()
		self.language_popup.SetText(uiScriptLocale.LANGUAGE_WILL_CHANGE)
		self.language_popup.Open()