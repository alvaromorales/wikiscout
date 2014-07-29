import unittest
from wikiscout import infobox_parser

class TestInfoboxTemplateNormalization(unittest.TestCase):
    def test_parens(self):
        template = 'infobox time zone (North America)'
        expected = 'wikipedia-time-zone'
        self.assertEquals(infobox_parser.get_class(template), expected)

    def test_colon(self):
        template = 'Infobox Avatar: The Last Airbender character'
        expected = 'wikipedia-avatar'
        self.assertEquals(infobox_parser.get_class(template), expected)

    def test_period(self):
        template = 'Infobox U.S. state'
        expected = 'wikipedia-us-state'
        self.assertEquals(infobox_parser.get_class(template), expected)
