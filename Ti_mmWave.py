# %%
import time
import math
import threading

import serial # pyserial-3.5
import numpy # numpy-1.26.0
import matplotlib.pyplot # matplotlib-3.8.1
import matplotlib.collections
import matplotlib.animation

import Log
import SerialTool

import Configuration
import DataFrame

# %% 
class Ti_mmWave:

  def __init__(self, platform: str, Ctrl_port_name: str, Data_port_name: str, Ctrl_port_baudrate: int = 115200, Data_port_baudrate: int = 921600, Send_timeInterval: int | float | None = 0.025, Buffering_timeInterval: int | float | None = None, Parse_timeInterval: int | float | None = 1):

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

  # def parseData(self, log: bool=False) -> None:
  #   """Parse sensed data.

  #   Experimental product.

  #   TODO: Continuously loading sensing data. (Use `threading.Thread` to drive `self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))`)
  #   TODO: Continuously parse sensing data. (Use `threading.Thread` to drive `self.data.parse(dataByte=self.buffer, log=log)`)

  #   Args:
  #     log (bool, optional): _description_. Defaults to False.
  #   """
  #   self.buffer += bytearray(self.Data_port.read(self.Data_port.in_waiting))
  #   self.data.parse(dataByte=self.buffer, log=log)

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
      # print("Buffering: self.buffer.length:", len(self.buffer))
      self.buffer = self.buffer + bytearray(self.Data_port.read(self.Data_port.in_waiting))
      # print("Buffering: self.buffer.length:", len(self.buffer))
      self._DataPort_inUse_ = False
  def Data_Buffering_continuous(self, timeInterval: int | float | None = None) -> None:
    try:
      # while True: 
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
    # print("Parse: self.buffer.length:", len(self.buffer))
    data, index = DataFrame.DataFrame.parse(self.buffer, log)
    # print("data: {}, index: {}".format(data, index))
    if data is not None: 
      self.data = data
      self.buffer = self.buffer[index:]
    # print("Parse: self.buffer.length:", len(self.buffer))
  def Data_Parse_continuous(self, timeInterval: int | float | None = None, log: str | None = None) -> None:
    try:
      # while True: 
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

# Calculate the distance between two points
distance = lambda point1, point2: float(numpy.linalg.norm(numpy.array(point1) - numpy.array(point2)))
# Calculate the center point of a cluster
center = lambda cluster: tuple(numpy.array([sum(vL) for vL in numpy.transpose(numpy.array(list(cluster)))]) / len(cluster))

def integration_V1_universal(points: list, rule, point=lambda point: point) -> list[tuple]:
  """merge adjacent points into one point

    1. Iterate through each point in the input list
    2. Check if the point belongs to any existing cluster based on the rule
    3. If the point does not belong to any cluster, create a new cluster
    4. If the point belongs to multiple clusters, merge those clusters
    5. Calculate the center point as the average of its points

  Args:
      points (list): Coordinate points to be processed
      rule (_type_): lambda
      point (_type_, optional): method to get coordinates. Defaults to `lambda point: point`.

  Returns:
      list[tuple]: Merged coordinates
  """
  clusters: list[set] = []
  
  for i in range(len(points)):
    for j in range(i+1, len(points)):
      # Join or add a new cluster
      if rule(points[i], points[j]):
        clustered = False
        newCluster = {point(points[i]), point(points[j])}
        # Join cluster
        for cluster in clusters:
          if not cluster.isdisjoint(newCluster):
            cluster |= newCluster
            clustered = True
            break  # Exit the loop after merging the cluster
        # Add a new cluster
        if not clustered:
          clusters.append(newCluster)

  # Merge associated clusters
  i = 0
  while i < len(clusters):
    j = i + 1
    while j < len(clusters):
      if clusters[i].isdisjoint(clusters[j]):
        j += 1
      else:
        clusters[i] |= clusters.pop(j)
    i += 1

  # Calculate the center point for each cluster
  return [center(cluster) for cluster in clusters if cluster]

