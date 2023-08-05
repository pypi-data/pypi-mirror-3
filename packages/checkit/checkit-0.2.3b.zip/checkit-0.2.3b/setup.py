import os
from setuptools import setup

version = '0.2.3b'
long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CHANGES.txt').read(),
])

setup(
    name = "checkit",
    version = version,
    description = "Validate your Python software against specifications created with BDD style grammar.",
    long_description = long_description,
    author = "Rudy Lattae",
    author_email = "rudylattae@gmail.com",
    url = 'https://bitbucket.org/rudylattae/checkit',
    license = "Simplified BSD",
    keywords = ['Specification', 'BDD', 'TDD', 'check', 'validate', 'example', 'nose', 'nosetest'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    py_modules = ['checkit'],
    zip_safe = False,
    install_requires = ['nose'],
    entry_points = {
        'console_scripts': [
            'checkit = checkit:main'
        ]
    }
)
