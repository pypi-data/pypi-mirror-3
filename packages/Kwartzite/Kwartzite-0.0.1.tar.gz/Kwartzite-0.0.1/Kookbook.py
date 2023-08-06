###
### $Release: 0.0.1 $
### $Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $
### $License: MIT License $
###

import sys, os, re
python = sys.executable

kookbook.default = 'test'

release   = prop('release', "0.0.1")
copyright = prop('copyright', "copyright(c) 2007-2011 kuwata-lab.com all rights reserved")
license   = prop('license', 'MIT License')
package   = 'Kwartzite'

target_files = [
    "README.rst", "MIT-LICENSE", "setup.py", "MANIFEST.in", "Kookbook.py",
    "lib/**/*.py", "test/**/*.py", "examples/**/*", "bin/*",
]




pyvers = ('2.5.5', '2.6.7', '2.7.2', '3.0.1', '3.1.3', '3.2.2')
vs_home = os.getenv('VS_HOME') or '/opt/lang'

class test(Category):

    @recipe
    def default(c):
        """do test"""
        system(c%"$(python) -m oktest -p '*_test.py' -sp test")

    @recipe
    def all(c):
        """do test on python 2.5, 2.6, and so on"""
        for pyver in pyvers:
            python = c%"$(vs_home)/python/$(pyver)/bin/python"
            system_f(c%"$(python) -m oktest -p '*_test.py' -sp test")


@recipe
def task_edit(c):
    replacer = (
        (r'\$Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $', '$Copyright: copyright(c) 2007-2011 kuwata-lab.com all rights reserved $' % (copyright,)),
    )
    edit('lib/**/*.py', 'test/**/*.py', by=replacer)



##
## 'clean' and 'sweep' recipes
##
kookbook.load('@kook/books/clean.py')
CLEAN.extend(['**/*.pyc', '**/__pycache__', '**/*.egg-info', 'dist', 'build'])
SWEEP.extend(['dist', package + '-*.tar.gz', package + '-*.egg', 'README.html'])


##
## recipes for package
##
class pkg(Category):

    @recipe
    @ingreds('pkg:dist')
    def default(c):
        """try to create packages (*.tar.gz and *.egg)"""
        if not release: raise Exception("--release is required.")
        dist_dir = "dist/%s-%s" % (package, release)
        with pushd(dist_dir):
            system(c%"$(python) setup.py sdist")
            system(c%"$(python) setup.py bdist_egg")
        mv(c%"$(dist_dir)/dist/$(package)-$(release).tar.gz", ".")
        mv(c%"$(dist_dir)/dist/$(package)-$(release)-*.egg", ".")
        rm_rf(c%"$(dist_dir)/build", c%"$(dist_dir)/dist")

    @recipe
    @ingreds('clean')
    @spices("-v: list files")
    def dist(c, *args, **kwargs):
        """copy files into 'dist' directory"""
        if not release: raise Exception("--release is required.")
        dist_dir = "dist/%s-%s" % (package, release)
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
        #
        if kwargs.get('v'):
            system(c%"find $(dist_dir) -type f")

    @recipe
    def register(c):
        """register current version into PyPI"""
        if not release: raise Exception("--release is required.")
        dist_dir = "dist/%s-%s" % (package, release)
        with pushd(dist_dir):
            system(c%"$(python) setup.py register")

    @recipe
    def upload(c):
        """upload source package (*.tar.gz) to PyPI"""
        if not release: raise Exception("--release is required.")
        dist_dir = "dist/%s-%s" % (package, release)
        with pushd(dist_dir):
            system(c%"$(python) setup.py sdist upload")
            #system(c%"$(python) setup.py bdist_egg upload")


