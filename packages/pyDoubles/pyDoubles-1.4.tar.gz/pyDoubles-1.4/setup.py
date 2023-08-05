from distutils.core import setup

setup(
    name='pyDoubles',
    version='1.4',
    author='Carlos Ble',
    author_email='carlos@iexpertos.com',
    packages=['pyDoubles', 'pyDoublesTests'],
    scripts=[],
    url='https://bitbucket.org/carlosble/pydoubles',
    license='LICENSE.txt',
    description='Test doubles framework for Python',
    long_description=open('README.txt').read(),
)

