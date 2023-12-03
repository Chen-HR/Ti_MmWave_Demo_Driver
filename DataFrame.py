# %%
import math
import copy

import numpy # numpy-1.26.0

try:
  import Logging
except ModuleNotFoundError:
  from Ti_mmWave_Demo_Driver import Logging
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

  magicWords: tuple[numpy.uint16] = (0x0102, 0x0304, 0x0506, 0x0708)
  magicBytes: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07)

  def __init__(self, log: str | None = None) -> None:
    """Initialize DataFrame
    """
    self.logger = Logging.Logger(log if log is not None else "Log/DataFrame.log")

    # header
    # self.magicWords: tuple[numpy.uint8] = (0x02, 0x01, 0x04, 0x03, 0x06, 0x05, 0x08, 0x07) # `self.magicWords` will be removed, and use `DataFrame.magicBytes` instead
    self.version:         numpy.uint32 | None = None
    self.totalPacketLen:  numpy.uint32 | None = None
    self.platform:        numpy.uint32 | None = None
    self.frameNumber:     numpy.uint32 | None = None
    self.timeCpuCycles:   numpy.uint32 | None = None
    self.numDetectedObj:  numpy.uint32 | None = None
    self.numTLVs:         numpy.uint32 | None = None
    self.subFrameNumber:  numpy.uint32 | None = None
    # # other arguments
    # self.numRangeBins:      numpy.uint32 | None = None
    # self.numVirtualAntAzim: numpy.uint32 | None = None
    # self.numDopplerBins:    numpy.uint32 | None = None
    # data contents
    self.detectedObjects:     DataFrame.DetectedObjects     | None = DataFrame.DetectedObjects()
    self.logMagRange:         DataFrame.LogMagRange         | None = DataFrame.LogMagRange()
    self.noiseProfile:        DataFrame.NoiseProfile        | None = DataFrame.NoiseProfile()
    self.rangeAzimuthHeatMap: DataFrame.RangeAzimuthHeatMap | None = DataFrame.RangeAzimuthHeatMap()
    self.rangeDopplerHeatMap: DataFrame.RangeDopplerHeatMap | None = DataFrame.RangeDopplerHeatMap()
    self.statsInfo:           DataFrame.StatsInfo           | None = DataFrame.StatsInfo()

    self.CRC32: numpy.uint32 | None = None
    self.iscomplete: bool = False

  @staticmethod
  def parse(dataByte: bytearray, log: str | None = None):
    """Parse dataByte to get dataFrame

    Args:
      dataByte (bytearray): Parse data sources
      log (bool, optional): Enable logging to log. Defaults to False.
    """
    logger = Logging.Logger(log if log is not None else "Log/DataFrame.log")
    dataFrame: DataFrame = DataFrame()

    # checke dataByte parse range
    BASE_NUMBER_OF_BITS = 8
    dataByte_uint8: numpy.NDArray[numpy.uint8] = numpy.frombuffer(buffer=dataByte, dtype=numpy.uint8) # Checke `dtype` need to reference from `BASE_NUMBER_OF_BITS`
    # print("dataByte.length = " + str(len(dataByte_uint8)))
    index: int | None = None

    # find the location of magicBytes
    # for startIndex_checker in numpy.where(dataByte == DataFrame.magicBytes[0])[0]:
    for startIndex_checker in numpy.where(dataByte_uint8 == DataFrame.magicBytes[0])[0]:
      # if numpy.all(dataByte_uint8[startIndex_checker:startIndex_checker+len(DataFrame.magicBytes)] == numpy.array(DataFrame.magicBytes, dtype=numpy.uint8)):
      if numpy.all(dataByte[startIndex_checker:startIndex_checker+len(DataFrame.magicBytes)] == numpy.array(DataFrame.magicBytes, dtype=numpy.uint8)):
        index = startIndex_checker
        # add next line to get the first data frame, else to get the last data frame (Wrong: may be incomplete)
        break

    # check index of frame start is correct
    if index is None: 
      logger.log(event="DataFrame.parse", level="Error", message="DataFrame not found")
      return None, None

    logger.log(event="DataFrame.parse", level="logging", message="magicBytes: {}".format(dataByte[index:index+len(DataFrame.magicBytes)]))
    # print("dataByte: {}".format(dataByte[index:index+len(DataFrame.magicBytes)]))
    # print("dataByte_uint8: {}".format(dataByte_uint8[index:index+len(DataFrame.magicBytes)]))
    # print("index: {}/{}".format(index, len(dataByte_uint8)))

    # record the dataFrame length
    length = 0

    # skip the magicBytes
    index += len(DataFrame.magicBytes)
    length += len(DataFrame.magicBytes)
    dataFrame.CRC32 = 0
    
    try:
      # read DataFrame header
      dataFrame.version         , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.totalPacketLen  , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.platform        , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.frameNumber     , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.timeCpuCycles   , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.numDetectedObj  , index = Converter.uint8_2_uint32(dataByte, index)
      dataFrame.numTLVs         , index = Converter.uint8_2_uint32(dataByte, index)
      platform: numpy.uint32 = dataFrame.platform & 0x0000ff00
      if platform == 0x00001600:
        dataFrame.subFrameNumber  , index = Converter.uint8_2_uint32(dataByte, index)
      # if log is not None:
      if True:
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.version       : {}.{}.{}.{}".format(int((dataFrame.version&0xff000000)>>24), int((dataFrame.version&0x00ff0000)>16), int((dataFrame.version&0x0000ff00)>8), int((dataFrame.version&0x000000ff))))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.totalPacketLen: {}".format(dataFrame.totalPacketLen))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.platform      : {}".format(format(dataFrame.platform, 'x')))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.frameNumber   : {}".format(dataFrame.frameNumber   ))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.timeCpuCycles : {}".format(dataFrame.timeCpuCycles ))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.numDetectedObj: {}".format(dataFrame.numDetectedObj))
        logger.log(event="DataFrame.parse", level="logging", message="DataFrame.numTLVs       : {}".format(dataFrame.numTLVs       ))
        if platform == 0x00001600:
          logger.log(event="DataFrame.parse", level="logging", message="DataFrame.subFrameNumber: {}".format(dataFrame.subFrameNumber))
      length += 32 if platform == 0x00001600 else 28
      logger.log(event="DataFrame.parse", level="logging", message="length: {}".format(length))

      # check length of dataByte is enough
      # NOTE: when all item of `guiMonitor` is enabled, TLV only can get first 4 items
      # NOTE: The built-in buffer of serial(use `pyserial-3.5`) is only about 12kB, but rangeAzimuthHeatMap and rangeDopplerHeatMap may each occupy about 8kB
      if index + dataFrame.totalPacketLen - len(DataFrame.magicBytes) - length > len(dataByte):
        logger.log(event="DataFrame.parse", level="Error", message="DataFrame is incomplete (index + total Packet Length - magicBytes length - length > length of dataByte)): {} + {} - {} - {} < {}\n{}".format(index, dataFrame.totalPacketLen, len(DataFrame.magicBytes), (32 if platform == 0x00001600 else 28), len(dataByte), dataByte))
        return None, None

      # record contents argument
      numRangeBins:      numpy.uint32 | None = None
      numVirtualAntAzim: numpy.uint32 | None = None
      numDopplerBins:    numpy.uint32 | None = None

      # read DataFrame contents
      for TLV_index in range(dataFrame.numTLVs):

        # read TLV header
        TLV_TypeId, index = Converter.uint8_2_uint32(dataByte, index)
        TLV_Length, index = Converter.uint8_2_uint32(dataByte, index) # bytes length of contents
        if log is not None:
          logger.log(event="DataFrame.parse", level="logging", message="DataFrame.TLV[{}].TypeId: {}".format(TLV_index, TLV_TypeId))
          logger.log(event="DataFrame.parse", level="logging", message="DataFrame.TLV[{}].Length: {}".format(TLV_index, TLV_Length))

        # parse TLV: detectedObjects
        if TLV_TypeId == 1:
          # parse detectedObjects header
          dataFrame.detectedObjects.infomation.numDetetedObj, index = Converter.uint8_2_uint16(dataByte, index)
          dataFrame.detectedObjects.infomation.xyzQFormat   , index = Converter.uint8_2_uint16(dataByte, index)
          if log is not None:
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.infomation.numDetetedObj: {}".format(dataFrame.detectedObjects.infomation.numDetetedObj)) # TODO: check this with `dataFrame.data.numDetectedObj`
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.infomation.xyzQFormat   : {}".format(dataFrame.detectedObjects.infomation.xyzQFormat   ))
          # parse detectedObjects list
          dataFrame.detectedObjects.Objects = []
          for DetetedObj_index in range(dataFrame.detectedObjects.infomation.numDetetedObj):
            rangeIdx  , index = Converter.uint8_2_uint16(dataByte, index)
            dopplerIdx, index = Converter.uint8_2_int16(dataByte, index)
            peakVal   , index = Converter.uint8_2_uint16(dataByte, index)
            x         , index = Converter.uint8_2_int16(dataByte, index)
            y         , index = Converter.uint8_2_int16(dataByte, index)
            z         , index = Converter.uint8_2_int16(dataByte, index)
            dataFrame.detectedObjects.Objects.append(dataFrame.detectedObjects.DetectedObj(rangeIdx, dopplerIdx, peakVal, x, y, z))
            if log is not None: logger.log(event="DataFrame.parse", level="logging", message="DataFrame.detectedObjects.Objects[{index:{index_log10}d}]: ({rangeIdx:3d}, {dopplerIdx:3d}, {peakVal:3d}, {x:5d}, {y:5d}, {z:5d}) -> ({xQFormat:8.4f}, {yQFormat:8.4f}, {zQFormat:8.4f})".format(
              index=DetetedObj_index, 
              index_log10=int(math.log10(dataFrame.detectedObjects.infomation.numDetetedObj))+1, 
              rangeIdx=rangeIdx, dopplerIdx=dopplerIdx, peakVal=peakVal, x=x, y=y, z=z, 
              xQFormat=Converter.QFormat.parse(dataFrame.detectedObjects.infomation.xyzQFormat, x), 
              yQFormat=Converter.QFormat.parse(dataFrame.detectedObjects.infomation.xyzQFormat, y), 
              zQFormat=Converter.QFormat.parse(dataFrame.detectedObjects.infomation.xyzQFormat, z)))
          # check TLV length
          if 4 + (dataFrame.detectedObjects.infomation.numDetetedObj * 12) != TLV_Length: 
            logger.log(event="DataFrame.parse.TLV", level="Warn", message="TLV(`detectedObjects`) length mismatch")
          length += 8 + 4 + (dataFrame.detectedObjects.infomation.numDetetedObj * 12)
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # parse TLV: logMagRange
        elif TLV_TypeId == 2:
          # parse logMagRange
          dataFrame.logMagRange.logMagRange = list()
          numRangeBins = TLV_Length//2
          for _ in range(numRangeBins):
            _logMagRange, index = Converter.uint8_2_uint16(dataByte, index)
            dataFrame.logMagRange.logMagRange.append(_logMagRange)
          if log is not None: logger.log(event="DataFrame.parse", level="logging", message="DataFrame.logMagRange: {}".format(dataFrame.logMagRange.logMagRange))
          length += 8 + TLV_Length
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # parse TLV: noiseProfile
        elif TLV_TypeId == 3:
          dataFrame.noiseProfile.noiseProfile = list()
          numRangeBins = TLV_Length//2
          for _ in range(numRangeBins):
            _noiseProfile, index = Converter.uint8_2_uint16(dataByte, index)
            dataFrame.noiseProfile.noiseProfile.append(_noiseProfile)
          if log is not None: logger.log(event="DataFrame.parse", level="logging", message="DataFrame.noiseProfile: {}".format(dataFrame.noiseProfile.noiseProfile))
          length += 8 + TLV_Length
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # parse TLV: rangeAzimuthHeatMap
        elif TLV_TypeId == 4:
          dataFrame.rangeAzimuthHeatMap.rangeAzimuthHeatMap = list()
          dataFrame.rangeAzimuthHeatMap.numRangeBins = numRangeBins
          if numRangeBins is not None: # TODO: Restructure this paragraph
            numVirtualAntAzim = (TLV_Length//4) // numRangeBins
            dataFrame.rangeAzimuthHeatMap.numVirtualAntAzim = numVirtualAntAzim
            for _ in range(numRangeBins): # TODO: unconfirmed is `numRangeBins` or `numVirtualAntAzim`
              _numRangeBins = list()
              for _ in range(numVirtualAntAzim): # TODO: unconfirmed is `numRangeBins` or `numVirtualAntAzim`
                imag, index = Converter.uint8_2_int16(dataByte, index)
                real, index = Converter.uint8_2_int16(dataByte, index)
                _numRangeBins.append(DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe(imag, real))
              dataFrame.rangeAzimuthHeatMap.rangeAzimuthHeatMap.append(copy.deepcopy(_numRangeBins))
          else:
            for _ in range(TLV_Length//4):
              imag, index = Converter.uint8_2_int16(dataByte, index)
              real, index = Converter.uint8_2_int16(dataByte, index)
              dataFrame.rangeAzimuthHeatMap.rangeAzimuthHeatMap.append(DataFrame.RangeAzimuthHeatMap.Cmplx16ImRe(imag, real))
          if log is not None: logger.log(event="DataFrame.parse", level="logging", message="DataFrame.rangeAzimuthHeatMap: {}".format(str(dataFrame.rangeAzimuthHeatMap)))
          length += 8 + TLV_Length
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # parse TLV: rangeDopplerHeatMap
        elif TLV_TypeId == 5:
          dataFrame.rangeDopplerHeatMap.rangeDopplerHeatMap = list()
          dataFrame.rangeDopplerHeatMap.numRangeBins = numRangeBins
          if numRangeBins is not None: # TODO: Restructure this paragraph
            numDopplerBins = (TLV_Length//2) // numRangeBins
            dataFrame.rangeDopplerHeatMap.numDopplerBins = numDopplerBins
            for _ in range(numRangeBins): # TODO: unconfirmed is `numRangeBins` or `numDopplerBins`
              _numRangeBins = list()
              for _ in range(numDopplerBins): # TODO: unconfirmed is `numRangeBins` or `numDopplerBins`
                _rangeDopplerHeatMap, index = Converter.uint8_2_uint16(dataByte, index)
                _numRangeBins.append(_rangeDopplerHeatMap)
              dataFrame.rangeDopplerHeatMap.rangeDopplerHeatMap.append(copy.deepcopy(_numRangeBins))
          else:
            for _ in range(TLV_Length//4):
              _rangeDopplerHeatMap, index = Converter.uint8_2_uint16(dataByte, index)
              dataFrame.rangeDopplerHeatMap.rangeDopplerHeatMap.append(_rangeDopplerHeatMap)
          if log is not None: logger.log(event="DataFrame.parse", level="logging", message="DataFrame.rangeDopplerHeatMap: {}".format(dataFrame.rangeDopplerHeatMap.rangeDopplerHeatMap))
          length += 8 + TLV_Length
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # parse TLV: statsInfo
        elif TLV_TypeId == 6:
          dataFrame.statsInfo.interFrameProcessingTime  , index = Converter.uint8_2_uint32(dataByte, index)
          dataFrame.statsInfo.transmitOutputTime        , index = Converter.uint8_2_uint32(dataByte, index)
          dataFrame.statsInfo.interFrameProcessingMargin, index = Converter.uint8_2_uint32(dataByte, index)
          dataFrame.statsInfo.interChirpProcessingMargin, index = Converter.uint8_2_uint32(dataByte, index)
          dataFrame.statsInfo.activeFrameCPULoad        , index = Converter.uint8_2_uint32(dataByte, index)
          dataFrame.statsInfo.interFrameCPULoad         , index = Converter.uint8_2_uint32(dataByte, index)
          if log is not None: 
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameProcessingTime  : {}".format(dataFrame.statsInfo.interFrameProcessingTime  ))
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.transmitOutputTime        : {}".format(dataFrame.statsInfo.transmitOutputTime        ))
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameProcessingMargin: {}".format(dataFrame.statsInfo.interFrameProcessingMargin))
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interChirpProcessingMargin: {}".format(dataFrame.statsInfo.interChirpProcessingMargin))
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.activeFrameCPULoad        : {}".format(dataFrame.statsInfo.activeFrameCPULoad        ))
            logger.log(event="DataFrame.parse", level="logging", message="DataFrame.statsInfo.interFrameCPULoad         : {}".format(dataFrame.statsInfo.interFrameCPULoad         ))
          length += 8 + TLV_Length
          # print("index: {}/{}".format(index, len(dataByte_uint8)))

        # deal with padding
        # Note that the padding is not in the TLV
        # # elif TLV_TypeId & 0x000000ff == 0x00000000:
        # elif dataByte[index-8] == 0x00:
        #   index -= 8
        #   while dataByte[index] == 0x00:
        #     index += 1
        #     length += 1
        #   break

        else: 
          logger.log(event="DataFrame.parse", level="Warn", message="Error TypeId: {}".format(TLV_TypeId))

      # print("index: {}/{}".format(index, len(dataByte_uint8)))

      # check dataFrame length is match (need to count parsed bytes from dataByte)
      # Note that padding may not be as expected
      # if dataFrame.totalPacketLen != length:
      #   logger.log(event="DataFrame.parse", level="Warn", message="dataFrame length mismatch (totalPacketLen != length): {} != {}\n{}".format(dataFrame.totalPacketLen, length, dataByte[index-(dataFrame.totalPacketLen-length):index-length+dataFrame.totalPacketLen]))

      # CRC32 checksum
      CRC_index = index-length
      while CRC_index < index-length+dataFrame.totalPacketLen:
        tmp, CRC_index = Converter.uint8_2_uint32(dataByte, CRC_index)
        dataFrame.CRC32 += tmp
    except Exception as exception:
      logger.log(event="DataFrame.parse", level="Warn", message="Error: {}".format(exception))
      dataFrame.CRC32 = 0
    
    # is complete DataFrame
    dataFrame.iscomplete = True if dataFrame.CRC32 != 0 else False

    return dataFrame, index-length+dataFrame.totalPacketLen