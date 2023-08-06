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

import bolg
import unittest

_equal = (
    ('?', '.'),
    ('\\?', '\\?'),
    ('+', '.+?'),
    ('*', '.*?'),
    ('++', '.+'),
    ('**', '.*'),
    (':a', '\\w'),
    (':n', '\\d'),
    (':s', '\\s'),
    (':a:a', '\\w\\w'),
    ('[abcd]', '[abcd]'),
    ('[ab\:]', '[ab:]'),
    ('[1-7]', '[1-7]'),
    ('[21-78]', '(2[1-9]|7[0-8]|[3-6][0-9])'),
    ('[311-541]', '(3(1[1-9]|[2-9][0-9])|5(4[01]|[0-3][0-9])|4[0-9]{2})'),
    ('{a,b}', '(a|b)'),
    ('{a,{b,c}}', '(a|(b|c))'),
    ('[^ua]', '[^ua]'),
    ('.', '\\.'),
    ('{ua,.\\,}', '(ua|\\.,)'),
    ('^{ua,.\\,}', '(?!(ua|\\.,))'),
    ('^x', '[^x]'),
    ('^\\*', '[^\\*]'),
    ('^^t', '(?!t)'),
    ('{abc,{def,[^1-3]}}', '(abc|(def|(0|[4-9])))'),
    )

_raises = (
    '[2-44]',
    '[823-120]',
    '{a,b',
    '[ab',
    )

_i_case = (
    ('{hello,goodbye}/i', 'HeLLo'),
    ('[abc][abc][abc][abc][abc][abc]/i', 'AaBbCc'),
    )

class TestBolg(unittest.TestCase):
    def test_equal(self):
        for b, r in _equal:
            print('{} => {}'.format(b, r))
            self.assertEqual(bolg._bolg_to_regex(b), r)

    def test_raises(self):
        print('-' * 40)
        for b in _raises:
            print(b)
            self.assertRaises(Exception, bolg._bolg_to_regex, b)

    def test_ignore_case(self):
        print('-' * 40)
        for b, t in _i_case:
            print('{} : {}'.format(b, t))
            self.assertEqual(bool(bolg.bolg_to_regex(b).match(t)), True)

if __name__ == '__main__':
    unittest.main()
