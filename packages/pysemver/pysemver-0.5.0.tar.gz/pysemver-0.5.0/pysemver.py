# -*- coding: utf-8 -*-
"""
pysemver provides handy utilities to work with versions that satisfy
Semantic Versioning Specification requirements. Allows validate, parse,
compare, increment version numbers, etc.

Homepage and documentation: https://github.com/antonmoiseev/pysemver

Copyright (c) 2011, Anton Moiseev
License: MIT (see LICENSE for details)
"""

__version__ = '0.5.0'

import re


_semver_regex = re.compile(r"^([0-9]+)"  # major
                         + r"\.([0-9]+)" # minor
                         + r"\.([0-9]+)" # patch
                         + r"(\-[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?"   # pre-release
                         + r"(\+[0-9A-Za-z]+(\.[0-9A-Za-z]+)*)?$") # build


class SemVer:

    def __init__(self, version=None):
        self._major = self._minor = self._patch = 0
        self._build = self._prerelease = None

        if version:
            match = _semver_regex.match(version)
            if match:
                self._major = int(match.group(1))
                self._minor = int(match.group(2))
                self._patch = int(match.group(3))

                if match.group(4):
                    self._prerelease = match.group(4).lstrip('-')

                if match.group(6):
                    self._build = match.group(6).lstrip('+')
            else:
                raise ValueError('{0} is not valid SemVer string'.format(version))

    @property
    def major(self):
        return self._major

    @property
    def minor(self):
        return self._minor

    @property
    def patch(self):
        return self._patch

    @property
    def prerelease(self):
        return self._prerelease

    @property
    def build (self):
        return self._build

    def is_prerelease(self):
        return self._prerelease != None

    def is_build(self):
        return self._build != None

    @staticmethod
    def is_valid(version):
        return True if _semver_regex.match(version) else False
