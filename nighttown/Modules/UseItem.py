import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class FarmToolsDialog(ui.ScriptWindow):

	Gui = []
	PotionBuffer = {}
	Taus = [50821, 50822, 50823, 50824, 50825, 50826]
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Gui = []
		self.AddGui()
		
		
	def __del__(self):
		self.Gui[0].Hide()
		try:
			self.PotionManagerGui[0].Hide()
		except:
			pass
		ui.ScriptWindow.__del__(self)
		
	def CreateGuild(self):
		pass
	def OpenPotionManagement(self):
		pass
		
	def AddGui(self):	
		Gui = [
			[[ui.ThinBoard, ""], [249, 300], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [225, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Schlieﬂen", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.TextLine, 0], [0, 0], [90, 8], [["SetOutline", [""]],	["SetText", ["Auto Potion Usage"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.TextLine, 0], [0, 0], [100, 250], [["SetOutline", [""]],	["SetText", ["©DaRealFreak"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			]
		GuiParser(Gui, self.Gui)
		
		self.Potions = []
		self.Leftovers = [50813,50814,50816,50817, 50821,50822,50825,50826, 71027,71028,71029,71030,71044,71045,50107,50108,27102]
		for bla in self.Leftovers:
			self.Potions.append(bla)
		tmp = []
		x = 22
		y = 30
		for potion in self.Potions:
			Index = self.Potions.index(potion)
			if IsDivideAble(Index, 4):
				x = 22
				y += 50
			ItemName = item.GetItemName(item.SelectItem(potion))
			ItemIcon = item.GetIconImageFileName()
			button = [[ui.ExpandedImageBox, 0], [0, 0], [x, y], [['LoadImage', [ItemIcon]]], []]
			name = [[ui.Button, 0], [0, 0], [x+7, y + 35], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ["SetText", [" "]], ['SetEvent', [lambda arg = (self.Potions.index(potion)): self.AutoUsage(arg)]]], []]
			tmp.append(button)
			tmp.append(name)
			x += 58					
		GuiParser(tmp, self.Gui)
		self.Gui[0].SetPosition(52, 40)
		
	def AutoUsage(self, ItemIndex):
		ItemValue = self.Potions[ItemIndex]
		try:
			del self.PotionBuffer[ItemValue]
			chat.AppendChat(1, item.GetItemName(item.SelectItem(ItemValue)) + " will not used!")
		except KeyError:
			self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp()
			chat.AppendChat(1, item.GetItemName(item.SelectItem(ItemValue)) + " will used from now!")
	
	def UsePotion(self, ItemValue):
		if player.GetItemCountByVnum(ItemValue) == 0:
			return
			
		Firework = [50107, 50108]
		Berries = [50813, 50814, 50817, 50818, 50819, 50820, 50801, 50802]
		GodItems = [27301, 71028, 71029, 71030]
		HelpItems = [71044, 71045, 27102]

		if ItemValue in self.Taus:
			HighestValue = [0, 0]
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemIndex = player.GetItemIndex(InventorySlot)
				if ItemValue == ItemIndex:
					Value0, Value , Time = [player.GetItemMetinSocket(InventorySlot, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
					if HighestValue[0] < Value:
						HighestValue = [Value, InventorySlot, Time]
						self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp() + HighestValue[2] + 2
			net.SendItemUsePacket(HighestValue[1])

		elif ItemValue in Firework:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemIndex = player.GetItemIndex(InventorySlot)
				if ItemValue == ItemIndex:
					net.SendItemUsePacket(InventorySlot)
					self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp() + 482
					break
					
		elif ItemValue in Berries:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemIndex = player.GetItemIndex(InventorySlot)
				if ItemValue == ItemIndex:
					net.SendItemUsePacket(InventorySlot)
					self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp() + 362
					break
					
		elif ItemValue in GodItems:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemIndex = player.GetItemIndex(InventorySlot)
				if ItemValue == ItemIndex:
					net.SendItemUsePacket(InventorySlot)
					self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp() + 1802
					break
					
		elif ItemValue in HelpItems:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemIndex = player.GetItemIndex(InventorySlot)
				if ItemValue == ItemIndex:
					net.SendItemUsePacket(InventorySlot)
					self.PotionBuffer[ItemValue] = app.GetGlobalTimeStamp() + 603
					break	
		chat.AppendChat(1, "Auto Usage: " + str(ItemValue))
	
	def OnUpdate(self):
		
		if self.PotionBuffer == {}:
			return
			
		for Potion in self.PotionBuffer:
			if app.GetGlobalTimeStamp() >= self.PotionBuffer[Potion]:
				self.UsePotion(Potion)
				
		

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

def IsDivideAble(x, y):
	if x == 0:
		return
	if float(x/y) == DivideToFloat(x, y):
		return 1
	
def DivideToFloat(x, y):
	try:
		return x * (y**-1)
	except:
		return 0		
		
#FarmToolsDialog().Show()











