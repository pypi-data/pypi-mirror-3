from gi.repository import Gtk
from window import Window

class Greet(Gtk.Window):
	def __init__(self):
		super(Greet, self).__init__()
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_default_size(400,300)
		self.set_layout()
		self.connect('destroy', self.destroy_window)
		
	def set_layout(self):
		box = Gtk.Box()
		box.set_orientation(Gtk.Orientation.VERTICAL)
		box.set_homogeneous(False)
		label = Gtk.Label("Please choose a source to view")
		button = Gtk.Button()
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.DIALOG)
		button.set_image(image)
		button.set_relief(Gtk.ReliefStyle.NONE)
		button.set_can_focus(False)
		button.connect('clicked', self.on_click_open)
		box.pack_start(label, False, True, 50)
		box.pack_start(button, False, True, 0)
		self.add(box)
	
	def on_click_open(self, data):
		d = Gtk.FileChooserDialog("Open File", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
				, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		d.set_default_response(Gtk.ResponseType.ACCEPT)
		if d.run() == Gtk.ResponseType.ACCEPT:
			filename = d.get_filename()
			self.hide()
			window = Window(filename)
			statusbar = window.handler.statusbar
			statusbar.push(statusbar.get_context_id('Open Doc'), 'Document has been opened successfuly')
		d.destroy()
		
	def destroy_window(self, data):
		Gtk.main_quit()
