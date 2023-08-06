#! /usr/bin/python
# -*- encoding: utf-8 -*-

from distutils.core import setup

setup(
    name="executionsquad",
    version='0.1.0',

    description='A script to split the blame.',
    long_description=(        
        'A script to execute a command on a randomly determined keypress, to '
        'shift the blame from the individual to the group.'
    ),

    url='http://flyingelephantsoftware.de/micro-projects/execution-squad/index.html',
    license='BSD',
    
    author='Philipp Benjamin Koeppchen',
    author_email='koeppchen@flyingelephantsoftware.de',
    
    maintainer='Philipp Benjamin Koeppchen',
    maintainer_email='koeppchen@flyingelephantsoftware.de',      
    
    platforms=['all'],
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    scripts=[
        'executionsquad',
    ],
)
