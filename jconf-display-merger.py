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
		self.jconf = None

		# Connect actions
		actions = [ action for action in self.window.findChildren(QAction)
			if action.objectName() != "separator"
			and len(action.objectName()) > 0 ]
		for action in actions:
			slotname = "on_" + action.objectName()
			if hasattr(self, slotname):
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
			item = QTreeWidgetItem(None, ["%s" % display_window.name,
					"%d px, %d px" % (int(display_window.origin[0].text), int(display_window.origin[1].text)),
					"%d px x %d px" % (int(display_window.size[0].text), int(display_window.size[1].text))
				])
			tree.addTopLevelItem(item)
			self.windows[item] = display_window
			for vp in display_window.surface_viewports:
				vpitem = QTreeWidgetItem(item, ["%s" % vp.name,
					"%f, %f" % (float(vp.origin[0].text), float(vp.origin[1].text)),
					"%f x %f" % (float(vp.size[0].text), float(vp.size[1].text))
				])
				item.addChild(vpitem)
			item.setExpanded(True)
		for col in range(0, 3):
			tree.resizeColumnToContents(col)

	def on_action_Open(self):
		fn, selfilter = QFileDialog.getOpenFileName(None, "Choose a jconf file")
		print fn
		self.open_file(fn)

	def on_action_Save(self):
		if self.jconf is not None:
			with open(self.jconf.fullpath, "w") as outfile:
				outfile.write(self.jconf.tostring())

	def on_action_Merge_selected_windows(self):
		selectedWindows = [self.windows[item] for item in self.tree.selectedItems() if item in self.windows and item.parent() is None]
		selectedViewports = [self.windows[item.parent()] for item in self.tree.selectedItems() if item.parent() in self.windows and self.windows[item.parent()] not in selectedWindows]
		selectedWindows.extend(selectedViewports)
		if len(selectedWindows) > 1:
			keeper = selectedWindows[0]
			for other in selectedWindows[1:]:
				keeper.merge(other)
			self.refresh_tree()
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
