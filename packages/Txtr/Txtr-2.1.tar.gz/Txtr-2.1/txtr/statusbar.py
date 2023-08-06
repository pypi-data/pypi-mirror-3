from gi.repository import Gtk

class Statusbar(Gtk.Statusbar):
	def __init__(self):
		super(Statusbar, self).__init__()
		
	def clear(self):
		self.push(self.get_context_id('space'), '')
