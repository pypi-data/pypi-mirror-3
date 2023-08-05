# Copyright (C) 2003-2008 by Dr. Dieter Maurer <dieter@handshake.de>
# see "LICENSE.txt" for details
#       $Id: ZopeProfiler.py,v 1.2 2011-11-13 09:52:57 dieter Exp $
'''ZopeProfiler.

  'ZopeProfiler' supports both low level and high level profiling for Zope
  applications.

  Low level profiling is on the level of Python function calls,
  high level profiling on the level of Zope (persistent) object calls.

  You can analyse the profiles in various modes (basic timing statistics,
  callers, callees) on the 'Zope level' and 'Python level' tabs.
  You select the analysis mode with the 'Mode' dropdown.
  
  'ZopeProfiler' uses Pythons 'profile' module to record profiling
  information and 'dm.profile.Stats' for its display.
  'dm.profile.Stats' is an extension of Pythons 'pstats.Stats'.
  You can use the 'display format' dropdown to choose between
  the 'dm.profile' format, Pythons standard format and 'automatic'.
  In my view, the 'dm.profile' format is much more readable for
  caller and callee analysis than Pythons standard format.
  'automatic' uses Pythons format for 'stats' analysis and the
  'dm.profile' format for 'caller' and 'callee' analysis.
  
  The 'dm.profile' format uses different formats for the primary
  function, caller and callee statistics.

  The primary function statistic lists the call number (*number* c),
  information about the internal time (time in the function without
  time in functions called by this function), cumulative time
  (time in the function including time in called functions)
  and the functions "stdname". The stdname consists of filename, line and
  function name for the function.
  Both internal time and cumulative time are given as the total time
  and the time per call.

  The caller statistics uses the primary function format to
  describe the statistics for the current function (the called function)
  and then
  each caller is described by a line of the form
  '*calls* c (from *caller calls* c in *caller time* s) *stdname*'.
  *calls* gives the number of calls the caller has called this called
  function. *caller calls* are the total number the caller has been called
  and *caller time* is the cumulative time spend in the caller.

  The callee statistics uses the primary function format to
  describe the statistics for the current function (the calling function)
  and then each called function (callee) is described by a line of the
  form
  '*calls* c (of *callee calls* c in *callee time* s) *stdname*'.
  *calls* is the number of calls from the calling function to this
  callee, *callee calls* is the total number of calls to this callee
  (including the calls from other callers) and *callee time* it the
  cumulative time spend in this function.
  
  Consult the 'pstats' documentation to learn how to interpret
  Pythons statistics data.

  The properties tab lets you specify defaults for most of
  the Zope and Python level tab input fields.

  You can put a regular expression into the 'StdnameRe' field
  to restrict output to those functions whose stdname contains
  the regular expression. The stdname has the form *file*:*line*(*function*),
  e.g. 'Publish.py:241(publish_module_standard)'.
  Note that you need to escape parenthesis
  in the regular expression
  by preceeding it with '\\'.

  That a function call is seen as a high level call
  requires that the function name is listed
  in a (configurable) sequence of high level function
  names (the default is the sequence '("__call__",)'),
  that the function namespace contains 'self'
  and that 'self' has a method 'getPhysicalPath'.
  In this case, the triple '("/".join(self.getPhysicalPath()),0,func_name)'
  is used as function id.

  Profiling can be controlled (turned on and off) dynamically (via
  a Web interface). Both low and high level profiles can be
  analysed and reset via a Web interface.

  Unlike the standard Zope profiling support, Zope can continue
  to operate in multi thread mode. If 'ZopeProfiler' is
  disabled, it causes only negligible interference or runtime overhead.
  The 'ZopeProfiler' is incompatible with Zopes standard profiling
  support. Therefore, it is disabled, when the standard
  Zope profiling is enabled, i.e. when 'PROFILE_PUBLISHER' is
  defined (and non-empty).

  ZopeProfiler uses monkey patching to install itself. It
  modifies 'ZServer.PubCore.ZServerPublisher.publish_module'.
  Monkey patching is potentially dangerous when the same resource is
  patched by different modules. This was a serious problem for
  version 0.01 of ZopeProfiler and WingIDEs Zope debugging support.
  ZopeProfilers monkey patching is much more careful now. Despite this, there
  may well be further problems with other pachages patching the
  above resource.
'''
_ModDict= globals()

