__author__="Edward"
__date__ ="$25-Jun-2012 11:48:44$"

from distutils.core import setup

setup (
  name = 'sampAPI',
  version = '1.1',
  py_modules=['sampQuery', 'sampRcon'],
  data_files=['readme.txt', 'sampQueryExample.py', 'sampRconExample.py'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'Edward McKnight (EM-Creations.co.uk)',
  author_email = 'eddy@em-creations.co.uk',

  description = 'SA-MP (GTA San Andreas Multiplayer) Python API.',
  url = 'http://www.em-creations.co.uk',
  license = 'Creative Commons Attribution-NoDerivs 3.0 Unported License',
  long_description = 'GTA San Andreas Multiplayer Python API, Query and RCON.',

  
)