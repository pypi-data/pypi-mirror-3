
import sys, os, re

from kook.utils import glob2

kookbook.default = 'test'

release   = prop('release', "0.2.0")
copyright = prop('copyright', "copyright(c) 2011 kuwata-lab.com all rights reserved")
license   = prop('license', 'MIT License')
package   = 'Cmdopt'

target_files = [
    "README.txt", "MIT-LICENSE", "setup.py", "MANIFEST.in", "Kookbook.py",
    "lib/**/*.py", "test/**/*.py", "examples/**/*", # "bin/*",
]


python  = sys.executable
vs_home = os.getenv('VS_PATH', '').split(':')[0] or os.getenv('HOME') + '/lang'
python_executables = [
    ('Python 2.4', "/opt/local/bin/python2.4"),
    #('Python 2.5', "/opt/local/bin/python2.5"),
    #('Python 2.6', "/opt/local/bin/python2.6"),
    #('Python 2.7', "/opt/local/bin/python2.7"),
    ('Python 2.5', "%s/python/2.5.5/bin/python" % vs_home),
    ('Python 2.6', "%s/python/2.6.7/bin/python" % vs_home),
    ('Python 2.7', "%s/python/2.7.2/bin/python" % vs_home),
    ('Python 3.0', "%s/python/3.0.1/bin/python" % vs_home),
    ('Python 3.1', "%s/python/3.1.4/bin/python" % vs_home),
    ('Python 3.2', "%s/python/3.2.2/bin/python" % vs_home),
    #('PyPy 1.7',   "%s/pypy/1.7/bin/python" % vs_home),
]


class test(Category):

    @recipe
    def default(c):
        """do test"""
        system("python -m picotest -ss test")

    @recipe
    def all(c):
        """do test on Python 2.4, 2.5, and so on"""
        for ver, bin in python_executables:
            print("******************** %s ********************" % ver)
            if '2.4' in ver:
                ctx = EditForPython24('test/*_test.py')
                try:
                    ctx.__enter__()
                    system_f(c%"$(bin) -m picotest -ss test/*.py")
                finally:
                    ctx.__exit__(*sys.exc_info())
            else:
                system_f(c%"$(bin) -m picotest -ss test")


class EditForPython24(object):

    def __init__(self, filepattern):
        self.filepattern = filepattern

    def __enter__(self):
        #f = open(filename); s = f.read(); f.close()
        replacer = [
            (r'with test', 'for _ in test'),
            (r'(from __future__)', '#\\1'),
        ]
        for fname in glob2(self.filepattern):
            mv(fname, fname + '.original')
            cp(fname + '.original', fname)
        edit(self.filepattern, by=replacer)

    def __exit__(self, *args):
        for fname in glob2(self.filepattern):
            mv(fname + '.original', fname)


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


##
## wiki
##
kookbook.load('./books/wiki.py')


@recipe('README.html')
@ingreds('README.txt')
def file_README_html(c):
    """create README.html"""
    system(c%"rst2html.py $(ingred) > $(product)")
    #system(c%"rst2html.py --strip-elements-with-class='section' $(ingred) > $(product)")
    #system(c%"rst2html.py --strip-class='literal-block' $(ingred) > $(product)")


@recipe(None, ['cmdopt.py'])
def doc2test(c):
    """copy code on document into test script."""
    import cmdopt
    arr = re.compile(r'^ex\.\n$', re.M).split(cmdopt.__doc__)
    assert len(arr) == 2
    assert len(arr[1]) > 100    # enough length
    doccode = arr[1]
    #
    filename = 'test/cmdopt_test.py'
    f = open(filename)
    s = f.read()
    f.close()
    rexp = re.compile(r'(.*?^##__DOC__\n)(.*?)^(##/__DOC__\n.*)', re.S|re.M)
    m = rexp.match(s)
    assert m
    m1, m2, m3 = m.groups()
    s2 = m1 + doccode + m3
    #
    if s == s2:
        print("*** not changed.")
    else:
        print("*** doc code changed!")
        open('__old.txt', 'w').write(s)
        open('__new.txt', 'w').write(s2)
        try:
            system_f("diff -u __old.txt __new.txt")
            sys.stdout.write("OK? [Y/n]: ")
            ans = raw_input()
            if not ans or ans[0] == "Y" or ans[0] == "y":
                f = open(filename, 'wb')
                f.write(s2)
                f.close()
                print("*** changed.")
            else:
                print("*** skipped.")
        finally:
            os.unlink('__old.txt')
            os.unlink('__new.txt')