from logging import getLogger
from cStringIO import StringIO
import sys
from threading import RLock
import os, marshal
from os import environ, path
from types import StringType
from dm.profile import Stats
from copy import deepcopy
from time import strftime
import time

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass, DTMLFile
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from HLProfiler import HLProfiler, _Empty
from MonkeyPatcher import patchModuleFunction


_log = getLogger('ZopeProfiler')

############################################################################
## Persistent Zope objects
class ZopeProfiler(SimpleItem,PropertyManager):
  '''Profiler singleton'''
  id= 'ZopeProfiler'
  title= id
  meta_type= 'Zope Profiler'

  ## Configuration
  ORDERS= ('time', 'cumulative', 'calls', 'pcalls', 'name', 'file', 'module', 'nfl', 'stdname',)
  MODES= ('stats', 'callees', 'callers',)
  FORMATS= ('dm.profile', 'python', 'automatic',)

  security= ClassSecurityInfo()
  security.declareProtected('ZopeProfiler: manage',
                            'manageStatus',
                            'manage_changeProperties',
                            'resetStatistics',
                            'saveStatistics',
                            'setTimer',
                            )

  security.declareProtected('ZopeProfiler: view',
                            'showStatus',
                            'showHigh', 'showLow',
                            'getStatistics',
                            'getStatus',
                            'listModes', 'listOrders',
                            'getTimers', 'getTimer',
                            )

  security.declarePublic(
                         'showInfo'
                         )

  security.setDefaultAccess(1)

  _properties= (
    { 'id' : 'title', 'type' : 'string', 'mode' : 'w', },
    { 'id' : 'FunctionNames', 'type' : 'lines', 'mode' : 'w', },
    { 'id' : 'DefaultOrder', 'type' : 'selection', 'select_variable' : 'listOrders', 'mode' : 'w', },
    { 'id' : 'DefaultLimit', 'type' : 'int', 'mode' : 'w', },
    { 'id' : 'DefaultStripDirs', 'type' : 'boolean', 'mode' : 'w', },
    { 'id' : 'DefaultMode', 'type' : 'selection', 'select_variable' : 'listModes', 'mode' : 'w',},
    { 'id' : 'DefaultDisplayFormat', 'type' : 'selection', 'select_variable' : 'listDisplayFormats', 'mode' : 'w'},
    { 'id' : 'PersistentState', 'type' : 'boolean', 'mode':'w',},
  )
  FunctionNames= ('__call__',)

  DefaultOrder= ORDERS[0]
  DefaultMode= MODES[0]
  DefaultLimit= 200
  DefaultStripDirs= 1
  PersistentState = False
  DefaultDisplayFormat = 'automatic'
    


  manage_options= (
  (
    {'label' : 'Status', 'action' : 'showStatus'},
    {'label' : 'Zope level', 'action' : 'showHigh'},
    {'label' : 'Python level', 'action' : 'showLow'},
    )
  + PropertyManager.manage_options
  + ( 
    {'label' : 'Info', 'action' : 'showInfo'},
    )
  + SimpleItem.manage_options
  )

  _enabled= 0

  # status
  def manageStatus(self,enable= None, disable=None, REQUEST= None):
    '''manage profile status.'''
    if enable: enabled= 1
    if disable: enabled= 0
    if self.PersistentState: self._enabled = enabled
    global _enabled; _enabled= enabled # ATT: violates transactions
    if REQUEST is not None:
      return self.showStatus(self,REQUEST)

  def getStatus(self):
    '''the current status as a triple (*configured*,*enabled*,*persistent*).
    '''
    return (_configured,_enabled,self.PersistentState )

  # statistics
  def getStatistics(self,what, sort, limit, stripDirs, mode, stdnameRe, format):
    '''return *what* statistics as a string.'''
    stats= self._getStatistics(what)
    if stats is None: return None
    output=StringIO()
    if stripDirs: stats.strip_dirs()
    stats.sort_stats(sort)
    filter = (stdnameRe and (str(stdnameRe),) or ()) + (limit,)
    dm_format = format == 'dm.profile' or (
      format == 'automatic' and mode != 'stats'
      )
    if dm_format:
      stats.setOutputFile(output)
      stats.showHeader()
      getattr(stats, 'show%s' % mode.capitalize())(*filter)
      res = output.getvalue()
      if not res: res = 'No matching functions'
      return res
    else:
      if hasattr(stats, "stream"):
        # Python 2.6 and above
        stats.stream = output
      else:
        stdout=sys.stdout
        sys.stdout=output # ATT: this is dangerous
      try:
        getattr(stats,'print_%s' % mode)(*filter)
        return output.getvalue()
      finally:
        if not hasattr(stats, "stream"): sys.stdout=stdout

  def _getStatistics(self,what):
    '''return the statistics object.'''
    _lock.acquire()
    try:
      stats= deepcopy(_ModDict.get('_Stats_' + what))
      return stats
    finally:
      _lock.release()

  def resetStatistics(self,what):
    '''reset the *what* statistics.'''
    if what == 'all':
      self.resetStatistics('Low')
      self.resetStatistics('High')
      return 'All statistics reset'
    _lock.acquire()
    try:
      _ModDict['_Stats_' + what]= None
      return 'Statistics reset'
    finally:
      _lock.release()

  def saveStatistics(self,what,filename):
    '''save *what* statistics to *filename*.'''
    stats= self._getStatistics(what)
    if not stats: return 'Currently no statistics available'
    if not filename: filename= '%s_Stats_%s' % (what,strftime('%y%m%dT%H%M%S'))
    # ensure filename does not contain the file separator
    if os.sep in filename: return 'Filename must not contain %s' % os.sep
    d= 'var/Statistics'
    try: 
      if not path.isdir(d): os.makedirs(d)
    except os.error: return 'Could not create directory %s' % d
    try:
      filename= path.join(d,filename)
      marshal.dump(stats.stats,open(filename,"wb"))
    except os.error: return 'Could not write file %s' % filename
    return 'Statistics written to %s' % filename
    

  # lists
  def listOrders(self): return self.ORDERS
  def listModes(self): return self.MODES
  def listDisplayFormats(self): return self.FORMATS

  # overridden methods
  def manage_editProperties(self, REQUEST):
    '''edit properties.'''
    res= ZopeProfiler.inheritedAttribute('manage_editProperties')(self,REQUEST)
    self._install()
    return res

  def manage_changeProperties(REQUEST=None, **kw):
    '''change properties.'''
    res= ZopeProfiler.inheritedAttribute('manage_changeProperties')(self,REQUEST,**kw)
    self._install()
    return res

  def _install(self):
    global _functionNames
    _functionNames= self.FunctionNames # ATT: violates transactions
    if self.PersistentState:
      global _enabled; _enabled = self._enabled

  Documentation= _ModDict['__doc__']

  # timer selection
  _timerName= 'time'
  def getTimers(self):
    tl= []
    if hasattr(time,'clock'): tl.append(('clock','CPU time',))
    tl.append(('time','Real time',))
    return tl

  def getTimerNames(self):
    return [n for n,_ in self.getTimers()]

  def getTimer(self):
    t= self._timerName
    if t is None:
      self._timerName= t=  self.getTimerNames()[0]
      self._setTimer()
    return t

  def setTimer(self,timer):
    tl= self.getTimerNames()
    if timer not in tl:
      raise ValueError, 'unsupported timer'
    self._timerName= timer
    self._setTimer()
    # reset statistics
    self.resetStatistics('Low')
    self.resetStatistics('High')

  def _setTimer(self):
    global _timerFunc
    tn= self.getTimer()
    tf= getattr(time,tn,None)
    if tf is None:
      tn= self._timerName= self.getTimerNames()[0]
      tf= getattr(time,tn)
    _timerFunc= tf

  # presentation
  showStatus= DTMLFile('showStatus',_ModDict)
  showHigh= DTMLFile('showStatistics',_ModDict,what='High')
  showLow= DTMLFile('showStatistics',_ModDict,what='Low')
  showInfo= DTMLFile('showDocumentation',_ModDict)

