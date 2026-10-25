import chat
import chr
import locale
import ui
import shop
import app
import net
import player

price = 0
vnum = 0
conprice = 0
convnum = 0
price1 = 0
vnum1 = 0
conprice1 = 0
convnum1 = 0
price2 = 0
vnum2 = 0
conprice2 = 0
convnum2 = 0
price3 = 0
vnum3 = 0
conprice3 = 0
convnum3 = 0
kauf = 0
eqi = 0
fbi = 0

stone_up = 28943
stone_down = 28000
armor_up = 12049
armor_down = 11200
weapon1_up = 5129
weapon1_down = 10
weapon2_up = 7199
weapon2_down = 7000
eq_up = 17209
eq_down = 12200




class Botdialog(ui.ThinBoard):

	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.LoadBoard()
		
	def LoadBoard(self):
		self.SetCenterPosition()
		self.SetSize(420, 320)
		self.Show()
		self.AddFlag("movable")
		
		self.LoadText()
		self.LoadButton()
		self.LoadInput()	
		
	def LoadText(self):
		global vnum
		global price
		global conprice
		global convnum
		global vnum1
		global price1
		global vnum2
		global price2
		global vnum3
		global price3

		self.Titel = ui.TextLine()
		self.Titel.SetParent(self)
		self.Titel.SetDefaultFontName()
		self.Titel.SetPosition(-200, 300)
		self.Titel.SetFeather()
		self.Titel.SetWindowHorizontalAlignCenter()
		self.Titel.SetText("Shop Scanner by P3nguin")
		self.Titel.SetFontColor(1.0, 0.8, 0)
		self.Titel.SetOutline()
		self.Titel.Show()

		self.atitel = ui.TextLine()
		self.atitel.SetParent(self)
		self.atitel.SetDefaultFontName()
		self.atitel.SetPosition(-160, 35)
		self.atitel.SetFeather()
		self.atitel.SetWindowHorizontalAlignCenter()
		self.atitel.SetText("Item Nr.: 1")
		self.atitel.SetFontColor(1.0, 0.8, 0)
		self.atitel.SetOutline()
		self.atitel.Show()	

		self.btitel = ui.TextLine()
		self.btitel.SetParent(self)
		self.btitel.SetDefaultFontName()
		self.btitel.SetPosition(-160, 60)
		self.btitel.SetFeather()
		self.btitel.SetWindowHorizontalAlignCenter()
		self.btitel.SetText("Preis Nr.: 1")
		self.btitel.SetFontColor(1.0, 0.8, 0)
		self.btitel.SetOutline()
		self.btitel.Show()

		self.ctitel = ui.TextLine()
		self.ctitel.SetParent(self)
		self.ctitel.SetDefaultFontName()
		self.ctitel.SetPosition(-160, 100)
		self.ctitel.SetFeather()
		self.ctitel.SetWindowHorizontalAlignCenter()
		self.ctitel.SetText("Item Nr.: 2")
		self.ctitel.SetFontColor(1.0, 0.8, 0)
		self.ctitel.SetOutline()
		self.ctitel.Show()	

		self.dtitel = ui.TextLine()
		self.dtitel.SetParent(self)
		self.dtitel.SetDefaultFontName()
		self.dtitel.SetPosition(-160, 125)
		self.dtitel.SetFeather()
		self.dtitel.SetWindowHorizontalAlignCenter()
		self.dtitel.SetText("Preis Nr.: 2")
		self.dtitel.SetFontColor(1.0, 0.8, 0)
		self.dtitel.SetOutline()
		self.dtitel.Show()

		self.etitel = ui.TextLine()
		self.etitel.SetParent(self)
		self.etitel.SetDefaultFontName()
		self.etitel.SetPosition(-160, 165)
		self.etitel.SetFeather()
		self.etitel.SetWindowHorizontalAlignCenter()
		self.etitel.SetText("Item Nr.: 3")
		self.etitel.SetFontColor(1.0, 0.8, 0)
		self.etitel.SetOutline()
		self.etitel.Show()	

		self.ftitel = ui.TextLine()
		self.ftitel.SetParent(self)
		self.ftitel.SetDefaultFontName()
		self.ftitel.SetPosition(-160, 190)
		self.ftitel.SetFeather()
		self.ftitel.SetWindowHorizontalAlignCenter()
		self.ftitel.SetText("Preis Nr.: 3")
		self.ftitel.SetFontColor(1.0, 0.8, 0)
		self.ftitel.SetOutline()
		self.ftitel.Show()

		self.gtitel = ui.TextLine()
		self.gtitel.SetParent(self)
		self.gtitel.SetDefaultFontName()
		self.gtitel.SetPosition(-160, 230)
		self.gtitel.SetFeather()
		self.gtitel.SetWindowHorizontalAlignCenter()
		self.gtitel.SetText("Item Nr.: 4")
		self.gtitel.SetFontColor(1.0, 0.8, 0)
		self.gtitel.SetOutline()
		self.gtitel.Show()

		self.htitel = ui.TextLine()
		self.htitel.SetParent(self)
		self.htitel.SetDefaultFontName()
		self.htitel.SetPosition(-160, 255)
		self.htitel.SetFeather()
		self.htitel.SetWindowHorizontalAlignCenter()
		self.htitel.SetText("Preis Nr.: 4")
		self.htitel.SetFontColor(1.0, 0.8, 0)
		self.htitel.SetOutline()
		self.htitel.Show()

			
		
	def LoadButton(self):
		self.CloseButton = ui.Button()
		self.CloseButton.SetParent(self)
		self.CloseButton.SetPosition(400, 4)
		self.CloseButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		self.CloseButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		self.CloseButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		self.CloseButton.SetToolTipText(locale.UI_CLOSE, 0, - 23)
		self.CloseButton.SetEvent(ui.__mem_func__(self.Close))
		self.CloseButton.Show()
	
		self.ChangeButton = ui.Button()
		self.ChangeButton.SetParent(self)
		self.ChangeButton.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.ChangeButton.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.ChangeButton.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.ChangeButton.SetText("Scan")
		self.ChangeButton.SetPosition(330, 290)
		self.ChangeButton.SetEvent(ui.__mem_func__(self.start))
		self.ChangeButton.Show()

		self.ChangeButton4 = ui.Button()
		self.ChangeButton4.SetParent(self)
		self.ChangeButton4.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.ChangeButton4.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.ChangeButton4.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.ChangeButton4.SetText("EQ")
		self.ChangeButton4.SetPosition(330, 250)
		self.ChangeButton4.SetEvent(ui.__mem_func__(self.eq))
		self.ChangeButton4.Show()

		self.ChangeButton5 = ui.Button()
		self.ChangeButton5.SetParent(self)
		self.ChangeButton5.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.ChangeButton5.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.ChangeButton5.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.ChangeButton5.SetText("FB")
		self.ChangeButton5.SetPosition(330, 230)
		self.ChangeButton5.SetEvent(ui.__mem_func__(self.fb))
		self.ChangeButton5.Show()
		
	def LoadInput(self):
		self.SlotBar1 = ui.SlotBar()
		self.SlotBar1.SetParent(self)
		self.SlotBar1.SetSize(160, 18)
		self.SlotBar1.SetPosition(10, 35)
		self.SlotBar1.SetWindowHorizontalAlignCenter()
		self.SlotBar1.Show()
		
		self.EditLine1 = ui.EditLine()
		self.EditLine1.SetParent(self.SlotBar1)
		self.EditLine1.SetSize(160, 17)
		self.EditLine1.SetPosition(5, 2)
		self.EditLine1.SetMax(12)
		self.EditLine1.SetText("ID")
		self.EditLine1.SetFocus()
		self.EditLine1.Show()
		
		self.SlotBar2 = ui.SlotBar()
		self.SlotBar2.SetParent(self)
		self.SlotBar2.SetSize(160, 18)
		self.SlotBar2.SetPosition(10, 60)
		self.SlotBar2.SetWindowHorizontalAlignCenter()
		self.SlotBar2.Show()
		
		self.EditLine2 = ui.EditLine()
		self.EditLine2.SetParent(self.SlotBar2)
		self.EditLine2.SetSize(160, 17)
		self.EditLine2.SetPosition(5, 2)
		self.EditLine2.SetMax(9)
		self.EditLine2.SetText("Preis")
		self.EditLine2.SetFocus()
		self.EditLine2.Show()

		self.SlotBar3 = ui.SlotBar()
		self.SlotBar3.SetParent(self)
		self.SlotBar3.SetSize(160, 18)
		self.SlotBar3.SetPosition(10, 100)
		self.SlotBar3.SetWindowHorizontalAlignCenter()
		self.SlotBar3.Show()
		
		self.EditLine3 = ui.EditLine()
		self.EditLine3.SetParent(self.SlotBar3)
		self.EditLine3.SetSize(160, 17)
		self.EditLine3.SetPosition(5, 2)
		self.EditLine3.SetMax(12)
		self.EditLine3.SetText("ID")
		self.EditLine3.SetFocus()
		self.EditLine3.Show()
		
		self.SlotBar4 = ui.SlotBar()
		self.SlotBar4.SetParent(self)
		self.SlotBar4.SetSize(160, 18)
		self.SlotBar4.SetPosition(10, 125)
		self.SlotBar4.SetWindowHorizontalAlignCenter()
		self.SlotBar4.Show()
		
		self.EditLine4 = ui.EditLine()
		self.EditLine4.SetParent(self.SlotBar4)
		self.EditLine4.SetSize(160, 17)
		self.EditLine4.SetPosition(5, 2)
		self.EditLine4.SetMax(9)
		self.EditLine4.SetText("Preis")
		self.EditLine4.SetFocus()
		self.EditLine4.Show()

		self.SlotBar5 = ui.SlotBar()
		self.SlotBar5.SetParent(self)
		self.SlotBar5.SetSize(160, 18)
		self.SlotBar5.SetPosition(10, 165)
		self.SlotBar5.SetWindowHorizontalAlignCenter()
		self.SlotBar5.Show()
		
		self.EditLine5 = ui.EditLine()
		self.EditLine5.SetParent(self.SlotBar5)
		self.EditLine5.SetSize(160, 17)
		self.EditLine5.SetPosition(5, 2)
		self.EditLine5.SetMax(12)
		self.EditLine5.SetText("ID")
		self.EditLine5.SetFocus()
		self.EditLine5.Show()
		
		self.SlotBar6 = ui.SlotBar()
		self.SlotBar6.SetParent(self)
		self.SlotBar6.SetSize(160, 18)
		self.SlotBar6.SetPosition(10, 190)
		self.SlotBar6.SetWindowHorizontalAlignCenter()
		self.SlotBar6.Show()
		
		self.EditLine6 = ui.EditLine()
		self.EditLine6.SetParent(self.SlotBar6)
		self.EditLine6.SetSize(160, 17)
		self.EditLine6.SetPosition(5, 2)
		self.EditLine6.SetMax(9)
		self.EditLine6.SetText("Preis")
		self.EditLine6.SetFocus()
		self.EditLine6.Show()
	
		self.SlotBar7 = ui.SlotBar()
		self.SlotBar7.SetParent(self)
		self.SlotBar7.SetSize(160, 18)
		self.SlotBar7.SetPosition(10, 230)
		self.SlotBar7.SetWindowHorizontalAlignCenter()
		self.SlotBar7.Show()
		
		self.EditLine7 = ui.EditLine()
		self.EditLine7.SetParent(self.SlotBar7)
		self.EditLine7.SetSize(160, 17)
		self.EditLine7.SetPosition(5, 2)
		self.EditLine7.SetMax(12)
		self.EditLine7.SetText("ID")
		self.EditLine7.SetFocus()
		self.EditLine7.Show()
		
		self.SlotBar8 = ui.SlotBar()
		self.SlotBar8.SetParent(self)
		self.SlotBar8.SetSize(160, 18)
		self.SlotBar8.SetPosition(10, 255)
		self.SlotBar8.SetWindowHorizontalAlignCenter()
		self.SlotBar8.Show()
		
		self.EditLine8 = ui.EditLine()
		self.EditLine8.SetParent(self.SlotBar8)
		self.EditLine8.SetSize(160, 17)
		self.EditLine8.SetPosition(5, 2)
		self.EditLine8.SetMax(9)
		self.EditLine8.SetText("Preis")
		self.EditLine8.SetFocus()
		self.EditLine8.Show()

				
	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Show(self):
		ui.ThinBoard.Show(self)

	def Close(self):
		self.Hide()
		
	def start(self):
		global vnum
		global price
		global vnum1
		global price1
		global vnum2
		global price2
		global vnum3
		global price3
		global fbi
		global eqi
		x = self.EditLine1.GetText()
		y = self.EditLine2.GetText()
		x1 = self.EditLine3.GetText()
		y1 = self.EditLine4.GetText()
		x2 = self.EditLine5.GetText()
		y2 = self.EditLine6.GetText()
		x3 = self.EditLine7.GetText()
		y3 = self.EditLine8.GetText()
		vnum = int(x)
		price = int(y)
		vnum1 = int(x1)
		price1 = int(y1)
		vnum2 = int(x2)
		price2 = int(y2)
		vnum3 = int(x3)
		price3 = int(y3)
		if vnum == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item ID Nr.1 fehlt!")
		if vnum1 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item ID Nr.2 fehlt!")
		if vnum2 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item ID Nr.3 fehlt!")
		if vnum3 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item ID Nr.4 fehlt!")
		if price == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item Preis Nr.1 fehlt!")
		if price1 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item Preis Nr.2 fehlt!")
		if price2 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item Preis Nr.3 fehlt!")
		if price3 == "":
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item Preis Nr.4 fehlt!")
		else:
			self.auswahl()


	def auswahl(self):
		global eqi
		global fbi

		if fbi == 0 and eqi == 1:
			self.out()

		elif eqi == 0 and fbi == 1:
			self.outfb()
		

	def out(self):
		global vnum
		global price
		global conprice
		global convnum
		global vnum1
		global price1
		global vnum2
		global price2
		global vnum3
		global price3
		global kauf
		global stone_up
		global stone_down
		global armor_up
		global armor_down
		global weapon1_up
		global weapon1_down
		global weapon2_up
		global weapon2_down
		global eq_up
		global eq_down

		for i in xrange(shop.SHOP_SLOT_COUNT):
		
			ivnum = shop.GetItemID(i)
			iprice = shop.GetItemPrice(i)

			convnum = int(ivnum)
			conprice = int(iprice)

			if vnum >= weapon1_down and vnum <= weapon1_up or vnum >= weapon2_down and vnum <= weapon2_up:
				vnumnew = vnum + 9
				if convnum >= vnum and convnum <= vnumnew and conprice <= price:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum >= armor_down and vnum <= armor_up:
				vnumnew = vnum + 9
				if convnum >= vnum and convnum <= vnumnew and conprice <= price:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum >= eq_down and vnum <= eq_up:
				vnumnew = vnum + 9
				if convnum >= vnum and convnum <= vnumnew and conprice <= price:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum >= stone_down and vnum <= stone_up:
				vnumnew = vnum + 9
				if convnum >= vnum and convnum <= vnumnew and conprice <= price:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1


			
			if vnum1 >= weapon1_down and vnum1 <= weapon1_up or vnum1 >= weapon2_down and vnum1 <= weapon2_up:
				vnumnew = vnum1 + 9
				if convnum >= vnum1 and convnum <= vnumnew and conprice <= price1:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum1 >= armor_down and vnum1 <= armor_up:
				vnumnew = vnum1 + 9
				if convnum >= vnum1 and convnum <= vnumnew and conprice <= price1:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum1 >= eq_down and vnum1 <= eq_up:
				vnumnew = vnum1 + 9
				if convnum >= vnum1 and convnum <= vnumnew and conprice <= price1:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum1 >= stone_down and vnum1 <= stone_up:
				vnumnew = vnum1 + 9
				if convnum >= vnum1 and convnum <= vnumnew and conprice <= price1:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1
			





			if vnum2 >= weapon1_down and vnum2 <= weapon1_up or vnum2 >= weapon2_down and vnum2 <= weapon2_up:
				vnumnew = vnum2 + 9
				if convnum >= vnum2 and convnum <= vnumnew and conprice <= price2:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum2 >= armor_down and vnum2 <= armor_up:
				vnumnew = vnum2 + 9
				if convnum >= vnum2 and convnum <= vnumnew and conprice <= price2:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum2 >= eq_down and vnum2 <= eq_up:
				vnumnew = vnum2 + 9
				if convnum >= vnum2 and convnum <= vnumnew and conprice <= price2:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum2 >= stone_down and vnum2 <= stone_up:
				vnumnew = vnum2 + 9
				if convnum >= vnum2 and convnum <= vnumnew and conprice <= price2:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1



			if vnum3 >= weapon1_down and vnum3 <= weapon1_up or vnum3 >= weapon2_down and vnum3 <= weapon2_up:
				vnumnew = vnum3 + 9
				if convnum >= vnum3 and convnum <= vnumnew and conprice <= price3:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum3 >= armor_down and vnum3 <= armor_up:
				vnumnew = vnum3 + 9
				if convnum >= vnum3 and convnum <= vnumnew and conprice <= price3:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum3 >= eq_down and vnum3 <= eq_up:
				vnumnew = vnum3 + 9
				if convnum >= vnum3 and convnum <= vnumnew and conprice <= price3:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1

			if vnum3 >= stone_down and vnum3 <= stone_up:
				vnumnew = vnum3 + 9
				if convnum >= vnum3 and convnum <= vnumnew and conprice <= price3:
					net.SendShopBuyPacket(i)
					kauf = kauf + 1
			
			if convnum == vnum3 and conprice <= price3:
				net.SendShopBuyPacket(i)
				kauf = kauf + 1

			if convnum == vnum and conprice <= price:
				net.SendShopBuyPacket(i)
				kauf = kauf + 1

			if convnum == vnum2 and conprice <= price2:
				net.SendShopBuyPacket(i)
				kauf = kauf + 1

			if convnum == vnum1 and conprice <= price1:
				net.SendShopBuyPacket(i)
				kauf = kauf + 1


		if kauf == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Es wurde nichts Gekauft!")
			net.SendShopEndPacket()

		if kauf == 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item mit der gewünschten ID wurde gekauft")
			kauf = 0
			net.SendShopEndPacket()

		if kauf > 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, str(kauf) +" Item`s mit den gewünschten ID`s wurden gekauft")	
			kauf = 0
			net.SendShopEndPacket()



	def outfb (self):
		global vnum
		global price
		global conprice
		global convnum
		global vnum1
		global price1
		global vnum2
		global price2
		global vnum3
		global price3
		global kauf

		for i in xrange(shop.SHOP_SLOT_COUNT):
			vid = shop.GetItemID(i)
			iprice = shop.GetItemPrice(i) 
			if (vid == 50300):
					fbid = shop.GetItemMetinSocket(i, 0)
					if vnum == fbid and iprice == price:
						net.SendShopBuyPacket(i)
						kauf = kauf + 1

					if vnum1 == fbid and iprice == price1:
						net.SendShopBuyPacket(i)
						kauf = kauf + 1

					if vnum2 == fbid and iprice == price2:
						net.SendShopBuyPacket(i)
						kauf = kauf + 1

					if vnum3 == fbid and iprice == price3:
						net.SendShopBuyPacket(i)
						kauf = kauf + 1

		if kauf == 0:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Es wurde nichts Gekauft!")
			net.SendShopEndPacket()

		if kauf == 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "Item mit der gewünschten ID wurde gekauft")
			kauf = 0
			net.SendShopEndPacket()

		if kauf > 1:
			chat.AppendChat(chat.CHAT_TYPE_INFO, str(kauf) +" Item`s mit den gewünschten ID`s wurden gekauft")	
			kauf = 0
			net.SendShopEndPacket()
					
	
	
	def eq (self):
		global eqi
		global fbi

		if eqi == 0 and fbi == 0:
			eqi = 1

		elif eqi == 1 and fbi == 0:
			eqi = 1

		elif eqi == 0 and fbi == 1:
			eqi = 1
			fbi = 0
		chat.AppendChat(chat.CHAT_TYPE_INFO, "Es wird nun nach Eq gesucht")


	def fb (self):
		global fbi
		global eqi

		if eqi == 0 and fbi == 0:
			fbi = 1

		elif eqi == 1 and fbi == 0:
			fbi = 1

		elif eqi == 1 and fbi == 0:
			eqi = 0
			fbi = 1
		chat.AppendChat(chat.CHAT_TYPE_INFO, "Es wird nun nach FB´s gesucht")

	
StartDialog = Botdialog()
StartDialog.Show()
