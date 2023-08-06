from distutils.core import setup

setup(
    name='ydown',
    version='2.0.0',
    author='Freddyt',
    author_email='freddy6896@gmail.com',
    packages=['ydown', 'ydown.test'],
    scripts=['bin/ydownlibExample.py','bin/ydatalibExample.py'],
    url='https://sourceforge.net/projects/ydown/',
    license='LICENSE.txt',
    description='ydown is a complete library for getting information about and downloading youtube videos',
    long_description=open('README.txt').read(),
)
