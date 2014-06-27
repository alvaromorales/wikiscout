import unittest
from wikiscout import sentence

class TestValidate(unittest.TestCase):
    def test_invalid_period(self):
        self.assertFalse(sentence.validate('TEMPLATE[DEFAULTSORT:Clinton,_Bill]'))

    def test_invalid_infobox(self):
        self.assertFalse(sentence.validate('TEMPLATE[Infobox_officeholder, name          = Bill Clinton]'))

    def test_valid(self):
        self.assertTrue(sentence.validate('Clinton left office with high approval ratings and was succeeded by George W. Bush.'))

class TestNormalize(unittest.TestCase):
    def test_normalize_template(self):
        self.assertEqual(sentence.normalize('In 2013, Clinton started following Buddhist meditation to help him relax.TEMPLATE[cite_web, url=http://www.dailymail.co.uk/news/article-2183101/Bill-Clinton-turns-art-Buddhist-meditation-relax.html, title=Chill Bill: Clinton turns to the art of Buddhist meditation to relax, accessdate=March 6, 2013]'), 'In 2013, Clinton started following Buddhist meditation to help him relax.')

    def test_normalize_ref_template(self):
        self.assertEqual(sentence.normalize('TEMPLATE[refimprove, date=March 2011]   Michael Crichton (October 23, 1942 - November 4, 2008) was an American author of many books.'),'Michael Crichton (October 23, 1942 - November 4, 2008) was an American author of many books.')

    def test_no_change(self):
        self.assertEqual(sentence.normalize('In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.'),'In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.')

