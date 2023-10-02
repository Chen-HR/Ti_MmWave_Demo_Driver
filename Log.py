import datetime

formatted_time = lambda timezone, format: datetime.datetime.now(tz=timezone).strftime(format)

class Logger:

  def __init__(self, fileName: str) -> None:
    self.fileName = fileName

  def log(self, event: str, level: str, message: str):
    with open(file=self.fileName, mode='a+') as file:
      file.write("[{prefix}] <{event}> ({level}) : {message}\n".format(prefix=formatted_time(datetime.timezone.utc, "%Y-%m-%d %H:%M:%S.%f"), event=event, level=level, message=message))

if __name__ == '__main__':
  LoggerTester = Logger(fileName="LoggerTester.log")
  LoggerTester.log(event="LoggerTester", level="Information", message="Testing Logger")
