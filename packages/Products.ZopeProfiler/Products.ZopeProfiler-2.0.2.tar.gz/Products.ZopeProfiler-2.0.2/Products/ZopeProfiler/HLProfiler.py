# Copyright (C) 2003-2010 by Dr. Dieter Maurer <dieter@handshake.de>
# see "LICENSE.txt" for details
#       $Id: HLProfiler.py,v 1.2 2010/05/04 05:25:09 dieter Exp $
from profile import Profile

# DM: Test
#file= open('/home/dieter/tmp/prof.log','w')

class HLProfiler(Profile):
  '''enhanced profiler to derive both low and high level information.

  It maintains additional data structures for high level information
  very much like the one maintained by the basic 'Profile' class
  for low level information. This means, a linked stack 'hl_cur' of
  frame descriptions and a dictionary mapping 'hl_timings'
  from function ids to timing information. 'hl_cur' and
  'hl_timings' have the same structure as 'cur' and 'timings'
  with the exception that each tuple in 'hl_cur' has the frame component
  replaced by a 'top' component.
  This component indicates whether the current
  frame describes the entry to a high level function.
  '''
  
  hl_cur= None

  def __init__(self,timer=None,hl_func_names=('__call__',)):
    self.hl_timings= {}
    fns= {}
    for fn in hl_func_names: fns[fn]= None
    self.hl_func= fns.has_key
    Profile.__init__(self,timer)

  # override inherited methods
  def trace_dispatch_exception(self, frame, t):
    #print >>file,  'exc(%d): ' % _getDepth(self.hl_cur), self.hl_cur[:-1]
    rt, rtt, rct, rfn, rframe, rcur = self.cur
    if (rframe is not frame) and rcur: # skip faked frames ?
      return self.trace_dispatch_return(rframe, t)
    self.cur = rt, rtt+t, rct, rfn, rframe, rcur
    hl_rt, hl_rtt, hl_rct, hl_rfn, hl_rtop, hl_rcur = self.hl_cur
    self.hl_cur = hl_rt, hl_rtt+t, hl_rct, hl_rfn, hl_rtop, hl_rcur
    return 1
  
  def trace_dispatch_call(self, frame, t):
    Profile.trace_dispatch_call(self,frame,t)
    return self.trace_dispatch_call_(frame, t, self._getFuncId(frame))

  def trace_dispatch_c_call(self, frame, t):
    Profile.trace_dispatch_c_call(self,frame,t)
    return self.trace_dispatch_call_(frame, t, None)

  def trace_dispatch_call_(self, frame, t, func_id):
    hl_cur= self.hl_cur
    parent_id= hl_cur and hl_cur[3]
    self.hl_cur= (t,0,0,func_id or parent_id,func_id is not None,self.hl_cur)
    #print >>file,  'call(%d): ' % _getDepth(self.hl_cur), self.hl_cur[:-1],
    if func_id:
      # a top level function
      timings= self.hl_timings
      if timings.has_key(func_id):
        cc, ns, tt, ct, callers = timings[func_id]
        timings[func_id] = cc, ns + 1, tt, ct, callers
      else:
        timings[func_id] = 0, 0, 0, 0, {}
      #print >>file,  timings[func_id],
    #print >>file
    return 1

  def trace_dispatch_return(self, frame, t):
    #print >>file,  'preturn(%d-%d): ' % (_getDepth(self.hl_cur),_getDepth(self.cur))
    cframe= self.cur[-2]
    Profile.trace_dispatch_return(self,frame,t)
    # Prefix "r" means part of the Returning or exiting frame
    # Prefix "p" means part of the Previous or older frame
    rt, rtt, rct, rfn, rtop, rcur = self.hl_cur
    pt, ptt, pct, pfn, ptop, pcur = rcur
    ltt= rtt + t
    #print >>file,  'return(%d): ' % _getDepth(self.hl_cur), self.hl_cur[:-1]
    #print >>file,  '              ', rcur[:-1]
    if rtop:
      self.hl_cur= pt, ptt+rt, pct+ltt+rct, pfn, ptop, pcur
      timings= self.hl_timings
      #print >>file,  '        ', timings[rfn]
      cc, ns, tt, ct, callers = timings[rfn]
      if not ns: cc+= 1; ct+= ltt + rct
      if callers.has_key(pfn): callers[pfn]+= 1
      else: callers[pfn]= 1
      timings[rfn]= cc, ns-1, tt+ltt, ct, callers
    else:
      self.hl_cur= pt, ptt+rt+ltt, pct+rct, pfn, ptop, pcur
    #print >>file,  '        ', self.hl_cur[:-1]
    #if rtop: #print >>file,  '        ', timings[rfn]
    return 1

  dispatch = {
        "call": trace_dispatch_call,
        "exception": trace_dispatch_exception,
        "return": trace_dispatch_return,
        "c_call": trace_dispatch_c_call,
        # DM 2005-09-20: exceptions in C always return
        #"c_exception": trace_dispatch_exception,
        "c_exception": trace_dispatch_return,
        "c_return": trace_dispatch_return,
        }

  # override as the standard library forgets to account for its
  # fake frame timing.
  def simulate_cmd_complete(self):
    if not self.cur: return
    get_time = self.get_time
    t = get_time() - self.t
    while self.cur[-1]:
      # We *can* cause assertion errors here if
      # dispatch_trace_return checks for a frame match!
      self.dispatch['return'](self, self.cur[-2], t)
      t = 0
    # account low level bottom frame
    rpt, rit, ret, rfn, frame, rcur = self.cur
    rit = rit + t
    frame_total = rit + ret
    timings = self.timings
    cc, ns, tt, ct, callers = timings[rfn]
    ct = ct + frame_total
    cc = cc + 1
    timings[rfn] = cc, ns - 1, tt + rit, ct, callers
    self.cur = None
    # account high level bottom frame
    rt, rtt, rct, rfn, rtop, rcur = self.hl_cur
    ltt= rtt + t
    timings= self.hl_timings
    cc, ns, tt, ct, callers = timings[rfn]
    if not ns: cc+= 1; ct+= ltt + rct
    timings[rfn]= cc, ns-1, tt+ltt, ct, callers
    self.hl_cur = None
    # ajust time    
    self.t = get_time() - t

    
  def get_hl_stats(self):
    self.create_stats()
    # delete dummy info -- as it is senseless
    #del self.hl_stats[self._topFuncId]
    return _ProfileData(self.hl_stats)

  _topFuncId= ('__Profiler__', 0,'Profile') # dummy
  def _getFuncId(self,frame):
    '''return the high level function id for *frame* or 'None'.'''
    l= getattr(frame,'f_locals',None)
    if l is None:
      # a fake frame - see whether it is the top frame
      if frame.f_back is None: return self._topFuncId
      if frame.f_back.f_back is None:
        return self.getTopFuncId()
    # Note: this does not work, as no code is executed yet
    #  when the function is called
    #if l.has_key('__profile_information__'): return l['__profile_information__']
    c= frame.f_code
    fn= c.co_name
    if self.hl_func(fn):
      # a potential high level function
      return self.getHLFuncId(fn,frame)

  def getTopFuncId(self):
    '''return the top level function id.'''
    return ('framework',_Empty,'')

  def getHLFuncId(self,fn,frame):
    '''return the high level function id for *frame*, if any.'''
    l= frame.f_locals
    s= l.get('self')
    i= getattr(s,'id',None)
    if i is None: return
    if callable(i): i= i()
    return (i,_Empty,fn) 

  def snapshot_stats(self):
    self.stats = self._snapshot_stats(self.timings)
    self.hl_stats = self._snapshot_stats(self.hl_timings)

  def _snapshot_stats(self, timings):
    t= _Timings(timings); t.snapshot_stats(); stats = t.stats
    # fixup top level call count (as it is computed via the number
    # of calls found in callers; and there are non for the top level)
    for func, (cc, nc, tt, ct, callers) in stats.iteritems():
      if nc == 0:
        # top level
        stats[func] = (cc, cc, tt, ct, callers)
    return stats

