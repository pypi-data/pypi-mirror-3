import gtk
import time

class Logger:

	text_buffer = gtk.TextBuffer()
	nature_tag = []

	def __init__(self) :
		self.text_buffer.set_text("")
		self.nature_tag.append(gtk.TextTag('urgent'))
		self.nature_tag[0].set_property('background', '#FFAAAA')

		self.nature_tag.append(gtk.TextTag('info'))
		self.nature_tag[1].set_property('background', '#AAFFAA')

		self.nature_tag.append(gtk.TextTag('alert'))
		self.nature_tag[2].set_property('background', '#88EEFF')
		
		tag_table = self.text_buffer.get_tag_table()
		for tag in self.nature_tag : tag_table.add(tag)

	def get_buffer(self) : return self.text_buffer

	def append_line(self, other, sender_string, nature, line) :
		begin = self.text_buffer.get_start_iter()
		self.text_buffer.insert_with_tags(begin, '[' + time.strftime('%d %b %Y %H:%M:%S') + '] ')
		self.text_buffer.insert_with_tags(begin, sender_string, self.nature_tag[nature])
		self.text_buffer.insert_with_tags(begin, ' : ' + line + '\n')

	def get_new_logger_view(self):
		view = gtk.TextView()
		view_win = gtk.ScrolledWindow()
		view.set_buffer(self.get_buffer())
		view_win.add(view)
		return view_win

def get_new_logger() :
	return Logger()
