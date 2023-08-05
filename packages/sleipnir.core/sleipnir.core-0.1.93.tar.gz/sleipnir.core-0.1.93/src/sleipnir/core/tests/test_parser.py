#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Test classes for sleipnir.core.idioms.parser"""

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here required modules
import io
import re

__all__ = ['TestParser']

# Project dependences
from sleipnir.testing.data import DATA
from sleipnir.testing.test import TestCase, create_suite, run_suite

# Submodule dependences
from sleipnir.core.parser import Parser


#pylint: disable-msg=R0904
class TestParser(TestCase):
    """Main TestCase for Parser Class"""

    class CustomParser(Parser):
        """Private Class to define a TestParser"""

        def __init__(self):
            def tok_event(*args):
                """An TOK event handler"""
                self.tok_event_called = True
                assert len(args) > 0

            super(TestParser.CustomParser, self).__init__()
            self.tokens['tok'] = "(.*)"
            self.events['tok'].connect(tok_event)
            self.tok_event_called = False

        #pylint: disable-msg=C0103
        def scanner_TOK(self):
            """handler for parser 'TOK' token"""
            return re.compile(r"%(tok)s" % self.tokens, re.DOTALL)

        def test_parse_file(self, where):
            """Parse 'where' file to lokkup for valid tokens"""
            return self.parse(where)

    #pylint: disable-msg=C0103
    def setUp(self):
        self.file = DATA().dct[-1]
        self.strm = io.open(self.file, "r").read()

    def test_abstract_parser(self):
        """Test that Parser could handler streams and file locations"""

        class TestAbstractParser(Parser):
            """Abstract Parser class"""

            def __init__(self):
                super(TestAbstractParser, self).__init__()

            def test_parse_file(self, where):
                """Parse a file location or descriptor"""
                self.parse(where)

            def test_parse_stream(self, where):
                """Parse a chunk of bytes"""
                self.parse(where)

        parser = TestAbstractParser()
        self.assertRaises(
            NotImplementedError, parser.test_parse_file, self.file)
        self.assertRaises(
            NotImplementedError, parser.test_parse_stream, self.strm)

    def test_good_parser(self):
        """Check that a well formed parser works properly"""

        class TestParserSuccess(TestParser.CustomParser):
            """Test Class"""

            def __init__(self):
                self.on_tok_called = False
                super(TestParserSuccess, self).__init__()

            @Parser.group('index')
            def on_tok(self, value):
                """'TOK' handler"""
                assert value and type(value) in (str, unicode,)
                self.on_tok_called = True
                return True

        parser = TestParserSuccess()
        parser.test_parse_file(self.file)

        assert parser.on_tok_called == True
        assert parser.tok_event_called

    def test_bad_parser(self):
        """Check that a class without token handlers raise exceptions"""

        class TestParserFail(TestParser.CustomParser):
            """ Custom Class"""

        parser = TestParserFail()
        self.assertRaises(
            NotImplementedError, parser.test_parse_file, self.file)

#pylint: disable-msg=C0103
main_suite = create_suite([TestParser, ])

if __name__ == '__main__':
    #pylint: disable-msg=E1120
    run_suite()
