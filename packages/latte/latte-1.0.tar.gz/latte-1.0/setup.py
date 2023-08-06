try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Automatic rule based Linux Time Tracker',
    'author': 'Tautvidas Sipavicius',
    'author_email': 'flakas@tautvidas.com',
    'homepage': 'https://github.com/flakas/Latte',
    'url' : 'https://github.com/flakas/Latte/zipball/latte-1.0',
    'install_requires': [],
    'packages': ['latte', 'latte.Categories', 'latte.Projects'],
    'scripts': ['bin/latte'],
    'version': '1.0',
    'name': 'latte'
}

setup(**config)
