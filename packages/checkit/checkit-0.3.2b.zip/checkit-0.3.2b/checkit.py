"""Checkit is a tool to validate executable specifications
created with BDD style grammar.

The checkit module is simply a wrapper around nose to discover
and execute specifications using flexible matching rules.
"""
import os
import sys


# these are the options that are passed to nose
NOSE_OPTIONS = [
    '-i "([Ss]pec[s]?)(.py)?$"',
    '-i "^([Dd]escribe)|([Gg]iven)"',
    '-i "^(it_|should_)"',
    '--with-doctest'
]


def main():
    """A simple wrapper that calls nosetests
    with a regex of keywords to use in discovering specs
    """
    command = 'nosetests %s %s' % (' '.join(NOSE_OPTIONS), ' '.join(sys.argv[1:]))
    return os.system(command)


if __name__ == '__main__':
    main()
