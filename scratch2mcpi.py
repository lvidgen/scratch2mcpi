#!/usr/bin/env python

import sys
import os
import gettext
import scratch
import mcpi.minecraft as minecraft
import time

VERSION = "1.0.2"
localedir = os.path.join(os.path.dirname(__file__), 'locale')
_ = gettext.translation(domain = 'scratch2mcpi', localedir = localedir, fallback = True).ugettext

def is_number(mc, variable_name, value):
  if (isinstance(value, (int, float))):
    return True
  else:
    return False

def connect():
  try:
    return scratch.Scratch()
  except scratch.ScratchError:
    print _("Error: Unable to connect to Scratch. Scratch may be not running or the remote sensor connections may be not enabled.") 
    return None

def _listen(s):
  while True:
    try:
      yield s.receive()
    except scratch.ScratchError:
      print _("Error: Disconnected from Scratch.")
      raise StopIteration

def listen(s, mc):
  mcpiX = 0
  mcpiY = 0
  mcpiZ = 0
  mcpiX0 = 0
  mcpiY0 = 0
  mcpiZ0 = 0
  mcpiX1 = 0
  mcpiY1 = 0
  mcpiZ1 = 0
  blockTypeId = 1
  blockData = 0

  for msg in _listen(s):
    if (msg):
      print "Received: %s" % str(msg)
      if msg[0] == 'broadcast':
        if not mc:
          mc = minecraft.Minecraft.create()
        if msg[1] == 'hello_minecraft':
          mc.postToChat("hello minecraft")
        elif msg[1] == 'setPos':
          if (is_number(mc, "mcpiX", mcpiX) and is_number(mc, "mcpiY", mcpiY) and is_number(mc, "mcpiZ", mcpiZ)): 
            mc.player.setPos(mcpiX, mcpiY, mcpiZ)
            print "setPos: %.1f %.1f %.1f" % (mcpiX, mcpiY, mcpiZ)
        elif msg[1] == 'setBlock':
          if (is_number(mc, 'mcpiX', mcpiX) and is_number(mc, 'mcpiY', mcpiY) and is_number(mc, 'mcpiZ', mcpiZ) and is_number(mc, 'blockTypeId', blockTypeId) and is_number(mc, 'blockData', blockData)):
            mc.setBlock(mcpiX, mcpiY, mcpiZ, blockTypeId, blockData)
            print "setBlock: %d %d %d %d %d" % (mcpiX, mcpiY, mcpiZ, blockTypeId, blockData)
        elif msg[1] == 'setBlocks':
          if (is_number(mc, 'mcpiX0', mcpiX0) and is_number(mc, 'mcpiY0', mcpiY0) and is_number(mc, 'mcpiZ0', mcpiZ0) and is_number(mc, 'mcpiX1', mcpiX1) and is_number(mc, 'mcpiY1', mcpiY1) and is_number(mc, 'mcpiZ1', mcpiZ1) and is_number(mc, 'blockTypeId', blockTypeId) and is_number(mc, 'blockData', blockData)):
            mc.setBlocks(mcpiX0, mcpiY0, mcpiZ0, mcpiX1, mcpiY1, mcpiZ1, blockTypeId, blockData)
            print "setBlocks(%d, %d, %d, %d, %d, %d, %d, %d" % (mcpiX0, mcpiY0, mcpiZ0, mcpiX1, mcpiY1, mcpiZ1, blockTypeId, blockData)
        elif msg[1] == 'getPos':
          playerPos = mc.player.getPos()
          s.sensorupdate(
           {'playerX': playerPos.x,
            'playerY': playerPos.y,
            'playerZ': playerPos.z}
          )
        elif msg[1] == 'getHeight':
          posY = mc.getHeight(mcpiX, mcpiZ)
          s.sensorupdate({'posY': posY})
          mc.postToChat("posY: %d" % posY)
        elif msg[1] == 'pollBlockHits':
          blockEvents = mc.events.pollBlockHits()
          print blockEvents
          if blockEvents:
            blockEvent = blockEvents[-1]
            s.sensorupdate(
             {'blockEventX': blockEvent.pos.x,
              'blockEventY': blockEvent.pos.y,
              'blockEventZ': blockEvent.pos.z,
              'blockEventFace': blockEvent.face,
              'blockEventEntityId': blockEvent.entityId}
            )
          else:
            s.sensorupdate(
             {'blockEventX': '',
              'blockEventY': '',
              'blockEventZ': '',
              'blockEventFace': '',
              'blockEventEntityId': ''}
            )
        elif msg[1] == 'reset':
          mc.postToChat('reset the world')
          mc.setBlocks(-100, 0, -100, 100, 63, 100, 0, 0)
          mc.setBlocks(-100, -63, -100, 100, -2, 100, 1, 0)
          mc.setBlocks(-100, -1, -100, 100, -1, 100, 2, 0)
          mc.player.setPos(0, 0, 0)
      elif msg[0] == 'sensor-update':
        mcpiX = msg[1].get('mcpiX', mcpiX)
        mcpiY = msg[1].get('mcpiY', mcpiY)
        mcpiZ = msg[1].get('mcpiZ', mcpiZ)
        mcpiX0 = msg[1].get('mcpiX0', mcpiX0)
        mcpiY0 = msg[1].get('mcpiY0', mcpiY0)
        mcpiZ0 = msg[1].get('mcpiZ0', mcpiZ0)
        mcpiX1 = msg[1].get('mcpiX1', mcpiX1)
        mcpiY1 = msg[1].get('mcpiY1', mcpiY1)
        mcpiZ1 = msg[1].get('mcpiZ1', mcpiZ1)
        blockTypeId = msg[1].get('blockTypeId', blockTypeId)
        blockData = msg[1].get('blockData', blockData)


def main():
  print "================="
  print "Sratch2MCPI %s" % VERSION
  print "================="
  print ""

  while True:
    s = connect()
    mc = minecraft.Minecraft.create()

    if (s):
      mc.postToChat("Scratch2MCPI connected to Minecraft Pi.")
      print _("Connected to Scratch")

      s.broadcast("hello_minecraft")
      s.broadcast("setPos")
      s.broadcast("setBlock")
      s.broadcast("setBlocks")
      s.broadcast("getPos")
      s.broadcast("getHeight")
      s.broadcast("pollBlockHits")
      s.broadcast("reset")

      listen(s, mc)
    time.sleep(5)

main()
