#!/usr/bin/env python
# Copyright 2011 Iowa State University (Author: Ryan Pavlik <rpavlik@iastate.edu> <abiryan@ryand.net> http://academic.cleardefinition.com/
#
import sys
import jconfdisplays
from PySide.QtCore import * #QFile
from PySide.QtGui import * #QApplication, QMainWindow, QAction
from PySide.QtUiTools import * #QUiLoader

'''Merge display windows.'''

__author__ = "Ryan Pavlik"

__version__ = "0.1"

class MergerGUI(QObject):
	def __init__(self, uifn = "display-merger.ui", parent = None):
		super(MergerGUI, self).__init__(parent)

		# Load UI
		uifile = QFile(uifn)
		uifile.open(QFile.ReadOnly)
		self.loader = QUiLoader()
		self.window = self.loader.load(uifile)
		self.window.show()
		uifile.close()

		# Set up attributes of this class
		self.tree = self.window.findChild(QTreeWidget)

		# Connect actions
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
	def open_file(self, fn):
		self.jconf = jconfdisplays.JConf(fn)
		self.refresh_tree()

	def refresh_tree(self):
		tree = self.window.findChild(QTreeWidget)
		if tree.topLevelItemCount() > 0:
			tree.clear()
		self.windows = {}
		for display_window in self.jconf.display_windows:
			item = QTreeWidgetItem(None, ["%s: %d, %d, %d, %d" % 
				(
				display_window.name,
				int(display_window.origin[0].text),
				int(display_window.origin[1].text),
				int(display_window.size[0].text),
				int(display_window.size[1].text),
				)
				])
			tree.addTopLevelItem(item)
			self.windows[item] = display_window
			for vp in display_window.surface_viewports:
				vpitem = QTreeWidgetItem(None, ["%s: %d, %d, %d, %d" % 
					(
					vp.name,
					int(vp.pixel_origin[0]),
					int(vp.pixel_origin[1]),
					int(vp.pixel_size[0]),
					int(vp.pixel_size[1]),
					)
					])
				item.addChild(vpitem)

	def on_action_Open(self):
		print "Open!"
		fn, selfilter = QFileDialog.getOpenFileName(None, "Choose a jconf file")
		print fn
		self.open_file(fn)

def main():
	app = QApplication(sys.argv)
	# Create and show window
	gui = MergerGUI()
	if len(sys.argv) > 1:
		gui.open_file(sys.argv[1])
	# Enter Qt application main loop
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
