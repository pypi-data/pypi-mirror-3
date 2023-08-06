from gi.repository import Gtk

class About(Gtk.AboutDialog):
	def __init__(self):
		super(About, self).__init__()
		self.set_program_name('Txtr')
		self.set_version('2.1')
		self.set_copyright('Copyrights reserved for Massive Bytes, 2012.')
		self.set_license('GPL v3')
		self.set_license_type(Gtk.License.GPL_3_0)
		self.set_authors(['Eslam Mostafa'])	
		self.set_comments('Txtr is a simple, neat and elegant text editor designed for linux.')
		self.connect('destroy', self.destroy_dialog)
		
	def destroy_dialog(self, data):
		self.destroy()
