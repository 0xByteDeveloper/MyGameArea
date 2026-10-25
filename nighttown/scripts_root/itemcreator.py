import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

CreateBonus0 = 0
CreateBonus1 = 0
CreateBonus2 = 0
CreateBonus3 = 0
CreateBonus4 = 0
CreateWhish0 = 0
CreateWhish1 = 0
CreateWhish2 = 0
CreateWhish3 = 0
CreateWhish4 = 0
FILE_NAME_LEN = 40 
ChangedValue = "FALSE"
ItemValue = 189

BonusListe = (  
	"","Max. TP","Max. MP","Vitalität","Intelligenz","Stärke","Ausweichwert","Angriffsgeschwindigkeit","Bewegungsgeschwindigkeit","Zaubergeschwindigkeit", "TP-Regeneration","MP-Regeneration","Vergiftungschance","Ohnmachtschance","Verlangsamungschance","Kritischer Treffer","Durchbohrender Treffer","Stark ggn Halbmenschen","Stark ggn Tiere","Stark ggn Orks","Stark ggn Esoterische","Stark ggn Untote","Stark ggn Teufel","TP-Absorbierung","MP-Absorbierung","Chance auf Manaraub","Chance MP-Regeneration","Nahkampf-Angriff blocken","Pfeilangriff ausweichen","Schwertverteidigung","Zweihandverteidigung","Dolchverteidigung","Glockenverteidigung","Fächerverteidigung","Pfeilwiderstand","Feuerwiderstand","Blitzwiderstand","Magieverteidigung","Windwiderstand","Nahkampftreffer reflektieren","Fluch reflektieren","Giftwiderstand","Chance MP wiederherzustellen","Exp-Bonus","Yang-Drop","Item-Drop","steigernde Trankwirkung","Chance TP wiederherzustellen","Immun gegen Ohnmacht","Immun gegen Verlangsamung","Immun gegen Stürzen","APPLY_SKILL","Pfeilreichweite","Angriffswert","Verteidigungswert","Magischer Angriffswert","Magischer Verteidigungswert","","Max. Ausdauer","Stark gegen Krieger","Stark gegen Ninjas","Stark gegen Suras","Stark gegen Schamanen","Stark gegen Monster","Itemshop Angriffswert","Itemshop Verteidigungswert","Itemshop Exp-Bonus","Itemshop Item-Bonus","Itemshop Yang-Bonus", "APPLY_MAX_HP_PCT","APPLY_MAX_SP_PCT","Fertigkeitsschaden","Durchschn. Schaden","Fertigkeitsschaden Widerstand","Durchschn. Schadenswiderstand","","iCafe EXP-Bonus","iCafe Item-Bonus","Abwehr ggn Krieger","Abwehr ggn Ninjas","Abwehr ggn Suras","Abwehr ggn Schamanen",
    ) 
BonusIDListe = {  
    "":0,"Max. TP":1,"Max. MP":2,"Vitalität":3,"Intelligenz":4,"Stärke":5,"Ausweichwert":6,"Angriffsgeschwindigkeit":7,"Bewegungsgeschwindigkeit":8,"Zaubergeschwindigkeit":9,"TP-Regeneration":10,"MP-Regeneration":11,"Vergiftungschance":12,"Ohnmachtschance":13,"Verlangsamungschance":14,"Kritischer Treffer":15,"Durchbohrender Treffer":16,"Stark ggn Halbmenschen":17,"Stark ggn Tiere":18,"Stark ggn Orks":19,"Stark ggn Esoterische":20,"Stark ggn Untote":21,"Stark ggn Teufel":22,"TP-Absorbierung":23,"TP-Absorbierung":23,"MP-Absorbierung":24,"Chance auf Manaraub":25,"Chance MP-Regeneration":26,"Nahkampf-Angriff blocken":27,"Pfeilangriff ausweichen":28,"Schwertverteidigung":29,"Zweihandverteidigung":30,"Dolchverteidigung":31,"Glockenverteidigung":32,"Fächerverteidigung":33,"Pfeilwiderstand":34,"Feuerwiderstand":35,"Blitzwiderstand":36,"Magieverteidigung":37,"Windverteidigung":38,"Nahkampftreffer reflektieren":39,"Fluch reflektieren":40,"Giftwiderstand":41,"Chance MP wiederherzustellen":42,"Exp-Bonus":43,"Yang-Drop":44,"Item-Drop":45,"steigernde Trankwirkung":46,"Chance TP wiederherzustellen":47,"Immun gegen Ohnmacht":48,"Immun gegen Verlangsamung":49,"Immun gegen Stürzen":50,"APPLY_SKILL":51,"Pfeilreichweite":52,"Angriffswert":53,"Verteidigungswert":54,"Magischer Angriffswert":55, "Magischer Verteidigungswert":56,"":57,"Max. Ausdauer":58,"Stark gegen Krieger":59,"Stark gegen Ninjas":60,"Stark gegen Suras":61,"Stark gegen Schamanen":62,"Stark gegen Monster":63,"Itemshop Angriffswert":64,"Itemshop Verteidigungswert":65,"Itemshop Exp-Bonus":66,"Itemshop Item-Bonus":67,"Itemshop Yang-Bonus":68,"APPLY_MAX_HP_PCT":69,"APPLY_MAX_SP_PCT":70,"Fertigkeitsschaden":71,"Durchschn. Schaden":72, "Fertigkeitsschaden Widerstand":73,"Durchschn. Schadenswiderstand":74,"":75,"iCafe EXP-Bonus":76,"iCafe Item-Bonus":77,"Abwehr ggn Krieger":78,"Abwehr ggn Ninjas":79,"Abwehr ggn Suras":80,"Abwehr ggn Schamanen":81,
	}
