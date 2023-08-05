try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


config = {
    'description': 'Text based adventure game',
    'author': 'Jose Luis Naranjo Gomez',
    'author_email': 'luisnaranjo733@hotmail.com',
    'version': '2.0',
    'install_requires': ['nose'],
    'packages': find_packages(),
    'name': 'zorky',
}


setup(**config)
