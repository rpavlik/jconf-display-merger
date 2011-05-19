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

class BBox2d(object):
	def union(bboxes):
		mins = bboxes[0].origin[:]
		maxes = [ origin + size for (origin, size) in zip(bboxes[0].origin, bboxes[0].size) ]
		for bbox in bboxes:
			for corner in bbox.corners():
				mins = [ min(prev, current) for (prev, current) in zip(mins, corner) ]
				maxes = [ max(prev, current) for (prev, current) in zip(maxes, corner) ]
		return BBox3d(mins, [theMax - theMin for (theMax, theMin) in zip(maxes, mins) ])

	def __init__(self, origin = [0, 0], size = [0, 0]):
		self.origin = origin
		self.size = size

	def corners(self):
		origin = self.origin[:]
		size = self.size[:]
		yield origin[:]
		yield [origin[0] + size[0], origin[1] ]
		yield [origin[0] + size[0], origin[1] + size[1] ]
		yield [origin[0], origin[1] + size[1] ]

class SurfaceViewport(object):
	def __init__(self, elt, window):
		self.window = window
		self.wrapper = elt
		self.elt = elt.find(ns + "surface_viewport")
		self.name = self.elt.get("name")
		self.origin = self.elt.findall(ns + "origin")
		self.size = self.elt.findall(ns + "size")
		self.pixel_origin = [ float(vp.text) * float(dw.text) + float(dwo.text) for (vp, dw, dwo) in zip(self.origin, self.window.size, self.window.origin) ]
		self.pixel_size = [ float(vp.text) * float(dw.text) for (vp, dw) in zip(self.size, self.window.size) ]
		print self.pixel_origin
		print self.pixel_size

class DisplayWindow(object):
	def __init__(self, elt, jconf):
		self.jconf = jconf
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

	def merge(self, other):
		vports = other.surface_viewports[:]
		originalOrigin = [int(elt.text) for elt in self.origin]
		newOrigin = [int(elt.text) for elt in self.origin]
		for coord in range(0, 2):
			origOther = int(other.origin[coord].text)
			origSelf = int(self.origin[coord].text)
			if origOther < origSelf:
				diff = origSelf - origOther
				self.origin[coord].text = other.origin[coord].text
				self.size[coord].text = int(self.size[coord].text) + diff



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
				self.display_windows = [ DisplayWindow(window, self) for window in self.elements.findall(ns + "display_window") ]

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