InitializeClass(ZopeProfiler)
    


############################################################################
## global variables
_timerFunc= None
_enabled= 0
_configured= not environ.get('PROFILE_PUBLISHER')
_lock= RLock()

_Stats_Low= None
_Stats_High= None



############################################################################
## Hooking
def _hookZServerPublisher():
  if not _configured: return
  global publish_module
  from ZServer.PubCore import ZServerPublisher as module
  funcName = 'publish_module'
  if not hasattr(module,funcName):
    # a post Zope 2.6 version
    import ZPublisher as module
  publish_module= patchModuleFunction(module,
                                      _profilePublishModule,
                                      funcName=funcName)

def _profilePublishModule(
  module_name, stdin=sys.stdin, stdout=sys.stdout, 
  stderr=sys.stderr, environ=environ, debug=0, 
  request=None, response=None
  ):
  lock= _lock # to facilitate refreshing
  psrc= request or environ; path= psrc.get('PATH_INFO')
  if _enabled and _doProfile(path):
    prof= ZProfiler(funcNames= _functionNames, path=path, timer=_timerFunc)
    result= prof.runcall(publish_module,
                         module_name, stdin, stdout, 
                         stderr, environ, debug, 
                         request, response)
    lock.acquire()
    try:
      pd_high= prof.get_hl_stats()
      global _Stats_High, _Stats_Low
      if _Stats_High is None: _Stats_High= Stats(pd_high)
      else: _Stats_High.add(pd_high)
      if _Stats_Low is None: _Stats_Low= Stats(prof)
      else: _Stats_Low.add(prof)
    finally: lock.release()
  else:
    result= publish_module(
                         module_name, stdin=stdin, stdout=stdout, 
                         stderr=stderr, environ=environ, debug=debug, 
                         request=request, response=response)
  return result

