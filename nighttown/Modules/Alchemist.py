import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr,event
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

teleport_mode = 0
telestep = 0
last_teleport_time = 0



class EnergyBotDialog(ui.ScriptWindow):
	
	Gui = []
	type = 0
	state = ""
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()
		self.InstallQuestWindowHook()
		
	def __del__(self):
		self.Gui[0].Hide()
		self.UnHookQuestWindow()
		ui.ScriptWindow.__del__(self)
		
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [210, 398], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [185, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.SlotBar, 0], [190, 225], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [15, 50], [["SetViewItemCount", [10]]], []],			
			[[ui.ScrollBar, 0], [0, 0], [180, 40], [["SetScrollBarSize", [220]]], []],			
			[[ui.TextLine, 0], [0, 0], [70, 8], [["SetOutline", [""]],	["SetText", ["Alchemist-Bot"]],	["SetFontColor", [1.0, 0.8, 0]]], []],			
			[[ui.TextLine, 0], [0, 0], [10, 37], [["SetOutline", [""]],	["SetText", [" Slot:	 ID:			Name:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],			
			[[ui.TextLine, 0], [0, 0], [78, 327], [["SetOutline", [""]],	["SetText", ["~by 123klo~"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.Button, 0], [0, 0], [15, 275], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Give Selected"]], ['SetToolTipText', ["Upgrades selected Item x Times"]], ['SetEvent', [lambda : self.GiveSingleItem()]]], []],	
			[[ui.Button, 0], [0, 0], [110, 275], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Give All"]], ['SetToolTipText', ["Upgrades All same Items x Times"]], ['SetEvent', [lambda : self.GiveAllItemsRequest()]]], []],	
			[[ui.Button, 0], [0, 0], [15, 305], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Buy One"]], ['SetToolTipText', ["Buys one level 36 dagger"]], ['SetEvent', [lambda : self.BuyOne()]]], []],	
			[[ui.Button, 0], [0, 0], [110, 305], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Buy All"]], ['SetToolTipText', ["Buys 90 level 36 dagger"]], ['SetEvent', [lambda : self.BuyAll()]]], []],	
			[[ui.Button, 0], [0, 0], [15, 345], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Alchemist"]], ['SetToolTipText', ["Buys one level 36 dagger"]], ['SetEvent', [lambda : self.TeleportToCoordinates("alchemist")]]], []],	
			[[ui.Button, 0], [0, 0], [110, 345], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["WeaponDealer"]], ['SetToolTipText', ["Buys 90 level 36 dagger"]], ['SetEvent', [lambda : self.TeleportToCoordinates("weapon")]]], []],
			[[ui.Button, 0], [0, 0], [60, 370], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Sellbot"]], ['SetToolTipText', ["Buy and Sells Items"]], ['SetEvent', [lambda : self.Sellbot()]]], []],
			[[ui.Button, 0], [0, 0], [160, 8], [['SetUpVisual', ["d:/ymir work/ui/game/guild/refresh_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/refresh_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/refresh_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
		#	[[ui.Button, 0], [0, 0], [140, 8], [['SetUpVisual', ["d:/ymir work/ui/game/guild/refresh_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/game/guild/refresh_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/game/guild/refresh_button_03.sub"]], ['SetToolTipText', ["Refresh", 0, - 23]], ['SetEvent', [lambda : self.UpdateFileList()]]], []],	
			]
		GuiParser(Gui, self.Gui)
	
		self.Gui[3].SetScrollBar(self.Gui[4])
		self.Gui[0].SetPosition(52, 40)
		self.Gui[0].AddFlag("movable")
		self.UpdateFileList()
		
	def Sellbot(self):
		self.SellBotDialog = SellBotDialog()
	
	def OnPressEscapeKey(self):
		self.__del__()
		return TRUE

	def UpdateFileList(self):
		self.Gui[3].RemoveAllItems()
		for i in xrange(100):
			ItemIndex = player.GetItemIndex(i)
			if ItemIndex != 0:
				item.SelectItem(ItemIndex)
				item.GetItemName(ItemIndex)
				ItemName = item.GetItemName()
				self.Gui[3].AppendItem(Item(str(i) + "	" + str(ItemIndex) + "	" + ItemName))

	def GiveSingleItem(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item selected!")
			return
		SelectedItem = ItemIndex.GetText().split("	")
		vid = player.GetTargetVID()
	#	chat.AppendChat(chat.CHAT_TYPE_INFO, str(vid))
		net.SendGiveItemPacket(int(vid), int(SelectedItem[0]), 1)				# DE 12302
		## Questions ##
		event.SelectAnswer(1, 0)
		## Except Fail/Succes ##
		event.SelectAnswer(1, 0)
				
	
	def GiveAllItemsRequest(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		try:
			SearchedName = ItemIndex.GetText().split("	")[2].split("+")[0]
		except:
			SearchedName = ItemIndex.GetText().split("	")[2]
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do You want to give all "+SearchedName+"´s to the alchemist?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.GiveAllItems))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()
		
	def GiveAllItems(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item Selected!")
			return
		self.CancelQuestionDialog()
		try:
			SearchedName = ItemIndex.GetText().split("	")[2].split("+")[0]
		except:
			SearchedName = ItemIndex.GetText().split("	")[2]
		for Slot in xrange(0, 90):
			ItemValue = player.GetItemIndex(Slot)
			try:
				ItemName = item.GetItemName(item.SelectItem(ItemValue)).split("+")[0]
			except:
				ItemName = item.GetItemName(item.SelectItem(ItemValue))
			if ItemName == SearchedName:
				vid = player.GetTargetVID()
				net.SendGiveItemPacket(int(vid), Slot, 1)
				## Questions ##
				event.SelectAnswer(1, 0)
				## Except Fail/Succes ##
				event.SelectAnswer(1, 0)
			
	def BuyOne(self):
		if shop.IsOpen():
			net.SendShopBuyPacket(25)
		self.TeleportToCoordinates()
	def BuyAll(self):
		if shop.IsOpen():
			for All in xrange(90):
				net.SendShopBuyPacket(25)
			
		
		
	def DropAllItemsRequest(self):
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do you want to drop ALL your Items?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.DropAllItems))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()
	def CancelQuestionDialog(self):
		self.QuestionDialog.Close()
		self.QuestionDialog = None
	def InstallQuestWindowHook(self):
		self.OldRecv = game.GameWindow.OpenQuestWindow
		game.GameWindow.OpenQuestWindow = self.HookedQuestWindow
	def UnHookQuestWindow(self):
		game.GameWindow.OpenQuestWindow = self.OldRecv
	def HookedQuestWindow(self, skin, idx):
		pass
	
	def OnRender(self):
		global telestep
		global teleport_mode
		global last_teleport_time
	#	self.UpdateFileList()
		teleport_mode = 0
		telestep = 0
		x,y = player.GetMainCharacterPosition()[:2]
		if teleport_mode == 1 and app.GetTime() > last_teleport_time + 5:
			last_teleport_time = app.GetTime()
			if self.State == "alchemist":
				self.TeleportToCoordinates("alchemist")	
			else:
				self.TeleportToCoordinates("weapon")
		
		
	def TeleportToCoordinates(self,mode):
		global telestep,teleport_mode
		(ax, ay, az) = player.GetMainCharacterPosition()
		if mode == "alchemist":
			x_coordinate = int(641)*100
			y_coordinate = int(663)*100
			self.State = "alchemist"
		else:
			x_coordinate = int(595)*100
			y_coordinate = int(602)*100
			self.State = "weapon"
		z_coordinate = int(0)*100
		
		teleport_mode = 1
		
###Teleportsteps by musicinstructor		
		if int(x_coordinate) < int(ax):
			while int(x_coordinate) < int(ax):
				if telestep > 10:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax) - 2000, int(ay))
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1
				
			chr.SetPixelPosition(int(x_coordinate), int(ay))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
			
		if int(x_coordinate) > int(ax):
			while int(x_coordinate) > int(ax):
				if telestep > 10:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax) + 2000, int(ay))
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1
				
			chr.SetPixelPosition(int(x_coordinate), int(ay))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
			
		if int(y_coordinate) < int(ay):
			while int(y_coordinate) < int(ay):
				if telestep > 10:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax), int(ay) - 2000)
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1
			
			chr.SetPixelPosition(int(ax), int(y_coordinate))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
			
		if int(y_coordinate) > int(ay):
			while int(y_coordinate) > int(ay):
				if telestep > 10:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax), int(ay) + 2000)
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1

			chr.SetPixelPosition(int(ax), int(y_coordinate))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)

		if int(z_coordinate) < int(az) and int(z_coordinate) != 0:
			while int(z_coordinate) < int(az):
				if telestep > 7:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax), int(ay), int(az) - 2000)
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1

			chr.SetPixelPosition(int(ax), int(ay), int(z_coordinate))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
			
		if int(z_coordinate) > int(az) and int(z_coordinate) != 0:
			while int(z_coordinate) > int(az):
				if telestep > 7:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "Um einen Packet-Flood Kick zu vermeiden wird erst in 5 Sekunden weiterteleportiert.")
					return
				chr.SetPixelPosition(int(ax), int(ay), int(az) + 2000)
				player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
				player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
				(ax, ay, az) = player.GetMainCharacterPosition()
				telestep = telestep + 1

			chr.SetPixelPosition(int(ax), int(ay), int(z_coordinate))
			player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
		
		if self.State == "alchemist":
			if player.GetMainCharacterPosition() == (641,663)[:2]:
				teleport_mode = 0
		else:
			if player.GetMainCharacterPosition() == (595,602)[:2]:
				teleport_mode = 0
		
		
		

