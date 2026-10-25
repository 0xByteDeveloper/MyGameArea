import ui,app,chat,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class BookReaderDialog(ui.ScriptWindow):
	Gui = []
	
	Books =   {"Warrior" : [[50401, 50402, 50403, 50404, 50405, 50406], [50416, 50417, 50418, 50419, 50420, 50421]], 
	"Assassin" : [[50431, 50432, 50433, 50434, 50435, 50436], [50446, 50447, 50448, 50449, 50450, 50451]],
	"Sura" : [[50461, 50462, 50463, 50464, 50465, 50466], [50476, 50477, 50478, 50479, 50450, 50451]],
	"Shaman" : [[50491, 50492, 50493, 50494, 50495, 50496], [50506, 50507, 50508, 50509,50510, 505011]],
	}
	
	State = "Stop"	
	TimeStamp = 0
	Konzi = 1
	Reading2 = 0
	BannedSlotIndex = []
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
		
	def AddGui(self):
		Gui = [
		#	[[ui.ThinBoard, ""], [218, 250], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
		#	[[ui.Button, 0], [0, 0], [183, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.SlotBar, 0], [190, 135], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [15, 50], [["SetViewItemCount", [10]]], []],			
		#	[[ui.TextLine, 0], [0, 0], [55, 8], [["SetOutline", [""]],	["SetText", ["Skill Book Reader"]],	["SetFontColor", [1.0, 0.8, 0]]], []],			
		#	[[ui.TextLine, 0], [0, 0], [13, 37], [["SetDefaultFontName", [""]],	["SetText", ["Skill  ID:         Name:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],			
		#	[[ui.Button, 0], [0, 0], [120, 185], [['SetUpVisual', ["m2kmod\Images\start_0.tga"]],['SetOverVisual', ["m2kmod\Images\start_1.tga"]], ['SetDownVisual', ["m2kmod\Images\start_2.tga"]], ['SetEvent', [lambda : self.Reading1()]]], []],	
		#	[[ui.Button, 0], [0, 0], [120, 185], [['SetUpVisual', ["m2kmod\Images\stop_0.tga"]],['SetOverVisual', ["m2kmod\Images\stop_1.tga"]], ['SetDownVisual', ["m2kmod\Images\stop_2.tga"]], ['SetEvent', [lambda : self.Reading1()]]], []],	
			[[ui.ExpandedImageBox, 0], [0, 0], [45, 190], [['LoadImage', [item.GetIconImageFileName(item.SelectItem(71094))]]], []],
		#	[[ui.Button, 0], [0, 0], [70, 190], [['SetUpVisual', ["m2kmod\Images\on_0.tga"]],['SetOverVisual', ["m2kmod\Images\on_1.tga"]], ['SetDownVisual', ["m2kmod\Images\on_2.tga"]],  ['SetEvent', [lambda : self.KonziState()]]], []],	
		#	[[ui.Button, 0], [0, 0], [70, 190], [['SetUpVisual', ["m2kmod\Images\off_0.tga"]],['SetOverVisual', ["m2kmod\Images\off_1.tga"]], ['SetDownVisual', ["m2kmod\Images\off_2.tga"]], ['SetEvent', [lambda : self.KonziState()]]], []],
			[[ui.TextLine, 0], [0, 0], [70, 230], [["SetOutline", [""]],	["SetText", ["©DaRealFreak"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			]
		GuiParser(Gui, self.Gui)		
		self.Gui[7].Hide()
		self.Gui[10].Hide()
		self.Gui[0].SetPosition(52, 40)
		self.AddItems()
		
	def KonziState(self):
		if self.Konzi == 1:
			self.Konzi = 0
			chat.AppendChat(1, "Concentrated Reading won´t be used!")
			self.Gui[9].Hide()
			self.Gui[10].Show()	
		else:
			self.Konzi = 1
			chat.AppendChat(1, "Concentrated Reading will be used!")
			self.Gui[10].Hide()
			self.Gui[9].Show()	
				
	def Reading1(self):
		if self.Reading2 == 0:
			self.Reading2 = 1
			self.Gui[6].Hide()
			self.Gui[7].Show()
			self.StartReading()
		else:
			self.Reading2 = 0
			self.Gui[7].Hide()
			self.Gui[6].Show()	
			self.BreakReading()
	def AddItems(self):
		RaceGroupInfo = GetClass()
		Class = str(RaceGroupInfo).split("/")[0]
		group = str(RaceGroupInfo).split("/")[1]
		if Class == "Warrior":
			self.SkillIndex = 1
			if int(group) == 2:
				self.SkillIndex = 16
		elif Class == "Assassin":
			self.SkillIndex = 31
			if int(group) == 2:
				self.SkillIndex = 46
		elif Class == "Sura":
			self.SkillIndex = 61
			if int(group) == 2:
				self.SkillIndex = 76
		elif Class == "Shaman":
			self.SkillIndex = 91
			if int(group) == 2:
				self.SkillIndex = 106

		for i in xrange(NewSkillsEnable()):
			Skillname = skill.GetSkillName(self.SkillIndex)
			RaceGroupInfo = GetClass().split("/")
			ID = self.Books[RaceGroupInfo[0]][int(RaceGroupInfo[1]) - 1][i]
			if str(Skillname) != "None":
				self.Gui[3].AppendItem(Item(str(self.SkillIndex) + "      " + str(ID) + "      " + str(Skillname)))
				self.SkillIndex += 1
			
	def BreakReading(self):
		self.Wait = WaitingDialog()	
		self.Wait.Close()
	
	def ReadBooks(self):
		if (player.GetItemCountByVnum(50300) == 0 and player.GetItemCountByVnum(int(self.SkillBook[1])) == 0):
			result = 0
			if shop.IsOpen():
				for EachShopSlot in xrange(shop.SHOP_SLOT_COUNT):
					ShopItemValue = shop.GetItemID(EachShopSlot)
					if ShopItemValue == int(self.SkillBook[1]):
						net.SendShopBuyPacket(EachShopSlot)
						self.BannedSlotIndex = []
						result = 1
						break
			else:
				chat.AppendChat(1, "You don´t have Skillbooks for the selected skill in your inventory!")
			if player.GetItemCountByVnum(71001) == 0:
				chat.AppendChat(1, "You don´t have Exorcism scrolls in your Inventory!")
				self.BreakReading()
				self.Reading2 = 0
				self.Gui[7].Hide()
				self.Gui[6].Show()
				return
			if result == 0:
				self.BreakReading()
				self.Reading2 = 0
				self.Gui[7].Hide()
				self.Gui[6].Show()
				return
		#	chat.AppendChat(1, "You don´t have skillbooks for the seleceted skill!")
		for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
			ItemValue = player.GetItemIndex(Slot)
			if ItemValue == 50300:
				metinSlot = [player.GetItemMetinSocket(Slot, i) for i in xrange(player.METIN_SOCKET_MAX_NUM)]
				if metinSlot[0] == int(self.SkillBook[0]):
					net.SendItemUsePacket(Slot)
					while len(self.BannedSlotIndex) >= 4:
						self.BannedSlotIndex.remove(self.BannedSlotIndex[0])
					self.BannedSlotIndex.append(Slot)
					break
			if ItemValue == int(self.SkillBook[1]):
				while len(self.BannedSlotIndex) >= 4:
					self.BannedSlotIndex.remove(self.BannedSlotIndex[0])
				try:
					self.BannedSlotIndex.index(Slot)
				except:
					net.SendItemUsePacket(Slot)
					self.BannedSlotIndex.append(Slot)
					break
		
		Exo = 0
		if self.UseConcentrated():
			Konz = 0
		else:
			Konz = 1
		
		for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
			ItemValue = player.GetItemIndex(Slot)
			if ItemValue == 71001 and Exo == 0:
				net.SendItemUsePacket(Slot)
				Exo = 1
			if ItemValue == 71094 and Konz == 0:
				net.SendItemUsePacket(Slot)
				Konz = 1
			if Konz == 1 and Exo == 1:
				break
	
		self.TimeStamp = float(app.GetTime()) + 0.5

	def OnUpdate(self):
		if self.State != "Start":
			return
	
		if app.GetTime() >= self.TimeStamp:
			if self.IsReadAble(self.SkillCount):
				self.ReadBooks()
			else:
				chat.AppendChat(1, "This Skill doesn´t have the level which is needed to read!")
				self.BreakReading()
				self.Reading2 = 0
				self.Gui[7].Hide()
				self.Gui[6].Show()
				
	def BreakReading(self):
		self.State = "Stop"
		
	def IsReadAble(self, count):
		Skillgrade = player.GetSkillGrade(count)
		Skilllevel = player.GetSkillLevel(count)

		if 1 == Skillgrade:
			Skilllevel += 19
		elif 2 == Skillgrade:
			Skilllevel += 29
		elif 3 == Skillgrade:
			Skilllevel = 40
		
		if Skilllevel < 20:
			return 0
		elif Skilllevel < 30 and Skilllevel >= 20:
			return 1
		else:
			return 0
		
	def StartReading(self):
	#	chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
			self.BreakReading()
			self.Reading2 = 0
			self.Gui[7].Hide()
			self.Gui[6].Show()
			return
		self.SkillBook = ItemIndex.GetText().split("      ")
		
		RaceGroupInfo = GetClass().split("/")
		self.SkillCount = self.Books[RaceGroupInfo[0]][int(RaceGroupInfo[1]) - 1].index(int(self.SkillBook[1])) + 1

		self.TimeStamp = app.GetTime()
		self.State = "Start"	
	
	def UseConcentrated(self):
		if player.GetItemCountByVnum(71094) > 0:
			if self.Konzi == 1:
				return 1
		else:
			if self.Konzi == 1:
				chat.AppendChat(1, "You have no Concentrated Readings in your inventory!")
				self.BreakReading()		
				self.Reading2 = 0
				self.Gui[7].Hide()
				self.Gui[6].Show()
			
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
	
class EterPackOperator(object):

	def __init__(self, filename):
	
	#	if not pack.Exist(filename):
	#		raise IOError, 'No file or directory'
		self.data = self.GetTextFile(filename)
		self.data=chr(10).join(self.data.split(chr(13)+chr(10)))

	def read(self, len = None):
		if not self.data:
			return ''
		if len:
			tmp = self.data[:len]
			self.data = self.data[len:]
			return tmp
		else:
			tmp = self.data
			self.data = ''
			return tmp

	def readlines(self):
		Array = str(self.data).split("\n")
		return Array
		
	def getline(self, line):
		return self.readlines()[line - 1]
		
	def getlinecount(self):
		return len(self.readlines())

	def GetTextFile(self, file):
		tmp = []
		try:
			Handle = app.OpenTextFile(file)
			CountLines = app.GetTextFileLineCount(Handle)
		except:
			return ""
		for i in xrange(CountLines):
			line = app.GetTextFileLine(Handle, i)
			if line != "":
				tmp.append(line + "\n")
		return("".join(tmp))
	
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
		

#BookReaderDialog().Show()