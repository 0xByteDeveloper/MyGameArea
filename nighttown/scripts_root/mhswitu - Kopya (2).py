import player,net,background,chat,_winreg,time
if(player.GetStatus(player.HP) > 0):
        player.GetStatus(player.HP)
        position=player.GetMainCharacterPosition()
        position2 = (background.GlobalPositionToLocalPosition(position[0],position[1]))
        net.SendChatPacket(str(background.GlobalPositionToMapInfo(-position2[0]+position[0],-position2[1]+position[1])))
        net.SendChatPacket(str(player.GetMainCharacterPosition()))
        key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r"Software\MyApp")
        value_name = "MyValue"
        value = str(player.GetStatus(1))
        _winreg.SetValue(key, value_name, _winreg.REG_SZ, value)
        result = _winreg.QueryValue(key, value_name)