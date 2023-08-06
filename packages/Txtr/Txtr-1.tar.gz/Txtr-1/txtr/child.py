from gi.repository import *
from tahrir.textview import *
from tahrir.linenumbers import *

class Child(Gtk.ScrolledWindow):
	def __init__(self, handler, content):
		super(Child, self).__init__()
		self.handler = handler
		self.content = content
		self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		self.set_layout()
		
	def set_layout(self):
		layout = Gtk.Box()
		layout.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.doc = Doc(self, self.handler, self.content)
		self.doc.grab_focus()
		self.linenumbers = LineNumbers(self, self.doc.buffer)
		layout.pack_start(self.linenumbers, False, False, 0)
		layout.pack_start(self.doc, True, True, 0)
		layout.show_all()
		self.add_with_viewport(layout)
		
		
	

