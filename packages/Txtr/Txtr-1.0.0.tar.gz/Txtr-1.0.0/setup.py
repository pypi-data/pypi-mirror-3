from distutils.core import *

setup(name='Txtr',
      version='1.0.0',
      author = 'Eslam Mostafa',
      author_email = 'cseslam@gmail.com',
      license = 'GPL3',
      description = 'A simple and neat text editor designed for gnu/linux',
      #py_modules=['txtr_window','txtr_greet','txtr_textview',
#			'txtr_notebook','txtr_about','txtr_menubar','txtr_toolbar', 'txtr_child',
#			'txtr_handler', 'txtr_linenumbers', 'txtr_statusbar', 'txtr_search'],
      packages=['txtr'],
      scripts=['bin/txtr',],
      data_files=[('/usr/share/applications',['applications/txtr.desktop']),
		  ('usr/share/', ['screenshots/txtr-welcome-screen.png', 'screenshots/txtr.png'])
		],
      )
