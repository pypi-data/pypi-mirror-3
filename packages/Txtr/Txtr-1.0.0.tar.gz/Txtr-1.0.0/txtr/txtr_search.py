from gi.repository import *

class Search(Gtk.Toolbar):
	def __init__(self, handler):
		super(Search, self).__init__()
		self.handler = handler
		
	def set_layout(self):
		self.actions = {}
		self.actions['search'] = Gtk.ToolItem()
		self.search_entry = Gtk.Entry()
		self.search_entry.set_icon_from_stock(Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_FIND)
		self.search_entry.set_placeholder_text('Type to search ..')
		#self.search_entry.connect('changed', self.handler.on_search)
		self.actions['search'].add(self.search_entry)
		self.actions['search_backward'] = Gtk.ToolButton()
		self.actions['search_backward'].set_stock_id(Gtk.STOCK_GO_UP)
		self.actions['search_backward'].connect('clicked', self.handler.on_click_search_backward)
		self.actions['search_forward'] = Gtk.ToolButton()
		self.actions['search_forward'].set_stock_id(Gtk.STOCK_GO_DOWN)
		#self.actions['search_forward'].connect('clicked', self.handler.on_click_search_forward)
		self.insert(self.actions['search'], -1)
		self.insert(self.actions['search_backward'], -1)
		self.insert(self.actions['search_forward'], -1)
		
