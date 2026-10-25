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

class Farmbot(ui.ScriptWindow):
	Farmbotstatus = 0
	ActualMetin = 0	
	startscan = 100
	endscan = 400000
	olddistance = 0
	SearchFail = 0
	
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.LoadUI()
		self.SetVIDRange()
		self.KuchenUpdate()

	def __del__(self):
		ui.ScriptWindow.__del__(self)
		self.Board.Hide()

	def LoadUI(self):
		
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(300, 200)
		self.Board.SetCenterPosition()
		self.Board.AddFlag("movable")
		self.Board.AddFlag("float") 
		self.Board.SetTitleName("Farmbot")
		self.Board.SetCloseEvent(self.__del__)
		self.Board.Show()
		
		self.Button1 = ui.Button()
		self.Button1.SetParent(self.Board)
		self.Button1.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.Button1.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.Button1.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.Button1.SetText("Start/Stopp")
		self.Button1.SetEvent(self.StartBot)
		self.Button1.SetPosition(100, 50)
		self.Button1.Show()	

	def SetVIDRange(self):#by realfreak#
		Found = 0
		Start = 0
		End = 1000000
		for loop in xrange(1, 7):
			for i in xrange(Start, End):
				if 2 == chr.GetInstanceType(i):
					self.startscan = int(i) - 500
					self.endscan = int(i) + 50000
					Found = 1
					break
			if Found == 0:
				Start = End
				End = End + 1000000
		#chat.AppendChat(chat.CHAT_TYPE_INFO, "VID Range: " + str(self.startscan) + " - " + str(self.endscan))
		
	def StartBot(self):
		if self.Farmbotstatus == 0:
			self.Farmbotstatus = 1
		else:
			self.Farmbotstatus = 0
			self.ActualMetin = 0
			player.SetAttackKeyState(FALSE)
			
	def SearchMetin(self):
		for i in xrange(int(self.startscan), int(self.endscan)):
			if 2 == chr.GetInstanceType(i):
				chr.SelectInstance(i)
				Alive = self.IsAlive(i)
				if Alive == "alive":
					MetinName = str(chr.GetName())
					chat.AppendChat(chat.CHAT_TYPE_INFO, str(self.startscan) + "Name: " + str(self.endscan) )
					vid = int(i)
					level = nonplayer.GetLevelByVID(i)
					mobX, mobY, mobZ = chr.GetPixelPosition(i)
					Distance = player.GetCharacterDistance(i)
					self.WalkToMob(mobX, mobY, mobZ, vid,Distance,self.olddistance)	
					self.ActualMetin = vid
					chat.AppendChat(chat.CHAT_TYPE_INFO, "System: Metinstein gefunden.")
					self.SearchFail = 0
					break
					
	def IsAlive(self, vid):
		info = str(chrmgr.GetVIDInfo(vid))
		splitinfo = info.split("isAlive=")
		if str(splitinfo[1][0]) != "1":
			return "dead"
		else:
			return "alive"

	def WalkToMob(self, x, y, z, vid,distance,olddistance):
		charvid = player.GetMainCharacterIndex()
		chr.MoveToDestPosition(charvid,int(x),int(y))
		if int(distance) > 200:
			if distance == olddistance: #Anti steckenbleiben
				RandomINT = int(app.GetRandom(1, 10))
				chr.MoveToDestPosition(charvid,int(x+RandomINT),int(y+RandomINT))
			if player.IsMountingHorse():
				net.SendChatPacket("/user_horse_ride")		
			player.SetAttackKeyState(FALSE)
			self.olddistance = distance
		else:	
			if not player.IsMountingHorse():
				player.ClickSkillSlot(4)
				player.ClickSkillSlot(3)
				net.SendChatPacket("/user_horse_ride")
			player.SetAttackKeyState(TRUE)
			
	def UpdateDistance(self,vid):
		mobX, mobY, mobZ = chr.GetPixelPosition(vid)
		Distance = player.GetCharacterDistance(vid)
		self.WalkToMob(mobX, mobY, mobZ, vid,Distance,self.olddistance)
	
	def OnRender(self):
		if self.Farmbotstatus == 1:
			player.PickCloseItem()
		
	def KuchenUpdate(self):
		self.Botdelay = WaitingDialog()
		self.Botdelay.Open(1.3)
		self.Botdelay.SAFE_SetTimeOverEvent(self.KuchenUpdate)	
		
		if self.ActualMetin != 0 or self.Farmbotstatus == 1:
			Alive = self.IsAlive(int(self.ActualMetin))
			if Alive == "dead":
				self.ActualMetin = 0
				player.SetAttackKeyState(FALSE)
				chat.AppendChat(chat.CHAT_TYPE_INFO, "System: Suche neuen Metinstein")
				self.SearchFail += 1
				if self.SearchFail == 8:
					chat.AppendChat(chat.CHAT_TYPE_INFO, "System: Setze neue VID Range")
					self.SetVIDRange()
				self.SearchMetin()
			else:
				self.UpdateDistance(int(self.ActualMetin))
				
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
				

FarmbotWindow = Farmbot()
FarmbotWindow.Show()