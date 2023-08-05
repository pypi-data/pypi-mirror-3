import sys
from distutils.core import setup

sys.path.insert(0, 'lib')
from wsgiservlets import version

setup(
    name='WSGIServlets',
    version='%d.%d.%d' % version,
    packages=['lib/wsgiservlets',],
    license='Apache License, Version 2.0',
    long_description=open('README.txt').read(),
    url='http://code.google.com/p/wsgiservlets/',
    author='Daniel J. Popowich',
    author_email='danielpopowich@gmail.com',
)
