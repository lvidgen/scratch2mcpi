#!/usr/bin/env python
import sys
import os
import gettext
import scratch
import mcpi.minecraft as minecraft

localedir = os.path.join(os.path.dirname(__file__), 'locale')
_ = gettext.translation(domain = 'main', localedir = localedir, fallback = True).ugettext

try:
  mc = minecraft.Minecraft.create()
except:
  print _("Error: Unable to connect to Minecraft. Minecraft may be not running.")
  sys.exit()

try:
  s = scratch.Scratch()
except scratch.ScratchError:
  print _("Error: Unable to connect to Scratch. Scratch may be not running or the remote sensor connections may be not enabled.") 
  sys.exit()

print _("Connected to Scratch")
x = 0
y = 0
z = 0
blockTypeId = 1

def listen():
  while True:
    try:
      yield s.receive()
    except scratch.ScratchError:
      raise StopIteration

for msg in listen():
  if msg[0] == 'broadcast':
    if msg[1] == 'hi':
      mc.postToChat("hi minecraft")
    elif msg[1] == 'p':
      mc.player.setPos(x, y, z)
      print "setPos: %d %d %d" % (x, y, z)
    elif msg[1] == 'b':
      mc.setBlock(x, y, z, blockTypeId)
      print "setBlock: %d %d %d %d" % (x, y, z, blockTypeId)
  elif msg[0] == 'sensor-update':
    x = msg[1].get('x', x)
    y = msg[1].get('y', y)
    z = msg[1].get('z', z)
    blockTypeId = msg[1].get('b', blockTypeId)
    print "x:%d,y:%d,z:%d" % (x, y, z)

