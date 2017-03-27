from setuptools import find_packages
from setuptools import setup

setup (
       name = 'PeerPace',
       version = '0.1',
       packages = find_packages(),

       # Declare your packages' dependencies here, for eg:
       install_requires = ['pprint', 'requests'],

       # Fill in these to make your Egg ready for upload to
       # PyPI
       author = 'kodecharlie',
       author_email = 'kodecharlie@users.sourceforge.net',

       #summary = 'Just another Python package for the cheese shop',
       url = '',
       license = '',
       long_description = 'Long description of the package',

       # could also include long_description, download_url, classifiers, etc.

  
       )