import ui,app,chat,chr,net,player,item,skill,time,game,shop
import background,constInfo,miniMap,uiminimap,wndMgr,math,grp,uiCommon

SkillBookNamesDE = [0,'3-Wege Schnitt','Schwertwirbel', 'Kampfrausch', 'Aura des Schwertes','Sausen',6,7,8,9,10,11,12,13,14,15,
					'Durchschlag','Heftiges Schlagen','Stampfer','Starker Körper','Schwertschlag',21,22,23,24,25,26,27,28,29,30,
					'Hinterhalt','Blitzangriff','Degenwirbel', 'Tarnung','Giftwolke',36,37,38,39,40,41,42,43,44,45,
					'Wiederholter Schuss','Pfeilregen','Feuerpfeil','Federschreiten','Giftpfeil',51,52,53,54,55,56,57,58,59,60,
					'Fingerschlag','Drachenwirbel','Verzauberte Klinge','Furcht','Verzauberte Rüstung','Zauber Aufheben',67,68,69,70,71,72,73,74,75,
					'Dunkler Schlag','Flammenschlag','GDF','Dunkler Schutz','Geisterschlag','Dunkler Stein',82,83,84,85,86,87,88,89,90,
					'Fliegender Talisman','Drachenschießen','Drachengebrüll','Segen','Reflektieren','Hilfe des Drachens',97,98,100,101,102.103,104,105,
					'Blitzwurf','Blitz Heraufbeschwören','Blitzkralle','Kurieren','Schnelligkeit','Angriff +']
SkillBookNamesEN = [0,'Three-Way Cut','Sword Spin', 'Berserk', 'Aura of the Sword','Dash',6,7,8,9,10,11,12,13,14,15,
					'Spirit Strike','Bash','Stump','Strong Body','Sword Strike',21,22,23,24,25,26,27,28,29,30,
					'Ambush','Fast Attack','Rolling Dagger', 'Stealth','Poisonous Cloud',36,37,38,39,40,41,42,43,44,45,
					'Repetitive Shot','Arrow Shower','Fire Arrow','Feather Walk','Poison Arrow',51,52,53,54,55,56,57,58,59,60,
					'Finger Strike','Dragon Swirl','Enchanted Blade','Fear','Enchanted Armour','Dispel',67,68,69,70,71,72,73,74,75,
					'Dark Strike','Flame Strike','Flame Spirit','Dark Protection','Spirit Strike','Dark Orb',82,83,84,85,86,87,88,89,90,
					'Flying Talisman','Shooting Dragon','Dragond Roar','Blessing','Reflect','Dragons Strength',97,98,100,101,102.103,104,105,
					'Lightning Throw','Summon Lightning','Lightning Claw','Cure','Swiftness','Attack Up']
SkillBookIds = [100000,100001,100002,100003,100004,100005,100006,100007,100008,100009,100010,100011,100012,100013,100014,100015,100016,100017,100018,100019,100020,
 				100021,100022,100023,100024,100025,100026,100027,100028,100029,100030,100031,100032,100033,100034,100035,100036,100037,100038,100039,100040,
				100041,100042,100043,100044,100045,100046,100047,100048,100049,100050,100051,100052,100053,100054,100055,100056,100057,100058,100059,100060,
				100061,100062,100063,100064,100065,100066,100067,100068,100069,100070,100071,100072,100073,100074,100075,100076,100077,100078,100079,100080,
				100081,100082,100083,100084,100085,100086,100087,100088,100089,100090,100091,100092,100093,100094,100095,100096,100097,100098,100099,100100,
				100101,100102,100103,100104,100105,100106,100107,100108,100109,100110,100111,100112]
ListOfItems = [ [ 0 for x in xrange(2) ] for x in xrange(50) ]

