import dbg
x=3543.543214

class hackme(object):
	def __init__(self):
		self.checkedSum=23
	def checkValue(self, val):
		if x!=3:
			return dbg.LogBox("failure")
		if val!=1.3:
			return
		if self.checkedSum!=4.3:
			return
		dbg.LogBox("succ")
		