class CreateItemDialog(ui.Window):

	ENABLE_COLOR = grp.GenerateColor(0.7607, 0.7607, 0.7607, 1.0)
	DISABLE_COLOR = grp.GenerateColor(0.9, 0.4745, 0.4627, 1.0)

	def __init__(self):
		ui.Window.__init__(self)

		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(350, 335)
		self.Board.SetCenterPosition()
		self.Board.AddFlag("movable")
		self.Board.AddFlag("float")
		self.Board.SetTitleName("Item Creator")
		self.Board.SetCloseEvent(self.Board.Hide)
		self.Board.Show()
		
		self.MetinStone1 = 28433
		self.MetinStone2 = 28434
		self.MetinStone3 = 28435

		self.AddTextLines()
		self.AddImages()
		self.AddSlotBars()
		
	def __del__(self):
		ui.Window.__del__(self)

	def AddSlotBars(self):
		return
		
	def AddImages(self):
		self.comp = Component()
		self.Metin1Button = self.comp.Button(self.Board, 'Set', '', 285, 85, self.SetMetin1, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.Metin2Button = self.comp.Button(self.Board, 'Set', '', 285, 120, self.SetMetin2, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.Metin3Button = self.comp.Button(self.Board, 'Set', '', 285, 155, self.SetMetin3, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		
		self.Metin1SlotBar, self.Metin1EditLine = self.comp.SlotBarEditLine(self.Board, (str(self.MetinStone1)), 240, 88, 35, 14, 5)
		self.Metin2SlotBar, self.Metin2EditLine = self.comp.SlotBarEditLine(self.Board, (str(self.MetinStone2)), 240, 123, 35, 14, 5)
		self.Metin3SlotBar, self.Metin3EditLine = self.comp.SlotBarEditLine(self.Board, (str(self.MetinStone3)), 240, 158, 35, 14, 5)
		
		global ItemValue
		item.SelectItem(int(ItemValue))
		ItemIcon = item.GetIconImageFileName()
		self.ItemImage = ui.ExpandedImageBox()
		self.ItemImage.SetParent(self.Board)
		self.ItemImage.SetPosition(17, 65 + 15)
		self.ItemImage.LoadImage(str(ItemIcon))
		self.ItemImage.Show()
		
		self.ItemNameText = ui.TextLine()
		self.ItemNameText.SetParent(self.Board)
		self.ItemNameText.SetDefaultFontName()
		self.ItemNameText.SetPosition(15, 55)
		self.ItemNameText.SetFeather()
		self.ItemNameText.SetText(str(item.GetItemName()))
		for i in xrange(0,1):
			(ItemTypeLimit, ItemLevelLimit) = item.GetLimit(i)
			if item.LIMIT_LEVEL == ItemTypeLimit:
				if player.GetStatus(player.LEVEL) < ItemLevelLimit:
					self.ItemNameText.SetPackedFontColor(self.DISABLE_COLOR)
				else:
					self.ItemNameText.SetPackedFontColor(self.ENABLE_COLOR)
		self.ItemNameText.SetOutline()
		self.ItemNameText.Show()

		self.Metin1Image = ui.ExpandedImageBox()
		self.Metin1Image.SetParent(self.Board)
		self.Metin1Image.SetPosition(65, 65 + 15)
		if int(self.MetinStone1) != 0:
			item.SelectItem(int(self.MetinStone1))
			ItemIcon = item.GetIconImageFileName()
			self.Metin1Image.LoadImage(str(ItemIcon))
		self.Metin1Image.Show()

		self.Metin1Text = ui.TextLine()
		self.Metin1Text.SetParent(self.Board)
		self.Metin1Text.SetDefaultFontName()
		self.Metin1Text.SetPosition(105, 65 + 23)
		self.Metin1Text.SetFeather()
		if int(self.MetinStone1) != 0:
			self.Metin1Text.SetText(str(item.GetItemName()))
		else:
			self.Metin1Text.SetText("Metinstein 1")			
		self.Metin1Text.SetFontColor(1.0, 1.0, 1.0)
		self.Metin1Text.SetOutline()
		self.Metin1Text.Show()	
		
		self.Metin2Image = ui.ExpandedImageBox()
		self.Metin2Image.SetParent(self.Board)
		self.Metin2Image.SetPosition(65, 100 + 15)
		if int(self.MetinStone2) != 0:
			item.SelectItem(int(self.MetinStone2))
			ItemIcon = item.GetIconImageFileName()
			self.Metin2Image.LoadImage(str(ItemIcon))
		self.Metin2Image.Show()

		self.Metin2Text = ui.TextLine()
		self.Metin2Text.SetParent(self.Board)
		self.Metin2Text.SetDefaultFontName()
		self.Metin2Text.SetPosition(105, 100 + 23)
		self.Metin2Text.SetFeather()
		if int(self.MetinStone2) != 0:
			self.Metin2Text.SetText(str(item.GetItemName()))
		else:
			self.Metin2Text.SetText("Metinstein 2")			
		self.Metin2Text.SetFontColor(1.0, 1.0, 1.0)
		self.Metin2Text.SetOutline()
		self.Metin2Text.Show()	

		self.Metin3Image = ui.ExpandedImageBox()
		self.Metin3Image.SetParent(self.Board)
		self.Metin3Image.SetPosition(65, 135 + 15)		
		if int(self.MetinStone3) != 0:
			item.SelectItem(int(self.MetinStone3))
			ItemIcon = item.GetIconImageFileName()
			self.Metin3Image.LoadImage(str(ItemIcon))
		self.Metin3Image.Show()
		
		self.Metin3Text = ui.TextLine()
		self.Metin3Text.SetParent(self.Board)
		self.Metin3Text.SetDefaultFontName()
		self.Metin3Text.SetPosition(105, 135 + 23)
		self.Metin3Text.SetFeather()
		if int(self.MetinStone3) != 0:
			self.Metin3Text.SetText(str(item.GetItemName()))
		else:
			self.Metin3Text.SetText("Stone 3")			
		self.Metin3Text.SetFontColor(1.0, 1.0, 1.0)
		self.Metin3Text.SetOutline()
		self.Metin3Text.Show()	
		
		
	def SetMetin1(self):
		self.MetinStone1 = int(self.Metin1EditLine.GetText())
		item.SelectItem(int(self.MetinStone1))
		ItemIcon = item.GetIconImageFileName()
		self.Metin1Image.LoadImage(str(ItemIcon))
		if int(self.MetinStone1) != 0:
			self.Metin1Text.SetText(str(item.GetItemName()))
		else:
			self.Metin1Text.SetText("Metinstein 1")			
	
	def SetMetin2(self):
		self.MetinStone2 = int(self.Metin2EditLine.GetText())
		item.SelectItem(int(self.MetinStone2))
		ItemIcon = item.GetIconImageFileName()
		self.Metin2Image.LoadImage(str(ItemIcon))
		if int(self.MetinStone2) != 0:
			self.Metin2Text.SetText(str(item.GetItemName()))
		else:
			self.Metin2Text.SetText("Metinstein 2")			
	
	def SetMetin3(self):
		self.MetinStone3 = int(self.Metin3EditLine.GetText())
		item.SelectItem(int(self.MetinStone3))
		ItemIcon = item.GetIconImageFileName()
		self.Metin3Image.LoadImage(str(ItemIcon))		
		if int(self.MetinStone2) != 0:
			self.Metin3Text.SetText(str(item.GetItemName()))
		else:
			self.Metin3Text.SetText("Metinstein 3")			
		
	def SetItemValue(self):
		global ItemValue
		ItemValue = int(self.ItemValueEditLine.GetText())
		item.SelectItem(int(ItemValue))
		ItemIcon = item.GetIconImageFileName()
		self.ItemImage.LoadImage(str(ItemIcon))
		self.ItemNameText.SetText(str(item.GetItemName()))
		for i in xrange(0,1):
			(ItemTypeLimit, ItemLevelLimit) = item.GetLimit(i)
			if item.LIMIT_LEVEL == ItemTypeLimit:
				if player.GetStatus(player.LEVEL) < ItemLevelLimit:
					self.ItemNameText.SetPackedFontColor(self.DISABLE_COLOR)
				else:
					self.ItemNameText.SetPackedFontColor(self.ENABLE_COLOR)	
		
	def AddTextLines(self):
		global ItemValue
		self.comp = Component()
		self.CreateItemButton = self.comp.Button(self.Board, 'Create Item', '', 40, 295, self.CreateItem, 'd:/ymir work/ui/public/xlarge_Button_01.sub', 'd:/ymir work/ui/public/xlarge_Button_02.sub', 'd:/ymir work/ui/public/xlarge_Button_03.sub')
		self.SetItemValueButton = self.comp.Button(self.Board, 'Set', '', 110, 33, self.SetItemValue, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.CallItemListButton = self.comp.Button(self.Board, 'Itemlist', '', 155, 33, self.CallItemList, 'd:/ymir work/ui/public/middle_Button_01.sub', 'd:/ymir work/ui/public/middle_Button_02.sub', 'd:/ymir work/ui/public/middle_Button_03.sub')
		self.Bonus1Button = self.comp.Button(self.Board, 'Choose Bonus 1', '', 240, 185, self.OpenBonusList1, 'd:/ymir work/ui/public/large_Button_01.sub', 'd:/ymir work/ui/public/large_Button_02.sub', 'd:/ymir work/ui/public/large_Button_03.sub')
		self.Bonus2Button = self.comp.Button(self.Board, 'Choose Bonus 2', '', 240, 205, self.OpenBonusList2, 'd:/ymir work/ui/public/large_Button_01.sub', 'd:/ymir work/ui/public/large_Button_02.sub', 'd:/ymir work/ui/public/large_Button_03.sub')
		self.Bonus3Button = self.comp.Button(self.Board, 'Choose Bonus 3', '', 240, 225, self.OpenBonusList3, 'd:/ymir work/ui/public/large_Button_01.sub', 'd:/ymir work/ui/public/large_Button_02.sub', 'd:/ymir work/ui/public/large_Button_03.sub')
		self.Bonus4Button = self.comp.Button(self.Board, 'Choose Bonus 4', '', 240, 245, self.OpenBonusList4, 'd:/ymir work/ui/public/large_Button_01.sub', 'd:/ymir work/ui/public/large_Button_02.sub', 'd:/ymir work/ui/public/large_Button_03.sub')
		self.Bonus5Button = self.comp.Button(self.Board, 'Choose Bonus 5', '', 240, 265, self.OpenBonusList5, 'd:/ymir work/ui/public/large_Button_01.sub', 'd:/ymir work/ui/public/large_Button_02.sub', 'd:/ymir work/ui/public/large_Button_03.sub')
		
		self.copyright = self.comp.TextLine(self.Board, 'by DaRealFreak', 250, 300, self.comp.RGB(255, 255, 0))
		self.ItemValueText = self.comp.TextLine(self.Board, 'Itemvalue:', 15, 35, self.comp.RGB(255, 255, 255))
		self.ItemCountText = self.comp.TextLine(self.Board, 'Itemcount:', 230, 35, self.comp.RGB(255, 255, 255))
		self.Bonus1Text = self.comp.TextLine(self.Board, 'Bonus 1:', 15, 190, self.comp.RGB(255, 255, 255))
		self.Bonus1AtrText = self.comp.TextLine(self.Board, '-', 65, 190, self.comp.RGB(255, 255, 255)) 
		self.Bonus2Text = self.comp.TextLine(self.Board, 'Bonus 2:', 15, 210, self.comp.RGB(255, 255, 255))
		self.Bonus2AtrText = self.comp.TextLine(self.Board, '-', 65, 210, self.comp.RGB(255, 255, 255)) 
		self.Bonus3Text = self.comp.TextLine(self.Board, 'Bonus 3:', 15, 230, self.comp.RGB(255, 255, 255))
		self.Bonus3AtrText = self.comp.TextLine(self.Board, '-', 65, 230, self.comp.RGB(255, 255, 255)) 
		self.Bonus4Text = self.comp.TextLine(self.Board, 'Bonus 4:', 15, 250, self.comp.RGB(255, 255, 255))
		self.Bonus4AtrText = self.comp.TextLine(self.Board, '-', 65, 250, self.comp.RGB(255, 255, 255)) 
		self.Bonus5Text = self.comp.TextLine(self.Board, 'Bonus 5:', 15, 270, self.comp.RGB(255, 255, 255))
		self.Bonus5AtrText = self.comp.TextLine(self.Board, '-', 65, 270, self.comp.RGB(255, 255, 255)) 
		
		self.ItemCountEditLine = self.comp.EditLine(self.Board, 21, 18, 290, 35, '1', 3)
		self.Bonus1ValueEditLine = self.comp.EditLine(self.Board, 29, 18, 211, 190, '0', 4)
		self.Bonus2ValueEditLine = self.comp.EditLine(self.Board, 29, 18, 211, 210, '0', 4)
		self.Bonus3ValueEditLine = self.comp.EditLine(self.Board, 29, 18, 211, 230, '0', 4)
		self.Bonus4ValueEditLine = self.comp.EditLine(self.Board, 29, 18, 211, 250, '0', 4)
		self.Bonus5ValueEditLine = self.comp.EditLine(self.Board, 29, 18, 211, 270, '0', 4)
		self.ItemValueSlotBar, self.ItemValueEditLine = self.comp.SlotBarEditLine(self.Board, (str(ItemValue)), 70, 35, 35, 14, 5)
		
		self.Bonus1ValueEditLine.SetTabEvent(ui.__mem_func__(self.Bonus2ValueEditLine.SetFocus))
		self.Bonus1ValueEditLine.SetReturnEvent(ui.__mem_func__(self.Bonus2ValueEditLine.SetFocus))
		self.Bonus2ValueEditLine.SetTabEvent(ui.__mem_func__(self.Bonus3ValueEditLine.SetFocus))
		self.Bonus2ValueEditLine.SetReturnEvent(ui.__mem_func__(self.Bonus3ValueEditLine.SetFocus))
		self.Bonus3ValueEditLine.SetTabEvent(ui.__mem_func__(self.Bonus4ValueEditLine.SetFocus))
		self.Bonus3ValueEditLine.SetReturnEvent(ui.__mem_func__(self.Bonus4ValueEditLine.SetFocus))
		self.Bonus4ValueEditLine.SetTabEvent(ui.__mem_func__(self.Bonus5ValueEditLine.SetFocus))
		self.Bonus4ValueEditLine.SetReturnEvent(ui.__mem_func__(self.Bonus5ValueEditLine.SetFocus))
		
	def OpenBonusList1(self):
		global CreateWhish0
		CreateWhish0 = 1
		self.CreateBonusListBox = CreateListDialog()
	def OpenBonusList2(self):
		global CreateWhish1
		CreateWhish1 = 1
		self.CreateBonusListBox = CreateListDialog()
	def OpenBonusList3(self):
		global CreateWhish2
		CreateWhish2 = 1
		self.CreateBonusListBox = CreateListDialog()
	def OpenBonusList4(self):
		global CreateWhish3
		CreateWhish3 = 1
		self.CreateBonusListBox = CreateListDialog()
	def OpenBonusList5(self):
		global CreateWhish4
		CreateWhish4 = 1
		self.CreateBonusListBox = CreateListDialog()
		
	def Close(self):
		self.Board = None
		
	def OnUpdate(self):
		global CreateBonus0
		global CreateBonus1
		global CreateBonus2
		global CreateBonus3
		global CreateBonus4
		global ItemValue
		global ChangedValue
		
		if int(ItemValue) != int(self.ItemValueEditLine.GetText()) and ChangedValue == "TRUE":
			self.ItemValueEditLine.SetText(str(ItemValue))
			ChangedValue = "FALSE"
			self.SetItemValue()
		
		if self.Bonus1AtrText.GetText() != str(BonusListe[int(CreateBonus0)]) and int(CreateBonus0) != 0:
			self.Bonus1AtrText.SetText(str(BonusListe[int(CreateBonus0)]))
		elif self.Bonus1AtrText.GetText() != "" and int(CreateBonus0) == 0:
			self.Bonus1AtrText.SetText("-")		
		if self.Bonus2AtrText.GetText() != str(BonusListe[int(CreateBonus1)]) and int(CreateBonus1) != 0:
			self.Bonus2AtrText.SetText(str(BonusListe[int(CreateBonus1)]))
		elif self.Bonus2AtrText.GetText() != "" and int(CreateBonus1) == 0:
			self.Bonus2AtrText.SetText("-")		
		if self.Bonus3AtrText.GetText() != str(BonusListe[int(CreateBonus2)]) and int(CreateBonus2) != 0:
			self.Bonus3AtrText.SetText(str(BonusListe[int(CreateBonus2)]))
		elif self.Bonus3AtrText.GetText() != "" and int(CreateBonus2) == 0:
			self.Bonus3AtrText.SetText("-")		
		if self.Bonus4AtrText.GetText() != str(BonusListe[int(CreateBonus3)]) and int(CreateBonus3) != 0:
			self.Bonus4AtrText.SetText(str(BonusListe[int(CreateBonus3)]))
		elif self.Bonus4AtrText.GetText() != "" and int(CreateBonus3) == 0:
			self.Bonus4AtrText.SetText("-")		
		if self.Bonus5AtrText.GetText() != str(BonusListe[int(CreateBonus4)]) and int(CreateBonus4) != 0:
			self.Bonus5AtrText.SetText(str(BonusListe[int(CreateBonus4)]))
		elif self.Bonus5AtrText.GetText() != "" and int(CreateBonus4) == 0:
			self.Bonus5AtrText.SetText("-")
			
		
		
	def CreateItem(self):
		global CreateBonus0,CreateBonus1,CreateBonus2,CreateBonus3,CreateBonus4,ItemValue
		self.ItemCount = int(self.ItemCountEditLine.GetText())
		Value0 = self.Bonus1ValueEditLine.GetText()
		Value1 = self.Bonus2ValueEditLine.GetText()
		Value2 = self.Bonus3ValueEditLine.GetText()
		Value3 = self.Bonus4ValueEditLine.GetText()
		Value4 = self.Bonus5ValueEditLine.GetText()
		
		for slot in xrange(player.INVENTORY_SLOT_COUNT):
			state = "go"
			if not player.isItem(int(slot)):
				if int(slot) >= 5:
					if player.isItem(int(slot) - 5):
						itemIndex = player.GetItemIndex(int(slot) - 5)
						item.SelectItem(itemIndex)
						if int(item.GetItemSize()[1]) >= 2:
							state = "banned"
			else:
				state = "banned"
			if str(state) == "go":
				player.SetItemData(int(slot), int(ItemValue),int(self.ItemCount))
				player.SetItemAttribute(int(slot), 0, int(CreateBonus0), int(Value0))
				player.SetItemAttribute(int(slot), 1, int(CreateBonus1), int(Value1))
				player.SetItemAttribute(int(slot), 2, int(CreateBonus2), int(Value2))
				player.SetItemAttribute(int(slot), 3, int(CreateBonus3), int(Value3))
				player.SetItemAttribute(int(slot), 4, int(CreateBonus4), int(Value4))
				player.SetItemMetinSocket(int(slot), 0, int(self.MetinStone1))
				player.SetItemMetinSocket(int(slot), 1, int(self.MetinStone2))
				player.SetItemMetinSocket(int(slot), 2, int(self.MetinStone3))
				break

	def CallItemList(self):
		self.ItemListDialog = ItemListDialog()		
class ItemListDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(170, 335)
		self.Board.SetPosition(400, 40)
	#	self.Board.AddFlag("movable")
	#	self.Board.AddFlag("float")
		self.Board.SetTitleName("Item List")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Show()
		
		self.__Load_BindObject()

		self.UpdateFileList()
		
	def __del__(self):
		ui.Window.__del__(self)

	def Show(self):
		ui.Window.Show(self)

	def Close(self):
		self.Board.Hide()

	def OnPressEscapeKey(self):
		self.Board.Close()
		return TRUE

	def __CreateFileListBox(self):
		fileListBox = ui.ListBoxEx()
		fileListBox.SetParent(self.Board)
		fileListBox.SetPosition(15, 80)
		fileListBox.Show()
		return fileListBox

	def __Load_BindObject(self):
		self.fileListBox = self.__CreateFileListBox()
		self.LoadFuckingScrollBar()
		self.fileListBox.SetScrollBar(self.ScrollBar)
		
		self.comp = Component()
		self.SelectBonus = self.comp.Button(self.Board, 'OK', '', 19, 295, self.SetBonis, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.CancelBonus = self.comp.Button(self.Board, 'Cancel', '', 89, 295, self.Close, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SearchItemButton = self.comp.Button(self.Board, 'Search', '', 117, 48, self.SearchItem, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.ItemValueText = self.comp.TextLine(self.Board, 'Search Item:', 19, 33, self.comp.RGB(255, 255, 255))
	
		self.SearchItemSlotBar = ui.SlotBar()
		self.SearchItemSlotBar.SetParent(self.Board)
		self.SearchItemSlotBar.SetSize(15*7, 14)
		self.SearchItemSlotBar.SetPosition(15, 50)
		self.SearchItemSlotBar.Show()
		self.SearchItemEditLine = ui.EditLine()
		self.SearchItemEditLine.SetParent(self.SearchItemSlotBar)
		self.SearchItemEditLine.SetSize(15*7, 18)
		self.SearchItemEditLine.SetPosition(3, 0)
		self.SearchItemEditLine.SetMax(16)
		self.SearchItemEditLine.SetText("")
		self.SearchItemEditLine.SetFocus()
		self.SearchItemEditLine.Show()		

	def LoadFuckingScrollBar(self):
		self.ScrollBar = ui.ScrollBar()
		self.ScrollBar.SetParent(self.Board)
		self.ScrollBar.SetPosition(140, 70)
		self.ScrollBar.SetScrollBarSize(220)
		self.ScrollBar.Show()

	def CancelGuildName(self):
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return TRUE

	def SearchItem(self):
		self.__RefreshFileList()
		SearchName = str(self.SearchItemEditLine.GetText())
		try:
			lines = pack_open("locale/de/item_list.txt", "r").readlines()
		except IOError:
			import dbg
			dbg.LogBox("Load Itemlist Error")
			app.Abort()

		for line in lines:
			tokens = str(line).split("\t")
			if len(tokens) == 0 or not tokens[0]:
				continue
				
			ItemValue = str(tokens[0])
			if str(ItemValue).find(" ") != -1:
				ItemValue = str(ItemValue).replace(" ", "")
			item.SelectItem(int(ItemValue))
			Itemname = str(item.GetItemName())
			if ItemValue and str(Itemname) != "":
				if str(Itemname).find(str(SearchName)) != -1:
					self.fileListBox.AppendItem(Item(Itemname))
		
	def UpdateFileList(self):
		self.__RefreshFileList()
		try:
			lines = pack_open("locale/de/item_list.txt", "r").readlines()
		except IOError:
			import dbg
			dbg.LogBox("Load Itemlist Error")
			app.Abort()

		for line in lines:
			tokens = str(line).split("\t")
			if len(tokens) == 0 or not tokens[0]:
				continue
				
			ItemValue = str(tokens[0])
			if str(ItemValue).find(" ") != -1:
				ItemValue = str(ItemValue).replace(" ", "")
			item.SelectItem(int(ItemValue))
			Itemname = str(item.GetItemName())
			if ItemValue and str(Itemname) != "":
				self.fileListBox.AppendItem(Item(Itemname))
		
	def __RefreshFileList(self):
		self.fileListBox.RemoveAllItems()
		
	def SetBonis(self):
		global ItemValue
		global ChangedValue
		SelectedIndex = self.fileListBox.GetSelectedItem()
		SelectedIndex = SelectedIndex.GetText()
		try:
			lines = pack_open("locale/de/item_list.txt", "r").readlines()
		except IOError:
			import dbg
			dbg.LogBox("Load Itemlist Error")
			app.Abort()

		for line in lines:
			tokens = str(line).split("\t")
			if len(tokens) == 0 or not tokens[0]:
				continue
				
			Itemvalue = str(tokens[0])
			if str(Itemvalue).find(" ") != -1:
				Itemvalue = str(Itemvalue).replace(" ", "")
			item.SelectItem(int(Itemvalue))
			Itemname = str(item.GetItemName())
			if str(Itemname) == str(SelectedIndex):
				ItemValue = int(Itemvalue)
				break
		ChangedValue = "TRUE"
		self.Close()
class CreateListDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		self.isLoaded=0
		self.selectEvent=None
		self.fileListBox=None
		
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(170, 335)
		self.Board.SetPosition(400, 40)
		self.Board.SetTitleName("Choose Bonus")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Show()
		
		self.__Load()
		
	def __del__(self):
		ui.Window.__del__(self)

	def Show(self):
		if self.isLoaded==0:
			self.isLoaded=1
			self.__Load()
		ui.Window.Show(self)

	def Open(self):	
		self.Show()

		self.SetCenterPosition()
		self.SetTop()
		self.UpdateFileList()

	def Close(self):
		self.Board.Hide()

	def OnPressEscapeKey(self):
		self.Close()
		return TRUE

	def __CreateFileListBox(self):
		fileListBox = ui.ListBoxEx()
		fileListBox.SetParent(self.Board)
		fileListBox.SetPosition(15, 50)
		fileListBox.Show()
		return fileListBox

	def __Load(self):
		self.__Load_BindObject()

		self.UpdateFileList()

	def __Load_BindObject(self):
		self.fileListBox = self.__CreateFileListBox()
		self.LoadFuckingScrollBar()
		self.fileListBox.SetScrollBar(self.ScrollBar)
		
		self.comp = Component()
		self.SelectBonus = self.comp.Button(self.Board, 'OK', '', 19, 265, self.SetBonis, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')	
		self.CancelBonus = self.comp.Button(self.Board, 'Cancel', '', 89, 265, self.Close, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.copyright = self.comp.TextLine(self.Board, 'by DaRealFreak', 50, 300, self.comp.RGB(255, 255, 0))

	def LoadFuckingScrollBar(self):
		self.ScrollBar = ui.ScrollBar()
		self.ScrollBar.SetParent(self.Board)
		self.ScrollBar.SetPosition(140, 40)
		self.ScrollBar.SetScrollBarSize(220)
		self.ScrollBar.Show()

	def CancelGuildName(self):
		self.guildNameBoard.Close()
		self.guildNameBoard = None
		return TRUE

	def UpdateFileList(self):
		self.__RefreshFileList()
		for BonusType in BonusListe:
			if BonusType == "":
				self.fileListBox.AppendItem(Item("keiner"))
			elif BonusType != "":
				self.fileListBox.AppendItem(Item(BonusType))
			#chat.AppendChat(chat.CHAT_TYPE_INFO, str(BonusIDListe[BonusType]))		
		
	def __RefreshFileList(self):
		self.fileListBox.RemoveAllItems()
		
	def SetBonis(self):
		global CreateBonus0
		global CreateBonus1
		global CreateBonus2
		global CreateBonus3
		global CreateBonus4
		global CreateWhish0
		global CreateWhish1
		global CreateWhish2
		global CreateWhish3
		global CreateWhish4
		SelectedIndex = self.fileListBox.GetSelectedItem()
		SelectedIndex = SelectedIndex.GetText()
		if str(SelectedIndex) != "keiner" and str(SelectedIndex) != "":
			if CreateWhish0 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "1.Bonus " + str(SelectedIndex))
				CreateBonus0 = BonusIDListe[str(SelectedIndex)]
				CreateWhish0 = 0
			elif CreateWhish1 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "2.Bonus " + str(SelectedIndex))
				CreateBonus1 = int(BonusIDListe[SelectedIndex])
				CreateWhish1 = 0
			elif CreateWhish2 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "3.Bonus " + str(SelectedIndex))
				CreateBonus2 = int(BonusIDListe[SelectedIndex])
				CreateWhish2 = 0
			elif CreateWhish3 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "4.Bonus " + str(SelectedIndex))
				CreateBonus3 = int(BonusIDListe[SelectedIndex])
				CreateWhish3 = 0
			elif CreateWhish4 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "5.Bonus " + str(SelectedIndex))
				CreateBonus4 = int(BonusIDListe[SelectedIndex])
				CreateWhish4 = 0
				
		elif str(SelectedIndex) == "keiner" and str(SelectedIndex) != "":
			if CreateWhish0 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "1.Bonus wurde gelöscht")
				CreateBonus0 = 0
				CreateWhish0 = 0
			elif CreateWhish1 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "2.Bonus wurde gelöscht")
				CreateBonus1 = 0
				CreateWhish1 = 0
			elif CreateWhish2 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "3.Bonus wurde gelöscht")
				CreateBonus2 = 0
				CreateWhish2 = 0
			elif CreateWhish3 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "4.Bonus wurde gelöscht")
				CreateBonus3 = 0
				CreateWhish3 = 0
			elif CreateWhish4 == 1:
				chat.AppendChat(chat.CHAT_TYPE_INFO, "5.Bonus wurde gelöscht")
				CreateBonus4 = 0
				CreateWhish4 = 0	
				
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "No Bonus Choosed!")		
		self.Board.Close()

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
		Slider.SetSliderPos(sliderPos / 100)
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
		Value.SetNumberMode()
		Value.Show()
		return SlotBar, Value
#CreateItemDialog().Show()