def integration_V2_1(points: list[tuple], limit: float | int, scaling: float | int) -> list[tuple]:
  """Integration and filtering of detection points

    1. Generate weighted virtual points
      1.1. Position: midpoint between two points
      1.2. Weight: log⁡(1/(𝑑/𝑟))
        1.2.1. 𝑑 : distance between two points
        1.2.2. 𝑟: distance limitation coefficient
    2. Generate virtual point clusters using existing virtual points as reference targets
      2.1. Point cluster: The weight of the generated virtual points is greater than 0, and the distance between virtual points is less than α𝑟
        2.1.1. α	distance limit scaling factor
    3. Merge virtual point cluster to generate merged points

  Args:
      points (list[tuple]): Coordinate points to be processed
      limit (float | int): distance limitation coefficient
      scaling (float | int): distance limit scaling factor

  Returns:
      list[tuple]: Merged coordinates
  """
  class VirtualPoint:
    def __init__(self, point1: tuple, point2: tuple, limit: float):
      self.sources = (numpy.array(point1), numpy.array(point2))
      # 1.1. Position: midpoint between two points
      self.point = tuple((self.sources[0] + self.sources[1])/2)
      # 1.2. Weight: log⁡(1/(𝑑/𝑟))
      #   1.2.1. 𝑑 : distance between two points
      #   1.2.2. 𝑟: distance limitation coefficient
      self.weight = numpy.log(1/(numpy.linalg.norm(self.sources[0]- self.sources[1])/limit))
  # 1. Generate weighted virtual points # NOTE: not full
  virtualPoints: list[VirtualPoint] = [VirtualPoint(points[i], points[j], limit) for i in range(len(points)) for j in range(i+1, len(points))]
  # 2. Generate virtual point clusters using existing virtual points as reference targets
  # 3. Merge virtual point cluster to generate merged points
  virtualClusterCenters = integration_V1_universal(virtualPoints, lambda point1, point2: point1.weight>0 and point2.weight>0 and distance(point1.point, point2.point) < scaling*limit, lambda virtualPoint: virtualPoint.point)
  return virtualClusterCenters

def integration_V2_2(points: list[tuple], limit: float | int, scaling: float | int) -> list[tuple]:
  """Integration and filtering of detection points

    1. Generate weighted virtual points
      1.1. Position: midpoint between two points
      1.2. Weight: log⁡(1/(𝑑/𝑟))
        1.2.1. 𝑑 : distance between two points
        1.2.2. 𝑟: distance limitation coefficient
    2. Generate point clusters using existing virtual points as reference targets
      2.1. Point clusters: The weight of the generated virtual points is greater than 0, and the distance between virtual points is less than α𝑟
        2.1.1. α	distance limit scaling factor
    3. Merge point clusters to generate merged points

  Args:
      points (list[tuple]): Coordinate points to be processed
      limit (float | int): distance limitation coefficient
      scaling (float | int): distance limit scaling factor

  Returns:
      list[tuple]: Merged coordinates
  """
  class VirtualPoint:
    def __init__(self, point1: tuple, point2: tuple, limit: float):
      self.sources = (numpy.array(point1), numpy.array(point2))
      # 1.1. Position: midpoint between two points
      self.point = tuple((self.sources[0] + self.sources[1])/2)
      # 1.2. Weight: log⁡(1/(𝑑/𝑟))
      #   1.2.1. 𝑑 : distance between two points
      #   1.2.2. 𝑟: distance limitation coefficient
      self.weight = numpy.log(1/(numpy.linalg.norm(self.sources[0]- self.sources[1])/limit))
      self.sources = (tuple(self.sources[0]), tuple(self.sources[1]))
  # 1. Generate weighted virtual points
  virtualPoints: list[VirtualPoint] = [VirtualPoint(points[i], points[j], limit) for i in range(len(points)) for j in range(i+1, len(points))]
  # 2. Generate point clusters using existing virtual points as reference targets
  clusters: list[set] = []
  for i in range(len(virtualPoints)):
    for j in range(i+1, len(virtualPoints)):

      # Join or add a new cluster
      if virtualPoints[i].weight>0 and virtualPoints[j].weight>0 and distance(virtualPoints[i].point, virtualPoints[j].point) < scaling*limit:
        clustered = False
        newCluster = set(virtualPoints[i].sources) | set(virtualPoints[j].sources)
        # Join cluster
        for cluster in clusters:
          if cluster.isdisjoint(newCluster):
            cluster |= newCluster
            clustered = True
        # Add a new cluster
        if not clustered:
          clusters.append(newCluster)

      # Merge associated clusters
      i = 0
      while i < len(clusters):
        j = i + 1
        while j < len(clusters):
          if clusters[i].isdisjoint(clusters[j]):
            j += 1
          else:
            clusters[i] |= clusters.pop(j)
        i += 1
  # 3. Merge point clusters to generate merged points
  return [center(cluster) for cluster in clusters]

