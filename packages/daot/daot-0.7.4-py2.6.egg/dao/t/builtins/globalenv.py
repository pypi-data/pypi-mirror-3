from dao.env import GlobalEnvironment

global_env = GlobalEnvironment({})

from dao.base import is_subclass
from dao.term import var

def collocet_builtins_to_module(globls, global_env, module): 
  for name, obj in globls.items():
    if isinstance(obj, Command):
      try: symbol = obj.symbol
      except:
        try: symbol = obj.name
        except: symbol = name
      v = var(symbol)
      module[v] = obj
      try: is_global = obj.is_global
      except: is_global = False
      if is_global: global_env[v] = obj
