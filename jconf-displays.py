#!/usr/bin/env python
# jconfdisplays - parse a VR Juggler jconf file for display info
# Author: Ryan Pavlik

#          Copyright Iowa State University 2011.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

import xml.etree.cElementTree as et
import sys

ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"

class SurfaceViewport(object):
	def __init__(self, elt, window):
		self.window = window
		self.wrapper = elt
		self.elt = elt.find(ns + "surface_viewport")
		self.name = self.elt.get("name")
		self.origin = self.elt.findall(ns + "origin")
		self.size = self.elt.findall(ns + "size")
		self.pixel_origin = [ float(vp.text) * float(dw.text) for (vp, dw) in zip(self.origin, self.window.origin) ]
		self.pixel_size = [ float(vp.text) * float(dw.text) for (vp, dw) in zip(self.size, self.window.size) ]
		print self.pixel_origin
		print self.pixel_size

class DisplayWindow(object):
	def __init__(self, elt, parent):
		self.parent = parent
		self.elt = elt
		self.name = elt.get("name")
		self.origin = elt.findall(ns + "origin")
		self.size = elt.findall(ns + "size")
		self.surface_viewports = [ SurfaceViewport(surface, self) for surface in elt.findall(ns + "surface_viewports") ]
	def removeViewport(self, vp):
		self.elt.remove(vp.wrapper)
		self.surface_viewports.remove(vp)
	def addViewport(self, vp):
		self.elt.append(vp.wrapper)
		self.surface_viewports.append(vp)


class JConf(object):
	def __init__(self, fullpath):
		self.fullpath = fullpath

		self.tree = et.ElementTree(file = fullpath)
		root = self.tree.getroot()

		for firstLevel in list(root):
			if firstLevel.tag == ns + "include":
				# recurse into included file
				# TODO
				pass
			elif firstLevel.tag == ns + "elements":
				self.elements = firstLevel
				self.display_windows = [ DisplayWindow(window, firstLevel) for window in self.elements.findall(ns + "display_window") ]

			else:
				continue
	def removeWindow(self, window):
		self.elements.remove(window.elt)
		self.display_windows.remove(window)

	def tostring(self):
		return """<?xml version="1.0" encoding="UTF-8"?>
<?org-vrjuggler-jccl-settings configuration.version="3.0"?>
""" + et.tostring(self.tree.getroot())

if __name__ == "__main__":
	config = JConf(sys.argv[1])
	for win in config.display_windows[1:]:
		config.removeWindow(win)

	print config.tostring()
