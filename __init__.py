# %%
import time
import threading
# import os

import serial # pyserial-3.5
import numpy # numpy-1.26.0

try:
  import Configuration
  import DataFrame
  import Logging
  import SerialTool
except ModuleNotFoundError:
  from Ti_mmWave_Demo_Driver import Configuration
  from Ti_mmWave_Demo_Driver import DataFrame
  from Ti_mmWave_Demo_Driver import Logging
  from Ti_mmWave_Demo_Driver import SerialTool
  __all__ = ["Configuration", "DataFrame"]
  version = 1.0

if __name__ == '__main__':
  import math
  import datetime
  import matplotlib.pyplot # matplotlib-3.8.1
  import matplotlib.collections
  import matplotlib.animation
  import IntegrationTool
  import Notify

# %% 
class Ti_mmWave:

  def __init__(self, platform: str, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600, Send_timeInterval: int | float | None = 0.025, Buffering_timeInterval: int | float | None = None, Parse_timeInterval: int | float | None = 1):

    self.platform = platform

    self.logger = Logging.Logger(fileName="Logging/Ti_mmWave.log")

    self.Ctrl_port_baudrate = Ctrl_port_baudrate
    self.Ctrl_port = serial.Serial(port=Ctrl_port_name, baudrate=Ctrl_port_baudrate)

    self.Data_port_baudrate = Data_port_baudrate
    self.Data_port = serial.Serial(port=Data_port_name, baudrate=Data_port_baudrate)
    
    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Ctrl_port, Name="Ctrl port"))
    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Data_port, Name="Data port"))

    self.buffer = bytearray()

    self.config = Configuration.Configuration_2_1_0(platform=platform)
    self.data = DataFrame.DataFrame()

    self.Send_timeInterval = Send_timeInterval

    self.State = "initialized"
    self._DataPort_inUse_ = False

    self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message="Initialization completed")
    self.sensorStop()

    # Thread Object
    self.Buffering_timeInterval = Buffering_timeInterval
    self.Buffering_active = False
    self.Buffering_thread = threading.Thread(target=self.Data_Buffering_continuous, args=(self.Buffering_timeInterval,))
    self.Parse_timeInterval = Parse_timeInterval
    self.Parse_active = False
    self.Parse_thread = threading.Thread(target=self.Data_Parse_continuous, args=(self.Parse_timeInterval,))

  # TODO: @Buffering_timeInterval.setter
  # TODO: @Parse_timeInterval.setter

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
    # self.configure_unit(commandLine="sensorStop", wait=wait, log=log)
    self.Ctrl_Send_unit(commandLine="sensorStop")
  def sensorStart(self, wait: float | int = 0.05, log: bool = False) -> None:
    """Use the command line to control the Sensor to start sensing.

    Args:
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    # self.configure_unit(commandLine="sensorStart", wait=wait, log=log)
    self.Ctrl_Send_unit(commandLine="sensorStart")

  def record_DataPort(self, record_file_name: str="Record/Data.bin") -> None:
    """Record sensing data to file

    Args:
        record_file_name (str, optional): File name. Defaults to "Record/Data.bin".
    """
    while self._DataPort_inUse_: pass # wait for dataport reading
    else: 
      self._DataPort_inUse_ = True
      try:
        with open(file=record_file_name, mode='wb+') as record_file:
          while self.Data_port.in_waiting > 0:
            Data_buffer: bytes = self.Data_port.read(self.Data_port.in_waiting)
            record_file.write(Data_buffer)
      except KeyboardInterrupt:
        pass
      self._DataPort_inUse_ = False

  def Ctrl_Load_unit(self, commandLine: str):
    commandLine = commandLine.strip()
    if commandLine[0] != '%': 
      self.config.parse_commandLine(commandLine)
      return commandLine
    else:
      return
  def Ctrl_Load(self, commandLines: list[str] | str):
    for commandLine in commandLines: # Assume `commandLines` is list[str]
      if len(commandLine) == 1: # `commandLines` is str, not list[str]
        self.Ctrl_Load_unit(commandLines)
        break
      else: self.Ctrl_Load_unit(commandLine)
  def Ctrl_Load_file(self, CFG_file_name: str = "profile.cfg"):
    with open(file=CFG_file_name, mode="r") as CFG_file:
      CFG_lines: list[str] = [CFG_line.strip() for CFG_line in CFG_file.readlines()]
      self.Ctrl_Load(CFG_lines)

  def Ctrl_Send_unit(self, commandLine: str, timeInterval: float | int | None = None):
    self.Ctrl_port.write(commandLine.strip().__add__('\n').encode())
    self.logger.log(event="{}.Ctrl_Send_unit".format(self.__str__()), level="logging", message="commandLine: `{commandLine}`".format(commandLine=commandLine))
    command: str = commandLine.split(' ')[0]
    if command == "sensorStart":
      old_State: str = self.State
      self.State = "Sensor_Start"
      if old_State != self.State: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Start")
    if command == "sensorStop":
      old_State: str = self.State
      self.State = "Sensor_Stop"
      if old_State != self.State: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Stop")
    try:
      time.sleep(timeInterval if timeInterval is not None else self.Send_timeInterval if self.Send_timeInterval is not None else 0.025)
    except Exception as exception:
      self.logger.log(event="{}.Ctrl_Send_unit".format(self.__str__()), level="logging", message="Error: `{exception}`".format(exception=exception))
  def Ctrl_Send(self, commandLines: str | None = None, timeInterval: float | int | None = None):
    if commandLines is None: commandLines = self.config.command.commandLines()
    for commandLine in commandLines: # Assume `commandLines` is list[str]
      if len(commandLine) == 1: # `commandLines` is str, not list[str]
        self.Ctrl_Send_unit(commandLines, timeInterval)
        break
      else: self.Ctrl_Send_unit(commandLine, timeInterval)

  def Data_Buffering_unit(self) -> None:
    while self._DataPort_inUse_: pass # wait for dataport reading
    else: 
      self._DataPort_inUse_ = True
      self.buffer = self.buffer + bytearray(self.Data_port.read(self.Data_port.in_waiting))
      self._DataPort_inUse_ = False
  def Data_Buffering_continuous(self, timeInterval: int | float | None = None) -> None:
    try:
      while self.Buffering_active: 
        self.Data_Buffering_unit()
        if timeInterval is not None: time.sleep(timeInterval)
        elif self.Buffering_timeInterval is not None: time.sleep(self.Buffering_timeInterval)
        else: time.sleep(self.config.parameter.framePeriodicity/10000)
    except KeyboardInterrupt:
      pass
  def Data_Buffering_thread_start(self):
    self.Buffering_active = True
    self.Buffering_thread.start()
  def Data_Buffering_thread_stop(self):
    self.Buffering_active = False

  def Data_Record_Buffer(self, record_file_name: str="Record/Data.bin", duration: int | float = 0, log: str | None = None) -> None:
    with open(file=record_file_name, mode='wb+') as record_file:
      if duration <= 0:
        record_file.write(self.buffer)
      else: 
        startTime = time.time()
        self.buffer.clear()
        # stop Buffering and Parse if needed
        Buffering_interrupt = False
        Parse_interrupt = False
        if self.Buffering_active: 
          Buffering_interrupt = True
          self.Data_Buffering_thread_stop()
        if self.Parse_active: 
          Parse_interrupt = True
          self.Data_Parse_thread_stop()
        # record
        while time.time() - startTime < duration:
          self.Data_Buffering_unit()
          record_file.write(self.buffer)
        # start Buffering and Parse if needed
        if Buffering_interrupt: self.Data_Buffering_thread_start()
        if Parse_interrupt: self.Data_Parse_thread_start()

  def Data_Parse_unit(self, log: str | None = None) -> None:
    data, index = DataFrame.DataFrame.parse(self.buffer, log)
    if data is not None: 
      self.data = data
      self.buffer = self.buffer[index:]
  def Data_Parse_continuous(self, timeInterval: int | float | None = None, log: str | None = None) -> None:
    try:
      while self.Parse_active: 
        self.Data_Parse_unit(log)
        if timeInterval is not None: time.sleep(timeInterval)
        elif self.Parse_timeInterval is not None: time.sleep(self.Parse_timeInterval)
        else: time.sleep(self.config.parameter.framePeriodicity/1000)
    except KeyboardInterrupt:
      pass
  def Data_Parse_thread_start(self):
    self.Parse_active = True
    self.Parse_thread.start()
  def Data_Parse_thread_stop(self):
    self.Parse_active = False

# %%
if __name__ == '__main__':
  device = Ti_mmWave(platform="xWR14xx", Ctrl_port_name="COM3", Data_port_name="COM4", Ctrl_port_baudrate=115200, Data_port_baudrate=921600)
  device.logger.echo = True
  device.config.logger.echo = True
  device.data.logger.echo = True
  print("configured device...")
  device.sensorStop(log=True)
  device.Ctrl_Load_file("Profile\Profile-4.cfg")
  device.config.set_CfarRangeThreshold_dB(threshold_dB=14)
  device.config.set_RemoveStaticClutter(enabled=True)
  # device.config.set_RemoveStaticClutter(enabled=False)
  device.config.set_FramePeriodicity(FramePeriodicity_ms=1000) # get as `device.config.parameter.framePeriodicity`
  device.Ctrl_Send()
  device.sensorStart(log=True)
  print("sensorStart")
  lineBot = Notify.LineBot("access_token")
  # os.system(".\LogConfiguration_2_1_0.log < ''")
  # os.system(".\LogDataFrame.log < ''")
  # os.system(".\LogTi_mmWave.log < ''")

  # def length(coordinate): return math.sqrt(sum(tuple(v**2 for v in coordinate)))
  length = lambda coordinate: math.sqrt(sum(tuple(v**2 for v in coordinate)))

  detectedPoints = []

  def update_SOP():
    print("mode `SOP` triggered")

    device.Data_Buffering_unit()
    device.Data_Parse_unit()

    if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
      detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
      detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints))
      print(detectedPoints)
      DetectionDistances = sorted([round(length(DetectedPoint), 2) for DetectedPoint in detectedPoints])
      print(DetectionDistances)
      detectedCenter: tuple[float, float, float] = (sum(detectedPoints_transposed[0]) / len(detectedPoints_transposed[0]), sum(detectedPoints_transposed[1]) / len(detectedPoints_transposed[1]), sum(detectedPoints_transposed[2]) / len(detectedPoints_transposed[2]))
      print(f"DetectionDistance: {length(detectedCenter)}, DetectedCenter: {detectedCenter}")
    
    return device.data.CRC32
  # update_SOP()

  enableCycle = (1, 10, 10)
  def update_SOP_Cycle(statusCode: tuple | None = None, enableCycle: tuple = (1, 10, 10)) -> tuple:
    print("mode `SOP with Cycle Contorl` triggered")
    statusCode: tuple = enableCycle if statusCode is None else statusCode
    try:
      statusCode = tuple(statusCode[i]-1 for i in range(len(statusCode)))

      if statusCode[0] == 0:
        device.Data_Buffering_unit()

      if statusCode[1] == 0:
        device.Data_Parse_unit()

      if statusCode[2] == 0:
        crc32: numpy.uint32 = 0
        if device.data is not None and device.data.iscomplete and device.data.CRC32 != crc32:
          detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
          detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints))
          print(detectedPoints)
          DetectionDistances = sorted([round(length(DetectedPoint), 2) for DetectedPoint in detectedPoints])
          print(DetectionDistances)
          detectedCenter: tuple[float, float, float] = (sum(detectedPoints_transposed[0]) / len(detectedPoints_transposed[0]), sum(detectedPoints_transposed[1]) / len(detectedPoints_transposed[1]), sum(detectedPoints_transposed[2]) / len(detectedPoints_transposed[2]))
          print(f"DetectionDistance: {length(detectedCenter)}, DetectedCenter: {detectedCenter}")

      statusCode = tuple(statusCode[i] if statusCode[i] != 0 else enableCycle[i] for i in range(len(statusCode)))

    except KeyboardInterrupt: 
      pass
    print("mode `SOP with Cycle Contorl` is stopped in console")
    return statusCode
  # update_SOP_Cycle()

  def update_continuous_SOP_Cycle():
    print("mode `SOP with Cycle Contorl` is starting in console...")
    try:
      interval: int | float = (device.config.parameter.framePeriodicity/1000)/10
      enableCycle = (1, 10, 10)
      statusCode = enableCycle

      while True:
        time.sleep(interval)
        statusCode = tuple(statusCode[i]-1 for i in range(len(statusCode)))

        if statusCode[0] == 0:
          device.Data_Buffering_unit()
          # print("device.buffer.length:", len(device.buffer))

        if statusCode[1] == 0:
          device.Data_Parse_unit()
          # print("device.buffer.length:", len(device.buffer))

        if statusCode[2] == 0:
          crc32: numpy.uint32 = 0
          if device.data is not None and device.data.iscomplete and device.data.CRC32 != crc32:
            detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
            detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
            print(detectedPoints)
            DetectionDistances = sorted([round(length(DetectedPoint), 2) for DetectedPoint in detectedPoints])
            print(DetectionDistances)
            detectedCenter: tuple[float, float, float] = (sum(detectedPoints_transposed[0]) / len(detectedPoints_transposed[0]), sum(detectedPoints_transposed[1]) / len(detectedPoints_transposed[1]), sum(detectedPoints_transposed[2]) / len(detectedPoints_transposed[2]))
            print(f"DetectionDistance: {length(detectedCenter)}, DetectedCenter: {detectedCenter}")

        statusCode = tuple(statusCode[i] if statusCode[i] != 0 else enableCycle[i] for i in range(len(statusCode)))

    except KeyboardInterrupt: 
      pass
    print("mode `SOP with Cycle Contorl` is stopped in console")
    return
  # update_continuous_SOP_Cycle()

  def update_continuous_Threading() -> None:
    print("mode `Threading` is starting in console...")
    try:
      device.Data_Buffering_thread_start()
      device.Data_Parse_thread_start()

      while True:
        time.sleep(device.config.parameter.framePeriodicity/1000)
        # print("device.buffer.length:", len(device.buffer))
        crc32: numpy.uint32 = 0
        if device.data is not None and device.data.iscomplete and device.data.CRC32 != crc32:
          detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
          detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
          print(detectedPoints)
          DetectionDistances = sorted([round(length(DetectedPoint), 2) for DetectedPoint in detectedPoints])
          print(DetectionDistances)
          detectedCenter: tuple[float, float, float] = (sum(detectedPoints_transposed[0]) / len(detectedPoints_transposed[0]), sum(detectedPoints_transposed[1]) / len(detectedPoints_transposed[1]), sum(detectedPoints_transposed[2]) / len(detectedPoints_transposed[2]))
          print(f"DetectionDistance: {length(detectedCenter)}, DetectedCenter: {detectedCenter}")

    except KeyboardInterrupt: 
      device.Data_Buffering_thread_stop()
      device.Data_Parse_thread_stop()
    print("mode `Threading` is stopped in console")
    return
  # update_continuous_Threading()

  class AxisLimit_3d:
    class _AxisLimit:
      def __init__(self, min: int | float = 0, max: int | float = 1):
        self.min = min
        self.max = max
    def __init__(self, min: int | float = 0, max: int | float = 1, x_min: int | float | None = None, x_max: int | float | None = None, y_min: int | float | None = None, y_max: int | float | None = None, z_min: int | float | None = None, z_max: int | float | None = None) -> None:
      self.x = AxisLimit_3d._AxisLimit(min if x_min is None else x_min, max if x_max is None else x_max)
      self.y = AxisLimit_3d._AxisLimit(min if y_min is None else y_min, max if y_max is None else y_max)
      self.z = AxisLimit_3d._AxisLimit(min if z_min is None else z_min, max if z_max is None else z_max)

  detectionLimit = AxisLimit_3d(-1.5, 1.5, y_min=0, y_max=3)
  
  def get_detectedPoints(device: Ti_mmWave) -> list[tuple]:
    return [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]

  def update_3D():

    device.Data_Buffering_thread_start()
    device.Data_Parse_thread_start()

    def matplotlib_animation_V1(limit: int|float):
      figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()

      axes_231: matplotlib.pyplot.Axes = figure.add_subplot(231, projection='3d')
      axes_231.set_title("Detection distribution map")
      axes_231.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_231.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_231.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_231(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        scatter._offsets3d = tuple(list(x) for x in zip(*get_detectedPoints(device))) if len(get_detectedPoints(device)) != 0 else ([], [], [])
      animation_231 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_231, fargs=(axes_231.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_231.legend()

      axes_233: matplotlib.pyplot.Axes = figure.add_subplot(233, projection='3d')
      axes_233.set_title("integration V1")
      axes_233.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_233.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_233.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_233(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(get_detectedPoints(device), limit))
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_233 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_233, fargs=(axes_233.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_233.legend()

      axes_234: matplotlib.pyplot.Axes = figure.add_subplot(234, projection='3d')
      axes_234.set_title("integration V2.1")
      axes_234.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_234.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_234.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_234(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(get_detectedPoints(device), limit, 0.8))
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_234 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_234, fargs=(axes_234.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_234.legend()
      
      axes_235: matplotlib.pyplot.Axes = figure.add_subplot(235, projection='3d')
      axes_235.set_title("integration V2.2")
      axes_235.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_235.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_235.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_235(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8))
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_235 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_235, fargs=(axes_235.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_235.legend()

      axes_236: matplotlib.pyplot.Axes = figure.add_subplot(236, projection='3d')
      axes_236.set_title("integration V2.3")
      axes_236.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_236.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_236.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_236(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8, withWeight=True))
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_236 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_236, fargs=(axes_236.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_236.legend()

      axes_232: matplotlib.pyplot.Axes = figure.add_subplot(232, projection='3d')
      axes_232.set_title("integration")
      axes_232.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_232.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_232.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_232(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing([detectedPoints, 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(get_detectedPoints(device), limit)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(get_detectedPoints(device), limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8, withWeight=True)) ], limit))
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_232 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_232, fargs=(axes_232.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_232.legend()

      matplotlib.pyplot.show()

    def matplotlib_animation_V2(limit: int|float):
      figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()

      axes_121: matplotlib.pyplot.Axes = figure.add_subplot(121, projection='3d')
      axes_121.set_title("Detection distribution map")
      axes_121.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_121.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_121.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_121(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        scatter._offsets3d = tuple(list(x) for x in zip(*get_detectedPoints(device))) if len(get_detectedPoints(device)) != 0 else ([], [], [])
      animation_121 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_121, fargs=(axes_121.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_121.legend()

      axes_122: matplotlib.pyplot.Axes = figure.add_subplot(122, projection='3d')
      axes_122.set_title("integration")
      axes_122.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_122.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_122.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_122(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing([detectedPoints, 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(get_detectedPoints(device), limit)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(get_detectedPoints(device), limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(get_detectedPoints(device), limit, 0.8, withWeight=True)) ], limit))
        print(detectedPoints_)
        print()
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_232 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_122, fargs=(axes_122.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_122.legend()

      matplotlib.pyplot.show()

    def matplotlib_animation_V3(limit: int|float):
      figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()

      axes_111: matplotlib.pyplot.Axes = figure.add_subplot(111, projection='3d')
      axes_111.set_title("integration")
      axes_111.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
      axes_111.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
      axes_111.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
      def update_matplotlibAnimation_SOP_111(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
        # os.system("cls")
        detectedPoints = get_detectedPoints(device)
        detectedPoints_ = IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing([detectedPoints, 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, limit)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8)), 
                    IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8, True))], limit))
        # print(detectedPoints, end="\n\n\n")
        # print(detectedPoints_, end="\n\n\n")
        scatter._offsets3d = tuple(list(x) for x in zip(*detectedPoints_)) if len(detectedPoints_) != 0 else ([], [], [])
      animation_111 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_111, fargs=(axes_111.scatter([], [], [], label='Detection Object'), ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
      axes_111.legend()

      matplotlib.pyplot.show()

    def matplotlib_animation_V4(limit: int|float):
      """Focus only on "x, y" coordinates
      """
      def filter_points(points, x_range, y_range, z_range):
        filtered_points = []
        if points is not None:
          for point in points:
            x, y, z = point
            if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1] and z_range[0] <= z <= z_range[1]:
              filtered_points.append(point)
        return filtered_points
      figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
      axes_111: matplotlib.pyplot.Axes = figure.add_subplot(111)
      def update_matplotlibAnimation_SOP_111(frame, axes: matplotlib.pyplot.Axes) -> matplotlib.collections.PathCollection:
        detectedPoints = filter_points(get_detectedPoints(device), [-1, 1], [0, 1.5], [-1, 1])
        detectedPoints_ = [detectedPoints]
        try:
          detectedPoints_.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, limit)))
          detectedPoints_.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, limit, 0.8)))
          detectedPoints_.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8)))
          detectedPoints_.append(IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8, True)))
        except ValueError:
          pass
        except ZeroDivisionError:
          pass

        x_range, y_range, z_range = [-1.5, 1.5], [0, 1.5], [-1, 1]

        target = filter_points(IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing(detectedPoints_, limit, useVirtualPoints=True)), x_range, y_range, z_range)

        axes.clear()
        axes.set_xlim([-.5, 1.5])
        axes.set_ylim(y_range)
        x, y, z = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        axes.scatter(x, y, color='b', alpha=0.3)
        x, y, z = tuple(list(x) for x in zip(*target)) if len(target) != 0 else ([], [], [])
        axes.scatter(x, y, color='r')
      animation_111 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_111, fargs=(axes_111, ), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)

      matplotlib.pyplot.show()

    limit = .3
    # matplotlib_animation_V1(limit)
    # matplotlib_animation_V2(limit)
    # matplotlib_animation_V3(limit)
    matplotlib_animation_V4(limit)

    device.Data_Buffering_thread_stop()
    device.Data_Parse_thread_stop()
  # update_3D()

  def detectMovement():
    device.Data_Buffering_thread_start()
    device.Data_Parse_thread_start()
    
    def filter_points(points, x_range, y_range, z_range):
      filtered_points = []
      if points is not None:
        for point in points:
          x, y, z = point
          if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1] and z_range[0] <= z <= z_range[1]:
            filtered_points.append(point)
      return filtered_points
    def nearestPoint(points: list[tuple], target_point = (0, 0, 0)):
      min_distance = float('inf')
      nearest = None
      for point in points:
        distance = IntegrationTool.Calculator.distance(target_point, point)
        if distance < min_distance:
          min_distance, nearest = distance, point
      return nearest
    def vectorOffset(target: tuple, source: tuple = (0, 0, 0)) -> tuple:
      return tuple(numpy.array(target) - numpy.array(source))
    def vectorMove(offset: tuple, source: tuple = (0, 0, 0)) -> tuple:
      return tuple(numpy.array(offset) + numpy.array(source))
    def vectorScale(source: tuple, scale) -> tuple:
      return tuple(numpy.array(source) * scale)
    def vectorPredict(current: tuple, previous: tuple = (0, 0, 0), scale = 1.0) -> tuple:
      return (vectorMove(vectorScale(vectorOffset(current, previous), -scale), previous), vectorMove(vectorScale(vectorOffset(current, previous), scale), previous))
    
    class Detected:
      # def __init__(self, device, limit = 0.5, TimeToLive = 5, predictScale = 1.5):
      #   self.device = device
      #   self.limit = limit
      #   self.TimeToLive = TimeToLive
      #   self.scale = predictScale
      #   self.ttl = self.TimeToLive
      #   self.earlier = None
      #   self.target = None
      def update_(self):
        print("Detected.update_()")
        try:
          while self.update:
            detectedPoints = get_detectedPoints(self.device)
            detectedPoints_with_clustering = [get_detectedPoints(self.device)]
            try:
              detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, self.limit)))
              detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, self.limit, 0.8)))
              detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8)))
              detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8, True)))
            except ValueError:
              pass
            except ZeroDivisionError:
              pass

            self.target = nearestPoint(filter_points(IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing(detectedPoints_with_clustering, self.limit, useVirtualPoints=True)), self.x_range, self.y_range, self.z_range))

            # detectedPoints = get_detectedPoints(self.device)
            # detectedPoints = IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing([detectedPoints, 
            #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, self.limit)), 
            #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, self.limit, 0.8)), 
            #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8)), 
            #             IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8, True))], self.limit))
            # self.target = nearestPoint(filter_points(detectedPoints),
            #             [-1, 1], [0, 2], [-1, 1])
            # print(self.ttl, self.earlier)
            # print(self.target)
            if self.target is not None:
              print("                                target is not None")
              if self.earlier is not None:
                print("                                earlier is not None")
                self.predict = vectorPredict(self.target, self.earlier, self.scale)
                if self.predict is not None and len(self.predict) == 2:
                  try:
                    print(f"                                {self.ttl}: predict: ({self.predict[0][0]:7.4f}, {self.predict[0][1]:7.4f}, {self.predict[0][2]:7.4f}), ({self.predict[1][0]:7.4f}, {self.predict[1][1]:7.4f}, {self.predict[1][2]:7.4f})")
                    if self.predict[0][1] > 0 and self.predict[1][1] < 0: # Leaving
                      print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone leaving")
                    if self.predict[0][1] < 0 and self.predict[1][1] > 0: # Entering
                      print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone entering")
                  except IndexError as indexError:
                    print(f"{indexError} {self.predict}")
              self.ttl = self.TimeToLive
              self.earlier = self.target
              # print(f"earlier: {self.earlier}")
            elif self.target is None:
              print("                                target is None")
              if self.predict is not None and len(self.predict) == 2 and self.predict[0][1] > 0 and self.predict[1][1] < 0: # Leaved
                print("                                predict is not None")
                print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone leaved")
              self.ttl = self.ttl-1 if self.ttl > 0 else self.TimeToLive
              if self.ttl <= 0:
                self.earlier =  None
                self.predict = tuple()
            # print(self.predict)
            # print()
            time.sleep(device.config.parameter.framePeriodicity/1000)
        except KeyboardInterrupt:
          pass
      def start(self):
        self.update = True
        self.updater.start()
      def stop(self):
        self.update = False
      def __init__(self, device, x_range, y_range, z_range, limit = 0.3, TimeToLive = 5, predictScale = 1.5):
        self.device = device
        self.limit = limit
        self.TimeToLive = TimeToLive
        self.scale = predictScale
        self.ttl = self.TimeToLive
        self.earlier = None
        self.predict = None
        self.target = None
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        self.updater = threading.Thread(target=self.update_)
        self.update = False
        self.start()
    # detected = Detected(device, [-1, 1], [0, 2], [-1, 1], predictScale=1.5)
    # try:
    #   while True:
    #     pass
    # except KeyboardInterrupt:
    #   pass
    # detected.stop()
    # figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
    # plot: matplotlib.pyplot.Axes = figure.add_subplot(111)
    # def update_matplotlibAnimation_SOP_111(frame, plot: matplotlib.pyplot.Axes, target, predict) -> matplotlib.collections.PathCollection:
    #   plot.clear()
    #   plot.set_xlim([-5, 5])
    #   plot.set_ylim([0, 5])
    #   if predict is not None and len(predict) == 2:
    #     plot.scatter([predict[0][0], predict[1][0]], [predict[0][1], predict[1][1]], color='r')
    #     print(f"scatter: ({predict[0][0]:7.4f}, {predict[0][1]:7.4f}, {predict[0][2]:7.4f}), ({predict[1][0]:7.4f}, {predict[1][1]:7.4f}, {predict[1][2]:7.4f})")
    #     if target is not None:
    #       offset = vectorOffset(predict[1], target)
    #       plot.arrow(target[0], target[1], offset[0], offset[1])
    # animation_111 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_111, fargs=(plot, detected.target, detected.predict), interval=device.config.parameter.framePeriodicity, cache_frame_data=False)
    # matplotlib.pyplot.show()

    limit = 0.3
    # x_range, y_range, z_range = [-.5, .5], [0, .5], [-.5, .5]
    x_range, y_range, z_range = [-1.5, 1.5], [0, 1], [-1, 1]
    earlier = None
    scale = 1
    predict = None
    TimeToLive = 5
    ttl = 0
    try:
      while True:
        detectedPoints = filter_points(get_detectedPoints(device), x_range, y_range, z_range)
        # print(f"{Logging.formatted_time(datetime.timezone.utc, '%Y-%m-%d %H:%M:%S.%f')}: [{detectedPoints}]")
        detectedPoints_with_clustering = [detectedPoints]
        try:
          detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, limit)))
          detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, limit, 0.8)))
          detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8)))
          detectedPoints_with_clustering.append(IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, limit, 0.8, True)))
        except ValueError:
          pass
        except ZeroDivisionError:
          pass

        target = nearestPoint(filter_points(IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing(detectedPoints_with_clustering, limit, useVirtualPoints=True)), x_range, y_range, z_range))

        # detectedPoints = get_detectedPoints(self.device)
        # detectedPoints = IntegrationTool.Calculator.cluster_centers(IntegrationTool.pairing([detectedPoints, 
        #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V1(detectedPoints, self.limit)), 
        #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_1(detectedPoints, self.limit, 0.8)), 
        #             IntegrationTool.Calculator.cluster_centers(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8)), 
        #             IntegrationTool.Calculator.cluster_centers_of_gravity(IntegrationTool.clustering_V2_2(detectedPoints, self.limit, 0.8, True))], self.limit))
        # self.target = nearestPoint(filter_points(detectedPoints),
        #             [-1, 1], [0, 2], [-1, 1])
        # print(self.ttl, self.earlier)
        # print(self.target)
        if target is not None:
          # print("                                target is not None")
          ttl = TimeToLive
          if earlier is not None:
            # print("                                earlier is not None")
            predict = vectorPredict(target, earlier, scale)
            if predict is not None and len(predict) == 2:
              try:
                # print(f"{Logging.formatted_time(datetime.timezone.utc, '%Y-%m-%d %H:%M:%S.%f')}: {ttl}: ({predict[0][0]:7.4f}, {predict[0][1]:7.4f}, {predict[0][2]:7.4f}), ({target[0]:7.4f}, {target[1]:7.4f}, {target[2]:7.4f}), ({predict[1][0]:7.4f}, {predict[1][1]:7.4f}, {predict[1][2]:7.4f})")
                print(f"{Logging.formatted_time(datetime.timezone.utc, '%Y-%m-%d %H:%M:%S.%f')}: {ttl}: ({target[0]:5.2f}, {target[2]:5.2f}, {target[1]:5.2f})")
                # if predict[0][0] > 0 and predict[1][0] < 0: # Leaving
                if earlier[0] > 0 and target[0] < 0: # Leaving
                  lineBot.multicast(["Uf91628cf84ce7d9dcf7cb355dc8d4102"], "有人離開了工作區")
                  print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone leaving")
                # if predict[0][0] < 0 and predict[1][0] > 0: # Entering
                if earlier[0] < 0 and target[0] > 0: # Entering
                  lineBot.multicast(["Uf91628cf84ce7d9dcf7cb355dc8d4102"], "有人進入了工作區")
                  print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone entering")
              except IndexError as indexError:
                print(f"{indexError} {predict}")
          earlier = target
        elif target is None:
          # print("                                target is None")
          print(f"{Logging.formatted_time(datetime.timezone.utc, '%Y-%m-%d %H:%M:%S.%f')}: {ttl}: {'---------------------' if ttl>0 else ''}")
          # if predict is not None and len(predict) == 2 and predict[0][0] > 0 and predict[1][0] < 0: # Leaved
          #   # print("                                predict is not None")
          #   print(Logging.formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), "someone leaved")
          ttl = ttl-1 if ttl > 0 else 0
          if ttl <= 0:
            earlier =  None
            predict = tuple()
        time.sleep(device.config.parameter.framePeriodicity/1000)
    except KeyboardInterrupt:
      pass

    device.Data_Buffering_thread_stop()
    device.Data_Parse_thread_stop()
  # detectMovement()
  
  update_3D()
  # detectMovement()
  del device
# %%
