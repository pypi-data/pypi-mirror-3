from gi.repository import Gtk

class Printer(Gtk.PageSetup):
	def __init__(self):
		super(Printer, self).__init__()
		
	def set_print_dialog(self):
		d = Gtk.PrintUnixDialog()
		d.set_page_setup(self)
		return d
