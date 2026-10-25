import app,item,chat,chr,locale,net,player,game,event,time,ui,interfacemodule,background,os,wndMgr,serverInfo

##### Server Information ############# 
serverNum=1
serverChannel=2
addr_new = serverInfo.REGION_DICT[0][serverNum]['channel'][serverChannel]['ip'] 
port_new = serverInfo.REGION_DICT[0][serverNum]['channel'][serverChannel]['tcp_port'] 
account_addr_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['ip'] 
account_port_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['port'] 
###################################### 
addr=addr_new 
port=port_new 
id='acc' 
pwd='pass' 
account_addr=account_addr_new 
account_port=account_port_new 
slot=0
autoLogin=0
autoSelect=0
######################################
LoadButton = ui.Button()
StateLoadMainButton = 0

PlayerVIDShop = 0
PlayerVIDBuff = 0
StateAutoTP = 0
StateAutoMP = 0
StateBuffBot = 0
StateHorseBot = 0
StateShopBot = 0
StateNoMove = 0
StateCombo = 0
StateZoomHack = 0
StateNoFog = 0
StateDayNight = 0
StateAutoAttack = 0
StateRestartHere = 0
StateAttackSpeed = 0
StateMoveSpeed = 0
StateMobPuller = 0
StateQuestWinTresi = 0
StateItemUseSettings = 0
StateItemUse = [0 for x in xrange(12)]
StateSkill = [0 for x in xrange(6)]

