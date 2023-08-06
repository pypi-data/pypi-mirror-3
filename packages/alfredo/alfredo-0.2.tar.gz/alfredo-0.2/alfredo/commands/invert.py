import alfredo

class InvertCommand(alfredo.Plugin):
  implements = [alfredo.ICommand]
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
