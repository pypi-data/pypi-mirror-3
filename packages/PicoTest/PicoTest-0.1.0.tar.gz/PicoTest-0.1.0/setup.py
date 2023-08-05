###
### $Release: 0.1.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, re, os
arg1 = len(sys.argv) > 1 and sys.argv[1] or None
#if arg1 == 'egg_info':
#    from ez_setup import use_setuptools
#    use_setuptools()
if arg1 == 'bdist_egg':
    from setuptools import setup
else:
    from distutils.core import setup

python2 = sys.version_info[0] == 2
python3 = sys.version_info[0] == 3


def _kwargs():

    name          = 'PicoTest'
    version       = '0.1.0'
    author        = 'makoto kuwata'
    author_email  = 'kwa@kuwata-lab.com'
    maintainer    = author
    maintainer_email = author_email
    description   = 'a fast and full-featured template engine based on embedded Python'
    url           = 'http://pypi.python.org/PicoTest'
    download_url  = 'http://pypi.python.org/packages/source/%s/%s/%s-%s.tar.gz' % (name[0], name, name, version)
    license       = 'MIT License'
    platforms     = 'any'
    py_modules    = ['picotest']
    package_dir   = {'': 'lib'}
    #scripts       = ['bin/picotest']
    #packages     = ['picotest']
    #zip_safe     = False
    #
    long_description = open("README.txt").read()
    #
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ]
    #
    return locals()


setup(**_kwargs())
