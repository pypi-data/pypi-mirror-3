import os
from setuptools import setup, find_packages

try:
    filename = os.path.join(os.path.dirname(__file__), 'README.txt')
    description = file(filename).read()
except:
    description = ""

version = "0.1.2"

setup(name='wordstream',
      version=version,
      description="word streamer; conversational and dissociatively play with text with a command line and web interface",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/wordstream',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      wordstream = wordstream.factory:factory

      [console_scripts]
      wordstream = wordstream.main:main
      dissociate = wordstream.dissociate:main
      """,
      )
      
