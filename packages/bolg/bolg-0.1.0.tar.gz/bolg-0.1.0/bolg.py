#!/usr/bin/python3

# bolg: match glob-regexes against files
# Copyright (C) 2011 Niels Serup

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
import os
import sys
import itertools
from optparse import OptionParser

__doc__ = '''
bolg is an extended version of Python's glob module. It allows for a small
amount of more features while still retaining the simplicity of glob. More
specifically, bolg mimics some of the features found in BASH's globbing
algorithm.

Patterns
========

*         any character, from zero to infinite occurences, non-greedy
**        same as above, but greedy
+         any character, from one to infinite occurences, non-greedy
++        same as above, but greedy
?         any character, one occurence
[abc]     a, b, or c (a character group)
[^abc]    not a, b, or c
{{t1,t2}}   t1 or t2 (a character group) (recursivity allowed)
^{{t1,t2}}  not followed by t1 or t2
[a-b]     any base 10 number from a to b, both included. a and b must both be
          positive and share the same number of digits, and b must be higher
          than a. Patterns like [2-5] and [054-233] are acceptable, but [1-42]
          and [22-333] are not.
[^a-b]    any base 10 number from 0 to a and from b to maximum number possible,
          neither included
:n        any numeric (base 10) character
:a        any alphanumeric character (including underscore)
:s        any whitespace character
^x        not x (the same as [^x])
^^x        not followed by x (the same as ^{{x}})
\\x        x (escape it)

When searching for files, the directory separator ('{slash}') cannot be used as
a character in any of the former patterns, except in the end of a path when it
is desirable to look for both directories and files, in which case '{slash}b'
is parsed differently: if the string ends with '{slash}b', both files and
directories are checked for matches; if the string ends with '{slash}', only
directories are checked; else, only files are checked.

if an expression ends with '/i' (must be after '{slash}b' if present), case is
ignored.

'/i' can be escaped with '/\i', and '{slash}b' can be escaped by '{slash}\b'.
'''.format(slash=os.sep)

_cmd_examples = \
'''
Examples
--------

  bolg * *

  bolg IMG_0[301-449].JPG

  bolg a-directory/a-file.{jpg,png,xcf}

  bolg refer?rer-of-me[ea]tin+g

  bolg '{a-dir,b-dir}/mr? T+.work'
'''

