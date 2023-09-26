# %%
import time
import threading

import serial # pyserial-3.5
import numpy # numpy-1.26.0

import Log
import SerialTool
import Configuration

# %% 
# (Ctrl_port_name, Data_port_name, Ctrl_port_baudrate, Data_port_baudrate, Ctrl_file_name, Data_file_name)
class xWR14xx:

  Ctrl_port: serial.Serial | None = None
  Data_port: serial.Serial | None = None

  Ctrl_port_baudrate: int | None = None
  Data_port_baudrate: int | None = None

  State: str | None = None
  Data_port_Reading: bool | None = None

  Config: Configuration.Configuration_2_1_0 | None = None

  logger: Log.Logger | None = None

  def __init__(self, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600):

    self.Ctrl_port_baudrate = Ctrl_port_baudrate
    self.Ctrl_port = serial.Serial(port=Ctrl_port_name, baudrate=Ctrl_port_baudrate)
    SerialTool.print_serial_info(port=self.Ctrl_port, Name="Ctrl port")

    self.Data_port_baudrate = Data_port_baudrate
    self.Data_port = serial.Serial(port=Data_port_name, baudrate=Data_port_baudrate)
    SerialTool.print_serial_info(port=self.Data_port, Name="Data port")

    self.logger = Log.Logger(fileName="Log/xWR14xx.log")

    self.Config = Configuration.Configuration_2_1_0(platform="xWR14xx")

    self.State = "initialized"
    self.Data_port_Reading = False

  def __delattr__(self, __name: str) -> None:
    self.Ctrl_port.close()
    self.Data_port.close()

  def __str__(self) -> str:
    return "xWR14xx('{Ctrl_port}', '{Data_port}', {Ctrl_port_baudrate}, {Data_port_baudrate})".format(Ctrl_port=self.Ctrl_port.name, Data_port=self.Data_port.name, Ctrl_port_baudrate=self.Ctrl_port_baudrate, Data_port_baudrate=self.Data_port_baudrate)

  def configure_unit(self, command: str, wait: float | int = 0.05, echo: bool = False):
    """unit configuration

    Args:
      command (str): Configuration command
      wait (float | int, optional): Configured wait delay. Defaults to 0.1.
      echo (bool, optional): Display configuration instructions. Defaults to False.
    """
    command = command.rstrip('\n').rstrip('\r')
    self.Ctrl_port.write(command.__add__('\n').encode())

    self.Config.parse_commandParameters(command=command)
    self.logger.log(event="{}.config".format(self.__str__()), level="logging", message="command: `{command}`".format(command=command))
    if echo: print(command)

    command_main: str = command.split(' ')[0]
    if command_main == "sensorStart":
      self.State = "Sensor_Start"
    if command_main == "sensorStop":
      self.State = "Sensor_Stop"
    
    time.sleep(wait)

  def configure(self, commands: list[str] | str, wait: float | int = 0.05, echo: bool = False):
    """configuration
    Args:
      command (str): Configuration commands
      wait (float | int, optional): Configured wait delay. Defaults to 0.1.
      echo (bool, optional): Display configuration instructions. Defaults to False.
    """
    for command in commands: # Assume `commands` is list[str]
      if len(command) == 1: # `commands` is str, not list[str]
        self.configure_unit(command=commands, wait=wait, echo=echo)
        break
      self.configure_unit(command=command, wait=wait, echo=echo)
  def configure_file(self, CFG_file_name: str = "profile.cfg", wait: float | int = 0.05, echo: bool = False):
    """configuration from file

    Args:
      CFG_file_name (str): Configuration command
      wait (float | int, optional): Configured wait delay. Defaults to 0.1.
      echo (bool, optional): Display configuration instructions. Defaults to False.
    """
    with open(file=CFG_file_name, mode="r") as CFG_file:
      CFG_lines: list[str] = [CFG_line.rstrip('\r\n').__add__('\n') for CFG_line in CFG_file.readlines()]
      self.configure(commands=CFG_lines, wait=wait, echo=echo)

  def record_DataPort(self, record_file_name: str="Record/Data.bin"):
    if not self.Data_port_Reading:
      self.Data_port_Reading = True
      try:
        with open(file=record_file_name, mode='wb+') as record_file:
          while self.Data_port.in_waiting > 0:
            Data_buffer: bytes = self.Data_port.read(self.Data_port.in_waiting)
            record_file.write(Data_buffer)
      except KeyboardInterrupt:
        pass
      self.Data_port_Reading = False

# %%
if __name__ == '__main__':
  device = xWR14xx(Ctrl_port_name="COM3", Data_port_name="COM4", Ctrl_port_baudrate=115200, Data_port_baudrate=921600)
  device.configure_file(CFG_file_name="Profile\profile.cfg")
  device.configure(device.Config.command_CfarRangeThreshold_dB_1443(threshold_dB=8))
  device.configure(device.Config.command_RemoveStaticClutter())
  print("configured device")
  time.sleep(device.Config.configParameters["framePeriodicity"]/1000)
  print("start recording")
  device.record_DataPort()
# %%
