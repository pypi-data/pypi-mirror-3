"""Class representing the list of files in a distribution.

The Manifest class can be used to:

 - read or write a MANIFEST file
 - read a template file and find out the file list
"""
# XXX todo: document + add tests
from __future__ import with_statement
import re
import os
import fnmatch

from logging import ERROR
from logging import basicConfig
from logging import getLogger

basicConfig()
logger = getLogger('manifest')
logger.setLevel(ERROR)

class ManifestTemplateError(Exception):
    pass

class ManifestInternalError(Exception):
    pass

def write_file(filename, contents):
    """Create *filename* and write *contents* to it.

    *contents* is a sequence of strings without line terminators.
    """
    with open(filename, "w") as f:
        for line in contents:
            f.write(line + "\n")

def convert_path(pathname):
    """Return 'pathname' as a name that will work on the native filesystem.

    The path is split on '/' and put back together again using the current
    directory separator.  Needed because filenames in the setup script are
    always supplied in Unix style, and have to be converted to the local
    convention before we can actually use them in the filesystem.  Raises
    ValueError on non-Unix-ish systems if 'pathname' either starts or
    ends with a slash.
    """
    if os.sep == '/':
        return pathname
    if not pathname:
        return pathname
    if pathname[0] == '/':
        raise ValueError("path '%s' cannot be absolute" % pathname)
    if pathname[-1] == '/':
        raise ValueError("path '%s' cannot end with '/'" % pathname)

    paths = pathname.split('/')
    while os.curdir in paths:
        paths.remove(os.curdir)
    if not paths:
        return os.curdir
    return os.path.join(*paths)

__all__ = [u'Manifest']

# a \ followed by some spaces + EOL
_COLLAPSE_PATTERN = re.compile(u'\\\w*\n', re.M)
_COMMENTED_LINE = re.compile(u'#.*?(?=\n)|\n(?=$)', re.M | re.S)


