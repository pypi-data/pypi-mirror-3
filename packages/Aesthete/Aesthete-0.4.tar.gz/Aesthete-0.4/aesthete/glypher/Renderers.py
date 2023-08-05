import glypher as g
import traceback
from ..utils import debug_print
import re
import pango
import pangocairo
import cairo
import Image

render_library = {}

class GlypherRendering :
	shape = None
	size = None
	height = None
	width = None
	image = None
	size = 20.0

	def __init__(self, shape, code = None, setup = False, italic = False) :
		self.shape = shape
		if setup : self.setup(shape, code)

	def setup(self, shape, code = None) :
		self.image = cairo.SVGSurface(None, self.size/2, self.size)
		cr = cairo.Context(self.image)
		cr.set_source_rgb(1.0,1.0,1.0)
		cr.rectangle(0, 0, self.size/2, self.size)
		self.height = g.stp*self.size; self.width = g.stp*self.size/2;
		cr.fill()
	
	def draw(self, size, cr = None, l = 0, r = 0, colour = [0.0, 0.0, 0.0]) :
		cr.save()
		cr.set_source_rgb(1.0,1.0,1.0)
		cr.rectangle(0, 0, size/2, size)
		cr.fill()
		cr.restore()

class GlypherPangoRendering (GlypherRendering):
	font = "sans"
	#font = { 'normal' : "sans", 'italic' : "sans italic", 'bold' : "sans bold", 'bold italic' : "sans italic bold" }
	def get_font(self, font_name = None, italic = False, bold = False) :
		return (self.font if font_name is None else font_name)+(" bold" if bold else "")+(" italic" if italic else "")
		#return self.font[('bold italic' if bold else 'italic') if italic else ('bold' if bold else 'normal')]

	def draw(self, size, cr = None, l = 0, r = 0, colour = [0.0, 0.0, 0.0], ink = False, italic = False, bold = False, font_name = None) :
		if cr == None :
			image = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(size), int(size))
			cr = cairo.Context(image)
		cr.set_source_rgb(*colour)
		pcr = pangocairo.CairoContext(cr)
		layout = pcr.create_layout()
		#layout.set_font_description(pango.FontDescription("LMMathItalic12 "+str(size/2)))
		layout.set_font_description(pango.FontDescription(self.get_font(font_name, italic, bold)+' '+str(size/2)))
		layout.set_text(self.shape)
		met = layout.get_pixel_extents()
		if ink :
			height = met[0][3]; width = met[0][2]
			cr.move_to(l - (met[0][0]-met[1][0]),r - (met[0][1]-met[1][1]))
		else :
			height = met[1][3]; width = met[1][2]
			cr.move_to(l, r)
		asc = layout.get_context().get_metrics(layout.get_font_description()).get_ascent()/pango.SCALE
		desc = layout.get_context().get_metrics(layout.get_font_description()).get_descent()/pango.SCALE
		pcr.show_layout(layout)
		# FIXME: this is a bit of a botch to guess where the midline of an equals or minus lies
		return (height, width, height*0.5 if ink else desc+0.4*(asc-desc))

class GlypherPangoCMURendering (GlypherPangoRendering):
	font = "CMU Serif"
	#font = { 'normal' : "CMU Serif", 'italic' : "CMU Serif italic", \
	#	 'bold' : "CMU Serif bold", \
	#	 'bold italic' : "CMU Serif italic bold" }
class GlypherPangoLLRendering (GlypherPangoRendering):
	font = "Linux Libertine"

class GlypherPangoCMMapRendering (GlypherPangoRendering):
	font = "cmmi10"
	cm_size_coeff = 1.0
	cm_vertical_offset = 0.0
	def __init__(self, shape, code = None, setup = False) :
		cmi = get_cm_index()
		if shape in cmi :
			self.font = cmi[shape][0]
			self.cm_size_coeff = cmi[shape][2]
			self.cm_vertical_offset = cmi[shape][3]
			shape = cmi[shape][1]
		GlypherPangoRendering.__init__(self, shape, code, setup)

	def draw(self, size, cr = None, l = 0, r = 0, colour = [0.0, 0.0, 0.0]) :
		if (cr) : cr.save(); cr.translate(0, -self.cm_vertical_offset)
		(rh,rw) = GlypherPangoRendering.draw(self, size*self.cm_size_coeff, cr, l, r, colour)
		if (cr) : cr.restore()
		return (rh,rw)

class GlypherTeXRendering (GlypherRendering):
	def setup(self, shape, size, code = None) :
		self.shape = shape
		self.size = size
		plain = tex.Style("plain", "", "\\bye\n")

		codestr = string.replace(shape, ' ', '_')
		codestr = string.replace(codestr, '\\', '@')
		codestr = string.replace(codestr, '$', '#')
		fn = "/tmp/aes-glypher-TeX_" + codestr
		if not os.path.exists(fn+'.png') :
	    		(dvi, log) = tex.tex(plain, shape if code == None else code)
			dvi.write(open(fn+'.dvi', 'wb'))
			os.system('convert -crop 8x20+90+67 ' + fn + '.dvi ' + fn +'.png 2> /dev/null')
		self.image = cairo.ImageSurface.create_from_png(fn+'.png')
		self.height = self.image.get_height()
		self.width = self.image.get_width()
		#os.system('rm ' + fn + '*')
		

#render_library[(' ',10)] = GlypherPangoRendering(' ', 10, None, False)
#render_library[(' ',10)].image = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 20)

def find_rendering(shape, code = None, italic = False, bold = False) :
	if g.use_rendering_library :
		if not (shape, italic) in render_library :
			render_library[(shape, italic)] = GlypherPangoLLRendering(shape, code, italic=italic, bold=bold)
		return render_library[(shape, italic)]
	else :
		return GlypherPangoLLRendering(shape, code, italic=italic)
