# %%
import math
import copy

import numpy # numpy-1.26.0

import Log
# %%
class DetectedObjects:

  class DetetedInfomation:
    numDetetedObj: numpy.uint16 | None = None
    xyzQFormat: numpy.uint16 | None = None
    def __init__(self):
      pass
  class DetectedObj:
    rangeIdx: numpy.uint16 | None = None
    dopplerIdx: numpy.int16 | None = None
    peakVal: numpy.uint16 | None = None
    x: numpy.int16 | None = None
    y: numpy.int16 | None = None
    z: numpy.int16 | None = None
    def __init__(self):
      pass
    def __init__(self, rangeIdx, dopplerIdx, peakVal, x, y, z):
      self.rangeIdx   = rangeIdx
      self.dopplerIdx = dopplerIdx
      self.peakVal    = peakVal
      self.x          = x
      self.y          = y
      self.z          = z
      pass

  infomation: DetetedInfomation | None = DetetedInfomation()
  Objects: list[DetectedObj] | None = list()
  
  def __init__(self):
    # self.infomation = DetectedObjects.DetetedInfomation()
    # self.Objects = list()
    pass


# %%


# %%
class DataFrame:

  # header
  magicWords: tuple[numpy.uint8] | None = None
  version: numpy.uint32 | None = None
  totalPacketLen: numpy.uint32 | None = None
  platform: numpy.uint32 | None = None
  frameNumber: numpy.uint32 | None = None
  timeCpuCycles: numpy.uint32 | None = None
  numDetectedObj: numpy.uint32 | None = None
  numTLVs: numpy.uint32 | None = None
  subFrameNumber: numpy.uint32 | None = None

  # data
  detectedObjects: DetectedObjects | None = DetectedObjects()

  def __init__(self) -> None:
    self.magicWords: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07)
    # self.detectedObjects = DetectedObjects()