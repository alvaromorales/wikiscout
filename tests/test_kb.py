import unittest
from wikiscout.wikikb import WikiKB
import wikiscout.infobox as infobox

class TestInfobox(unittest.TestCase):
    def test_cls(self):
        self.assertEqual('wikipedia-president', infobox.get_class(' Infobox president  \n'))

class TestGetClasses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._kb = WikiKB('nauru')

    def test_no_classes(self):
        self.assertEquals([],self._kb.get_classes('foobarbaz'))

    def test_officeholder(self):
        expected = ['wikipedia-term','wikipedia-paragraphs','wikipedia-officeholder']
        self.assertItemsEqual(expected,self._kb.get_classes('Barack Obama'))

    def test_country(self):
        expected = ['wikipedia-term','wikipedia-paragraphs','wikipedia-country']
        self.assertItemsEqual(expected,self._kb.get_classes('Peru'))
        
class TestGetAttributes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._kb = WikiKB('nauru')

    def test_wrong_classname(self):
        self.assertEquals([],self._kb.get_attributes('wikipedia-officeholder','Peru'))
        
    def test_officeholder(self):
        expected = [u'NAME', u'IMAGE', u'ALT', u'ORDER', u'OFFICE', u'VICEPRESIDENT', u'TERM-START', u'PREDECESSOR', u'STATE2', u'TERM-START2', u'TERM-END2', u'PREDECESSOR2', u'SUCCESSOR2', u'OFFICE3', u'TERM-START3', u'TERM-END3', u'PREDECESSOR3', u'SUCCESSOR3', u'BIRTH-NAME', u'BIRTH-DATE', u'BIRTH-PLACE', u'PARTY', u'SPOUSE', u'CHILDREN', u'RESIDENCE', u'ALMA-MATER', u'PROFESSION', u'RELIGION', u'BLANK1', u'DATA1', u'SIGNATURE', u'SIGNATURE-ALT', u'WEBSITE',u'JR/SR2']
        self.assertItemsEqual(expected,self._kb.get_attributes('wikipedia-officeholder','Barack Obama'))
    
    def test_person(self):
        expected = [u'NAME', u'IMAGE', u'IMAGE-SIZE', u'ALT', u'CAPTION', u'BIRTH-NAME', u'BIRTH-DATE', u'BIRTH-PLACE', u'RESIDENCE', u'ALMA-MATER', u'OCCUPATION', u'YEARS-ACTIVE', u'NET-WORTH', u'BOARDS', u'RELIGION', u'SPOUSE', u'CHILDREN', u'PARENTS', u'SIGNATURE', u'SIGNATURE-ALT', u'WEBSITE']
        self.assertItemsEqual(expected,self._kb.get_attributes('wikipedia-person','Bill Gates'))
    
    def test_president(self):
        expected = [u'NAME', u'IMAGE', u'ORDER', u'OFFICE', u'VICEPRESIDENT', u'TERM-START', u'TERM-END', u'PREDECESSOR', u'SUCCESSOR', u'ORDER1', u'OFFICE1', u'LIEUTENANT1', u'TERM-START1', u'TERM-END1', u'PREDECESSOR1', u'SUCCESSOR1', u'LIEUTENANT2', u'TERM-START2', u'TERM-END2', u'PREDECESSOR2', u'SUCCESSOR2', u'ORDER3', u'OFFICE3', u'GOVERNOR3', u'TERM-START3', u'TERM-END3', u'PREDECESSOR3', u'SUCCESSOR3', u'BIRTH-NAME', u'BIRTH-DATE', u'BIRTH-PLACE', u'DEATH-DATE', u'DEATH-PLACE', u'PARTY', u'SPOUSE', u'CHILDREN', u'ALMA-MATER', u'RELIGION', u'SIGNATURE', u'SIGNATURE-ALT', u'WEBSITE']
        self.assertItemsEqual(expected,self._kb.get_attributes('wikipedia-president','Bill Clinton'))

class TestGet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._kb = WikiKB('nauru')
    
    def test_get_alma_mater(self):
        expected = 'Edmund A.Georgetown University (B.S.)<br />University College, Oxford<br />Yale University (J.D.)'
        self.assertEquals(expected,self._kb.get("wikipedia-president", "Bill Clinton", "ALMA-MATER"))

    def test_birth_place(self):
        expected = 'Seattle, WA, US'
        self.assertEquals(expected,self._kb.get("wikipedia-person", "Bill Gates", "BIRTH-PLACE"))
