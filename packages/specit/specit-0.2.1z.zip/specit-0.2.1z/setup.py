import os
from setuptools import setup

version = '0.2.1z'
long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.txt').read(),
    open('TODO.txt').read(),
])

setup(
    name = "specit",
    version = version,
    description = "Create and run executable specifications with Pythonic BDD style grammar",
    long_description = long_description,
    author = "Rudy Lattae",
    author_email = "rudylattae@gmail.com",
    url = 'https://bitbucket.org/rudylattae/specit',
    license = "Simplified BSD",
    keywords = ['Specification', 'BDD', 'TDD'],
    classifiers = [
        'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    package_dir = {'': 'src'},
    packages = [''],
    zip_safe = False,
    install_requires = ['nose'],
    entry_points = {
        'console_scripts': [
            'specit = specit:main'
        ]
    }
)