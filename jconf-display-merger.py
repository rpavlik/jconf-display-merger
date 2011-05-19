#!/usr/bin/env python
# Copyright 2011 Iowa State University (Author: Ryan Pavlik <rpavlik@iastate.edu> <abiryan@ryand.net> http://academic.cleardefinition.com/
#
import sys
from PySide.QtCore import QFile
from PySide.QtGui import QApplication, QMainWindow
from PySide.QtUiTools import QUiLoader

'''Merge display windows.'''

__author__ = "Ryan Pavlik"

__version__ = "0.1"

class MergerWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MergerWindow, self).__init__(parent)
        self.resize(800, 600)  
        

def main():
	app = QApplication(sys.argv)
	# Create and show window
	win = MergerWindow()
	win.show()
	uifile = QFile("display-merger.ui")
	uifile.open(QFile.ReadOnly)
	loader = QUiLoader()
	widget = loader.load(uifile)
	uifile.close()
	widget.show()
	# Enter Qt application main loop
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
