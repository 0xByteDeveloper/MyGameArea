#Metin2 EXP-Donator by musicinstructor@elitepvpers.com 2011
#Run with Python Module Loader (www.elitepvpers.com/forum/metin2-hacks-bots-cheats-exploits-macros/1279509-tool-python-module-loader.html)

import ui
import chat
import app
import player
import net
import time

DONATION_CHECK_DELAY = 1.0
AUTODONATION = TRUE

EXPDONATOR_HOTKEY_DOWN = FALSE
EXPDONATOR_LAST_TIME = 0

def MainLoop():
	global AUTODONATION
	global EXPDONATOR_HOTKEY_DOWN
	global EXPDONATOR_LAST_TIME
	global DONATION_CHECK_DELAY
	
	if (app.IsPressed(app.DIK_F5) == FALSE):
		EXPDONATOR_HOTKEY_DOWN = FALSE
	
	if (app.IsPressed(app.DIK_F5) == TRUE and EXPDONATOR_HOTKEY_DOWN == FALSE):
		EXPDONATOR_HOTKEY_DOWN = TRUE
		
		if (AUTODONATION == FALSE):
			AUTODONATION = TRUE
			chat.AppendChat(chat.CHAT_TYPE_INFO, "EXP-Donator: Autodonation enabled.")
		else:
			AUTODONATION = FALSE
			chat.AppendChat(chat.CHAT_TYPE_INFO, "EXP-Donator: Autodonation disenabled.")

	cur_exp = player.GetStatus(player.EXP)
	if (AUTODONATION == TRUE and time.clock() > EXPDONATOR_LAST_TIME + DONATION_CHECK_DELAY and cur_exp >= 100):
		new_exp = cur_exp - int(round(cur_exp,-2))
		
		if (new_exp < 0):
			return

		EXPDONATOR_LAST_TIME = time.clock()
		player.SetStatus(player.EXP, new_exp)
		net.SendGuildOfferPacket(cur_exp)

EXPDonator = ui.Window()
EXPDonator.OnUpdate = MainLoop
EXPDonator.Show()
chat.AppendChat(chat.CHAT_TYPE_INFO, "EXP-Donator by musicinstructor")