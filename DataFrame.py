# %%
import math
import copy

import numpy # numpy-1.26.0

import Log
# %%
class Converter:
  margeUint8_array = lambda num_of_uint8: [2**(8*i) for i in range(num_of_uint8)]
  margeUint8 = lambda uint8_1DArray, index, N: (numpy.matmul(uint8_1DArray[index:index+N],Converter.margeUint8_array(N)), index+N)
  uint8_2_uintN = lambda uint8_1DArray, index, N: (numpy.matmul(uint8_1DArray[index:index+(N/8)],Converter.margeUint8_array((N/8))), index+(N/8))
  uint8_2_uint16 = lambda uint8_1DArray, index: (numpy.uint16(numpy.matmul(uint8_1DArray[index:index+2],Converter.margeUint8_array(2))), index+2)
  uint8_2_uint32 = lambda uint8_1DArray, index: (numpy.uint32(numpy.matmul(uint8_1DArray[index:index+4],Converter.margeUint8_array(4))), index+4)
  uint8_2_uint64 = lambda uint8_1DArray, index: (numpy.uint64(numpy.matmul(uint8_1DArray[index:index+8],Converter.margeUint8_array(8))), index+8)
  uint8_2_int16 = lambda uint8_1DArray, index: (numpy.int16(numpy.matmul(uint8_1DArray[index:index+2],Converter.margeUint8_array(2))), index+2)
  uint8_2_int32 = lambda uint8_1DArray, index: (numpy.int32(numpy.matmul(uint8_1DArray[index:index+4],Converter.margeUint8_array(4))), index+4)
  class QFormat:
    make = lambda Q, value: value * (2**Q)
    parse = lambda Q, value: value / (2**Q)
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

  class LogMagRange:
    def __init__(self):
      self.logMagRange: list[numpy.uint16] | None = None

  class NoiseProfile:
    def __init__(self):
      self.noiseProfile: list[numpy.uint16] | None = None

  class RangeAzimuthHeatMap:
    class Cmplx16ImRe:
      def __init__(self, imag: numpy.uint16, real: numpy.uint16):
        self.imag: numpy.uint16 = imag
        self.real: numpy.uint16 = real
      def __str__(self) -> str:
        return "({real}, {imag}i)".format(real=self.real, imag=self.imag)
    def __init__(self, numRangeBins: numpy.uint32 | None = None, numVirtualAntAzim: numpy.uint32 | None = None, numTotal: numpy.uint32 | None = None):
      self.numRangeBins:      numpy.uint32 | None = None
      self.numVirtualAntAzim: numpy.uint32 | None = None
      if numRangeBins is not None:
        self.numRangeBins:      numpy.uint32 = numRangeBins
        if numVirtualAntAzim is not None:
          self.numVirtualAntAzim = numVirtualAntAzim
        elif numTotal is not None:
          self.numVirtualAntAzim = numTotal
        else: 
          raise ValueError("when specify `numRangeBins`, need to specify `numVirtualAntAzim` or `numTotal`")
      self.rangeAzimuthHeatMap: list[list[DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe]] | list[DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe] = list()
    def __str__(self) -> str:
      string = "["
      for item in self.rangeAzimuthHeatMap:
        if self.numRangeBins is not None and self.numVirtualAntAzim is not None: # item: list[Cmplx16ImRe]
          string += "["
          for i in item:
            string += str(i) + ", "
          string = string[0:-2] + "], "
          pass
        else: # item: Cmplx16ImRe
          string += str(item) + ", "
      string = string[0:-2] + "]"
      return string

  class RangeDopplerHeatMap:
    def __init__(self, numRangeBins: numpy.uint32 | None = None, numDopplerBins: numpy.uint32 | None = None, numTotal: numpy.uint32 | None = None):
      self.numRangeBins:      numpy.uint32 | None = None
      self.numDopplerBins:    numpy.uint32 | None = None
      if numRangeBins is not None:
        self.numRangeBins:      numpy.uint32 = numRangeBins
        if numDopplerBins is not None:
          self.numDopplerBins = numDopplerBins
        elif numTotal is not None:
          self.numDopplerBins = numTotal
        else: 
          raise ValueError("when specify `numRangeBins`, need to specify `numDopplerBins` or `numTotal`")
      self.rangeDopplerHeatMap: list[list[numpy.uint16]] | list[numpy.uint16] = list()

  class StatsInfo:
    def __init__(self):
      self.interFrameProcessingTime:   numpy.uint32 | None = None
      self.transmitOutputTime:         numpy.uint32 | None = None
      self.interFrameProcessingMargin: numpy.uint32 | None = None
      self.interChirpProcessingMargin: numpy.uint32 | None = None
      self.activeFrameCPULoad:         numpy.uint32 | None = None
      self.interFrameCPULoad:          numpy.uint32 | None = None

  magicBytes: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07)
  def __init__(self, dataByte: bytearray | None = None) -> None:
    """Initialize DataFrame

    Args:
        dataByte (bytearray | None, optional): Initialize data source. Defaults to None.
    """
    self.logger = Log.Logger(fileName="Log/DataFrame.log")

    # header
    self.magicWords: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07) # `self.magicWords` will be removed, and use `DataFrame.magicBytes` instead
    self.version:         numpy.uint32 | None = None
    self.totalPacketLen:  numpy.uint32 | None = None
    self.platform:        numpy.uint32 | None = None
    self.frameNumber:     numpy.uint32 | None = None
    self.timeCpuCycles:   numpy.uint32 | None = None
    self.numDetectedObj:  numpy.uint32 | None = None
    self.numTLVs:         numpy.uint32 | None = None
    self.subFrameNumber:  numpy.uint32 | None = None
    # other arguments
    self.numRangeBins:      numpy.uint32 | None = None
    self.numVirtualAntAzim: numpy.uint32 | None = None
    self.numDopplerBins:    numpy.uint32 | None = None
    # data contents
    self.detectedObjects:     DataFrame.DetectedObjects     | None = DataFrame.DetectedObjects()
    self.logMagRange:         DataFrame.LogMagRange         | None = DataFrame.LogMagRange()
    self.noiseProfile:        DataFrame.NoiseProfile        | None = DataFrame.NoiseProfile()
    self.rangeAzimuthHeatMap: DataFrame.RangeAzimuthHeatMap | None = DataFrame.RangeAzimuthHeatMap()
    self.rangeDopplerHeatMap: DataFrame.RangeDopplerHeatMap | None = DataFrame.RangeDopplerHeatMap()
    self.statsInfo:           DataFrame.StatsInfo           | None = DataFrame.StatsInfo()

    # if dataByte is not None, parse dataByte
    if dataByte is not None:
      self.parse(dataByte)

  def parse(self, dataByte: bytearray, log: bool=False):
    """Parse data

    Args:
      dataByte (bytearray): Parse data sources
      log (bool, optional): Enable logging to log. Defaults to False.
    """
    # checke dataByte parse range
    BASE_NUMBER_OF_BITS = 8
    dataByte_uint8: numpy.NDArray[numpy.uint8] = numpy.frombuffer(buffer=dataByte, dtype=numpy.uint8) # Checke `dtype` need to reference from `BASE_NUMBER_OF_BITS`
    # print("dataByte.length = " + str(len(dataByte_uint8)))
    index: int | None = None
    # find the location of magicBytes
    for startIndex_checker in numpy.where(dataByte_uint8 == DataFrame.magicBytes[0])[0]:
      if numpy.all(dataByte_uint8[startIndex_checker:startIndex_checker+len(DataFrame.magicBytes)] == numpy.array(DataFrame.magicBytes, dtype=numpy.uint8)):
        index = startIndex_checker
        # add next line to get the first data frame, else to get the last data frame (Wrong: may be incomplete)
        break
    # TODO: check index of frame start is correct
    # TODO: check length of dataByte is enough (when all item of `guiMonitor` is enabled, TLV only can get first 4 items)
    self.logger.log(event="DataFrame.parse", level="logging", message="magicBytes: {}".format(dataByte[index:index+len(DataFrame.magicBytes)]))
    # print("dataByte: {}".format(dataByte[index:index+len(DataFrame.magicBytes)]))
    # print("dataByte_uint8: {}".format(dataByte_uint8[index:index+len(DataFrame.magicBytes)]))

    # print("index: {}/{}".format(index, len(dataByte_uint8)))
    # skip the magicBytes
    index += len(DataFrame.magicBytes)
    # read DataFrame header
    self.version         , index = Converter.uint8_2_uint32(dataByte, index)
    self.totalPacketLen  , index = Converter.uint8_2_uint32(dataByte, index)
    self.platform        , index = Converter.uint8_2_uint32(dataByte, index)
    self.frameNumber     , index = Converter.uint8_2_uint32(dataByte, index)
    self.timeCpuCycles   , index = Converter.uint8_2_uint32(dataByte, index)
    self.numDetectedObj  , index = Converter.uint8_2_uint32(dataByte, index)
    self.numTLVs         , index = Converter.uint8_2_uint32(dataByte, index)
    platform: numpy.uint32 = self.platform & 0x0000ff00
    if platform == 0x00001600:
      self.subFrameNumber  , index = Converter.uint8_2_uint32(dataByte, index)
    if log:
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.version       : {}.{}.{}.{}".format(int((self.version&0xff000000)>>24), int((self.version&0x00ff0000)>16), int((self.version&0x0000ff00)>8), int((self.version&0x000000ff))))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.totalPacketLen: {}".format(self.totalPacketLen))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.platform      : {}".format(format(self.platform, 'x')))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.frameNumber   : {}".format(self.frameNumber   ))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.timeCpuCycles : {}".format(self.timeCpuCycles ))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.numDetectedObj: {}".format(self.numDetectedObj))
      self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.numTLVs       : {}".format(self.numTLVs       ))
      if platform == 0x00001600:
        self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.subFrameNumber: {}".format(self.subFrameNumber))
    
    self.numRangeBins:      numpy.uint32 | None = None
    self.numVirtualAntAzim: numpy.uint32 | None = None
    self.numDopplerBins:    numpy.uint32 | None = None

    # read DataFrame contents
    for TLV_index in range(self.numTLVs):
      TLV_TypeId, index = Converter.uint8_2_uint32(dataByte, index)
      TLV_Length, index = Converter.uint8_2_uint32(dataByte, index) # bytes length of contents
      if log:
        self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.TLV[{}].TypeId: {}".format(TLV_index, TLV_TypeId))
        self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.TLV[{}].Length: {}".format(TLV_index, TLV_Length))
      # parse TLV
      # TLV: detectedObjects
      if TLV_TypeId == 1:
        self.detectedObjects.infomation.numDetetedObj, index = Converter.uint8_2_uint16(dataByte, index)
        self.detectedObjects.infomation.xyzQFormat   , index = Converter.uint8_2_uint16(dataByte, index)
        if log:
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.infomation.numDetetedObj: {}".format(self.detectedObjects.infomation.numDetetedObj)) # TODO: check this with `self.data.numDetectedObj`
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.infomation.xyzQFormat   : {}".format(self.detectedObjects.infomation.xyzQFormat   ))
        self.detectedObjects.Objects = []
        for DetetedObj_index in range(self.detectedObjects.infomation.numDetetedObj):
          rangeIdx  , index = Converter.uint8_2_uint16(dataByte, index)
          dopplerIdx, index = Converter.uint8_2_int16(dataByte, index)
          peakVal   , index = Converter.uint8_2_uint16(dataByte, index)
          x         , index = Converter.uint8_2_int16(dataByte, index)
          y         , index = Converter.uint8_2_int16(dataByte, index)
          z         , index = Converter.uint8_2_int16(dataByte, index)
          self.detectedObjects.Objects.append(self.detectedObjects.DetectedObj(rangeIdx, dopplerIdx, peakVal, x, y, z))
          if log: self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.Objects[{index:{index_log10}d}]: ({rangeIdx:3d}, {dopplerIdx:3d}, {peakVal:3d}, {x:5d}, {y:5d}, {z:5d}) -> ({xQFormat:8.4f}, {yQFormat:8.4f}, {zQFormat:8.4f})".format(
            index=DetetedObj_index, 
            index_log10=int(math.log10(self.detectedObjects.infomation.numDetetedObj))+1, 
            rangeIdx=rangeIdx, dopplerIdx=dopplerIdx, peakVal=peakVal, x=x, y=y, z=z, 
            xQFormat=Converter.QFormat.parse(self.detectedObjects.infomation.xyzQFormat, x), 
            yQFormat=Converter.QFormat.parse(self.detectedObjects.infomation.xyzQFormat, y), 
            zQFormat=Converter.QFormat.parse(self.detectedObjects.infomation.xyzQFormat, z)))
        # TODO: check TLV length
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      # TLV: logMagRange
      elif TLV_TypeId == 2:
        self.logMagRange.logMagRange = list()
        self.numRangeBins = TLV_Length//2
        for _ in range(self.numRangeBins):
          _logMagRange, index = Converter.uint8_2_uint16(dataByte, index)
          self.logMagRange.logMagRange.append(_logMagRange)
        if log: self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.logMagRange: {}".format(self.logMagRange.logMagRange))
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      # TLV: noiseProfile
      elif TLV_TypeId == 3:
        self.noiseProfile.noiseProfile = list()
        self.numRangeBins = TLV_Length//2
        for _ in range(self.numRangeBins):
          _noiseProfile, index = Converter.uint8_2_uint16(dataByte, index)
          self.noiseProfile.noiseProfile.append(_noiseProfile)
        if log: self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.noiseProfile: {}".format(self.noiseProfile.noiseProfile))
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      # TLV: rangeAzimuthHeatMap
      elif TLV_TypeId == 4:
        self.rangeAzimuthHeatMap.rangeAzimuthHeatMap = list()
        self.rangeAzimuthHeatMap.numRangeBins = self.numRangeBins
        if self.numRangeBins is not None: # TODO: Restructure this paragraph
          self.numVirtualAntAzim = (TLV_Length//4) // self.numRangeBins
          self.rangeAzimuthHeatMap.numVirtualAntAzim = self.numVirtualAntAzim
          for _ in range(self.numRangeBins): # TODO: unconfirmed is `numRangeBins` or `numVirtualAntAzim`
            _numRangeBins = list()
            for _ in range(self.numVirtualAntAzim): # TODO: unconfirmed is `numRangeBins` or `numVirtualAntAzim`
              imag, index = Converter.uint8_2_int16(dataByte, index)
              real, index = Converter.uint8_2_int16(dataByte, index)
              _numRangeBins.append(DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe(imag, real))
            self.rangeAzimuthHeatMap.rangeAzimuthHeatMap.append(copy.deepcopy(_numRangeBins))
        else:
          for _ in range(TLV_Length//4):
            imag, index = Converter.uint8_2_int16(dataByte, index)
            real, index = Converter.uint8_2_int16(dataByte, index)
            self.rangeAzimuthHeatMap.rangeAzimuthHeatMap.append(DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe(imag, real))
        if log: self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.rangeAzimuthHeatMap: {}".format(str(self.rangeAzimuthHeatMap))) # TODO: fix output content
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      # TLV: rangeDopplerHeatMap
      elif TLV_TypeId == 5:
        self.rangeDopplerHeatMap.rangeDopplerHeatMap = list()
        self.rangeDopplerHeatMap.numRangeBins = self.numRangeBins
        if self.numRangeBins is not None: # TODO: Restructure this paragraph
          self.numDopplerBins = (TLV_Length//2) // self.numRangeBins
          self.rangeDopplerHeatMap.numDopplerBins = self.numDopplerBins
          for _ in range(self.numRangeBins): # TODO: unconfirmed is `numRangeBins` or `numDopplerBins`
            _numRangeBins = list()
            for _ in range(self.numDopplerBins): # TODO: unconfirmed is `numRangeBins` or `numDopplerBins`
              _rangeDopplerHeatMap, index = Converter.uint8_2_uint16(dataByte, index)
              _numRangeBins.append(_rangeDopplerHeatMap)
            self.rangeDopplerHeatMap.rangeDopplerHeatMap.append(copy.deepcopy(_numRangeBins))
        else:
          for _ in range(TLV_Length//4):
            _rangeDopplerHeatMap, index = Converter.uint8_2_uint16(dataByte, index)
            self.rangeDopplerHeatMap.rangeDopplerHeatMap.append(_rangeDopplerHeatMap)
        if log: self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.rangeDopplerHeatMap: {}".format(self.rangeDopplerHeatMap.rangeDopplerHeatMap))
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      # TLV: statsInfo
      elif TLV_TypeId == 6:
        self.statsInfo.interFrameProcessingTime  , index = Converter.uint8_2_uint32(dataByte, index)
        self.statsInfo.transmitOutputTime        , index = Converter.uint8_2_uint32(dataByte, index)
        self.statsInfo.interFrameProcessingMargin, index = Converter.uint8_2_uint32(dataByte, index)
        self.statsInfo.interChirpProcessingMargin, index = Converter.uint8_2_uint32(dataByte, index)
        self.statsInfo.activeFrameCPULoad        , index = Converter.uint8_2_uint32(dataByte, index)
        self.statsInfo.interFrameCPULoad         , index = Converter.uint8_2_uint32(dataByte, index)
        if log: 
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameProcessingTime  : {}".format(self.statsInfo.interFrameProcessingTime  ))
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.transmitOutputTime        : {}".format(self.statsInfo.transmitOutputTime        ))
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameProcessingMargin: {}".format(self.statsInfo.interFrameProcessingMargin))
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interChirpProcessingMargin: {}".format(self.statsInfo.interChirpProcessingMargin))
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.activeFrameCPULoad        : {}".format(self.statsInfo.activeFrameCPULoad        ))
          self.logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameCPULoad         : {}".format(self.statsInfo.interFrameCPULoad         ))
        # print("index: {}/{}".format(index, len(dataByte_uint8)))
      else: self.logger.log(event="DataFrame.parse", level="Error", message="Error TypeId: {}".format(TLV_TypeId))
      # TODO: check frame length
      # TODO: clear readed frame data from `data.buffer`
    
    # print("index: {}/{}".format(index, len(dataByte_uint8)))