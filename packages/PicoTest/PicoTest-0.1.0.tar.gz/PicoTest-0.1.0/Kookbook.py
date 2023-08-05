# -*- coding: utf-8 -*-

###
### $Release: 0.1.0 $
### $Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

from __future__ import with_statement

import sys, os, re
from kook.utils import glob2

package   = 'PicoTest'
release   = prop('release', "0.1.0")
copyright = prop('copyright', "copyright(c) 2011 kuwata-lab.com all rights reserved")
license   = "MIT License"

basename  = package + '-' + release
dist_dir  = "dist/%s-%s" % (package, release)
target_files = [
    "README.txt", "CHANGES.txt", "MIT-LICENSE", "setup.py", "MANIFEST.in", "Kookbook.py",
    "lib/**/*.py", "test/**/*.py",   # "bin/*",
]

python    = sys.executable
python_versions = [
    ('2.4', "/opt/local/bin/python2.4"),
    ('2.5', "/opt/local/bin/python2.5"),
    ('2.6', "/opt/local/bin/python2.6"),
    ('2.7', "/opt/local/bin/python2.7"),
    ('3.0', "/opt/lang/python/3.0.1/bin/python"),
    ('3.1', "/opt/lang/python/3.1.4/bin/python"),
    ('3.2', "/opt/lang/python/3.2.1/bin/python"),
]

kookbook.default = 'test'


##
## testing
##
@recipe
@spices("-a: do test on Python 2.5, 2.6, ...")
def test(c, *args, **kwargs):
    flag_all = kwargs.get('a')
    if flag_all:
        for ver, bin in python_versions:
            print("############### Python %s ####################" % ver)
            for fname in glob2("test/**/*_test.py"):
                system(c%"$(bin) $(fname)")
    else:
        for fname in glob2("test/**/*_test.py"):
            system(c%"$(python) $(fname)")


##
## 'clean' and 'sweep' recipes
##
kookbook.load('@kook/books/clean.py')
CLEAN.extend(['**/*.pyc', '**/__pycache__', '**/*.egg-info', ])
SWEEP.extend(['dist', basename + '.tar.gz', basename + '-*.egg', 'README.html'])


##
## recipes for package
##
class pkg(Category):

    @recipe
    @ingreds('pkg:dist')
    def default(c):
        """try to create packages (*.tar.gz and *.egg)"""
        with pushd(dist_dir):
            system(c%"$(python) setup.py sdist")
            system(c%"$(python) setup.py bdist_egg")
        mv(c%"$(dist_dir)/dist/$(package)-$(release).tar.gz", ".")
        mv(c%"$(dist_dir)/dist/$(package)-$(release)-*.egg", ".")
        rm_rf(c%"$(dist_dir)/build", c%"$(dist_dir)/dist")

    @recipe
    def dist(c):
        if os.path.isdir(dist_dir):
            rm_rf(dist_dir)
        mkdir_p(dist_dir)
        #
        store(target_files, dist_dir)
        #
        def replacer(s):
            s = re.sub(r'\$(Release):.*?\$',   r'$\1: %s $' % release,   s)
            s = re.sub(r'\$(Copyright):.*?\$', r'$\1: %s $' % copyright, s)
            s = re.sub(r'\$(License):.*?\$',   r'$\1: %s $' % license,   s)
            s = re.sub(r'\$(Package)\$',   package,   s)
            s = re.sub(r'\$(Release)\$',   release,   s)
            s = re.sub(r'\$(Copyright)\$', copyright, s)
            s = re.sub(r'\$(License)\$',   license,   s)
            return s
        edit(c%'$(dist_dir)/**/*', by=replacer)

    @recipe
    def register(c):
        """register current version into PyPI"""
        dir = dist_dir
        with pushd(dir):
            system(c%"$(python) setup.py register")

    @recipe
    def upload(c):
        """upload source package (*.tar.gz) to PyPI"""
        dir = dist_dir
        with pushd(dir):
            system(c%"$(python) setup.py sdist upload")
            #system(c%"$(python) setup.py bdist_egg upload")


##
## update '$Release: 0.1.0 $', '$Copyright: copyright(c) 2011 kuwata-lab.com all rights reserved $', and so on in files
##
@recipe
@spices("-a: update all files", "[files]")
def edit_files(c, *args, **kwargs):
    """update '$Release: 0.1.0 $' and so on in files"""
    def replacer(s):
        s = re.sub(r'\$(Release):.*?\$',   r'$\1: %s $' % release, s)
        s = re.sub(r'\$(Copyright):.*?\$', r'$\1: %s $' % copyright, s)
        s = re.sub(r'\$(License):.*?\$',   r'$\1: %s $' % license, s)
        return s
    if kwargs.get('a'):
        edit(target_files, by=replacer)
    elif args:
        filenames = args
        edit(filenames, by=replacer)
    else:
        print("edit_files: filename or '-a' required.")
        return 1


##
## is README.txt correct reStructured format?
##
@recipe
@product('README.html')
def file_README_html(c):
    """convert README.txt into html file"""
    system(c%"rst2html.py README.txt > README.html")


##
## run examples
##
@recipe
@spices("-a: run with Python 2.4, 2.5, and so on")
def examples(c, *args, **kwargs):
    filenames = glob2("examples/*.py")
    if kwargs.get('a'):
        for ver, bin in python_versions:
            if ver == '2.4': continue
            for fname in filenames:
                system(c%"$(bin) $(fname)")
    else:
        for fname in filenames:
            system(c%"$(python) $(fname)")
