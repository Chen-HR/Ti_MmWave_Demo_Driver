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
  from . import Configuration
  from . import DataFrame
  from . import Logging
  from . import SerialTool
  __all__ = ["Configuration", "DataFrame"]
  version = 1.0

if __name__ == '__main__':
  import math
  import datetime

# %% 
class Ti_mmWave:

  def __init__(self, platform: str, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600, Send_timeInterval: int | float | None = 0.025, Buffering_timeInterval: int | float | None = 0.05, Parse_timeInterval: int | float | None = 0.2, log_file: str | None = None, log_echo: bool = False, log_enable: bool = False):

    self.platform = platform

    self.log_enable = log_enable
    if self.log_enable: self.logger = Logging.Logger(log_file if log_file is not None else "Log/Ti_mmWave.log", log_echo)

    self.Ctrl_port_baudrate = Ctrl_port_baudrate
    self.Ctrl_port = serial.Serial(port=Ctrl_port_name, baudrate=Ctrl_port_baudrate)

    self.Data_port_baudrate = Data_port_baudrate
    self.Data_port = serial.Serial(port=Data_port_name, baudrate=Data_port_baudrate)

    if self.log_enable: self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Ctrl_port, Name="Ctrl port"))
    if self.log_enable: self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message=SerialTool.serial_info(port=self.Data_port, Name="Data port"))

    self.buffer = bytearray()

    self.config = Configuration.Configuration_2_1_0(platform=platform)
    self.data = DataFrame.DataFrame()

    self.Send_timeInterval = Send_timeInterval

    # Thread Object
    self.Buffering_timeInterval = Buffering_timeInterval
    self.Buffering_active = False
    self.Buffering_thread = threading.Thread(target=self.Data_Buffering_continuous, args=(self.Buffering_timeInterval,))
    self.Parse_timeInterval = Parse_timeInterval
    self.Parse_active = False
    self.Parse_thread = threading.Thread(target=self.Data_Parse_continuous, args=(self.Parse_timeInterval,))
    self.crc32: numpy.uint32 | None = None

    self.State = "initialized"
    self._DataPort_inUse_ = False

    if self.log_enable: self.logger.log(event="{}.initializing".format(self.__str__()), level="infomation", message="Initialization completed")
    self.sensorStop()

  # TODO: @Buffering_timeInterval.setter
  # TODO: @Parse_timeInterval.setter

  def __del__(self):
    if self.log_enable: self.logger.log(event="{}.deleting".format(self.__str__()), level="infomation", message="Delete device...")
    self.Ctrl_port.close()
    self.Data_port.close()
    self.sensorStop()
    if self.log_enable: self.logger.log(event="{}.deleting".format(self.__str__()), level="infomation", message="Delete completed")

  def __str__(self) -> str:
    return "Ti_mmWave('{platform}', '{Ctrl_port}', '{Data_port}', {Ctrl_port_baudrate}, {Data_port_baudrate})".format(platform=self.platform, Ctrl_port=self.Ctrl_port.name, Data_port=self.Data_port.name, Ctrl_port_baudrate=self.Ctrl_port_baudrate, Data_port_baudrate=self.Data_port_baudrate)
  
  # TODO: support `with mmWave(...) as mmWaveDevice:`

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
    if self.log_enable: self.logger.log(event="{}.configure_unit".format(self.__str__()), level="logging", message="commandLine: `{commandLine}`".format(commandLine=commandLine))

    command: str = commandLine.split(' ')[0]
    if command == "sensorStart":
      old_State: str = self.State
      self.State = "Sensor_Start"
      if old_State != self.State and self.log_enable: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Start")
    if command == "sensorStop":
      old_State: str = self.State
      self.State = "Sensor_Stop"
      if old_State != self.State and self.log_enable: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Stop")
    
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
    if self.State != "Sensor_Stop": 
      self.Data_Buffering_thread_stop()
      self.Data_Parse_thread_stop()
      self.Ctrl_Send_unit(commandLine="sensorStop")
  def sensorStart(self, wait: float | int = 0.05, log: bool = False) -> None:
    """Use the command line to control the Sensor to start sensing.

    Args:
      wait (float | int, optional): Configured wait delay. Defaults to 0.05.
      log (bool, optional): log configuration instructions. Defaults to False.
    """
    # self.configure_unit(commandLine="sensorStart", wait=wait, log=log)
    if self.State != "Sensor_Start": 
      self.Ctrl_Send_unit(commandLine="sensorStart")
      self.Data_Buffering_thread_start()
      self.Data_Parse_thread_start()

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
    if self.log_enable: self.logger.log(event="{}.Ctrl_Send_unit".format(self.__str__()), level="logging", message="commandLine: `{commandLine}`".format(commandLine=commandLine))
    command: str = commandLine.split(' ')[0]
    if command == "sensorStart":
      old_State: str = self.State
      self.State = "Sensor_Start"
      if old_State != self.State and self.log_enable: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Start")
    if command == "sensorStop":
      old_State: str = self.State
      self.State = "Sensor_Stop"
      if old_State != self.State and self.log_enable: self.logger.log(event="{}.stateChanged".format(self.__str__()), level="logging", message="Sensor Stop")
    try:
      time.sleep(timeInterval if timeInterval is not None else self.Send_timeInterval if self.Send_timeInterval is not None else 0.025)
    except Exception as exception:
      if self.log_enable: self.logger.log(event="{}.Ctrl_Send_unit".format(self.__str__()), level="logging", message="Error: `{exception}`".format(exception=exception))
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
        elif self.Buffering_timeInterval is not None: time.sleep(self.config.parameter.framePeriodicity*self.Buffering_timeInterval)
        else: time.sleep(self.config.parameter.framePeriodicity/10000)
    except KeyboardInterrupt:
      pass
  def Data_Buffering_thread_start(self):
    self.Buffering_active = True
    self.Buffering_thread.start()
  def Data_Buffering_thread_stop(self):
    self.Buffering_active = False

  def Data_Record_Buffer(self, record_file_name: str="Record/Data.bin", duration: int | float = 0) -> None:
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
      # print(f"[{datetime.datetime.now()}] Data_Parse_unit")
  def Data_Parse_continuous(self, timeInterval: int | float | None = None, log: str | None = None) -> None:
    try:
      while self.Parse_active: 
        self.Data_Parse_unit(log)
        if timeInterval is not None: time.sleep(timeInterval)
        elif self.Parse_timeInterval is not None: time.sleep(self.config.parameter.framePeriodicity*self.Parse_timeInterval)
        else: time.sleep(self.config.parameter.framePeriodicity/1000)
    except KeyboardInterrupt:
      pass
  def Data_Parse_thread_start(self):
    self.Parse_active = True
    self.Parse_thread.start()
  def Data_Parse_thread_stop(self):
    self.Parse_active = False

  def set_cfarRangeThreshold_dB(self, threshold_dB: int | float):
    self.config.set_CfarRangeThreshold_dB(threshold_dB)
  def set_removeStaticClutter(self, enabled: bool):
    self.config.set_RemoveStaticClutter(enabled)
  def set_framePeriodicity(self, FramePeriodicity_ms: int | float):
    self.config.set_FramePeriodicity(FramePeriodicity_ms)
  def get_detectedPoints(self, wait_new: bool = False) -> list[tuple]:
    while wait_new and self.data.CRC32 == self.crc32: pass
    self.crc32 = self.data.CRC32
    return self.data.detectedPoints()

