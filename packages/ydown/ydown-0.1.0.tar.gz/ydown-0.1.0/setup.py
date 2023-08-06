from distutils.core import setup

setup(
    name='ydown',
    version='0.1.0',
    author='Freddyt',
    author_email='freddy6896@gmail.com',
    packages=['ydown', 'ydown.test'],
    scripts=['bin/ydownExample.py'],
    url='https://sourceforge.net/projects/ydown/',
    license='LICENSE.txt',
    description='ydown is a complete library for downloading youtube videos',
    long_description=open('README.txt').read(),
)