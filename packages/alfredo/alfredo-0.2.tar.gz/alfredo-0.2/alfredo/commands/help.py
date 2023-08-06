import alfredo

class HelpCommand(alfredo.Plugin):

  implements = [alfredo.ICommand]
  SHORTHELP = 'List all commands. Type help <command> for more details'

  def name(self):
    return 'help'

  def help(self):
    return (self.SHORTHELP, self.SHORTHELP)

  def match_name(self, command):
    return 'help' == command

  def run(self, user, command, *args):
    if len(args) > 0:
      for implementor in alfredo.ICommand.implementors():
        if implementor.match_name(args[0]):
          return implementor.help()[1]
    return "\n".join(["{0} - {1}".format(c.name(), c.help()[0]) for c in alfredo.ICommand.implementors()])

