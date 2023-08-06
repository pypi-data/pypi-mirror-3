import sys
from distutils.core import setup

setup(
    name         = 'pytkapp',
    version      = '0.1.0',
    author       = 'Paul "Mid.Tier"',
    author_email = 'mid.tier@gmail.com',
    url          = 'http://pypi.python.org/pypi/pytkapp',
    description  = 'Python package to develop a simple application (MDI/SDI) using tkinter library.',

    packages=['pytkapp','pytkapp.tkw','pytkapp.cpr'],
    keywords = "tkinter mdi/sdi application widgets tablelist",
    license='LICENSE.txt',
    long_description=open('README.txt').read(),    
)