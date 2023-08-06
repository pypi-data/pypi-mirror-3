from gi.repository import Gtk
from greet import Greet

class Txtr:
	def __init__(self):
		greet = Greet()
		greet.show_all()
		
if __name__ == '__main__':
    Txtr()
    Gtk.main()
