import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class SwitchBotDialog(ui.ScriptWindow):
	Gui = []
	BoniGui = []
	
	Values = []
	Boni = []
	Count = 0
	Slot = 0
	Startmode = 0
	Swich = 0
	
	LastProcessTimeStamp = 0
	
	SlotStack = [0, 0]
	BonusIDListePL = [["nic", 0], ["Max. PZ", 1], ["Max. PE", 2], ["Witalnosc", 3], ["Inteligencja", 4], ["Sila", 5], ["Zrecznosc", 6], ["Szybkosc Ataku", 7], ["Szybkosc ruchu", 8], ["Szybkosc zaklecia", 9], ["Regeneracja PZ", 10], ["Regeneracja PE", 11], ["Szansa na otrucie", 12], ["Szansa na omdlenie", 13], ["Szansa na spowolnienie", 14], ["Szansa na kryt", 15], ["Szansa na przesz", 16], ["Ludzie", 17], ["Zwierzeta", 18], ["Orki", 19], ["Mistyki", 20], ["Nieumarli", 21], ["Diably", 22], ["Kradziez HP", 23], ["Kradziez PE", 24], ["Szansa na kradziez PE", 25], ["Szansa na odzyskanie PE", 26], ["Blok ciosow", 27], ["Unikniecie skrzaly", 28], ["Odpornosc na miecze", 29], ["Odpornosc na 2 reke", 30], ["Odpornosc na sztylety", 31], ["Odpornosc na dzwony", 32], ["Odpornosc na wachlarze", 33], ["Odpornosc na strzaly", 34], ["Odpornosc na ogien", 35,      "Odpornosc na blyskawice", 36], ["Odpornosc na magie", 37], ["Odpornosc na wiatr", 38], ["Szansa na odbicie ataku", 39], ["-", 40], ["-", 41], ["Szansa na odzyskanie PE", 42], ["Exp-Bonus", 43], ["Yang-Drop", 44], ["Item-Drop", 45], ["-", 46], ["Szansa na odzyskanie HP", 47], ["Odporny na Omdlenia", 48], ["Odporny na spowolnienie", 49], ["-", 50], ["-", 51], ["-", 52], ["Wartosc Ataku", 53], ["Obrona", 54], ["-", 55], ["-", 56], ["Max wytrzymalosc", 58], ["Silny przeciwko wojownikom", 59], ["Silny przeciwko ninja", 60], ["Silny przeciwko sura", 61], ["Silny przeciwko szamana", 62], ["Silny przeciwko potworom", 63], ["-", 64], ["-", 65], ["-", 66], ["-", 67], ["-", 68], ["-", 69], ["-", 70], ["Obrazenia Umiejetnosci", 71], ["Srednie Obrazenia", 72], ["-", 73], ["-", 74], ["-", 76], ["-", 77], ["Orpornosc na wojownikow", 78], ["Odpornosc na ninja", 79], ["Odpornosc na sura", 80], ["Odpornosc na szamanow", 81]]
	BonusIDListe = [["keiner", 0], ["Max. TP", 1], ["Max. MP", 2], ["Vitalität", 3], ["Intelligenz", 4], ["Stärke", 5], ["Beweglichkeit", 6], ["Angriffsgeschwindigkeit", 7], ["Bewegungsgeschwindigkeit", 8], ["Zaubergeschwindigkeit", 9], ["TP-Regeneration", 10], ["MP-Regeneration", 11], ["Vergiftungschance", 12], ["Ohnmachtschance", 13], ["Verlangsamungschance", 14], ["Kritischer Treffer", 15], ["Durchbohrender Treffer", 16], ["Stark ggn Halbmenschen", 17], ["Stark ggn Tiere", 18], ["Stark ggn Orks", 19], ["Stark ggn Esoterische", 20], ["Stark ggn Untote", 21], ["Stark ggn Teufel", 22], ["TP-Absorbierung", 23], ["MP-Absorbierung", 24], ["Chance auf Manaraub", 25], ["Chance MP-Regeneration", 26], ["Nahkampf-Angriff blocken", 27], ["Pfeilangriff ausweichen", 28], ["Schwertverteidigung", 29], ["Zweihandverteidigung", 30], ["Dolchverteidigung", 31], ["Glockenverteidigung", 32], ["Fächerverteidigung", 33], ["Pfeilwiderstand", 34], ["Feuerwiderstand", 35,	"Blitzwiderstand", 36], ["Magieverteidigung", 37], ["Windverteidigung", 38], ["Nahkampftreffer reflektieren", 39], ["Fluch reflektieren", 40], ["Giftverteidigung", 41], ["Chance MP wiederherzustellen", 42], ["Exp-Bonus", 43], ["Yang-Drop", 44], ["Item-Drop", 45], ["steigernde Trankwirkung", 46], ["Chance TP wiederherzustellen", 47], ["Immun gegen Ohnmacht", 48], ["Immun gegen Verlangsamung", 49], ["Immun gegen Stürzen", 50], ["APPLY_SKILL", 51], ["Pfeilreichweite", 52], ["Angriffswert", 53], ["Verteidigungswert", 54], ["Magischer Angriffswert", 55], ["Magischer Verteidigungswert", 56], ["Max. Ausdauer", 58], ["Stark gegen Krieger", 59], ["Stark gegen Ninjas", 60], ["Stark gegen Suras", 61], ["Stark gegen Schamanen", 62], ["Stark gegen Monster", 63], ["Itemshop Angriffswert", 64], ["Itemshop Verteidigungswert", 65], ["Itemshop Exp-Bonus", 66], ["Itemshop Item-Bonus", 67], ["Itemshop Yang-Bonus", 68], ["APPLY_MAX_HP_PCT", 69], ["APPLY_MAX_SP_PCT", 70], ["Fertigkeitsschaden", 71], ["Durchschn. Schaden", 72], ["Fertigkeitsschaden Widerstand", 73], ["Durchschn. Schadenswiderstand", 74], ["iCafe EXP-Bonus", 76], ["iCafe Item-Bonus", 77], ["Abwehr ggn Krieger", 78], ["Abwehr ggn Ninjas", 79], ["Abwehr ggn Suras", 80], ["Abwehr ggn Schamanen", 81]]
	SearchBoni = []
	SearchBoniValues = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]
	
	SwitchValue = 71084
	
	State = "Stop"
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
		
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [533, 353], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [493, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Schließen", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.SlotBar, 0], [190, 255], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [15, 65], [["SetViewItemCount", [11]], ["SetItemStep",[20]]], []],			
			[[ui.ScrollBar, 0], [0, 0], [180, 55], [["SetScrollBarSize", [230]]], []],			
			[[ui.TextLine, 0], [0, 0], [10, 39], [["SetDefaultFontName", [""]],	["SetText", ["    Slot:			Name:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],
			[[ui.TextLine, 0], [0, 0], [250, 180], [["SetText", ["Boni"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.TextLine, 0], [0, 0], [410, 180], [["SetText", ["Altern. Boni"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.Line, 0], [310, 0], [210, 195], [["SetColor",[0xff777777]]], []],
			[[ui.Button, 0], [0, 0], [260, 305], [['SetUpVisual', ["m2kmod\Images\start_0.tga"]],['SetOverVisual', ["m2kmod\Images\start_1.tga"]], ['SetDownVisual', ["m2kmod\Images\start_2.tga"]], ['SetEvent', [lambda : self.SwichbotState()]]], []],	
			[[ui.Button, 0], [0, 0], [260, 305], [['SetUpVisual', ["m2kmod\Images\stop_0.tga"]],['SetOverVisual', ["m2kmod\Images\stop_1.tga"]], ['SetDownVisual', ["m2kmod\Images\stop_2.tga"]], ['SetEvent', [lambda : self.SwichbotState()]]], []],	
			[[ui.TextLine, 0], [0, 0], [210, 8], [["SetText", ["Switchbot v3.1.2 by DaRealFreak"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			]
		GuiParser(Gui, self.Gui)
		self.Gui[0].SetPosition(52, 40)
		tmp = []
		y = 37
		texty = 200
		for i in xrange(5):
			button = [[ui.Button, 0], [0, 0], [210, y], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Bonus " + str(i + 1)]], ['SetEvent', [lambda Index = i: self.SelectBonus(Index)]]], []]
			slotbar = [[ui.SlotBar, 0], [35, 18], [310, y], [], []]
			editline = [[ui.EditLine, 13 + i*4], [35, 17], [6, 2], [["SetMax", [4]], ["SetNumberMode", [""]], ["SetText", ["0"]]], []]
			textline = [[ui.TextLine, 0], [0, 0], [220, texty], [["SetText", ["keiner"]]], []]
			tmp.append(button)
			tmp.append(slotbar)
			tmp.append(textline)
			tmp.append(editline)
			y += 30
			texty += 20
		y = 37
		texty = 200
		for i in xrange(5, 10):
			button = [[ui.Button, 0], [0, 0], [370, y], [['SetUpVisual', ["d:/ymir work/ui/public/Large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/Large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/Large_button_03.sub"]], ["SetText", ["Altern. Bonus " + str(i - 5 + 1)]], ['SetEvent', [lambda Index = i: self.SelectBonus(Index)]]], []]
			slotbar = [[ui.SlotBar, 0], [35, 18], [470, y], [], []]
			editline = [[ui.EditLine, 33 + (i-5)*4], [35, 17], [6, 2], [["SetMax", [4]], ["SetNumberMode", [""]], ["SetText", ["0"]]], []]
			textline = [[ui.TextLine, 0], [0, 0], [390, texty], [["SetText", ["keiner"]]], []]
			tmp.append(button)
			tmp.append(slotbar)
			tmp.append(editline)
			tmp.append(textline)
			y += 30
			texty += 20
			
		GuiParser(tmp, self.Gui)
		self.Gui[3].SetScrollBar(self.Gui[4])
		self.UpdateFileList()
		self.Gui[11].SetOutline()
		self.Gui[6].SetOutline()
		self.Gui[7].SetOutline()
		self.Gui[10].Hide()
	
	def SelectBonus(self, Index):
		self.BoniGui = []
		Gui = [
			[[ui.ThinBoard, ""], [223, 353], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [190, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Schließen", 0, - 23]], ['SetEvent', [lambda : self.HideBonusList()]]], []],	
			[[ui.SlotBar, 0], [190, 277], [15, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [20, 65], [], []],			
			[[ui.ScrollBar, 0], [0, 0], [185, 55], [["SetScrollBarSize", [240]]], []],			
			[[ui.TextLine, 0], [0, 0], [15, 39], [["SetDefaultFontName", [""]],	["SetText", ["ID:			Bonus:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],
			[[ui.TextLine, 0], [0, 0], [60, 8], [["SetText", ["Choose Bonus: " + str(Index + 1)]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			[[ui.Button, 0], [0, 0], [20, 325], [['SetUpVisual', ["d:/ymir work/ui/public/large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/large_button_03.sub"]], ["SetText", ["Choose"]], ['SetEvent', [lambda index = Index: self.AddBonus(Index)]]], []],			
			[[ui.Button, 0], [0, 0], [113, 325], [['SetUpVisual', ["d:/ymir work/ui/public/large_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/large_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/large_button_03.sub"]], ["SetText", ["Exit"]], ['SetEvent', [lambda : self.HideBonusList()]]], []],
			]
		GuiParser(Gui, self.BoniGui)
		self.BoniGui[0].SetPosition(587, 40)
		self.BoniGui[3].SetScrollBar(self.BoniGui[4])
		self.BoniGui[3].SetViewItemCount(12)
		self.SetBonusList()


	
	def SwichbotState(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			if self.Swich == 0:
				self.Swich = 1
				self.Gui[9].Hide()
				self.Gui[10].Show()
				self.ChangeState("Start")
			else:
				self.Swich = 0
				self.Gui[10].Hide()
				self.Gui[9].Show()	
				self.ChangeState("Stop")
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
			return
			
		
	def ChangeState(self, state):
		if state == "Start":
			if self.SearchBoni == []:
				chat.AppendChat(1, "Please Choose Bonus first!")
				
			ItemIndex = self.Gui[3].GetSelectedItem()
			if ItemIndex:
				pass
			else:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
				return
			self.Slot = int(ItemIndex.GetText().split("	")[0])
			self.Startmode = 1
			
			for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
				itemVNum = player.GetItemIndex(Slot)
				if itemVNum == self.SwitchValue:
					self.SlotStack = [Slot, player.GetItemCount(Slot)]
					break
					
			self.DefineBoni()
			self.State = "Start"
			
			chat.AppendChat(1, "Switchbot started")
		else:
			self.State = "Stop"
			chat.AppendChat(1, "Switchbot started")

		
	
		
	def AddBonus(self, Index):
		ItemIndex = self.BoniGui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
			return
		BonusValue = ItemIndex.GetText().split("			")
		if int(BonusValue[0]) == 0:
			try:
				if Index > 4:
					BackUp = self.SearchBoni[Index - 5]
					if BackUp[0] == 0:
						self.SearchBoni.remove(self.SearchBoni[Index - 5])
					else:
						self.SearchBoni[Index - 5] = [BackUp[0], 0]
				else:
					BackUp = self.SearchBoni[Index]
					if BackUp[1] == 0:
						self.SearchBoni.remove(self.SearchBoni[Index])
					else:
						self.SearchBoni[Index] = [0, BackUp[1]]
			except:
				pass
		else:
			if Index > 4:
				NewIndex = Index - 5
				try:
					try:
						BackUp = self.SearchBoni[NewIndex]
						self.SearchBoni.remove(self.SearchBoni[NewIndex])
					except:
						Backup = [0, 0]
					self.SearchBoni.insert(NewIndex, [BackUp[0], int(BonusValue[0])])
				except:
					self.SearchBoni.append([0, int(BonusValue[0])])
			else:
				try:
					try:
						BackUp = self.SearchBoni[Index]
						self.SearchBoni.remove(self.SearchBoni[Index])
					except:
						Backup = [0, 0]
					self.SearchBoni.insert(Index,  [int(BonusValue[0]), BackUp[1]])
				except:
					self.SearchBoni.append([int(BonusValue[0]), 0])

		self.UpdateBonusList()
		self.HideBonusList()
		
	def UpdateBonusValues(self):
		TmpValues = []
		for Index in xrange(5):
			try:
				SearchValue = int(self.Gui[15 + (Index)*4].GetText())
			except:
				SearchValue = 0
			try:
				AlternateSearchValue = int(self.Gui[34 + (Index)*4].GetText())
			except:
				AlternateSearchValue = 0
			TmpValues.append([SearchValue, AlternateSearchValue])
			
		if TmpValues != self.SearchBoniValues:
			self.SearchBoniValues = TmpValues
		
	def UpdateBonusList(self):
		tmp = {}
		for Bonus in self.BonusIDListe:
			tmp[Bonus[1]] = Bonus[0]
			
		for Index in xrange(5):
			self.Gui[14 + (Index)*4].SetText("None")
			self.Gui[35 + (Index)*4].SetText("None")			
			
		for Bonus in self.SearchBoni:
			Index = self.SearchBoni.index(Bonus)
			self.Gui[14 + (Index)*4].SetText(tmp[Bonus[0]])
			self.Gui[35 + (Index)*4].SetText(tmp[Bonus[1]])
		
	def SetBonusList(self):
		self.BoniGui[3].RemoveAllItems()
		for Bonus in self.BonusIDListe:
			self.BoniGui[3].AppendItem(Item(str(Bonus[1]) + "			" + Bonus[0]))
		
	def HideBonusList(self):
		self.BoniGui[0].Hide()
		
	def UpdateFileList(self):
		Allow = [item.WEAPON_ARROW, item.WEAPON_FAN, item.WEAPON_BELL, item.WEAPON_TWO_HANDED, item.WEAPON_BOW, item.WEAPON_DAGGER, item.WEAPON_SWORD]
		self.Gui[3].RemoveAllItems()
		





		for i in xrange(101):
			ItemIndex = player.GetItemIndex(i)
			ItemType = item.GetItemType(item.SelectItem(ItemIndex))
			if ItemIndex != 0 and ItemType in Allow:
				item.SelectItem(ItemIndex)
				item.GetItemName(ItemIndex)
				ItemName = item.GetItemName()
				self.Gui[3].AppendItem(Item(str(i) + "	" + ItemName))

		self.UpdateBonusList()
	
	def OnUpdate(self):		
		if self.State == "Stop":
			return
			
		self.UpdateBonusValues()
		self.UpdateBoni()
		
	def ControllBoni(self, Boni, Values):
		try:
			for i in xrange(len(self.SearchBoni)):
				try:
					Index = Boni.index(self.SearchBoni[i][0])
					if Values[Index] < self.SearchBoniValues[i][0]:
						Boni.index("-1")
				except:
					Index = Boni.index(self.SearchBoni[i][1])
					if Values[Index] < self.SearchBoniValues[i][1]:
						Boni.index("-1")				
			self.State = "Stop"
			chat.AppendChat(1, "Boni Count: " + str(self.Count))
			chat.AppendChat(1, "Bonis: " + str(Boni))
			chat.AppendChat(1, "Values: " + str(Values))
		except:
			if player.GetItemCountByVnum(self.SwitchValue) <= 0:
				if shop.IsOpen():
					for EachShopSlot in xrange(shop.SHOP_SLOT_COUNT):
						ShopItemValue = shop.GetItemID(EachShopSlot)
						if ShopItemValue == int(self.SwitchValue):
							net.SendShopBuyPacket(EachShopSlot)
				else:
					chat.AppendChat(1, "No Swichtime in the Inventory")
					self.State = "Stop"
					return
				
			for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemValue = player.GetItemIndex(Slot)
				if ItemValue == self.SwitchValue:
					if self.State == "Stop":
						return
					self.SlotStack = [Slot, player.GetItemCount(Slot)]
					net.SendItemUseToItemPacket(Slot, self.Slot)
					break
					
	def DefineBoni(self):
		self.Values = []
		self.Boni = []
		self.Count = 0
		for AttributeIndex in xrange(5):
			Bonus, Value = player.GetItemAttribute(self.Slot, AttributeIndex)
			if Bonus != 0:
				self.Count += 1
				self.Boni.append(Bonus)
				self.Values.append(Value)
		self.ControllBoni(self.Boni, self.Values)
	
	def UpdateBoni(self):
		if self.State == "Stop":
			return
		Values = []
		Boni = []
		Count = 0
		for AttributeIndex in xrange(self.Count):
			Bonus, Value = player.GetItemAttribute(self.Slot, AttributeIndex)
			if Bonus == 0:
				return
			Count += 1
			Values.append(Value)
			Boni.append(Bonus)
		
		if (player.GetItemCount(self.SlotStack[0]) <= 0 and (self.Boni != Boni or self.Values != Values)) or (self.Boni != Boni or self.Values != Values) or app.GetTime() >= self.LastProcessTimeStamp + 0.8:
			self.LastProcessTimeStamp = app.GetTime()
			self.Boni = Boni
			self.Values = Values
			self.ControllBoni(Boni, Values)

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
#SwitchBotDialog().Show()