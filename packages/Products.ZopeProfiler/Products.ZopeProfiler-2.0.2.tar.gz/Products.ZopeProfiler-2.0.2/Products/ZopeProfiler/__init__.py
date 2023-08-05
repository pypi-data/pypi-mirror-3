#       $Id: __init__.py,v 1.2 2011-11-13 09:52:57 dieter Exp $
from ZopeProfiler import _hookZServerPublisher, _initializeModule, \
     ZopeProfiler

_hookZServerPublisher()

def initialize(context):
  app = context._ProductContext__app
  no_product_install = app is None
  if no_product_install:
    # must open a secondary ZODB connection to access "Control_Panel"
    #  Note: in general, it is dangerous to access the same ZODB from
    #    different connections in the same transaction (deadlock may occur)
    #    In our special case, our connection should be the only writing one.
    #    If necessary, we could abort an existing transaction.
    from transaction import commit # to be used later
    from Zope2 import app as z_app
    app = z_app()
  try:
    control_panel = app.Control_Panel
    zpid = ZopeProfiler.id
    zp = getattr(control_panel, zpid, None)
    if zp is None:
      zp = ZopeProfiler()
      control_panel._setObject(zpid, zp)
      if no_product_install: commit() # to ensure, `ZopeProfiler` is installed
    _initializeModule(zp)
  finally:
    if no_product_install: app._p_jar.close()