class _Timings:
  '''auxiliary class to reuse 'Profile.snapshot_stats'.'''
  def __init__(self,timings):
    self.timings= timings

  snapshot_stats= Profile.snapshot_stats.im_func

class _ProfileData:
  '''auxiliary class wrapper.'''
  def __init__(self,stats): self.stats= stats
  def create_stats(self): pass

class _Empty:
  '''auxiliary class for empty linenumber.'''
  def __repr__(self): return ''

# we must use an elementary type, as otherwise the statistics
# wont be marshallable
#_Empty= _Empty()
_Empty= 0

#############################################################################
## Test
def _getDepth(stack):
  i= 0
  while stack[-1]: i+=1; stack= stack[-1]
  return i


class _B:
  def __init__(self,id): self._id= id
  def __call__(self,*args):
    for i in range(int(self._id)):
      x= 1l
      for j in range(1,10000): x= x*j
    if not args: return
    apply(args[0],args[1:])
class _F(_B):
  def __init__(self,id): _B.__init__(self,id); self.id= id

def main():
  '''perform some tests.'''
  p= HLProfiler()
  p.runcall(_F('1'),_F('2'),_B('3'),_B('4'))
  return p


# $Log: HLProfiler.py,v $
# Revision 1.2  2010/05/04 05:25:09  dieter
# documentation improvement (not working for Zope 2.12 due to Python bug 'http://bugs.python.org/issue7372'
#
# Revision 1.1.1.1  2008/08/18 10:17:30  dieter
# ZopeProfiler 2.0
#
# Revision 1.8  2006/03/16 22:14:52  dieter
# replace our own function name based filtering by 'pstats' stdname based filtering;
# remove the unworking '__profile_information__' from the documentation and implementation
#
# Revision 1.7  2006/03/11 15:38:52  dieter
# Supports analysis of functions matched by a regular expression
# use my standard license
#
# Revision 1.6  2005/09/21 20:40:54  dieter
# fixed 'c_exception' dispatch bug
#
# Revision 1.5  2005/07/06 18:11:41  dieter
# Python 2.4.1 compatibility
# work around 'xmlrpclib' peculiarity'
#
# Revision 1.4  2004/12/05 08:43:02  dieter
# fix for 'callers' bug
#
# Revision 1.3  2004/04/02 22:51:56  dieter
# handle callable id's
#
# Revision 1.2  2003/02/02 17:00:19  dieter
# Python 2.2 compatibility
#
