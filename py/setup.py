#!/usr/bin/env python

import os
import sys

## prepare to run PyTest as a command
from distutils.core import Command

## explain this...
#from distribute_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages

from version import get_git_version
VERSION, SOURCE_LABEL = get_git_version()
PROJECT = 'streamcorpus'
URL = 'http://github.com/trec-kba/streamcorpus'
AUTHOR = 'Diffeo, Inc.'
AUTHOR_EMAIL = 'support@diffeo.com'
DESC = 'Tools for organizing a collections of text for entity-centric stream processing.'

def read_file(file_name):
    file_path = os.path.join(
        os.path.dirname(__file__),
        file_name
        )
    return open(file_path).read()


def _myinstall(pkgspec):
    setup(
        script_args = ['-q', 'easy_install', '-v', pkgspec],
        script_name = 'easy_install'
    )


class PyTest(Command):
    '''run py.test'''

    description = 'runs py.test to execute all tests'

    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # ensure that pytest is installed
        _myinstall('pytest>=2.3')
        # and everything else we'd need. setuptools tests_require is dumb because it copies locally instead of installing to system, and install_requires isn't used untill install (but maybe someone wants to run the test before they install).
        for pkgspec in install_requires:
            _myinstall(pkgspec)
        print sys.path
        # reload sys.path for any new libraries installed
        import site
        site.main()
        print sys.path
        # use pytest to run tests
        pytest = __import__('pytest')
        if pytest.main(['-s', 'src']):
            sys.exit(1)

from distutils.dir_util import remove_tree
from distutils.util import spawn, newer, execute

import distutils.command.build

def version_suffix_rename(fname, version):
    assert fname.endswith('.py')
    fname = fname[:-3]
    return fname + version + '.py'

class Thrift(Command):
    '''run thrift'''
    description = 'run thrift generator from data language to generated python'

    user_options = [
        ('force', 'f',
         "run all the build commands even if we don't need to")
        ]

    boolean_options = ['force']

    def initialize_options(self):
        self.force = 0
    def finalize_options(self):
        pass
    def run(self):
        self.maybe_thrift_gen('../if/streamcorpus-v0_1_0.thrift', 'src/streamcorpus', lambda x: version_suffix_rename(x, '_v0_1_0'))
        self.maybe_thrift_gen('../if/streamcorpus-v0_2_0.thrift', 'src/streamcorpus', lambda x: version_suffix_rename(x, '_v0_2_0'))
        self.maybe_thrift_gen('../if/streamcorpus-v0_3_0.thrift', 'src/streamcorpus', lambda x: x)

    def maybe_thrift_gen(self, thrift_src, outdir, renamefunc):
        self.make_file(
            thrift_src,
            os.path.join(outdir, renamefunc('ttypes.py')),
            self._run_thrift,
            [thrift_src, outdir, renamefunc])

    def _run_thrift(self, thrift_src, outdir, renamefunc):
        self.spawn(['thrift', '--gen', 'py:new_style,slots', thrift_src])
        for fname in ('constants.py', 'ttypes.py'):
            self.copy_file('gen-py/streamcorpus/' + fname, os.path.join(outdir, renamefunc(fname)))
        remove_tree('gen-py')


## We currently assume that the thrift generated python files are included in our source
## generation.  If we actually want other users to be able to generate the thrift files (
## which is very reasonable) we need to include the interface files in the
## source distribution.  Comment this out until them.
#distutils.command.build.build.sub_commands.insert(0, ('thrift', None))

setup(
    name=PROJECT,
    version=VERSION,
    #source_label=SOURCE_LABEL,
    description=DESC,
    long_description=read_file('README.rst'),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    license='MIT/X11 license http://opensource.org/licenses/MIT',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    cmdclass = {'test': PyTest, 'thrift': Thrift},
    # We can select proper classifiers later
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',  ## MIT/X11 license http://opensource.org/licenses/MIT
    ],
    entry_points={
        'console_scripts': [
            'streamcorpus_dump = streamcorpus.dump:main',
        ]
    },
    install_requires=[
        'thrift>=0.9',
        'cbor>=0.1.15',
    ],
    extras_require = {
        'snappy': [
            'python-snappy',
        ],
        'xz': [
            'backports.lzma',
        ],
    },
)
