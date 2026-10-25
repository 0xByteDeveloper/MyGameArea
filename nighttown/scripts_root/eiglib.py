import chat
import net
import player
import ui
import chr
import app
import math
import introLogin
import time
import thread
import threading
import os
import wndMgr
import __builtin__
import snd
import shop

chat.AppendChat(1, "Metin2 Useful Functions")
chat.AppendChat(1, "Date: 22.08.2013")
chat.AppendChat(1, "Author: Eigenartig")

##Information chat
def SendInformationChat(text):
	chat.AppendChat(1, str(text))

#Item dropper	
def DropTheseItems(start, stop):
	for Slot in xrange(int(start), int(stop)):
		net.SendItemDropPacket(Slot)

##Separater		
def SeparateItem(slotnum):
	for i in xrange(0, 90):
		ItemValue = player.GetItemIndex(i)
		if int(ItemValue == 0):
			net.SendItemMovePacket(int(slotnum), int(i), 1)

##Python loader			
def LoadPythonFile(name):
	try:
		pyScrLoader = ui.PythonScriptLoader()
		pyScrLoader.LoadScriptFile(0, str(name))
	except:
		chat.AppendChat(1, "File couldn't loaded")
	
##Teleport	
def Teleport(aimx, aimy):
	(TmpX, TmpY, Count) = GetTmpTeleport(aimx, aimy)
	TmpCount = 0
	
	while TmpCount < Count:
		(TmpX, TmpY, Crap) = GetTmpTeleport(aimx, aimy)
		chr.SetPixelPosition(int(TmpX), int(TmpY))
		TmpCount += 1
		Debug()
				
	chr.SetPixelPosition(int(aimx), int(aimy))
	Debug()

def Debug():
	player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
	player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
		
def GetTmpTeleport(DestX, DestY):
	(PlayerX, PlayerY, PlayerZ) = player.GetMainCharacterPosition()
	DifX = DestX - PlayerX
	DifY = DestY - PlayerY
	Vektor = DivideToFloat(2000, math.sqrt(DifX**2 + DifY**2))
	TempX = PlayerX + Vektor*DifX
	TempY = PlayerY + Vektor*DifY
	Count = DivideToFloat((DestX - PlayerX), (Vektor*DifX))
	return (TempX, TempY, Count)
	
def DivideToFloat(x, y):
	try:
		return x * (y**-1)
	except:
		return 0

##Channel changer
def ConnectToChannel(AccountID, Password, serverNum, serverChannel, characterPos):
	serverName = serverInfo.REGION_DICT[0][serverNum]["name"]
	channelName = serverInfo.REGION_DICT[0][serverNum]["channel"][serverChannel]["name"]
	##
	addr_new = serverInfo.REGION_DICT[0][serverNum]["channel"][serverChannel]["ip"]
	port_new = serverInfo.REGION_DICT[0][serverNum]["channel"][serverChannel]["tcp_port"]
	account_addr_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]["ip"]
	account_port_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]["port"]
	##
	net.SetServerInfo("%s, %s " % (serverName, channelName))	
	net.SetLoginInfo(AccountID, Password)
	net.SetPacketSequenceMode()
	net.ConnectToAccountServer(addr_new, port_new, account_addr_new, account_port_new)
	net.DirectEnter(0)
	net.SendSelectCharacterPacket(characterPos)
	net.SendEnterGamePacket()
	
	net.SendSelectCharacterPacket = 
	
	import game

original=game.GameWindow.OpenQuestWindow
def InitHook(*args):
 game.GameWindow.OpenQuestWindow=original
 
game.GameWindow.OpenQuestWindow=InitHook

	
##Walk Mods
def WalkVID(vid):
	x, y, z = chr.GetPixelPosition(vid)
	myVid = player.GetMainCharacterIndex()
	myx, myy, myz = player.GetMainCharacterPosition()
	distance = 135
	
	if myx < x:
		aimx = int(x) - distance
	else:
		aimx = int(x)  + distance
	if myy < y:
		aimy = int(y) - distance
	else:
		aimy = int(y) + distance
		
	chr.MoveToDestPosition(int(myVid), int(aimx), int(aimy))
	
def WalkCOORD(x, y):
	myVid = player.GetMainCharacterIndex()
	myx, myy, myz = player.GetMainCharacterPosition()
	distance = 135
	
	if myx < x:
		aimx = int(x) - distance
	else:
		aimx = int(x)  + distance
	if myy < y:
		aimy = int(y) - distance
	else:
		aimy = int(y) + distance
		
	chr.MoveToDestPosition(int(myVid), int(aimx), int(aimy))
	