class Manifest(object):
    u"""A list of files built by on exploring the filesystem and filtered by
    applying various patterns to what we find there.
    """

    def __init__(self):
        self.allfiles = None
        self.files = []

    #
    # Public API
    #

    def findall(self, dir=os.curdir):
        self.allfiles = _findall(dir)

    def append(self, item):
        self.files.append(item)

    def extend(self, items):
        self.files.extend(items)

    def sort(self):
        # Not a strict lexical sort!
        self.files = [os.path.join(*path_tuple) for path_tuple in
                      sorted(os.path.split(path) for path in self.files)]

    def clear(self):
        u"""Clear all collected files."""
        self.files = []
        if self.allfiles is not None:
            self.allfiles = []

    def remove_duplicates(self):
        # Assumes list has been sorted!
        for i in xrange(len(self.files) - 1, 0, -1):
            if self.files[i] == self.files[i - 1]:
                del self.files[i]

    def read_template(self, path_or_file):
        u"""Read and parse a manifest template file.
        'path' can be a path or a file-like object.

        Updates the list accordingly.
        """
        if isinstance(path_or_file, unicode):
            f = open(path_or_file)
        else:
            f = path_or_file

        try:
            content = f.read()
            # first, let's unwrap collapsed lines
            content = _COLLAPSE_PATTERN.sub(u'', content)
            # next, let's remove commented lines and empty lines
            content = _COMMENTED_LINE.sub(u'', content)

            # now we have our cleaned up lines
            lines = [line.strip() for line in content.split(u'\n')]
        finally:
            f.close()

        for line in lines:
            if line == u'':
                continue
            try:
                self._process_template_line(line)
            except ManifestTemplateError, msg:
                logger.warning(u"%s, %s", path_or_file, msg)

    def write(self, path):
        u"""Write the file list in 'self.filelist' (presumably as filled in
        by 'add_defaults()' and 'read_template()') to the manifest file
        named by 'self.manifest'.
        """
        if os.path.isfile(path):
            with open(path) as fp:
                first_line = fp.readline()

            if first_line != u'# file GENERATED by packaging, do NOT edit\n':
                logger.info(u"not writing to manually maintained "
                            u"manifest file %r", path)
                return

        self.sort()
        self.remove_duplicates()
        content = self.files[:]
        content.insert(0, u'# file GENERATED by packaging, do NOT edit')
        logger.info(u"writing manifest file %r", path)
        write_file(path, content)

    def read(self, path):
        u"""Read the manifest file (named by 'self.manifest') and use it to
        fill in 'self.filelist', the list of files to include in the source
        distribution.
        """
        logger.info(u"reading manifest file %r", path)
        with open(path) as manifest:
            for line in manifest.readlines():
                self.append(line)

    def exclude_pattern(self, pattern, anchor=True, prefix=None,
                        is_regex=False):
        u"""Remove strings (presumably filenames) from 'files' that match
        'pattern'.

        Other parameters are the same as for 'include_pattern()', above.
        The list 'self.files' is modified in place. Return True if files are
        found.
        """
        files_found = False
        pattern_re = _translate_pattern(pattern, anchor, prefix, is_regex)
        for i in xrange(len(self.files) - 1, -1, -1):
            if pattern_re.search(self.files[i]):
                del self.files[i]
                files_found = True

        return files_found

    #
    # Private API
    #

    def _parse_template_line(self, line):
        words = line.split()
        if len(words) == 1:
            # no action given, let's use the default 'include'
            words.insert(0, u'include')

        action = words[0]
        patterns = dir = dir_pattern = None

        if action in (u'include', u'exclude',
                      u'global-include', u'global-exclude'):
            if len(words) < 2:
                raise ManifestTemplateError(
                      u"%r expects <pattern1> <pattern2> ..." % action)

            patterns = [convert_path(word) for word in words[1:]]

        elif action in (u'recursive-include', u'recursive-exclude'):
            if len(words) < 3:
                raise ManifestTemplateError(
                      u"%r expects <dir> <pattern1> <pattern2> ..." % action)

            dir = convert_path(words[1])
            patterns = [convert_path(word) for word in words[2:]]

        elif action in (u'graft', u'prune'):
            if len(words) != 2:
                raise ManifestTemplateError(
                     u"%r expects a single <dir_pattern>" % action)

            dir_pattern = convert_path(words[1])

        else:
            raise ManifestTemplateError(u"unknown action %r" % action)

        return action, patterns, dir, dir_pattern

    def _process_template_line(self, line):
        # Parse the line: split it up, make sure the right number of words
        # is there, and return the relevant words.  'action' is always
        # defined: it's the first word of the line.  Which of the other
        # three are defined depends on the action; it'll be either
        # patterns, (dir and patterns), or (dir_pattern).
        action, patterns, dir, dir_pattern = self._parse_template_line(line)

        # OK, now we know that the action is valid and we have the
        # right number of words on the line for that action -- so we
        # can proceed with minimal error-checking.
        if action == u'include':
            for pattern in patterns:
                if not self._include_pattern(pattern, anchor=True):
                    logger.warning(u"no files found matching %r", pattern)

        elif action == u'exclude':
            for pattern in patterns:
                if not self.exclude_pattern(pattern, anchor=True):
                    logger.warning(u"no previously-included files "
                                   u"found matching %r", pattern)

        elif action == u'global-include':
            for pattern in patterns:
                if not self._include_pattern(pattern, anchor=False):
                    logger.warning(u"no files found matching %r "
                                   u"anywhere in distribution", pattern)

        elif action == u'global-exclude':
            for pattern in patterns:
                if not self.exclude_pattern(pattern, anchor=False):
                    logger.warning(u"no previously-included files "
                                   u"matching %r found anywhere in "
                                   u"distribution", pattern)

        elif action == u'recursive-include':
            for pattern in patterns:
                if not self._include_pattern(pattern, prefix=dir):
                    logger.warning(u"no files found matching %r "
                                   u"under directory %r", pattern, dir)

        elif action == u'recursive-exclude':
            for pattern in patterns:
                if not self.exclude_pattern(pattern, prefix=dir):
                    logger.warning(u"no previously-included files "
                                   u"matching %r found under directory %r",
                                   pattern, dir)

        elif action == u'graft':
            if not self._include_pattern(None, prefix=dir_pattern):
                logger.warning(u"no directories found matching %r",
                               dir_pattern)

        elif action == u'prune':
            if not self.exclude_pattern(None, prefix=dir_pattern):
                logger.warning(u"no previously-included directories found "
                               u"matching %r", dir_pattern)
        else:
            raise ManifestInternalError(
                u"this cannot happen: invalid action %r" % action)

    def _include_pattern(self, pattern, anchor=True, prefix=None,
                         is_regex=False):
        u"""Select strings (presumably filenames) from 'self.files' that
        match 'pattern', a Unix-style wildcard (glob) pattern.

        Patterns are not quite the same as implemented by the 'fnmatch'
        module: '*' and '?'  match non-special characters, where "special"
        is platform-dependent: slash on Unix; colon, slash, and backslash on
        DOS/Windows; and colon on Mac OS.

        If 'anchor' is true (the default), then the pattern match is more
        stringent: "*.py" will match "foo.py" but not "foo/bar.py".  If
        'anchor' is false, both of these will match.

        If 'prefix' is supplied, then only filenames starting with 'prefix'
        (itself a pattern) and ending with 'pattern', with anything in between
        them, will match.  'anchor' is ignored in this case.

        If 'is_regex' is true, 'anchor' and 'prefix' are ignored, and
        'pattern' is assumed to be either a string containing a regex or a
        regex object -- no translation is done, the regex is just compiled
        and used as-is.

        Selected strings will be added to self.files.

        Return True if files are found.
        """
        files_found = False
        pattern_re = _translate_pattern(pattern, anchor, prefix, is_regex)

        # delayed loading of allfiles list
        if self.allfiles is None:
            self.findall()

        for name in self.allfiles:
            if pattern_re.search(name):
                self.files.append(name)
                files_found = True

        return files_found


