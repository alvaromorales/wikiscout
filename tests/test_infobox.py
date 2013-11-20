import unittest
from scout.tools import infobox

class TestNormalizeTemplate(unittest.TestCase):
    def test_caps(self):
        assert infobox.normalize_template('INFOBOX_template') == 'infobox_template'

    def test_underscores(self):
        assert infobox.normalize_template('infobox__officeholder') == 'infobox_officeholder'

    def test_spaces(self):
        assert infobox.normalize_template(' INFOBOX__PERSON ') == 'infobox_person'

class TestNormalizeAttribute(unittest.TestCase):
    def test_valid(self):
        assert infobox.normalize_attribute('birth_date') == 'birth_date'

    def test_numbers(self):
        assert infobox.normalize_attribute('PREdecessor1') == 'predecessor'

    def test_spaces(self):
        assert infobox.normalize_attribute(' SUCCESSOR__17   ') == 'successor'

class TestValidationRules(unittest.TestCase):
    def test_valid_attribute(self):
        assert infobox.validate_attribute('predecessor3') == True

    def test_invalid_attribute(self):
        assert infobox.validate_attribute('1') == False

    def test_valid_template(self):
        assert infobox.validate_template('infobox_officeholder') == True

    def test_invalid_template(self):
        assert infobox.validate_template('infobox_person/template') == False

class TextInfoboxParsing(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.article = {"title":"Bill Clinton","wikiTitle":"Bill_Clinton","wid":5424,"lang":"en","namespace":"","integerNamespace":0,"timestamp":"2013-10-21T13:51:33Z","type":"ARTICLE","paragraphs":["William Jefferson Clinton (born on August 19, 1946 as William Jefferson Blythe III), better known as Bill Clinton, is an American lawyer who was the 42nd President of the United States.  He served from 1993 to 2001.","Clinton married Hillary Rodham in 1975. In 1980, their daughter, Chelsea Clinton, was born.","TEMPLATE[wikiquote, Bill Clinton] TEMPLATE[commons, Bill Clinton]"],"highlights":["William Jefferson Clinton","William Jefferson Blythe III","Bill Clinton","My Life"],"infobox":{"name":"Infobox_officeholder","description":["name          = Bill Clinton","vicepresident = [[Al Gore]]","term_start    = January 20, 1993", "1    = invalid attribute", "no_value    = "]}}

    def test_parse(self):
        infobox.parse(self.article['infobox']['name'], self.article['infobox']['description'])
        
    def test_get_attributes(self):
        article_infobox = infobox.parse(self.article['infobox']['name'], self.article['infobox']['description'])
        self.assertItemsEqual(infobox.get_attributes(article_infobox),['name','vicepresident','term_start','no_value'])

    def test_get_all_attributes(self):
        article_infobox = infobox.parse(self.article['infobox']['name'], self.article['infobox']['description'])
        self.assertItemsEqual(infobox.get_all_attributes(article_infobox),['name','vicepresident','term_start','no_value','1'])

    def test_get_items(self):
        article_infobox = infobox.parse(self.article['infobox']['name'], self.article['infobox']['description'])
        self.assertItemsEqual(infobox.get_items(article_infobox), [('name','Bill Clinton'), ('vicepresident','Al Gore'), ('term_start', 'January 20, 1993')])
