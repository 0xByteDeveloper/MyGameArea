import app
import chat
import chr
import locale
import net
import os
import pack
import player
import snd
import time
import ui
import uiCommon
import uiTip
import skill
import item
import shop
import grp
import wndMgr

HALF_WHITE_COLOR = grp.GenerateColor(1.0, 1.0, 1.0, 0.2)
SELECT_COLOR = grp.GenerateColor(0.0, 0.0, 0.5, 0.3)

Error = ""
Errortype = "none"
Dialog = 0

class ScriptStealerDialog(ui.ThinBoard):
	
	def __init__(self):
		ui.ThinBoard.__init__(self)
		self.__Load_FileExtractor()
		
	def __del__(self):
		ui.ThinBoard.__del__(self)

	def Destroy(self):
		self.Hide()
		return TRUE	
		
	def __CreateFileListBox(self):
		fileListBox = ui.ListBoxEx()
		fileListBox.SetParent(self)
		fileListBox.SetPosition(25, 57)
		fileListBox.SetViewItemCount(8)
		fileListBox.SetItemSize(160, 16)
		fileListBox.Show()
		return fileListBox
		
	def __Load_FileExtractor(self):
		self.fileListBox = self.__CreateFileListBox()
		
		self.ScrollBar = ui.ScrollBar()
		self.ScrollBar.SetParent(self)
		self.ScrollBar.SetPosition(183, 47)
		self.ScrollBar.SetScrollBarSize(170)
		self.ScrollBar.Show()
		self.fileListBox.SetScrollBar(self.ScrollBar)
	
		self.SetPosition(5, 350)
		self.SetSize(293, 283 + 65)
		self.Show()
		self.AddFlag("movable")
		snd.PlaySound("sound/ui/type.wav")

		self.titel = ui.TextLine()
		self.titel.SetParent(self)
		self.titel.SetDefaultFontName()
		self.titel.SetPosition(95, 10)
		self.titel.SetFeather()
		self.titel.SetText("Metin2 File Extractor")
		self.titel.SetFontColor(0.1, 0.7, 1)
		self.titel.SetOutline()
		self.titel.Show()

		self.notice = ui.TextLine()
		self.notice.SetParent(self)
		self.notice.SetDefaultFontName()
		self.notice.SetPosition(20, 30)
		self.notice.SetFeather()
		self.notice.SetText("Folgende Dateien werden entpackt:")
		self.notice.SetFontColor(0.6, 0.7, 1)
		self.notice.SetOutline()
		self.notice.SetTop()
		self.notice.Show()

		self.CloseButton = ui.Button()
		self.CloseButton.SetParent(self)
		self.CloseButton.SetPosition(253, 13)
		self.CloseButton.SetUpVisual("d:/ymir work/ui/public/close_button_01.sub")
		self.CloseButton.SetOverVisual("d:/ymir work/ui/public/close_button_02.sub")
		self.CloseButton.SetDownVisual("d:/ymir work/ui/public/close_button_03.sub")
		self.CloseButton.SetToolTipText(locale.UI_CLOSE, 0, - 23)
		self.CloseButton.SetEvent(ui.__mem_func__(self.Close))
		self.CloseButton.Show()

		self.extractbutton = ui.Button()
		self.extractbutton.SetParent(self)
		self.extractbutton.SetUpVisual("d:/ymir work/ui/public/xlarge_button_01.sub")
		self.extractbutton.SetOverVisual("d:/ymir work/ui/public/xlarge_button_02.sub")
		self.extractbutton.SetDownVisual("d:/ymir work/ui/public/xlarge_button_03.sub")
		self.extractbutton.SetText("Extract!")
		self.extractbutton.SetPosition(20, 223 + 65)
		self.extractbutton.SetEvent(ui.__mem_func__(self.OnClickExtract))
		self.extractbutton.Show()

		self.UpdateButton = ui.Button()
		self.UpdateButton.SetParent(self)
		self.UpdateButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.UpdateButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.UpdateButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.UpdateButton.SetText("File Update")
		self.UpdateButton.SetPosition(210, 225 + 65)
		self.UpdateButton.SetEvent(ui.__mem_func__(self.namelinemodule))
		self.UpdateButton.Show()

		self.NewFileButton = ui.Button()
		self.NewFileButton.SetParent(self)
		self.NewFileButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.NewFileButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.NewFileButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.NewFileButton.SetText("New File")
		self.NewFileButton.SetPosition(210, 55)
		self.NewFileButton.SetEvent(ui.__mem_func__(self.WriteNewFile))
		self.NewFileButton.Show()

		self.AddFileButton = ui.Button()
		self.AddFileButton.SetParent(self)
		self.AddFileButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.AddFileButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.AddFileButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.AddFileButton.SetText("Add File")
		self.AddFileButton.SetPosition(210, 85)
		self.AddFileButton.SetEvent(ui.__mem_func__(self.AddFile))
		self.AddFileButton.Show()

		self.ChangeFileButton = ui.Button()
		self.ChangeFileButton.SetParent(self)
		self.ChangeFileButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.ChangeFileButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.ChangeFileButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.ChangeFileButton.SetText("Change File")
		self.ChangeFileButton.SetPosition(210, 115)
		self.ChangeFileButton.SetEvent(ui.__mem_func__(self.ReplaceExistingFile))
		self.ChangeFileButton.Show()

		self.DeleteFileButton = ui.Button()
		self.DeleteFileButton.SetParent(self)
		self.DeleteFileButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.DeleteFileButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.DeleteFileButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.DeleteFileButton.SetText("Delete File")
		self.DeleteFileButton.SetPosition(210, 145)
		self.DeleteFileButton.SetEvent(ui.__mem_func__(self.DeleteExistingFile))
		self.DeleteFileButton.Show()

		self.ReplaceFileButton = ui.Button()
		self.ReplaceFileButton.SetParent(self)
		self.ReplaceFileButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.ReplaceFileButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.ReplaceFileButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.ReplaceFileButton.SetText("Replace File")
		self.ReplaceFileButton.SetPosition(210, 175)
		self.ReplaceFileButton.SetEvent(ui.__mem_func__(self.ReplaceFile))
		self.ReplaceFileButton.Show()

		self.OpenListButton = ui.Button()
		self.OpenListButton.SetParent(self)
		self.OpenListButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.OpenListButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.OpenListButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.OpenListButton.SetText("Open")
		self.OpenListButton.SetPosition(210, 215)
		self.OpenListButton.SetEvent(ui.__mem_func__(self.OpenList))
		self.OpenListButton.Show()

		self.NewTestButton = ui.Button()
		self.NewTestButton.SetParent(self)
		self.NewTestButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.NewTestButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.NewTestButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.NewTestButton.SetText("Xml Unpack")
		self.NewTestButton.SetPosition(210, 245)
		self.NewTestButton.SetEvent(ui.__mem_func__(self.XMLUnPack))
		self.NewTestButton.Show()
		
		self.copyright = ui.TextLine()
		self.copyright.SetParent(self)
		self.copyright.SetDefaultFontName()
		self.copyright.SetPosition(125, 255 + 65)
		self.copyright.SetFeather()
		self.copyright.SetText("v2.4 © Tyrson/RealFreak/Crank")
		self.copyright.SetFontColor(1.0, 0.5, 0.5)
		self.copyright.SetOutline()
		self.copyright.Show()

		self.Log = ui.TextLine()
		self.Log.SetParent(self)
		self.Log.SetDefaultFontName()
		self.Log.SetPosition(20, 220)
		self.Log.SetFeather()
		self.Log.SetText("File Extractor Log:")
		self.Log.SetFontColor(0.6, 0.7, 1)
		self.Log.SetOutline()
		self.Log.Show()

		self.LogTextLine1 = ui.TextLine()
		self.LogTextLine1.SetParent(self)
		self.LogTextLine1.SetDefaultFontName()
		self.LogTextLine1.SetPosition(23, 235)
		self.LogTextLine1.SetFeather()
		self.LogTextLine1.SetText("-")
		self.LogTextLine1.SetOutline()
		self.LogTextLine1.Show()
		
		self.LogTextLine2 = ui.TextLine()
		self.LogTextLine2.SetParent(self)
		self.LogTextLine2.SetDefaultFontName()
		self.LogTextLine2.SetPosition(23, 250)
		self.LogTextLine2.SetFeather()
		self.LogTextLine2.SetText("")
		self.LogTextLine2.SetOutline()
		self.LogTextLine2.Show()

		self.LogTextLine3 = ui.TextLine()
		self.LogTextLine3.SetParent(self)
		self.LogTextLine3.SetDefaultFontName()
		self.LogTextLine3.SetPosition(23, 265)
		self.LogTextLine3.SetFeather()
		self.LogTextLine3.SetText("")
		self.LogTextLine3.SetOutline()
		self.LogTextLine3.Show()
		
		self.namelinemodule()
	
	def XMLUnPack(self):
		global Dialog
		self.FilenameDialog = XMLUnPackDialog()
		self.FilenameDialog.SetAcceptEvent(lambda arg=TRUE: self.NewFile(arg, "add"))
		self.FilenameDialog.SetCancelEvent(lambda arg=FALSE: self.NewFile(arg, ""))
		self.FilenameDialog.SetTitle("Add XML")
		self.FilenameDialog.Show()	
		Dialog = 1
		
	def OpenList(self):
		os.system("notepad exlist.txt")
	
	def ReplaceFile(self):
		global Dialog
		self.FilenameDialog = ReplaceDialog()
		self.FilenameDialog.SetAcceptEvent(lambda arg=TRUE: self.NewFile(arg, "replace"))
		self.FilenameDialog.SetCancelEvent(lambda arg=FALSE: self.NewFile(arg, ""))
		self.FilenameDialog.SetTitle("Replace File")
		self.FilenameDialog.Show()	
		Dialog = 1
			
	def DeleteExistingFile(self):
		DeleteContent = self.fileListBox.GetSelectedItem()
		DeleteText = DeleteContent.GetText()
		if str(DeleteText) == "":
			return
		else:
			file = open("exlist.txt", "r+")
			FileString = file.read()
			NewFiles = str(FileString).replace(str(DeleteText + ",\n"), str(""))
			file.close()
			f = open("exlist.txt", "w+")
			f.write(NewFiles)
			f.close()
			self.namelinemodule()
	
	def ReplaceExistingFile(self):
		global Dialog
		Replace = self.fileListBox.GetSelectedItem()
		Replace = Replace.GetText()
		if str(Replace) == "":
			return
		else:
			FilenameDialog = uiCommon.InputDialog()
			FilenameDialog.SetAcceptEvent(lambda arg=TRUE: self.NewFile(arg, "special"))
			FilenameDialog.SetCancelEvent(lambda arg=FALSE: self.NewFile(arg, ""))
			FilenameDialog.SetTitle("Change File")
			FilenameDialog.SetMaxLength(64)
			FilenameDialog.Open()	
			Dialog = 1
			self.FilenameDialog = FilenameDialog
	
	def AddFile(self):
		global Dialog
		FilenameDialog = uiCommon.InputDialog()
		FilenameDialog.SetAcceptEvent(lambda arg=TRUE: self.NewFile(arg, "a+"))
		FilenameDialog.SetCancelEvent(lambda arg=FALSE: self.NewFile(arg, ""))
		FilenameDialog.SetTitle("Add new Files")
		FilenameDialog.SetMaxLength(64)
		FilenameDialog.Open()
		Dialog = 1
		self.FilenameDialog = FilenameDialog
	
	def WriteNewFile(self):
		global Dialog
		FilenameDialog = uiCommon.InputDialog()
		FilenameDialog.SetAcceptEvent(lambda arg=TRUE: self.NewFile(arg, "w+"))
		FilenameDialog.SetCancelEvent(lambda arg=FALSE: self.NewFile(arg, ""))
		FilenameDialog.SetTitle("Extract new Files")
		FilenameDialog.SetMaxLength(64)
		FilenameDialog.Open()
		Dialog = 1
		self.FilenameDialog = FilenameDialog
		
	def NewFile(self, answer, type):
		global Dialog
		Dialog = 0
		
		if not self.FilenameDialog:
			return
			
		if str(type) == "special":
			Replace = self.fileListBox.GetSelectedItem()
			Replace = Replace.GetText()
			self.ReplaceExtraction(str(Replace), str(str(self.FilenameDialog.GetText())))
			
		if str(type) == "replace":
			String = str(self.FilenameDialog.GetText()).split("%&/")
			ReplaceExisting = str(String[0])
			ReplaceText = str(String[1])
			self.ReplaceExtraction(str(ReplaceExisting), str(ReplaceText))
			
		if str(type) == "add":
			if os.path.exists(self.FilenameDialog.GetText()):
				file = open(self.FilenameDialog.GetText(), "r+")
				FileString = file.read()
				FileString = str(FileString).replace("<File archivedPath=\"", "!§$%&")
				NewFiles = str(FileString).replace("\" type=", "!§$%&")
				TestFiles = NewFiles.split("!§$%&")
				file.close()
				f = open("exlist.txt", "a+")
				i = 1
				for z in xrange(int(NewFiles.count("!§$%&") / 2)):
					f.write(str(TestFiles[i] + ",\n"))
					i += 2
				f.close()
			else:
				self.LogTextLine1.SetText("Xml existiert nicht!")
				return
			
		if answer and str(type) != "special" and str(type) != "replace" and str(type) != "add":
			newfilename = self.FilenameDialog.GetText()
			f = open("exlist.txt", type)
			f.write(newfilename + ",\n")
			f.close()
		self.FilenameDialog.Close()
		self.FilenameDialog = None
		self.namelinemodule()
		
	def ReplaceExtraction(self, ReplaceExisting, ReplaceText):
		file = open("exlist.txt", "r+")
		file_lines = file.read()
		NewFiles = str(file_lines).replace(str(ReplaceExisting), str(ReplaceText))
		file.close()
		f = open("exlist.txt", "w+")
		f.write(NewFiles)
		f.close()	
	
	def namelinemodule(self):
		if not os.path.exists("exlist.txt"):
			create_exlist = open("exlist.txt", "w")
			create_exlist.write("game.py,\n")
			create_exlist.close()
		self.fileListBox.RemoveAllItems()
		file = open("exlist.txt", "r+")
		file_lines = file.read()
		Test = str(file_lines).replace("\n", "")
		Scripts = str(Test).split(",")
		for Testies in xrange(int(str(file_lines).count(","))):
			self.fileListBox.AppendItem(ExtractList(Scripts[Testies]))
			
	def OnClickExtract(self):
		global Error
		global Errortype
		Error = ""
		Errortype = "none"
		file = open("exlist.txt", "r+")
		FileToExtract = file.read()
		
		FilesCount = str(FileToExtract).count("\n")
		if str(FileToExtract).find(",") != -1:
			FileToExtract = str(FileToExtract).replace(",", "")
		FileToExtractSplit = str(FileToExtract).split("\n")
		for i in xrange(0, int(FilesCount)):
			if str(Error) == "":
				ActualScript = FileToExtractSplit[i]
				self.ExtractScript(str(ActualScript))
			else:
				break
		if str(Errortype) == "exist":
			self.LogTextLine1.SetText("Die Datei:")
			self.LogTextLine2.SetText(str(Error))
			self.LogTextLine3.SetText("existiert nicht!")
		elif str(Errortype) == "read":
			self.LogTextLine1.SetText("Die Datei: ")
			self.LogTextLine2.SetText(str(Error))
			self.LogTextLine3.SetText("konnte nicht ausgelesen werden!")
		elif str(Errortype) == "none":
			self.LogTextLine1.SetText("Die Dateien wurden erfolgreich ausgelesen!")
			self.LogTextLine2.SetText("")
			self.LogTextLine3.SetText("")
		elif str(Errortype) == "ending":
			self.LogTextLine1.SetText("Die Datei:")
			self.LogTextLine2.SetText(str(Error))
			self.LogTextLine3.SetText("hat keine Dateiendung!")			

	def ExtractScript(self, script):
		global Error
		global Errortype
		Error = ""
		Errortype = "none"
		add = ""
		if str(script).find("d:/") != -1:
			script = str(script).replace("d:/", "")
			add = "d:/"
		if pack.Exist(add + script):
			if not os.path.exists("source/" + script):
				os.makedirs("source/" + script)
			if os.path.exists("source/" + script):
				if os.path.isfile("source/" + script):
					os.remove("source/" + script)
				else:
					os.rmdir("source/" + script)
			if self.IsBinary(script) == 0:
				lines = pack_open(add + script, "r").readlines()
				f = open("source/" + script, "a+")		
				for line in lines:
					tokens = line
					f.write(str(tokens))		
				f.close()
			else:
#				Binary = pack.Get(script)
				Binary = pack_open(add + script, 'rb')
				Bytes = Binary.read()
				if len(Bytes) == 0:
					if Errortype != "ending":
						Error = str(add + script)
						Errortype = "read"
					return
				else:
					f = open("source/" + script, "wb")		
					f.write(str(Bytes))		
					f.close()
		else:
			Error = str(add + script)
			Errortype = "exist"
			return

	def IsBinary(self, script):
		global Error
		global Errortype
		if str(script).count(".") == 0:
			Error = str(script)
			Errortype = "ending"
			script = script + ".binary"
		Split = script.split(".")
		end = str(Split[1])
		end = end.lower()
		
		if end == ".py": 
			return 0 
		else:
			return 1
			
	def Show(self):
		ui.ThinBoard.Show(self)
		
	def Close(self):
		global Dialog
		if Dialog >= 1:
			self.FilenameDialog.Close()
		self.Hide()
		return TRUE
		
	def OnPressEscapeKey(self):
		global Dialog
		if int(Dialog) >= 1:
			self.FilenameDialog.Close()
		self.Hide()
		return TRUE

class ReplaceDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(293, 180)
		self.Board.SetPosition(wndMgr.GetScreenWidth() / 2 - 293, wndMgr.GetScreenHeight() / 2 - 180)
		self.Board.AddFlag("movable")
		self.Board.SetTitleName("Replace Files")
		self.Board.Show()
		
		self.ReplaceExisting = ui.TextLine()
		self.ReplaceExisting.SetParent(self.Board)
		self.ReplaceExisting.SetDefaultFontName()
		self.ReplaceExisting.SetPosition(20, 40)
		self.ReplaceExisting.SetFeather()
		self.ReplaceExisting.SetText("Existing Text:")
		self.ReplaceExisting.SetFontColor(0.6, 0.7, 1)
		self.ReplaceExisting.SetOutline()
		self.ReplaceExisting.Show()
	
		self.ReplaceExistingSlotBar = ui.SlotBar()
		self.ReplaceExistingSlotBar.SetParent(self.Board)
		self.ReplaceExistingSlotBar.SetSize(250, 18)
		self.ReplaceExistingSlotBar.SetPosition(0, 60)
		self.ReplaceExistingSlotBar.SetWindowHorizontalAlignCenter()
		self.ReplaceExistingSlotBar.Show()
		
		self.ReplaceExistingEditLine = ui.EditLine()
		self.ReplaceExistingEditLine.SetParent(self.ReplaceExistingSlotBar)
		self.ReplaceExistingEditLine.SetSize(250, 17)
		self.ReplaceExistingEditLine.SetPosition(10, 2)
		self.ReplaceExistingEditLine.SetMax(64)
		self.ReplaceExistingEditLine.SetFocus()
		self.ReplaceExistingEditLine.Show()
		
		self.ReplaceText = ui.TextLine()
		self.ReplaceText.SetParent(self.Board)
		self.ReplaceText.SetDefaultFontName()
		self.ReplaceText.SetPosition(20, 85)
		self.ReplaceText.SetFeather()
		self.ReplaceText.SetText("New Text:")
		self.ReplaceText.SetFontColor(0.6, 0.7, 1)
		self.ReplaceText.SetOutline()
		self.ReplaceText.Show()
	
		self.ReplaceSlotBar = ui.SlotBar()
		self.ReplaceSlotBar.SetParent(self.Board)
		self.ReplaceSlotBar.SetSize(250, 18)
		self.ReplaceSlotBar.SetPosition(0, 105)
		self.ReplaceSlotBar.SetWindowHorizontalAlignCenter()
		self.ReplaceSlotBar.Show()
		
		self.ReplaceEditLine = ui.EditLine()
		self.ReplaceEditLine.SetParent(self.ReplaceSlotBar)
		self.ReplaceEditLine.SetSize(250, 17)
		self.ReplaceEditLine.SetPosition(10, 2)
		self.ReplaceEditLine.SetMax(64)
		self.ReplaceEditLine.Show()

		self.ReplaceEditLine.SetTabEvent(ui.__mem_func__(self.ReplaceExistingEditLine.SetFocus))
		self.ReplaceEditLine.SetReturnEvent(ui.__mem_func__(self.ReplaceExistingEditLine.SetFocus))
		self.ReplaceExistingEditLine.SetTabEvent(ui.__mem_func__(self.ReplaceEditLine.SetFocus))
		self.ReplaceExistingEditLine.SetReturnEvent(ui.__mem_func__(self.ReplaceEditLine.SetFocus))

		self.ClickReplaceButton = ui.Button()
		self.ClickReplaceButton.SetParent(self.Board)
		self.ClickReplaceButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.ClickReplaceButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.ClickReplaceButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.ClickReplaceButton.SetText("Suchen & Ersetzen")
		self.ClickReplaceButton.SetPosition(50, 137)
		self.ClickReplaceButton.Show()

		self.ClickBreakButton = ui.Button()
		self.ClickBreakButton.SetParent(self.Board)
		self.ClickBreakButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.ClickBreakButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.ClickBreakButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.ClickBreakButton.SetText("Abbrechen")
		self.ClickBreakButton.SetPosition(150, 137)
		self.ClickBreakButton.Show()

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.ClearDictionary()
		self.Board = None
		self.ClickReplaceButton = None
		self.ClickBreakButton = None
		self.ReplaceExistingSlotBar = None
		self.ReplaceExistingEditLine = None
		self.ReplaceSlotBar = None
		self.ReplaceEditLine = None
		self.Hide()

	def SetTitle(self, name):
		self.Board.SetTitleName(name)

	def SetNumberMode(self):
		self.ReplaceExistingEditLine.SetNumberMode()
		self.ReplaceEditLine.SetNumberMode()

	def SetSecretMode(self):
		self.ReplaceExistingEditLine.SetSecret()
		self.ReplaceEditLine.SetSecret()

	def SetFocus(self):
		self.ReplaceExistingEditLine.SetFocus()

	def SetMaxLength(self, length):
		width = length * 6 + 10
		self.ReplaceExistingEditLine.SetMax(length)
		self.ReplaceEditLine.SetMax(length)
		self.SetSlotWidth(width)
		self.SetBoardWidth(max(width + 50, 160))

	def SetSlotWidth(self, width):
		self.ReplaceExistingSlotBar.SetSize(width, self.ReplaceExistingSlotBar.GetHeight())
		self.ReplaceSlotBar.SetSize(width, self.ReplaceSlotBar.GetHeight())
		self.ReplaceExistingEditLine.SetSize(width, self.ReplaceExistingEditLine.GetHeight())
		self.ReplaceEditLine.SetSize(width, self.ReplaceEditLine.GetHeight())

	def SetBoardWidth(self, width):
		self.Board.SetSize(max(width + 50, 160), self.GetHeight())
		self.SetSize(max(width + 50, 160), self.GetHeight())
		self.UpdateRect()

	def SetAcceptEvent(self, event):
		self.ClickReplaceButton.SetEvent(event)
		self.ReplaceExistingEditLine.OnIMEReturn = event
		self.ReplaceEditLine.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.Board.SetCloseEvent(event)
		self.ClickBreakButton.SetEvent(event)
		self.ReplaceExistingEditLine.OnPressEscapeKey = event
		self.ReplaceEditLine.OnPressEscapeKey = event

	def GetText(self):
		return self.ReplaceExistingEditLine.GetText() + "%&/" + self.ReplaceEditLine.GetText()

class XMLUnPackDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)

		self.__CreateDialog()

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def __CreateDialog(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(293, 120)
		self.Board.SetPosition(wndMgr.GetScreenWidth() / 2 - 293, wndMgr.GetScreenHeight() / 2 - 120)
		self.Board.AddFlag("movable")
		self.Board.AddFlag("float")
		self.Board.SetTitleName("Add Xml Files")
		self.Board.Show()
		
		self.XmlFileNameText = ui.TextLine()
		self.XmlFileNameText.SetParent(self.Board)
		self.XmlFileNameText.SetDefaultFontName()
		self.XmlFileNameText.SetPosition(20, 40)
		self.XmlFileNameText.SetFeather()
		self.XmlFileNameText.SetText("Xml Filename:")
		self.XmlFileNameText.SetFontColor(0.6, 0.7, 1)
		self.XmlFileNameText.SetOutline()
		self.XmlFileNameText.Show()
	
		self.XmlFileSlotBar = ui.SlotBar()
		self.XmlFileSlotBar.SetParent(self.Board)
		self.XmlFileSlotBar.SetSize(250, 18)
		self.XmlFileSlotBar.SetPosition(0, 60)
		self.XmlFileSlotBar.SetWindowHorizontalAlignCenter()
		self.XmlFileSlotBar.Show()
		
		self.XmlFileEditLine = ui.EditLine()
		self.XmlFileEditLine.SetParent(self.XmlFileSlotBar)
		self.XmlFileEditLine.SetSize(250, 17)
		self.XmlFileEditLine.SetPosition(10, 2)
		self.XmlFileEditLine.SetMax(64)
		self.XmlFileEditLine.SetFocus()
		self.XmlFileEditLine.Show()

		self.AddXMLButton = ui.Button()
		self.AddXMLButton.SetParent(self.Board)
		self.AddXMLButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.AddXMLButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.AddXMLButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.AddXMLButton.SetText("Add Xml")
		self.AddXMLButton.SetPosition(50, 87)
		self.AddXMLButton.Show()

		self.ClickBreakButton = ui.Button()
		self.ClickBreakButton.SetParent(self.Board)
		self.ClickBreakButton.SetUpVisual("d:/ymir work/ui/public/large_button_01.sub")
		self.ClickBreakButton.SetOverVisual("d:/ymir work/ui/public/large_button_02.sub")
		self.ClickBreakButton.SetDownVisual("d:/ymir work/ui/public/large_button_03.sub")
		self.ClickBreakButton.SetText("Abbrechen")
		self.ClickBreakButton.SetPosition(150, 87)
		self.ClickBreakButton.Show()

	def Open(self):
		self.SetCenterPosition()
		self.SetTop()
		self.Show()

	def Close(self):
		self.ClearDictionary()
		self.Board = None
		self.AddXMLButton = None
		self.ClickBreakButton = None
		self.XmlFileSlotBar = None
		self.XmlFileEditLine = None
		self.Hide()

	def SetTitle(self, name):
		self.Board.SetTitleName(name)

	def SetNumberMode(self):
		self.XmlFileEditLine.SetNumberMode()

	def SetSecretMode(self):
		self.XmlFileEditLine.SetSecret()

	def SetFocus(self):
		self.XmlFileEditLine.SetFocus()

	def SetMaxLength(self, length):
		width = length * 6 + 10
		self.XmlFileEditLine.SetMax(length)
		self.SetSlotWidth(width)
		self.SetBoardWidth(max(width + 50, 160))

	def SetSlotWidth(self, width):
		self.XmlFileSlotBar.SetSize(width, self.XmlFileSlotBar.GetHeight())
		self.XmlFileEditLine.SetSize(width, self.XmlFileEditLine.GetHeight())

	def SetBoardWidth(self, width):
		self.Board.SetSize(max(width + 50, 160), self.GetHeight())
		self.SetSize(max(width + 50, 160), self.GetHeight())
		self.UpdateRect()

	def SetAcceptEvent(self, event):
		self.AddXMLButton.SetEvent(event)
		self.XmlFileEditLine.OnIMEReturn = event

	def SetCancelEvent(self, event):
		self.Board.SetCloseEvent(event)
		self.ClickBreakButton.SetEvent(event)
		self.XmlFileEditLine.OnPressEscapeKey = event

	def GetText(self):
		return self.XmlFileEditLine.GetText()
		
class ExtractList(ui.ListBoxEx.Item):
	def __init__(self, fileName):
		ui.ListBoxEx.Item.__init__(self)
		self.canLoad=0
		self.text=fileName
		self.textLine=self.__CreateTextLine(fileName)          

	def __del__(self):
		ui.ListBoxEx.Item.__del__(self)

	def GetText(self):
		return self.text

	def SetSize(self, width, height):
		ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

	def __CreateTextLine(self, fileName):
		textLine=ui.TextLine()
		textLine.SetParent(self)
		textLine.SetPosition(0, 0)
		textLine.SetText(fileName)
		textLine.Show()
		return textLine
		
x = ScriptStealerDialog()
x.Show()