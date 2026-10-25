// main.cpp - Generated v9.2.0
#define AUTO_PTR
#define AUTO_ARGUMENT

#include "globals.h"
#include <cstdlib>

static HMODULE g_hModule=NULL;static HANDLE g_hConsole=NULL;
static FILE*g_fpIn=nullptr,*g_fpOut=nullptr;static bool g_running=true;

std::string ReadLine(const char*p){GConPrint(CON_YELLOW,"%s",p);char b[4096]={};if(fgets(b,4096,stdin)){std::string s(b);while(!s.empty()&&(s.back()=='\n'||s.back()=='\r'))s.pop_back();return s;}return"";}
DWORD ReadDword(const char*p){std::string s=ReadLine(p);if(s.empty())return 0;if(s.size()>=2&&s[0]=='0'&&(s[1]=='x'||s[1]=='X'))return(DWORD)strtoull(s.c_str(),nullptr,16);return(DWORD)strtoul(s.c_str(),nullptr,10);}
int ReadInt(const char*p){std::string s=ReadLine(p);if(s.empty())return-1;return atoi(s.c_str());}

struct FE{int idx;const char*name;const char*full;int argc;bool isPyFake;bool isPyVirt;const char*pyClass;const char*pyFunc;int pyArgCount;};
static const FE g_ft[]={
	{0,"SendAttackPacket","CPythonNetworkStream::SendAttackPacket",2,false,false,"","",0},
	{1,"SendChangeNamePacket","CPythonNetworkStream::SendChangeNamePacket",2,false,false,"","",0},
	{2,"SendCharacterPositionPacket","CPythonNetworkStream::SendCharacterPositionPacket",1,false,false,"","",0},
	{3,"SendCharacterStatePacket","CPythonNetworkStream::SendCharacterStatePacket",4,false,false,"","",0},
	{4,"SendChatPacket","CPythonNetworkStream::SendChatPacket",2,false,false,"","",0},
	{5,"GetSlotItemID","CPythonSafeBox::GetSlotItemID",2,false,false,"","",0},
	{6,"GetStatus","CPythonPlayer::GetStatus",1,false,false,"","",0},
	{7,"playerGetStatus","playerGetStatus (FakePy)",1,true,false,"player","GetStatus",1},
	{8,"playerGetStatus","playerGetStatus (Virtual)",1,false,true,"player","GetStatus",1},
};static const int g_fc=9;

void CallIdx(int i,int m,const DWORD*a,int c){
	if(i<0||i>=g_fc){GConPrint(CON_RED,"Bad idx!\n");return;}
#ifdef AUTO_ARGUMENT
	AutoCallFunction(i,a,c,m);
#else
	if(g_ft[i].isPyFake){
		switch(i){
		case 7:switch(m){case 1:playerGetStatus_py_typedef(a,c);break;case 2:playerGetStatus_py_asm(a,c);break;default:playerGetStatus_py_bytecode(a,c);break;}break;
		}
	}
	else if(g_ft[i].isPyVirt){
		switch(i){
		case 8:{DWORD iType=(c>0)?a[0]:0;switch(m){case 1:playerGetStatus_virtual_typedef(iType);break;case 2:playerGetStatus_virtual_asm(iType);break;default:playerGetStatus_virtual_bytecode(iType);break;}}break;
		}
	}
	else{
		DWORD result=0;switch(i){
		case 0:{DWORD a0=(c>0)?a[0]:0;DWORD a1=(c>1)?a[1]:0;switch(m){case 1:result=CPythonNetworkStreamSendAttackPacket_call_typedef(a0,a1);break;case 2:result=CPythonNetworkStreamSendAttackPacket_call_asm(a0,a1);break;default:result=CPythonNetworkStreamSendAttackPacket_call_bytecode(a0,a1);break;}}break;
		case 1:{DWORD a0=(c>0)?a[0]:0;DWORD a1=(c>1)?a[1]:0;switch(m){case 1:result=CPythonNetworkStreamSendChangeNamePacket_call_typedef(a0,a1);break;case 2:result=CPythonNetworkStreamSendChangeNamePacket_call_asm(a0,a1);break;default:result=CPythonNetworkStreamSendChangeNamePacket_call_bytecode(a0,a1);break;}}break;
		case 2:{DWORD a0=(c>0)?a[0]:0;switch(m){case 1:result=CPythonNetworkStreamSendCharacterPositionPacket_call_typedef(a0);break;case 2:result=CPythonNetworkStreamSendCharacterPositionPacket_call_asm(a0);break;default:result=CPythonNetworkStreamSendCharacterPositionPacket_call_bytecode(a0);break;}}break;
		case 3:{DWORD a0=(c>0)?a[0]:0;DWORD a1=(c>1)?a[1]:0;DWORD a2=(c>2)?a[2]:0;DWORD a3=(c>3)?a[3]:0;switch(m){case 1:result=CPythonNetworkStreamSendCharacterStatePacket_call_typedef(a0,a1,a2,a3);break;case 2:result=CPythonNetworkStreamSendCharacterStatePacket_call_asm(a0,a1,a2,a3);break;default:result=CPythonNetworkStreamSendCharacterStatePacket_call_bytecode(a0,a1,a2,a3);break;}}break;
		case 4:{DWORD a0=(c>0)?a[0]:0;DWORD a1=(c>1)?a[1]:0;switch(m){case 1:result=CPythonNetworkStreamSendChatPacket_call_typedef(a0,a1);break;case 2:result=CPythonNetworkStreamSendChatPacket_call_asm(a0,a1);break;default:result=CPythonNetworkStreamSendChatPacket_call_bytecode(a0,a1);break;}}break;
		case 5:{DWORD a0=(c>0)?a[0]:0;DWORD a1=(c>1)?a[1]:0;switch(m){case 1:result=CPythonSafeBoxGetSlotItemID_call_typedef(a0,a1);break;case 2:result=CPythonSafeBoxGetSlotItemID_call_asm(a0,a1);break;default:result=CPythonSafeBoxGetSlotItemID_call_bytecode(a0,a1);break;}}break;
		case 6:{DWORD a0=(c>0)?a[0]:0;switch(m){case 1:result=CPythonPlayerGetStatus_call_typedef(a0);break;case 2:result=CPythonPlayerGetStatus_call_asm(a0);break;default:result=CPythonPlayerGetStatus_call_bytecode(a0);break;}}break;
		}
	}
#endif
}

