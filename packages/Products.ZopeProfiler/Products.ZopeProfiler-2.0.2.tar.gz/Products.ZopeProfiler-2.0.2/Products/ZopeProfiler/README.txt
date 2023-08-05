ZopeProfiler

  ZopeProfiler provides profiling support for Zope.
  
  It can derive both high and low level timing statistics.
  High level means Zope object call level, while low level
  is the Python function call level.

  Unlike the standard Zope profiling support, ZopeProfiler
  does not bring Zope into effective single user mode.
  Zope continues to work as usual.

  ZopeProfiler can be dynamically enabled/disabled.
  When disabled, there is only a negligible runtime
  penalty. When enabled, profiling slows down Zope
  considerably.

  ZopeProfiler installs itself through "monkey patching".
  You will then find a ZopeProfiler instance in your "Control_Panel".
  (You need ``enable-product-installation on`` for ZopeProfiler
  to be able install itself in the "Control_Panel".)
  Please read the "Info" tab for further information.
