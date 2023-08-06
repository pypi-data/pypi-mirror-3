try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Converts a binary number to a decimal number',
    'author': 'Sel_iddqd',
    'url': 'none',
    'download_url': 'none',
    'author_email': 'none',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['BtoDConverter'],
    'scripts': [],
    'name': 'BtoDConverter'
}

setup(**config)