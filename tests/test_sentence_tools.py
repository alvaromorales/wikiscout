import unittest
from scout.tools import sentence_tools

class TestValidate(unittest.TestCase):
    def test_invalid_period(self):
        self.assertFalse(sentence_tools.validate('TEMPLATE[DEFAULTSORT:Clinton,_Bill]'))

    def test_invalid_infobox(self):
        self.assertFalse(sentence_tools.validate('TEMPLATE[Infobox_officeholder, name          = Bill Clinton]'))

    def test_valid(self):
        self.assertTrue(sentence_tools.validate('Clinton left office with high approval ratings and was succeeded by George W. Bush.'))

class TestNormalize(unittest.TestCase):
    def test_normalize_template(self):
        self.assertEqual(sentence_tools.normalize('In 2013, Clinton started following Buddhist meditation to help him relax.TEMPLATE[cite_web, url=http://www.dailymail.co.uk/news/article-2183101/Bill-Clinton-turns-art-Buddhist-meditation-relax.html, title=Chill Bill: Clinton turns to the art of Buddhist meditation to relax, accessdate=March 6, 2013]'), 'In 2013, Clinton started following Buddhist meditation to help him relax.')

    def test_no_change(self):
        self.assertEqual(sentence_tools.normalize('In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.'),'In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.')

