import alfredo

import requests
from BeautifulSoup import BeautifulSoup, Tag

class MegaUploadCommand(alfredo.Plugin):

  implements = [alfredo.ICommand]

  def help(self):
    return ("Discover the final URL for a megaupload file", "Call mu <URL> to get the final link.")

  def name(self):
    return 'mu'

  def match_name(self, command):
    return 'mu' == command

  def run(self, user, command, *args):
    if len(args) < 1:
      return 'Needs a least one argument'
    return mu(args[0])


def mu(link):
  r = requests.get(link).content
  html = BeautifulSoup(r)
  href = html.findAll('a', attrs = {'class': 'down_butt1'})
  if len(href) > 0:
    return href[0]['href']
  else:
    return "{0} is not a valid Megaupload link anymore".format(link)
