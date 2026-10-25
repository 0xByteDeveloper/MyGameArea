import ui
import player
import chr
import chat
import chrmgr
import time
import skill
import nonplayer
import net
import snd
import item
import pack
import app

class NewLevelBotDialog(ui.Window):
	MobList = []
	SkillList = []
	SkillIconList = []
	SkillIconIndex = []
	ActiveSkillList = []
	startscan = 100
	endscan = 400000
	vid = 0
	AutoPotionRedPercent = 0
	AutoPotionBluePercent = 0
	
	def __init__(self):
		ui.Window.__init__(self)
		self.SetVIDRange()
		self.AddMobData()
		self.AddSkillIcons()
		self.AddPotionBar()
#		self.AttackMob()
		
	def SetVIDRange(self):
		Found = 0
		Start = 0
		End = 1000000
		for loop in xrange(1, 7):
			for i in xrange(Start, End):
				if chr.INSTANCE_TYPE_ENEMY == chr.GetInstanceType(i):
					self.startscan = int(i) - 500
					self.endscan = int(i) + 50000
					Found = 1
					break
			if Found == 0:
				Start = End
				End = End + 1000000
		chat.AppendChat(chat.CHAT_TYPE_INFO, "VID Range: " + str(self.startscan) + " - " + str(self.endscan))				
		
	def AddPotionBar(self):
		item.SelectItem(int(27003))
		ItemIcon = item.GetIconImageFileName()
		self.RedPotionImage = ui.ExpandedImageBox()
		self.RedPotionImage.SetPosition(wndMgr.GetScreenWidth() - 150, wndMgr.GetScreenHeight() / 2 - 100)
		self.RedPotionImage.LoadImage(str(ItemIcon))
		self.RedPotionImage.Show()
		
		self.RedPotionPercentText = ui.TextLine()
		self.RedPotionPercentText.SetDefaultFontName()
		self.RedPotionPercentText.SetPosition(wndMgr.GetScreenWidth() - 120, wndMgr.GetScreenHeight() / 2 - 90)
		self.RedPotionPercentText.SetFeather()
		self.RedPotionPercentText.SetText("50%")
		self.RedPotionPercentText.SetOutline()
		self.RedPotionPercentText.Show()

		self.RedPotionSlider = ui.SliderBar()
		self.RedPotionSlider.SetPosition(wndMgr.GetScreenWidth() - 220, wndMgr.GetScreenHeight() / 2 - 60)
		self.RedPotionSlider.SetEvent(ui.__mem_func__(self.SetPotion))
		self.RedPotionSlider.SetSliderPos(0.5)
		self.RedPotionSlider.Show()
		
		
		item.SelectItem(int(27006))
		ItemIcon = item.GetIconImageFileName()
		self.BluePotionImage = ui.ExpandedImageBox()
		self.BluePotionImage.SetPosition(wndMgr.GetScreenWidth() - 150, wndMgr.GetScreenHeight() / 2 - 40)
		self.BluePotionImage.LoadImage(str(ItemIcon))
		self.BluePotionImage.Show()

		self.BluePotionPercentText = ui.TextLine()
		self.BluePotionPercentText.SetDefaultFontName()
		self.BluePotionPercentText.SetPosition(wndMgr.GetScreenWidth() - 120, wndMgr.GetScreenHeight() / 2 - 30)
		self.BluePotionPercentText.SetFeather()
		self.BluePotionPercentText.SetText("50%")
		self.BluePotionPercentText.SetOutline()
		self.BluePotionPercentText.Show()
		
		self.BluePotionSlider = ui.SliderBar()
		self.BluePotionSlider.SetPosition(wndMgr.GetScreenWidth() - 220, wndMgr.GetScreenHeight() / 2)
		self.BluePotionSlider.SetEvent(ui.__mem_func__(self.SetPotion))
		self.BluePotionSlider.SetSliderPos(0.5)
		self.BluePotionSlider.Show()

	def SetPotion(self):
		self.AutoPotionRedPercent = int(self.RedPotionSlider.GetSliderPos() * 100)
		self.AutoPotionBluePercent = int(self.BluePotionSlider.GetSliderPos() * 100)
		self.RedPotionPercentText.SetText(str(int(self.RedPotionSlider.GetSliderPos() * 100)) + "%")
		self.BluePotionPercentText.SetText(str(int(self.BluePotionSlider.GetSliderPos() * 100)) + "%")
		
	def AddMobData(self):
		Count = 0
		for i in xrange(int(self.startscan), int(self.endscan)):
			if chr.INSTANCE_TYPE_ENEMY == chr.GetInstanceType(i):
				chr.SelectInstance(i)
				Alive = self.IsAlive(i)
				if int(Alive) == 1:
					vid = int(i)
					level = nonplayer.GetLevelByVID(i)
					vnum = chr.GetRace(i)
					mobX, mobY, mobZ = chr.GetPixelPosition(i)
					Distance = player.GetCharacterDistance(i)
					MobData = { 
						"VNUM":vnum,
						"LEVEL":level,
						"X":mobX,
						"Y":mobY,
						"Z":mobZ,
						"VID":vid,
						"COUNT":Count,
						"DISTANCE":Distance,
						}
					Count += 1
					self.MobList.append(MobData)
		
		if len(self.MobList) != 0:
			self.CheckNearestMob()
		
	def IsAlive(self, vid): ##doesn't work yet
		info = chrmgr.GetVIDInfo(vid)
		return info.split("isAlive=")[1][0]
		
	def CheckNearestMob(self):
		NearestMob = 0
		
		for data in self.MobList:
			Vnum = str(data["VNUM"])
			Level = str(data["LEVEL"])
			Distance = float(data["DISTANCE"])
			Vid = str(data["VID"])
			Count = str(data["COUNT"])
			if float(Distance) < float(self.MobList[NearestMob]["DISTANCE"]):
				NearestMob = int(Count)

		x = float(self.MobList[int(NearestMob)]["X"])
		y = float(self.MobList[int(NearestMob)]["Y"])
		z = float(self.MobList[int(NearestMob)]["Z"])
		vid = int(self.MobList[int(NearestMob)]["VID"])
