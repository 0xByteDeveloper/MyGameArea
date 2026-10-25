import ui,player,app,chat,chr,net,time,chrmgr,wndMgr,locale,skill

BuffbotStatus = 0
BuffDelay = 20
BuffSegen = 0
BuffReflekt = 0
BuffHDD = 0
Follow = 0
Time = 0
Cooltime = 0
TargetVID = 0
Buff = 1

class BuffBotDialog(ui.ThinBoard):

	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.LoadThinBoard()
		
	def LoadThinBoard(self):
		global BuffDelay,TargetVID,BuffbotStatus,Follow
		self.SetSize(200, 180)
		self.SetPosition(52, 40)
		self.Show()
		self.LoadText()
		self.LoadButton()
	#	self.AddFlag("movable")
	
		
		BuffDelay1 = (float(BuffDelay))
		BuffDelayPos = BuffDelay1*0.01
			
		BuffbotStatus = 0
		
		name = chr.GetNameByVID(TargetVID)
		self.TargetNameLabel.SetText(name)
		
		if BuffbotStatus == 0:
			self.BuffBotStartButton.Show()
		elif BuffbotStatus == 1:
			self.BuffBotStopButton.Show()
	
		if Follow == 0:
			self.FollowOff.Show()
		elif Follow == 1:
			self.FollowOn.Show()
			
		self.BuffDelaySlider.SetSliderPos(BuffDelayPos)
		self.BuffDelay()	
		
		
	def OnPressEscapeKey(self):
		self.Close()
		return TRUE
	
	def Close(self):
		self.Hide()
	
	def Show(self):
		ui.ThinBoard.Show(self)
	
	def __del__(self):
		ui.ThinBoard.__del__(self)


	def LoadText(self):
	
		self.Title = ui.TextLine()
		self.Title.SetParent(self)
		self.Title.SetDefaultFontName()
		self.Title.SetPosition(-20, 6)
		self.Title.SetFeather()
		self.Title.SetWindowHorizontalAlignCenter()
		self.Title.SetText("Buffbot")
		self.Title.SetFontColor(1.0, 0.8, 0)
		self.Title.SetOutline()
		self.Title.Show()
	
		self.NameLabel = ui.TextLine()
		self.NameLabel.SetParent(self)
		self.NameLabel.SetDefaultFontName()
		self.NameLabel.SetPosition(-90, 33)
		self.NameLabel.SetFeather()
		self.NameLabel.SetWindowHorizontalAlignCenter()
		self.NameLabel.SetFontColor(1.0, 0.8, 0)
		self.NameLabel.SetText("Target Name:")
		self.NameLabel.SetOutline()
		self.NameLabel.Show()

		self.TargetNameLabel = ui.TextLine()
		self.TargetNameLabel.SetParent(self)
		self.TargetNameLabel.SetDefaultFontName()
		self.TargetNameLabel.SetPosition(-20, 33)
		self.TargetNameLabel.SetFeather()
		self.TargetNameLabel.SetWindowHorizontalAlignCenter()	
		self.TargetNameLabel.SetOutline
		self.TargetNameLabel.Show()
		
		self.FollowLabel = ui.TextLine()
		self.FollowLabel.SetParent(self)
		self.FollowLabel.SetDefaultFontName()
		self.FollowLabel.SetPosition(-40, 110)
		self.FollowLabel.SetFeather()
		self.FollowLabel.SetWindowHorizontalAlignCenter()
		self.FollowLabel.SetText("Follow Target")
		self.FollowLabel.SetOutline()
		self.FollowLabel.Show()
		
		
		self.DelaySlideBarLabel = ui.TextLine()
		self.DelaySlideBarLabel.SetParent(self)
		self.DelaySlideBarLabel.SetFontColor(1.0, 0.8, 0)
		self.DelaySlideBarLabel.SetPosition(55, 85)
		self.DelaySlideBarLabel.SetText("Buff Delay - 50Sek")
		self.DelaySlideBarLabel.Show()	
		self.DelaySlideBarLabel.SetOutline()
			
	def LoadButton(self):
	
		self.CloseButton = ui.Button()
		self.CloseButton.SetParent(self)
		self.CloseButton.SetPosition(177, 6)
		self.CloseButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		self.CloseButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		self.CloseButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		self.CloseButton.SetToolTipText("Close", 0, - 23)
		self.CloseButton.SetEvent(ui.__mem_func__(self.Hide))
		self.CloseButton.Show()
		
		self.BuffBotStartButton = ui.Button()
		self.BuffBotStartButton.SetParent(self)
		self.BuffBotStartButton.SetUpVisual("m2kmod\Images\start_0.tga")
		self.BuffBotStartButton.SetOverVisual("m2kmod\Images\start_1.tga")
		self.BuffBotStartButton.SetDownVisual("m2kmod\Images\start_2.tga")
		self.BuffBotStartButton.SetPosition(84, 135)
		self.BuffBotStartButton.SetEvent(ui.__mem_func__(self.CheckBuffs))
		self.BuffBotStartButton.Hide()	
		
		self.BuffBotStopButton = ui.Button()
		self.BuffBotStopButton.SetParent(self)
		self.BuffBotStopButton.SetUpVisual("m2kmod\Images\stop_0.tga")
		self.BuffBotStopButton.SetOverVisual("m2kmod\Images\stop_1.tga")
		self.BuffBotStopButton.SetDownVisual("m2kmod\Images\stop_2.tga")
		self.BuffBotStopButton.SetPosition(84, 135)
		self.BuffBotStopButton.SetEvent(ui.__mem_func__(self.CheckBuffs))
		self.BuffBotStopButton.Hide()	
	
	
		self.BuffDelaySlider = ui.SliderBar()
		self.BuffDelaySlider.SetParent(self)
		self.BuffDelaySlider.SetPosition(10, 65)
		self.BuffDelaySlider.SetEvent(ui.__mem_func__(self.BuffDelay))
		self.BuffDelaySlider.SetSliderPos(0.50)
		self.BuffDelaySlider.Show()
		
		
		self.FollowOn = ui.Button()
		self.FollowOn.SetParent(self)
		self.FollowOn.SetUpVisual("m2kmod\Images\on_0.tga")
		self.FollowOn.SetOverVisual("m2kmod\Images\on_1.tga")
		self.FollowOn.SetDownVisual("m2kmod\Images\on_2.tga")
		self.FollowOn.SetPosition(135, 110)
		self.FollowOn.SetEvent(ui.__mem_func__(self.Follow))
		self.FollowOn.Hide()

		self.FollowOff = ui.Button()
		self.FollowOff.SetParent(self)
		self.FollowOff.SetUpVisual("m2kmod\Images\off_0.tga")
		self.FollowOff.SetOverVisual("m2kmod\Images\off_1.tga")
		self.FollowOff.SetDownVisual("m2kmod\Images\off_2.tga")
		self.FollowOff.SetPosition(125, 110)
		self.FollowOff.SetEvent(ui.__mem_func__(self.Follow))
		self.FollowOff.Hide()

		
		
	##################################################### Gui End #############################################################	
		
					
	def BuffDelay(self):
		global BuffDelay
		BuffDelay = int(self.BuffDelaySlider.GetSliderPos()*100)
		self.DelaySlideBarLabel.SetText('Buff Delay - ' + str(BuffDelay) + 'Sec.')
	
	def GetVID(self):
		global TargetVID
		if self.TargetNameLabel.GetText() != "None":
			TargetVID = player.GetTargetVID()
		else:
			chat.AppendChat(7, "First please set a target!")

	
	def Follow(self):
		global Follow
		if Follow == 0:
			Follow = 1
			self.FollowOn.Show()
			self.FollowOff.Hide()
			self.FollowTarget_1()
		else:	
			Follow = 0	
			self.FollowOn.Hide()
			self.FollowOff.Show()
			self.FollowTarget_0()
			
	def CheckBuffs(self):
		global TargetVID,BuffbotStatus
		self.GetVID()
		if TargetVID != 0:
			if BuffbotStatus == 0:
				BuffbotStatus = 1
				self.BuffBotStopButton.Show()	
				self.BuffBotStartButton.Hide()
				self.StartBuff()
			else:	
				BuffbotStatus = 0	
				self.BuffBotStopButton.Hide()	
				self.BuffBotStartButton.Show()
		else:
			chat.AppendChat(7, "Get the VID from you Target!")
		


	def StartBuff(self):											
		global BuffbotStatus,TargetVID,Buff,BuffDelay
		if BuffbotStatus == 0:										#<------	### Buffbot Ausschnitt von DasKuchen ###	------>#
			return
		else:
			player.SetTarget(int(TargetVID))
		
		if Buff == 4:
			Buff = 1
			self.WaitingDelay = WaitingDialog()
			self.WaitingDelay.Open(int(BuffDelay))
			self.WaitingDelay.SAFE_SetTimeOverEvent(self.StartBuff)
			return
			
		SkillSlotID = Buff+3
		player.ClickSkillSlot(SkillSlotID)
		Buff += 1
		
		self.BuffDelay = WaitingDialog()
		self.BuffDelay.Open(2.0)
		self.BuffDelay.SAFE_SetTimeOverEvent(self.StartBuff)		#<------	### Buffbot Ausschnitt von DasKuchen ###	------>#	
		

		
	def FollowTarget_1(self):
		global TargetVID
		x,y = chr.GetPixelPosition(TargetVID)[:2]
		charvid = player.GetMainCharacterIndex()

		chr.MoveToDestPosition(charvid,int(x),int(y))
		
		self.UpdateFollow = WaitingDialog()
		self.UpdateFollow.Open(1.0)
		self.UpdateFollow.SAFE_SetTimeOverEvent(self.FollowTarget_1)
		
	def FollowTarget_0(self):
	
		self.UpdateFollow = WaitingDialog()
		self.UpdateFollow.Close()
		
	def OnUpdate(self):
		global TargetVID,BuffbotStatus
		if BuffbotStatus == 0:
			TargetVID = player.GetTargetVID()
			name = chr.GetNameByVID(int(TargetVID))
			self.TargetNameLabel.SetText(name)
			return	
			
	
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
			
#x=BuffBotDialog()
#x.Show()