##Attack VID
def SendAttack(vid):
	Distance = player.GetCharacterDistance(vid)
	myx, myy, myz = player.GetMainCharacterPosition()
	mobX, mobY, mobZ = chr.GetPixelPosition(vid)		
	if Distance <= 210:
		chr.SetRotation(GetDegree(mobX, mobY, myx, myy))
		player.SetAttackKeyState(TRUE)	
	else:
		player.SetAttackKeyState(FALSE)
		WalkVID(vid)
		
def GetDegree(mobX, mobY, playerX, playerY):
	try:
		rada = ConvertToDegrees(math.acos((mobY-playerY)/math.sqrt((mobX - playerX)**2 + (mobY - playerY)**2))) + 180
		if playerX >= mobX:
			rada = 360 - rada
	except:
		rada = 0
	return rada
	
def ConvertToDegrees(value):
	return 180 * value / math.pi
	
##Give item to vid
def GiveItemTo(start, stop, vid, count):
	for i in xrange(int(start), int(stop)):
		net.SendGiveItemPacket(int(vid), int(i), int(count))
		
##Use Item
def UseItem(value):
	for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
		ItemIndex = player.GetItemIndex(InventorySlot)
		if value == ItemIndex:
			net.SendItemUsePacket(InventorySlot)
			break
			
##Buy Item
def BuyItem(value):
	if shop.IsOpen(): 
		for ShopSlot in xrange(shop.SHOP_SLOT_COUNT): 
			getShopItemID = shop.GetItemID(ShopSlot) 
			if getShopItemID == value: 
				net.SendShopBuyPacket(ShopSlot) 
	else:
		chat.AppendChat(1, "You must open a shop!")

##IsMoneyOkay
def IsMoneyOkay(value):
	if shop.IsOpen(): 
		for ShopSlot in xrange(shop.SHOP_SLOT_COUNT): 
			getShopItem = shop.GetItemID(ShopSlot) 
			if getShopItem == value: 	
				itemPrice = shop.GetItemPrice(ShopSlot)
				myMoney = player.GetElk()
				need_money = int(itemPrice)-int(myMoney)
				if itemPrice >= myMoney:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "You haven't got enough money! You need:  "+str(need_money)+" yang")
					return 0
				else:
					return 1
	else:
		chat.AppendChat(1, "You must open a shop!")					
##Upgrade
def UpgradeItem(Slot, type, count):
	BannedSlotIndex = []
	for i in xrange(count):
		#Normal Upgrade
		if type == 0:
			net.SendRefinePacket(Slot, 0)
	
		#Guild Blacksmith Upgrade
		elif type == 1:
			net.SendRefinePacket(Slot, 1)
			
		#Bless Scroll Upgrade
		elif type == 2:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemValue = player.GetItemIndex(InventorySlot)
				if ItemValue == 25040 and not InventorySlot in BannedSlotIndex:
					BannedSlotIndex.append(InventorySlot)
					net.SendItemUseToItemPacket(InventorySlot, Slot)
					net.SendRefinePacket(Slot, 2)
					break
			
		#Magic Metal Upgrade
		elif type == 3:
			for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemValue = player.GetItemIndex(InventorySlot)
				if ItemValue == 25041 and not InventorySlot in BannedSlotIndex:
					BannedSlotIndex.append(InventorySlot)
					net.SendItemUseToItemPacket(InventorySlot, Slot)
					net.SendRefinePacket(Slot, 3)
					break
						
		#Deviltower Upgrade
		elif type == 4:
			net.SendRefinePacket(Slot, 4)
		
##Send Whisper To Everybody
def SendEverybody(message):			
	VidList = [vid for vid in xrange(600000) if chr.GetInstanceType(vid) == 6 and chr.GetNameByVID(vid) != "None"]
	for xd in VidList:
		net.SendWhisperPacket(chr.GetNameByVID(xd), message)