#		chat.AppendChat(chat.CHAT_TYPE_INFO, "Nächster Mob: " + str(chr.GetNameByVID(self.MobList[int(NearestMob)]["VID"])))
		self.TeleportToMob(x, y, z, vid)
		self.MobList = []
		
	def TeleportToMob(self, x, y, z, vid):
		self.vid = vid
		myVid = player.GetMainCharacterIndex()
		chr.SelectInstance(myVid)
		chr.MoveToDestPosition(int(myVid), int(x), int(y))
	#	chr.SetPixelPosition(int(x), int(y), int(z))
		self.AttackMob()
		
	def AttackMob(self):
		if self.IsAlive(self.vid):
			RandomRotation = app.GetRandom(0,7)
			chr.SetDirection(RandomRotation)
			player.SetAttackKeyState(TRUE)

			self.RestartDialog = WaitingDialog()
			self.RestartDialog.Open(2.5)
			self.RestartDialog.SAFE_SetTimeOverEvent(self.AddMobData)
		else:
			self.AddMobData()
		
	def AddSkillIcons(self):
		self.SkillList = []
		try:
			handle = app.OpenTextFile("locale/de/skilldesc.txt")
			count = app.GetTextFileLineCount(handle)
		except IOError:
			import dbg
			dbg.LogBox("Load Skilldesc Error")
			app.Abort()

		for i in xrange(count):
			line = app.GetTextFileLine(handle, i)
			if str(line).count("\t") >= 21:
				SkillData = str(line).split("\t")
				SkillName = str(SkillData[2])
				SkillIconName = str(SkillData[12])
				SkillIndex = str(SkillData[0])
				SkillData = { 
					"NAME":SkillName,
					"ICON":SkillIconName,
					"INDEX":SkillIndex,
					}
				self.SkillList.append(SkillData)
		
		RaceGroupInfo = self.GetClass()
		Class = str(RaceGroupInfo).split("/")[0]
		group = str(RaceGroupInfo).split("/")[1]
		if Class == "Warrior":
			SkillIndex = 1
			if int(group) == 2:
				SkillIndex = 16
		elif Class == "Assassin":
			SkillIndex = 31
			if int(group) == 2:
				SkillIndex = 46
		elif Class == "Sura":
			SkillIndex = 61
			if int(group) == 2:
				SkillIndex = 76
		elif Class == "Shaman":
			SkillIndex = 91
			if int(group) == 2:
				SkillIndex = 106
				
		self.SkillIconIndex = []
		Count = 0
		for SkillValue in xrange(self.NewSkillsEnable()):
			Skillname = skill.GetSkillName(int(SkillIndex))
			SkillIndex += 1
			for Skills in self.SkillList:
				SkillNameList = Skills["NAME"]
				if str(Skillname) == str(SkillNameList):
					Count += 1
					SkillName = Skills["NAME"]
					SkillIcon = Skills["ICON"]
					SkillIndexAppend = SkillIndex - 1
					PrivateSkillData = { 
						"NAME":SkillName,
						"ICON":SkillIcon,
						"INDEX":SkillIndexAppend,
						"COUNT":Count,
						}
					self.SkillIconIndex.append(PrivateSkillData)

		self.GetSkillIcon()
		
	def GetSkillIcon(self):
		self.SkillIconList = []
		RaceGroupInfo = self.GetClass()
		Class = str(RaceGroupInfo).split("/")[0]
		x = 80
		i = 0
