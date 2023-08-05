#encoding: utf-8

import sys
from PyGtalkRobot import GtalkRobot

import plugnplay
import base64

__all__ = ['ICommand', 'InvertCommand', 'Base64Command', 'HelpCommand', 'Plugin']

Plugin = plugnplay.Plugin


class ICommand(plugnplay.Interface):


  '''
   Returns tha command name
  '''
  def name(self):
    pass

  '''
   Returns a tuple (short-help, long-help)
   about the command
  '''
  def help(self):
    pass

  '''
   Returns true if the command name passed as a paramater
   matches the command implemented by this interface
  '''
  def match_name(self, command):
    pass

  '''
   Run the specific command. Returns a string.
   Receives the username of the sender and any parameters
   passed on the message, eg:

    sender: process arg0 arg1 arg2

   would be translated to: run(sender, 'process', arg0, arg1, arg2)
  '''
  def run(self, user, command, *args):
    pass


class HelpCommand(Plugin):

  implements = [ICommand]
  SHORTHELP = 'List all commands. Type help <command> for more details'

  def name(self):
    return 'help'

  def help(self):
    return (self.SHORTHELP, self.SHORTHELP)

  def match_name(self, command):
    return 'help' == command

  def run(self, user, command, *args):
    if len(args) > 0:
      for implementor in ICommand.implementors():
        if implementor.match_name(args[0]):
          return implementor.help()[1]
    return "\n".join(["{0} - {1}".format(c.name(), c.help()[0]) for c in ICommand.implementors()])

class InvertCommand(Plugin):
  implements = [ICommand]
  SHORTHELP = 'Inverts all passed arguments'

  def name(self):
    return 'inv'

  def help(self):
    return (self.SHORTHELP, self.SHORTHELP)

  def match_name(self, command):
    return 'inv' == command

  def run(self, user, command, *args):
    if len(args) == 0:
      return "inv command needs at least one argument"
    return " ".join(s[::-1] for s in args[::-1])

class Base64Command(Plugin):

  implements = [ICommand]
  SHORTHELP = 'b64d/b64e Decode/Encode form/to Base64'
  LONGHELP = 'b64d decodes from Base64, b64e Encodes to base64'

  def name(self):
    return 'b64e/b64d'

  def help(self):
    return (self.SHORTHELP, self.LONGHELP)

  def match_name(self, command):
    return command in ('b64e', 'b64d')

  def run(self, user, command=None, *data):
    if len(data) == 0:
      return "{0} command needs one argument".format(command)
    return getattr(self, "_{0}".format(command))(data[0])


  def _b64e(self, data):
    return base64.b64encode(data)

  def _b64d(self, data):
    return base64.b64decode(data)


from urbandictionary import *
