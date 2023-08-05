import cairo

def draw_inverse_blush(cr, length, height, colour=(0,0,0), thickness=5) :
	cr.save()
	cr.rel_line_to(length, 0)
	cr.rel_line_to(0, height)
	cr.rel_line_to(-length, 0)
	cr.rel_line_to(0, -height)
	cr.close_path()
	fe = cr.fill_extents()
	blush_grad = cairo.LinearGradient(fe[0]+length/2,fe[1],fe[0]+length/2,fe[3])
	colour = list(colour)+[0]
	blush_grad.add_color_stop_rgba(0.4, *colour); colour[3] = 1
	blush_grad.add_color_stop_rgba(0, *colour)
	cr.set_source(blush_grad)
	cr.fill()
	cr.move_to(fe[0],fe[1])
	cr.rel_line_to(0, thickness)
	cr.move_to(fe[0],fe[1])
	cr.rel_line_to(length, 0)
	cr.rel_line_to(0, thickness)
	cr.set_source_rgba(*colour)
	cr.stroke()
	cr.restore()

def draw_full_blush(cr, length, height, colour=(0,0,0)) :
	pt = cr.get_current_point()
	cr.rel_move_to(0, -height)
	draw_inverse_blush	(cr, length, height, colour, height/2)
	cr.move_to(*pt)
	draw_blush		(cr, length, colour, height/2)

def draw_blush(cr, length, colour=(0,0,0), thickness=5) :
	cr.save()
	cr.set_source_rgb(*colour)
	cr.rel_line_to(length, 0)
	cr.rel_line_to(0, -thickness)
	cr.rel_move_to(-length, 0)
	cr.rel_line_to(0, thickness)
	cr.set_line_width(2.0)
	fe = cr.fill_extents()
	cr.stroke()

	cr.move_to(fe[0], fe[1])
	cr.rel_line_to(0, thickness)
	cr.rel_line_to(length, 0)
	cr.rel_line_to(0, -thickness)
	cr.rel_line_to(-length, 0)
	cr.close_path()
	blush_grad = cairo.LinearGradient(fe[0]+length/2,fe[1],fe[0]+length/2,fe[3])
	colour = list(colour)+[0]
	blush_grad.add_color_stop_rgba(0, *colour); colour[3] = 1
	blush_grad.add_color_stop_rgba(1, *colour)
	cr.set_source(blush_grad)
	cr.fill()
	#cr.clip()
	#cr.mask(blush_grad)
	cr.restore()

# By Helton Moraes (heltonbiker at gmail dot com) c/o http://www.cairographics.org/cookbook/roundedrectangles/
# (Method D)
def trace_rounded(cr, area, radius):
    """ draws rectangles with rounded (circular arc) corners """
    from math import pi
    a,b,c,d=area

    #slight change
    cr.move_to(a, c + radius)

    cr.arc(a + radius, c + radius, radius, 2*(pi/2), 3*(pi/2))
    cr.arc(b - radius, c + radius, radius, 3*(pi/2), 4*(pi/2))
    cr.arc(b - radius, d - radius, radius, 0*(pi/2), 1*(pi/2))  # ;o)
    cr.arc(a + radius, d - radius, radius, 1*(pi/2), 2*(pi/2))
    cr.close_path()
