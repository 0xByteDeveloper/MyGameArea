import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,wndMgr,math,uiCommon,grp,dbg,os,event,uiCommon

class QuestBugDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.comp = Component()
		self.Account1Button = self.comp.Button(None, 'Start', '', wndMgr.GetScreenWidth()-90, 157, self.StartQuest, 'd:/ymir work/ui/public/middle_button_01.sub', 'd:/ymir work/ui/public/middle_button_02.sub','d:/ymir work/ui/public/middle_button_03.sub')
		self.InstallQuestWindowHook()
		
	def __del__(self):
		self.UnHookQuestWindow()
		ui.ScriptWindow.__del__(self)


		
	def Close(self):
		self.Board.Hide()
		self.UnHookQuestWindow()
	def Show(self):
		ui.ScriptWindow.Show(self)
		
		
	def StartQuest(self):
		net.ExitGame()		# chat.AppendChat(1, str(player.GetTargetVID()))
		net.SendOnClickPacket(12465)
		event.SelectAnswer(1, 1)
		self.Timer = WaitingDialog()
		self.Timer.Open(5)					
		self.Timer.SAFE_SetTimeOverEvent(self.Check)
	
	def Check(self):
		if player.GetStatus(player.ATT_SPEED) <= 100:
			self.Timer2 = WaitingDialog()
			self.Timer2.Open(0.5)
			self.Timer2.SAFE_SetTimeOverEvent(self.Check)
		else:
			self.Timer3 = WaitingDialog()
			self.Timer3.Open(0.5)
			self.Timer3.SAFE_SetTimeOverEvent(self.StartQuest)
		
		
	def DebugTimer(self):
		self.Timer2 = WaitingDialog()
		self.Timer2.Open(12)
		self.Timer2.SAFE_SetTimeOverEvent(self.Debug)
	
	def Debug(self):
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Player Name = "+str(player.GetStatus(player.ATT_SPEED)))
		self.QuestionDialog.SetCenterPosition()
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()
	def CancelQuestionDialog(self):
		self.QuestionDialog.Close()
		self.QuestionDialog = None
		
	def InstallQuestWindowHook(self):
		self.OldRecv = game.GameWindow.OpenQuestWindow
		game.GameWindow.OpenQuestWindow = self.HookedQuestWindow
	def UnHookQuestWindow(self):
		game.GameWindow.OpenQuestWindow = self.OldRecv
	def HookedQuestWindow(self, skin, idx):
		pass
	
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
	def HideButton(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.Hide()
		button.SetEvent(func)
		return button
	def CheckButton(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.SetEvent(func)
		return button	
	def OnScreenButton(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
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
				
try:
	app.Shop.Close()
except:
	pass
app.Shop = QuestBugDialog()