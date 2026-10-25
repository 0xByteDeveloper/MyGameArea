(ax, ay, az) = player.GetMainCharacterPosition()
(TmpX, TmpY) = (GetPositiveValue(ax - x) ** 2, GetPositiveValue(ay - y) ** 2)

def GetPositiveValue(value):
	if value < 0:
		return value - (2*value)
	else:
		return value
		
		
if (TmpX < 50 or TmpY < 50):
	#chr.SetPixelPosition(tX, tY)
	#chr.MoveToDestPosition(player.GetMainCharacterIndex(), x, y)
	#chat.AppendChat(chat.CHAT_TYPE_INFO, "PosIMG:" + str(tX) + ", " + str(tY))		
	#chat.AppendChat(chat.CHAT_TYPE_INFO, "Distance:" + str(TmpX) + ", " + str(TmpY))
	chat.AppendChat(3, "Append Item: " + str(item.GetItemName(item.SelectItem(kamer.GetVirtualNumberOfGroundItem(iVID)))) + ",  " + str(LocalX) + ", " + str(LocalY) + " Distance: " + str(TmpX) + ", " + str(TmpY) + ", VID: " + str(iVID) + ", VNUM: " + str(kamer.GetVirtualNumberOfGroundItem(iVID)))
	net.SendItemPickUpPacket(iVID)
	return List			
elif if (TmpX >= 50 or TmpY >= 50):
	chat.AppendChat(chat.CHAT_TYPE_INFO, "Sorry i cant pick up" + str(TmpX) + ", " + str(TmpY))
							
		List=[]
		Picker=Pick
		for y in range(125,1125,9): # xrange(125,600,9)
			for x in range(300,1300,25):# xrange(300,825,25)
					iVID = Picker(x, y)
					LocalX, LocalY = background.GlobalPositionToLocalPosition(x, y)
					(ax, ay, az) = player.GetMainCharacterPosition(iVID)
					(mapName, xBase, yBase)=background.GlobalPositionToMapInfo(ax, ay)
					tX = int(LocalX)+xBase
					tY = int(LocalY)+yBase
					evAx = int(ax)/100
					evAy = int(ay)/100
					#self.FOUND_COORDS = (int(xx), int(yy))
					if -1 != iVID:			
						#chr.SetPixelPosition(tX, tY)
						#chr.MoveToDestPosition(player.GetMainCharacterIndex(), x, y)
						#chat.AppendChat(chat.CHAT_TYPE_INFO, "PosIMG:" + str(tX) + ", " + str(tY))		
						#chat.AppendChat(chat.CHAT_TYPE_INFO, "Pos:" + str(evAx) + ", " + str(evAy))
						chat.AppendChat(3, "Append Item: " + str(item.GetItemName(item.SelectItem(kamer.GetVirtualNumberOfGroundItem(iVID)))) + ",  " + str(LocalX) + ", " + str(LocalY) + ", VID: " + str(iVID) + ", VNUM: " + str(kamer.GetVirtualNumberOfGroundItem(iVID)))
						net.SendItemPickUpPacket(iVID)
		return List