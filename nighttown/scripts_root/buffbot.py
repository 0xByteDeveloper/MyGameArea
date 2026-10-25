import chr
import locale
import time
import ui
import chat
import player

Buffbotstarten = 0
waitingdelay = 0
xBuff = 1

class Botdialog(ui.ThinBoard):

	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.LoadBoard()
		
	def LoadBoard(self):
		self.SetCenterPosition()
		self.SetSize(300, 150)
		self.Show()
		self.AddFlag("movable")
		
		self.LoadText()
		self.LoadButton()
		
	def LoadText(self):
		self.Titel = ui.TextLine()
		self.Titel.SetParent(self)
		self.Titel.SetDefaultFontName()
		self.Titel.SetPosition(-70, 4)
		self.Titel.SetFeather()
		self.Titel.SetWindowHorizontalAlignCenter()
		self.Titel.SetText("Buffbot by DasKuchen")
		self.Titel.SetFontColor(1.0, 0.8, 0)
		self.Titel.SetOutline()
		self.Titel.Show()
		
		self.TargetName = ui.TextLine()
		self.TargetName.SetParent(self)
		self.TargetName.SetDefaultFontName()
		self.TargetName.SetPosition(-70, 33)
		self.TargetName.SetFeather()
		self.TargetName.SetWindowHorizontalAlignCenter()
		self.TargetName.SetText("None")
		self.TargetName.SetOutline()
		self.TargetName.Show()

		self.Info = ui.TextLine()
		self.Info.SetParent(self)
		self.Info.SetDefaultFontName()
		self.Info.SetPosition(-125, 33)
		self.Info.SetFeather()
		self.Info.SetWindowHorizontalAlignCenter()
		self.Info.SetFontColor(1.0, 0.8, 0)
		self.Info.SetText("Dein Ziel: ")
		self.Info.SetOutline()
		self.Info.Show()
		
		self.Info3 = ui.TextLine()
		self.Info3.SetParent(self)
		self.Info3.SetDefaultFontName()
		self.Info3.SetPosition(-125, 70)
		self.Info3.SetFeather()
		self.Info3.SetWindowHorizontalAlignCenter()
		self.Info3.SetFontColor(1.0, 0.8, 0)
		self.Info3.SetText("Delay:")
		self.Info3.SetOutline()
		self.Info3.Show()
		
		self.InfoDelay = ui.TextLine()
		self.InfoDelay.SetParent(self)
		self.InfoDelay.SetDefaultFontName()
		self.InfoDelay.SetPosition(-30, 90)
		self.InfoDelay.SetFeather()
		self.InfoDelay.SetWindowHorizontalAlignCenter()
		self.InfoDelay.SetFontColor(1.0, 0.8, 0)
		self.InfoDelay.SetText("0 Sekunden")
		self.InfoDelay.SetOutline()
		self.InfoDelay.Show()				
		
	def LoadButton(self):
		self.CloseButton = ui.Button()
		self.CloseButton.SetParent(self)
		self.CloseButton.SetPosition(280, 4)
		self.CloseButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		self.CloseButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		self.CloseButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		self.CloseButton.SetToolTipText(locale.UI_CLOSE, 0, - 23)
		self.CloseButton.SetEvent(ui.__mem_func__(self.Close))
		self.CloseButton.Show()
		
		self.BuffBotStartButton = ui.Button()
		self.BuffBotStartButton.SetParent(self)
		self.BuffBotStartButton.SetUpVisual("d:/ymir work/ui/public/xlarge_button_01.sub")
		self.BuffBotStartButton.SetOverVisual("d:/ymir work/ui/public/xlarge_button_02.sub")
		self.BuffBotStartButton.SetDownVisual("d:/ymir work/ui/public/xlarge_button_03.sub")
		self.BuffBotStartButton.SetText("Buffbot Starten")
		self.BuffBotStartButton.SetPosition(60, 120)
		self.BuffBotStartButton.SetEvent(ui.__mem_func__(self.StartBuffbot))
		self.BuffBotStartButton.Show()	

		self.DelaySlide = ui.SliderBar()
		self.DelaySlide.SetParent(self)
		self.DelaySlide.SetPosition(60, 70)
		self.DelaySlide.SetEvent(ui.__mem_func__(self.SlideDelay))
		self.DelaySlide.Show()
		
	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Show(self):
		ui.ThinBoard.Show(self)

	def Close(self):
		global Buffbotstarten
		Buffbotstarten = 0
		player.ClearTarget()
		self.Hide()
		
	def StartBuffbot(self):
		global Buffbotstarten
		import chat
	#	self.Teleport2Target()
	#	if Buffbotstarten == 0:
	#		self.BuffBotStartButton.SetText("Buffbot Stoppen")
	#		Buffbotstarten = 1
	#		self.MakeBuff()
	#	else:
	#		self.BuffBotStartButton.SetText("Buffbot Starten")
	#		Buffbotstarten = 0
		vid = player.GetTargetVID()
		chat.AppendChat(chat.CHAT_TYPE_INFO, str(vid))
	
	def SlideDelay(self):
		global waitingdelay
		waitingdelay=int(self.DelaySlide.GetSliderPos()*100)
		self.InfoDelay.SetText(str(waitingdelay) + " Sekunden")		
	
	def MakeBuff(self):
		global Buffbotstarten
		global waitingdelay
		if Buffbotstarten == 0:
			return
		global xBuff
		if xBuff == 4:
			xBuff = 1
			self.WaitingDelay = WaitingDialog()
			self.WaitingDelay.Open(int(waitingdelay))
			self.WaitingDelay.SAFE_SetTimeOverEvent(self.MakeBuff)
			return
			
		SkillSlotID = xBuff+3
		player.ClickSkillSlot(SkillSlotID)
		xBuff += 1
		self.BuffDelay = WaitingDialog()
		self.BuffDelay.Open(2.0)
		self.BuffDelay.SAFE_SetTimeOverEvent(self.MakeBuff)
		
	def MoveToTarget(self):
		x,y = chr.GetPixelPosition(player.GetTargetVID() )[:2]
		chr.MoveToDestPosition(player.GetMainCharacterIndex(),int(x),int(y))
				
	def OnUpdate(self):
		vid = player.GetTargetVID()
		name = chr.GetNameByVID(vid)
		self.TargetName.SetText(vid)
		self.TargetName.Show()	
		global Buffbotstarten
		
		self.MoveToTarget()		
		
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
			
StartDialog = Botdialog()
StartDialog.Show()