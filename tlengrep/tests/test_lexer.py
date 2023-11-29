import pytest
import re

from parse_regex import lexer

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

        token = lexer.token()

        assert token.type == 'RANGE'
        assert token.value.min == 3
        assert token.value.max == 3

    def test_range_both(self):
        lexer.input(r'{2,3}')

        token = lexer.token()

        assert token.type == 'RANGE'
        assert token.value.min == 2
        assert token.value.max == 3

    # Testear mezclando ranges con otras cositas
