import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,wndMgr,math,uiCommon,grp
WeaponValue = 189
ArmorValue = 12019
ChangedWeapon = "FALSE"
ChangedArmor = "FALSE"	
class EQChangerItemDialog(ui.Window):

	def __init__(self):
		ui.Window.__init__(self)

		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(200, 160)
		self.Board.SetPosition(52, 40)
	#	self.Board.AddFlag("movable")
	#	self.Board.AddFlag("float")
		self.Board.SetTitleName("EQ-Changer")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Show()
		
		self.BuildWindow()
		
	def __del__(self):
		ui.Window.__del__(self)
		
	def Close(self):
		self.Board = None
		
	def BuildWindow(self):
		self.comp = Component()
		self.ChangeEQButton = self.comp.Button(self.Board, 'Change Equipment', '', 10, 120, self.ChangeEQ, 'd:/ymir work/ui/public/xlarge_Button_01.sub', 'd:/ymir work/ui/public/xlarge_Button_02.sub', 'd:/ymir work/ui/public/xlarge_Button_03.sub')
		self.SetWeaponButton = self.comp.Button(self.Board, 'Set', '', 145, 36, self.Weapon, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.SetArmorButton = self.comp.Button(self.Board, 'Set', '', 145, 63, self.Armor, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.GmOnButton = self.comp.Button(self.Board, 'On', '', 90, 90, self.GMEffectOn, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.GmOffButton = self.comp.Button(self.Board, 'Off', '', 145, 90, self.GMEffectOff, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		
		self.WeaponValueText = self.comp.TextLine(self.Board, 'WeaponValue:', 15, 38, self.comp.RGB(255, 255, 0))
		self.ArmorValueText = self.comp.TextLine(self.Board, 'ArmorValue:', 15, 65, self.comp.RGB(255, 255, 0))
		self.GMOn = self.comp.TextLine(self.Board, 'GM-Clientside:', 15, 92, self.comp.RGB(255, 255, 0))
	#	self.WeaponEditLine = self.comp.TextLine(self.Board, '189', 90, 38, self.comp.RGB(255, 255, 255))
	#	self.ArmorEditLine = self.comp.TextLine(self.Board, '12019', 90, 65, self.comp.RGB(255, 255, 255))
		self.WeaponSlotBar, self.WeaponEditLine = self.comp.SlotBarEditLine(self.Board, "189", 90, 38, 35, 14, 5)
		self.ArmorValueSlotBar, self.ArmorEditLine = self.comp.SlotBarEditLine(self.Board, "12019", 90, 65, 35, 14, 5)
		
	def ChangeEQ(self):
		
		Waffe = self.WeaponEditLine.GetText()
		Russi = self.ArmorEditLine.GetText()
		
		chr.SetWeapon(int(Waffe))
		chr.SetArmor(int(Russi))
	
#	def OnUpdate(self):
#	
#		global WeaponValue,ChangedWeapon
#		global ArmorValue,ChangedArmor
#	
	#	if int(WeaponValue) != int(self.WeaponEditLine.GetText()) and ChangedWeapon == "TRUE":
#			self.WeaponEditLine.SetText(str(WeaponValue))
#			ChangedWeapon = "FALSE"	
##		if int(ArmorValue) != int(self.ArmorEditLine.GetText()) and ChangedArmor == "TRUE":
	#		self.WeaponEditLine.SetText(str(ArmorValue))
	#		ChangedArmor = "FALSE"	
	
	def Weapon(self):
		self.ItemListDialog = ItemListDialog()	
	def Armor(self):
		self.ItemListDialog = ItemListDialog()	

	def GMEffectOn(self):
		name = chr.GetName()
		namegm = ("[GM]" + name)
		chrmgr.SetAffect(-1,0,1)
		chr.SetNameString(namegm)
		namegm = namegm.replace("[GM]", "")
	def GMEffectOff(self):
		name = chr.GetName()
		name = name.replace("[GM]", "")
		chrmgr.SetAffect(-1,0,0)
		chr.SetNameString(name)	
class ItemListDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)

		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(170, 335)
		self.Board.SetPosition(250, 100)
		self.Board.SetTitleName("Information - Item ID")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Show()
		
		self.__Load_BindObject()

		
	def __del__(self):
		ui.Window.__del__(self)

	def Show(self):
		ui.Window.Show(self)

	def Close(self):
		self.Board.Hide()

	def OnPressEscapeKey(self):
		self.Board.Close()
		return TRUE


	def __Load_BindObject(self):
		
		
		self.comp = Component()
	#	self.SelectBonus = self.comp.Button(self.Board, 'OK', '', 19, 295, self.Test, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.CancelBonus = self.comp.Button(self.Board, 'Cancel', '', 50, 295, self.Close, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SearchItemButton = self.comp.Button(self.Board, 'German', '', 20, 45, self.German, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SearchItemButton1 = self.comp.Button(self.Board, 'English', '', 90, 45, self.English, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SearchItemButton2 = self.comp.Button(self.Board, 'Romanian ', '', 20, 70, self.Romanian, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SearchItemButton3 = self.comp.Button(self.Board, 'Turkish', '', 90, 70, self.Turkey, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.ItemValueText = self.comp.TextLine(self.Board, ' ', 19, 33, self.comp.RGB(255, 255, 255))
		self.ItemValueText1 = self.comp.TextLine(self.Board, 'Send a link with ro/tr or other', 11, 120, self.comp.RGB(255, 255, 255))
		self.ItemValueText2 = self.comp.TextLine(self.Board, 'languages Item IDs and i will add', 11, 135, self.comp.RGB(255, 255, 255))
		self.ItemValueText3 = self.comp.TextLine(self.Board, 'you have to look for the id and', 11, 170, self.comp.RGB(255, 255, 255))
		self.ItemValueText4 = self.comp.TextLine(self.Board, 'than enter this id at "Itemvalue"', 11, 185, self.comp.RGB(255, 255, 255))
		self.ItemValueText5 = self.comp.TextLine(self.Board, '', 11, 200, self.comp.RGB(255, 255, 255))
		self.ItemValueText6 = self.comp.TextLine(self.Board, 'The Items are only clientside, that', 11, 230, self.comp.RGB(255, 255, 0))
		self.ItemValueText7 = self.comp.TextLine(self.Board, 'means that you can not sell, equip', 11, 245, self.comp.RGB(255, 255, 0))
		self.ItemValueText8 = self.comp.TextLine(self.Board, 'or trade it! (only fun)', 11, 260, self.comp.RGB(255, 255, 0))
	
	def German(self):
		os.system("start http://www.metin2pserver.info/tools/item-vnum-id/")
		
	def English(self):
		os.system("start http://www.mt2-codes.com/metin2/eng/1000-all.htm")
	
	def Romanian(self):
		os.system("start http://www.mt2-codes.com/metin2/eng/1000-all.htm")
	
	def Turkey(self):
		os.system("start http://www.mt2-codes.com/metin2/eng/1000-all.htm")
		
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
#EQChangerItemDialog().Show()