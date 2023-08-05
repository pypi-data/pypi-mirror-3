import gtk

class PreferencesTableMaker :
	cells = None
	save_preferences_methods = None
	headings = 0
	def __init__ (self) :
		self.cells = []
		self.save_preferences_methods = []
	def append_row(self, left_text, right_widget, indicator = "") :
		self.cells.append((left_text, right_widget, indicator))
	def save_preferences(self) :
		for s in self.save_preferences_methods :
			s.save_preferences()
	def append_heading(self, text) :
		self.cells.append((text, None, None))
		self.headings += 1
	def make_table(self,
                xoptions=gtk.EXPAND|gtk.FILL,
                yoptions=gtk.SHRINK) :
		table = gtk.Table(len(self.cells) + self.headings, 3)
		r = 0
		for row in self.cells :
			if row[1] == None :
				label = gtk.Label()
				label.set_markup("<b>"+row[0]+"</b>")
				label.set_alignment(0.1, 0)
				table.attach(gtk.HSeparator(), 0, 3, r, r+1)
				r += 1
				table.attach(label, 0, 2, r, r+1, xoptions, yoptions)
			else :
				label = gtk.Label(row[0])
				label.set_alignment(0, 0)
				label.set_padding(0, 3)
				indicator = gtk.Label(row[2])
				indicator.set_size_request(20,20)
				table.attach(indicator, 0, 1, r, r+1, xoptions, yoptions) # Can use this for indicators
				table.attach(label, 1, 2, r, r+1, xoptions, yoptions)
				table.attach(row[1], 2, 3, r, r+1, xoptions, yoptions)
			r += 1
		return table
