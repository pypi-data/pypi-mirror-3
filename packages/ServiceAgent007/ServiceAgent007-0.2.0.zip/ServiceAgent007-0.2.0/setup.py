#!/usr/bin/env python
from distutils.core import setup
from os import path
  
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development',
]

setup(
    author="Tim Savage",
    author_email="tim.savage@poweredbypenguins.org",
    name='ServiceAgent007',
    version='0.2.0',
    description='Wrapper of urllib2 suited for HTTP REST service requests.',
    long_description=open(path.join(path.dirname(__file__), 'README.rst')).read(),
    url='https://bitbucket.org/timsavage/service-agent',
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    py_modules = ['service_agent'],
)
