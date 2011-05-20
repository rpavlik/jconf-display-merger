#!/usr/bin/env python
# jconfdisplays - parse a VR Juggler jconf file for display info, and
# being able to modify
# Author: Ryan Pavlik

#          Copyright Iowa State University 2011.
# Distributed under the Boost Software License, Version 1.0.
#    (See accompanying file LICENSE_1_0.txt or copy at
#          http://www.boost.org/LICENSE_1_0.txt)

import sys

try:
	import xml.etree.ElementTree
	needsNewerET = (xml.etree.ElementTree.VERSION.split(".")[:2] < ["1", "3"])
except:
	needsNewerET = True

if needsNewerET:
	# Use bundled ElementTree instead
	import os.path
	sys.path.append(os.path.join(sys.path[0], "elementtree-1.3a3-20070912"))
	import elementtree.ElementTree as et
else:
	et = xml.etree.ElementTree

ns = "{http://www.vrjuggler.org/jccl/xsd/3.0/configuration}"

class BBox2d(object):

	@staticmethod
	def union(bboxes):
		mins = bboxes[0].origin[:]
		maxes = [ origin + size for (origin, size) in zip(bboxes[0].origin, bboxes[0].size) ]
		for bbox in bboxes:
			for corner in bbox.corners():
				mins = [ min(prev, current) for (prev, current) in zip(mins, corner) ]
				maxes = [ max(prev, current) for (prev, current) in zip(maxes, corner) ]
		return BBox2d(mins, [theMax - theMin for (theMax, theMin) in zip(maxes, mins) ])

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
		self.origin = list(self.elt.findall(ns + "origin"))
		self.size = list(self.elt.findall(ns + "size"))
		self.pixel_origin = [ float(vp.text) * float(dw.text) + float(dwo.text) for (vp, dw, dwo) in zip(self.origin, self.window.size, self.window.origin) ]
		self.pixel_size = [ float(vp.text) * float(dw.text) for (vp, dw) in zip(self.size, self.window.size) ]

class DisplayWindow(object):
	def __init__(self, elt, jconf):
		self.jconf = jconf
		self.elt = elt
		self.name = elt.get("name")
		self.origin = list(elt.findall(ns + "origin"))
		self.size = list(elt.findall(ns + "size"))
		self.surface_viewports = [ SurfaceViewport(surface, self) for surface in elt.findall(ns + "surface_viewports") ]

	def removeViewport(self, vp):
		self.elt.remove(vp.wrapper)
		self.surface_viewports.remove(vp)

	def addViewport(self, vp):
		self.elt.append(vp.wrapper)
		self.surface_viewports.append(vp)

	def merge(self, other):
		# Update the display window's origin and size
		unifiedBBox = BBox2d.union([
			BBox2d([int(elt.text) for elt in self.origin], [int(elt.text) for elt in self.size]),
			BBox2d([int(elt.text) for elt in other.origin], [int(elt.text) for elt in other.size]),
			])
		for coord in range(0, 2):
			self.origin[coord].text = str(unifiedBBox.origin[coord])
			self.size[coord].text = str(unifiedBBox.size[coord])

		# Transfer viewport ownership
		for vp in other.surface_viewports[:]:
			other.removeViewport(vp)
			self.addViewport(vp)

		# Update viewport normalized dimensions
		for vp in self.surface_viewports:
			for coord in range(0, 2):
				vp.origin[coord].text = str((vp.pixel_origin[coord] - unifiedBBox.origin[coord]) / unifiedBBox.size[coord])
				vp.size[coord].text = str(vp.pixel_size[coord] / unifiedBBox.size[coord])

		# Update our own name
		self.name = self.name + "," + other.name
		self.elt.set("name", self.name)

		# Remove other window from jconf
		other.jconf.removeWindow(other)



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

		# This statement appears to do nothing? Wanted to set this as the default namespace...
		#et.register_namespace("", ns)

		return """<?xml version="1.0" encoding="UTF-8"?>
<?org-vrjuggler-jccl-settings configuration.version="3.0"?>
""" + et.tostring(self.tree.getroot())

if __name__ == "__main__":
	config = JConf(sys.argv[1])
	for win in config.display_windows[1:]:
		config.display_windows[0].merge(win)

	print config.tostring()
