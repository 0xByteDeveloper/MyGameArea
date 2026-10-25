import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr
import background,constInfo,wndMgr,math,uiCommon,grp,dbg

State = 0
Delay = 15
Type = 0
Num = 1

class Spamdialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.BuildWindow()
		
	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def BuildWindow(self):
		self.Board = ui.ThinBoard()
		self.Board.SetSize(198, 245)
		self.Board.SetPosition(52, 40)
	#	self.Board.AddFlag('movable')
	#	self.Board.AddFlag('float')
		self.Board.Show()
		
		self.comp = Component()
		self.Slotbar, self.SpamText = self.comp.EditLine(self.Board, '', 23, 29, 150, 75, 150)
		self.Header = self.comp.TextLine(self.Board, 'Spambot', 73, 7, self.comp.RGB(255, 255, 0))
		self.DelayLabel = self.comp.TextLine(self.Board, 'Delay: 15 Sec.', 70, 163, self.comp.RGB(255, 255, 255))
		
		self.DelaySlide = self.comp.SliderBar(self.Board, 0.15, self.SlideFunc, 13, 148)
		self.Close = self.comp.Button(self.Board, '', 'Close', 175, 7, self.Board.Hide, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.Text1Button = self.comp.Button(self.Board, 'Text1', 'Load & Set Text1', 6, 115, self.Text1, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.Text2Button = self.comp.Button(self.Board, 'Text2', 'Load & Set Text2', 54, 115, self.Text2, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.Text3Button = self.comp.Button(self.Board, 'Text3', 'Load & Set Text3', 102, 115, self.Text3, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.Text4Button = self.comp.Button(self.Board, 'Text4', 'Load & Set Text4', 150, 115, self.Text4, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.ChatTypeButton = self.comp.Button(self.Board, 'Global', 'Chattype', 6, 180, self.SetType, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.SaveButton = self.comp.Button(self.Board, 'Save', '', 150, 180, self.Save, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub','d:/ymir work/ui/public/small_button_03.sub')
		self.SpamOn = self.comp.HideButton(self.Board, '', '', 80, 190, self.SpamState, 'm2kmod\Images\start_0.tga', 'm2kmod\Images\start_1.tga', 'm2kmod\Images\start_2.tga')
		self.SpamOff = self.comp.HideButton(self.Board, '', '', 75, 190, self.SpamState, 'm2kmod\Images\stop_0.tga', 'm2kmod\Images\stop_1.tga', 'm2kmod\Images\stop_2.tga')
	
		global State,Delay,Type,Num
		DelayPos1 = (float(Delay))
		DelayPos = DelayPos1*0.01
		if State == 1:
			self.SpamOff.Show()
			self.StartSpam()
		elif State == 0:
			self.SpamOn.Show()
			self.StopSpam()
			
		if Type == 1:
			self.ChatTypeButton.SetText("Normal")
		elif State == 0:
			self.ChatTypeButton.SetText("Global")
			
		if Num == 1:
			self.Text1()
		elif Num == 2:
			self.Text2()
		elif Num == 3:
			self.Text3()
		elif Num == 4:
			self.Text4()
		
		self.DelaySlide.SetSliderPos(DelayPos)
		self.SlideFunc()
	
	def Text1(self):
		global Num
		self.Text1Button.ButtonText.SetFontColor(*self.comp.RGB(255,255,0))
		self.Text2Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text3Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text4Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		Num = 1
		self.LoadText1()
	def Text2(self):
		global Num
		self.Text1Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text2Button.ButtonText.SetFontColor(*self.comp.RGB(255,255,0))
		self.Text3Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text4Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		Num = 2
		self.LoadText2()
	def Text3(self):
		global Num
		self.Text1Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text2Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text3Button.ButtonText.SetFontColor(*self.comp.RGB(255,255,0))
		self.Text4Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		Num = 3
		self.LoadText3()
	def Text4(self):
		global Num
		self.Text1Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text2Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text3Button.ButtonText.SetFontColor(*self.comp.RGB(200,200,200))
		self.Text4Button.ButtonText.SetFontColor(*self.comp.RGB(255,255,0))
		Num = 4
		self.LoadText4()
	def SlideFunc(self):
		global Delay
		Delay = int(self.DelaySlide.GetSliderPos()*100)
		self.DelayLabel.SetText("Delay: "+str(Delay)+ ' Sec.')
	
	def SpamState(self):
		global State
		if State == 0:
			State = 1
			self.SpamOff.Show()
			self.SpamOn.Hide()
			self.StartSpam()
		else: 
			State = 0
			self.SpamOn.Show()
			self.SpamOff.Hide()	
			self.StopSpam()
	def SetType(self):
		global Type
		if Type == 0:
			Type = 1
			self.ChatTypeButton.SetText("Normal")
		else: 
			Type = 0
			self.ChatTypeButton.SetText("Global")			
	
	def Save(self):
		global Num
		if Num == 1:
			self.SaveText1()
		if Num == 2:
			self.SaveText2()	
		if Num == 3:
			self.SaveText3()
		if Num == 4:
			self.SaveText4()
	def SaveText1(self):
		f = open("m2kmod/Saves/text1.m2k", "w")
		f.write(str(self.SpamText.GetText()) + "\n")
	def SaveText2(self):
		f = open("m2kmod/Saves/text2.m2k", "w")
		f.write(str(self.SpamText.GetText()) + "\n")
	def SaveText3(self):
		f = open("m2kmod/Saves/text3.m2k", "w")
		f.write(str(self.SpamText.GetText()) + "\n")
	def SaveText4(self):
		f = open("m2kmod/Saves/text4.m2k", "w")
		f.write(str(self.SpamText.GetText()) + "\n")
		
	def LoadText1(self):
		f = open("m2kmod/Saves/text1.m2k", "r")
		self.SpamText.SetText(str(f.read()))
	def LoadText2(self):
		f = open("m2kmod/Saves/text2.m2k", "r")
		self.SpamText.SetText(str(f.read()))
	def LoadText3(self):
		f = open("m2kmod/Saves/text3.m2k", "r")
		self.SpamText.SetText(str(f.read()))
	def LoadText4(self):
		f = open("m2kmod/Saves/text4.m2k", "r")
		self.SpamText.SetText(str(f.read()))
	
	
	def Close(self):
		self.Board.Hide()
	def Show(self):
		ui.Window.Show(self)
		
		
	def StartSpam(self):
		global Type,Delay
		if Type == 1:
			net.SendChatPacket(str(self.SpamText.GetText()), chat.CHAT_TYPE_TALKING)
		else: 
			net.SendChatPacket(str(self.SpamText.GetText()), chat.CHAT_TYPE_SHOUT)
		
		self.UpdateSpam = WaitingDialog()
		self.UpdateSpam.Open(Delay)
		self.UpdateSpam.SAFE_SetTimeOverEvent(self.StartSpam)
		
	def StopSpam(self):
		self.UpdateSpam = WaitingDialog()
		self.UpdateSpam.Close()


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
	#	button.Show()
		button.SetEvent(func)
		return button

	def ToggleButton(self, parent, buttonName, tooltipText, x, y, funcUp, funcDown, UpVisual, OverVisual, DownVisual):
		button = ui.ToggleButton()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.Show()
		button.SetToggleUpEvent(funcUp)
		button.SetToggleDownEvent(funcDown)
		return button

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
		Value.SetPosition(1, 1)
		Value.SetMax(max)
		Value.SetLimitWidth(width)
		Value.SetMultiLine()
		Value.SetText(editlineText)
		Value.Show()
		return SlotBar, Value

	def TextLine(self, parent, textlineText, x, y, color):
		textline = ui.TextLine()
		if parent != None:
			textline.SetParent(parent)
		textline.SetPosition(x, y)
		if color != None:
			textline.SetFontColor(color[0], color[1], color[2])
		textline.SetText(textlineText)
		textline.Show()
		return textline

	def RGB(self, r, g, b):
		return (r*255, g*255, b*255)

	def SliderBar(self, parent, sliderPos, func, x, y):
		Slider = ui.SliderBar()
		if parent != None:
			Slider.SetParent(parent)
		Slider.SetPosition(x, y)
		Slider.SetSliderPos(sliderPos)
		Slider.Show()
		Slider.SetEvent(func)
		return Slider

	def ExpandedImage(self, parent, x, y, img):
		image = ui.ExpandedImageBox()
		if parent != None:
			image.SetParent(parent)
		image.SetPosition(x, y)
		image.LoadImage(img)
		image.Show()
		return image

	def ComboBox(self, parent, text, x, y, width):
		combo = ui.ComboBox()
		if parent != None:
			combo.SetParent(parent)
		combo.SetPosition(x, y)
		combo.SetSize(width, 15)
		combo.SetCurrentItem(text)
		combo.InsertItem(1,"Text2")
		combo.InsertItem(2,"Text3")
		combo.InsertItem(3,"Text4")
		combo.InsertItem(4,"Text5")
		combo.Show()
		combo.SetEvent(self.Text)
		return combo

	def ThinBoard(self, parent, moveable, x, y, width, heigh, center):
		thin = ui.ThinBoard()
		if parent != None:
			thin.SetParent(parent)
		if moveable == TRUE:
			thin.AddFlag('movable')
			thin.AddFlag('float')
		thin.SetSize(width, heigh)
		thin.SetPosition(x, y)
		if center == TRUE:
			thin.SetCenterPosition()
		thin.Show()
		return thin

	def Gauge(self, parent, width, color, x, y):
		gauge = ui.Gauge()
		if parent != None:
			gauge.SetParent(parent)
		gauge.SetPosition(x, y)
		gauge.MakeGauge(width, color)
		gauge.Show()
		return gauge

	def ListBoxEx(self, parent, x, y, width, heigh):
		bar = ui.Bar()
		if parent != None:
			bar.SetParent(parent)
		bar.SetPosition(x, y)
		bar.SetSize(width, heigh)
		bar.SetColor(0x77000000)
		bar.Show()
		ListBox=ui.ListBoxEx()
		ListBox.SetParent(bar)
		ListBox.SetPosition(0, 0)
		ListBox.SetSize(width, heigh)
		ListBox.Show()
		scroll = ui.ScrollBar()
		scroll.SetParent(ListBox)
		scroll.SetPosition(width-15, 0)
		scroll.SetScrollBarSize(heigh)
		scroll.Show()
		ListBox.SetScrollBar(scroll)
		return bar, ListBox

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
				
#Spamdialog().Show()