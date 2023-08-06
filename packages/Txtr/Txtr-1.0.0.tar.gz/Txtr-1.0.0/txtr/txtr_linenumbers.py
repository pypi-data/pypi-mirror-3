from gi.repository import Gtk, Gdk

class LineNumbers(Gtk.TextView):
	def __init__(self, parent, docbuffer):
		super(LineNumbers, self).__init__()
		self.buffer = self.get_buffer()
		self.buffer.set_text('1')
		lines = docbuffer.get_line_count()
		self.set_background_color()
		self.set_lines(lines)
		self.set_right_margin(5)
		self.set_editable(False)
		self.set_can_focus(False)
		
	def set_background_color(self):
		self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.1,1.1,1.0,0))
		#self.override_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1.6,1.6,1.6,1))
		
	def set_lines(self, lines):
		self.buffer.set_text('')
		for l in range(1, lines+1):
			self.buffer.insert(self.buffer.get_end_iter(), '%d\n' % l)
