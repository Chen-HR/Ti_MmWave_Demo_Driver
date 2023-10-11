# %%
import time
import math
import threading

import serial # pyserial-3.5
import numpy # numpy-1.26.0

import Log
import SerialTool

import Configuration
import DataFrame

# %% 
class Ti_mmWave:

  def __init__(self, platform: str, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600):

    self.platform = platform

    self.logger = Log.Logger(fileName="Log/Ti_mmWave.log")

    self.Ctrl_port_baudrate = Ctrl_port_baudrate
    self.Ctrl_port = serial.Serial(port=Ctrl_port_name, baudrate=Ctrl_port_baudrate)

    self.Data_port_baudrate = Data_port_baudrate
    self.Data_port = serial.Serial(port=Data_port_name, baudrate=Data_port_baudrate)
    
    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Ctrl_port, Name="Ctrl port"))
    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Data_port, Name="Data port"))

    self.buffer = bytearray()

    self.config = Configuration.Configuration_2_1_0(platform=platform)
    self.data = DataFrame.DataFrame()

    self.State = "initialized"
    self.Data_port_Reading = False

    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message="Initialization completed")
    self.sensorStop()

  def __del__(self) -> None:
    self.logger.log(event="{}.deleting".format(self.__str__()), level="infomation", message="Delete device...")
    self.sensorStop()
    self.Ctrl_port.close()
    self.Data_port.close()
    self.logger.log(event="{}.deleting".format(self.__str__()), level="infomation", message="Delete completed")

  def __str__(self) -> str:
    return "Ti_mmWave('{platform}', '{Ctrl_port}', '{Data_port}', {Ctrl_port_baudrate}, {Data_port_baudrate})".format(platform=self.platform, Ctrl_port=self.Ctrl_port.name, Data_port=self.Data_port.name, Ctrl_port_baudrate=self.Ctrl_port_baudrate, Data_port_baudrate=self.Data_port_baudrate)

  def configure_unit(self, commandLine: str, wait: float | int = 0.05, log: bool = False):
    """unit configuration

    Args:
      commandLine (str): Configuration commandLine
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    commandLine = commandLine.strip()
    self.Ctrl_port.write(commandLine.__add__('\n').encode())

    self.config.parse_commandLine(commandLine=commandLine)
    if log: self.logger.log(event="{}.configure_unit".format(self.__str__()), level="logging", message="commandLine: `{commandLine}`".format(commandLine=commandLine))

    command: str = commandLine.split(' ')[0]
    if command == "sensorStart":
      old_State: str = self.State
      self.State = "Sensor_Start"
      if old_State != self.State: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Start")
    if command == "sensorStop":
      old_State: str = self.State
      self.State = "Sensor_Stop"
      if old_State != self.State: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Stop")
    
    time.sleep(wait)

  def configure(self, commandLines: list[str] | str | None = None, wait: float | int = 0.05, log: bool = False):
    """configuration

    Args:
        commandLines (list[str] | str | None, optional): Configuration commandLines. Defaults to None, it will use self.config data.
        wait (float | int, optional): Configured wait delay. Defaults to 0.05.
        log (bool, optional): log configuration instructions. Defaults to False.
    """
    if commandLines == None:
      for commandLine in self.config.command.commandLines():
        self.configure_unit(commandLine=commandLine, wait=wait, log=log)
    else: 
      for commandLine in commandLines: # Assume `commandLines` is list[str]
        if len(commandLine) == 1: # `commandLines` is str, not list[str]
          self.configure_unit(commandLine=commandLines, wait=wait, log=log)
          break
        self.configure_unit(commandLine=commandLine, wait=wait, log=log)
  def configure_file(self, CFG_file_name: str = "profile.cfg", wait: float | int = 0.05, log: bool = False):
    """configuration from file

    Args:
      CFG_file_name (str): Configuration command
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    with open(file=CFG_file_name, mode="r") as CFG_file:
      CFG_lines: list[str] = [CFG_line.strip() for CFG_line in CFG_file.readlines()]
      self.configure(commandLines=CFG_lines, wait=wait, log=log)

  def sensorStop(self, wait: float | int = 0.05, log: bool = False) -> None:
    """Use the command line to control the Sensor to stops sensing.

    Args:
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    self.configure_unit(commandLine="sensorStop", wait=wait, log=log)
  def sensorStart(self, wait: float | int = 0.05, log: bool = False) -> None:
    """Use the command line to control the Sensor to start sensing.

    Args:
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    self.configure_unit(commandLine="sensorStart", wait=wait, log=log)

  def record_DataPort(self, record_file_name: str="Record/Data.bin") -> None:
    """Record sensing data to file

    Args:
        record_file_name (str, optional): File name. Defaults to "Record/Data.bin".
    """
    while self.Data_port_Reading: pass # wait for dataport reading
    else: 
      self.Data_port_Reading = True
      try:
        with open(file=record_file_name, mode='wb+') as record_file:
          while self.Data_port.in_waiting > 0:
            Data_buffer: bytes = self.Data_port.read(self.Data_port.in_waiting)
            record_file.write(Data_buffer)
      except KeyboardInterrupt:
        pass
      self.Data_port_Reading = False

  def parse_DataPort(self, log: bool=False) -> None:
    """Parse sensed data.

    Experimental product, has been moved to `self.parseData()`.

    Args:
      log (bool, optional): logging parsing process. Defaults to False.
    """
    self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))
    buffer_uint8: numpy.NDArray[numpy.uint8] = numpy.frombuffer(buffer=self.buffer, dtype=numpy.uint8)
    BASE_NUMBER_OF_BITS = 8
    index: int | None = None
    
    margeUint8_array = lambda num_of_uint8: [2**(8*i) for i in range(num_of_uint8)]
    margeUint8 = lambda uint8_1DArray, index, N: (numpy.matmul(uint8_1DArray[index:index+N],margeUint8_array(N)), index+N)
    uint8_2_uintN = lambda uint8_1DArray, index, N: (numpy.matmul(uint8_1DArray[index:index+(N/8)],margeUint8_array((N/8))), index+(N/8))
    uint8_2_uint16 = lambda uint8_1DArray, index: (numpy.uint16(numpy.matmul(uint8_1DArray[index:index+2],margeUint8_array(2))), index+2)
    uint8_2_uint32 = lambda uint8_1DArray, index: (numpy.uint32(numpy.matmul(uint8_1DArray[index:index+4],margeUint8_array(4))), index+4)
    uint8_2_uint64 = lambda uint8_1DArray, index: (numpy.uint64(numpy.matmul(uint8_1DArray[index:index+8],margeUint8_array(8))), index+8)
    uint8_2_int16 = lambda uint8_1DArray, index: (numpy.int16(numpy.matmul(uint8_1DArray[index:index+2],margeUint8_array(2))), index+2)
    uint8_2_int32 = lambda uint8_1DArray, index: (numpy.int32(numpy.matmul(uint8_1DArray[index:index+4],margeUint8_array(4))), index+4)

    QFormat = lambda Q, value: value / (2**Q)
    # find the location of magicWords
    dataFrame_startIndex = -1
    for startIndex in numpy.where(buffer_uint8 == self.data.magicWords[0])[0]:
      # for magicWord_Index in range(1, len(self.data.magicWords)):
      if numpy.all(buffer_uint8[startIndex:startIndex+BASE_NUMBER_OF_BITS] == numpy.array(self.data.magicWords, dtype=numpy.uint8)):
        dataFrame_startIndex = startIndex
        break # add this line to get the first data frame, else to get the last data frame (Wrong:)
    self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="")

    # Remove redundant data before location of magicWords
    self.buffer = self.buffer[dataFrame_startIndex*BASE_NUMBER_OF_BITS:] # Warning: uncheck
    buffer_uint8 = buffer_uint8[dataFrame_startIndex:]

    index = len(self.data.magicWords)
    # read DataFrame header
    self.data.version         , index = uint8_2_uint32(buffer_uint8, index)
    self.data.totalPacketLen  , index = uint8_2_uint32(buffer_uint8, index)
    self.data.platform        , index = uint8_2_uint32(buffer_uint8, index)
    self.data.frameNumber     , index = uint8_2_uint32(buffer_uint8, index)
    self.data.timeCpuCycles   , index = uint8_2_uint32(buffer_uint8, index)
    self.data.numDetectedObj  , index = uint8_2_uint32(buffer_uint8, index)
    self.data.numTLVs         , index = uint8_2_uint32(buffer_uint8, index)
    if self.platform == "xWR16xx":
      self.data.subFrameNumber  , index = uint8_2_uint32(buffer_uint8, index)
    if log:
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.version       : {}.{}.{}.{}".format(int((self.data.version&0xff000000)>>24), int((self.data.version&0x00ff0000)>16), int((self.data.version&0x0000ff00)>8), int((self.data.version&0x000000ff))))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.totalPacketLen: {}".format(self.data.totalPacketLen))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.platform      : {}".format(format(self.data.platform, 'x')))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.frameNumber   : {}".format(self.data.frameNumber   ))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.timeCpuCycles : {}".format(self.data.timeCpuCycles ))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.numDetectedObj: {}".format(self.data.numDetectedObj))
      self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.numTLVs       : {}".format(self.data.numTLVs       ))
      if self.platform == "xWR16xx":
        self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.subFrameNumber: {}".format(self.data.subFrameNumber))
    
    for TLV_index in range(self.data.numTLVs):
      TLV_TypeId, index = uint8_2_uint32(buffer_uint8, index)
      TLV_Length, index = uint8_2_uint32(buffer_uint8, index)
      if log:
        self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.TLV[{}].TypeId: {}".format(TLV_index, TLV_TypeId))
        self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.TLV[{}].Length: {}".format(TLV_index, TLV_Length))
      if TLV_TypeId == 1:
        self.data.detectedObjects.infomation.numDetetedObj, index = uint8_2_uint16(buffer_uint8, index)
        self.data.detectedObjects.infomation.xyzQFormat   , index = uint8_2_uint16(buffer_uint8, index)
        if log:
          self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.detectedObjects.infomation.numDetetedObj: {}".format(self.data.detectedObjects.infomation.numDetetedObj)) # TODO: check this with `self.data.numDetectedObj`
          self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.detectedObjects.infomation.xyzQFormat   : {}".format(self.data.detectedObjects.infomation.xyzQFormat   ))
        self.data.detectedObjects.Objects = []
        for DetetedObj_index in range(self.data.detectedObjects.infomation.numDetetedObj):
          rangeIdx  , index = uint8_2_uint16(buffer_uint8, index)
          dopplerIdx, index = uint8_2_int16(buffer_uint8, index)
          peakVal   , index = uint8_2_uint16(buffer_uint8, index)
          x         , index = uint8_2_int16(buffer_uint8, index)
          y         , index = uint8_2_int16(buffer_uint8, index)
          z         , index = uint8_2_int16(buffer_uint8, index)
          self.data.detectedObjects.Objects.append(self.data.detectedObjects.DetectedObj(rangeIdx, dopplerIdx, peakVal, x, y, z))
          if log: self.logger.log(event="{}.updateData".format(self.__str__()), level="logging", message="self.data.detectedObjects.Objects[{index:{index_log10}d}]: ({rangeIdx:3d}, {dopplerIdx:3d}, {peakVal:3d}, {x:5d}, {y:5d}, {z:5d}) -> ({xQFormat:8.4f}, {yQFormat:8.4f}, {zQFormat:8.4f})".format(
            index=DetetedObj_index, 
            index_log10=int(math.log10(self.data.detectedObjects.infomation.numDetetedObj))+1, 
            rangeIdx=rangeIdx, 
            dopplerIdx=dopplerIdx, 
            peakVal=peakVal, 
            x=x, 
            y=y, 
            z=z, 
            xQFormat=QFormat(self.data.detectedObjects.infomation.xyzQFormat, x), 
            yQFormat=QFormat(self.data.detectedObjects.infomation.xyzQFormat, y), 
            zQFormat=QFormat(self.data.detectedObjects.infomation.xyzQFormat, z)))
        # TODO: check TLV length
      elif TLV_TypeId == 2:
        # TODO: parse logMagnitudeRange
        pass
      elif TLV_TypeId == 3:
        # TODO: parse noiseProfile
        pass
      elif TLV_TypeId == 4:
        # TODO: parse rangeAzimuthHeatMap
        pass
      elif TLV_TypeId == 5:
        # TODO: parse rangeDopplerHeatMap
        pass
      elif TLV_TypeId == 6:
        # TODO: parse statsInfo
        pass
      else: self.logger.log(event="{}.updateData".format(self.__str__()), level="Error", message="Error TypeId: {}".format(TLV_TypeId))
      # TODO: check frame length
      # TODO: clear readed frame data from `data.buffer`

  def parseData(self, log: bool=False) -> None:
    """Parse sensed data.

    Experimental product.

    TODO: Continuously loading sensing data. (Use `threading.Thread` to drive `self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))`)
    TODO: Continuously parse sensing data. (Use `threading.Thread` to drive `self.data.parse(dataByte=self.buffer, log=log)`)

    Args:
        log (bool, optional): _description_. Defaults to False.
    """
    self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))
    self.data.parse(dataByte=self.buffer, log=log)


# %%
if __name__ == '__main__':
  device = Ti_mmWave(platform="xWR14xx", Ctrl_port_name="COM3", Data_port_name="COM4", Ctrl_port_baudrate=115200, Data_port_baudrate=921600)
  device.logger.echo = True
  device.config.logger.echo = True
  device.data.logger.echo = True
  print("configured device...")
  device.configure_file(CFG_file_name="Profile\profile.cfg", log=True)
  device.sensorStart(log=True)
  device.sensorStop(log=True)
  device.config.set_CfarRangeThreshold_dB(threshold_dB=5)
  device.config.set_RemoveStaticClutter(enabled=True)
  device.config.set_FramePeriodicity(FramePeriodicity_ms=2000)
  device.configure(log=True)
  device.sensorStart(log=True)
  print("sensorStart")
  # time.sleep(device.config.parameter.framePeriodicity/1000)
  # print("record_DataPort")
  # device.record_DataPort()
  time.sleep(device.config.parameter.framePeriodicity/1000)
  # device.parse_DataPort(log=True)
  device.parseData(log=True)
  device.sensorStop(log=True)
  del device
# %%