# %%
if __name__ == '__main__':
  class Timer:
    """Simple timer class to measure elapsed time."""
    def __init__(self):
      self.starttime = 0.0
    def start(self):
      """Start the timer."""
      self.starttime = time.time()
    def now(self):
      """Get the elapsed time since starting the timer."""
      return time.time() - self.starttime
  class AxisLimit_3d:
    class _AxisLimit:
      def __init__(self, min: int | float = 0, max: int | float = 1):
        self.min = min
        self.max = max
    def __init__(self, min: int | float = 0, max: int | float = 1, x_min: int | float | None = None, x_max: int | float | None = None, y_min: int | float | None = None, y_max: int | float | None = None, z_min: int | float | None = None, z_max: int | float | None = None) -> None:
      self.x = AxisLimit_3d._AxisLimit(min if x_min is None else x_min, max if x_max is None else x_max)
      self.y = AxisLimit_3d._AxisLimit(min if y_min is None else y_min, max if y_max is None else y_max)
      self.z = AxisLimit_3d._AxisLimit(min if z_min is None else z_min, max if z_max is None else z_max)
  detectionLimit = AxisLimit_3d(-5, 5, y_min=0, y_max=5)

  device = Ti_mmWave(platform="xWR14xx", Ctrl_port_name="COM3", Data_port_name="COM4", Ctrl_port_baudrate=115200, Data_port_baudrate=921600, Parse_timeInterval=0.5)
  print("configured device...")
  device.sensorStop()
  device.Ctrl_Load_file("Profile\Profile-4.cfg")
  device.set_cfarRangeThreshold_dB(threshold_dB=14)
  device.set_removeStaticClutter(enabled=True)
  device.set_framePeriodicity(FramePeriodicity_ms=1000) # get as `device.config.parameter.framePeriodicity`
  device.Ctrl_Send()
  device.sensorStart()

  try:
    print("Begin execution")
    def frameDelay_tester():
      timer = Timer()
      delay = list()
      timer.start()
      try:
        while True:
          detectedPoints = device.get_detectedPoints(True)
          delay_ = device.config.parameter.framePeriodicity - float(timer.now())
          timer.start()
          print(f"[{datetime.datetime.now()}] frame.delay: {delay_: 9.4f}, frame.detectedPoints: {detectedPoints}")
          delay.append(delay_)
      except KeyboardInterrupt:
        print(f"[{datetime.datetime.now()}] frame.delay.average: {sum(delay)/len(delay): 9.4f}")
    frameDelay_tester()
  except KeyboardInterrupt:
    pass
  finally:
    print("End execution")

  print("free device...")
  device.sensorStop()
  del device

# %%
