import unittest
from wikiscout import infobox

class TestGetClass(unittest.TestCase):
    def test_caps(self):
        self.assertEqual(infobox.get_class('INFOBOX_template'),'wikipedia-template')

    def test_underscores(self):
        self.assertEqual(infobox.get_class('infobox__officeholder'),'wikipedia-officeholder')

    def test_spaces(self):
        self.assertEqual(infobox.get_class(' INFOBOX__PERSON '),'wikipedia-person')

class TestNormalizeAttribute(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(infobox.normalize_attribute('birth_date'),'BIRTH-DATE')

    def test_numbers(self):
        self.assertEqual(infobox.normalize_attribute('PREdecessor1'),'PREDECESSOR')

    def test_spaces(self):
        self.assertEqual(infobox.normalize_attribute(' SUCCESSOR__17   '),'SUCCESSOR')

    def test_allow_suffix(self):
        self.assertEqual(infobox.normalize_attribute('office3',allow_suffix=True),'OFFICE3')

class TestValidationRules(unittest.TestCase):
    def test_valid_attribute(self):
        self.assertTrue(infobox.validate_attribute('PREDECESSOR3'))

    def test_invalid_attribute(self):
        self.assertFalse(infobox.validate_attribute('1'))

    def test_valid_template(self):
        self.assertTrue(infobox.validate_class('wikipedia-officeholder'))

    def test_invalid_template(self):
        self.assertFalse(infobox.validate_class('wikipedia_person/template'))

class TextInfoboxParsing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article = {"title":"Bill Clinton","wikiTitle":"Bill_Clinton","wid":5424,"lang":"en","namespace":"","integerNamespace":0,"timestamp":"2013-10-21T13:51:33Z","type":"ARTICLE","paragraphs":["William Jefferson Clinton (born on August 19, 1946 as William Jefferson Blythe III), better known as Bill Clinton, is an American lawyer who was the 42nd President of the United States.  He served from 1993 to 2001.","Clinton married Hillary Rodham in 1975. In 1980, their daughter, Chelsea Clinton, was born.","TEMPLATE[wikiquote, Bill Clinton] TEMPLATE[commons, Bill Clinton]"],"highlights":["William Jefferson Clinton","William Jefferson Blythe III","Bill Clinton","My Life"],"infobox":{"name":"Infobox_officeholder","description":["NAME          = Bill Clinton","vicepresident = [[Al Gore]]","term___start    = January 20, 1993", "1    = invalid attribute", "no_value    = "]}}

    def test_parse(self):
        infobox.Infobox(self.article['infobox'])
        
    def test_get_attributes(self):
        article_infobox = infobox.Infobox(self.article['infobox'])
        self.assertItemsEqual(article_infobox.attributes,['VICEPRESIDENT','TERM-START','NO-VALUE'])

    def test_get_attributes_raw(self):
        article_infobox = infobox.Infobox(self.article['infobox'])
        self.assertItemsEqual(article_infobox.get_attributes(raw=True),[('VICEPRESIDENT','vicepresident'),('TERM-START','term___start'),('NO-VALUE','no_value')])

    def test_get_all_attributes(self):
        article_infobox = infobox.Infobox(self.article['infobox'])
        self.assertItemsEqual(article_infobox.get_attributes(only_valid=False),['NAME','VICEPRESIDENT','TERM-START','NO-VALUE','1'])

    def test_get_all_attributes_raw(self):
        article_infobox = infobox.Infobox(self.article['infobox'])
        self.assertItemsEqual(article_infobox.get_attributes(raw=True,only_valid=False),[('NAME','NAME'),('VICEPRESIDENT','vicepresident'),('TERM-START','term___start'),('NO-VALUE','no_value'),('1','1')])

    def test_get_items(self):
        article_infobox = infobox.Infobox(self.article['infobox'])
        self.assertItemsEqual(article_infobox.items, {'VICEPRESIDENT':'Al Gore', 'TERM-START': 'January 20, 1993'})
