import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class InventoryManagerDialog(ui.ScriptWindow):
	Gui = []
	type = 0
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.LoadBoard()
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
		
	def LoadBoard(self):
	
		self.AddGui()
		
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [210, 415], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [185, 10], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.SlotBar, 0], [190, 225], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [15, 50], [["SetViewItemCount", [10]]], []],			
			[[ui.ScrollBar, 0], [0, 0], [180, 40], [["SetScrollBarSize", [220]]], []],			
			[[ui.TextLine, 0], [0, 0], [50, 8], [["SetOutline", [""]],	["SetText", ["Inventory Manager"]],	["SetFontColor", [1.0, 0.8, 0]]], []],			
			[[ui.TextLine, 0], [0, 0], [10, 37], [["SetOutline", [""]],	["SetText", [" Slot:	 ID:			Name:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],			
			[[ui.Button, 0], [0, 0], [160, 8], [['SetUpVisual', ["d:/ymir work/ui/game/guild/refresh_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/game/guild/refresh_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/game/guild/refresh_button_03.sub"]], ['SetToolTipText', ["Refresh", 0, - 23]], ['SetEvent', [lambda : self.UpdateFileList()]]], []],	
			[[ui.Button, 0], [0, 0], [15, 265], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Upgrade Selected"]], ['SetToolTipText', ["Upgrades selected Item x Times"]], ['SetEvent', [lambda : self.UpgradeSingleItem()]]], []],	
			[[ui.Button, 0], [0, 0], [110, 265], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Upgrade All"]], ['SetToolTipText', ["Upgrades All same Items x Times"]], ['SetEvent', [lambda : self.UpgradeItemType()]]], []],	
			[[ui.TextLine, 0], [0, 0], [70, 292], [["SetOutline", [""]],	["SetText", ["Upgrade					x"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.Button, 0], [0, 0], [15, 315], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ['SetText', ["Drop Selected"]], ['SetToolTipText', ["Drops all same Items like the selected one"]], ['SetEvent', [lambda : self.DropItem()]]], []],	
			[[ui.Button, 0], [0, 0], [110, 315], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ['SetText', ["Drop All"]], ['SetToolTipText', ["Drops ALL Items in your Inventory"]], ['SetEvent', [lambda : self.DropAllItemsRequest()]]], []],	
			[[ui.Button, 0], [0, 0], [15, 340], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ['SetText', ["Sell Selected"]], ['SetToolTipText', ["Sells all same Items like the selected one"]], ['SetEvent', [lambda : self.SellItem()]]], []],	
			[[ui.Button, 0], [0, 0], [110, 340], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ['SetText', ["Sell All"]], ['SetToolTipText', ["Sells ALL Items in your Inventory"]], ['SetEvent', [lambda : self.SellAllItems()]]], []],	
			[[ui.SlotBar, 0], [15, 18], [115, 292], [], []],			
			[[ui.EditLine, 15], [15, 17], [6, 2], [["SetMax", [1]], ["SetText", ["6"]], ["SetNumberMode", [""]], ["SetFocus", [""]]], []],
			[[ui.Button, 0], [0, 0], [60, 365], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ['SetText', ["DT-Upgr. selected"]], ['SetToolTipText', ["Sells ALL Items in your Inventory"]], ['SetEvent', [lambda : self.UpgradeSingleDTItem()]]], []],	
			[[ui.TextLine, 0], [0, 0], [63, 390], [["SetOutline", [""]],	["SetText", ["~by DaRealFreak~"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			]
		GuiParser(Gui, self.Gui)
		
		
		self.Gui[3].SetScrollBar(self.Gui[4])
		self.Gui[0].SetPosition(52, 40)
		self.UpdateFileList()
	
	
		
	def OnPressEscapeKey(self):
		
		self.CloseAbfrage()
		return TRUE
		
	def CloseAbfrage(self):
		self.__del__()
		
	def UpdateFileList(self):
		self.Gui[3].RemoveAllItems()
		for i in xrange(100):
			ItemIndex = player.GetItemIndex(i)
			if ItemIndex != 0:
				item.SelectItem(ItemIndex)
				item.GetItemName(ItemIndex)
				ItemName = item.GetItemName()
				self.Gui[3].AppendItem(Item(str(i) + "	" + str(ItemIndex) + "	" + ItemName))

	def UpgradeSingleItem(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item selected!")
			return
		SelectedItem = ItemIndex.GetText().split("	")
		Count = int(self.Gui[16].GetText())
	#	self.UpgradeItem(int(SelectedItem[0]), int(Count))
#	def UpgradeItem(self, Slot, Count):
	#	self.BannedSlotIndex = []
		for i in xrange(4):
	#		if self.type == 0:
			net.SendRefinePacket(int(SelectedItem[0]), 0)
			break
				
	def UpgradeSingleDTItem(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item selected!")
			return
		SelectedItem = ItemIndex.GetText().split("	")
		Count = int(self.Gui[16].GetText())
		self.UpgradeDTItem(int(SelectedItem[0]), int(Count))
	def UpgradeDTItem(self, Slot, Count):
		self.BannedSlotIndex = []
		for i in xrange(Count):
			if self.type == 0:
				net.SendRefinePacket(Slot, 4)
				break
				
			
	def UpgradeItemType(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item Selected!")
			return
		try:
			SearchedName = ItemIndex.GetText().split("	")[2].split("+")[0]
		except:
			SearchedName = ItemIndex.GetText().split("	")[2]
		Count = int(self.Gui[16].GetText())
		for Slot in xrange(0, 90):
			ItemValue = player.GetItemIndex(Slot)
			try:
				ItemName = item.GetItemName(item.SelectItem(ItemValue)).split("+")[0]
			except:
				ItemName = item.GetItemName(item.SelectItem(ItemValue))
			if ItemName == SearchedName:
				self.UpgradeItem(Slot, Count)
		
	def SellItem(self):
		if not shop.IsOpen():
			chat.AppendChat(7, "You need an open Shop for that!")
			return
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No selctd Items!")
			return
			
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
				net.SendShopSellPacket(Slot)

	def SellAllItems(self):
		if not shop.IsOpen():
			chat.AppendChat(7, "You need an open Shop for that!")
			return
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do you want so sell All your Items?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.SellAll))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()
		
	def SellAll(self):
		for i in xrange(90):
			net.SendShopSellPacket(i)
		self.CancelQuestionDialog()
	
	def DropItem(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "No Item selected!")
			return
		SelectedItem = ItemIndex.GetText().split("	")
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
				net.SendItemDropPacket(Slot)
		
	def DropAllItemsRequest(self):
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do you want to drop ALL your Items?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.DropAllItems))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()
			
	def DropAllItems(self):
		for i in xrange(90):
			net.SendItemDropPacket(i)
		self.CancelQuestionDialog()
		
	def CancelQuestionDialog(self):
		self.QuestionDialog.Close()
		self.QuestionDialog = None

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

		
#InventoryManagerDialog().Show()