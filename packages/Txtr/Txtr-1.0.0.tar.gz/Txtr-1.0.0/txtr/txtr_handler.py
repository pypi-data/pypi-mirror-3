from txtr_menubar import *
from txtr_toolbar import *
from txtr_textview import *
from txtr_notebook import *
from txtr_statusbar import *
from txtr_about import *
from txtr_search import *
from txtr_printer import *
from txtr_welcome_screen import *
import mimetypes

class Handler:
	def __init__(self, mainwindow):
		self.mw = mainwindow
		self.searchbar = Search(self)
		self.searchbar.set_layout()
		
	def set_window_title(self, filename):
		if filename != None:
			title = self.split_filename(filename)
			self.mw.set_title('Txtr - ' + title)
		else:
			self.mw.set_title('Txtr - Untitled Document' )
		
	def get_file_type(self):
		filename = self.notebook.get_current_filename()
		if filename != None:
			filetype, encoding = mimetypes.guess_type(filename)
			return filetype
		else:
			return None
	
	def set_toolbar(self):
		self.toolbar = Toolbar(self)
		return self.toolbar
	
	def set_toolbar_actions(self, boolean):
		self.toolbar.actions['save'].set_sensitive(boolean)
		
	def set_notebook(self, filenames):
		if len(filenames) != 0:
			self.notebook = Notebook(self, False, filenames)
		else:
			self.notebook = Notebook(self, True, None)
		return self.notebook
	
	def set_welcome_screen(self):
		self.ws = WelcomeScreen(self)
		return self.ws
		
	def set_statusbar(self):
		self.statusbar = Statusbar()
		return self.statusbar
		
	def read_file(self, filename):
		try:
			f = open(filename, 'rb')
		except:
			d = Gtk.Dialog('Txtr - Error', self.mw, Gtk.DialogFlags.MODAL, Gtk.STOCK_OK, 1)
			msg = Gtk.Label('Cannot open file !')
			content = d.get_conteant_area()
			conteant.pack_start(msg, True, True, 10)
			d.show_all()
			if d.run() == 1:
				d.destroy()
		finally:
			content = f.read()
			f.close()
			return content
	
	def confirm_exit(self):
		d = Gtk.Dialog('Txtr - Unsaved Changes', self.mw, Gtk.DialogFlags.MODAL, None)
		d.set_resizable(False)
		d.set_destroy_with_parent(True)
		d.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
		d.add_button('Close without saving', -1)
		d.add_button(Gtk.STOCK_CANCEL, 0)
		d.add_button(Gtk.STOCK_SAVE, 1)
		d.set_default_response(0)
		contentarea = d.get_content_area()
		msg = Gtk.Label('Unsaved changes have been detected,\n What do you want to do?')
		contentarea.pack_start(msg, True, True, 25)
		d.show_all()
		return d
	
	def split_filename(self, filename):
		name = filename.split('/')
		name = name[-1]
		return name
			
	def on_click_new(self, data):
		self.notebook.new_tab(None)
		self.statusbar.push(self.statusbar.get_context_id('New Doc'), 'New document has been opened')
	
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
			self.statusbar.push(self.statusbar.get_context_id('Open Doc'), 'Document has been opened successfuly')
		d.destroy()
	
	def on_click_save(self, data):
		filename = self.notebook.get_current_filename()
		if filename != None:
			self.save_process(filename)
			name = self.split_filename(filename)
			self.notebook.update_tab_title(name)
			self.set_save_icon(False)
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
				self.set_save_icon(False)
				self.statusbar.push(self.statusbar.get_context_id('Save Doc'), 'Document has been saved successfuly')
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
		#doc.cut_text()
		iters = doc.buffer.get_selection_bounds()
		if iters:
			self.clipboard.set_text(doc.buffer.get_text(iters[0], iters[1], False), -1)
			self.clipboard.store()
			doc.buffer.delete(iters[0], iters[1])
		
	def on_click_copy(self, data):
		doc = self.notebook.get_current_doc()
		#doc.copy_text()
		iters = doc.buffer.get_selection_bounds()
		if iters:
			self.clipboard.set_text(doc.buffer.get_text(iters[0], iters[1], False), -1)
			self.clipboard.store()
		
	def on_click_paste(self, data):
		doc = self.notebook.get_current_doc()
		text = self.clipboard.wait_for_text()
		if text != None:
			doc.buffer.insert_at_cursoe(text, -1)
		#doc.paste_text()
	
	def on_search(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_for_text(text)
		
	def on_click_search(self, data):
		self.toolbar.search_entry.grab_focus()
		
	def on_click_search_forward(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_forward(text)
		
	def on_click_search_backward(self, data):
		text = self.toolbar.search_entry.get_text()
		doc = self.notebook.get_current_doc()
		doc.search_backward(text)
		
	def on_click_settings(self, data):
		pass
		
	def on_click_find_and_replace(self, data):
		d = Search()
		if d.run() == 0:
			d.destroy()
		
	def on_click_go_to(self, data):
		d = Gtk.Dialog()
		d.set_modal(True)
		d.add_button('Cancel', 0)
		d.add_button('Go To', 1)
		d.set_default_response(1)
		hbox = Gtk.Box()
		label = Gtk.Label('Go to line: ')
		entry = Gtk.Entry()
		hbox.pack_start(label, False, False, 5)
		hbox.pack_start(entry, False, False, 5)
		contentarea = d.get_content_area()
		contentarea.pack_start(hbox, True, True, 0)
		d.show_all()
		if d.run() == 1:
			line = entry.get_text()
			doc = self.notebook.get_current_doc()
			iter = doc.buffer.get_iter_at_line(int(line) - 1)
			doc.buffer.place_cursor(iter)
		d.destroy()
		
	def on_click_about(self, data):
		about = About()
		if about.run() == Gtk.ResponseType.CANCEL:
			about.destroy()
			
	def on_click_print(self, data):
		printer = Printer()
		d = printer.set_print_dialog()
		if d.run() == Gtk.ResponseType.CANCEL:
			d.destroy()
		
	def on_click_exit(self, data):
		Gtk.main_quit()
		
	def set_save_icon(self, boolean):
		self.toolbar.actions['save'].set_sensitive(boolean)
