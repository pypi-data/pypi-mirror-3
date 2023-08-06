from distutils.core import setup

import sys
sys.path.insert(0, 'src')

from cqlug_demo import __version__

# Only if you use restructured text in the readme (http://docutils.sourceforge.net/rst.html)
#with open('README.txt') as file:
#    long_description = file.read()

setup(name='cqlug_demo',
      version= __version__,
      packages=['cqlug_demo'],
      package_dir = {'':'src'},
      scripts = ["scripts/hello","scripts/hello.bat","scripts/create-doku-page"],
      package_data = {'cqlug_demo': [
           'templates/doku.txt'
           ]},
      author = "Daniel Stonier",
      author_email = "d.stonier@gmail.com",
      url = "http://pypi.python.org/pypi/cqlug_demo/",
      download_url = "https://github.com/stonier/cqlug_demo.git",
      classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License" ],
      keywords = ["ROS"],
      description = "Demo package for the cqlug demo, August 2012",
      long_description = "Refer to the documentation at https://github.com/stonier/cqlug-demo.",
      license = "BSD"
      )
