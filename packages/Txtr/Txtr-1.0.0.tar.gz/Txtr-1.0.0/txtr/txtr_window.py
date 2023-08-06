from gi.repository import Gtk
from txtr_handler import *

class Window(Gtk.Window):
	def __init__(self, filenames):
		super(Window, self).__init__()
		self.set_title('Txtr')
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_default_size(900,550)
		self.handler = Handler(self)
		self.filenames = filenames
		self.set_layout()
		self.connect("destroy", self.quit_app)
		self.show_all()

		
	def set_layout(self):
		layout = Gtk.Box() 
		layout.set_orientation(Gtk.Orientation.VERTICAL)
		toolbar = self.handler.set_toolbar()
		searchbar = self.handler.searchbar
		notebook = self.handler.set_notebook(self.filenames)
		welcomescreen = self.handler.set_welcome_screen()
		statusbar = self.handler.set_statusbar()
		layout.pack_start(toolbar, False, True, 0)
		layout.pack_start(notebook, True, True, 0)
		layout.pack_start(welcomescreen, True, True, 0)
		layout.pack_start(searchbar, False, True, 0)
		searchbar.hide()
		layout.pack_start(statusbar, False, True, 0)
		self.add(layout)

				
	def quit_app(self, widget):
		Gtk.main_quit()
