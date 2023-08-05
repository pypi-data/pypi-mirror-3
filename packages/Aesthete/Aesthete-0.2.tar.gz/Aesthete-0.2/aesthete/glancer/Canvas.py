from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as mpl_Canvas
from ..utils import debug_print

class GlancerCanvas(mpl_Canvas) :
    def __init__(self, fig) :
        mpl_Canvas.__init__(self, fig)
