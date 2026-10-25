import net,chat
RetnDic={}
Kuerzel={"ghost":"import chr;chr.Revive()",
         "restart":"import net;net.SendChatPacket(\"/restart_here\")"}
def netSendChatPacket(text, type=0):
	if text[0:2] == "/$" :
		Command=str(text[2:-1]+text[-1])
		if Command in Kuerzel:
			Command = Kuerzel[Command]
		CommandList = Command.split(";")
		ToExe=""
		for i in CommandList:
			ToExe+=str(i)+"\n"
		try:
			global RetnDic
			exec ToExe in RetnDic
			try:
				chat.AppendChat(3,"Return: "+str(RetnDic[Command.split("=")[0]]))
			except:
				#chat.AppendChat(2,"\""+Command+"\"exeuted !")
				pass
		except:
			chat.AppendChat(2,"Error while executing \""+Command+"\"")
		return
	Copy[0](text,type)
Copy=[None]
if net.SendChatPacket!=netSendChatPacket:
	Copy[0]=net.SendChatPacket
net.SendChatPacket=netSendChatPacket