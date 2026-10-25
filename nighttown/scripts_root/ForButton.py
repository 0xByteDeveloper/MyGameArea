pos = [[30,40],[30,70],[30,100],[30,130]]
		
		self.Buttons = {}
		for line in xrange(4):
			self.Buttons["Btn"+str(line)] = ui.Button()
			self.Buttons["Btn"+str(line)].SetParent(self)
			self.Buttons["Btn"+str(line)].SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
			self.Buttons["Btn"+str(line)].SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
			self.Buttons["Btn"+str(line)].SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
			self.Buttons["Btn"+str(line)].SetText("Wechsle in Channel "+str(line+1))
			self.Buttons["Btn"+str(line)].SetPosition(pos[line][0],pos[line][1])
			self.Buttons["Btn"+str(line)].Show()
		self.Buttons["Btn0"].SetEvent(lambda: self.ChangeChannel(1))
		self.Buttons["Btn1"].SetEvent(lambda: self.ChangeChannel(2))
		self.Buttons["Btn2"].SetEvent(lambda: self.ChangeChannel(3))
		self.Buttons["Btn3"].SetEvent(lambda: self.ChangeChannel(4))