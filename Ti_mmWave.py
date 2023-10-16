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

  def _LoadingSensingData_(self) -> None:
    while True:
      while self.Data_port_Reading: pass # wait for dataport reading
      else: 
        self.Data_port_Reading = True
        try:
          self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))
        except KeyboardInterrupt:
          pass
        self.Data_port_Reading = False
  def _ParseSensingData_(self, log: bool=False) -> None:
    while True:
      while self.Data_port_Reading: pass # wait for dataport reading
      else: 
        self.Data_port_Reading = True
        try:
          self.data.parse(dataByte=self.buffer, log=log)
        except KeyboardInterrupt:
          pass
        self.Data_port_Reading = False

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
  time.sleep(device.config.parameter.framePeriodicity/1000)
  device.parseData(log=True)
  device.sensorStop(log=True)
  del device
# %%
