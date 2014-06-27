import unittest
from scout.tools.annotation import Annotation

class TestGenerateSymbol(unittest.TestCase):
    def test_infobox_template(self):
        self.assertEqual(Annotation.generate_symbol('infobox_president'),'any-wikipedia-president')

    def test_wikipedia_symbol(self):
        self.assertEqual(Annotation.generate_symbol('Wikipedia-Person'), 'any-wikipedia-person')

    def test_invalids(self):
        self.assertIsNone(Annotation.generate_symbol('foo'))

class TestGetClass(unittest.TestCase):
    pass

class TestSubTitle(unittest.TestCase):
    def test_simple(self):
        sentence = "Bill Clinton married Hillary Clinton in 1975."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Hillary Clinton"

        annotation = Annotation(sentence,wiki_title,template,value)

        self.assertEqual(annotation.sub_title(),"any-wikipedia-president married Hillary Clinton in 1975.")

    def test_possesive(self):
        sentence = "Bill Clinton's wife is Hillary Clinton."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Hillary Clinton"

        annotation = Annotation(sentence,wiki_title,template,value)

        self.assertEqual(annotation.sub_title(),"any-wikipedia-president's wife is Hillary Clinton.")
    
    def test_no_title(self):
        sentence = "Hillary Rodham Clinton was born in Chicago."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Chicago"

        annotation = Annotation(sentence,wiki_title,template,value)
        
        self.assertIsNone(annotation.sub_title())

class TestSubPronoun(unittest.TestCase):
    def test_possesive(self):
        sentence = "He was born in Arkansas."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Arkansas"
        
        annotation = Annotation(sentence,wiki_title,template,value)

        self.assertEquals(annotation.sub_pronoun(),"any-wikipedia-president was born in Arkansas.")

    def test_subjective(self):
        sentence = "His father was William Jefferson Blythe, Jr."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "William Jefferson Blythe, Jr"

        annotation = Annotation(sentence,wiki_title,template,value)

        self.assertEquals(annotation.sub_pronoun(),"any-wikipedia-president's father was William Jefferson Blythe, Jr.")
        
    def test_no_pronoun(self):
        sentence = "Georgetown was his alma mater."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Georgetown"
        
        annotation = Annotation(sentence,wiki_title,template,value)

        self.assertIsNone(annotation.sub_pronoun())
    
class TestSubHighlights(unittest.TestCase):
    def test_longest_highlight(self):
        sentence = "William Jefferson Clinton was a US president."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "US president"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,wiki_title,template,value,highlights=highlights)
        
        self.assertEquals(annotation.sub_highlights(),"any-wikipedia-president was a US president.")

    def test_possesive(self):
        sentence = "Clinton's nickname is Bill."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "Bill"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,wiki_title,template,value,highlights=highlights)
        
        self.assertEquals(annotation.sub_highlights(),"any-wikipedia-president's nickname is Bill.")
        
    def test_no_highlights(self):
        sentence = "Barack Obama is the president of the US."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "president of the US"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,wiki_title,template,value,highlights=highlights)
        
        self.assertIsNone(annotation.sub_highlights())

class TestSubWikipediaBaseSymbols(unittest.TestCase):
    def test(self):
        sentence = "William Clinton was the president of the US."
        wiki_title = "Bill_Clinton"
        template = "infobox_president"
        value = "president of the US"
        
        annotation = Annotation(sentence,wiki_title,template,value)        
        self.assertEquals(annotation.sub_wb_subject(),"any-wikipedia-president was the president of the US.")

class TestIndexSymbols(unittest.TestCase):
    def test_no_indexes(self):
        annotation = "any-wikipedia-anthem is the national anthem of any-wikipedia-country."
        self.assertEquals(Annotation.index_symbols(annotation),annotation)

    def test_index(self):
        annotation = "any-wikipedia-person studied at the any-wikipedia-university from any-date to any-date."
        expected = "any-wikipedia-person studied at the any-wikipedia-university from any-date-one to any-date-two."
        self.assertEquals(Annotation.index_symbols(annotation),expected)

    def test_possesive_index(self):
        annotation = "any-wikipedia-term's any-wikipedia-term studied at the any-wikipedia-university."
        expected = "any-wikipedia-term-one's any-wikipedia-term-two studied at the any-wikipedia-university."
        self.assertEquals(Annotation.index_symbols(annotation),expected)
