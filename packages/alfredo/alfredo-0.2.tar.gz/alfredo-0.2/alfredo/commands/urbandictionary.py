


import alfredo

import requests
from BeautifulSoup import BeautifulSoup, Tag
import urllib


URL = "http://www.urbandictionary.com/define.php?"

class UdCommand(alfredo.Plugin):

  implements = [alfredo.ICommand]

  def help(self):
    return ("Searches any term on urbandictionary.com", "Just call ud <term> and you will se the first available definition as returned by urbandictionary, and a link to the full result page.")

  def name(self):
    return 'ud'

  def match_name(self, command):
    return 'ud' == command

  def run(self, user, command, *args):
    if len(args) < 1:
      return 'Needs a least one argument'
    return urban(" ".join(list(args)))



def urban(term):

  params = urllib.urlencode({'term': term})
  response = requests.get(URL + params).content
  html = BeautifulSoup(response)
  tags = html.findAll('div', attrs = {'class': 'definition'})
  if len(tags) >= 1:
    text = ""
    for c in tags[0].contents:
      if isinstance(c, Tag):
        text += unicode("".join(c.contents))
      else:
        text += unicode(c)
    text = text.encode('utf-8')
    return "{0}:\n{1}\nYou can see all results at: {2}".format(term, unescape(text), URL + params)
  return "Term not found: {0}".format(term)


import htmllib

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()
