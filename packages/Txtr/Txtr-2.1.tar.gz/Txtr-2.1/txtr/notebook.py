from gi.repository import *
from child import *

class Notebook(Gtk.Notebook):
	def __init__(self, handler):
		super(Notebook, self).__init__()
		self.handler = handler
		self.filenames = []
		#self.new_tab(None)
		self.connect('switch-page', self.page_changed)
		self.connect('page-removed', self.on_page_removed)
		self.connect('page-added', self.on_page_added)
		
	def new_tab(self, filename):
		label = Gtk.Box()
		label.set_orientation(Gtk.Orientation.HORIZONTAL)
		label.set_can_focus(False)
		if filename != None:
			titlestring = self.handler.split_filename(filename)
			content = self.handler.read_file(filename)
		else:
			titlestring = 'Untitled Document'
			content = ''
		self.filenames.append(filename)
		fileimage = Gtk.Image()
		fileimage.set_from_stock(Gtk.STOCK_FILE, Gtk.IconSize.MENU)
		title = Gtk.Label(titlestring)
		title.set_can_focus(False)
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
		close = Gtk.Button()
		close.set_relief(Gtk.ReliefStyle.NONE)
		close.set_image(image)
		close.set_can_focus(False)
		label.pack_start(fileimage, False, False, 0)
		label.pack_start(title, True, True, 0)
		label.pack_start(close, False, False, 0)
		label.show_all()
		self.child = Child(self.handler, content)
		self.append_page(self.child, label)
		self.set_tab_reorderable(self.child, True)
		close.connect('clicked', self.on_click_close, self.child)
		self.show_all()
		self.set_current_page(-1)
		
	def update_window_title(self, filename):
		self.handler.set_window_title(filename)
		
	def update_tab_title(self, name):
		child = self.get_current_child()
		label = Gtk.Box()
		label.set_orientation(Gtk.Orientation.HORIZONTAL)
		title = Gtk.Label(name)
		image = Gtk.Image()
		image.set_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU)
		close = Gtk.Button()
		close.set_image(image)
		label.pack_start(title, True, True, 0)
		label.pack_start(close, False, False, 0)
		label.show_all()
		self.set_tab_label(child, label)
		
	def get_doc(self, pagenum):
		child = self.get_nth_page(pagenum)
		doc = child.doc
		return doc
		
	def get_current_child(self):
		page = self.get_current_page()
		child = self.get_nth_page(page)
		return child
		
	def get_current_doc(self):
		page = self.get_current_page()
		child = self.get_nth_page(page)
		doc = child.doc
		return doc
		
	def get_current_filename(self):
		page = self.get_current_page()
		filename = self.filenames[page]
		return filename
		
	def on_click_close(self, data, child):
		result = child.doc.has_unsaved_changes()
		if result == True:
			d = self.handler.confirm_exit()
			response = d.run()
			if response == -1:
				self.close_tab(child)
			elif response == 0:
				pass
			elif response == 1:
				self.handler.save_request()
			d.destroy()
		else:
			self.close_tab(child)
			
	def close_tab(self, child):
		page = self.page_num(child)
		filename = self.filenames[page]
		self.filenames.remove(filename)
		self.remove_page(page)
	
	def page_changed(self, notebook, page, pagenum):
		filename = self.filenames[pagenum]
		self.update_window_title(filename)
		currentdoc = self.get_current_doc()
		currentdoc.do_highlight()
		currentdoc.grab_focus()
		self.handler.statusbar.clear()
				
	def on_page_removed(self, notebook, child, pagenum):
		if self.get_n_pages() == 0:
			self.handler.set_toolbar_actions(False)
			self.handler.statusbar.clear()
		else:
			pass

	def on_page_added(self, notebook, child, page_num):
		if self.get_n_pages() == 1:
			self.handler.set_toolbar_actions(True)
			self.handler.set_save_icon(False)