#
# Utility functions
#
def _findall(dir=os.curdir):
    u"""Find all files under 'dir' and return the list of full filenames
    (relative to 'dir').
    """
    from stat import S_ISREG, S_ISDIR, S_ISLNK

    list = []
    stack = [dir]
    pop = stack.pop
    push = stack.append

    root_path_len = len(dir)
    while stack:
        dir = pop()
        names = os.listdir(dir)

        for name in names:
            if dir != os.curdir:        # avoid the dreaded "./" syndrome
                fullname = os.path.join(dir, name)
            else:
                fullname = name

            # Avoid excess stat calls -- just one will do, thank you!
            stat = os.stat(fullname)
            mode = stat.st_mode
            if S_ISREG(mode):
                list.append(fullname[root_path_len:])
            elif S_ISDIR(mode) and not S_ISLNK(mode):
                push(fullname)

    return list

def _glob_to_re(pattern):
    u"""Translate a shell-like glob pattern to a regular expression.

    Return a string containing the regex.  Differs from
    'fnmatch.translate()' in that '*' does not match "special characters"
    (which are platform-specific).
    """
    pattern_re = fnmatch.translate(pattern)

    # '?' and '*' in the glob pattern become '.' and '.*' in the RE, which
    # IMHO is wrong -- '?' and '*' aren't supposed to match slash in Unix,
    # and by extension they shouldn't match such "special characters" under
    # any OS.  So change all non-escaped dots in the RE to match any
    # character except the special characters.
    # XXX currently the "special characters" are just slash -- i.e. this is
    # Unix-only.
    pattern_re = re.sub(ur'((?<!\\)(\\\\)*)\.', ur'\1[^/]', pattern_re)

    return pattern_re


def _translate_pattern(pattern, anchor=True, prefix=None, is_regex=False):
    u"""Translate a shell-like wildcard pattern to a compiled regular
    expression.

    Return the compiled regex.  If 'is_regex' true,
    then 'pattern' is directly compiled to a regex (if it's a string)
    or just returned as-is (assumes it's a regex object).
    """
    if is_regex:
        if isinstance(pattern, unicode):
            return re.compile(pattern)
        else:
            return pattern

    if pattern:
        pattern_re = _glob_to_re(pattern)
    else:
        pattern_re = u''

    if prefix is not None:
        # ditch end of pattern character
        empty_pattern = _glob_to_re(u'')
        prefix_re = _glob_to_re(prefix)[:-len(empty_pattern)]
        pattern_re = u"^" + os.path.join(prefix_re, u".*" + pattern_re)
    else:                               # no prefix -- respect anchor flag
        if anchor:
            pattern_re = u"^" + pattern_re

    return re.compile(pattern_re)
