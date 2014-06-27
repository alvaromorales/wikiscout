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
        self.assertEqual(sentence.normalize('TEMPLATE[refimprove, date=March 2011]   Michael Crichton (October 23, 1942 - November 4, 2008) was an American author of many books.'), 'Michael Crichton was an American author of many books.')

    def test_no_change(self):
        self.assertEqual(sentence.normalize('In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.'), 'In 1994, during Clinton\'s first term in office, the Congress switched to a Republican majority.')


class TestContains(unittest.TestCase):
    def test_exact_value_match(self):
        s = "Mark Zuckerberg went to Harvard University."
        value = "Harvard University"
        self.assertTrue(sentence.has_value(s, value))

    def test_possessive_value_match(self):
        s = "Mark Zuckerberg is one of Harvard University's most notable alumni."
        value = "Harvard University"
        self.assertTrue(sentence.has_value(s, value))

    def test_synonym_match(self):
        s = "Mark Zuckerberg went to Harvard."
        values = ["Harvard University", "Harvard"]
        self.assertTrue(sentence.contains(s, values))

    def test_possessive_synonym_match(self):
        s = "Mark Zuckerberg is one of Harvard's most notable alumni."
        values = ["Harvard University", "Harvard"]
        self.assertTrue(sentence.contains(s, values))


class TestContainsObject(unittest.TestCase):
    def test_title_match(self):
        s = 'Bill Clinton married Hillary Clinton'
        title = 'Bill Clinton'
        gender = 'masculine'
        synonyms = []
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))

    def test_possessive_title(self):
        s = 'Bill Clinton\'s wife is Hillary Clinton'
        title = 'Bill Clinton'
        gender = 'masculine'
        synonyms = []
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))

    def test_no_title_match(self):
        s = 'Barack Obama is the president of the US'
        title = 'Bill Clinton'
        gender = 'masculine'
        synonyms = []
        self.assertFalse(sentence.contains_object(s, title, gender, synonyms))

    def test_synonym(self):
        s = 'Mark Zuckerberg went to Harvard'
        title = 'Harvard University'
        gender = 'neuter'
        synonyms = ["Harvard College", "Harvard"]
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))

    def test_possessive_synonym(self):
        s = 'Mark Zuckerberg is one of Harvard\'s most notable alumni'
        title = 'Harvard University'
        gender = 'neuter'
        synonyms = ["Harvard College", "Harvard"]
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))

    def test_no_synonym(self):
        s = 'Drew Houston went to MIT'
        title = 'Harvard University'
        gender = 'neuter'
        synonyms = ["Harvard University", "Harvard"]
        self.assertFalse(sentence.contains_object(s, title, gender, synonyms))

    def test_pronoun(self):
        s = 'He married Hillary Clinton'
        title = 'Bill Clinton'
        gender = 'masculine'
        synonyms = []
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))

    def test_possessive_pronoun(self):
        s = 'Her husband is Bill Clinton'
        title = 'Hillary Clinton'
        gender = 'femenine'
        synonyms = []
        self.assertTrue(sentence.contains_object(s, title, gender, synonyms))