##Send Chat
def SendChat(chattype, message):
	##Shout
	if chattype == 0:
		if player.GetStatus(player.LEVEL) >= 15:
			net.SendChatPacket(message, 6)
		else:
			chat.AppendChat(1, "You must be 15 level or more.")
	##Normal Chat
	elif chattype == 1:
		net.SendChatPacket(message, 0)	
	##Guild Chat	
	elif chattype == 2:
		if player.GetGuildID() != 0:
			net.SendChatPacket(message, 4)
		else:
			chat.AppendChat(1, "You haven't got a guild.")
	##Party Chat
	elif chattype == 3:
		if chr.IsPartyMember(player.GetMainCharacterIndex()):
			net.SendChatPacket(message, 3)
		else:
			chat.AppendChat(1, "You haven't got a party xD.")

##Game Master Detector
def IsGameMasterHere(apply):
	VidList = [vid for vid in xrange(600000) if chr.GetInstanceType(vid) == chr.INSTANCE_TYPE_PLAYER and chr.GetNameByVID(vid) != "None" and (chr.IsGameMaster(vid) or chr.GetNameByVID(vid)[0] == "[")]		
	if len(VidList) != 0:
		for xd in VidList:
			if apply ==0:
				chat.AppendChat(1, "Game Master: "+str(chr.GetNameByVID(xd))+" is here.")
			elif apply ==1:
				chat.AppendChat(1, "You'll be kicked in 2 seconds.")
				threading.Timer(2.5, KickMe).start()
			elif apply ==2:
				app.Exit()
							
	else:
		chat.AppendChat(1, "There is not Game Master around.")

##Self kicker		
def KickMe():
	thread.start_new_thread( lambda: (
		player.SetSingleDIKKeyState(app.DIK_UP, TRUE), 
		[net.LogOutGame() for i in xrange(251)], time.sleep(1.0), 
		player.SetSingleDIKKeyState(app.DIK_UP, FALSE),
	), ())
	
##Write to text
def WriteToFile(filename, text):
	open(filename, "a+").write(text + "\n")	
	
#GM mods
def GameMasterCommand(type=0, name="", value_1=0, value_2=0, value_3=0):
	chat_dict = {
	0: "/i %s %s" % (value_1, value_2),
	1: "/warp %s" % (name),
	2: "/transfer %s" % (name),
	3: "/set %s align %s" % (name, value_1),
	4: "/m %s %s" % (value_1, value_2),
	5: "/set %s gold %s" % (name, value_1),
	6: [lambda: net.SendChatPacket("/setskillother %s %s %s" % (name, index, value_3)) for index in xrange(value_1, value_2)],
	7: "/polyitem %s" % (value_1),
	8: "/level %s" % (value_1),
	9: "/purge",
	10: "/b %s" % (value_1),
	11: "/n %s" % (value_1),
	12: "/kill %s" % (name), 
	13: "/x %s" % (value_1),
	14: "/dc %s" % (name), 
	15: "/ip",
	16: "/r",
	17: "/horse_level %s %s" % (name, value_1),
	18: "/a %s %s" % (name, value_1),
	19: "/stun %s" % (name),
	20: "/slow %s" % (name),
	21: [lambda: net.SendChatPacket("/setsk %s %s" % (index, value_3)) for index in xrange(value_1, value_2)],
	}
	result = chat_dict[type]
	if isinstance(result, list):
		for cmd in result:
			cmd()
	else:
		net.SendChatPacket(result)
	
def GoAsGameMaster(type):
	chat_dict = {
	0: "/go d",
	1: "/go f",
	2: "/go tr",
	3: "/go trent02",
	4: "/go s",
	5: "/go t",
	6: "/go m",
	7: "/go a",
	8: "/go a3",
	9: "/go b",
	10: "/go b3",
	11: "/go c",
	12: "/go c3",
	13: "/go ox",
	14: "/warp 7050 4650",
	15: "/warp 5910 1110",	
	}
	
	result = chat_dict[type]
	net.SendChatPacket(result)	
	
##Teleport [Arrow]
def Teleport2(side):	
	if side == "up":
		(x, y, z) = player.GetMainCharacterPosition()
		chr.SetPixelPosition(int(x), int(y) - 2000, int(z))
	elif side == "down":
		(x, y, z) = player.GetMainCharacterPosition()
		chr.SetPixelPosition(int(x), int(y) + 2000, int(z))	
	elif side == "right":
		(x, y, z) = player.GetMainCharacterPosition()
		chr.SetPixelPosition(int(x) + 2000, int(y), int(z))
	elif side == "left":
		(x, y, z) = player.GetMainCharacterPosition()
		chr.SetPixelPosition(int(x) - 2000, int(y), int(z))	
	player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
	player.SetSingleDIKKeyState(app.DIK_UP, FALSE)		
	