class ShopCreatorDialog(ui.ScriptWindow):
	
	UI = []
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.LoadGui()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)
		
	
	def LoadGui(self):
		self.Shop = ui.ThinBoard() 
		self.Shop.SetPosition(52, 40)
		self.Shop.SetSize(310, 345)
	#	self.Shop.AddFlag("float") 
	#	self.Shop.AddFlag("movable")
		self.Shop.Show()
		
		self.Language = 0
		self.comp = Component()
		## Buttons ##
		self.CloseButton = self.comp.Button(self.Shop, '', 'Close', 280, 8, self.Close, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.LangButton = self.comp.Button(self.Shop, 'English', '', 20, 310, self.ChangeLang, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub','d:/ymir work/ui/public/large_button_03.sub')
		self.MakeShopButton = self.comp.Button(self.Shop, 'Make Shop', '', 190, 310, self.MakeShop, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub','d:/ymir work/ui/public/large_button_03.sub')
		
		## Text ##
		self.Header = self.comp.TextLine(self.Shop, 'Shop-Creator by Romeo79 (edited by 123klo)', 40, 8, self.comp.RGB(255, 255, 0))
		self.Name = self.comp.TextLine(self.Shop, 'Shop-Name:', 10, 285, self.comp.RGB(0, 229, 650))
		self.Item1 = self.comp.TextLine(self.Shop, 'Item1', 82, 30, self.comp.RGB(0, 229, 650))
		self.Item2 = self.comp.TextLine(self.Shop, 'Item2', 82, 55, self.comp.RGB(0, 229, 650))
		self.Item3 = self.comp.TextLine(self.Shop, 'Item3', 82, 80, self.comp.RGB(0, 229, 650))
		self.Item4 = self.comp.TextLine(self.Shop, 'Item4', 82, 105, self.comp.RGB(0, 229, 650))
		self.Item5 = self.comp.TextLine(self.Shop, 'Item5', 82, 130, self.comp.RGB(0, 229, 650))
		self.Item6 = self.comp.TextLine(self.Shop, 'Item6', 82, 155, self.comp.RGB(0, 229, 650))
		self.Item7 = self.comp.TextLine(self.Shop, 'Item7', 82, 180, self.comp.RGB(0, 229, 650))
		self.Item8 = self.comp.TextLine(self.Shop, 'Item8', 82, 205, self.comp.RGB(0, 229, 650))
		self.Item9 = self.comp.TextLine(self.Shop, 'Item9', 82, 230, self.comp.RGB(0, 229, 650))
		self.Item10 = self.comp.TextLine(self.Shop, 'Item10', 82, 255, self.comp.RGB(0, 229, 650))
		self.Item11 = self.comp.TextLine(self.Shop, 'Item11', 242, 30, self.comp.RGB(0, 229, 650))
		self.Item12 = self.comp.TextLine(self.Shop, 'Item12', 242, 55, self.comp.RGB(0, 229, 650))
		self.Item13 = self.comp.TextLine(self.Shop, 'Item13', 242, 80, self.comp.RGB(0, 229, 650))
		self.Item14 = self.comp.TextLine(self.Shop, 'Item14', 242, 105, self.comp.RGB(0, 229, 650))
		self.Item15 = self.comp.TextLine(self.Shop, 'Item15', 242, 130, self.comp.RGB(0, 229, 650))
		self.Item16 = self.comp.TextLine(self.Shop, 'Item16', 242, 155, self.comp.RGB(0, 229, 650))
		self.Item17 = self.comp.TextLine(self.Shop, 'Item17', 242, 180, self.comp.RGB(0, 229, 650))
		self.Item18 = self.comp.TextLine(self.Shop, 'Item18', 242, 205, self.comp.RGB(0, 229, 650))
		self.Item19 = self.comp.TextLine(self.Shop, 'Item19', 242, 230, self.comp.RGB(0, 229, 650))
		self.Item20 = self.comp.TextLine(self.Shop, 'Item20', 242, 255, self.comp.RGB(0, 229, 650))
		
		## EditLines ##
		self.ShopNameSlotbar, self.ShopNameEditline = self.comp.EditLine(self.Shop, '', 80, 282, 200, 18, 34)
		self.ItemPriceSlotBar1, self.ItemPriceEditline1 = self.comp.EditLine(self.Shop, '0', 10, 30, 67, 18, 9)
		self.ItemPriceSlotBar2, self.ItemPriceEditline2 = self.comp.EditLine(self.Shop, '0', 10, 55, 67, 18, 9)
		self.ItemPriceSlotBar3, self.ItemPriceEditline3 = self.comp.EditLine(self.Shop, '0', 10, 80, 67, 18, 9)
		self.ItemPriceSlotBar4, self.ItemPriceEditline4 = self.comp.EditLine(self.Shop, '0', 10, 105, 67, 18, 9)
		self.ItemPriceSlotBar5, self.ItemPriceEditline5 = self.comp.EditLine(self.Shop, '0', 10, 130, 67, 18, 9)
		self.ItemPriceSlotBar6, self.ItemPriceEditline6 = self.comp.EditLine(self.Shop, '0', 10, 155, 67, 18, 9)
		self.ItemPriceSlotBar7, self.ItemPriceEditline7 = self.comp.EditLine(self.Shop, '0', 10, 180, 67, 18, 9)
		self.ItemPriceSlotBar8, self.ItemPriceEditline8 = self.comp.EditLine(self.Shop, '0', 10, 205, 67, 18, 9)
		self.ItemPriceSlotBar9, self.ItemPriceEditline9 = self.comp.EditLine(self.Shop, '0', 10, 230, 67, 18, 9)
		self.ItemPriceSlotBar10, self.ItemPriceEditline10 = self.comp.EditLine(self.Shop, '0', 10, 255, 67, 18, 9)
		self.ItemPriceSlotBar11, self.ItemPriceEditline11 = self.comp.EditLine(self.Shop, '0', 170, 30, 67, 18, 9)
		self.ItemPriceSlotBar12, self.ItemPriceEditline12 = self.comp.EditLine(self.Shop, '0', 170, 55, 67, 18, 9)
		self.ItemPriceSlotBar13, self.ItemPriceEditline13 = self.comp.EditLine(self.Shop, '0', 170, 80, 67, 18, 9)
		self.ItemPriceSlotBar14, self.ItemPriceEditline14 = self.comp.EditLine(self.Shop, '0', 170, 105, 67, 18, 9)
		self.ItemPriceSlotBar15, self.ItemPriceEditline15 = self.comp.EditLine(self.Shop, '0', 170, 130, 67, 18, 9)
		self.ItemPriceSlotBar16, self.ItemPriceEditline16 = self.comp.EditLine(self.Shop, '0', 170, 155, 67, 18, 9)
		self.ItemPriceSlotBar17, self.ItemPriceEditline17 = self.comp.EditLine(self.Shop, '0', 170, 180, 67, 18, 9)
		self.ItemPriceSlotBar18, self.ItemPriceEditline18 = self.comp.EditLine(self.Shop, '0', 170, 205, 67, 18, 9)
		self.ItemPriceSlotBar19, self.ItemPriceEditline19 = self.comp.EditLine(self.Shop, '0', 170, 230, 67, 18, 9)
		self.ItemPriceSlotBar20, self.ItemPriceEditline20 = self.comp.EditLine(self.Shop, '0', 170, 255, 67, 18, 9)
		
		self.Load()
		self.GetItems()	
			
			
	def ChangeLang(self):
		if self.Language == 0:
			self.Language = 1
			chat.AppendChat(chat.CHAT_TYPE_INFO, 'Skill book language chnaged to German')
			self.LangButton.SetText('German')
			self.GetItems()
		else: 
			self.Language = 0
			chat.AppendChat(chat.CHAT_TYPE_INFO, 'Skill book language chnaged to English')
			self.LangButton.SetText('English')
			self.GetItems()
	
	def MakeShop(self):
		self.MakeShop1()
		self.MakeShop1()

	def MakeShop1(self):
		name = self.ShopNameEditline.GetText()
		shop.BuildPrivateShop(name)
		for i in xrange(0, 40):
			ItemValue = player.GetItemIndex(i)
			if (ItemValue == 50300):
				sbId1 = player.GetItemMetinSocket(i, 0)
				ItemValue = SkillBookIds[sbId1]
			if (int(ItemValue) != 0):
				if (ItemValue == ListOfItems[0][0]):
					price = self.ItemPriceEditline1.GetText()
				if (ItemValue == ListOfItems[1][0]):
					price = self.ItemPriceEditline2.GetText()
				if (ItemValue == ListOfItems[2][0]):
					price = self.ItemPriceEditline3.GetText()
				if (ItemValue == ListOfItems[3][0]):
					price = self.ItemPriceEditline4.GetText()
				if (ItemValue == ListOfItems[4][0]):
					price = self.ItemPriceEditline5.GetText()
				if (ItemValue == ListOfItems[5][0]):
					price = self.ItemPriceEditline6.GetText()
				if (ItemValue == ListOfItems[6][0]):
					price = self.ItemPriceEditline7.GetText()
				if (ItemValue == ListOfItems[7][0]):
					price = self.ItemPriceEditline8.GetText()
				if (ItemValue == ListOfItems[8][0]):
					price = self.ItemPriceEditline9.GetText()
				if (ItemValue == ListOfItems[9][0]):
					price = self.ItemPriceEditline10.GetText()
				if (ItemValue == ListOfItems[10][0]):
					price = self.ItemPriceEditline11.GetText()
				if (ItemValue == ListOfItems[11][0]):
					price = self.ItemPriceEditline12.GetText()
				if (ItemValue == ListOfItems[12][0]):
					price = self.ItemPriceEditline13.GetText()
				if (ItemValue == ListOfItems[13][0]):
					price = self.ItemPriceEditline14.GetText()
				if (ItemValue == ListOfItems[14][0]):
					price = self.ItemPriceEditline15.GetText()
				if (ItemValue == ListOfItems[15][0]):
					price = self.ItemPriceEditline16.GetText()
				if (ItemValue == ListOfItems[16][0]):
					price = self.ItemPriceEditline17.GetText()
				if (ItemValue == ListOfItems[17][0]):
					price = self.ItemPriceEditline18.GetText()
				if (ItemValue == ListOfItems[18][0]):
					price = self.ItemPriceEditline19.GetText()
				if (ItemValue == ListOfItems[19][0]):
					price = self.ItemPriceEditline20.GetText()
				Icount = player.GetItemCount(i)
				Trueprice = (int(price) * int(Icount))
				shop.AddPrivateShopItemStock(player.SLOT_TYPE_INVENTORY, int(i), int(i), int(Trueprice))
		shop.IsOpen()



	def GetItems(self):
	
		for ra in xrange(0,40):
			ListOfItems[ra][0] = 0
			
		for sho in xrange(0,20):
			exec (('self.ItemPriceSlotBar' + str((sho + 1))) + '.Show()')
			exec (('self.Item' + str((sho + 1))) + '.Show()')
			
		for ri in xrange(0,40):
			disable = 0
			ItemValue = player.GetItemIndex(ri)
			if ((int(ItemValue) != 0) and (ItemValue != 50300)):
				item.SelectItem(ItemValue)
				ItemName = item.GetItemName()
				for i in xrange(0,29):
					if (ListOfItems[i][0] == ItemValue):
						disable = 1
						break
					else:
						disable = 0
				
				if (disable == 0):
					for j in xrange(0,29):
						if (ListOfItems[j][0] == 0):
							ListOfItems[j][0] = ItemValue
							exec (((('self.Item' + str((j + 1))) + '.SetText("') + ItemName) + '")')
							break
	
			if (ItemValue == 50300):
				sbId = player.GetItemMetinSocket(ri, 0)
				ItemValue = SkillBookIds[sbId]
				disable = 0
				for i in xrange(0, 19):
					if (ListOfItems[i][0] == ItemValue):
						disable = 1
						break
					else:
						disable = 0
						
				if (disable == 0):
					for j in xrange(0, 19):
						if (ListOfItems[j][0] == 0):
							ListOfItems[j][0] = ItemValue
							if (self.Language == 1):
								exec (((('self.Item' + str((j + 1))) + '.SetText("') + str(SkillBookNamesDE[sbId])) + '")')
							elif (self.Language == 0):
								exec (((('self.Item' + str((j + 1))) + '.SetText("') + str(SkillBookNamesEN[sbId])) + '")')
							break
		CountItems = 0
		for hid in xrange(0, 20):
			if (ListOfItems[hid][0] == 0):
				exec (('self.ItemPriceSlotBar' + str((hid + 1))) + '.Hide()')
				exec (('self.Item' + str((hid + 1))) + '.Hide()')
			if (ListOfItems[hid][0] != 0):
				CountItems += 1
				
	
	def Save(self):
		f = open("m2kmod/Saves/priceconfig.m2k", 'w+')
		f.write((str(int(self.ItemPriceEditline1.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline2.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline3.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline4.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline5.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline6.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline7.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline8.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline9.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline10.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline11.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline12.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline13.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline14.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline15.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline16.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline17.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline18.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline19.GetText())) + '\n'))
		f.write((str(int(self.ItemPriceEditline20.GetText())) + '\n'))
		f.write(str(self.ShopNameEditline.GetText()) + '\n')
		f.close()
		chat.AppendChat(chat.CHAT_TYPE_INFO, 'Prices Saved!')

	def Load(self):
		rf = open("m2kmod/Saves/priceconfig.m2k", 'r')
		lines = rf.readlines()
		self.ItemPriceEditline1.SetText(str(lines[0]))
		self.ItemPriceEditline2.SetText(str(lines[1]))
		self.ItemPriceEditline3.SetText(str(lines[2]))
		self.ItemPriceEditline4.SetText(str(lines[3]))
		self.ItemPriceEditline5.SetText(str(lines[4]))
		self.ItemPriceEditline6.SetText(str(lines[5]))
		self.ItemPriceEditline7.SetText(str(lines[6]))
		self.ItemPriceEditline8.SetText(str(lines[7]))
		self.ItemPriceEditline9.SetText(str(lines[8]))
		self.ItemPriceEditline10.SetText(str(lines[9]))
		self.ItemPriceEditline11.SetText(str(lines[10]))
		self.ItemPriceEditline12.SetText(str(lines[11]))
		self.ItemPriceEditline13.SetText(str(lines[12]))
		self.ItemPriceEditline14.SetText(str(lines[13]))
		self.ItemPriceEditline15.SetText(str(lines[14]))
		self.ItemPriceEditline16.SetText(str(lines[15]))
		self.ItemPriceEditline17.SetText(str(lines[16]))
		self.ItemPriceEditline18.SetText(str(lines[17]))
		self.ItemPriceEditline19.SetText(str(lines[18]))
		self.ItemPriceEditline20.SetText(str(lines[19]))
		self.ShopNameEditline.SetText(str(lines[20]))
		rf.close()



	def Show(self):
		ui.ScriptWindow.Show(self)

	def Close(self):
		self.Save()
		self.Shop.Hide()



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
	def TextLine(self, parent, textlineText, x, y, color, ):
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
	def EditLine(self, parent, editlineText, x, y, width, heigh, max):
		SlotBar = ui.SlotBar()
		if parent != None:
			SlotBar.SetParent(parent)
		SlotBar.SetSize(width, heigh)
		SlotBar.SetPosition(x, y)
		SlotBar.Show()
		Value = ui.EditLine()
		Value.SetParent(SlotBar)
		Value.SetSize(width, heigh)
		Value.SetPosition(10, 2)
		Value.SetMax(max)
		Value.SetLimitWidth(width)
		Value.SetMultiLine()
		Value.SetText(editlineText)
		Value.Show()
		return SlotBar, Value

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

try:
	app.Shop.Close()
except:
	pass
app.Shop = ShopCreatorDialog()