def integration_V2_3(points: list[tuple], limit: float | int, scaling: float | int) -> list[tuple]:
  """Integration and filtering of detection points

    1. Generate weighted virtual points
      1.1. Position: midpoint between two points
      1.2. Weight: log⁡(1/(𝑑/𝑟))
        1.2.1. 𝑑 : distance between two points
        1.2.2. 𝑟 : distance limitation coefficient
    2. Generate point clusters using existing virtual points as reference targets
      2.1. Point cluster: The weight of the generated virtual points is greater than 0, and the distance between virtual points is less than α𝑟
        2.1.1. α	distance limit scaling factor
    3. The virtual point weights within each point cluster are synthesized into each point weight.
      3.1. Weight: virtual point weight average
    4. Calculate the center of gravity of each point cluster

  Args:
      points (list[tuple]): Coordinate points to be processed
      limit (float | int): distance limitation coefficient
      scaling (float | int): distance limit scaling factor

  Returns:
      list[tuple]: Merged coordinates
  """
  class VirtualPoint:
    def __init__(self, point1: tuple, point2: tuple, limit: float):
      self.sources = (numpy.array(point1), numpy.array(point2))
      # 1.1. Position: midpoint between two points
      self.point = tuple((self.sources[0] + self.sources[1])/2)
      # 1.2. Weight: log⁡(1/(𝑑/𝑟))
      #   1.2.1. 𝑑 : distance between two points
      #   1.2.2. 𝑟: distance limitation coefficient
      self.weight = numpy.log(1/(numpy.linalg.norm(self.sources[0]- self.sources[1])/limit))
      self.sources = (tuple(self.sources[0]), tuple(self.sources[1]))
  # 1. Generate weighted virtual points
  virtualPoints: list[VirtualPoint] = [VirtualPoint(points[i], points[j], limit) for i in range(len(points)) for j in range(i+1, len(points))]
  # 2. Generate point clusters using existing virtual points as reference targets
  clusters: list[set] = []
  for i in range(len(virtualPoints)):
    for j in range(i+1, len(virtualPoints)):

      # Join or add a new cluster
      if virtualPoints[i].weight>0 and virtualPoints[j].weight>0 and distance(virtualPoints[i].point, virtualPoints[j].point) < scaling*limit:
        clustered = False
        newCluster = set(virtualPoints[i].sources) | set(virtualPoints[j].sources)
        # Join cluster
        for cluster in clusters:
          if cluster.isdisjoint(newCluster):
            cluster |= newCluster
            clustered = True
        # Add a new cluster
        if not clustered:
          clusters.append(newCluster)

      # Merge associated clusters
      i = 0
      while i < len(clusters):
        j = i + 1
        while j < len(clusters):
          if clusters[i].isdisjoint(clusters[j]):
            j += 1
          else:
            clusters[i] |= clusters.pop(j)
        i += 1
  # 3. The virtual point weights within each point cluster are synthesized into each point weight.
  weightClusters = []
  for cluster in clusters:
    cluster_list = list(cluster)
    weighted_dict = {}
    for i in range(len(cluster_list)):
      weighted_dict[cluster_list[i]] = sum([VirtualPoint(cluster_list[i], cluster_list[j], limit).weight for j in range(len(cluster)) if i != j]) / len(cluster)
    weightClusters.append(weighted_dict)
  # 4. Calculate the center of gravity of each point cluster
  def calculate_center_of_gravity(weighted_dict):
    total_weight = sum(weighted_dict.values())
    center_coordinates = [0] * len(next(iter(weighted_dict.keys())))
    for point, weight in weighted_dict.items():
      for i, coordinate in enumerate(point):
        center_coordinates[i] += coordinate * (weight / total_weight)
    return tuple(center_coordinates)
  return [calculate_center_of_gravity(wp) for wp in weightClusters]

