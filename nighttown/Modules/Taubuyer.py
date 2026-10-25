import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class TauAutobuyDialog(ui.ScriptWindow):

	Gui = []
	PotionBuffer = {}
	Taus = [50821, 50822, 50823, 50824, 50825, 50826]

	ExpBot = "off"

	PotionManagerGui = []
	PotionManager = [100, 5]
	PotionManagerState = "off"
	
	State = 0
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
		
		
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [200, 340], [0,0], [["SetCenterPosition", [""]]], ["float"]],		
			[[ui.SlotBar, 0], [170, 140], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [25, 50], [["SetViewItemCount", [6]]], []],			
			[[ui.ScrollBar, 0], [0, 0], [160, 40], [["SetScrollBarSize", [130]]], []],			
			[[ui.TextLine, 0], [0, 0], [70, 180], [["SetDefaultFontName", [""]], ["SetText", ["Minimum Value"]],	["SetFontColor", [0.6, 0.7, 1.0]]], []],			
			[[ui.SliderBar, 0], [0, 0], [13, 200], [["SetEvent", [ui.__mem_func__(self.SetConfig)]], ["SetSliderPos", [0.5]]], []],			
			[[ui.TextLine, 0], [0, 0], [85, 215], [["SetDefaultFontName", [""]], ["SetText", ["+ 100"]],	], []],			
			[[ui.TextLine, 0], [0, 0], [85, 240], [["SetDefaultFontName", [""]], ["SetText", ["Dauer"]],	["SetFontColor", [0.6, 0.7, 1.0]]], []],			
			[[ui.SliderBar, 0], [0, 0], [13, 260], [["SetEvent", [ui.__mem_func__(self.SetConfig)]], ["SetSliderPos", [0.5]]], []],			
			[[ui.TextLine, 0], [0, 0], [87, 275], [["SetDefaultFontName", [""]], ["SetText", ["5 Min"]],	], []],			
			[[ui.Button, 0], [0, 0], [80, 295], [['SetUpVisual', ["m2kmod\Images\start_0.tga"]],['SetOverVisual', ["m2kmod\Images\start_1.tga"]], ['SetDownVisual', ["m2kmod\Images\start_2.tga"]], ['SetEvent', [lambda : self.PotionState()]]], []],		
			[[ui.Button, 0], [0, 0], [80, 295], [['SetUpVisual', ["m2kmod\Images\stop_0.tga"]],['SetOverVisual', ["m2kmod\Images\stop_1.tga"]], ['SetDownVisual', ["m2kmod\Images\stop_2.tga"]], ['SetEvent', [lambda : self.PotionState()]]], []],	
			[[ui.TextLine, 0], [0, 0], [55, 8], [["SetOutline", [""]],	["SetText", ["Tau Auto-Buyer"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.Button, 0], [0, 0], [170, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.HidePotionManagement()]]], []],	
			]
		GuiParser(Gui, self.PotionManagerGui)
		self.PotionManagerGui[0].SetPosition(52, 40)
		self.PotionManagerGui[11].Hide()
		self.PotionManagerGui[2].SetScrollBar(self.PotionManagerGui[3])
		for blaaa in self.Taus:
			self.PotionManagerGui[2].AppendItem(Item(str(blaaa) + "	" + str(item.GetItemName(item.SelectItem(blaaa)))))
	
	def PotionState(self):
		if not shop.IsOpen():
			chat.AppendChat(1, "Please open a Shop first!")
			return
		ItemIndex = self.PotionManagerGui[2].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Please select an Item!")
			return
		if self.State == 0:
			self.State = 1
			self.PotionManagerGui[10].Hide()
			self.PotionManagerGui[11].Show()
			self.StartBuying()
			chat.AppendChat(1, "The Potion manager has started!")
		else:
			self.State = 0
			self.PotionManagerGui[11].Hide()
			self.PotionManagerGui[10].Show()
			self.StopBuying()
			chat.AppendChat(1, "The Potion manager has stopped!")
	
	def HidePotionManagement(self):
		self.PotionManagerGui[0].Hide()
	
	def SetConfig(self):
		Value, Time = self.PotionManager
		
		MinValue = int(self.PotionManagerGui[5].GetSliderPos() * 200)
		MinTime = int(self.PotionManagerGui[8].GetSliderPos() * 10)
		if MinValue != Value:
			self.PotionManagerGui[6].SetText("+ " + str(MinValue))
		if MinTime != Time:
			self.PotionManagerGui[9].SetText(str(MinTime) + " Min")
			
		self.PotionManager = [MinValue, MinTime]

			
	def StartBuying(self):
		ItemIndex = self.PotionManagerGui[2].GetSelectedItem()
		MinValue, MinTime = self.PotionManager
		MinTime = MinTime * 60
		PotionValue = int(ItemIndex.GetText().split("	")[0])
		
		for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
			ItemIndex = player.GetItemIndex(InventorySlot)
			if PotionValue == ItemIndex:
				Value0, Value , Time = [player.GetItemMetinSocket(InventorySlot, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
				if Value >= MinValue and Time >= MinTime:
					self.StopBuying()
				else:
					net.SendShopSellPacket(InventorySlot)
		for EachShopSlot in xrange(shop.SHOP_SLOT_COUNT):
			ShopItemValue = shop.GetItemID(EachShopSlot)
			if ShopItemValue == int(PotionValue):
				net.SendShopBuyPacket(EachShopSlot)
				break
		self.Wait = WaitingDialog()			
		self.Wait.Open(1.0)
		self.Wait.SAFE_SetTimeOverEvent(self.StartBuying)
	def StopBuying(self):
		self.Wait = WaitingDialog()	
		self.Wait.Close()
		
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
#TauAutobuyDialog().Show()