__version__ = '0.1.0'
__author__ = 'Niels Serup <ns@metanohi.org>'
__copyright__ = '''
Copyright 2011 Niels Serup

Copyright (C) 2011 Niels Serup

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

# Warning: lacks comments. Must be fixed. 

def _subrange(a, b):
    diff = int(b) - int(a)
    fmt = '[{a}-{b}]' if diff > 1 else '[{a}{b}]' if diff == 1 else '{a}'
    return fmt.format(a=a, b=b)

def _metarangefunc(a, b):
    la, lb = len(a), len(b)
    assert la == lb, 'numbers do not share the same number of digits'
    assert int(b) >= int(a), 'second number must be higher than first number'
    return a, b, la

def _rangefunc(a, b):
    a, b, rl = _metarangefunc(a, b)
    if rl == 1:
        return _subrange(a, b)
    regex = ''
    for c in range(rl):
        ca, cb = a[c], b[c]
        if ca == cb:
            regex += ca
        else:
            break
    if rl - c == 1:
        return regex + _subrange(ca, cb)
    a, b = a[c:], b[c:]
    ca, cb = int(a[0]), int(b[0])
    times = rl - 1
    times = '{' + str(times) + '}' if times > 1 else ''
    extra = '|' + _subrange(ca + 1, cb - 1) + \
            '[0-9]' + times if cb - ca > 1 else ''
    regex += '({}|{}{})'.format(
        _rangeregex_min(a), _rangeregex_max(b), extra)
    return regex

def _rangeregex_min(n):
    if len(n) > 2:
        st = int(n[1]) + 1
        times = len(n) - 2
        times = '{' + str(times) + '}' if times > 1 else ''
        extra = '|{}[0-9]{}'.format(_subrange(st, 9),
                                        times) if st <= 9 else ''
        regex = '{c}({rec}{extra})'.format(
            c=n[0], rec=_rangeregex_min(n[1:]), extra=extra)
    else:
        regex = '{}{}'.format(n[0], _subrange(n[1], 9))
    return regex

def _rangeregex_max(n):
    if len(n) > 2:
        st = int(n[1]) - 1
        times = len(n) - 2
        times = '{' + str(times) + '}' if times > 1 else ''
        extra = '|{}[0-9]{}'.format(_subrange(0, st),
                                    times) if st >= 0 else ''
        regex = '{c}({rec}{extra})'.format(
            c=n[0], rec=_rangeregex_max(n[1:]), extra=extra)
    else:
        regex = '{}{}'.format(n[0], _subrange(0, n[1]))
    return regex
    
def _notrangefunc(a, b):
    a, b, rl = _metarangefunc(a, b)
    fmt = '{:' + str(rl) + 'd}'
    return '({}|{})'.format(_rangefunc('0' * rl, fmt.format(int(a) - 1)),
                            _rangefunc(fmt.format(int(b) + 1), '9' * rl))

_escapees = '[]^{}*+?\\'
_char_escapees = 'nrtbv'
_re_escapees = '.()$'
_all_escapees = _escapees + _char_escapees + _re_escapees
_escape = lambda x, is_escaped=False: '\\' + x if x in \
    (_all_escapees if is_escaped else _char_escapees) else x
_re_escape = lambda x: '\\' + x if x in _re_escapees else x

_scd = {
    'n': 'd',
    'a': 'w',
    's': 's'
    }
_range_re_base = r'\[{}([0-9]+)-([0-9]+)\]'
_notrange_re = re.compile(_range_re_base.format('\^'))
_range_re = re.compile(_range_re_base.format(''))

_LETTERGROUP, _ANYGROUP, _DUPLICATOR, _GROUP, _NEGATE, _FUTURENEGATE = range(1, 7)

def _bolg_to_regex(pattern):
    regex = ''
    i, x = 0, ' '
    pattern_len = len(pattern)
    escape, was_escaped = False, False
    insides = [None]
    while i < pattern_len: 
        x = pattern[i]
        c = pattern[i:]
        inside = insides[-1]
        if not escape and x == '\\':
            escape = True
            i += 1
            continue
        if escape:
            # \\, \[, etc.
            x = _escape(x, True)
            escape = False
            was_escaped = True
        else:
            x = _re_escape(x)
            if was_escaped:
                was_escaped = False

        if inside == _GROUP:
            assert x in 'ans', '{} is not a proper group'.format(repr(':' + x))
            regex += '\\' + _scd[x]
            insides.pop()
        elif inside == _DUPLICATOR:
            insides.pop()
            if x == extra:
                regex += '.' + extra
            else:
                regex += '.' + extra + '?'
                if was_escaped:
                    escape = True # character has not been used
                continue
        elif inside == _NEGATE:
            if x == '^':
                insides[-1] = _FUTURENEGATE
            else:
                if x == '{':
                    regex += '(?!('
                    insides.append(_ANYGROUP)
                else:
                    regex += '[^{}]'.format(x)
        elif inside == _FUTURENEGATE:
            regex += '(?!{})'.format(x)
            insides.pop()
        elif inside == _LETTERGROUP:
            regex += x
            if x == ']':
                insides.pop()
        elif inside == _ANYGROUP:
            if x == '}':
                regex += ')'
                insides.pop()
                if insides[-1] == _NEGATE:
                    regex += ')'
                    insides.pop()
            elif x == ',' and not was_escaped:
                regex += '|'
            else:
                inside = None # Let it be parsed like global text
        if inside:
            i += 1
            continue

        # [^23-41]
        m = _notrange_re.match(c)
        if not was_escaped and m:
            regex += _notrangefunc(m.group(1), m.group(2))
            i += len(m.group(0))
            continue
        # [23-41]
        m = _range_re.match(c)
        if not was_escaped and m:
            regex += _rangefunc(m.group(1), m.group(2))
            i += len(m.group(0))
            continue

        if x == '[':
            insides.append(_LETTERGROUP)
            regex += '['
        elif x == '{':
            insides.append(_ANYGROUP)
            regex += '('
        elif x in '*+':
            insides.append(_DUPLICATOR)
            extra = x
        elif x == '?':
            regex += '.'
        elif not was_escaped and x == ':':
            insides.append(_GROUP)
        elif x == '^':
            insides.append(_NEGATE)
        else:
            regex += x
        i += 1
    if insides[-1] == _DUPLICATOR:
        regex += '.' + extra + '?'
        insides.pop()
    if escape:
        regex += '\\'
    assert insides[-1] != _ANYGROUP, 'no end }' + regex
    assert insides[-1] != _LETTERGROUP, 'no end ]'
    return regex

class PortableRegex:
    """
    A simple regex container
    """
    def __init__(self, regex, ignore_case=False):
        self.set_regex(regex, ignore_case)

    def set_regex(self, regex, ignore_case=False):
        if isinstance(regex, re._pattern_type):
            self.comp_regex = regex
            self.regex = self.comp_regex
            self.compiled = True
        else:
            self.raw_regex = regex
            self.regex = self.raw_regex
            self.compiled = False
        self.ignore_case = ignore_case
        self._update()

    def compile(self, force=False):
        '''
        compile(force=False) -> regex|(regex,)

        Compile if not already compiled, and return the Python regex object or
        tuple of regex objects.
        '''
        if force or not self.compiled:
            self._compile()
        return self.comp_regex

    def re(self):
        '''
        re() -> str|(str,)

        Get the Python regex string or a tuple of regex strings.
        '''
        return self.raw_regex

    def _compile(self):
        if isinstance(self.raw_regex, str):
            self.comp_regex = self._compile_one(self.raw_regex)
        else:
            self.comp_regex = tuple(self._compile_one(x) for x in self.raw_regex)
        self.regex = self.comp_regex
        self.compiled = True
        self._update()

    def _compile_one(self, regex):
        return re.compile(regex, re.I if self.ignore_case else 0)

    def _update(self):
        if self.compiled:
            self.match = self._match
        else:
            self.match = self._match1

    def _match(self, x):
        return self.comp_regex.match(x)

    def _match1(self, x):
        self.compile()
        return self._match(x)

def _choose_ignore_case(expr, ignore_case=False):
    if expr.endswith('/i'):
        return expr[:-2], True
    else:
        return expr, ignore_case

def bolg_to_regex(expression, ignore_case=False, accept_expr_ignore_case=True):
    '''
    bolg_to_regex(expression, cmpile=True) -> PortableRegex

    Convert a bolg expression to a Python regex (stored in a wrapper)
    '''
    if accept_expr_ignore_case:
        expression, ignore_case = _choose_ignore_case(expression, ignore_case)
    regex = PortableRegex(_bolg_to_regex(expression) + '$', ignore_case)
                                   # $ to force it to look at everything
    return regex

def bolg(expression, strings=None, ignore_case=False, alrdy_regex=False):
    '''
    bolg(expression, strings:list, ignore_case=False) -> list

    If strings is not None, return the strings in strings which match
    pattern. Else, return bolg_files(expression). If alrdy_regex, do not
    attempt to convert expression to a regex.
    '''
    if not strings:
        return bolg_files(expression, None, ignore_case)
    if not alrdy_regex and isinstance(expression, str):
        expression = bolg_to_regex(expression, True, ignore_case)
    nstrings = tuple(filter(expression.match, strings))
    return nstrings

_DIRS, _FILES, _DIRSANDFILES = range(1, 4)
    
def bolg_files(expression, path='', ignore_case=False, return_regex=False):
    '''
    bolg_files(expression:string|PortableRegex, path:str='',
               ignore_case=False, return_regex=False) -> [str]|PortableRegex

    Return all the files and/or directories which match the expression. If
    path is None, the current working directory is used. Return a list of
    filenames if not return_regex, else return the generated regex.
    '''
    if not isinstance(expression, str):
        return _bolg_files(expression)
    expression, ignore_case = _choose_ignore_case(expression, ignore_case)
    pattern = re.sub(r'^(\.{})+'.format('\\' + os.sep), '', expression)
    # remove ./././ ...

    p = os.path.expanduser(pattern)
    if p != pattern:
        # Is something like ~/blah or ~user/bluh
        st = pattern.find(os.sep)
        if st == -1:
            lt = 0
        else:
            lt = len(pattern) - st
        lt = len(p) - lt
        path = os.path.join(path, p[:lt])
        if st == -1:
            return paths
        pattern = p[lt + 1:]
    elif pattern.startswith(os.sep):
        path = os.sep
        pattern = pattern[1:]
    elif pattern.startswith('..' + os.sep):
        pattern = pattern[3:]
        path = os.path.join(path, '..')
        while pattern.startswith('..' + os.sep):
            pattern = pattern[3:]
            path = os.path.join(path, '..')
    if not path:
        path = '.'
    paths = [path]
    if pattern.endswith(os.sep):
        lookfor = _DIRS
        pattern = pattern[:-1]
    elif pattern.endswith(os.sep + 'b'):
        lookfor = _DIRSANDFILES
        pattern = pattern[:-2]
    else:
        lookfor = _FILES

    regex = bolg_to_regex(pattern, ignore_case, False)
    rsp = regex.re().split(os.sep)
    regex.set_regex(tuple(itertools.chain((x + '$' for x in rsp[:-1]),
                                          (rsp[-1],))))
    regex._lookfor = lookfor
    regex._paths = paths
    if return_regex:
        return regex
    return _bolg_files(regex)

def _bolg_files(regex):
    lookfor = regex._lookfor
    paths = regex._paths
    regex = regex.compile()
    for sub in regex[:-1]:
        npaths = []
        for p in paths:
            for x in os.listdir(p):
                n = os.path.join(p, x)
                if os.path.isdir(n) and sub.match(x):
                    npaths.append(n)
        paths = npaths
    nfiles = []
    sub = regex[-1]
    if lookfor == _DIRS:
        # Only match directories
        for p in paths:
            for x in os.listdir(p):
                n = os.path.join(p, x)
                if os.path.isdir(n) and sub.match(x):
                    nfiles.append(n)
    elif lookfor == _FILES:
        # Only match files
        for p in paths:
            for x in os.listdir(p):
                n = os.path.join(p, x)
                if os.path.isfile(n) and sub.match(x):
                    nfiles.append(n)
    elif lookfor == _DIRSANDFILES:
        # Match both directories and files
        for p in paths:
            for x in os.listdir(p):
                if sub.match(x):
                    n = os.path.join(p, x)
                    nfiles.append(n)
    nfiles.sort()
    return nfiles

class _OptionParser(OptionParser):
    '''A slightly modified OptionParser'''
    def format_epilog(self, formatter):
        return self.epilog

def command_line(args=None):
    '''
    Allow easy use from the command-line. If ``args`` is None,
    ``sys.argv[1:]`` is used.
    '''
    parser = _OptionParser(
        prog='bolg',
        usage='Usage: %prog EXPRESSION [DIR]',
        description='match glob-regexes against files',
        version='''\
bolg 0.1.0
Copyright (C) 2010  Niels Serup
Apache License 2.0 <http://www.apache.org/licenses/LICENSE-2.0>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''',
        epilog='''
This utility will return a space-separated list of all the files which matches
EXPRESSION. If DIR is specified, DIR will be considered the current working
directory.

Extensive bolg documentation is available. To view it, run ``pydoc3
bolg``.

''' + _cmd_examples)

    parser.add_option('-i', '--ignore-case', dest='ignore_case',
                      action='store_true', default=False,
                      help='ignore case')

    options, args = parser.parse_args(*((args,) if args else tuple()))
    try:
        options.expression = args[0]
    except IndexError:
        parser.error('no pattern specified')
    try:
        options.curdir = args[1]
    except IndexError:
        options.curdir = ''

    files = bolg_files(options.expression, options.curdir, options.ignore_case)
    print(' '.join(repr(x) for x in files))

if __name__ == '__main__':
    command_line()
