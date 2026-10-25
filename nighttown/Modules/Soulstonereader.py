import ui,app,chat,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,miniMap,uiminimap,wndMgr,math,uiCommon,grp

class SoulStoneBotDialog(ui.ScriptWindow):
	Gui = []
	
	State = "Stop"	
	TimeStamp = 0
	Zen = 1
	ReadExo = 1	
	Start = 0
	
	def __init__(self):
		self.Gui = []
		ui.ScriptWindow.__init__(self)
		self.AddGui()
		
	def __del__(self):
		self.Gui[0].Hide()
		ui.ScriptWindow.__del__(self)
		
	def AddGui(self):
		Gui = [
			[[ui.ThinBoard, ""], [218, 290], [0,0], [["SetCenterPosition", [""]]], ["float"]],			
			[[ui.Button, 0], [0, 0], [183, 8], [['SetUpVisual', ["d:/ymir work/ui/public/close_button_01.sub"]],['SetOverVisual', ["d:/ymir work/ui/public/close_button_02.sub"]], ['SetDownVisual', ["d:/ymir work/ui/public/close_button_03.sub"]], ['SetToolTipText', ["Close", 0, - 23]], ['SetEvent', [lambda : self.__del__()]]], []],	
			[[ui.SlotBar, 0], [190, 135], [10, 35], [], []],			
			[[ui.ListBoxEx, 0], [0, 0], [15, 50], [["SetViewItemCount", [10]]], []],			
			[[ui.TextLine, 0], [0, 0], [55, 8], [["SetOutline", [""]],	["SetText", ["Soul Stone Reader"]],	["SetFontColor", [1.0, 0.8, 0]]], []],			
			[[ui.TextLine, 0], [0, 0], [13, 37], [["SetDefaultFontName", [""]],	["SetText", ["Skill  Count:         Name:"]],	["SetFontColor", [0.2, 0.2, 1.0]]], []],			
			[[ui.Button, 0], [0, 0], [95, 240], [['SetUpVisual', ["m2kmod\Images\start_0.tga"]],['SetOverVisual', ["m2kmod\Images\start_1.tga"]], ['SetDownVisual', ["m2kmod\Images\start_2.tga"]], ['SetEvent', [lambda : self.ReadSelis()]]], []],	
			[[ui.Button, 0], [0, 0], [95, 240], [['SetUpVisual', ["m2kmod\Images\stop_0.tga"]],['SetOverVisual', ["m2kmod\Images\stop_1.tga"]], ['SetDownVisual', ["m2kmod\Images\stop_2.tga"]], ['SetEvent', [lambda : self.ReadSelis()]]], []],	
			[[ui.ExpandedImageBox, 0], [0, 0], [25, 175], [['LoadImage', [item.GetIconImageFileName(item.SelectItem(70102))]]], []],
			[[ui.Button, 0], [0, 0], [57, 177], [['SetUpVisual', ["m2kmod\Images\on_0.tga"]],['SetOverVisual', ["m2kmod\Images\on_1.tga"]], ['SetDownVisual', ["m2kmod\Images\on_2.tga"]],  ['SetEvent', [lambda : self.ZenState()]]], []],	
			[[ui.TextLine, 0], [0, 0], [90, 185], [["SetOutline", [""]],	["SetText", ["Confirm String"]]], []],			
			[[ui.TextLine, 0], [0, 0], [23, 213], [["SetOutline", [""]],	["SetText", [" "]]], []],
			[[ui.TextLine, 0], [0, 0], [23, 213], [["SetOutline", [""]],	["SetText", [" "]]], []],			
			[[ui.SlotBar, 0], [87, 18], [100, 211], [], []],			
			[[ui.EditLine, 13], [87, 17], [6, 2], [["SetMax", [16]], ["SetFocus", [""]]], []],			
			[[ui.Button, 0], [0, 0], [57, 177], [['SetUpVisual', ["m2kmod\Images\off_0.tga"]],['SetOverVisual', ["m2kmod\Images\off_1.tga"]], ['SetDownVisual', ["m2kmod\Images\off_2.tga"]], ['SetEvent', [lambda : self.ZenState()]]], []],
			[[ui.TextLine, 0], [0, 0], [23, 213], [["SetOutline", [""]],	["SetText", [" "]]], []],
			[[ui.TextLine, 0], [0, 0], [20, 260], [["SetOutline", [""]],	["SetText", ["©DaRealFreak"]],	["SetFontColor", [1.0, 0.8, 0]]], []],
			]
		GuiParser(Gui, self.Gui)		

		self.AddItems()
		self.Gui[15].Hide()
		self.Gui[16].Hide()
		self.Gui[7].Hide()
		self.Gui[0].SetPosition(52, 40)
	
	def ZenState(self):
		if self.Zen == 1:
			self.Zen = 0
			self.Gui[9].Hide()
			self.Gui[15].Show()
		else:
			self.Zen = 1
			self.Gui[15].Hide()
			self.Gui[9].Show()	
		
	def ConfigExo(self):
		if self.ReadExo == 1:
			self.ReadExo = 0
			self.Gui[11].Hide()
			self.Gui[16].Show()
		else:
			self.ReadExo = 1
			self.Gui[16].Hide()
			self.Gui[11].Show()
			
			
	def ReadSelis(self):
		
		if self.Start == 0:
			self.Start = 1
			self.Gui[6].Hide()
			self.Gui[7].Show()
			self.StartReading()
		else:
			self.Start = 0
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
				
		for Count in xrange(NewSkillsEnable()):
			Skillname = skill.GetSkillName(self.SkillIndex)
			Count += 1
			RaceGroupInfo = GetClass().split("/")
			if str(Skillname) != "None":
				self.Gui[3].AppendItem(Item(str(self.SkillIndex) + "      " + str(Count) + "      " + str(Skillname)))
				self.SkillIndex += 1
			
	def BreakReading(self):
		self.UnHookQuestWindow()
		self.State = "Stop"
		
	def GetNeededAlignment(self):
		point, grade = player.GetAlignmentData()
		SkillLevel = self.IsReadAble(int(self.SkillBook[1]), 1)
		NeedAlignment = 1000+500*(SkillLevel-30)
		if point < 0:
			NeedAlignment = NeedAlignment * 2
		
		if point - NeedAlignment <= -20000:
			if not self.Zen:
				chat.AppendChat(1, "You need more alignment than this: " + str(point + NeedAlignment))
				self.Stop()
				return 0
			else:
				if player.GetItemCountByVnum(70102) == 0:
					chat.AppendChat(1, "You don´t have Zen-Beans!")
					self.Stop()
				round = -1 * point / 2000
				for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
					ItemValue = player.GetItemIndex(Slot)
					if ItemValue == 70102:
						for i in xrange(round):
							net.SendItemUsePacket(Slot)
							break					
		return 1
		
	def ReadBooks(self, SkillIndex):
		if player.GetItemCountByVnum(50513) == 0: 
			if shop.IsOpen():
				for EachShopSlot in xrange(shop.SHOP_SLOT_COUNT):
					ShopItemValue = shop.GetItemID(EachShopSlot)
					if ShopItemValue == 50513:
						net.SendShopBuyPacket(EachShopSlot)
						break
			else:
				chat.AppendChat(1, "You don´t have a Soul Stone to read the skill!")
				self.Stop()
				return
		if player.GetItemCountByVnum(71001) == 0:	
			chat.AppendChat(1, "You don´t have Exorcism scrolls in your Inventory!")
			self.Stop()
			return

		for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
			ItemValue = player.GetItemIndex(Slot)
			if ItemValue == 71001:
				net.SendItemUsePacket(Slot)
				break
				
		for Slot in xrange(player.INVENTORY_PAGE_SIZE*2):
			ItemValue = player.GetItemIndex(Slot)
			if ItemValue == 50513:
				net.SendItemUsePacket(Slot)
				if self.State != "Stop":
					if self.GetNeededAlignment():
						self.ReadQuest(SkillIndex)
				break
				
	def CheckIndex(self, AskedSkill):
		self.ReadAbleSkillList = []
		for Count in xrange(NewSkillsEnable()):
			if self.IsReadAble(Count, 0):
				self.ReadAbleSkillList.append(Count)
		return(str(self.ReadAbleSkillList.index(AskedSkill)))
	
	def OnUpdate(self):
		if self.State != "Start":
			return
	
		if app.GetTime() >= self.TimeStamp:
			if self.IsReadAble(int(self.SkillBook[1]), 0):
				self.TimeStamp = app.GetTime() + 1
				self.ReadBooks(self.CheckIndex(int(self.SkillBook[1])))
			else:
				chat.AppendChat(1, "This Skill doesn´t have the level which is needed to read!")
				self.Stop()
		
	def ReadQuest(self, index):
		if self.State == "Stop":
			return
		import event
		#start
	#	if self.ReadExo:
		event.SelectAnswer(1, 254)
		event.SelectAnswer(1, 0)
		event.SelectAnswer(1, int(index))
		#say you want to read
		event.SelectAnswer(1, 0)
		#send string packet
		net.SendQuestInputStringPacket(self.Gui[14].GetText())		
		#sucess/fail
		event.SelectAnswer(1, 0)
		
	def IsReadAble(self, count, state):
		Skillgrade = player.GetSkillGrade(count)
		Skilllevel = player.GetSkillLevel(count)

		if 1 == Skillgrade:
			Skilllevel += 19
		elif 2 == Skillgrade:
			Skilllevel += 29
		elif 3 == Skillgrade:
			Skilllevel = 40
		
		if state != 1:
			if Skilllevel > 29 and Skilllevel < 40:
				return 1	
		else:
			return(Skilllevel)
		
	def StartReading(self):
		ItemIndex = self.Gui[3].GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(chat.CHAT_TYPE_INFO, "No Item selected!")
			return
		self.SkillBook = ItemIndex.GetText().split("      ")
		
		RaceGroupInfo = GetClass().split("/")

		self.TimeStamp = app.GetTime()
		self.State = "Start"	
		self.InstallQuestWindowHook()
	
	def InstallQuestWindowHook(self):
		self.OldRecv = game.GameWindow.OpenQuestWindow
		game.GameWindow.OpenQuestWindow = self.HookedQuestWindow
	#	chat.AppendChat(1, "Quest Window wurde erfolgreich gehooked.")		
		
	def UnHookQuestWindow(self):
		game.GameWindow.OpenQuestWindow = self.OldRecv
	#	chat.AppendChat(1, "Quest Window Hook wurde entfernt.")
		
	def HookedQuestWindow(self, skin, idx):
		pass
		
	def Stop(self):
		self.Start = 0
		self.Gui[7].Hide()
		self.Gui[6].Show()
		self.BreakReading()
		
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

def NewSkillsEnable():
	playersettingmodule = EterPackOperator("playersettingmodule.py").read()
	RaceGroupInfo = GetClass()
	Class = str(RaceGroupInfo).split("/")[0]
	if str(playersettingmodule).find("NEW_678TH_SKILL_ENABLE = TRUE") or str(playersettingmodule).count("36") >= 4 or str(Class) == "Shaman" or str(Class) == "Sura":
		return 6
	else:
		return 5
		
def GetClass():
	race = net.GetMainActorRace()
	group = net.GetMainActorSkillGroup()
	if race == 0 or race == 4:
		return "Warrior" + "/" + str(group)
	elif race == 1 or race == 5:
		return "Assassin" + "/" + str(group)
	elif race == 2 or race == 6:
		return "Sura" + "/" + str(group)
	elif race == 3 or race == 7:
		return "Shaman" + "/" + str(group)
		

		