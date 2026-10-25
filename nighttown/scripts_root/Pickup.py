import player,ui,wndMgr

Pickup = 0

class PickupDialog(ui.ThinBoard):
	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.LoadPickup()
		
	def __del__(self):
		ui.ThinBoard.__del__(self)
		
	def LoadPickup(self):
	
		self.PickupButton = ui.Button()
		self.PickupButton.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
		self.PickupButton.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
		self.PickupButton.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
		self.PickupButton.SetText("Of")
		self.PickupButton.SetPosition(wndMgr.GetScreenWidth()-90,157)
		self.PickupButton.SetEvent(ui.__mem_func__(self.Pickup))
		self.PickupButton.Show()
		
	def Show(self):
		ui.ThinBoard.Show(self)
	
	def Pickup(self):
	
		global Pickup
		
		if Pickup == 0:
			Pickup = 1
			self.PickupButton.SetText("On")
		else:	
			Pickup = 0
			self.PickupButton.SetText("Off")
			
			
	def OnUpdate(self):
	
		global Pickup
	
		if Pickup == 1:
			player.PickCloseItem() 
		
PickupDialog().Show()

