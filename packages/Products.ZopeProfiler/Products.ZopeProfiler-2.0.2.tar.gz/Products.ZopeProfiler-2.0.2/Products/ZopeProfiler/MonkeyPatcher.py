#       $Id: MonkeyPatcher.py,v 1.1.1.1 2008/08/18 10:17:30 dieter Exp $
'''Monkey patch utilities.'''

# prevent refreshing as it would destroy our repositories
__refresh_module__= 0


_ModFuncRepo= {}
def patchModuleFunction(module,function,funcName=None):
  '''patch *funcName* in *module* with *function*; return original.

  The patching can handle the case that the patched function is monkey
  patched also by a different package.
  It assumes however, that the module is not reloaded.
  '''
  n= _getFunctionName(function,funcName); k= (module,n)
  w= _ModFuncRepo.get(k)
  if w is None:
    _ModFuncRepo[k]= w= _WrapFunction(module,n)
  w.setFunction(function)
  return w.getOriginalFunction()


class _WrapFunction:
  def __init__(self,module,name):
    self._oriFunction= getattr(module,name)
    setattr(module,name,self)

  def setFunction(self,function):
    self._function= function

  def getOriginalFunction(self): return self._oriFunction

  def __call__(self,*args,**kw):
    return self._function(*args,**kw)


def _getFunctionName(function,funcName):
  if funcName is not None: return funcName
  return function.__name__


#       $Log: MonkeyPatcher.py,v $
#       Revision 1.1.1.1  2008/08/18 10:17:30  dieter
#       ZopeProfiler 2.0
#
#       Revision 1.1  2003/03/30 14:39:57  dieter
#       careful monkey patching
#
