import ui
import time
import _winreg
import net as net
import chat as chat
import player as player
import chr as chr
import app as app
myclient = 3
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
        self.__BuildKeyDict()
        self.DumpServerInfo()

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
        try:
            import ServerInfo

            self.ServerNames = []
            self.AuthServers = []
            self.AuthPorts = []
            self.ServerIps = []
            self.ServerPorts = []
            try:
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
                        if line.find('net.SetServerInfo("') != -1 and not line.find('AAA') != -1:
                            if not line.split('"')[1] in ServerNames:
                                ServerNames.append(line.split('"')[1])
            except:
                self.kickfinish()
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
        except:
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
            net.SendChatPacket('/ride')

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
                    MyOnline = '0'
                else:
                    MyOnline = '1'
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'SOFTWARE\\BinDir')
                myregway = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r'SOFTWARE\\BinDir')
                if MyOnline =='0' and MyOtoTry == '1':
                    autologinbvalue = _winreg.QueryValueEx(key, 'autologinb'+str(myclient))[0]
                    if autologinbvalue == '1':
                        net.DirectEnter(0)
                        MyOtoTry = '0'
                _winreg.SetValueEx(myregway, 'onln'+str(myclient), 0, _winreg.REG_SZ, MyOnline)
                if(MyOnline =='1'):
                    MyOtoTry = '1'
                    _winreg.SetValueEx(myregway, 'mplynm'+str(myclient), 0, _winreg.REG_SZ, str(player.GetName()))
                    _winreg.SetValueEx(myregway, 'mplylv'+str(myclient), 0, _winreg.REG_SZ, str(player.GetStatus(player.LEVEL)))
                    _winreg.SetValueEx(myregway, 'orthp'+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.HP)) / (float(player.GetStatus(player.MAX_HP))) * 100))
                    _winreg.SetValueEx(myregway, 'ortmp'+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.SP)) / (float(player.GetStatus(player.MAX_SP))) * 100))
                    _winreg.SetValueEx(myregway, 'ortexp'+str(myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.EXP)) / (float(player.GetStatus(player.NEXT_EXP))) * 100))
                    _winreg.SetValueEx(myregway, 'mjob'+str(myclient), 0, _winreg.REG_SZ, str(net.GetMainActorSkillGroup()))
                    _winreg.SetValueEx(myregway, 'mrace'+str(myclient), 0, _winreg.REG_SZ, str(net.GetMainActorRace()))
                    zoombvalue = _winreg.QueryValueEx(key, 'zoomb'+str(myclient))[0]
                    if zoombvalue == '1':
                        app.SetCameraMaxDistance(12000)
                        _winreg.SetValueEx(myregway, 'zoomb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    ghostbvalue = _winreg.QueryValueEx(key, 'ghostb'+str(myclient))[0]
                    if ghostbvalue == '1':
                        chr.Revive()
                        _winreg.SetValueEx(myregway, 'ghostb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    nofogbvalue = _winreg.QueryValueEx(key, 'nofogb'+str(myclient))[0]
                    if nofogbvalue == '1':
                        chr.Revive()
                        _winreg.SetValueEx(myregway, 'nofogb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    sumonhorsebvalue = _winreg.QueryValueEx(key, 'sumonhorseb'+str(myclient))[0]
                    if sumonhorsebvalue == '1':
                        net.SendChatPacket('/ride')
                        _winreg.SetValueEx(myregway, 'sumonhorseb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    reloginbvalue = _winreg.QueryValueEx(key, 'reloginb'+str(myclient))[0]
                    if reloginbvalue == '1':
                        net.DirectEnter(0)
                        _winreg.SetValueEx(myregway, 'reloginb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    changecharacterbvalue = _winreg.QueryValueEx(key, 'changecharacterb'+str(myclient))[0]
                    if changecharacterbvalue == '1':
                        net.SendChatPacket('/phase_select')
                        _winreg.SetValueEx(myregway, 'changecharacterb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    dropinventory2bvalue = _winreg.QueryValueEx(key, 'dropinventory2b'+str(myclient))[0]
                    if dropinventory2bvalue == '1':
                        for i in range(45, 90):
                            net.SendItemDropPacketNew(i, 1)
                        _winreg.SetValueEx(myregway, 'dropinventory2b'+str(myclient), 0, _winreg.REG_SZ, '0')
                    logoutbvalue = _winreg.QueryValueEx(key, 'logoutb'+str(myclient))[0]
                    if logoutbvalue == '1':
                        net.SendChatPacket('/logout')
                        _winreg.SetValueEx(myregway, 'logoutb'+str(myclient), 0, _winreg.REG_SZ, '0')
                    skillc1bvalue = _winreg.QueryValueEx(key, 'skillc1b'+str(myclient))[0]
                    if skillc1bvalue == '1' and player.IsSkillCoolTime(1) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(1)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc2bvalue = _winreg.QueryValueEx(key, 'skillc2b'+str(myclient))[0]
                    if skillc2bvalue == '1' and player.IsSkillCoolTime(2) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(2)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc3bvalue = _winreg.QueryValueEx(key, 'skillc3b'+str(myclient))[0]
                    if skillc3bvalue == '1' and player.IsSkillCoolTime(3) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(3)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc4bvalue = _winreg.QueryValueEx(key, 'skillc4b'+str(myclient))[0]
                    if skillc4bvalue == '1' and player.IsSkillCoolTime(4) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(4)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc5bvalue = _winreg.QueryValueEx(key, 'skillc5b'+str(myclient))[0]
                    if skillc5bvalue == '1' and player.IsSkillCoolTime(5) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(5)
                            useblehorse = 1
                            self.usehorse_delay()
                    skillc6bvalue = _winreg.QueryValueEx(key, 'skillc6b'+str(myclient))[0]
                    if skillc6bvalue == '1' and player.IsSkillCoolTime(6) == 0:
                        if player.IsMountingHorse() == 1:
                            net.SendChatPacket(('/ride'))
                        if player.IsMountingHorse() == 0:
                            player.ClickSkillSlot(6)
                            useblehorse = 1
                            self.usehorse_delay()
            except WindowsError:
                useblehorse = 0
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