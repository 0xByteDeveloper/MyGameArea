import math
import dbg
import ui
import time
import _winreg
import net as net
import chat as chat
import player as player
import chr as chr
import app as app
import chrmgr as chrmgr
import background as background
class Dialog1(ui.Window):
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'SOFTWARE\\BinDir')
    onlinestatuselementscontrol = 0
    mobgetstatuselementscontrol = 0
    rootuseri = 0
    myclient = 1
    mapmyregway = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r'SOFTWARE\\BinDir\\climap1')
    autologinbvalue = '0'
    kontroluseslot1 = 0
    kontroluseslot2 = 0
    kontroluseslot3 = 0
    kontroluseslot4 = 0
    kontroluseslot5 = 0
    kontroluseslot6 = 0
    onefinish = 0
    logingame = 0
    usableactive1 = 0
    usableactive2 = 0
    boostactive = 0
    MyOtoTry = '0'
    clogintypefnction = _winreg.QueryValueEx(key, 'clogintypefnction'+str(myclient))[0]
    cloginfnction = _winreg.QueryValueEx(key, 'cloginfnction'+str(myclient))[0]
    try:
        cotolgn = _winreg.QueryValueEx(key, 'cotolgn'+str(myclient))[0]
    except:
        cotolgn = 0
    try:
        Myusername = _winreg.QueryValueEx(key, 'cusernm'+str(myclient))[0]
    except:
        Myusername = 0
    try:
        Mypass = _winreg.QueryValueEx(key, 'cpassw'+str(myclient))[0]
    except:
        Mypass = 0
    try:
        cchannel = _winreg.QueryValueEx(key, 'cchannel'+str(myclient))[0]
    except:
        cchannel = 0
    try:
        cminisv = _winreg.QueryValueEx(key, 'cminisv'+str(myclient))[0]
    except:
        cminisv = 0
    globalx = 0
    globaly = 0
    number_list = []
    number_list2 = []
    MyOnline = ''
    denemedeger = 0
    useblehorse = 0
    mspeed = 0
    mspeed2 = 0
    mspeed3 = 0
    myregway = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, r'SOFTWARE\\BinDir')
    ServerNames = []
    AuthServers = []
    AuthPorts = []
    ServerIps = []
    ServerPorts = []
    #fonksvaryok
    netGetMainActorVIDvy = 3
    playerGetMainCharacterIndexvy = 3
    playerGetMainCharacterPositionvy = 3
    chrGetPixelPositionvy = 3
    chrGetInstanceTypevy = 3
    chrmgrGetVIDInfovy = 3
    def __init__(self):
        ui.Window.__init__(self)
        self.BuildWindow()
    def BuildWindow(self):
        self.__BuildKeyDict()
        self.DumpServerInfo()
        _winreg.SetValueEx(self.myregway, 'pysoket'+str(self.myclient), 0, _winreg.REG_SZ, '1')
    def __BuildKeyDict(self):
        onPressKeyDict = {}
        onPressKeyDict[app.DIK_F5] = lambda : self.OpenWindow()
        self.onPressKeyDict = onPressKeyDict
    def OpenWindow(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()
#classfuncs net
    def net_GetMainActorVID(self):
        try:
            return net.GetMainActorVID()
        except:
            self.netGetMainActorVIDvy = 0
            return 0
    def net_SetPacketSequenceMode(self):
        try:
            net.SetPacketSequenceMode()
        except:
            self.useblehorse = 0
    def net_SetLoginInfo(self, AccountID, Password):
        try:
            net.SetLoginInfo(AccountID, Password)
        except:
            self.useblehorse = 0
    def net_ConnectToAccountServer(self, ChannelIP, ChannelPort, AuthServerIP, AuthServerPort):
        try:
            net.ConnectToAccountServer(ChannelIP, ChannelPort, AuthServerIP, AuthServerPort)
        except:
            self.useblehorse = 0
    def net_ConnectTCP(self,ChannelIP, ChannelPort):
        try:
            net.ConnectTCP(ChannelIP, ChannelPort)
        except:
            self.useblehorse = 0
    def net_DirectEnter(self):
        try:
            net.DirectEnter(0)
        except:
            self.useblehorse = 0
    def net_SendItemUsePacket(self,value):
        try:
            net.SendItemUsePacket(value)
        except:
            self.useblehorse = 0
    def net_SendRefinePacket(self,v1, v2):
        try:
            net.SendRefinePacket(v1,v2)
        except:
            self.useblehorse = 0
    def net_SendChatPacket(self,value):
        try:
            net.SendChatPacket(value)
        except:
            self.useblehorse = 0
    def net_SendItemDropPacketNew(self,v1,v2):
        try:
            net.SendItemDropPacketNew(v1, v2)
        except:
            self.useblehorse = 0
    def net_SendCommandPacket(self,v1,v2,v3):
        try:
            net.SendCommandPacket(v1,v2,v3)
        except:
            self.useblehorse = 0
#classfuncs app
    def app_SetCameraMaxDistance(self):
        try:
            app.SetCameraMaxDistance(15000)
        except:
            self.useblehorse = 0
    def app_SetMinFog(self):
        try:
            app.SetMinFog(20000)
        except:
            self.useblehorse = 0
#classfuncs background
    def background_SetEnvironmentData(self,value):
        try:
            background.SetEnvironmentData(value)
        except:
            self.useblehorse = 0
    def background_RegisterEnvironmentData(self):
        try:
            background.RegisterEnvironmentData(1, constInfo.ENVIRONMENT_NIGHT)
        except:
            self.useblehorse = 0
    def background_EnableSnow(self,value):
        try:
            background.EnableSnow(value)
        except:
            self.useblehorse = 0
    def background_GetCurrentMapName(self):
        try:
            if background.GetCurrentMapName():
                return str(background.GetCurrentMapName())
            else:
                return 'None'
        except:
            return 0
#classfuncs chr
    def chr_Revive(self):
        try:
            chr.Revive()
        except:
            self.useblehorse = 0
    def chr_GetInstanceType(self,v1):
        try:
            return chr.GetInstanceType(v1)
        except:
            self.chrGetInstanceTypevy = 0
            return 0
    def chr_GetPixelPosition(self,v1):
        try:
            return chr.GetPixelPosition(v1)
        except:
            self.chrGetPixelPositionvy = 0
            return 0
    def chr_GetRotation(self):
        try:
            return chr.GetRotation()
        except:
            self.useblehorse = 0
            return 0
    def chr_SetPixelPosition(self,v1,v2,v3):
        try:
            chr.SetPixelPosition(v1,v2,v3)
        except:
            self.useblehorse = 0
#classfuncs chrmgr
    def chrmgr_SetAffect(self,v1,v2,v3):
        try:
            chrmgr.SetAffect(v1,v2,v3)
        except:
            self.useblehorse = 0
    def chrmgr_SetMovingSpeed(self,v1):
        try:
            chrmgr.SetMovingSpeed(v1)
        except:
            self.useblehorse = 0
    def chrmgr_GetVIDInfo(self,v1):
        try:
            return chrmgr.GetVIDInfo(v1)
        except:
            return 0
            self.chrmgrGetVIDInfovy = 0
#classfuncs player
    def player_GetMainCharacterIndex(self):
        try:
            return player.GetMainCharacterIndex()
        except:
            self.playerGetMainCharacterIndexvy = 0
            return 0
    def player_PickCloseItem(self):
        try:
            return player.PickCloseItem()
        except:
            self.useblehorse = 0
    def player_GetMainCharacterPosition(self):
        try:
            return player.GetMainCharacterPosition()
        except:
            self.playerGetMainCharacterPositionvy = 0
            return 0
    def player_IsMountingHorse(self):
        try:
            if player.IsMountingHorse() == 1:
                return '1'
            else:
                return '0'
        except:
            return '0'
    def player_IsSkillCoolTime(self,value):
        try:
            if player.IsSkillCoolTime(value) == 1:
                return 1
            else:
                return 0
        except:
            return 0
    def player_ClickSkillSlot(self,v1):
        try:
            player.ClickSkillSlot(v1)
        except:
            self.useblehorse = 0
    def player_GetStatus(self):
        try:
            _winreg.SetValueEx(self.myregway, 'orthp'+str(self.myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.HP)) / (float(player.GetStatus(player.MAX_HP))) * 100))
        except:
            self.useblehorse = 0
        try:
            _winreg.SetValueEx(self.myregway, 'ortmp'+str(self.myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.SP)) / (float(player.GetStatus(player.MAX_SP))) * 100))
        except:
            self.useblehorse = 0
        try:
            _winreg.SetValueEx(self.myregway, 'ortexp'+str(self.myclient), 0, _winreg.REG_SZ, str(float(player.GetStatus(player.EXP)) / (float(player.GetStatus(player.NEXT_EXP))) * 100))
        except:
            self.useblehorse = 0
        try:
            _winreg.SetValueEx(self.myregway, 'mplylv'+str(self.myclient), 0, _winreg.REG_SZ, str(player.GetStatus(player.LEVEL)))
        except:
            self.useblehorse = 0
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
    def DumpServerInfo(self):
        self.ServerNames = []
        self.AuthServers = []
        self.AuthPorts = []
        self.ServerIps = []
        self.ServerPorts = []
        try:
            import serverInfo
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
            for Server in xrange(len(serverInfo.REGION_DICT[int(self.cminisv)])):
                self.ServerIps = []
                self.ServerPorts = []
                self.ServerName = serverInfo.REGION_DICT[int(self.cminisv)][Server + 1]['name']
                AuthServerIp = serverInfo.REGION_AUTH_SERVER_DICT[0][Server + 1]['ip']
                self.AuthServers.append(AuthServerIp)
                AuthServerPort = serverInfo.REGION_AUTH_SERVER_DICT[0][Server + 1]['port']
                self.AuthPorts.append(AuthServerPort)
                for Channel in xrange(len(serverInfo.REGION_DICT[int(self.cminisv)][Server + 1]['channel'])):
                    self.ServerIps.append(serverInfo.REGION_DICT[int(self.cminisv)][Server + 1]['channel'][Channel + 1]['ip'])
                    ServerPort = serverInfo.REGION_DICT[int(self.cminisv)][Server + 1]['channel'][Channel + 1]['tcp_port']
                    if not ServerPort in self.ServerPorts:
                        self.ServerPorts.append(ServerPort)
                for Channels in self.ServerPorts:
                    Index = self.ServerPorts.index(Channels)
            if(self.cloginfnction == '1' and self.clogintypefnction == '0' and self.cotolgn == '1'):
                self.DirectConnect(self.AuthServers[int(self.cchannel)], self.AuthPorts[int(self.cchannel)], self.ServerIps[int(self.cchannel)], self.ServerPorts[int(self.cchannel)], str(self.Myusername), str(self.Mypass))
            else:
                self.kickfinish()
        except:
            self.kickfinish()
    def DirectConnect(self, AuthServerIP, AuthServerPort, ChannelIP, ChannelPort, AccountID, Password):
        self.net_SetPacketSequenceMode()
        self.net_SetLoginInfo(AccountID, Password)
        self.net_ConnectToAccountServer(ChannelIP, ChannelPort, AuthServerIP, AuthServerPort)
        self.login_enter_delay()
    def CHDirectConnect(self, AuthServerIP, AuthServerPort, ChannelIP, ChannelPort, AccountID, Password):
        chchangemethodvalue = _winreg.QueryValueEx(self.key, 'chchangemethod'+str(self.myclient))[0]
        self.net_SetPacketSequenceMode()
        self.net_SetLoginInfo(AccountID, Password)
        if chchangemethodvalue == '0':
            self.net_ConnectToAccountServer(ChannelIP, ChannelPort, AuthServerIP, AuthServerPort)
        if chchangemethodvalue == '1':
            self.net_ConnectTCP(ChannelIP, ChannelPort)
        if self.autologinbvalue == '0':
            self.login_enter_delay()
    def login_enter_delay(self):
        self.login_enter_WaitingDialog = WaitingDialog()
        self.login_enter_WaitingDialog.Open(int(11))
        if self.logingame == 0:
            self.login_enter_WaitingDialog.SAFE_SetTimeOverEvent(self.login_enter_fnc)
            if self.onefinish == 0:
                self.logingame = 1
                self.onefinish = 1
    def login_enter_fnc(self):
        try:
            self.net_DirectEnter()
            self.kickfinish()
        except:
            self.kickfinish()
    def usblefunc(self):
        if self.usableactive2 < 3:
            self.usblefuncseg = WaitingDialog()
            self.usblefuncseg.Open(3)
            self.usblefuncseg.SAFE_SetTimeOverEvent(self.usblefunc)
            self.usableactive2 = self.usableactive2 + 1
    def boosttabdelay(self):
            self.boostseg = WaitingDialog()
            self.boostseg.Open(1)
            self.boostseg.SAFE_SetTimeOverEvent(self.boosttab)
            self.boostactive = 1
    def boosttab(self):
        self.boosttabseg = WaitingDialog()
        self.boosttabseg.Open(0.01)
        self.boosttabseg.SAFE_SetTimeOverEvent(self.boosttab)
        walkspeedstatusbvalue = _winreg.QueryValueEx(self.key, 'walkspeedstatusb'+str(self.myclient))[0]
        movspeed3bvalue = _winreg.QueryValueEx(self.key, 'movspeed3b'+str(self.myclient))[0]
        movspeedvaluebvalue = _winreg.QueryValueEx(self.key, 'walkspd'+str(self.myclient))[0]
        if walkspeedstatusbvalue == '1' and movspeed3bvalue == '1':
            px, py, pz = self.player_GetMainCharacterPosition()
            if app.IsPressed(app.DIK_LSHIFT) or app.IsPressed(app.DIK_UP) or app.IsPressed(app.DIK_DOWN) or app.IsPressed(app.DIK_LEFT) or app.IsPressed(app.DIK_RIGHT) or app.IsPressed(app.DIK_W)  or app.IsPressed(app.DIK_A)  or app.IsPressed(app.DIK_S)  or app.IsPressed(app.DIK_D):
                rotation = 360.0 - self.chr_GetRotation()
                frotation = 180.0 - rotation
                xx = int(movspeedvaluebvalue) * math.sin(frotation * 0.017453)
                yy = int(movspeedvaluebvalue) * math.cos(frotation * 0.017453)
                newPositionx = float(px + xx)
                newPositiony = float(py - yy)
                self.chr_SetPixelPosition(newPositionx, newPositiony, pz)
    def kickfinish(self):
            self.kickseg = WaitingDialog()
            self.kickseg.Open((0.3))
            self.kickseg.SAFE_SetTimeOverEvent(self.kickfinish)
            try:
                self.Onlinestatus()
                self.Otologincontrol()
                if(self.MyOnline =='0'):
                    self.usableactive2 = 0
                    self.usableactive1 = 0
                if(self.MyOnline =='1'):
                    if self.usableactive1 == 0:
                        self.usblefunc()
                        self.usableactive1 = 1
                    if self.usableactive2 == 3:
                        self.MyOtoTry = '1'
                        Mobgettervalue = _winreg.QueryValueEx(self.key, 'cmobgetter'+str(self.myclient))[0]
                        if Mobgettervalue == '1':
                            self.Mobgetterfunction()
                        self.MyGetStatus()
                        self.menutab1genel()
                        self.menutab3farm()
                        if self.boostactive == 0:
                            self.boosttabdelay()
            except:
                self.useblehorse = 0
    def Onlinestatus(self):
        PyO2bvalue = _winreg.QueryValueEx(self.key, 'PyO2b'+str(self.myclient))[0]
        if PyO2bvalue == '0':
            try:
                cpponlinevalue = _winreg.QueryValueEx(self.key, 'cpponline'+str(self.myclient))[0]
                if cpponlinevalue == '1':
                    self.MyOnline = '1'
                if cpponlinevalue == '0':
                    self.MyOnline = '0'
            except:
                self.useblehorse = 0
        if PyO2bvalue == '1':
            if self.onlinestatuselementscontrol == 0:
                self.chr_GetPixelPosition(0)
                self.net_GetMainActorVID()
                self.onlinestatuselementscontrol = 1
            if self.onlinestatuselementscontrol == 1:
                if self.chrGetPixelPositionvy == 3 and self.netGetMainActorVIDvy == 3:
                    OnlineControl = str(self.chr_GetPixelPosition(self.net_GetMainActorVID()))
                    if OnlineControl == 'None':
                        self.MyOnline = '0'
                    else:
                        self.MyOnline = '1'
                else:
                    if self.player_GetMainCharacterPosition()[0] > -71 and self.player_GetMainCharacterPosition()[0] < 71:
                        self.MyOnline = '0'
                    else:
                        self.MyOnline = '1'
    def Otologincontrol(self):
        if self.MyOtoTry == '1':
            reloginbvalue = _winreg.QueryValueEx(self.key, 'reloginb'+str(self.myclient))[0]
            if reloginbvalue == '1':
                self.otologinorenterfunc()
                _winreg.SetValueEx(self.myregway, 'reloginb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        if self.MyOnline =='0' and self.MyOtoTry == '1':
            self.autologinbvalue = _winreg.QueryValueEx(self.key, 'autologinb'+str(self.myclient))[0]
            if self.autologinbvalue == '1':
                self.otologinorenterfunc()
                self.MyOtoTry = '0'
        _winreg.SetValueEx(self.myregway, 'onln'+str(self.myclient), 0, _winreg.REG_SZ, self.MyOnline)
    def Mobgetterfunction(self):
        if self.mobgetstatuselementscontrol == 0:
            self.chr_GetPixelPosition(0)
            self.chr_GetInstanceType(0)
            self.chrmgr_GetVIDInfo(0)
            self.player_GetMainCharacterIndex()
            self.player_GetMainCharacterPosition()
        if self.mobgetstatuselementscontrol == 1:
            if self.chrGetPixelPositionvy == 3 and self.chrGetInstanceTypevy == 3:
                for i in xrange(0, 30000):
                    if i == 29000:
                        if self.denemedeger == 0:
                            self.denemedeger = 1
                    if 2 == self.chr_GetInstanceType(i) or 1 == self.chr_GetInstanceType(i) or 0 == self.chr_GetInstanceType(i):
                        self.number_list.append((i))
                        if self.denemedeger == 0:
                            self.number_list2.append((i))
                if len(self.number_list) != len(self.number_list2):
                    self.number_list2 = []
                    self.number_list2.extend(self.number_list)
                    self.denemedeger = 0
                self.number_list = []
                _winreg.SetValueEx(self.mapmyregway, 'maxM', 0, _winreg.REG_SZ, str(len(self.number_list2)-1))
                if len(self.number_list2) != 0:
                    for i in xrange(0, len(self.number_list2)):
                        if len(self.number_list2) > 1:
                            xx, yy, zz = self.chr_GetPixelPosition(self.number_list2[i])
                            generalstr = str(xx) + ',' + str(yy * -1) + '^' + str(self.chr_GetInstanceType(self.number_list2[i]))
                            _winreg.SetValueEx(self.mapmyregway, str(i), 0, _winreg.REG_SZ, str(generalstr))
            if self.playerGetMainCharacterPositionvy == 3 and self.playerGetMainCharacterIndexvy == 3 and self.chrGetInstanceTypevy == 3 and self.chrmgrGetVIDInfovy == 3:
                for i in xrange(0, 30000):
                    if i == 29000:
                        if self.denemedeger == 0:
                            self.denemedeger = 1
                    if 2 == chr.GetInstanceType(i) or 1 == chr.GetInstanceType(i) or 0 == chr.GetInstanceType(i):
                        info = str(chrmgr.GetVIDInfo(player.GetMainCharacterIndex()))
                        splitinfo = info.split('pos=(')
                        splitinfo2 = splitinfo[1].split(', ')
                        splitinfo3 = splitinfo2[1].split(')')
                        pxx, pyy, pzz = player.GetMainCharacterPosition()
                        self.globalx = int(splitinfo2[0]) - pxx
                        self.globaly = int(splitinfo3[0]) - pyy
                        self.number_list.append((i))
                        if self.denemedeger == 0:
                            self.number_list2.append((i))
                if len(self.number_list) != len(self.number_list2):
                    self.number_list2 = []
                    self.number_list2.extend(number_list)
                    self.denemedeger = 0
                self.number_list = []
                _winreg.SetValueEx(self.mapmyregway, 'maxM', 0, _winreg.REG_SZ, str(len(self.number_list2)-1))
                if len(self.number_list2) != 0:
                    for i in xrange(0, len(self.number_list2)):
                        if len(self.number_list2) > 1:
                            info = str(chrmgr.GetVIDInfo(self.number_list2[i]))
                            splitinfo = info.split('pos=(')
                            splitinfo2 = splitinfo[1].split(', ')
                            splitinfo3 = splitinfo2[1].split(')')
                            xx = int(splitinfo2[0]) - self.globalx
                            yy = int(splitinfo3[0]) - self.globaly
                            generalstr = str(xx) + ',' + str(yy * -1) + '^' + str(chr.GetInstanceType(self.number_list2[i]))
                            _winreg.SetValueEx(self.mapmyregway, str(i), 0, _winreg.REG_SZ, str(generalstr))
    def MyGetStatus(self):
        self.player_GetStatus()
        try:
            _winreg.SetValueEx(self.myregway, 'mplynm'+str(self.myclient), 0, _winreg.REG_SZ, str(player.GetName()))
        except:
            self.useblehorse = 0
        try:
            _winreg.SetValueEx(self.myregway, 'mjob'+str(self.myclient), 0, _winreg.REG_SZ, str(net.GetMainActorSkillGroup()))
        except:
            self.useblehorse = 0
        try:
            _winreg.SetValueEx(self.myregway, 'mrace'+str(self.myclient), 0, _winreg.REG_SZ, str(net.GetMainActorRace()))
        except:
            self.useblehorse = 0
        if(self.net_GetMainActorVID() != 0 and self.netGetMainActorVIDvy != 0):
            _winreg.SetValueEx(self.myregway, 'myvid'+str(self.myclient), 0, _winreg.REG_SZ, str(self.net_GetMainActorVID()))
        else:
            if(self.player_GetMainCharacterIndex() != 0 and self.playerGetMainCharacterIndexvy != 0):
                _winreg.SetValueEx(self.myregway, 'myvid'+str(self.myclient), 0, _winreg.REG_SZ, str(self.player_GetMainCharacterIndex()))
            else:
                _winreg.SetValueEx(self.myregway, 'myvid'+str(self.myclient), 0, _winreg.REG_SZ, '0')
    def mspeed_delay(self):
        self.mspeed = 1
        self.mspeed_WaitingDialog = WaitingDialog()
        self.mspeed_WaitingDialog.Open(1.3)
        if self.mspeed2 == 0:
            self.mspeed_WaitingDialog.SAFE_SetTimeOverEvent(self.mspeed_fnc)
            self.mspeed2 = 1
    def mspeed_fnc(self):
        self.mspeed3 = 1
        self.chrmgr_SetMovingSpeed(10)
    def UseHorse(self):
        sumonhorsetrybvalue = _winreg.QueryValueEx(self.key, 'sumonhorsetry'+str(self.myclient))[0]
        shorsemethodbvalue = _winreg.QueryValueEx(self.key, 'shorsemethod'+str(self.myclient))[0]
        if sumonhorsetrybvalue == '1':
            if shorsemethodbvalue == '0':
                self.net_SendChatPacket('/ride')
            if shorsemethodbvalue == '1':
                self.net_SendCommandPacket(1,2,3)
        if sumonhorsetrybvalue == '0':
            if shorsemethodbvalue == '0':
                self.net_SendChatPacket('/ride')
                _winreg.SetValueEx(self.myregway, 'sumonhorseb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
            if shorsemethodbvalue == '1':
                self.net_SendCommandPacket(1,2,3)
                _winreg.SetValueEx(self.myregway, 'sumonhorseb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
    def otologinorenterfunc(self):
        otologinmethodvalue = _winreg.QueryValueEx(self.key, 'otologinmethod'+str(self.myclient))[0]
        if otologinmethodvalue == '0':
            self.net_DirectEnter()
        if otologinmethodvalue == '1':
            self.net_ConnectTCP(self.ServerIps[0], self.ServerPorts[0])
            self.logingame = 0
            self.login_enter_delay()
    def menutab1genel(self):
        _winreg.SetValueEx(self.mapmyregway, 'mapn' , 0, _winreg.REG_SZ, str(self.background_GetCurrentMapName()))
        px, py, pz = self.player_GetMainCharacterPosition()
        _winreg.SetValueEx(self.mapmyregway, 'px' , 0, _winreg.REG_SZ, str(px))
        _winreg.SetValueEx(self.mapmyregway, 'py' , 0, _winreg.REG_SZ, str(py * -1))
        _winreg.SetValueEx(self.mapmyregway, 'pz' , 0, _winreg.REG_SZ, str(pz))
        pckupenablebvalue = _winreg.QueryValueEx(self.key, 'pckupenable'+str(self.myclient))[0]
        if pckupenablebvalue == '1':
            self.player_PickCloseItem()
        zoombvalue = _winreg.QueryValueEx(self.key, 'zoomb'+str(self.myclient))[0]
        if zoombvalue == '1':
            self.app_SetCameraMaxDistance()
            _winreg.SetValueEx(self.myregway, 'zoomb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        ghostbvalue = _winreg.QueryValueEx(self.key, 'ghostb'+str(self.myclient))[0]
        if ghostbvalue == '1':
            self.chr_Revive()
            _winreg.SetValueEx(self.myregway, 'ghostb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        nofogbvalue = _winreg.QueryValueEx(self.key, 'nofogb'+str(self.myclient))[0]
        if nofogbvalue == '1':
            self.app_SetMinFog()
            _winreg.SetValueEx(self.myregway, 'nofogb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        sunbvalue = _winreg.QueryValueEx(self.key, 'sunb'+str(self.myclient))[0]
        if sunbvalue == '1':
            self.background_SetEnvironmentData(0)
            _winreg.SetValueEx(self.myregway, 'sunb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        if sunbvalue == '2':
            self.background_SetEnvironmentData(1)
            self.background_RegisterEnvironmentData()
            _winreg.SetValueEx(self.myregway, 'sunb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        snowbvalue = _winreg.QueryValueEx(self.key, 'snowb'+str(self.myclient))[0]
        if snowbvalue == '1':
            self.background_EnableSnow(1)
            _winreg.SetValueEx(self.myregway, 'snowb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        if snowbvalue == '2':
            self.background_EnableSnow(0)
            _winreg.SetValueEx(self.myregway, 'snowb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        myantiflvalue = _winreg.QueryValueEx(self.key, 'myantifl'+str(self.myclient))[0]
        if myantiflvalue == '1':
            self.chrmgr_SetAffect(-1,16,1)
        sumonhorsebvalue = _winreg.QueryValueEx(self.key, 'sumonhorseb'+str(self.myclient))[0]
        if sumonhorsebvalue == '1':
            if self.player_IsMountingHorse() == '0':
                self.UseHorse()
        walkspeedstatusbvalue = _winreg.QueryValueEx(self.key, 'walkspeedstatusb'+str(self.myclient))[0]
        movspeed1bvalue = _winreg.QueryValueEx(self.key, 'movspeed1b'+str(self.myclient))[0]
        movspeed2bvalue = _winreg.QueryValueEx(self.key, 'movspeed2b'+str(self.myclient))[0]
        movspeedvaluebvalue = _winreg.QueryValueEx(self.key, 'walkspd'+str(self.myclient))[0]
        if walkspeedstatusbvalue == '1':
            if movspeed1bvalue == '1':
                self.chrmgr_SetMovingSpeed(int(movspeedvaluebvalue))
            if movspeed2bvalue == '1':
                if self.mspeed == 0:
                    self.chrmgr_SetMovingSpeed(int(movspeedvaluebvalue))
                    self.mspeed_delay()
                if self.mspeed == 1 and self.mspeed2 == 1 and self.mspeed3 == 1:
                    self.mspeed = 0
                    self.mspeed2 = 0
                    self.mspeed3 = 0
        cmobgettervalue = _winreg.QueryValueEx(self.key, 'cmobgetter'+str(self.myclient))[0]
        attmetinsbvalue = _winreg.QueryValueEx(self.key, 'attmetinsb'+str(self.myclient))[0]
        attbossbvalue = _winreg.QueryValueEx(self.key, 'attbossb'+str(self.myclient))[0]
        mineoresbvalue = _winreg.QueryValueEx(self.key, 'mineoresb'+str(self.myclient))[0]
        changecharacterbvalue = _winreg.QueryValueEx(self.key, 'changecharacterb'+str(self.myclient))[0]
        if changecharacterbvalue == '1':
            self.net_SendChatPacket('/phase_select')
            _winreg.SetValueEx(self.myregway, 'changecharacterb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        dropinventory2bvalue = _winreg.QueryValueEx(self.key, 'dropinventory2b'+str(self.myclient))[0]
        invdropslotvalue = _winreg.QueryValueEx(self.key, 'invdropslot'+str(self.myclient))[0]
        if dropinventory2bvalue == '1':
            for i in range(int(invdropslotvalue) * 45, (int(invdropslotvalue) + 1)*45):
                self.net_SendItemDropPacketNew(i, 1)
            _winreg.SetValueEx(self.myregway, 'dropinventory2b'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        logoutbvalue = _winreg.QueryValueEx(self.key, 'logoutb'+str(self.myclient))[0]
        if logoutbvalue == '1':
            self.net_SendChatPacket('/logout')
            _winreg.SetValueEx(self.myregway, 'logoutb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        try:
            ch1bevalue = _winreg.QueryValueEx(self.key, 'ch1be'+str(self.myclient))[0]
            if ch1bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[0], self.AuthPorts[0], self.ServerIps[0], self.ServerPorts[0], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch1be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch2bevalue = _winreg.QueryValueEx(self.key, 'ch2be'+str(self.myclient))[0]
            if ch2bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[1], self.AuthPorts[1], self.ServerIps[1], self.ServerPorts[1], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch2be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch3bevalue = _winreg.QueryValueEx(self.key, 'ch3be'+str(self.myclient))[0]
            if ch3bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[2], self.AuthPorts[2], self.ServerIps[2], self.ServerPorts[2], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch3be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch4bevalue = _winreg.QueryValueEx(self.key, 'ch4be'+str(self.myclient))[0]
            if ch4bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[3], self.AuthPorts[3], self.ServerIps[3], self.ServerPorts[3], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch4be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch5bevalue = _winreg.QueryValueEx(self.key, 'ch5be'+str(self.myclient))[0]
            if ch5bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[4], self.AuthPorts[4], self.ServerIps[4], self.ServerPorts[4], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch5be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch6bevalue = _winreg.QueryValueEx(self.key, 'ch6be'+str(self.myclient))[0]
            if ch6bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[5], self.AuthPorts[5], self.ServerIps[5], self.ServerPorts[5], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch6be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch7bevalue = _winreg.QueryValueEx(self.key, 'ch7be'+str(self.myclient))[0]
            if ch7bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[6], self.AuthPorts[6], self.ServerIps[6], self.ServerPorts[6], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch7be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch8bevalue = _winreg.QueryValueEx(self.key, 'ch8be'+str(self.myclient))[0]
            if ch8bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[7], self.AuthPorts[7], self.ServerIps[7], self.ServerPorts[7], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch8be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        try:
            ch9bevalue = _winreg.QueryValueEx(self.key, 'ch9be'+str(self.myclient))[0]
            if ch9bevalue == '1':
                self.logingame = 0
                self.CHDirectConnect(self.AuthServers[8], self.AuthPorts[8], self.ServerIps[8], self.ServerPorts[8], str(self.Myusername), str(self.Mypass))
                _winreg.SetValueEx(self.myregway, 'ch9be'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        except:
            self.useblehorse = 0
        upgradebvalue = _winreg.QueryValueEx(self.key, 'upgradeb'+str(self.myclient))[0]
        upgradetypebvalue = _winreg.QueryValueEx(self.key, 'upgradetypeb'+str(self.myclient))[0]
        upgradecountbvalue = _winreg.QueryValueEx(self.key, 'upgradecountb'+str(self.myclient))[0]
        upgradeslot1bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot1b'+str(self.myclient))[0]
        upgradeslot2bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot2b'+str(self.myclient))[0]
        upgradeslot3bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot3b'+str(self.myclient))[0]
        upgradeslot4bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot4b'+str(self.myclient))[0]
        upgradeslot5bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot5b'+str(self.myclient))[0]
        upgradeslot6bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot6b'+str(self.myclient))[0]
        upgradeslot7bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot7b'+str(self.myclient))[0]
        upgradeslot8bvalue = _winreg.QueryValueEx(self.key, 'upgradeslot8b'+str(self.myclient))[0]
        if int(upgradebvalue) == 1:
            for i in xrange(0, int(upgradecountbvalue)):
                if upgradeslot1bvalue == '1':
                    self.net_SendRefinePacket(0,int(upgradetypebvalue))
                if upgradeslot2bvalue == '1':
                    self.net_SendRefinePacket(1,int(upgradetypebvalue))
                if upgradeslot3bvalue == '1':
                    self.net_SendRefinePacket(2,int(upgradetypebvalue))
                if upgradeslot4bvalue == '1':
                    self.net_SendRefinePacket(3,int(upgradetypebvalue))
                if upgradeslot5bvalue == '1':
                    self.net_SendRefinePacket(4,int(upgradetypebvalue))
                if upgradeslot6bvalue == '1':
                    self.net_SendRefinePacket(5,int(upgradetypebvalue))
                if upgradeslot7bvalue == '1':
                    self.net_SendRefinePacket(6,int(upgradetypebvalue))
                if upgradeslot8bvalue == '1':
                    self.net_SendRefinePacket(7,int(upgradetypebvalue))
            _winreg.SetValueEx(self.myregway, 'upgradeb'+str(self.myclient), 0, _winreg.REG_SZ, '0')
        islot1bvalue = _winreg.QueryValueEx(self.key, 'islot1b'+str(self.myclient))[0]
        islot2bvalue = _winreg.QueryValueEx(self.key, 'islot2b'+str(self.myclient))[0]
        islot3bvalue = _winreg.QueryValueEx(self.key, 'islot3b'+str(self.myclient))[0]
        islot4bvalue = _winreg.QueryValueEx(self.key, 'islot4b'+str(self.myclient))[0]
        islot5bvalue = _winreg.QueryValueEx(self.key, 'islot5b'+str(self.myclient))[0]
        islot6bvalue = _winreg.QueryValueEx(self.key, 'islot6b'+str(self.myclient))[0]
        if islot1bvalue == '1':
            if self.kontroluseslot1 == 0:
                self.useslot1_fnc()
                self.kontroluseslot1 = 1
        if islot2bvalue == '1':
            if self.kontroluseslot2 == 0:
                self.useslot2_fnc()
                self.kontroluseslot2 = 1
        if islot3bvalue == '1':
            if self.kontroluseslot3 == 0:
                self.useslot3_fnc()
                self.kontroluseslot3 = 1
        if islot4bvalue == '1':
            if self.kontroluseslot4 == 0:
                self.useslot4_fnc()
                self.kontroluseslot4 = 1
        if islot5bvalue == '1':
            if self.kontroluseslot5 == 0:
                self.useslot5_fnc()
                self.kontroluseslot5 = 1
        if islot6bvalue == '1':
            if self.kontroluseslot6 == 0:
                self.useslot6_fnc()
                self.kontroluseslot6 = 1
    def useslot1_fnc(self):
        slotms1value = _winreg.QueryValueEx(self.key, 'slotms1'+str(self.myclient))[0]
        self.kicksegs1 = WaitingDialog()
        self.kicksegs1.Open(float(str(slotms1value)))
        islot1bvalue = _winreg.QueryValueEx(self.key, 'islot1b'+str(self.myclient))[0]
        if islot1bvalue == '0':
            self.kontroluseslot1 = 0
        if islot1bvalue != '0':
            self.kicksegs1.SAFE_SetTimeOverEvent(self.useslot1_fnc)
        if islot1bvalue == '1':
            self.net_SendItemUsePacket(0)
    def useslot2_fnc(self):
        slotms2value = _winreg.QueryValueEx(self.key, 'slotms2'+str(self.myclient))[0]
        self.kicksegs2 = WaitingDialog()
        self.kicksegs2.Open(float(str(slotms2value)))
        islot2bvalue = _winreg.QueryValueEx(self.key, 'islot2b'+str(self.myclient))[0]
        if islot2bvalue == '0':
            self.kontroluseslot2 = 0
        if islot2bvalue != '0':
            self.kicksegs2.SAFE_SetTimeOverEvent(self.useslot2_fnc)
        if islot2bvalue == '1':
            self.net_SendItemUsePacket(1)
    def useslot3_fnc(self):
        slotms3value = _winreg.QueryValueEx(self.key, 'slotms3'+str(self.myclient))[0]
        self.kicksegs3 = WaitingDialog()
        self.kicksegs3.Open(float(str(slotms3value)))
        islot3bvalue = _winreg.QueryValueEx(self.key, 'islot3b'+str(self.myclient))[0]
        if islot3bvalue == '0':
            self.kontroluseslot3 = 0
        if islot3bvalue != '0':
            self.kicksegs3.SAFE_SetTimeOverEvent(self.useslot3_fnc)
        if islot3bvalue == '1':
            self.net_SendItemUsePacket(2)
    def useslot4_fnc(self):
        slotms4value = _winreg.QueryValueEx(self.key, 'slotms4'+str(self.myclient))[0]
        self.kicksegs4 = WaitingDialog()
        self.kicksegs4.Open(float(str(slotms4value)))
        islot4bvalue = _winreg.QueryValueEx(self.key, 'islot4b'+str(self.myclient))[0]
        if islot4bvalue == '0':
            self.kontroluseslot4 = 0
        if islot4bvalue != '0':
            self.kicksegs4.SAFE_SetTimeOverEvent(self.useslot4_fnc)
        if islot4bvalue == '1':
            self.net_SendItemUsePacket(3)
    def useslot5_fnc(self):
        slotms5value = _winreg.QueryValueEx(self.key, 'slotms5'+str(self.myclient))[0]
        self.kicksegs5 = WaitingDialog()
        self.kicksegs5.Open(float(str(slotms5value)))
        islot5bvalue = _winreg.QueryValueEx(self.key, 'islot5b'+str(self.myclient))[0]
        if islot5bvalue == '0':
            self.kontroluseslot5 = 0
        if islot5bvalue != '0':
            self.kicksegs5.SAFE_SetTimeOverEvent(self.useslot5_fnc)
        if islot5bvalue == '1':
            self.net_SendItemUsePacket(4)
    def useslot6_fnc(self):
        slotms6value = _winreg.QueryValueEx(self.key, 'slotms6'+str(self.myclient))[0]
        self.kicksegs6 = WaitingDialog()
        self.kicksegs6.Open(float(str(slotms6value)))
        islot6bvalue = _winreg.QueryValueEx(self.key, 'islot6b'+str(self.myclient))[0]
        if islot6bvalue == '0':
            self.kontroluseslot6 = 0
        if islot6bvalue != '0':
            self.kicksegs6.SAFE_SetTimeOverEvent(self.useslot6_fnc)
        if islot6bvalue == '1':
            self.net_SendItemUsePacket(5)
    def menutab3farm(self):
        skillc1bvalue = _winreg.QueryValueEx(self.key, 'skillc1b'+str(self.myclient))[0]
        if skillc1bvalue == '1' and self.player_IsSkillCoolTime(1) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(1)
                self.useblehorse = 1
                self.usehorse_delay()
        skillc2bvalue = _winreg.QueryValueEx(self.key, 'skillc2b'+str(self.myclient))[0]
        if skillc2bvalue == '1' and self.player_IsSkillCoolTime(2) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(2)
                self.useblehorse = 1
                self.usehorse_delay()
        skillc3bvalue = _winreg.QueryValueEx(self.key, 'skillc3b'+str(self.myclient))[0]
        if skillc3bvalue == '1' and self.player_IsSkillCoolTime(3) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(3)
                self.useblehorse = 1
                self.usehorse_delay()
        skillc4bvalue = _winreg.QueryValueEx(self.key, 'skillc4b'+str(self.myclient))[0]
        if skillc4bvalue == '1' and self.player_IsSkillCoolTime(4) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(4)
                self.useblehorse = 1
                self.usehorse_delay()
        skillc5bvalue = _winreg.QueryValueEx(self.key, 'skillc5b'+str(self.myclient))[0]
        if skillc5bvalue == '1' and self.player_IsSkillCoolTime(5) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(5)
                self.useblehorse = 1
                self.usehorse_delay()
        skillc6bvalue = _winreg.QueryValueEx(self.key, 'skillc6b'+str(self.myclient))[0]
        if skillc6bvalue == '1' and self.player_IsSkillCoolTime(6) == 0:
            if self.player_IsMountingHorse() == '1':
                self.net_SendChatPacket(('/ride'))
            if self.player_IsMountingHorse() == '0':
                self.player_ClickSkillSlot(6)
                self.useblehorse = 1
                self.usehorse_delay()
    def usehorse_delay(self):
        self.usehorse_WaitingDialog = WaitingDialog()
        self.usehorse_WaitingDialog.Open(int(4))
        if self.useblehorse == 1:
            self.usehorse_WaitingDialog.SAFE_SetTimeOverEvent(self.usehorse_fnc)
            self.useblehorse = 0
      
    def usehorse_fnc(self):
        if self.player_IsMountingHorse() == '0':
            self.net_SendChatPacket('/ride')

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