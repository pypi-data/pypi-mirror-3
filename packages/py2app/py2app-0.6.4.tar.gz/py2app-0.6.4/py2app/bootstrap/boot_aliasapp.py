def _run(scriptpath):
    global __file__
    import os, sys, site
    sys.frozen = 'macosx_app'
    sys.argv[0] = __file__ = scriptpath
    execfile(scriptpath, globals(), globals())