##Get Class
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
	
##New Skills Enable
def NewSkillsEnable():
	playersettingmodule = EterPackOperator("playersettingmodule.py").read()
	RaceGroupInfo = GetClass()
	Class = str(RaceGroupInfo).split("/")[0]
	if str(playersettingmodule).find("NEW_678TH_SKILL_ENABLE = TRUE") or str(playersettingmodule).count("36") >= 4 or str(Class) == "Shaman" or str(Class) == "Sura":
		return 6
	else:
		return 5	
	
##Eter Pack Operator
class EterPackOperator(object):

	def __init__(self, filename):
		_chr = __builtin__.chr
		self.data = self.GetTextFile(filename)
		self.data=_chr(10).join(self.data.split(_chr(13)+_chr(10)))

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
	
##Toggle Button
class Button(ui.Window):
    __module__ = __name__
    def __init__(self, layer = 'UI'):
        ui.Window.__init__(self, layer)
        self.eventFunc = None
        self.eventArgs = None
        self.ButtonText = None
        self.ToolTipText = None
    def __del__(self):
        ui.Window.__del__(self)
        self.eventFunc = None
        self.eventArgs = None
    def RegisterWindow(self, layer):
        self.hWnd = wndMgr.RegisterButton(self, layer)
    def SetUpVisual(self, filename):
        wndMgr.SetUpVisual(self.hWnd, filename)
    def SetOverVisual(self, filename):
        wndMgr.SetOverVisual(self.hWnd, filename)
    def SetDownVisual(self, filename):
        wndMgr.SetDownVisual(self.hWnd, filename)
    def SetDisableVisual(self, filename):
        wndMgr.SetDisableVisual(self.hWnd, filename)
    def GetUpVisualFileName(self):
        return wndMgr.GetUpVisualFileName(self.hWnd)
    def GetOverVisualFileName(self):
        return wndMgr.GetOverVisualFileName(self.hWnd)
    def GetDownVisualFileName(self):
        return wndMgr.GetDownVisualFileName(self.hWnd)
    def Flash(self):
        wndMgr.Flash(self.hWnd)
    def Enable(self):
        wndMgr.Enable(self.hWnd)
    def Disable(self):
        wndMgr.Disable(self.hWnd)
    def Down(self):
        wndMgr.Down(self.hWnd)
    def SetUp(self):
        wndMgr.SetUp(self.hWnd)
    def SAFE_SetEvent(self, func, *args):
        self.eventFunc = ui.__mem_func__(func)
        self.eventArgs = args
    def SetEvent(self, func, *args):
        self.eventFunc = func
        self.eventArgs = args
    def SetTextColor(self, r, b, g):
        if (not self.ButtonText):
            return 
        self.ButtonText.SetFontColor(r, g, b)
    def SetButtonFontName(self, font):
        if (not self.ButtonText):
            return 
        BackUpText = self.ButtonText.GetText()
        self.ButtonText.SetFontName(font)
        self.ButtonText.SetText('')
        self.ButtonText.SetText(str(BackUpText))
    def SetText(self, text, height = 4):
        if (not self.ButtonText):
            self.ButtonText = ui.TextLine()
            self.ButtonText.SetParent(self)
            self.ButtonText.SetPosition((self.GetWidth() / 2), (self.GetHeight() / 2))
            self.ButtonText.SetVerticalAlignCenter()
            self.ButtonText.SetHorizontalAlignCenter()
            self.ButtonText.Show()
        self.ButtonText.SetText(text)
    def SetTextPosition(self, x, y):
        self.ButtonText.SetPosition(((self.GetWidth() / 2) + int(x)), ((self.GetHeight() / 2) + int(y)))
    def SetFormToolTipText(self, type, text, x, y):
        if (not self.ToolTipText):
            toolTip = ui.createToolTipWindowDict[type]()
            toolTip.SetParent(self)
            toolTip.SetSize(0, 0)
            toolTip.SetHorizontalAlignCenter()
            toolTip.SetOutline()
            toolTip.Hide()
            toolTip.SetPosition((x + (self.GetWidth() / 2)), y)
            self.ToolTipText = toolTip
        self.ToolTipText.SetText(text)
    def SetToolTipWindow(self, toolTip):
        self.ToolTipText = toolTip
        self.ToolTipText.SetParentProxy(self)
    def SetToolTipText(self, text, x = 0, y = -19):
        self.SetFormToolTipText('TEXT', text, x, y)
    def CallEvent(self):
        snd.PlaySound('sound/ui/click.wav')
        if self.eventFunc:
            apply(self.eventFunc, self.eventArgs)
    def ShowToolTip(self):
        if self.ToolTipText:
            self.ToolTipText.Show()
    def HideToolTip(self):
        if self.ToolTipText:
            self.ToolTipText.Hide()
    def IsDown(self):
        return wndMgr.IsDown(self.hWnd)		
