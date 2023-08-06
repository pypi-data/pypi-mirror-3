try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    
config = {
    'description'   :   'Just some utilities I find useful for my research',
    'author'        :   'Craig Snoeyink',
    'url'           :   'http://pypi.python.org/pypi/CASutils/',
    
    'author_email'  :   'craig.snoeyink@gmail.com',
    'version'       :   '0.191111',
    'install_requires': ['nose'],
    'packages'      :   ['CASutils'],
    'scripts'       :   ['bin/CASutils_runner'],
    'name'          :   'CASutils',
    
    }
    
setup(**config)
