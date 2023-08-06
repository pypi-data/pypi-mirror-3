#!/usr/bin/env python
from distutils.core import setup
import os
import fnmatch

ginfo_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'pebsaq', 'generalinformation.py')
execfile(ginfo_file)

readme = open('README.txt').read()
conf = dict(
    name=program_name,
    version=version_text,
    author='Niels G. W. Serup',
    author_email='ns@metanohi.name',
    packages=['pebsaq', 'pebsaq.external'],
    scripts=['scripts/pebsaq'],
    requires=['qvikconfig'],
    url='http://metanohi.name/projects/pebsaq/',
    license='GPLv3+',
    description=program_description,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: End Users/Desktop',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'License :: DFSG approved',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities',
                 'Topic :: Multimedia :: Sound/Audio',
                 'Topic :: Multimedia :: Sound/Audio :: Sound Synthesis'
                 ]
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
