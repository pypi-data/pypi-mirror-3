# setup.py
# -*- coding: UTF-8 -*-
# vi:si:et:sw=4:sts=4:ts=4
try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_bzr_version():
    import os
    info = os.path.join(os.path.dirname(__file__), '.bzr/branch/last-revision')
    if os.path.exists(info):
        f = open(info)
        rev = int(f.read().split()[0])
        f.close()
        if rev:
            return u'%s' % rev
    return u'unknown'

setup(name='oxtimelines',
    version='0.%s' % get_bzr_version() ,
    scripts=[
        'bin/oxtimelines',
    ],
    packages=[
        'oxtimelines',
    ],
    author='0x2620',
    author_email='0x2620@0x2620.org',
    description='extract timelines from videos',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
)

