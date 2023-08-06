from gi.repository import *

class LineNumbers(Gtk.TextView):
	def __init__(self, parent, docbuffer):
		super(LineNumbers, self).__init__()
		self.buffer = self.get_buffer()
		self.buffer.set_text('1')
		self.set_right_margin(5)
		self.set_editable(False)
		lines = docbuffer.get_line_count()
		self.set_lines(lines)
		self.set_can_focus(False)
		
	def set_lines(self, lines):
		self.buffer.set_text('')
		for l in range(1, lines+1):
			self.buffer.insert(self.buffer.get_end_iter(), '%d\n' % l)
		
