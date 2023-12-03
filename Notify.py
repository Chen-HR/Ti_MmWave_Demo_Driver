"""
# Notify
---
## EmailBot

### `Email` Class

- **Attributes:**
  - `host` (str): The email server host.
  - `port` (int): The port number for the email server.
  - `name` (str): The name associated with the email.
  - `user` (str): The username for authentication.
  - `password` (str): The password for authentication.

### `EmailBot` Class

- **Methods:**
  - `__init__(self, email: Email)`: Initializes an EmailBot instance with the provided `Email` object.
  - `send(self, receivers: list[str], title: str, content: str) -> bool`: Sends an email to the specified receivers with the given title and content.
    - `receivers` (list[str]): List of email addresses to receive the email.
    - `title` (str): Subject of the email.
    - `content` (str): Body/content of the email.
    - Returns `True` if the email is sent successfully; otherwise, `False`.

### EmailBot Usage Examples

```python
# Creating an EmailBot instance
email = EmailBot(Email(host="smtp.example.com", port=587, name="John Doe", user="john@example.com", password="password"))

# Sending an email
receivers = ["recipient1@example.com", "recipient2@example.com"]
title = "Sample Subject"
content = "This is a sample email content."
result = email.send(receivers, title, content)

if result:
    print("Email sent successfully.")
else:
    print("Failed to send email.")
```
---
## LineBot

### `LineBot` Class

- **Methods:**
  - `__init__(self, access_token: str)`: Initializes a LineBot instance with the provided Line Messaging API access token.
  - `multicast(self, usersid: list, msg: str)`: Sends a multicast message to the specified user IDs.
    - `usersid` (list): List of user IDs to receive the message.
    - `msg` (str): Message content to be sent.

### LineBot Usage Examples

```python
# Creating a LineBot instance
lineBot = LineBot(access_token="your_line_access_token")

# Sending a multicast message
usersId = ["user1", "user2", "user3"]
message = "Hello from LineBot!"
lineBot.multicast(usersId, message)
```
---
## ZenBot

### `ZenBot` Class

- **Methods:**
  - `__init__(self, host: str, timeout: int | float = 10)`: Initializes a ZenBot instance with the specified IP address (host) and optional connection timeout.
  - `connect(self, timeout: int | float = 10)`: Connects to the ZenBot with an optional timeout for the connection.
  - `disconnect(self, timeout: int | float = 10)`: Disconnects from the ZenBot with an optional timeout.
  - `expression(self, facial = RobotFace.DEFAULT, sentence: str | None = None, config = None, sync: bool = True, timeout: int | float = None)`: Sets the facial expression of the ZenBot.
    - `facial`: Facial expression to set (default is `RobotFace.DEFAULT`).
    - `sentence` (str | None): Optional sentence associated with the expression.
    - `config`: Additional configuration for expression.
    - `sync` (bool): Whether to synchronize the expression (default is `True`).
    - `timeout` (int | float): Optional timeout for the expression.

  - `__del__(self)`: Releases resources when the ZenBot instance is deleted.

### ZenBot Usage Examples

```python
# Creating a ZenBot instance
zenBot = ZenBot(host="192.168.31.27")

# Setting expressions
zenBot.expression(facial=RobotFace.DEFAULT, sentence="Testing ZenBot expressions")
```
"""

import time
import threading
import dataclasses

def delayedTrigger(delay: int | float, target, args: tuple = tuple()):
  def _delayedTrigger(delay, target, args: tuple = tuple()):
    time.sleep(delay)
    threading.Thread(target=target, args=args).start()
  threading.Thread(target=_delayedTrigger, args=(delay, target, args)).start()

import smtplib
from email.message import EmailMessage

@dataclasses.dataclass
class Email:
  host: str
  port: int
  name: str
  user: str
  password: str
class EmailBot:
  def __init__(self, email: Email):
    self.email = email
  def send(self, receivers: list[str], title: str, content: str):
    # if self.state_isLogin is not: return False
    smtpServer = smtplib.SMTP(self.email.host, self.email.port)
    smtpServer.starttls()
    smtpServer.login(f"{self.email.user}", self.email.password)
    data = EmailMessage()
    data.set_content(content)
    data['subject'] = title
    data['from'] = f"{self.email.user}@{self.email.host}"
    data['to'] = receivers
    smtpServer.login(f"{self.email.user}", self.email.password)
    return smtpServer.send_message(data)

# if __name__ == "__main__":
#   senders = [
#     {
#       "host": "smtp.example.com", 
#       "port": 587, 
#       "name": "John Doe", 
#       "user": "john@example.com", 
#       "password": "password"
#     }
#   ]
#   receivers = [
#     "recipient1@example.com", 
#     "recipient2@example.com"
#   ]
#   for sender in senders:
#     email = EmailBot(Email(host = sender["host"], port = sender["port"], name = sender["name"],  user = sender["user"],  password = sender["password"]))
#     email.send(receivers, "Email().send()", "EmailBot(Email(host, port, name,  user,  password)).send(receivers, title, content)")

