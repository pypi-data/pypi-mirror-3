from distutils.core import setup
from backlift import VERSION

setup(name='backlift-test',
      version=VERSION,
      description='Backlift Command Line Interface',
      author='Cole Krumbholz',
      author_email='cole@backlift.com',
      py_modules=['backlift'],
      scripts=['backlift']
     )
