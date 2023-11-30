import pytest
import re

from parse_regex.lexer import lexer, RegexRange, RegexClassInterval

class TestRegexes:
    def _assert_expected(self, lexer, expected):
        for idx, tok in enumerate(lexer):
            assert (tok.type, tok.value) == expected[idx]

    def test_chars(self):
        lexer.input('ola')

        expected = [
            ('CHAR', 'o'),
            ('CHAR', 'l'),
            ('CHAR', 'a'),
        ]

        self._assert_expected(lexer, expected)

    def test_chars_curly_brackets(self):
        lexer.input('}}{{a')

        expected = [
            ('CHAR', '}'),
            ('CHAR', '}'),
            ('CHAR', '{'),
            ('CHAR', '{'),
            ('CHAR', 'a'),
        ]

        self._assert_expected(lexer, expected)

    def test_literals(self):
        lexer.input('ol)a|q++t*?>a)(')

        expected = [
            ('CHAR', 'o'),
            ('CHAR', 'l'),
            (')', ')'),
            ('CHAR', 'a'),
            ('|', '|'),
            ('CHAR', 'q'),
            ('+', '+'),
            ('+', '+'),
            ('CHAR', 't'),
            ('*', '*'),
            ('?', '?'),
            ('CHAR', '>'),
            ('CHAR', 'a'),
            (')', ')'),
            ('(', '('),
        ]

        self._assert_expected(lexer, expected)

    def test_escaped(self):
        lexer.input(r'\o\|\laa}q\w\d\+\(\)')

        expected = [
            ('ESCAPED', 'o'),
            ('ESCAPED', '|'),
            ('ESCAPED', 'l'),
            ('CHAR', 'a'),
            ('CHAR', 'a'),
            ('CHAR', '}'),
            ('CHAR', 'q'),
            ('ESCAPED', 'w'),
            ('ESCAPED', 'd'),
            ('ESCAPED', '+'),
            ('ESCAPED', '('),
            ('ESCAPED', ')'),
            ('CHAR', '\''),
        ]

        self._assert_expected(lexer, expected)

    def test_range_one(self):
        lexer.input(r'{3}')

        expected = [
            ('RANGE', RegexRange(3, 3)),
        ]

        self._assert_expected(lexer, expected)

    def test_range_both(self):
        lexer.input(r'{2,322}')

        expected = [
            ('RANGE', RegexRange(2, 322)),
        ]

        self._assert_expected(lexer, expected)

    def test_range_integration(self):
        lexer.input(r'ola}{2,3}{a{183,234}}{}}{')

        expected = [
            ('CHAR', 'o'),
            ('CHAR', 'l'),
            ('CHAR', 'a'),
            ('CHAR', '}'),
            ('RANGE', RegexRange(2, 3)),
            ('CHAR', '{'),
            ('CHAR', 'a'),
            ('RANGE', RegexRange(183, 234)),
            ('CHAR', '}'),
            ('CHAR', '{'),
            ('CHAR', '}'),
            ('CHAR', '}'),
            ('CHAR', '{'),
        ]

        self._assert_expected(lexer, expected)

    def test_class_int(self):
        lexer.input(r'[a-z]')

        expected = [
            ('[', '['),
            ('CLASS_INT', RegexClassInterval('a', 'z')),
            (']', ']'),
        ]

        self._assert_expected(lexer, expected)