def _doProfile(path):
  '''we do not profile 'Control_Panel' requests.'''
  return not path.startswith('/Control_Panel/')

def _initializeModule(zp):
  zp._install()
  zp._setTimer()






############################################################################
## Zope specific high level profiler
class ZProfiler(HLProfiler):
  def __init__(self,timer=None, funcNames=('__call__',), path=None):
    self._path= path
    HLProfiler.__init__(self,timer,funcNames)

  def getHLFuncId(self,fn,frame):
    '''return the high level function id for *frame*, if any.'''
    l= frame.f_locals
    s= l.get('self')
    gP= getattr(s,'getPhysicalPath',None)
    if gP is None: return
    # Try to work around a problem with funny classes returning
    #   instances of itself for "getPhysicalPath".
    #   "xmlrpclib._Method" is such a funny class
    #   Problem reported by "Pperegrina@Lastminute.com"
    #
    #   Note that a clean fix would require interfaces with
    #   a specific interface indicating that "getPhysicalPath" is
    #   the method we expect.
    s_class = getattr(s, '__class__', None)
    gpp_class = getattr(gP, '__class__', None)
    if s_class is not None and s_class is gpp_class: return
    # Five broke 'getPhysicalPath' for its view classes -- work around
    try: p= gP()
    except:
      _log.error("calling 'getPhysicalPath' failed for %r", s,
                 exc_info=sys.exc_info()
                 )
      return
    if type(p) is StringType: fi= p
    else: fi= '/'.join(p)
    return (fi,_Empty,fn) 

  def getTopFuncId(self):
    return (self._path,_Empty,'Request')


# $Log: ZopeProfiler.py,v $
# Revision 1.2  2011-11-13 09:52:57  dieter
# 2.0.2: compatibilty with Zope 2.12/2.13
#
# Revision 1.1.1.1  2008/08/18 10:17:30  dieter
# ZopeProfiler 2.0
#
# Revision 1.15  2006/10/13 20:19:09  dieter
# work around FIVE bug; allow to control whether profiling state is persistent or temporary
#
# Revision 1.14  2006/03/16 22:14:52  dieter
# replace our own function name based filtering by 'pstats' stdname based filtering;
# remove the unworking '__profile_information__' from the documentation and implementation
#
# Revision 1.13  2006/03/11 15:38:52  dieter
# Supports analysis of functions matched by a regular expression
# use my standard license
#
# Revision 1.12  2005/07/06 18:11:41  dieter
# Python 2.4.1 compatibility
# work around 'xmlrpclib' peculiarity'
#
# Revision 1.11  2005/03/26 10:09:23  dieter
# fix first time initialization (avoiding a 'ConflictError' during startup
#
# Revision 1.10  2004/10/21 17:35:29  dieter
# made compatible with Zope 2.7.3
#
# Revision 1.9  2003/12/07 12:42:43  dieter
# UI improvements; make Zope 2.8 compatible
#
# Revision 1.8  2003/06/28 08:41:12  dieter
# Version 1.0
#
# Revision 1.7  2003/05/13 16:12:05  dieter
# rename 'showDocumentation' to 'showInfo' to avoid a name clash with 'DocFinderEveryWhere'
#
# Revision 1.6  2003/04/03 18:28:37  dieter
# fix: used uninitialized '_timerName'
#
# Revision 1.5  2003/03/30 14:49:11  dieter
# Version 0.2
#
# Revision 1.3  2003/03/30 11:14:47  dieter
# selectable timer: CPU and real
#
# Revision 1.2  2003/02/02 17:00:19  dieter
# Python 2.2 compatibility
#