int FindName(const char*n){for(int i=0;i<g_fc;++i)if(_stricmp(g_ft[i].name,n)==0||_stricmp(g_ft[i].full,n)==0||_stricmp(g_ft[i].pyFunc,n)==0)return i;return-1;}

void Menu(){
	GConPrint(CON_BWHITE,"\n=== Generated DLL v9.2.0 ===\n");
#ifdef AUTO_ARGUMENT
	GConPrint(CON_CYAN,"[AUTO_ARGUMENT]\n");
#endif
#ifdef AUTO_PTR
	GConPrint(CON_CYAN,"[AUTO_PTR] %d funcs, %d singletons\n",(int)GenCache::g_functions.size(),(int)GenCache::g_singletons.size());
#endif
	GConPrint(CON_WHITE,"\nFunctions:\n");
	for(int i=0;i<g_fc;++i){
		if(g_ft[i].isPyFake)GConPrint(CON_MAGENTA,"  [%d] [PY-FAKE] %s::%s (tuple args=%d)",i,g_ft[i].pyClass,g_ft[i].pyFunc,g_ft[i].pyArgCount);
		else if(g_ft[i].isPyVirt)GConPrint(CON_CYAN,"  [%d] [PY-VIRT] %s::%s (no tuple, args=%d)",i,g_ft[i].pyClass,g_ft[i].pyFunc,g_ft[i].pyArgCount);
		else GConPrint(CON_GREEN,"  [%d] %s (%d args)",i,g_ft[i].full,g_ft[i].argc);
#ifdef AUTO_ARGUMENT
		if(g_resolvedValid[i])GConPrint(CON_CYAN," [%d detected]",g_detectedArgs[i]);
#endif
		GConPrint(CON_WHITE,"\n");}
	GConPrint(CON_WHITE,"\nCommands:\n");
	GConPrint(CON_WHITE,"  call <i> <m> [args]\n  calln <name> <m> [args]\n  i (interactive)\n");
	GConPrint(CON_WHITE,"  setmethod <i> <0-2> | pyrefresh | resetsingleton <i> | listsingletons | exit\n");
}

