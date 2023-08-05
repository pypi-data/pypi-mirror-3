try:
        import IPython
except Exception,e:
        raise RuntimeError("Error importing IPython (%s)" % str(e))

if IPython.__version__[:4] == '0.10' :
  from ipython_view_10 import *
else :
  from ipython_view_11 import *