class Item(ui.ListBoxEx.Item):
	def __init__(self, fileName):
		ui.ListBoxEx.Item.__init__(self)
		self.canLoad=0
		self.text=fileName
		self.textLine=self.__CreateTextLine(fileName)          

	def __del__(self):
		ui.ListBoxEx.Item.__del__(self)

	def GetText(self):
		return self.text

	def SetSize(self, width, height):
		ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

	def __CreateTextLine(self, fileName):
		textLine=ui.TextLine()
		textLine.SetParent(self)
		textLine.SetPosition(0, 0)
		textLine.SetText(fileName)
		textLine.Show()
		return textLine

def GuiParser(guiobjects, list):
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
		Object.Show()
	
		list.append(Object)		


class SellBotDialog(ui.ScriptWindow): 				
	
	State = 0
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.LoadGui()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	def Close(self):
		self.Board.Hide()
		
	def LoadGui(self):
	
		self.Board = ui.ThinBoard() 
		self.Board.SetPosition(262, 40)
		self.Board.SetSize(90, 110) 
		self.Board.AddFlag("float") 
		self.Board.AddFlag("movable")
		self.Board.Show()
		
		self.comp = Component()
		self.CloseButton = self.comp.Button(self.Board, '', 'Close', 68, 8, self.Close, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.HeaderLabel = self.comp.TextLine(self.Board, 'Sellbot', 25, 8, self.comp.RGB(255, 255, 0))
		self.ShopslotLabel = self.comp.TextLine(self.Board, 'Shopslot:', 10, 35, self.comp.RGB(255, 255, 255))
	#	self.ShopslotLabel = self.comp.TextLine(self.Board, 'Shopslot:', 10, 55, self.comp.RGB(255, 255, 255))

		chat.AppendChat(1, "Please move the items from slot 0 away!")
		self.StateButton = self.comp.Button(self.Board, 'Start', '', 15, 60, self.SetState, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.InfoButton = self.comp.Button(self.Board, 'Info', '', 15, 85, self.Info, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.Slotbar, self.Edidline = self.comp.SlotBarEditLine(self.Board, '9', 60, 35, 20, 15, 2)
	
	def SetState(self):	
		if self.State == 0:
			self.State = 1
			self.StateButton.SetText("Stop")
			self.StateStart()
		else:	
			self.State = 0
			self.StateButton.SetText("Start")
			self.StateStop()
	def Info(self):
		self.InfoDialog = InfoDialog()	
	
	def StateStart(self):
		
		if shop.IsOpen():
			net.SendShopBuyPacket(int(self.Edidline.GetText()))
			net.SendShopSellPacket(0)
		else:
			self.State = 0
			chat.AppendChat(1, "Please open a Shop!")
			chat.AppendChat(1, "Please move the items from slot 0 away!")
			self.StateButton.SetText("Start")
			self.StateStop()
		
		self.Update = WaitingDialog()			
		self.Update.Open(int(0.5))
		self.Update.SAFE_SetTimeOverEvent(self.StateStart)
	
	def StateStop(self):
		self.Update = WaitingDialog()
		self.Update.Close()	
	

class InfoDialog(ui.ScriptWindow): 				
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.LoadGui()
	def __del__(self):
		ui.ScriptWindow.__del__(self)
	def Close(self):
		self.Board.Hide()
		
	def LoadGui(self):
		self.Board = ui.ThinBoard() 
		self.Board.SetPosition(352, 40)
		self.Board.SetSize(180, 295) 
		self.Board.Show()
		
		self.comp = Component()
		self.CloseButton = self.comp.Button(self.Board, '', 'Close', 160, 8, self.Close, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.HeaderLabel = self.comp.TextLine(self.Board, 'Info - Shopslot Number', 25, 8, self.comp.RGB(255, 255, 0))
		
		self.Image = ui.ExpandedImageBox()
		self.Image.SetParent(self.Board)
		self.Image.SetPosition(2, 25)
		self.Image.LoadImage("m2kmod/Images/General/shop.tga")
		self.Image.Show()

	
class Component:
	def Button(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.Show()
		button.SetEvent(func)
		return button
	def CheckButton(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.SetEvent(func)
		return button	
	def TextLine(self, parent, textlineText, x, y, color):
		textline = ui.TextLine()
		if parent != None:
			textline.SetParent(parent)
		textline.SetPosition(x, y)
		if color != None:
			textline.SetFontColor(color[0], color[1], color[2])
		textline.SetText(textlineText)
		textline.SetOutline()
		textline.Show()
		return textline
	def RGB(self, r, g, b):
		return (r*255, g*255, b*255)
	def ExpandedImage(self, parent, x, y, img):
		image = ui.ExpandedImageBox()
		if parent != None:
			image.SetParent(parent)
		image.SetPosition(x, y)
		image.LoadImage(img)
		image.Show()
		return image	
	def SliderBar(self, parent, sliderPos, func, x, y):
		Slider = ui.SliderBar()
		if parent != None:
			Slider.SetParent(parent)
		Slider.SetPosition(x, y)
		Slider.SetSliderPos(sliderPos)
		Slider.Show()
		Slider.SetEvent(func)
		return Slider		
	def EditLine(self, parent, width, heigh, x, y, editlineText, max):
		Value = ui.EditLine()
		if parent != None:
			Value.SetParent(parent)
		Value.SetSize(width, heigh)
		Value.SetPosition(x, y)
		Value.SetMax(max)
		Value.SetText(editlineText)
		Value.SetNumberMode()
		Value.Show()
		return Value
	def SlotBarEditLine(self, parent, editlineText, x, y, width, heigh, max):
		SlotBar = ui.SlotBar()
		if parent != None:
			SlotBar.SetParent(parent)
		SlotBar.SetSize(width, heigh)
		SlotBar.SetPosition(x, y)
		SlotBar.Show()
		Value = ui.EditLine()
		Value.SetParent(SlotBar)
		Value.SetSize(width, heigh)
		Value.SetPosition(6, 0)
		Value.SetMax(max)
		Value.SetLimitWidth(width)
		Value.SetMultiLine()
		Value.SetText(editlineText)
		#Value.SetNumberMode()
		Value.Show()
		return SlotBar, Value		

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
		
	def OnPressExitKey(self):
		self.Close()
		return TRUE
		
#EnergyBotDialog().Show()