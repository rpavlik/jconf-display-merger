#!/usr/bin/env python
# Copyright 2011 Iowa State University (Author: Ryan Pavlik <rpavlik@iastate.edu> <abiryan@ryand.net> http://academic.cleardefinition.com/
#
import sys
import inspect
from PySide.QtCore import * #QFile
from PySide.QtGui import * #QApplication, QMainWindow, QAction
from PySide.QtUiTools import * #QUiLoader

'''Merge display windows.'''

__author__ = "Ryan Pavlik"

__version__ = "0.1"

class MergerGUI(QObject):
	def __init__(self, uifn = "display-merger.ui", parent = None):
		super(MergerGUI, self).__init__(parent)
		uifile = QFile(uifn)
		uifile.open(QFile.ReadOnly)
		loader = QUiLoader()
		self.window = loader.load(uifile)
		self.window.show()
		uifile.close()
		actions = [ action for action in self.window.findChildren(QAction)
			if action.objectName() != "separator"
			and len(action.objectName()) > 0 ]
		for action in actions:
			slotname = "on_" + action.objectName()
			if hasattr(self, slotname):
				print "Connecting %s" % slotname
				QObject.connect(action, SIGNAL("triggered()"), getattr(self, slotname))
			else:
				print "No method %s found" % slotname

	def on_action_Open(self):
		print "Open!"

def main():
	app = QApplication(sys.argv)
	# Create and show window
	gui = MergerGUI()

	# Enter Qt application main loop
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
