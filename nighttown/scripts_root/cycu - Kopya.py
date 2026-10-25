import ui
import time
import _winreg
import ServerInfo
import textTail
import net
import chat
import player
import app
myclient = 1
class Dialog1(ui.Window):

    def __init__(self):
        ui.Window.__init__(self)
        self.BuildWindow()

    def BuildWindow(self):
        global logingame
        logingame = 0
        global MyOnline
        MyOnline = ''
        global MyOtoTry
        MyOtoTry = '0'
        global useblehorse
        useblehorse=0
        self.DumpServerInfo()
        self.__BuildKeyDict()

    def __BuildKeyDict(self):
        onPressKeyDict = {}
        onPressKeyDict[app.DIK_F5] = lambda : self.OpenWindow()
        self.onPressKeyDict = onPressKeyDict

    def OpenWindow(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    def DumpServerInfo(self):                                                                                           
        self.ServerNames = []                                                                                           
        self.AuthServers = []                                                                                           
        self.AuthPorts = []                                                                                             
        self.ServerIps = []                                                                                             
        self.ServerPorts = []                                                                                           
                                                                                                                        
        LoginFile = self.GetTextFileTuple('intrologin.py', 0)                                                           
        for line in LoginFile:                                                                                          
            if line.find('self.stream.SetConnectInfo("') != -1:                                                         
                AuthPort = int(line.split('"')[4].split(', ')[1].split(')')[0])                                         
                if not AuthPort in self.AuthPorts:                                                                      
                    self.AuthServers.append(line.split('"')[3])                                                         
                    self.AuthPorts.append(AuthPort)                                                                     
                ServerPort = int(line.split('"')[2].split(', ')[1])                                                     
                if not ServerPort in self.ServerPorts:                                                                  
                    self.ServerIps.append(line.split('"')[1])                                                           
                    self.ServerPorts.append(ServerPort)                                                                 
                if line.find('net.SetServerInfo("') != -1 and not line.find('├Á©Â ╝¡╣÷') != -1:                         
                    if not line.split('"')[1] in ServerNames:                                                           
                        ServerNames.append(line.split('"')[1])                                                          
                                                                                                                        
        for Server in xrange(len(ServerInfo.REGION_DICT[0])):                                                           
            self.ServerIps = []                                                                                         
            self.ServerPorts = []                                                                                       
            self.ServerName = ServerInfo.REGION_DICT[0][Server + 1]['name']                                             
            AuthServerIp = ServerInfo.REGION_AUTH_SERVER_DICT[0][Server + 1]['ip']                                      
            self.AuthServers.append(AuthServerIp)                                                                       
            AuthServerPort = ServerInfo.REGION_AUTH_SERVER_DICT[0][Server + 1]['port']                                  
            self.AuthPorts.append(AuthServerPort)                                                                       
            for Channel in xrange(len(ServerInfo.REGION_DICT[0][Server + 1]['channel'])):                               
                self.ServerIps.append(ServerInfo.REGION_DICT[0][Server + 1]['channel'][Channel + 1]['ip'])              
                ServerPort = ServerInfo.REGION_DICT[0][Server + 1]['channel'][Channel + 1]['tcp_port']                  
                if not ServerPort in self.ServerPorts:                                                                  
                    self.ServerPorts.append(ServerPort)                                                                 
            for Channels in self.ServerPorts:                                                                           
                Index = self.ServerPorts.index(Channels)                                                                
            self.DirectConnect(self.AuthServers[0], self.AuthPorts[0], self.ServerIps[0], self.ServerPorts[0], 'admin', '1')
                                                                                                                        
    def DirectConnect(self, AuthServerIP, AuthServerPort, ChannelIP, ChannelPort, AccountID, Password):                 
        net.SetPacketSequenceMode()
        net.SetLoginInfo(AccountID, Password)
        net.ConnectToAccountServer(ChannelIP, ChannelPort, AuthServerIP, AuthServerPort)
        self.login_enter_delay()


    def login_enter_delay(self):
        self.login_enter_WaitingDialog = WaitingDialog()
        self.login_enter_WaitingDialog.Open(int(11))
        global logingame
        if logingame == 0:
            self.login_enter_WaitingDialog.SAFE_SetTimeOverEvent(self.login_enter_fnc)
            logingame = 1

    def login_enter_fnc(self):
            net.DirectEnter(0)
            self.kickfinish()

    def GetTextFileTuple(self, file, mode):                                                                             
        tmp = []                                                                                                        
        try:                                                                                                            
            Handle = app.OpenTextFile(file)                                                                             
            CountLines = app.GetTextFileLineCount(Handle)                                                               
        except:                                                                                                         
            return ''                                                                                                   
        if mode == 0:                                                                                                   
            return(tmp)                                                                                                 
        for i in xrange(CountLines):                                                                                    
            line = app.GetTextFileLine(Handle, i)                                                                       
            if line != '':                                                                                              
                tmp.append(line + '\n')                                                                                 
        return(''.join(tmp))

    def usehorse_delay(self):
        self.usehorse_WaitingDialog = WaitingDialog()
        self.usehorse_WaitingDialog.Open(int(4))
        global useblehorse
        if useblehorse == 1:
            self.usehorse_WaitingDialog.SAFE_SetTimeOverEvent(self.usehorse_fnc)
            useblehorse = 0

    def usehorse_fnc(self):
            net.SendChatPacket("/ride")

    def __del__(self):
        ui.Window.__del__(self)


    def kickfinish(self):
            self.kickseg = WaitingDialog()
            self.kickseg.Open(int(1))
            self.kickseg.SAFE_SetTimeOverEvent(self.kickfinish)
            global MyOnline
            global MyOtoTry
            global useblehorse
            try:  
                OnlineControl = str(chr.GetPixelPosition(net.GetMainActorVID()))
                if OnlineControl == 'None':
                    MyOnline = "0"
                else:
                    MyOnline = "1"
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'SOFTWARE\\BinDir')
                myregway = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r"SOFTWARE\\BinDir")
                if MyOnline =='0' and MyOtoTry == '1':
                    autologinbvalue = _winreg.QueryValueEx(key, 'autologinb'+str(myclient))[0]
                    if autologinbvalue == '1':
                        net.DirectEnter(0)
                        MyOtoTry = '0'
                _winreg.SetValueEx(myregway, "onln"+str(myclient), 0, _winreg.REG_SZ, MyOnline)
                if(MyOnline =='1'):
                    MyOtoTry = '1'
                    _winreg.SetValueEx(myregway, "mplynm"+str(myclient), 0, _winreg.REG_SZ, str(player.GetName()))
                    _winreg.SetValueEx(myregway, "mplylv"+str(myclient), 0, _winreg.REG_SZ, str(player.GetStatus(player.LEVEL)))
                    _winreg.SetValueEx(myregway, "orthp"+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.HP)) / (float(player.GetStatus(player.MAX_HP))) * 100))
                    _winreg.SetValueEx(myregway, "ortmp"+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.SP)) / (float(player.GetStatus(player.MAX_SP))) * 100))
                    _winreg.SetValueEx(myregway, "ortexp"+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.EXP)) / (float(player.GetStatus(player.NEXT_EXP))) * 100))
                    _winreg.SetValueEx(myregway, "mjob"+str(myclient), 0, _winreg.REG_SZ, str(net.GetMainActorSkillGroup()))
                    _winreg.SetValueEx(myregway, "mrace"+str(myclient), 0, _winreg.REG_SZ, str(net.GetMainActorRace()))
                    zoombvalue = _winreg.QueryValueEx(key, 'zoomb'+str(myclient))[0]
                    if zoombvalue == '1':
                        app.SetCameraMaxDistance(12000)
                        _winreg.SetValueEx(myregway, "zoomb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    ghostbvalue = _winreg.QueryValueEx(key, 'ghostb'+str(myclient))[0]
                    if ghostbvalue == '1':
                        chr.Revive()
                        _winreg.SetValueEx(myregway, "ghostb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    nofogbvalue = _winreg.QueryValueEx(key, 'nofogb'+str(myclient))[0]
                    if nofogbvalue == '1':
                        chr.Revive()
                        _winreg.SetValueEx(myregway, "nofogb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    sumonhorsebvalue = _winreg.QueryValueEx(key, 'sumonhorseb'+str(myclient))[0]
                    if sumonhorsebvalue == '1':
                        net.SendChatPacket("/ride")
                        _winreg.SetValueEx(myregway, "sumonhorseb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    reloginbvalue = _winreg.QueryValueEx(key, 'reloginb'+str(myclient))[0]
                    if reloginbvalue == '1':
                        net.DirectEnter(0)
                        net.DirectEnter(0)
                    changecharacterbvalue = _winreg.QueryValueEx(key, 'changecharacterb'+str(myclient))[0]
                    if changecharacterbvalue == '1':
                        net.SendChatPacket('/phase_select')
                        _winreg.SetValueEx(myregway, "changecharacterb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    dropinventory2bvalue = _winreg.QueryValueEx(key, 'dropinventory2b'+str(myclient))[0]
                    if dropinventory2bvalue == '1':
                        for i in range(45, 90):
                            net.SendItemDropPacketNew(i, 1)
                        _winreg.SetValueEx(myregway, "dropinventory2b"+str(myclient), 0, _winreg.REG_SZ, '0')
                    logoutbvalue = _winreg.QueryValueEx(key, 'logoutb'+str(myclient))[0]
                    if logoutbvalue == '1':
                        net.SendChatPacket("/logout")
                        _winreg.SetValueEx(myregway, "logoutb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    skillc1bvalue = _winreg.QueryValueEx(key, 'skillc1b'+str(myclient))[0]
                    if skillc1bvalue == '1' and player.IsSkillCoolTime(1) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(1)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc2bvalue = _winreg.QueryValueEx(key, 'skillc2b'+str(myclient))[0]
                    if skillc2bvalue == '1' and player.IsSkillCoolTime(2) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(2)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc3bvalue = _winreg.QueryValueEx(key, 'skillc3b'+str(myclient))[0]
                    if skillc3bvalue == '1' and player.IsSkillCoolTime(3) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(3)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc4bvalue = _winreg.QueryValueEx(key, 'skillc4b'+str(myclient))[0]
                    if skillc4bvalue == '1' and player.IsSkillCoolTime(4) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(4)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc5bvalue = _winreg.QueryValueEx(key, 'skillc5b'+str(myclient))[0]
                    if skillc5bvalue == '1' and player.IsSkillCoolTime(5) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(5)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc6bvalue = _winreg.QueryValueEx(key, 'skillc6b'+str(myclient))[0]
                    if skillc6bvalue == '1' and player.IsSkillCoolTime(6) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket("/ride")
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(6)
                            useblehorse = 1
                            self.usehorse_delay()
                    upgradeslot1bvalue = _winreg.QueryValueEx(key, 'upgradeslot1b'+str(myclient))[0]
                    upgradeslot2bvalue = _winreg.QueryValueEx(key, 'upgradeslot2b'+str(myclient))[0]
                    upgradeslot3bvalue = _winreg.QueryValueEx(key, 'upgradeslot3b'+str(myclient))[0]
                    upgradeslot4bvalue = _winreg.QueryValueEx(key, 'upgradeslot4b'+str(myclient))[0]
                    upgradeslot5bvalue = _winreg.QueryValueEx(key, 'upgradeslot5b'+str(myclient))[0]
                    upgradeslot6bvalue = _winreg.QueryValueEx(key, 'upgradeslot6b'+str(myclient))[0]
                    upgradeslot7bvalue = _winreg.QueryValueEx(key, 'upgradeslot7b'+str(myclient))[0]
                    upgradeslot8bvalue = _winreg.QueryValueEx(key, 'upgradeslot8b'+str(myclient))[0]
                    upgradebvalue = _winreg.QueryValueEx(key, 'upgradeb'+str(myclient))[0]
                    upgradetypebvalue = _winreg.QueryValueEx(key, 'upgradetypeb'+str(myclient))[0]
                    upgradecountbvalue = _winreg.QueryValueEx(key, 'upgradecountb'+str(myclient))[0]
                    if upgradebvalue == '1':
                        for i in range(0, int(upgradecountbvalue)):
                            if upgradeslot1bvalue == '1':
                                net.SendRefinePacket(0, int(upgradetypebvalue))
                            if upgradeslot2bvalue == '1':
                                net.SendRefinePacket(1, int(upgradetypebvalue))
                            if upgradeslot3bvalue == '1':
                                net.SendRefinePacket(2, int(upgradetypebvalue))
                            if upgradeslot4bvalue == '1':
                                net.SendRefinePacket(3, int(upgradetypebvalue))
                            if upgradeslot5bvalue == '1':
                                net.SendRefinePacket(4, int(upgradetypebvalue))
                            if upgradeslot6bvalue == '1':
                                net.SendRefinePacket(5, int(upgradetypebvalue))
                            if upgradeslot7bvalue == '1':
                                net.SendRefinePacket(6, int(upgradetypebvalue))
                            if upgradeslot8bvalue == '1':
                                net.SendRefinePacket(7, int(upgradetypebvalue))
                        _winreg.SetValueEx(myregway, "upgradeb"+str(myclient), 0, _winreg.REG_SZ, '0')
                    islot1bvalue = _winreg.QueryValueEx(key, 'islot1b'+str(myclient))[0]
                    islot2bvalue = _winreg.QueryValueEx(key, 'islot2b'+str(myclient))[0]
                    islot3bvalue = _winreg.QueryValueEx(key, 'islot3b'+str(myclient))[0]
                    islot4bvalue = _winreg.QueryValueEx(key, 'islot4b'+str(myclient))[0]
                    islot5bvalue = _winreg.QueryValueEx(key, 'islot5b'+str(myclient))[0]
                    islot6bvalue = _winreg.QueryValueEx(key, 'islot6b'+str(myclient))[0]
                    slotms1value = _winreg.QueryValueEx(key, 'slotms1'+str(myclient))[0]
                    slotms2value = _winreg.QueryValueEx(key, 'slotms2'+str(myclient))[0]
                    slotms3value = _winreg.QueryValueEx(key, 'slotms3'+str(myclient))[0]
                    slotms4value = _winreg.QueryValueEx(key, 'slotms4'+str(myclient))[0]
                    slotms5value = _winreg.QueryValueEx(key, 'slotms5'+str(myclient))[0]
                    slotms6value = _winreg.QueryValueEx(key, 'slotms6'+str(myclient))[0]
                    if islot1bvalue == '1':
                        net.SendItemUsePacket(1, 0)
                    if islot2bvalue == '1':
                        net.SendItemUsePacket(1, 1)
                    if islot3bvalue == '1':
                        net.SendItemUsePacket(1, 2)
                    if islot4bvalue == '1':
                        net.SendItemUsePacket(1, 3)
                    if islot5bvalue == '1':
                        net.SendItemUsePacket(1, 4)
                    if islot6bvalue == '1':
                        net.SendItemUsePacket(1, 5)
            except WindowsError:
                print('Anahtar bulunamadı.')


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

Dialog1().Show()