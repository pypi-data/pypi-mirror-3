from gi.repository import Gtk
from handler import *

class Window(Gtk.Window):
	def __init__(self, filename):
		super(Window, self).__init__()
		self.filename = filename
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_default_size(700,550)
		self.set_title('Txtr')
		self.handler = Handler(self)
		self.set_layout()
		self.show_all()
		self.connect("destroy", self.quit_app)
		
	def set_layout(self):
		layout = Gtk.Box() 
		layout.set_orientation(Gtk.Orientation.VERTICAL)
		menubar = self.handler.menubar
		toolbar = self.handler.toolbar
		notebook = self.handler.notebook
		statusbar = self.handler.statusbar
		layout.pack_start(menubar, False, True, 0)
		layout.pack_start(toolbar, False, True, 0)
		layout.pack_start(notebook, True, True, 0)
		layout.pack_start(statusbar, False, True, 0)
		self.add(layout)
		#notebook.get_current_doc().grab_focus()
		notebook.new_tab(self.filename)
				
	def quit_app(self, widget):
		Gtk.main_quit()