void Proc(const std::string&cmd){
	if(cmd.empty())return;
	std::vector<std::string>t;std::string tk;for(size_t i=0;i<=cmd.size();++i){if(i==cmd.size()||cmd[i]==' '||cmd[i]=='\t'){if(!tk.empty()){t.push_back(tk);tk.clear();}}else tk+=cmd[i];}if(t.empty())return;
	if(t[0]=="exit"||t[0]=="quit"){g_running=false;return;}
	if(t[0]=="list"){Menu();return;}
	if(t[0]=="pyrefresh"){FindPyTypes();return;}
	if(t[0]=="call"&&t.size()>=3){int fi=atoi(t[1].c_str()),mt=atoi(t[2].c_str());DWORD a[16]={};int ac=0;for(size_t i=3;i<t.size()&&ac<16;++i){const char*s=t[i].c_str();a[ac++]=(s[0]=='0'&&(s[1]=='x'||s[1]=='X'))?(DWORD)strtoull(s,nullptr,16):(DWORD)strtoul(s,nullptr,10);}CallIdx(fi,mt,a,ac);return;}
	if(t[0]=="calln"&&t.size()>=3){int fi=FindName(t[1].c_str()),mt=atoi(t[2].c_str());DWORD a[16]={};int ac=0;for(size_t i=3;i<t.size()&&ac<16;++i){const char*s=t[i].c_str();a[ac++]=(s[0]=='0'&&(s[1]=='x'||s[1]=='X'))?(DWORD)strtoull(s,nullptr,16):(DWORD)strtoul(s,nullptr,10);}if(fi>=0)CallIdx(fi,mt,a,ac);else{
#ifdef AUTO_ARGUMENT
		AutoCallByName(t[1].c_str(),a,ac,mt);
#else
		GConPrint(CON_RED,"Not found!\n");
#endif
	}return;}
	if(t[0]=="i"){Menu();int fi=ReadInt("Func: ");if(fi<0||fi>=g_fc)return;int mt=ReadInt("Method[1-3]: ");if(mt<1||mt>3)mt=2;
		if(g_ft[fi].isPyFake||g_ft[fi].isPyVirt){
			int pac=g_ft[fi].pyArgCount;
#ifdef AUTO_ARGUMENT
			if(g_resolvedValid[fi]&&g_detectedArgs[fi]>0)pac=g_detectedArgs[fi];
#endif
			if(g_ft[fi].isPyVirt)GConPrint(CON_CYAN,"Python Virtual: enter %d arg(s):\n",pac);
			else GConPrint(CON_YELLOW,"Python FakeTuple: enter %d tuple arg(s):\n",pac);
			DWORD a[16]={};for(int k=0;k<pac;++k){char pr[64];sprintf_s(pr,"  arg%d: ",k);a[k]=ReadDword(pr);}CallIdx(fi,mt,a,pac);
		}else{
			int ac=g_ft[fi].argc;
#ifdef AUTO_ARGUMENT
			if(g_resolvedValid[fi]&&g_detectedArgs[fi]>ac)ac=g_detectedArgs[fi];
#endif
			GConPrint(CON_YELLOW,"Enter %d args:\n",ac);DWORD a[16]={};for(int k=0;k<ac;++k){char pr[64];sprintf_s(pr,"  arg%d: ",k);a[k]=ReadDword(pr);}CallIdx(fi,mt,a,ac);
		}return;}
#ifdef AUTO_ARGUMENT
	if(t[0]=="setmethod"&&t.size()>=3){SetAutoArgMethod(atoi(t[1].c_str()),atoi(t[2].c_str()));return;}
	if(t[0]=="resolve"&&t.size()>=2){int i=atoi(t[1].c_str());g_resolvedValid[i]=false;AutoResolveFunction(i);return;}
	if(t[0]=="resolveall"){for(int i=0;i<g_autoCount;++i)g_resolvedValid[i]=false;InitAutoResolveAll();return;}
	if(t[0]=="resetsingleton"&&t.size()>=2){int i=atoi(t[1].c_str());if(i>=0&&i<g_autoCount){g_pyVirtWorkingSingleton[i]=0;g_pyVirtCandidatesBuilt[i]=false;g_pyVirtCandidates[i].clear();GConPrint(CON_CYAN,"[%d] working singleton cache reset\n",i);}return;}
	if(t[0]=="listsingletons"){for(int i=0;i<g_autoCount;++i){if(g_autoTable[i].isPythonVirtual){GConPrint(CON_CYAN,"[%d] %s: %d candidates, working=0x%08X\n",i,g_autoTable[i].fid,(int)g_pyVirtCandidates[i].size(),g_pyVirtWorkingSingleton[i]);}}return;}
#endif
	GConPrint(CON_RED,"Unknown: %s\n",t[0].c_str());
}

DWORD WINAPI MainThread(LPVOID){
	AllocConsole();SetConsoleTitleA("Generated v9.2.0");
	freopen_s(&g_fpIn,"CONIN$","r",stdin);freopen_s(&g_fpOut,"CONOUT$","w",stdout);freopen_s(&g_fpOut,"CONOUT$","w",stderr);
	g_hConsole=GetStdHandle(STD_OUTPUT_HANDLE);
	GConPrint(CON_GREEN,"=== Injected PID:%d ===\n",GetCurrentProcessId());
	InitAll(g_hConsole);GConPrint(CON_GREEN,"Base:0x%08X Funcs:%d\n",hEntryBaseAddress,g_fc);
	Menu();while(g_running){std::string c=ReadLine("> ");Proc(c);}
	if(g_fpIn)fclose(g_fpIn);if(g_fpOut)fclose(g_fpOut);FreeConsole();
	FreeLibraryAndExitThread(g_hModule,0);return 0;
}

BOOL APIENTRY DllMain(HMODULE h,DWORD r,LPVOID){
	switch(r){case DLL_PROCESS_ATTACH:g_hModule=h;DisableThreadLibraryCalls(h);CreateThread(NULL,0,MainThread,NULL,0,NULL);break;case DLL_PROCESS_DETACH:g_running=false;break;}
	return TRUE;
}
