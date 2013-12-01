import unittest
from scout.tools.annotation import Annotation

class TestGenerateSymbol(unittest.TestCase):
    def test_infobox_template(self):
        self.assertEqual(Annotation.generate_symbol('infobox_officeholder'),'any-wikipedia-officeholder')

    def test_wikipedia_symbol(self):
        self.assertEqual(Annotation.generate_symbol('Wikipedia-Person'), 'any-wikipedia-person')

    def test_invalids(self):
        self.assertIsNone(Annotation.generate_symbol('foo'))

class TestGetClass(unittest.TestCase):
    pass

class TestSubTitle(unittest.TestCase):
    def test_simple(self):
        sentence = "Bill Clinton married Hillary Clinton in 1975."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)

        self.assertEqual(annotation.sub_title(),"any-wikipedia-officeholder married Hillary Clinton in 1975.")

    def test_possesive(self):
        sentence = "Bill Clinton's wife is Hillary Clinton."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)

        self.assertEqual(annotation.sub_title(),"any-wikipedia-officeholder's wife is Hillary Clinton.")
    
    def test_no_title(self):
        sentence = "Hillary Rodham Clinton was born in Chicago."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)
        
        self.assertIsNone(annotation.sub_title())

class TestSubPronoun(unittest.TestCase):
    def test_possesive(self):
        sentence = "He was born in Arkansas."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)

        self.assertEquals(annotation.sub_pronoun(),"any-wikipedia-officeholder was born in Arkansas.")

    def test_subjective(self):
        sentence = "His father was William Jefferson Blythe, Jr."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)

        self.assertEquals(annotation.sub_pronoun(),"any-wikipedia-officeholder's father was William Jefferson Blythe, Jr.")
        
    def test_no_pronoun(self):
        sentence = "Georgetown was his alma mater."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)

        self.assertIsNone(annotation.sub_pronoun())
    
class TestSubHighlights(unittest.TestCase):
    def test_longest_highlight(self):
        sentence = "William Jefferson Clinton was a US president."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,title,template,highlights=highlights)
        
        self.assertEquals(annotation.sub_highlights(),"any-wikipedia-officeholder was a US president.")

    def test_possesive(self):
        sentence = "Clinton's nickname is Bill."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,title,template,highlights=highlights)
        
        self.assertEquals(annotation.sub_highlights(),"any-wikipedia-officeholder's nickname is Bill.")
        
    def test_no_highlights(self):
        sentence = "Barack Obama is the president of the US."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        highlights = ['William Jefferson Clinton', 'William Jefferson Blythe III', 'Bill Clinton', 'My Life','Bill','Clinton']

        annotation = Annotation(sentence,title,template,highlights=highlights)
        
        self.assertIsNone(annotation.sub_highlights())

class TestSubWikipediaBaseSymbols(unittest.TestCase):
    def test(self):
        sentence = "William Clinton was the president of the US."
        title = "Bill Clinton"
        template = "infobox_officeholder"
        
        annotation = Annotation(sentence,title,template)        
        self.assertEquals(annotation.sub_wb_subject(),"any-wikipedia-officeholder was the president of the US.")

