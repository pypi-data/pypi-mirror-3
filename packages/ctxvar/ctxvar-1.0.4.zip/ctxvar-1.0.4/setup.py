from distutils.core import setup
import sys, os

if sys.argv[1] == 'test':
    sys.path.insert(0, os.path.dirname(__file__))
    import ctxvar
    r = ctxvar._test(ctxvar)
    failed, attempted = r
    if not failed:
        sys.stdout.write("%s tests ok\n"%attempted)
 
else:    
    version = '1.0.4'
    setup(
      name         = 'ctxvar',
      version      = version,
      py_modules   = ['ctxvar'],
      author       = 'Kay-Uwe (Kiwi) Lorenz',
      author_email = "kiwi@franka.dyndns.org",
      url          = 'http://ctxvar.readthedocs.org',
      description  = "Module to access variables defined in calling frames.",

      license = "New BSD License",
      )
