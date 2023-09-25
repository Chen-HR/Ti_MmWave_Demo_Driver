# %%
import time
import serial
import serial.tools.list_ports
import threading

import Log
import SerialTool
import Configuration

# %% 
# (Ctrl_port_name, Data_port_name, Ctrl_port_baudrate, Data_port_baudrate, Ctrl_file_name, Data_file_name)
class AWR1443BOOST:
  Ctrl_port: serial.Serial | None = None
  Data_port: serial.Serial | None = None
  Config: Configuration.Configuration_2_1_0 | None = None
  logger_config: Log.Logger | None = None
  # logger_parse:  Log.Logger | None = None
  def __init__(self, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600):
    self.Ctrl_port = serial.Serial(port=Ctrl_port_name, baudrate=Ctrl_port_baudrate)
    self.Data_port = serial.Serial(port=Data_port_name, baudrate=Data_port_baudrate)
    SerialTool.print_serial_info(port=self.Ctrl_port, Name="Ctrl port")
    SerialTool.print_serial_info(port=self.Data_port, Name="Data port")
    self.logger_config = Log.Logger(fileName="config.log")
    # self.logger_parse = Log.Logger(fileName="parse.log")
    self.Config = Configuration.Configuration_2_1_0(platform="xWR1443")
    
  def __delattr__(self, __name: str) -> None:
    self.Ctrl_port.close()
    self.Data_port.close()

  def configure_unit(self, command: str, wait: float | int = 0.05, echo: bool = False):
    """unit configuration

    Args:
      command (str): Configuration command
      wait (float | int, optional): Configured wait delay. Defaults to 0.1.
      echo (bool, optional): Display configuration instructions. Defaults to False.
    """
    self.Ctrl_port.write(command.rstrip('\r\n').__add__('\n').encode())
    self.logger_config.log(command)
    self.Config.parse_commandParameters_1443(command)
    if echo: print(command.rstrip('\n').rstrip('\r'))
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
    for cfg_key in self.Config.commandParameters.keys():
      print(cfg_key)
      
# %%
if __name__ == '__main__':
  device = AWR1443BOOST(
    Ctrl_port_name="COM3", 
    Data_port_name="COM4", 
    Ctrl_port_baudrate=115200, 
    Data_port_baudrate=921600
    )
  device.configure_file(echo=True)
# %%
