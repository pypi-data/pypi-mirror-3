#!/usr/bin/env python
"""Distutils setup file, used to install or test 'setuptools'"""
import sys
import os

src_root = None
if sys.version_info >= (3,):
    tmp_src = os.path.join("build", "src")
    from distutils.filelist import FileList
    from distutils import dir_util, file_util, util, log
    log.set_verbosity(1)
    fl = FileList()
    for line in open("MANIFEST.in"):
        fl.process_template_line(line)
    dir_util.create_tree(tmp_src, fl.files)
    outfiles_2to3 = []
    for f in fl.files:
        outf, copied = file_util.copy_file(f, os.path.join(tmp_src, f), update=1)
        if copied and outf.endswith(".py"):
            outfiles_2to3.append(outf)
        if copied and outf.endswith('api_tests.txt'):
            # XXX support this in distutils as well
            from lib2to3.main import main
            main('lib2to3.fixes', ['-wd', os.path.join(tmp_src, 'tests', 'api_tests.txt')])

    util.run_2to3(outfiles_2to3)

    # arrange setup to use the copy
    sys.path.insert(0, tmp_src)
    src_root = tmp_src

from distutils.util import convert_path

d = {}
init_path = convert_path('setuptools/command/__init__.py')
exec(open(init_path).read(), d)

SETUP_COMMANDS = d['__all__']
VERSION = "0.6.8"

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
scripts = []

# specific command that is used to generate windows .exe files
class build_py(_build_py):
    def build_package_data(self):
        """Copy data files into build directory"""
        lastdir = None
        for package, src_dir, build_dir, filenames in self.data_files:
            for filename in filenames:
                target = os.path.join(build_dir, filename)
                self.mkpath(os.path.dirname(target))
                srcfile = os.path.join(src_dir, filename)
                outf, copied = self.copy_file(srcfile, target)
                srcfile = os.path.abspath(srcfile)

                # avoid a bootstrapping issue with easy_install -U (when the
                # previous version doesn't have convert_2to3_doctests)
                if not hasattr(self.distribution, 'convert_2to3_doctests'):
                    continue

                if copied and srcfile in self.distribution.convert_2to3_doctests:
                    self.__doctests_2to3.append(outf)

# if we are installing Distribute using "python setup.py install"
# we need to get setuptools out of the way
def _easy_install_marker():
    return (len(sys.argv) == 5 and sys.argv[2] == 'bdist_egg' and
            sys.argv[3] == '--dist-dir' and 'egg-dist-tmp-' in sys.argv[-1])

def _buildout_marker():
    command = os.environ.get('_')
    if command:
        return 'buildout' in os.path.basename(command)

def _being_installed():
    if os.environ.get('DONT_PATCH_SETUPTOOLS') is not None:
        return False
    if _buildout_marker():
        # Installed by buildout, don't mess with a global setuptools.
        return False
    # easy_install marker
    return 'install' in sys.argv[1:] or _easy_install_marker()

if _being_installed():
    from distribute_setup import _before_install
    _before_install()

dist = setup(
    name="distribute",
    version=VERSION,
    description="Easily download, build, install, upgrade, and uninstall "
                "Python packages",
    author="The fellowship of the packaging",
    author_email="distutils-sig@python.org",
    license="PSF or ZPL",
    long_description = open('README.txt').read() + open('CHANGES.txt').read(),
    keywords = "CPAN PyPI distutils eggs package management",
    url = "http://packages.python.org/distribute",
    test_suite = 'setuptools.tests',
    src_root = src_root,
    packages = find_packages(),
    package_data = {'setuptools':['*.exe']},

    py_modules = ['pkg_resources', 'easy_install', 'site'],

    zip_safe = (sys.version>="2.5"),   # <2.5 needs unzipped for -m to work

    entry_points = {

        "distutils.commands" : [
            "%(cmd)s = setuptools.command.%(cmd)s:%(cmd)s" % locals()
            for cmd in SETUP_COMMANDS
        ],

        "distutils.setup_keywords": [
            "eager_resources        = setuptools.dist:assert_string_list",
            "namespace_packages     = setuptools.dist:check_nsp",
            "extras_require         = setuptools.dist:check_extras",
            "install_requires       = setuptools.dist:check_requirements",
            "tests_require          = setuptools.dist:check_requirements",
            "entry_points           = setuptools.dist:check_entry_points",
            "test_suite             = setuptools.dist:check_test_suite",
            "zip_safe               = setuptools.dist:assert_bool",
            "package_data           = setuptools.dist:check_package_data",
            "exclude_package_data   = setuptools.dist:check_package_data",
            "include_package_data   = setuptools.dist:assert_bool",
            "dependency_links       = setuptools.dist:assert_string_list",
            "test_loader            = setuptools.dist:check_importable",
            "use_2to3               = setuptools.dist:assert_bool",
            "convert_2to3_doctests  = setuptools.dist:assert_string_list",
            "use_2to3_fixers = setuptools.dist:assert_string_list",
        ],

        "egg_info.writers": [
            "PKG-INFO = setuptools.command.egg_info:write_pkg_info",
            "requires.txt = setuptools.command.egg_info:write_requirements",
            "entry_points.txt = setuptools.command.egg_info:write_entries",
            "eager_resources.txt = setuptools.command.egg_info:overwrite_arg",
            "namespace_packages.txt = setuptools.command.egg_info:overwrite_arg",
            "top_level.txt = setuptools.command.egg_info:write_toplevel_names",
            "depends.txt = setuptools.command.egg_info:warn_depends_obsolete",
            "dependency_links.txt = setuptools.command.egg_info:overwrite_arg",
        ],

        "console_scripts": [
             "easy_install = setuptools.command.easy_install:main",
             "easy_install-%s = setuptools.command.easy_install:main"
                % sys.version[:3]
        ],

        "setuptools.file_finders":
            ["svn_cvs = setuptools.command.sdist:_default_revctrl"],

        "setuptools.installation":
            ['eggsecutable = setuptools.command.easy_install:bootstrap'],
        },


    classifiers = [f.strip() for f in """
    Development Status :: 5 - Production/Stable
    Intended Audience :: Developers
    License :: OSI Approved :: Python Software Foundation License
    License :: OSI Approved :: Zope Public License
    Operating System :: OS Independent
    Programming Language :: Python
    Programming Language :: Python :: 3
    Topic :: Software Development :: Libraries :: Python Modules
    Topic :: System :: Archiving :: Packaging
    Topic :: System :: Systems Administration
    Topic :: Utilities""".splitlines() if f.strip()],
    scripts = scripts,
)

if _being_installed():
    from distribute_setup import _after_install
    _after_install(dist)