class ToggleButton(Button):
    __module__ = __name__
    def __init__(self):
        Button.__init__(self)
        self.eventUp = None
        self.eventDown = None
        self.ToolTipText = None
    def __del__(self):
        Button.__del__(self)
        self.eventUp = None
        self.eventDown = None
    def SetToggleUpEvent(self, event):
        self.eventUp = event
    def SetToggleDownEvent(self, event):
        self.eventDown = event
    def RegisterWindow(self, layer):
        self.hWnd = wndMgr.RegisterToggleButton(self, layer)
    def SetTextPosition(self, x, y):
        self.ButtonText.SetPosition(((self.GetWidth() / 2) + int(x)), ((self.GetHeight() / 2) + int(y)))
    def OnToggleUp(self):
        if self.eventUp:
            self.eventUp()
    def OnToggleDown(self):
        if self.eventDown:
            self.eventDown()
    def Down(self):
        wndMgr.Down(self.hWnd)
    def SetUp(self):
        wndMgr.SetUp(self.hWnd)
    def SetFormToolTipText(self, type, text, x, y):
        if (not self.ToolTipText):
            toolTip = ui.createToolTipWindowDict[type]()
            toolTip.SetParent(self)
            toolTip.SetSize(0, 0)
            toolTip.SetHorizontalAlignCenter()
            toolTip.SetOutline()
            toolTip.Hide()
            toolTip.SetPosition((x + (self.GetWidth() / 2)), y)
            self.ToolTipText = toolTip
        self.ToolTipText.SetText(text)
    def SetToolTipWindow(self, toolTip):
        self.ToolTipText = toolTip
        self.ToolTipText.SetParentProxy(self)
    def SetToolTipText(self, text, x = 0, y = -19):
        self.SetFormToolTipText('TEXT', text, x, y)
    def ShowToolTip(self):
        if self.ToolTipText:
            self.ToolTipText.Show()
    def HideToolTip(self):
        if self.ToolTipText:
            self.ToolTipText.Hide()
    def Enable(self):
        wndMgr.Enable(self.hWnd)
    def Disable(self):
        wndMgr.Disable(self.hWnd)

