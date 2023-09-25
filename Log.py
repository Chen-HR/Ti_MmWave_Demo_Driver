import datetime

formatted_time = lambda timezone, format: datetime.datetime.now(tz=timezone).strftime(format)

class Logger:
  fileName: str = None
  prefix = None
  def __init__(self, fileName: str, prefix = formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f")) -> None:
    self.fileName = fileName
    self.prefix = prefix
  def log(self, message):
    with open(file=self.fileName, mode='a+') as file:
      file.write(self.prefix + ": " + message + '\n')

if __name__ == '__main__':
  LoggerTester = Logger(fileName="LoggerTester.log")
  LoggerTester.log(message="Testing Logger")