# %%
if __name__ == '__main__':
  device = Ti_mmWave(platform="xWR14xx", Ctrl_port_name="COM3", Data_port_name="COM4", Ctrl_port_baudrate=115200, Data_port_baudrate=921600)
  device.logger.echo = True
  device.config.logger.echo = True
  device.data.logger.echo = True
  print("configured device...")
  device.sensorStop(log=True)
  device.Ctrl_Load_file("Profile\Profile-3.cfg")
  device.config.set_CfarRangeThreshold_dB(threshold_dB=12)
  device.config.set_RemoveStaticClutter(enabled=True)
  device.config.set_FramePeriodicity(FramePeriodicity_ms=200)
  device.Ctrl_Send()
  device.sensorStart(log=True)
  print("sensorStart")

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
  
  def update_3D():

    figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()

    axes_231: matplotlib.pyplot.Axes = figure.add_subplot(231, projection='3d')
    axes_231.set_title("Detection distribution map")
    axes_231.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
    axes_231.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
    axes_231.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
    def update_matplotlibAnimation_SOP_231(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
      device.Data_Buffering_unit()
      device.Data_Parse_unit()
      if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
        detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
        detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        scatter._offsets3d = detectedPoints_transposed
    animation_231 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_231, fargs=(axes_231.scatter([], [], [], label='Detection Object'), ), interval=100)
    axes_231.legend()

    limit = 0.3

    axes_233: matplotlib.pyplot.Axes = figure.add_subplot(233, projection='3d')
    axes_233.set_title("integration V1")
    axes_233.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
    axes_233.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
    axes_233.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
    def update_matplotlibAnimation_SOP_233(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
      device.Data_Buffering_unit()
      device.Data_Parse_unit()
      if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
        detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
        detectedPoints = integration_V1_universal(detectedPoints, lambda point1, point2: distance(point1, point2) < limit)
        detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        scatter._offsets3d = detectedPoints_transposed
    animation_233 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_233, fargs=(axes_233.scatter([], [], [], label='Detection Object'), ), interval=100)
    axes_233.legend()

    axes_234: matplotlib.pyplot.Axes = figure.add_subplot(234, projection='3d')
    axes_234.set_title("integration V2.1")
    axes_234.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
    axes_234.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
    axes_234.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
    def update_matplotlibAnimation_SOP_234(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
      device.Data_Buffering_unit()
      device.Data_Parse_unit()
      if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
        detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
        detectedPoints = integration_V2_1(detectedPoints, limit, 1)
        detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        scatter._offsets3d = detectedPoints_transposed
    animation_234 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_234, fargs=(axes_234.scatter([], [], [], label='Detection Object'), ), interval=100)
    axes_234.legend()
    
    axes_235: matplotlib.pyplot.Axes = figure.add_subplot(235, projection='3d')
    axes_235.set_title("integration V2.2")
    axes_235.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
    axes_235.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
    axes_235.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
    def update_matplotlibAnimation_SOP_235(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
      device.Data_Buffering_unit()
      device.Data_Parse_unit()
      if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
        detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
        detectedPoints = integration_V2_2(detectedPoints, limit, 1)
        detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        scatter._offsets3d = detectedPoints_transposed
    animation_235 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_235, fargs=(axes_235.scatter([], [], [], label='Detection Object'), ), interval=100)
    axes_235.legend()

    axes_236: matplotlib.pyplot.Axes = figure.add_subplot(236, projection='3d')
    axes_236.set_title("integration V2.3")
    axes_236.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel='X')
    axes_236.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel='Y')
    axes_236.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel='Z')
    def update_matplotlibAnimation_SOP_236(frame, scatter: matplotlib.collections.PathCollection) -> matplotlib.collections.PathCollection:
      device.Data_Buffering_unit()
      device.Data_Parse_unit()
      if device.data is not None and device.data.iscomplete and device.data.CRC32 is not None:
        detectedPoints = [(DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.x), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.y), DataFrame.Converter.QFormat.parse(device.data.detectedObjects.infomation.xyzQFormat, DetectedObj.z)) for DetectedObj in device.data.detectedObjects.Objects]
        detectedPoints = integration_V2_3(detectedPoints, limit, 1)
        detectedPoints_transposed: tuple[list[float], list[float], list[float]] = tuple(list(x) for x in zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
        scatter._offsets3d = detectedPoints_transposed
    animation_236 = matplotlib.animation.FuncAnimation(fig=figure, func=update_matplotlibAnimation_SOP_236, fargs=(axes_236.scatter([], [], [], label='Detection Object'), ), interval=100)
    axes_236.legend()

    matplotlib.pyplot.show()
  update_3D()

  del device
# %%
