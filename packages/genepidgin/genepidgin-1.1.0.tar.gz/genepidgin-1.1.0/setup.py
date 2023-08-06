# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from genepidgin import version

with open('README.rst') as f:
    readme = f.read()

tests_require = [
    'nose',
    'virtualenv>=1.7',
    'scripttest>=1.1.1',
    'mock',
]

install_requires = [
]

data = dict(
    name    = 'genepidgin',
    version = version,

    author       = 'Clint Howarth',
    author_email = 'clint.howarth@gmail.com',

    url = 'https://www.github.com/clinthowarth/genepidgin',

    install_requires = install_requires,
    tests_require    = tests_require,
    extras_require   = {'test': tests_require},
    test_suite       = 'nose.collector',

    packages             = find_packages(exclude=('tests')),
    entry_points         = {
        'console_scripts' : [ 'genepidgin = genepidgin.cmdline:main', ]
    },
    include_package_data = True,
    zip_safe             = False,
    
    license          = 'BSD',
    description      = 'gene naming utility belt',
    long_description = readme,
    keywords         = "bioinformatics homology-naming gene-naming",
    classifiers      = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
    ],
)

setup(**data)
