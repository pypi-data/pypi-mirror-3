from tahrir.toolbar import *
from tahrir.textview import *
from tahrir.notebook import *

class Handler:
	def __init__(self, mainwindow):
		self.mw = mainwindow
		self.filenames = {}
		self.set_notebook()
		self.set_toolbar()
		
	def set_window_title(self, filename):
		if filename != None:
			title = self.split_filename(filename)
			self.mw.set_title('Txtr - ' + title)
		else:
			self.mw.set_title('Txtr - Untitled Document' )
		
	def get_file_type(self):
		filename = self.notebook.get_current_filename()
		if filename != None:
			filetype = filename.split('.')
			filetype = filetype[-1]
		else:
			filetype = None
		return filetype
		
	def set_toolbar(self):
		self.toolbar = Toolbar(self)
	
	def set_toolbar_actions(self, boolean):
		self.toolbar.actions['save'].set_sensitive(boolean)
		self.toolbar.actions['cut'].set_sensitive(boolean)
		self.toolbar.actions['copy'].set_sensitive(boolean)
		self.toolbar.actions['paste'].set_sensitive(boolean)
		self.toolbar.search_entry.set_sensitive(boolean)
		self.toolbar.actions['search_forward'].set_sensitive(boolean)
		self.toolbar.actions['search_backward'].set_sensitive(boolean)
		
	def set_notebook(self):
		self.notebook = Notebook(self)
		
	def read_file(self, filename):
		f = open(filename, 'r')
		content = f.read()
		f.close()
		return content
	
	def confirm_exit(self):
		d = Gtk.Dialog()
		d.add_button('Close Without Saving', -1)
		d.add_button(Gtk.STOCK_CANCEL, 0)
		d.add_button(Gtk.STOCK_SAVE, 1)
		d.set_default_response(1)
		contentarea = d.get_content_area()
		msg = Gtk.Label('Save changes to document before closing ?\n')
		contentarea.pack_start(msg, True, True, 5)
		d.show_all()
		return d
		
	def on_click_new(self, data):
		self.notebook.new_tab(None)
		
	def split_filename(self, filename):
		name = filename.split('/')
		name = name[-1]
		return name
		
	def on_click_open(self, data):
		d = Gtk.FileChooserDialog("Open File", None, Gtk.FileChooserAction.OPEN, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
				, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
		d.set_default_response(Gtk.ResponseType.ACCEPT)
		if d.run() == Gtk.ResponseType.ACCEPT:
			filename = d.get_filename()
			self.notebook.new_tab(filename)
			name = self.split_filename(filename)
			#self.mw.set_title('Tahrir - ' + name)
			doc = self.notebook.get_current_doc()
			doc.set_modified(False)
		d.destroy()
	
	def on_click_save(self, data):
		filename = self.notebook.get_current_filename()
		if filename != None:
			self.save_process(filename)
		else: 
			d = Gtk.FileChooserDialog("Save File", None, Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL
				, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT))
			d.set_do_overwrite_confirmation(True)
			if d.run() == Gtk.ResponseType.ACCEPT:
				filename = d.get_filename()
				self.notebook.filenames.append(filename)
				name = self.split_filename(filename)
				self.save_process(filename)
				self.mw.set_title('Tahrir - ' + name)
				self.notebook.update_tab_title(name)
			d.destroy()
				
	def save_process(self, filename):
		f = open(filename, 'w')
		doc = self.notebook.get_current_doc()
		contents = doc.get_text()
		f.write(contents)
		f.close()
		doc.set_modified(False)
		
	def on_click_undo(self, data):
		pass
		
	def on_click_redo(self, data):
		pass
		
	def on_click_cut(self, data):
		doc = self.notebook.get_current_doc()
		doc.cut_text()
		
	def on_click_copy(self, data):
		doc = self.notebook.get_current_doc()
		doc.copy_text()
		
	def on_click_paste(self, data):
		doc = self.notebook.get_current_doc()
		doc.paste_text()
	
	def on_search(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_for_text(text)
		
	def on_click_search_forward(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_forward(text)
		
	def on_click_search_backward(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_backward(text)
		
	def on_click_about(self, data):
		pass
		
	def on_click_settings(self, data):
		pass
		
	def set_save_icon(self, boolean):
		self.toolbar.actions['save'].set_sensitive(boolean)
