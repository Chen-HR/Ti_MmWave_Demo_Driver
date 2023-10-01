# %%
import serial
import serial.tools.list_ports
# %%
def print_serial_info(port: serial.Serial, Name: str | None=None):
  prefix: str = "  " if Name is not None else ""
  if Name: print("{Name}:".format(Name=Name))
  for port_info in serial.tools.list_ports.grep(port.portstr):
    if port_info.usb_info()        is not None: print(prefix + "usb_info()        : " + port_info.usb_info()       )
    if port_info.usb_description() is not None: print(prefix + "usb_description() : " + port_info.usb_description())
    if port_info.device            is not None: print(prefix + "device            : " + port_info.device           )
    if port_info.name              is not None: print(prefix + "name              : " + port_info.name             )
    if port_info.description       is not None: print(prefix + "description       : " + port_info.description      )
    if port_info.hwid              is not None: print(prefix + "hwid              : " + port_info.hwid             )
    if port_info.vid               is not None: print(prefix + "vid               : " + str(object=port_info.vid)  )
    if port_info.pid               is not None: print(prefix + "pid               : " + str(object=port_info.pid)  )
    if port_info.serial_number     is not None: print(prefix + "serial_number     : " + port_info.serial_number    )
    if port_info.location          is not None: print(prefix + "location          : " + port_info.location         )
    if port_info.manufacturer      is not None: print(prefix + "manufacturer      : " + port_info.manufacturer     )
    if port_info.product           is not None: print(prefix + "product           : " + port_info.product          )
    if port_info.interface         is not None: print(prefix + "interface         : " + port_info.interface        )
    break
def serial_info(port: serial.Serial, Name: str | None=None):
  result = ""
  prefix: str = "  " if Name is not None else ""
  if Name: result += "{Name}:".format(Name=Name) + '\n'
  for port_info in serial.tools.list_ports.grep(port.portstr):
    if port_info.usb_info()        is not None:  result += prefix + "usb_info()        : " + port_info.usb_info()        + '\n'
    if port_info.usb_description() is not None:  result += prefix + "usb_description() : " + port_info.usb_description() + '\n'
    if port_info.device            is not None:  result += prefix + "device            : " + port_info.device            + '\n'
    if port_info.name              is not None:  result += prefix + "name              : " + port_info.name              + '\n'
    if port_info.description       is not None:  result += prefix + "description       : " + port_info.description       + '\n'
    if port_info.hwid              is not None:  result += prefix + "hwid              : " + port_info.hwid              + '\n'
    if port_info.vid               is not None:  result += prefix + "vid               : " + str(object=port_info.vid)   + '\n'
    if port_info.pid               is not None:  result += prefix + "pid               : " + str(object=port_info.pid)   + '\n'
    if port_info.serial_number     is not None:  result += prefix + "serial_number     : " + port_info.serial_number     + '\n'
    if port_info.location          is not None:  result += prefix + "location          : " + port_info.location          + '\n'
    if port_info.manufacturer      is not None:  result += prefix + "manufacturer      : " + port_info.manufacturer      + '\n'
    if port_info.product           is not None:  result += prefix + "product           : " + port_info.product           + '\n'
    if port_info.interface         is not None:  result += prefix + "interface         : " + port_info.interface         + '\n'
    break
  return result