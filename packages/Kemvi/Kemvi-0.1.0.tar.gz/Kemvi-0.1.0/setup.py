#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Kemvi',
    version='0.1.0',
    description='Kemvi is a semantic search engine for computable data.',
    author='Kemvi',
    author_email='info@kemvi.com',
    url='http://pypi.python.org/pypi/kemvi/',
    packages=['kemvi'],
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
	classifiers=[
	'Development Status :: 4 - Beta',
	'Intended Audience :: Science/Research',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: GNU General Public License (GPL)',
	'Operating System :: POSIX',
	'Operating System :: Microsoft :: Windows',
	'Operating System :: MacOS :: MacOS X',
	'Programming Language :: Python :: 2.5',
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Topic :: Database :: Front-Ends',        
	]
)