##Skill Button		
class SkillButton(ui.Window):
	def __init__(self, layer = "UI"):
		ui.Window.__init__(self, layer)
		self.eventFunc = None
		self.eventArgs = None
		self.ButtonText = None
		self.ToolTipText = None
	def __del__(self):
		ui.Window.__del__(self)
		self.eventFunc = None
		self.eventArgs = None
	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterButton(self, layer)
	def SetUpVisual(self, filename):
		wndMgr.SetUpVisual(self.hWnd, filename)
	def SetOverVisual(self, filename):
		wndMgr.SetOverVisual(self.hWnd, filename)
	def SetDownVisual(self, filename):
		wndMgr.SetDownVisual(self.hWnd, filename)
	def SetDisableVisual(self, filename):
		wndMgr.SetDisableVisual(self.hWnd, filename)
	def GetUpVisualFileName(self):
		return wndMgr.GetUpVisualFileName(self.hWnd)
	def GetOverVisualFileName(self):
		return wndMgr.GetOverVisualFileName(self.hWnd)
	def GetDownVisualFileName(self):
		return wndMgr.GetDownVisualFileName(self.hWnd)
	def Flash(self):
		wndMgr.Flash(self.hWnd)
	def Enable(self):
		wndMgr.Enable(self.hWnd)
	def Disable(self):
		wndMgr.Disable(self.hWnd)
	def Down(self):
		wndMgr.Down(self.hWnd)
	def SetUp(self):
		wndMgr.SetUp(self.hWnd)
	def SAFE_SetEvent(self, func, *args):
		self.eventFunc = ui.__mem_func__(func)
		self.eventArgs = args		
	def SetEvent(self, func, *args):
		self.eventFunc = func
		self.eventArgs = args
	def SetTextColor(self, r, b, g):
		if not self.ButtonText:
			return
		self.ButtonText.SetFontColor(r, g, b)
	def SetButtonFontName(self, font):
		if not self.ButtonText:
			return
		BackUpText = self.ButtonText.GetText()	
		self.ButtonText.SetFontName(font)
		self.ButtonText.SetText("")
		self.ButtonText.SetText(str(BackUpText))		
	def SetText(self, text, height = 4):
		if not self.ButtonText:
			self.ButtonText = ui.TextLine()
			self.ButtonText.SetParent(self)
			self.ButtonText.SetPosition(self.GetWidth() / 2, self.GetHeight() / 2)
			self.ButtonText.SetVerticalAlignCenter()
			self.ButtonText.SetHorizontalAlignCenter()
			self.ButtonText.Show()
		self.ButtonText.SetText(text)
	def SetTextPosition(self, x, y):
		self.ButtonText.SetPosition(self.GetWidth() / 2 + int(x), self.GetHeight() / 2 + int(y))			
	def SetFormToolTipText(self, type, text, x, y):
		if not self.ToolTipText:		
			toolTip = ui.createToolTipWindowDict[type]()
			toolTip.SetParent(self)
			toolTip.SetSize(0, 0)
			toolTip.SetHorizontalAlignCenter()
			toolTip.SetOutline()
			toolTip.Hide()
			toolTip.SetPosition(x + self.GetWidth()/2, y)
			self.ToolTipText=toolTip
		self.ToolTipText.SetText(text)
	def SetToolTipWindow(self, toolTip):		
		self.ToolTipText = toolTip		
		self.ToolTipText.SetParentProxy(self)
	def SetToolTipText(self, text, x=0, y = -19):
		self.SetFormToolTipText("TEXT", text, x, y)
	def CallEvent(self):
		snd.PlaySound("sound/ui/click.wav")
		if self.eventFunc:
			apply(self.eventFunc, self.eventArgs)
	def ShowToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Show()
	def HideToolTip(self):
		if self.ToolTipText:
			self.ToolTipText.Hide()
	def IsDown(self):
		return wndMgr.IsDown(self.hWnd)

##IconBox
class IconBox(ui.ImageBox):
	def __init__(self, layer = "UI"):
		ui.ImageBox.__init__(self, layer)
	def __del__(self):
		ui.ImageBox.__del__(self)
	def RegisterWindow(self, layer):
		self.hWnd = wndMgr.RegisterExpandedImageBox(self, layer)
	def SetScale(self, xScale, yScale):
		wndMgr.SetScale(self.hWnd, xScale, yScale)		
	def SetToolTipText(self, text, x = 0, y = -19):
		if not self.toolTipText:
			textLine = ui.TextLine()
			textLine.SetParent(self)
			textLine.SetSize(0, 0)
			textLine.SetOutline()
			textLine.Hide()
			self.toolTipText = textLine
			self.toolTipText.SetPosition(x + self.GetWidth()/2 - 20, y)
		self.toolTipText.SetText(text)
	def SetOrigin(self, x, y):
		wndMgr.SetOrigin(self.hWnd, x, y)
	def SetRotation(self, rotation):
		wndMgr.SetRotation(self.hWnd, rotation)
	def SetRenderingMode(self, mode):
		wndMgr.SetRenderingMode(self.hWnd, mode)
	# [0.0, 1.0] »çÀÌÀÇ °ª¸¸Å­ ÆÛ¼¾Æ®·Î ±×¸®Áö ¾Ê´Â´Ù.
	def SetRenderingRect(self, left, top, right, bottom):
		wndMgr.SetRenderingRect(self.hWnd, left, top, right, bottom)
	def SetPercentage(self, curValue, maxValue):
		if maxValue:
			self.SetRenderingRect(0.0, 0.0, -1.0 + float(curValue) / float(maxValue), 0.0)
		else:
			self.SetRenderingRect(0.0, 0.0, 0.0, 0.0)
	def GetWidth(self):
		return wndMgr.GetWindowWidth(self.hWnd)
	def GetHeight(self):
		return wndMgr.GetWindowHeight(self.hWnd)	
		
