## Script (Python) "formatSize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=size
##title=Format a give size (in bytes) into a nice string (xx Kb, xx Mb, xx Gb or xx bytes)
##

size=long(size)

if size>(1024L*1024L*1024L):
  return "%2.2f Gb" % float(float(size)/(1024L*1024L*1024L))
elif size>(1024L*1024L):
  return "%2.2f Mb" % float(float(size)/(1024L*1024L))
elif size>1024L:
  return "%2.2f Kb" % float(float(size)/(1024L))
else:
  return "%2d Bytes" % size
