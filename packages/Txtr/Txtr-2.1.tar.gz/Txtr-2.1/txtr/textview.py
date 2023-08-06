from gi.repository import Gtk

class Doc(Gtk.TextView):
	def __init__(self, parent, handler, contents):
		super(Doc, self).__init__()
		self.parent = parent
		self.handler = handler
		self.contents = contents
		self.set_left_margin(5)
		
		self.buffer = self.get_buffer()
		self.set_text(contents)
		fonttag = self.buffer.create_tag('Font')
		fonttag.set_property('font', 'Ubuntu Mono 12')
		self.buffer.apply_tag(fonttag, self.buffer.get_start_iter(), self.buffer.get_end_iter())
		self.buffer.connect("changed", self.buffer_changed)
		self.buffer.connect("modified-changed", self.buffer_modified)
		self.set_highlighter()
		self.set_clipboard()
		self.set_search_tag()
		self.set_can_focus(True)
		self.grab_focus()
		self.show_all()
	
	def set_modified(self, boolean):
		self.buffer.set_modified(boolean)
	
	def buffer_modified(self, data):
		if self.buffer.get_modified() == True:
			self.handler.toolbar.actions['save'].set_sensitive(True)
		else:
			self.handler.toolbar.actions['save'].set_sensitive(False)
			
	def has_unsaved_changes(self):
		return self.buffer.get_modified()
		
	def get_text(self):
		contents = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
		return contents
		
	def set_text(self, text):
		self.buffer.set_text(text, -1)
		
	def set_clipboard(self):
		self.clipboard = Gtk.Clipboard()
		
	def set_search_tag(self):
		self.searchtag = self.buffer.create_tag('yellowBackground')
		self.searchtag.set_property('background', 'yellow')
		
	def cut_text(self):
		self.buffer.cut_clipboard(self.clipboard, False)
		
	def copy_text(self):
		self.buffer.copy_clipboard(self.clipboard)
		
	def paste_text(self):
		self.buffer.paste_clipboard(self.clipboard, None, True)
		
	def buffer_changed(self, data):
		self.handler.set_save_icon(True)
		self.parent.linenumbers.set_lines(self.buffer.get_line_count())
		self.do_highlight()
		
	def select_text(self, matchstart, matchend):
		self.buffer.select_range(matchstart, matchend)
	
	def find_text(self, text):		
		startiter = self.buffer.get_start_iter()
		result = []
		while True:
			found = startiter.forward_search(text, 0, None)
			if found:
				matchstart, matchend = found
				result.append((matchstart, matchend))
				startiter = matchend
			else:
				break
		return result
			
	def search_for_text(self, text):
		self.buffer.remove_tag(self.searchtag, self.buffer.get_start_iter(), self.buffer.get_end_iter())
		result = self.find_text(text)
		if len(result) != 0:
			self.matchstart = result[0][0]
			self.matchend = result[0][1]
			self.select_text(self.matchstart, self.matchend)
			for r in result:
				matchstart = r[0]
				matchend = r[1]
				self.buffer.apply_tag(self.searchtag, matchstart, matchend)
		else:
			pass
			
	def search_forward(self, text):
		if self.matchend:
			startiter = self.matchend
		if not self.matchend:
			startiter = self.buffer.get_start_iter()
		found = startiter.forward_search(text, 0, None)
		if found:
			self.matchstart, self.matchend = found
			self.select_text(self.matchstart, self.matchend)
			
	def search_backward(self, text):
		if self.matchstart:
			startiter = self.matchstart
		if not self.matchstart:
			startiter = self.buffer.get_end_iter()
		found = startiter.backward_search(text, 0, None)
		if found:
			self.matchstart, self.matchend = found
			self.select_text(self.matchstart, self.matchend)
			
	def set_highlighter(self):
		self.tags = {}
		self.tags['boldblue'] = self.buffer.create_tag('BoldBlue')
		self.tags['boldblue'].set_property('foreground', 'darkblue')
		self.tags['boldblue'].set_property('weight', 550)
		
		self.tags['blue'] = self.buffer.create_tag('blue')
		self.tags['blue'].set_property('foreground', 'blue')
		
		self.tags['darkgreen'] = self.buffer.create_tag('DarkGreen')
		self.tags['darkgreen'].set_property('foreground', 'darkgreen')
		
		self.tags['orange'] = self.buffer.create_tag('Orange')
		self.tags['orange'].set_property('foreground', 'orange')
		
		self.numbers = ['0','1','2','3','4','5','6','7','8','9']
		self.python = ['def', 'from', 'import', 'class', 'if', 'elif', 'for', 'else', 'return', 'break', 'while', 'do'] 
		self.c = ['function', 'this', '#include', 'class', 'if', 'for', 'else', 'return', 'break', 'exit', 'while', 'do'] 
	
	def do_highlight(self):
		if self.handler.get_file_type() == 'py':
			for code in self.python:
				result = self.find_text(code)
				if result:
					for iter in result:
						self.buffer.apply_tag(self.tags['boldblue'], iter[0], iter[1])
			for n in self.numbers:
				result = self.find_text(n)
				if result:
					for iter in result:
						self.buffer.apply_tag(self.tags['darkgreen'], iter[0], iter[1])
			match = "^\"$\""
			result = self.find_text(match)
			if result:
				for iter in result:
					self.buffer.apply_tag(self.tags['boldblue'], iter[0], iter[1])
		elif self.handler.get_file_type() in ['c', 'cpp', 'h', 'cc']:
			for code in self.c:
				result = self.find_text(code)
				if result:
					for iter in result:
						self.buffer.apply_tag(self.tags['boldblue'], iter[0], iter[1])
			for n in self.numbers:
				result = self.find_text(n)
				if result:
					for iter in result:
						self.buffer.apply_tag(self.tags['darkgreen'], iter[0], iter[1])
		
