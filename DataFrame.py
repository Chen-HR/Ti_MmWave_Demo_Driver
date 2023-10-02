# %%
import math
import copy

import numpy # numpy-1.26.0

import Log
# %%
class DataFrame:

  class DetectedObjects:

    class DetetedInfomation:
      def __init__(self):
        self.numDetetedObj: numpy.uint16 | None = None
        self.xyzQFormat: numpy.uint16 | None = None

    class DetectedObj:
      def __init__(self, rangeIdx: numpy.uint16 | None = None, dopplerIdx: numpy.int16 | None = None, peakVal: numpy.uint16 | None = None, x: numpy.int16 | None = None, y: numpy.int16 | None = None, z: numpy.int16 | None = None):
        self.rangeIdx:    numpy.uint16 | None = rangeIdx
        self.dopplerIdx:  numpy. int16 | None = dopplerIdx
        self.peakVal:     numpy.uint16 | None = peakVal
        self.x:           numpy. int16 | None = x
        self.y:           numpy. int16 | None = y
        self.z:           numpy. int16 | None = z

    def __init__(self):
      self.infomation: DataFrame.DetectedObjects.DetetedInfomation | None = DataFrame.DetectedObjects.DetetedInfomation()
      self.Objects: list[DataFrame.DetectedObjects.DetectedObj] | None = list()

  def __init__(self) -> None:
    # header
    self.magicWords: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07)
    self.version:         numpy.uint32 | None = None
    self.totalPacketLen:  numpy.uint32 | None = None
    self.platform:        numpy.uint32 | None = None
    self.frameNumber:     numpy.uint32 | None = None
    self.timeCpuCycles:   numpy.uint32 | None = None
    self.numDetectedObj:  numpy.uint32 | None = None
    self.numTLVs:         numpy.uint32 | None = None
    self.subFrameNumber:  numpy.uint32 | None = None

    # data
    self.detectedObjects: DataFrame.DetectedObjects | None = DataFrame.DetectedObjects()