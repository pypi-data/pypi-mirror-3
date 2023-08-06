#!/usr/bin/python
from __future__ import with_statement
from setuptools import setup



from setuptools.command.test import test

class pytest(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        import pytest
        pytest.main([])


def read_readme():
    result = []
    for fname in ('docs/readme.rst', 'docs/changelog.rst'):
        with open(fname) as f:
            result.append(f.read())
    return '\n'.join(result)

setup(
    name='anyvc',
    packages=[
        'anyvc',
        'anyvc.common',
        'anyvc.remote',

        # backends
        'anyvc.mercurial',
        'anyvc.git',
        'anyvc.subversion',
    ],
    setup_requires=[
        'hgdistver',
    ],
    install_requires=[
        'apipkg',
        'py>=1.3',
    ],
    extras_require={
        'mercurial': ['mercurial'],
        'git': ['dulwich'],
        'subversion': ['subvertpy'],
        'remoting': ['execnet'],
    },

    scripts=[
        'bin/vc',
    ],
    description='Library to access any version control system.',
    license='GNU GPL2 (or later) as published by the FSF',
    url='http://www.bitbucket.org/RonnyPfannschmidt/anyvc/',
    author='Ronny Pfannschmidt',
    author_email='Ronny.Pfannschmidt@gmx.de',
    long_description=read_readme(),
    get_version_from_scm=True,
    classifiers=[
        'Intended Audience :: Developers',
    ],
    cmdclass = {'test': pytest}
)