##Map names [Turkish]		
MapNameDict = {	
	"metin2_map_a1":"Yongan(Shinsoo)", 	
	"metin2_map_a3":"Jayang(Shinsoo)", 	
	"metin2_map_b1":"Joan(Chunjo)", 	
	"metin2_map_b3":"Bokjung(Chunjo)",	
	"metin2_map_c1":"Pyungmoo(Chunjo)",	
	"metin2_map_c3":"Bakra(Chunjo)",
	"map_a2":"Seungr. Vadisi",	
	"map_n_snowm_01":"Sohan Dagi",	
	"metin2_map_n_desert_01":"Yongbi Colu",	
	"metin2_map_deviltower1":"Seytan Kulesi",	
	"metin2_map_guild_01":"Jungrang(Lonca)",	
	"metin2_map_guild_02":"Waryong(Lonca)",	
	"metin2_map_guild_03":"Imha(Lonca)",	
	"metin2_guild_village_01":"Miryan(Lonca Savasi)",	
	"metin2_guild_village_02":"Songpa(Lonca Savasi)",	
	"metin2_guild_village_03":"Daeyami(Lonca Savasi)",	
	"metin2_map_milgyo":"Hwang Tapinagi",	
	"metin2_map_monkeydungeon":"Maymun Z.(Kolay)",	
	"metin2_map_monkeydungeon_02":"Maymun Z.(Normal)",	
	"metin2_map_monkeydungeon_03":"Maymun Z.(Uzman)",	
	"metin2_map_n_flame_01":"Doyumhwan",	
	"metin2_map_spiderdungeon":"O. Zindani 1.Kat",	
	"metin2_map_spiderdungeon_02":"O. Zindani 2.Kat",	
	"metin2_map_spiderdungeon_03":"O. Zindani 3.Kat",	
	"metin2_map_trent":"Hayalet Ormani",	
	"metin2_map_trent02":"Kizil Orman",	
	"metin2_map_skipia_dungeon_01":"Surgun M. 1.Kat",	
	"metin2_map_skipia_dungeon_02":"Surgun M. 2.Kat",
	"metin2_map_devilscatacomb":"Seytan'in Catacombu",
	"metin2_map_CapeDragonHead":"Pelerin",
	"metin2_map_BayBlackSand":"Koy",
	"metin2_map_MT_Thunder":"Gok Gurultusu",
	"metin2_map_dawnmistwood":"Safak",
	"season1/metin2_map_nusluck01":"Devler Diyari",
	"season1/metin2_map_WL_01":"Yilan Vadisi",
}

IsBuff = { "1": {"IsBuff": 0}, "2": {"IsBuff": 0}, "3": {"IsBuff": 1}, "4": {"IsBuff": 1}, "5": {"IsBuff": 0}, "6": {"IsBuff": 0}, "16": {"IsBuff": 0}, "17": {"IsBuff": 0}, "18": {"IsBuff": 0}, "19": {"IsBuff": 1}, "20": {"IsBuff": 0}, "21": {"IsBuff": 0}, "31": {"IsBuff": 0}, "32": {"IsBuff": 0}, "33": {"IsBuff": 0}, "34": {"IsBuff": 1}, "35": {"IsBuff": 0}, "36": {"IsBuff": 0}, "46": {"IsBuff": 0}, "47": {"IsBuff": 0}, "48": {"IsBuff": 0}, "49": {"IsBuff": 1}, "50": {"IsBuff": 0}, "51": {"IsBuff": 0}, "61": {"IsBuff": 0}, "62": {"IsBuff": 0}, "63": {"IsBuff": 0}, "64": {"IsBuff": 0}, "65": {"IsBuff": 0}, "66": {"IsBuff": 0}, "76": {"IsBuff": 0}, "77": {"IsBuff": 0}, "78": {"IsBuff": 0}, "79": {"IsBuff": 1}, "80": {"IsBuff": 1}, "81": {"IsBuff": 0}, "91": {"IsBuff": 0}, "92": {"IsBuff": 0}, "93": {"IsBuff": 0}, "94": {"IsBuff": 1}, "95": {"IsBuff": 1}, "96": {"IsBuff": 1}, "106": {"IsBuff": 0}, "107": {"IsBuff": 0}, "108": {"IsBuff": 0}, "109": {"IsBuff": 1}, "110": {"IsBuff": 1}, "111": {"IsBuff": 1}}


		##types:[0:Chat, 1:Log Out, 2:Quit Game]
		##types:[0:Shout, 1:Normal Chat, 2:Guild Chat, 3:Party Chat]
		##types:[0:Blacksmith, 1:Guild Blacksmith, 2:Bless Scroll, 3:Magic Metal, 4:Dewiltower]
		
