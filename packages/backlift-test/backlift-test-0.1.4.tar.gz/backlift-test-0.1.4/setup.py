from distutils.core import setup

setup(name='backlift-test',
      version='0.1.4',
      description='Backlift Command Line Interface',
      author='Cole Krumbholz',
      author_email='cole@backlift.com',
      py_modules=['backlift'],
      package_dir={
        'yaml': 'lib/PyYAML-3.10/lib/yaml',
        'chardet': 'lib/chardet-1.0.1/chardet',
        'certifi': 'lib/certifi-0.0.8/certifi',
        'requests': 'lib/requests/requests',
      },
      packages=['yaml', 'chardet', 'certifi', 'requests'],
      scripts=['backlift']
     )
