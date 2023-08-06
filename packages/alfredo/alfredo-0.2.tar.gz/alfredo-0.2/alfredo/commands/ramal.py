#coding: utf-8
import alfredo

class RamalEsys(alfredo.Plugin):

  implements = [alfredo.ICommand]

  def help(self):
    return ("Procura por um ramal", "Apenas chame <ramal> <nome> e você verá uma lista dos ramais encontrados.")

  def name(self):
    return 'ramal'

  def match_name(self, command):
    return 'ramal' == command

  def run(self, user, command, *args):
    if len(args) == 1:
      nome = args[0]
    else:
      nome = None
    
    return ramal(nome)



def ramal(nome=None):

  import simplejson as json
  from os.path import dirname, join
  with open(join(dirname(__file__),'ramais.json')) as f:
    s = f.read()
  
  j = json.loads(s)
  
  res = []
  for reg in j:
    if nome.lower() in reg['nome'].lower():
        res.append(reg)
  
  if len(res) == 0:
    s = u'sem informações para %s' % (nome, )
  else:
    s = '\n\n'.join(['%s (%s) - Ramal: %s Email: %s' % (v['nome'], v['depto'], v['ramal'], v['email']) for v in res])
        
  return s.encode('utf-8')
