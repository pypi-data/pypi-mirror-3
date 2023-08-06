try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Andrew Kitchell',
    'url': '',
    'download_url': '',
    'author_email': 'akitchell@gmail.com',
    'version': '0.1.1',
    'install_requires': ['nose'],
    'packages': ['ex47'],
    'scripts': ['bin/ex47.py'],
    'name': 'projectname'
}
    
setup(**config)   