#		for Skills in self.SkillIconIndex:
#			chat.AppendChat(chat.CHAT_TYPE_INFO, "Skill Index: " + str(int(Skills["INDEX"]) - 1))
#			chat.AppendChat(chat.CHAT_TYPE_INFO, "Skill Name: " + str(Skills["NAME"]))
#			chat.AppendChat(chat.CHAT_TYPE_INFO, "Skill Icon: d:/ymir work/ui/skill/" + str(Class).lower() + "/" + str(Skills["ICON"]))

		for Skills in self.SkillIconIndex:
			SkillIconButton = SkillButton()
			SkillIconButton.SetPosition(wndMgr.GetScreenWidth() - x, wndMgr.GetScreenHeight() / 2 - 160)
			SkillIconButton.SetUpVisual("d:/ymir work/ui/skill/" + str(Class).lower() + "/" + str(Skills["ICON"]) + "_0" + str(self.GetSkillLevel(str(Skills["NAME"]))) + ".sub")
			SkillIconButton.SetOverVisual("d:/ymir work/ui/skill/" + str(Class).lower() + "/" + str(Skills["ICON"]) + "_0" + str(self.GetSkillLevel(str(Skills["NAME"]))) + ".sub")
			SkillIconButton.SetDownVisual("d:/ymir work/ui/skill/" + str(Class).lower() + "/" + str(Skills["ICON"]) + "_0" + str(self.GetSkillLevel(str(Skills["NAME"]))) + ".sub")
			SkillIconButton.SetText("Off")
			SkillIconButton.SetTextColor(0.1, 0.7, 1.0)
			SkillIconButton.SetButtonFontName("MAGNETO:16")
			SkillIconButton.SetTextPosition(0, 22)
			SkillIconButton.Show()
			
			SkillActivated = SkillButton()
			SkillActivated.SetPosition(wndMgr.GetScreenWidth() - x, wndMgr.GetScreenHeight() / 2 - 160)
			SkillActivated.SetUpVisual("d:/ymir work/ui/public/slot_cover_button_03.sub")
			SkillActivated.SetOverVisual("d:/ymir work/ui/public/slot_cover_button_03.sub")
			SkillActivated.SetDownVisual("d:/ymir work/ui/public/slot_cover_button_03.sub")
			SkillActivated.Hide()
			
			Mod = self.SkillIconIndex[i]			
			SkillIconButton.SetEvent(lambda arg = Mod: self.SelectSkill(arg))
			SkillActivated.SetEvent(lambda arg = Mod: self.SelectSkill(arg))
			self.SkillIconList.append(SkillIconButton)
			self.SkillIconList.append(SkillActivated)			
			x += 37
			i += 1
			
	def SelectSkill(self, skillindex):
		SkillEvent = skillindex["COUNT"]
		SkillIndex = skillindex["INDEX"]
		SkillName = skillindex["NAME"]

		Search = 0
		for test in self.ActiveSkillList:
			if test["INDEX"] == SkillIndex:
				Search = 1
		ActiveSkillData = { 
			"COUNT":SkillEvent,
			"INDEX":SkillIndex,
			"NAME":SkillName,
		}
		if Search == 0:
			self.ActiveSkillList.append(ActiveSkillData)
			chat.AppendChat(chat.CHAT_TYPE_INFO, str(SkillName) + " wurde aktiviert.")
			self.SkillIconList[(int(SkillEvent) - 1)*2].SetText("On")
			self.SkillIconList[(int(SkillEvent) - 1)*2 + 1].Show()
		else:
			self.ActiveSkillList.remove(ActiveSkillData)
			chat.AppendChat(chat.CHAT_TYPE_INFO, str(SkillName) + " wurde deaktiviert.")
			self.SkillIconList[(int(SkillEvent) - 1)*2].SetText("Off")
			self.SkillIconList[(int(SkillEvent) - 1)*2 + 1].Hide()
		
	def OnRender(self):
		for Skills in self.ActiveSkillList:
			if skill.CanUseSkill(int(Skills["COUNT"])):
					player.ClickSkillSlot(int(Skills["COUNT"]))
					
	##Auto Potions:
		#Auto Potion Red
		Maximum_TP = player.GetStatus(player.MAX_HP)
		Actual_TP = player.GetStatus(player.HP)
		if (float(Actual_TP) / (float(Maximum_TP)) * 100) < int(self.AutoPotionRedPercent):
			for i in xrange(player.INVENTORY_PAGE_SIZE*2):
				ItemValue = player.GetItemIndex(i)
				if ItemValue == 27001 or ItemValue == 27002 or ItemValue == 27003:
					net.SendItemUsePacket(i)
					
		#Auto Potion Blue
		Maximum_MP = player.GetStatus(player.MAX_SP)
		Actual_MP = player.GetStatus(player.SP)
		if (float(Actual_MP) / (float(Maximum_MP)) * 100) < int(self.AutoPotionBluePercent):
			for i in xrange(player.INVENTORY_PAGE_SIZE*3):
				ItemValue = player.GetItemIndex(i)
				if ItemValue == 27004 or ItemValue == 27005 or ItemValue == 27006:
					net.SendItemUsePacket(i)
			
	def GetSkillLevel(self, skillname):
		SkillIconLevel = []
		for Skill in self.SkillIconIndex:
			Skillgrade = player.GetSkillGrade(Skill["COUNT"])
			Skilllevel = player.GetSkillLevel(Skill["COUNT"])
			Skillname = Skill["NAME"]
			SkillLevelData = { 
				"GRADE":Skillgrade,
				"LEVEL":Skilllevel,
				"NAME":Skillname,
			}
			SkillIconLevel.append(SkillLevelData)
			
		for SkillData in SkillIconLevel:
			SkillLevel = int(SkillData["LEVEL"]) + int(SkillData["GRADE"])*10
			Skillname = str(SkillData["NAME"])
			if str(Skillname) == str(skillname):
				if int(SkillLevel) < 11:
					return 1
				elif int(SkillLevel) < 21:
					return 2
				else:
					return 3
			
	def GetClass(self):
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
			
	def NewSkillsEnable(self):
		playersettingmodule = pack.Get("playersettingmodule.py")
		RaceGroupInfo = self.GetClass()
		Class = str(RaceGroupInfo).split("/")[0]
		if str(playersettingmodule).find("NEW_678TH_SKILL_ENABLE = TRUE") != -1 or str(playersettingmodule).count("1, 2, 3, 4, 5, 6,") >= 2 or str(Class) == "Shaman" or str(Class) == "Sura":
			return 6
		else:
			return 5
			
	def __del__(self):
		ui.Window.__del__(self)
	
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

	def Destroy(self):
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
	
NewLevelBot = NewLevelBotDialog()
NewLevelBot.Show()
