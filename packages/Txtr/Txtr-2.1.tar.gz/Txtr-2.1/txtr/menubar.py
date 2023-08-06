from gi.repository import Gtk

class Menubar(Gtk.MenuBar):
	def __init__(self, handler):
		super(Menubar, self).__init__()
		self.handler = handler
		self.set_file_menu()
		self.set_edit_menu()
		self.set_view_menu()
		self.set_search_menu()
		self.set_help_menu()
		self.show_all()
		
	def set_file_menu(self):
		filerootmenu = Gtk.MenuItem('File')
		filemenu = Gtk.Menu()
		newdoc = Gtk.MenuItem('New Document')
		newdoc.connect('activate', self.handler.on_click_new)
		opendoc = Gtk.MenuItem('Open Document')
		opendoc.connect('activate', self.handler.on_click_open)
		savedoc = Gtk.MenuItem('Save Document')
		savedoc.connect('activate', self.handler.on_click_save)
		separator = Gtk.SeparatorMenuItem()
		exititem = Gtk.MenuItem('Exit')
		exititem.connect('activate', self.handler.on_click_exit)
		filemenu.append(newdoc)
		filemenu.append(opendoc)
		filemenu.append(savedoc)
		filemenu.append(separator)
		filemenu.append(exititem)
		filerootmenu.set_submenu(filemenu)
		self.append(filerootmenu)
	
	def set_edit_menu(self):
		editrootmenu = Gtk.MenuItem('Edit')
		editmenu = Gtk.Menu()
		cut = Gtk.MenuItem('Cut Text')
		copy = Gtk.MenuItem('Copy Text')
		paste = Gtk.MenuItem('Paste Text')
		editmenu.append(cut)
		editmenu.append(copy)
		editmenu.append(paste)
		editrootmenu.set_submenu(editmenu)
		self.append(editrootmenu)
		
	def set_view_menu(self):
		viewrootmenu = Gtk.MenuItem('View')
		viewmenu = Gtk.Menu()
		toolbar = Gtk.CheckMenuItem('Toolbar')
		statusbar = Gtk.CheckMenuItem('Statusbar')
		linenumbers = Gtk.CheckMenuItem('Line Numbers')
		viewmenu.append(toolbar)
		viewmenu.append(statusbar)
		viewmenu.append(linenumbers)
		viewrootmenu.set_submenu(viewmenu)
		self.append(viewrootmenu)
	
	def set_search_menu(self):
		searchrootmenu = Gtk.MenuItem('search')
		searchmenu = Gtk.Menu()
		find = Gtk.MenuItem('Find')
		findandreplace = Gtk.MenuItem('Find and replace')
		searchmenu.append(find)
		searchmenu.append(findandreplace)
		searchrootmenu.set_submenu(searchmenu)
		self.append(searchrootmenu)
		
	def set_help_menu(self):
		helprootmenu = Gtk.MenuItem('Help')
		helpmenu = Gtk.Menu()
		shortcuts = Gtk.MenuItem('Shortcuts')
		helpdialog = Gtk.MenuItem('Help')
		about = Gtk.MenuItem('About')
		helpmenu.append(shortcuts)
		helpmenu.append(helpdialog)
		helpmenu.append(about)
		helprootmenu.set_submenu(helpmenu)
		self.append(helprootmenu)
		

		
