from gi.repository import Gtk

class Toolbar(Gtk.Toolbar):
	def __init__(self, handler):
		super(Toolbar, self).__init__()
		self.handler = handler
		context = self.get_style_context()
		context.add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
		self.set_layout()
		self.set_can_focus(False)
		self.show_all()
		
	def set_layout(self):
		self.actions = {}
		#
		self.actions['new'] = Gtk.ToolButton()
		self.actions['new'].set_stock_id(Gtk.STOCK_NEW)
		self.actions['new'].set_tooltip_text('Create New Empty Document')
		self.actions['new'].connect('clicked', self.handler.on_click_new)
		self.insert(self.actions['new'], -1)
		#
		self.actions['open'] = Gtk.ToolButton()
		self.actions['open'].set_stock_id(Gtk.STOCK_OPEN)
		self.actions['open'].set_label('Open Doc')
		
		self.actions['open'].set_tooltip_text('Open Document')
		self.actions['open'].connect('clicked', self.handler.on_click_open)
		self.insert(self.actions['open'], -1)
		#
		self.actions['save'] = Gtk.ToolButton()
		self.actions['save'].set_stock_id(Gtk.STOCK_SAVE)
		self.actions['save'].set_label('Save Doc')
		self.actions['save'].set_tooltip_text('Save Document')
		self.actions['save'].set_sensitive(False)
		self.actions['save'].connect('clicked', self.handler.on_click_save)
		self.insert(self.actions['save'], -1)	
		#
		self.actions['separator'] = Gtk.SeparatorToolItem()
		self.insert(self.actions['separator'], -1)
		#
		self.actions['undo'] = Gtk.ToolButton()
		self.actions['undo'].set_stock_id(Gtk.STOCK_UNDO)
		self.actions['undo'].set_tooltip_text('Undo')
		self.actions['undo'].set_sensitive(False)
		self.actions['undo'].connect('clicked', self.handler.on_click_undo)
		self.insert(self.actions['undo'], -1)
		#
		self.actions['redo'] = Gtk.ToolButton()
		self.actions['redo'].set_stock_id(Gtk.STOCK_REDO)
		self.actions['redo'].set_tooltip_text('Redo')
		self.actions['redo'].set_sensitive(False)
		self.actions['redo'].connect('clicked', self.handler.on_click_redo)
		self.insert(self.actions['redo'], -1)
		#
		#self.actions['separator1'] = Gtk.SeparatorToolItem()
		#self.insert(self.actions['separator1'], -1)
		#
		#self.actions['cut'] = Gtk.ToolButton()
		#self.actions['cut'].set_stock_id(Gtk.STOCK_CUT)
		#self.actions['cut'].set_tooltip_text('Cut text')
		#self.actions['cut'].connect('clicked', self.handler.on_click_cut)
		#self.insert(self.actions['cut'], -1)
		#
		#self.actions['copy'] = Gtk.ToolButton()
		#self.actions['copy'].set_stock_id(Gtk.STOCK_COPY)
		#self.actions['copy'].set_tooltip_text('Copy text')
		#self.actions['copy'].connect('clicked', self.handler.on_click_copy)
		#self.insert(self.actions['copy'], -1)
		#
		#self.actions['paste'] = Gtk.ToolButton()
		#self.actions['paste'].set_stock_id(Gtk.STOCK_PASTE)
		#self.actions['paste'].set_tooltip_text('Paste text')
		#self.actions['paste'].connect('clicked', self.handler.on_click_paste)
		#self.insert(self.actions['paste'], -1)
		#
		self.actions['spacer'] = Gtk.ToolItem()
		self.actions['spacer'].set_expand(True)
		self.insert(self.actions['spacer'], -1)
		#
		#self.actions['search'] = Gtk.ToolItem()
		#self.search_entry = Gtk.Entry()
		#self.search_entry.set_icon_from_stock(Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_FIND)
		#self.search_entry.set_placeholder_text('Type to search ..')
		#self.search_entry.connect('changed', self.handler.on_search)
		#self.actions['search'].add(self.search_entry)
		#self.actions['search_backward'] = Gtk.ToolButton()
		#self.actions['search_backward'].set_stock_id(Gtk.STOCK_GO_UP)
		#self.actions['search_backward'].connect('clicked', self.handler.on_click_search_backward)
		#self.actions['search_forward'] = Gtk.ToolButton()
		#self.actions['search_forward'].set_stock_id(Gtk.STOCK_GO_DOWN)
		#self.actions['search_forward'].connect('clicked', self.handler.on_click_search_forward)
		#self.insert(self.actions['search'], -1)
		#self.insert(self.actions['search_backward'], -1)
		#self.insert(self.actions['search_forward'], -1)
		#
		self.actions['search'] = Gtk.ToolButton()
		self.actions['search'].set_stock_id(Gtk.STOCK_FIND)
		self.insert(self.actions['search'], -1)
		#
		self.actions['settings'] = Gtk.MenuToolButton()
		self.actions['settings'].set_stock_id(Gtk.STOCK_PREFERENCES)
		menu = self.settings_menu()
		self.actions['settings'].set_menu(menu)
		self.actions['settings'].connect('clicked', self.on_click_settings)
		self.insert(self.actions['settings'], -1)

	def on_click_settings(self, data):
		menu = self.settings_menu()
		menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())
		menu.show_all()
		
		
	def settings_menu(self):
		menu = Gtk.Menu()
		settings = Gtk.MenuItem('Settings Manager')
		about = Gtk.MenuItem('About')
		about.connect('activate', self.handler.on_click_about)
		menu.append(settings)
		menu.append(about)
		menu.show_all()
		return menu
		