class Multi(ui.ThinBoard):
	Gui = []
	
	def __init__(self):
		self.Gui = []
		"""
		self.ButtonList = []
		"""
		#############################
		#self.ReloggerState = []	#
		#############################
		
		ui.ThinBoard.__init__(self)
		self.StartMulti()
		
		#############################################################
		#self.GetReloggerState()									#
		#if self.ReloggerState[0] == "on":							#
		#	self.delayAutoLogin = WaitingDialog()					#
		#	self.delayAutoLogin.Open(int(5))						#
		#	self.delayAutoLogin.SAFE_SetTimeOverEvent(self.Relogger)#
		#############################################################
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ThinBoard.__del__(self)
	
	def Show(self):
		ui.ThinBoard.Show(self)
	
	def Close(self):
		self.Hide()
		return TRUE
		
	def OnPressEscapeKey(self):
		self.Close()
		return TRUE
		
	def StartMulti(self):
		self.CreateBoard()
		self.LoadMain()
	
	def LoadMain(self):
		global LoadButton
		
		LoadButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		LoadButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		LoadButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		LoadButton.SetText("Show")
		LoadButton.SetPosition(10, 50)
		LoadButton.SetEvent(self.LoadMainButton)
		LoadButton.Show()
		
	def LoadMainButton(self):
		global StateLoadMainButton
	
		if StateLoadMainButton == 0:
			StateLoadMainButton = 1
			self.Gui[0].Show()
			LoadButton.SetText("Hide")
		else:
			StateLoadMainButton = 0
			self.Gui[0].Hide()
			LoadButton.SetText("Show")
	
	def GetReloggerState(self):
		try:													
			r = open("Relogger-Settings.txt", "rb")
			for line in r:
				if "=" in line:
					self.ReloggerState.append(line.split('=')[1])
			r.close()
		except IOError:
			self.ReloggerState[0] = "off"
			w = open("Relogger-Settings.txt", "wb")
			w.write("State=%s\n"%("off"))
			w.close()
	
	def LoginInfo(self):
		serverNum = 1
		serverChannel = 2
		ChannelIP = serverInfo.REGION_DICT[0][serverNum]['channel'][serverChannel]['ip'] 
		ChannelPort = serverInfo.REGION_DICT[0][serverNum]['channel'][serverChannel]['tcp_port'] 
		AuthServerIP = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['ip'] 
		AuthServerPort = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['port']
		Acc = "Account"
		Pw = "Password"
		return ChannelIP, ChannelPort, AuthServerIP, AuthServerPort, Acc, Pw
	
	def addButton(self, parent, name, x, y, size, event):
		Gui = [
			[[ui.Button, parent], [0, 0], [x, y], [['SetUpVisual', ["d:/ymir work/ui/public/"+size+"_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/"+size+"_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/"+size+"_button_03.sub"]], ['SetText', [name]], ['SetEvent', [event]]], [], ["on"]],
			]
		self.GuiParser(Gui, self.Gui)
	"""
	def addButton(self, name, parent, x, y, Size, event):
		btn = ui.Button()
		btn.SetParent(parent)
		btn.SetUpVisual('d:/ymir work/ui/public/'+Size+'_button_01.sub')
		btn.SetOverVisual('d:/ymir work/ui/public/'+Size+'_button_02.sub')
		btn.SetDownVisual('d:/ymir work/ui/public/'+Size+'_button_03.sub')
		if event:
			btn.SetEvent(event)
		btn.SetText(name)
		btn.SetPosition(x, y)
		btn.Show()
		self.ButtonList.append(btn)
	"""
	def GuiParser(self, guiobjects, list):
	#[Type, Parentindex],[Sizex, Sizey], [Posx, Posy], [commands], [flags]
		for object in guiobjects:
			Object = object[0][0]()
			if object[0][1] != "":
				Object.SetParent(list[object[0][1]])
			if object[1][0] + object[1][1] != 0:
				Object.SetSize(object[1][0], object[1][1])
			if object[2][0] + object[2][1] != 0:
				Object.SetPosition(object[2][0], object[2][1])
					
			for command in object[3]:
				cmd = command[0]	
				attr = getattr(Object,cmd)			
				if callable(attr):
					argument = command[1]
					lenght = len(argument)
					if lenght == 1:
						if argument[0] == "":
							attr()
						else:
							attr(argument[0])
					elif lenght == 2:
						attr(argument[0], argument[1])
					elif lenght == 3:
						attr(argument[0], argument[1], argument[2])
					elif lenght == 4:
						attr(argument[0], argument[1], argument[2], argument[3])
			for flag in object[4]:
				Object.AddFlag(str(flag))
			if "on" in object[5]:
				Object.Show()
		
			list.append(Object)
	
	def CreateBoard(self):
		Gui = [
			[[ui.ThinBoard, ""], [100, 260], [5,70], [["Hide", [""]]], ["float"], []], # Main
			[[ui.ThinBoard, ""], [195, 190], [105,70], [["Hide", [""]]], ["float"], []], # Item-Use
			[[ui.ThinBoard, ""], [200, 100], [105,70], [["Hide", [""]]], ["float"], []], # Buff-Bot
			[[ui.ThinBoard, ""], [100, 200], [105,70], [["Hide", [""]]], ["float"], []], # Bonus
			[[ui.TextLine, 0], [0, 0], [25, 10], [["SetDefaultFontName", [""]], ["SetText", ["No-THX =)"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], ["on"]],
			[[ui.TextLine, 1], [0, 0], [25, 10], [["SetDefaultFontName", [""]], ["SetText", ["ITEM-USER"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], ["on"]],
			[[ui.TextLine, 1], [0, 0], [5, 110], [["SetDefaultFontName", [""]], ["SetText", ["//////////////////////////////////////////////"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], ["on"]],
			[[ui.TextLine, 1], [0, 0], [5, 163], [["SetDefaultFontName", [""]], ["SetText", ["Item:"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], []],
			[[ui.TextLine, 1], [0, 0], [30, 163], [["SetDefaultFontName", [""]], ["SetText", ["None"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], []],
			[[ui.TextLine, 1], [0, 0], [70, 163], [["SetDefaultFontName", [""]], ["SetText", ["Time:"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], []],
			[[ui.TextLine, 2], [0, 0], [25, 10], [["SetDefaultFontName", [""]], ["SetText", ["BUFF-BOT"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], ["on"]],
			[[ui.TextLine, 2], [0, 0], [100, 30], [["SetDefaultFontName", [""]], ["SetText", ["Char:"]], ["SetFontColor", [1.0, 0.5, 1.0]]], [], ["on"]],
			[[ui.SlotBar, 0], [25, 15], [70, 33], [], [], ["on"]], # TP
			[[ui.SlotBar, 0], [25, 15], [70, 53], [], [], ["on"]], # MP
			[[ui.SlotBar, 0], [25, 15], [70, 73], [], [], ["on"]], # Attackspeed
			[[ui.SlotBar, 0], [25, 15], [70, 93], [], [], ["on"]], # Movespeed
			[[ui.SlotBar, 0], [25, 15], [70, 113], [], [], ["on"]], # Mob-Puller
			[[ui.SlotBar, 1], [25, 15], [98, 163], [], [], []], # Item-Use-Time
			[[ui.EditLine, 12], [25, 15], [8, 2], [["SetMax", [2]], ["SetText", ["90"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], ["on"]],
			[[ui.EditLine, 13], [25, 15], [8, 2], [["SetMax", [2]], ["SetText", ["30"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], ["on"]],
			[[ui.EditLine, 14], [25, 15], [8, 2], [["SetMax", [3]], ["SetText", ["200"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], ["on"]],
			[[ui.EditLine, 15], [25, 15], [8, 2], [["SetMax", [3]], ["SetText", ["200"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], ["on"]],
			[[ui.EditLine, 16], [25, 15], [8, 2], [["SetMax", [3]], ["SetText", ["10"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], ["on"]],
			[[ui.EditLine, 17], [25, 15], [8, 2], [["SetMax", [2]], ["SetText", ["5"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], [], []],
			]
		self.GuiParser(Gui, self.Gui)
		"""
		self.addButton("Test", self.Board, 7, 30, 'middle', lambda : self.TestFunktion())
		"""
		################################ Buttons Main # Gui[24]
		self.addButton(0, "TP", 7, 30, "middle", ui.__mem_func__(self.EnableAutoTP))
		self.addButton(0, "MP", 7, 50, "middle", ui.__mem_func__(self.EnableAutoMP))
		self.addButton(0, "AttackSpeed", 7, 70, "middle", ui.__mem_func__(self.EnableAttackSpeed))
		self.addButton(0, "MoveSpeed", 7, 90, "middle", ui.__mem_func__(self.EnableMoveSpeed))
		self.addButton(0, "MobPuller", 7, 110, "middle", ui.__mem_func__(self.EnableMobPuller))
		self.addButton(0, "Buff", 7, 130, "middle", ui.__mem_func__(self.BuffStart))
		self.addButton(0, ".", 78, 133, "close", ui.__mem_func__(self.OpenBuffSettings))
		self.addButton(0, "ItemUser", 7, 150, "middle", ui.__mem_func__(self.EnableHorseBot))
		self.addButton(0, ".", 78, 153, "close", ui.__mem_func__(self.OpenItemUseSettings))
		self.addButton(0, "AutoAttack", 7, 170, "large", ui.__mem_func__(self.EnableAutoAttack))
		self.addButton(0, "Restart", 7, 190, "large", ui.__mem_func__(self.EnableRestartHere))
		self.addButton(0, "Ghost", 7, 210, "large", self.GhostModus)
		self.addButton(0, "Bonus", 7, 230, "large", ui.__mem_func__(self.Gui[3].Show))
		################################ Buttons Item-Use # Gui[37]
		self.addButton(1, ".", 180, 0, "close", ui.__mem_func__(self.CloseItemUseSettings))
		self.addButton(1, "Settings", 67, 130, "middle", ui.__mem_func__(self.ItemUseSettings))
		self.addButton(1, "Save", 127, 160, "middle", ui.__mem_func__(self.SaveItemList)), self.Gui[39].Hide()
		self.addButton(1, "None", 7, 30, "middle", ui.__mem_func__(self.EnableItemUse1))
		self.addButton(1, "None", 7, 50, "middle", ui.__mem_func__(self.EnableItemUse2))
		self.addButton(1, "None", 7, 70, "middle", ui.__mem_func__(self.EnableItemUse3))
		self.addButton(1, "None", 7, 90, "middle", ui.__mem_func__(self.EnableItemUse4))
		self.addButton(1, "None", 67, 30, "middle", ui.__mem_func__(self.EnableItemUse5))
		self.addButton(1, "None", 67, 50, "middle", ui.__mem_func__(self.EnableItemUse6))
		self.addButton(1, "None", 67, 70, "middle", ui.__mem_func__(self.EnableItemUse7))
		self.addButton(1, "None", 67, 90, "middle", ui.__mem_func__(self.EnableItemUse8))
		self.addButton(1, "None", 127, 30, "middle", ui.__mem_func__(self.EnableItemUse9))
		self.addButton(1, "None", 127, 50, "middle", ui.__mem_func__(self.EnableItemUse10))
		self.addButton(1, "None", 127, 70, "middle", ui.__mem_func__(self.EnableItemUse11))
		self.addButton(1, "None", 127, 90, "middle", ui.__mem_func__(self.EnableItemUse12))
		################################ Buttons Buff-Bot # Gui[52]
		self.addButton(2, ".", 185, 0, "close", ui.__mem_func__(self.CloseBuffSettings))
		self.addButton(2, "Use-Horse", 110, 50, "middle", ui.__mem_func__(self.EnableHorseBot))
		self.addButton(2, "No-Move", 110, 70, "middle", ui.__mem_func__(self.EnableNoMove))
		self.addButton(2, "1", 7, 30, "small", ui.__mem_func__(self.EnableBuffSkill1))
		self.addButton(2, "2", 7, 50, "small", ui.__mem_func__(self.EnableBuffSkill2))
		self.addButton(2, "3", 7, 70, "small", ui.__mem_func__(self.EnableBuffSkill3))
		self.addButton(2, "4", 50, 30, "small", ui.__mem_func__(self.EnableBuffSkill4))
		self.addButton(2, "5", 50, 50, "small", ui.__mem_func__(self.EnableBuffSkill5))
		self.addButton(2, "6", 50, 70, "small", ui.__mem_func__(self.EnableBuffSkill6))
		################################ Buttons Bonus # Gui[62]
		self.addButton(3, ".", 75, 15, "close", ui.__mem_func__(self.Gui[3].Hide))
		self.addButton(3, "Select Shop", 7, 30, "large", ui.__mem_func__(self.EnableShopBot))
		self.addButton(3, "Horse", 7, 50, "large", ui.__mem_func__(self.EnableHorseBot))
		self.addButton(3, "Combo", 7, 70, "large", self.Combo)
		self.addButton(3, "Zoom", 7, 90, "large", self.ZoomHack)
		self.addButton(3, "NoFog", 7, 110, "large", self.NoFog)
		self.addButton(3, "Day/Night", 7, 130, "large", self.DayNight)
		self.addButton(3, "Lavanda2", 7, 150, "large", self.EnableQuestWinTresi)
		################################ Relogger Settings # Gui[69] ####
		#self.Gui[0].SetSize(100, 290)									#
		#self.addButton(0, "Relogger", 7, 260, "large", self.Relogger)	#
		################################# MultiHack Funktions Main ######
	def Relogger(self):
		global GetReloggerState
		ChannelIP, ChannelPort, AuthServerIP, AuthServerPort, AccountID, Password = self.LoginInfo()
		
		if self.ReloggerState[0] == "on":
			self.ReloggerState[0] = "Ingame"
			self.Gui[68].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			net.SetLoginInfo(AccountID, Password)
			net.ConnectToAccountServer(ChannelIP, ChannelPort, AuthServerIP, AuthServerPort)
			net.DirectEnter(0)
		elif self.ReloggerState[0] == "Ingame":
			self.ReloggerState[0] = "off"
			self.Gui[68].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			w = open("Relogger-Settings.txt", "wb")
			w.write("State=%s"%("off"))
			w.close()
		elif self.ReloggerState[0] == "off":
			self.ReloggerState[0] = "on"
			self.Gui[68].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			w = open("Relogger-Settings.txt", "wb")
			w.write("State=%s"%("on"))
			w.close()
			self.Relogger()
		r.close()
		# net.SendSelectCharacterPacket(0)
		#net.SendEnterGamePacket()
			
	def ReadItemList(self):
		try:
			r = open("Bot-Settings.txt", "rb")
		except IOError:
			w = open("Bot-Settings.txt", "wb")
			for i in range(0,12):
				w.write("Name=%s\n"%("None"))
				w.write("ID=%i\n"%(0))
				w.write("Time=%i\n\n"%(5))
			w.close()
			
		GetItemData = []
	
		for line in r: 
			if "=" in line:
				GetItemData.append(line.split('=')[1])
		r.close()
		
		return GetItemData
	
	def EditItemList(self):
		global StateItemUse
		EditItemData = self.ReadItemList()
		
		for i in range(0,36,3):
			if StateItemUse[i/3] == 3:
				EditItemData[i] = self.Gui[8].GetText()+"\n"
				EditItemData[i+1] = player.GetItemIndex(0)
				EditItemData[i+2] = self.Gui[23].GetText()
				break
		
		return EditItemData
	
	def WriteItemList(self):
		SetItemData = self.EditItemList()
		w = open("Bot-Settings.txt", "wb")
		
		for i in xrange(0,36,3):
			w.write("Name=%s"%(str(SetItemData[i])))
			w.write("ID=%i\n"%(int(SetItemData[i+1])))
			w.write("Time=%i\n\n"%(int(SetItemData[i+2])))
		w.close()
	
	def EnableAutoTP(self):
		global StateAutoTP
		
		if StateAutoTP == 0:
			StateAutoTP = 1
			self.Gui[24].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.AutoTP()
		else:	
			StateAutoTP = 0
			self.Gui[24].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableAutoTP()
			
	def AutoTP(self):
		MaxTP = player.GetStatus(player.MAX_HP)
		ActualTP = player.GetStatus(player.HP)
		RedPercentValue = self.Gui[18].GetText()
		
		if (float(ActualTP) / (float(MaxTP)) * 100) < int(RedPercentValue):
			for i in xrange(90):
				RedPott = player.GetItemIndex(i)
				if RedPott == 27001 or RedPott == 27002 or RedPott == 27003:
					net.SendItemUsePacket(i)
					break
					
		self.delayAutoTP = WaitingDialog()
		self.delayAutoTP.Open(int(0.5))
		self.delayAutoTP.SAFE_SetTimeOverEvent(self.AutoTP)
			
	def DisableAutoTP(self):
		self.delayAutoTP.Close()
		
	def EnableAutoMP(self):
		global StateAutoMP
		
		if StateAutoMP == 0:
			StateAutoMP = 1
			self.Gui[25].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.AutoMP()
		else:	
			StateAutoMP = 0
			self.Gui[25].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableAutoMP()
			
	def AutoMP(self):
		MaxSP = player.GetStatus(player.MAX_SP)
		ActualSP = player.GetStatus(player.SP)
		BluePercentValue = self.Gui[19].GetText()
		
		if (float(ActualSP) / (float(MaxSP)) * 100) < int(BluePercentValue):
			for i in xrange(player.INVENTORY_PAGE_SIZE*3):
				BluePott = player.GetItemIndex(i)
				if BluePott == 27004 or BluePott == 27005 or BluePott == 27006:
					net.SendItemUsePacket(i)
					break
					
		self.delayAutoMP = WaitingDialog()
		self.delayAutoMP.Open(int(1.0))
		self.delayAutoMP.SAFE_SetTimeOverEvent(self.AutoMP)
			
	def DisableAutoMP(self):
		self.delayAutoMP.Close()
		
	def EnableAttackSpeed(self):
		global StateAttackSpeed
		if StateAttackSpeed == 0:
			StateAttackSpeed = 1
			self.Gui[26].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.AttackSpeed()
		else:	
			StateAttackSpeed = 0
			self.Gui[26].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableAttackSpeed()
			
	def AttackSpeed(self):
		AttackSpeed = self.Gui[20].GetText()
		chr.SetAttackSpeed(int(AttackSpeed))
		self.delayAttackSpeed = WaitingDialog()
		self.delayAttackSpeed.Open(int(1.0))
		self.delayAttackSpeed.SAFE_SetTimeOverEvent(self.AttackSpeed)		
	
	def DisableAttackSpeed(self):
		AttackSpeedNormal = player.GetStatus(player.ATT_SPEED)
		
		chr.SetAttackSpeed(int(AttackSpeedNormal))
		self.delayAttackSpeed.Close()
		
	def EnableMoveSpeed(self):
		global StateMoveSpeed
		if StateMoveSpeed == 0:
			StateMoveSpeed = 1
			self.Gui[27].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.MoveSpeed()
		else:	
			StateMoveSpeed = 0
			self.Gui[27].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableMoveSpeed()
			
	def MoveSpeed(self):
		MoveSpeed = self.Gui[21].GetText()
		chr.SetMoveSpeed(int(MoveSpeed))
		self.delayMoveSpeed = WaitingDialog()
		self.delayMoveSpeed.Open(int(1.0))
		self.delayMoveSpeed.SAFE_SetTimeOverEvent(self.MoveSpeed)		
	
	def DisableMoveSpeed(self):
		MoveSpeedNormal = player.GetStatus(player.MOVING_SPEED)
		
		chr.SetMoveSpeed(int(MoveSpeedNormal))
		self.delayMoveSpeed.Close()
	
	def EnableMobPuller(self):
		global StateMobPuller
		
		if StateMobPuller == 0:
			StateMobPuller = 1
			self.Gui[28].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.MobPuller()
		else:	
			StateMobPuller = 0
			self.Gui[28].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableMobPuller()
	
	def MobPuller(self):
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == 70038:
				net.SendItemUsePacket(i)
				break
				
		self.delayMobPuller = WaitingDialog()
		self.delayMobPuller.Open(int(self.Gui[22].GetText()))
		self.delayMobPuller.SAFE_SetTimeOverEvent(self.MobPuller)
	
	def DisableMobPuller(self):
		self.delayMobPuller.Close()
	
	def EnableAutoAttack(self):
		global StateAutoAttack 
		
		if StateAutoAttack == 0:
			StateAutoAttack = 1
			self.Gui[33].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.AutoAttack()
		else:	
			StateAutoAttack = 0
			self.Gui[33].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.DisableAutoAttack()
	
	def AutoAttack(self):
		player.SetAttackKeyState(TRUE)
		Direction = app.GetRandom(0,7)
		chr.SetDirection(Direction)		
		self.delayAutoAttack = WaitingDialog()
		self.delayAutoAttack.Open(int(2.0))
		self.delayAutoAttack.SAFE_SetTimeOverEvent(self.AutoAttack)
	
	def DisableAutoAttack(self):
		player.SetAttackKeyState(FALSE)
		self.delayAutoAttack.Close()	
	
	def EnableRestartHere(self):
		global StateRestartHere
		
		if StateRestartHere == 0:
			StateRestartHere = 1
			self.Gui[34].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.RestartHere()
		else:	
			StateRestartHere = 0
			self.Gui[34].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.DisableRestartHere()
	
	def RestartHere(self):
		global StateAutoAttack
		
		if player.GetStatus(player.HP) <= 0:
			if StateAutoAttack == 1:
				selfDisableAutoAttack()
				self.delayPauseMob = WaitingDialog()
				self.delayPauseMob.Open(20)
				self.delayPauseMob.SAFE_SetTimeOverEvent(self.AutoAttack)
		self.delayRestartHere = WaitingDialog()
		self.delayRestartHere.Open(int(3.0))
		net.SendChatPacket("/restart_here")
		self.delayRestartHere.SAFE_SetTimeOverEvent(self.RestartHere)
	
	def DisableRestartHere(self):
		self.delayRestartHere.Close()
		
	def GhostModus(self):
		if player.GetStatus(player.HP) <= 0:
			chr.Revive()
			chat.AppendChat(chat.CHAT_TYPE_INFO, "GhostModus aktiviert")
	################################# Bonus #################################
	def EnableShopBot(self):
		global StateShopBot
		
		if StateShopBot == 0:
			StateShopBot = 1
			self.Gui[62].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.ShopBot()
			
		else:	
			StateShopBot = 0
			self.Gui[62].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.DisableShopBot()
			
	def ShopBot(self):
		global PlayerVIDShop
		
		net.SendOnClickPacket(PlayerVIDShop)
		self.delayShopBot = WaitingDialog()
		self.delayShopBot.Open(int(1.0))
		self.delayShopBot.SAFE_SetTimeOverEvent(self.ShopBot)
			
	def DisableShopBot(self):
		self.delayShopBot.Close()
			
	def EnableHorseBot(self):
		global StateHorseBot
		
		if StateHorseBot == 0:
			StateHorseBot = 1
			self.Gui[63].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.HorseBot()
		else:
			StateHorseBot = 0	
			self.Gui[63].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.DisableHorseBot()
		
	def HorseBot(self):
		net.SendChatPacket("/user_horse_ride")
		self.delayHorseBot = WaitingDialog()
		self.delayHorseBot.Open(int(2.0))
		net.SendChatPacket("/user_horse_ride")
		self.delayHorseBot.Open(int(10.0))
		self.delayHorseBot.SAFE_SetTimeOverEvent(self.HorseBot)
			
	def DisableHorseBot(self):
		self.delayHorseBot.Close()
		
	def EnableNoMove(self):
		global StateNoMove
		
		if StateNoMove == 0:
			StateNoMove = 1
			self.Gui[54].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.NoMove()
		else:	
			StateNoMove = 0
			self.Gui[54].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableNoMove()
			
	def NoMove(self):
		chr.SetMoveSpeed(0)
		self.delayNoMove = WaitingDialog()
		self.delayNoMove.Open(int(1.0))
		self.delayNoMove.SAFE_SetTimeOverEvent(self.NoMove)
		
	def DisableNoMove(self):
		MoveSpeedNormal = player.GetStatus(player.MOVING_SPEED)
		
		chr.SetMoveSpeed(int(MoveSpeedNormal))
		self.delayNoMove.Close()			
	
	def Combo(self):
		global StateCombo 
		if StateCombo == 0:
			StateCombo = 1
			self.Gui[64].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			chr.testSetComboType(2)
		else:
			StateCombo = 0
			self.Gui[64].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			chr.testSetComboType(0)

	def ZoomHack(self):
		global StateZoomHack
		if StateZoomHack == 0:
			StateZoomHack = 1
			self.Gui[65].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			app.SetCameraMaxDistance(12000)	
		else:	
			StateZoomHack = 0
			self.Gui[65].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			app.SetCameraMaxDistance(2500)	
	
	def NoFog(self):
		global StateNoFog
		if StateNoFog == 0:
			StateNoFog = 1
			self.Gui[66].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			app.SetMinFog(70000)
		else:	
			StateNoFog = 0
			self.Gui[66].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			app.SetMinFog(2500)

	def DayNight(self):
		global StateDayNight
		if StateDayNight == 0:
			StateDayNight = 1
			self.Gui[67].SetText("Night")
			background.SetEnvironmentData(1)
			background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)
		else:	
			StateDayNight = 0
			self.Gui[67].SetText("Day")
			background.SetEnvironmentData(0)
			
	def EnableQuestWinTresi(self):
		global StateQuestWinTresi
		
		if StateQuestWinTresi == 0:
			StateQuestWinTresi = 1
			self.Gui[68].SetUpVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.HookQuestWindow()
			self.QuestWinTresi()
		else:	
			StateQuestWinTresi = 0
			self.Gui[68].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.UnHookQuestWindow()
			self.DisableQuestWinTresi()
			
	def QuestWinTresi(self):
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == 80008:
				net.SendItemUsePacket(i)
				break
		event.SelectAnswer(1, 0)
		self.delayQuestWinTresi = WaitingDialog()
		self.delayQuestWinTresi.Open(int(30.0))
		self.delayQuestWinTresi.SAFE_SetTimeOverEvent(self.QuestWinTresi)
		
	def DisableQuestWinTresi(self):
		self.UnHookQuestWindow()
		self.delayQuestWinTresi.Close()
	
	def HookedQuestWindow(self, skin, idx):
		pass
	def HookQuestWindow(self):
		self.OldRecv = game.GameWindow.OpenQuestWindow
		game.GameWindow.OpenQuestWindow = self.HookedQuestWindow
		chat.AppendChat(1, "Hooking Quest-Window!")
	def UnHookQuestWindow(self):
		game.GameWindow.OpenQuestWindow = self.OldRecv
		chat.AppendChat(1, "Un-Hooking Quest-Window!")
	
	################################ Buff-Skill ################################
	def OpenBuffSettings(self):
		self.Gui[2].Show()
		self.SelectBuffChar()
		
	def CloseBuffSettings(self):
		self.Gui[2].Hide()
		self.delaySelectBuffChar.Close()
	
	def SelectBuffChar(self):
		global PlayerVIDBuff
		global StateBuffBot
		
		if StateBuffBot == 0:
			PlayerVIDBuff = player.GetTargetVID()
			CharName = chr.GetNameByVID(PlayerVIDBuff)
			self.Gui[11].SetText("Char: " + CharName)
		self.delaySelectBuffChar = WaitingDialog()
		self.delaySelectBuffChar.Open(int(1.0))
		self.delaySelectBuffChar.SAFE_SetTimeOverEvent(self.SelectBuffChar)
	
	def BuffStart(self):
		global StateBuffBot
		
		if StateBuffBot == 0:
			StateBuffBot = 1
			self.Gui[29].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.EnableFollowChar()
		else:
			StateBuffBot = 0	
			self.Gui[29].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableFollowChar()
	
	def EnableFollowChar(self):
		global PlayerVIDBuff
		
		x,y = chr.GetPixelPosition(int(PlayerVIDBuff))[:2]
		Distance = player.GetCharacterDistance(int(PlayerVIDBuff))
		if Distance >= 1000:
			charvid = player.GetMainCharacterIndex()
			chr.MoveToDestPosition(charvid,int(x),int(y))
		self.delayFollowChar = WaitingDialog()
		self.delayFollowChar.Open(int(1.0))
		self.delayFollowChar.SAFE_SetTimeOverEvent(self.EnableFollowChar)
	
	def DisableFollowChar(self):
		self.delayFollowChar.Close()
	
	def EnableBuffSkill1(self):
		global StateSkill
		
		if StateSkill[0] == 0:
			StateSkill[0] = 1
			self.Gui[55].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill1()
		else:
			StateSkill[0] = 0
			self.Gui[55].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill1()
	
	def BuffSkill1(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(1)
			
		self.delayBuffSkill1 = WaitingDialog()
		self.delayBuffSkill1.Open(int(4.0))
		self.delayBuffSkill1.SAFE_SetTimeOverEvent(self.BuffSkill1)
	
	def DisableBuffSkill1(self):
		self.delayBuffSkill1.Close()
	
	def EnableBuffSkill2(self):
		global StateSkill
		
		if StateSkill[1] == 0:
			StateSkill[1] = 1
			self.Gui[56].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill2()
		else:
			StateSkill[1] = 0
			self.Gui[56].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill2()
	
	def BuffSkill2(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(2)
			
		self.delayBuffSkill2 = WaitingDialog()
		self.delayBuffSkill2.Open(int(4.0))
		self.delayBuffSkill2.SAFE_SetTimeOverEvent(self.BuffSkill2)
	
	def DisableBuffSkill2(self):
		self.delayBuffSkill2.Close()
	
	def EnableBuffSkill3(self):
		global StateSkill
		
		if StateSkill[2] == 0:
			StateSkill[2] = 1
			self.Gui[57].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill3()
		else:
			StateSkill[2] = 0
			self.Gui[57].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill3()
	
	def BuffSkill3(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(3)
			
		self.delayBuffSkill3 = WaitingDialog()
		self.delayBuffSkill3.Open(int(4.0))
		self.delayBuffSkill3.SAFE_SetTimeOverEvent(self.BuffSkill3)
	
	def DisableBuffSkill3(self):
		self.delayBuffSkill3.Close()
	
	def EnableBuffSkill4(self):
		global StateSkill
		
		if StateSkill[3] == 0:
			StateSkill[3] = 1
			self.Gui[58].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill4()
		else:
			StateSkill[3] = 0
			self.Gui[58].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill4()
	
	def BuffSkill4(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(4)
			
		self.delayBuffSkill4 = WaitingDialog()
		self.delayBuffSkill4.Open(int(4.0))
		self.delayBuffSkill4.SAFE_SetTimeOverEvent(self.BuffSkill4)
	
	def DisableBuffSkill4(self):
		self.delayBuffSkill4.Close()
	
	def EnableBuffSkill5(self):
		global StateSkill
		
		if StateSkill[4] == 0:
			StateSkill[4] = 1
			self.Gui[59].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill5()
		else:
			StateSkill[4] = 0
			self.Gui[59].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill5()
	
	def BuffSkill5(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(5)
			
		self.delayBuffSkill5 = WaitingDialog()
		self.delayBuffSkill5.Open(int(4.0))
		self.delayBuffSkill5.SAFE_SetTimeOverEvent(self.BuffSkill5)
	
	def DisableBuffSkill5(self):
		self.delayBuffSkill5.Close()
	
	def EnableBuffSkill6(self):
		global StateSkill
		
		if StateSkill[5] == 0:
			StateSkill[5] = 1
			self.Gui[60].SetUpVisual("d:/ymir work/ui/public/small_button_02.sub")
			self.BuffSkill6()
		else:
			StateSkill[5] = 0
			self.Gui[60].SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			self.DisableBuffSkill6()	
			
	def BuffSkill6(self):
		global StateBuffBot
		global PlayerVIDBuff
		
		if StateBuffBot == 1:
			player.SetTarget(PlayerVIDBuff)
			player.ClickSkillSlot(6)
			
		self.delayBuffSkill6 = WaitingDialog()
		self.delayBuffSkill6.Open(int(4.0))
		self.delayBuffSkill6.SAFE_SetTimeOverEvent(self.BuffSkill6)
	
	def DisableBuffSkill6(self):
		self.delayBuffSkill6.Close()
	################################ Item-Use ################################
	def OpenItemUseSettings(self):
		self.Gui[1].Show()
		self.ShowItemID()
	
	def CloseItemUseSettings(self):
		self.Gui[1].Hide()
		self.delayShowItemID.Close()
	
	def ShowItemID(self):
		ButtonName = self.ReadItemList()
		tmp = 0
		for i in xrange(40,52):	
			self.Gui[i].SetText(str(ButtonName[tmp]))
			tmp+=3
		item.SelectItem(player.GetItemIndex(0))
		item.GetItemName(player.GetItemIndex(0))
		self.Gui[8].SetText(str(item.GetItemName()))
		self.delayShowItemID = WaitingDialog()
		self.delayShowItemID.Open(int(1.0))
		self.delayShowItemID.SAFE_SetTimeOverEvent(self.ShowItemID)
	
	def ItemUseSettings(self):
		global StateItemUseSettings
		global StateItemUse
		
		if StateItemUseSettings == 0:
			StateItemUseSettings = 1
			self.Gui[38].SetText("Finish")
			self.Gui[39].Show()
			self.Gui[17].Show()
			self.Gui[23].Show()
			self.Gui[7].Show()
			self.Gui[8].Show()
			self.Gui[9].Show()
			for i in xrange(40,52):	
				self.Gui[i].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			StateItemUse = [2 for x in xrange(12)]
		else:
			StateItemUseSettings = 0
			self.Gui[38].SetText("Settings")
			self.Gui[39].Hide()
			self.Gui[17].Hide()
			self.Gui[23].Hide()
			self.Gui[7].Hide()
			self.Gui[8].Hide()
			self.Gui[9].Hide()
			for i in xrange(40,52):	
				self.Gui[i].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			StateItemUse = [0 for x in xrange(12)]
	
	def SaveItemList(self):
		self.WriteItemList()
		for i in range(0,12):
			if StateItemUse[i] == 3:
				if i == 0:
					self.EnableItemUse1()
				elif i == 1:
					self.EnableItemUse2()
				elif i == 2:
					self.EnableItemUse3()
				elif i == 3:
					self.EnableItemUse4()
				elif i == 4:
					self.EnableItemUse5()
				elif i == 5:
					self.EnableItemUse6()
				elif i == 6:
					self.EnableItemUse7()
				elif i == 7:
					self.EnableItemUse8()
				elif i == 8:
					self.EnableItemUse9()
				elif i == 9:
					self.EnableItemUse10()
				elif i == 10:
					self.EnableItemUse11()
				elif i == 11:
					self.EnableItemUse12()
	
	def EnableItemUse1(self):
		global StateItemUse
		
		if StateItemUse[0] == 0:
			StateItemUse[0] = 1
			self.Gui[40].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse1()
		elif StateItemUse[0] == 1:
			StateItemUse[0] = 0
			self.Gui[40].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse1()
		elif StateItemUse[0] == 2:
			StateItemUse[0] = 3
			self.Gui[40].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[0] == 3:
			StateItemUse[0] = 2
			self.Gui[40].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse1(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[1]):
				net.SendItemUsePacket(i)
				break
		
		self.delayItemUse1 = WaitingDialog()
		self.delayItemUse1.Open(int(ItemData[2]))
		self.delayItemUse1.SAFE_SetTimeOverEvent(self.ItemUse1)
	
	def DisableItemUse1(self):
		self.delayItemUse1.Close()
	
	def EnableItemUse2(self):
		global StateItemUse
		
		if StateItemUse[1] == 0:
			StateItemUse[1] = 1
			self.Gui[41].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse2()
		elif StateItemUse[1] == 1:
			StateItemUse[1] = 0
			self.Gui[41].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse2()
		elif StateItemUse[1] == 2:
			StateItemUse[1] = 3
			self.Gui[41].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[1] == 3:
			StateItemUse[1] = 2
			self.Gui[41].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
	
	def ItemUse2(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[4]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse2 = WaitingDialog()
		self.delayItemUse2.Open(int(ItemData[5]))
		self.delayItemUse2.SAFE_SetTimeOverEvent(self.ItemUse2)
	
	def DisableItemUse2(self):
		self.delayItemUse2.Close()
	
	def EnableItemUse3(self):
		global StateItemUse
		
		if StateItemUse[2] == 0:
			StateItemUse[2] = 1
			self.Gui[42].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse3()
		elif StateItemUse[2] == 1:
			StateItemUse[2] = 0
			self.Gui[42].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse3()
		elif StateItemUse[2] == 2:
			StateItemUse[2] = 3
			self.Gui[42].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[2] == 3:
			StateItemUse[2] = 2
			self.Gui[42].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
	
	def ItemUse3(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[7]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse3 = WaitingDialog()
		self.delayItemUse3.Open(int(ItemData[8]))
		self.delayItemUse3.SAFE_SetTimeOverEvent(self.ItemUse3)
	
	def DisableItemUse3(self):
		self.delayItemUse3.Close()
	
	def EnableItemUse4(self):
		global StateItemUse
		
		if StateItemUse[3] == 0:
			StateItemUse[3] = 1
			self.Gui[43].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse4()
		elif StateItemUse[3] == 1:
			StateItemUse[3] = 0
			self.Gui[43].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse4()
		elif StateItemUse[3] == 2:
			StateItemUse[3] = 3
			self.Gui[43].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[3] == 3:
			StateItemUse[3] = 2
			self.Gui[43].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
	
	def ItemUse4(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[10]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse4 = WaitingDialog()
		self.delayItemUse4.Open(int(ItemData[11]))
		self.delayItemUse4.SAFE_SetTimeOverEvent(self.ItemUse4)
	
	def DisableItemUse4(self):
		self.delayItemUse4.Close()
		
	def EnableItemUse5(self):
		global StateItemUse
		
		if StateItemUse[4] == 0:
			StateItemUse[4] = 1
			self.Gui[44].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse5()
		elif StateItemUse[4] == 1:
			StateItemUse[4] = 0
			self.Gui[44].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse5()
		elif StateItemUse[4] == 2:
			StateItemUse[4] = 3
			self.Gui[44].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[4] == 3:
			StateItemUse[4] = 2
			self.Gui[44].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
	
	def ItemUse5(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[13]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse5 = WaitingDialog()
		self.delayItemUse5.Open(int(ItemData[14]))
		self.delayItemUse5.SAFE_SetTimeOverEvent(self.ItemUse5)
	
	def DisableItemUse5(self):
		self.delayItemUse5.Close()
		
	def EnableItemUse6(self):
		global StateItemUse
		
		if StateItemUse[5] == 0:
			StateItemUse[5] = 1
			self.Gui[45].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse6()
		elif StateItemUse[5] == 1:
			StateItemUse[5] = 0
			self.Gui[45].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse6()
		elif StateItemUse[5] == 2:
			StateItemUse[5] = 3
			self.Gui[45].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[5] == 3:
			StateItemUse[5] = 2
			self.Gui[45].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
	
	def ItemUse6(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[16]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse6 = WaitingDialog()
		self.delayItemUse6.Open(int(ItemData[17]))
		self.delayItemUse6.SAFE_SetTimeOverEvent(self.ItemUse6)
	
	def DisableItemUse6(self):
		self.delayItemUse6.Close()
		
	def EnableItemUse7(self):
		global StateItemUse
		
		if StateItemUse[6] == 0:
			StateItemUse[6] = 1
			self.Gui[46].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse7()
		elif StateItemUse[6] == 1:
			StateItemUse[6] = 0
			self.Gui[46].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse7()
		elif StateItemUse[6] == 2:
			StateItemUse[6] = 3
			self.Gui[46].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[6] == 3:
			StateItemUse[6] = 2
			self.Gui[46].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse7(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[19]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse7 = WaitingDialog()
		self.delayItemUse7.Open(int(ItemData[20]))
		self.delayItemUse7.SAFE_SetTimeOverEvent(self.ItemUse7)
	
	def DisableItemUse7(self):
		self.delayItemUse7.Close()
		
	def EnableItemUse8(self):
		global StateItemUse
		
		if StateItemUse[7] == 0:
			StateItemUse[7] = 1
			self.Gui[47].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse8()
		elif StateItemUse[7] == 1:
			StateItemUse[7] = 0
			self.Gui[47].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse8()
		elif StateItemUse[7] == 2:
			StateItemUse[7] = 3
			self.Gui[47].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[7] == 3:
			StateItemUse[7] = 2
			self.Gui[47].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse8(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[22]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse8 = WaitingDialog()
		self.delayItemUse8.Open(int(ItemData[23]))
		self.delayItemUse8.SAFE_SetTimeOverEvent(self.ItemUse8)
	
	def DisableItemUse8(self):
		self.delayItemUse8.Close()
		
	def EnableItemUse9(self):
		global StateItemUse
		
		if StateItemUse[8] == 0:
			StateItemUse[8] = 1
			self.Gui[48].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse9()
		elif StateItemUse[8] == 1:
			StateItemUse[8] = 0
			self.Gui[48].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse9()
		elif StateItemUse[8] == 2:
			StateItemUse[8] = 3
			self.Gui[48].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[8] == 3:
			StateItemUse[8] = 2
			self.Gui[48].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse9(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[25]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse9 = WaitingDialog()
		self.delayItemUse9.Open(int(ItemData[26]))
		self.delayItemUse9.SAFE_SetTimeOverEvent(self.ItemUse9)
	
	def DisableItemUse9(self):
		self.delayItemUse9.Close()
		
	def EnableItemUse10(self):
		global StateItemUse
		
		if StateItemUse[9] == 0:
			StateItemUse[9] = 1
			self.Gui[49].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse10()
		elif StateItemUse[9] == 1:
			StateItemUse[9] = 0
			self.Gui[49].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse9()
		elif StateItemUse[9] == 2:
			StateItemUse[9] = 3
			self.Gui[49].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[9] == 3:
			StateItemUse[9] = 2
			self.Gui[49].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse10(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[28]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse10 = WaitingDialog()
		self.delayItemUse10.Open(int(ItemData[29]))
		self.delayItemUse10.SAFE_SetTimeOverEvent(self.ItemUse10)
	
	def DisableItemUse10(self):
		self.delayItemUse10.Close()
		
	def EnableItemUse11(self):
		global StateItemUse
		
		if StateItemUse[10] == 0:
			StateItemUse[10] = 1
			self.Gui[50].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse11()
		elif StateItemUse[10] == 1:
			StateItemUse[10] = 0
			self.Gui[50].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse11()
		elif StateItemUse[10] == 2:
			StateItemUse[10] = 3
			self.Gui[50].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[10] == 3:
			StateItemUse[10] = 2
			self.Gui[50].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse11(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[31]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse11 = WaitingDialog()
		self.delayItemUse11.Open(int(ItemData[32]))
		self.delayItemUse11.SAFE_SetTimeOverEvent(self.ItemUse10)
	
	def DisableItemUse11(self):
		self.delayItemUse11.Close()
		
	def EnableItemUse12(self):
		global StateItemUse
		
		if StateItemUse[11] == 0:
			StateItemUse[11] = 1
			self.Gui[51].SetUpVisual("d:/ymir work/ui/public/middle_button_02.sub")
			self.ItemUse12()
		elif StateItemUse[11] == 1:
			StateItemUse[11] = 0
			self.Gui[51].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
			self.DisableItemUse12()
		elif StateItemUse[11] == 2:
			StateItemUse[11] = 3
			self.Gui[51].SetUpVisual("d:/ymir work/ui/public/middle_button_03.sub")
		elif StateItemUse[11] == 3:
			StateItemUse[11] = 2
			self.Gui[51].SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		
	def ItemUse12(self):
		ItemData = self.ReadItemList()
		
		for i in xrange(0, 90):
			ItemValue = player.GetItemIndex(i)
			if ItemValue == int(ItemData[34]):
				net.SendItemUsePacket(i)
				break
					
		self.delayItemUse12 = WaitingDialog()
		self.delayItemUse12.Open(int(ItemData[35]))
		self.delayItemUse12.SAFE_SetTimeOverEvent(self.ItemUse12)
	
	def DisableItemUse12(self):
		self.delayItemUse12.Close()
		
class WaitingDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.eventTimeOver = lambda *arg: None
		self.eventExit = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self, waitTime):
		curTime = time.clock()
		self.endTime = curTime + waitTime

		self.Show()		

	def Close(self):
		self.Hide()

	def Destroy(self):
		self.Hide()

	def SAFE_SetTimeOverEvent(self, event):
		self.eventTimeOver = ui.__mem_func__(event)

	def SAFE_SetExitEvent(self, event):
		self.eventExit = ui.__mem_func__(event)
		
	
	def OnUpdate(self):
		lastTime = max(0, self.endTime - time.clock())
		if 0 == lastTime:
			self.Close()
			self.eventTimeOver()
			
		else:
			return
		
StartHack = Multi()