from linebot import LineBotApi # line-bot-sdk==2.4.2
from linebot.models import TextSendMessage

class LineBot:
  def __init__(self, access_token: str):
    self.API = LineBotApi(access_token)
  def multicast(self, usersid: list, msg: str):
    self.API.multicast(usersid, TextSendMessage(text=msg))

# if __name__ == "__main__":
#   LineBot_API_Access_Tokens: dict[str, str] = {
#     "Name1": "your_line_access_token1", 
#     "Name2": "your_line_access_token2"
#   }
#   usersId = ["user1", "user2", "user3"]
#   for token in LineBot_API_Access_Tokens.values():
#     lineBot = LineBot(access_token=token)
#     lineBot.multicast(usersId, "LineBot.multicast")

import pyzenbo # 1.0.46.2220
from pyzenbo.modules.dialog_system import RobotFace

class ZenBot:
  def __init__(self, host: str, timeout: int | float = 10, log: bool = False):
    self.host = host
    self.isConnected = False
    self.timeout = timeout
    self.zenBot = None
    self.log = log
    if self.log: print("self.__init__")
    # self.connect()
  def connect(self):
    if self.log: print("| | self.connect().start")
    if self.isConnected and self.zenBot.get_connection_state() == (1, 1): return
    self.zenBot = pyzenbo.connect(self.host)
    if self.log and self.zenBot.get_connection_state() == (1, 1): print("| | |", self.zenBot.get_connection_state(), "vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
    if self.zenBot.get_connection_state() == (1, 1): self.isConnected = True
    # delayedTrigger(self.timeout, self.disconnect)
    if self.log: print("| | self.connect().end")
  def disconnect(self, wait: int | float = 0.5):
    if self.log: print("| | self.disconnect().start")
    if not self.isConnected and self.zenBot.get_connection_state() == (7, 7): return
    self.isConnected = False
    try:
      _ = self.zenBot.release()
      # del self.zenBot
      # self.zenBot = None
      time.sleep(wait)
    except:
      pass
    if self.log and self.zenBot.get_connection_state() == (7, 7): print("| | |", self.zenBot.get_connection_state(), "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    if self.log: print("| | self.disconnect().end")
  def expression(self, facial = RobotFace.DEFAULT, sentence: str | None = None, config = None, sync: bool = True, timeout: int | float = 10, wait: int | float = 1):
    if self.log: print("| self.expression().start")
    if not self.isConnected or self.zenBot == None or self.zenBot.get_connection_state() != (1, 1): self.connect()
    if self.log: print("| | ", self.zenBot)
    return self.zenBot.robot.set_expression(facial, sentence, config, sync, timeout)
    time.sleep(wait)
    # if self.isConnected or self.zenBot != None or self.zenBot.get_connection_state() != (7, 7): self.disconnect()
    if self.log: print("| self.expression().end")
  def speak(self, facial = RobotFace.DEFAULT, sentence: str | None = None, config = None, sync: bool = True, timeout: int | float = 10, wait: int | float = 1):
    if self.log: print("| self.speak().start")
    if not self.isConnected or self.zenBot == None or self.zenBot.get_connection_state() != (1, 1): self.connect()
    if self.log: print("| | ", self.zenBot)
    return self.zenBot.robot.speak( sentence, config, sync, timeout)
    time.sleep(wait)
    # if self.isConnected or self.zenBot != None or self.zenBot.get_connection_state() != (7, 7): self.disconnect()
    if self.log: print("| self.speak().end")
  def __del__(self):
    if self.log: print("self.__del__().start")
    try:
      # if self.isConnected or self.zenBot.get_connection_state() == (7, 7): self.zenBot.release()
      self.disconnect()
    except AttributeError:
      pass

if __name__ == "__main__":
  timeout = 5
  host = "192.168.31.27"
  zenBot = ZenBot(host, timeout)
  zenBot.connect()
  print(zenBot.zenBot.robot.set_expression(facial=RobotFace.HAPPY, sentence="expression")) # have thread and can't auto stop
  print(zenBot.zenBot.robot.speak(sentence="speak")) # have thread and can't auto stop
  time.sleep(1)
  print(zenBot.zenBot.robot.stop_speak())
  time.sleep(1)
  print(zenBot.zenBot.cancel_command_all())

  print(zenBot.expression(sentence="expression", sync=False))
  print(zenBot.expression(facial=RobotFace.HAPPY, sentence="expression", sync=False)) # recall when zenBot not yet disconnect
  print(zenBot.speak(sentence="speak", sync=False))
  time.sleep(timeout*1.5) # wait for zenBot disconnect
  print(zenBot.expression(sentence="expression", sync=False))
  print(zenBot.speak(sentence="speak", sync=False))

