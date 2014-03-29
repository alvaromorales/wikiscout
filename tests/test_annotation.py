import copy
import unittest
from wikiscout import annotation
from wikiscout import tokenize


class TestObject(unittest.TestCase):
    def helper(self, replacement_function, sentence, object, symbol, expected):
        tokenization = tokenize.tokenize(sentence)[0]
        tokenization_copy = copy.deepcopy(tokenization)
        replacement_function(object, symbol, tokenization)
        actual = tokenization.join_tokens()
        self.assertEqual(actual, expected)

        tokenization = tokenization_copy
        annotation.replace_object(object, symbol, tokenization)
        actual = tokenization.join_tokens()
        self.assertEqual(actual, expected)

    def test_replace_title(self):
        sentence = 'Bill Clinton married Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president married Hillary Rodham'
        self.helper(annotation.replace_title, sentence,
                    object, symbol, expected)

    def test_replace_possessive_title(self):
        sentence = 'Bill Clinton\'s wife is Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president\'s wife is Hillary Rodham'
        self.helper(annotation.replace_title, sentence,
                    object, symbol, expected)

    def test_replace_pronoun(self):
        sentence = 'He married Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president married Hillary Rodham'
        self.helper(annotation.replace_pronoun, sentence,
                    object, symbol, expected)

    def test_replace_possessive_pronoun(self):
        sentence = 'His wife is Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president\'s wife is Hillary Rodham'
        self.helper(annotation.replace_pronoun, sentence,
                    object, symbol, expected)

    def test_replace_person_synonym(self):
        sentence = 'Clinton married Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president married Hillary Rodham'
        self.helper(annotation.replace_synonyms, sentence,
                    object, symbol, expected)

    def test_replace_synonym(self):
        sentence = 'William Clinton married Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president married Hillary Rodham'
        self.helper(annotation.replace_synonyms, sentence,
                    object, symbol, expected)

    def test_replace_possessive_synonym(self):
        sentence = 'William Clinton\'s wife is Hillary Rodham'
        object = 'Bill Clinton'
        symbol = 'any-wikipedia-president'
        expected = 'any-wikipedia-president\'s wife is Hillary Rodham'
        self.helper(annotation.replace_synonyms, sentence,
                    object, symbol, expected)


class TestProperNouns(unittest.TestCase):
    def test_replace_title(self):
        object = 'Bill Clinton'
        sentence = 'Bill Clinton married Hillary Rodham'
        expected = 'any-wikipedia-president married any-wikipedia-officeholder'
        tokenization = tokenize.tokenize(sentence)[0]
        annotation.replace_proper_nouns(object, tokenization)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)

    def test_replace_possessive(self):
        object = 'Bill Clinton'
        sentence = 'Hillary Clinton\'s husband is Bill Clinton'
        expected = 'any-wikipedia-officeholder\'s husband is any-wikipedia-president'
        tokenization = tokenize.tokenize(sentence)[0]
        annotation.replace_proper_nouns(object, tokenization)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)

    def test_replace_synonyms(self):
        object = 'Mark Zuckerberg'
        sentence = 'Zuck dropped out of Harvard University to start Facebook'
        expected = 'any-wikipedia-person dropped out of any-wikipedia-university to start any-wikipedia-dot-com-company'
        tokenization = tokenize.tokenize(sentence)[0]
        annotation.replace_proper_nouns(object, tokenization)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)

    def test_shortest_path(self):
        object = 'Mark Zuckerberg'
        sentence = 'Zuck studied at Harvard'
        expected = 'any-wikipedia-person studied at any-wikipedia-university'
        tokenization = tokenize.tokenize(sentence)[0]
        annotation.replace_proper_nouns(object, tokenization)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)


class TestAnnotate(unittest.TestCase):
    def test_annotate(self):
        sentence = 'Bill Clinton married Hillary Rodham'
        object = 'Bill Clinton'
        expected = 'any-wikipedia-president married any-wikipedia-officeholder'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_no_object(self):
        sentence = 'Hillary Clinton attended Wellesley College'
        object = 'Bill Clinton'
        self.assertRaises(annotation.ObjectNotFoundException,
                          annotation.annotate, sentence, object)

    def test_no_symbol(self):
        sentence = 'Bill Clinton married Hillary Rodham'
        object = 'WrongOBJECT'
        self.assertRaises(annotation.ObjectSymbolNotFoundException,
                          annotation.annotate, sentence, object)


class TestIndexSymbols(unittest.TestCase):
    def test_index(self):
        sentence = 'Brad Pitt married Angelina Jolie'
        object = 'Brad Pitt'
        expected = 'any-wikipedia-person-one married any-wikipedia-person-two'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_multiple_indexes(self):
        sentence = 'Brad Pitt married Angelina Jolie after Brad Pitt and Angelina Jolie filmed a movie together'
        object = 'Brad Pitt'
        expected = 'any-wikipedia-person-one married any-wikipedia-person-two after any-wikipedia-person-one and any-wikipedia-person-two filmed a movie together'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_possessive_index(self):
        sentence = 'Brad Pitt\'s wife is Angelina Jolie'
        object = 'Brad Pitt'
        expected = 'any-wikipedia-person-one\'s wife is any-wikipedia-person-two'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)


class TestTagDates(unittest.TestCase):
    def test_simple(self):
        sentence = 'Tom Brady signed with the Patriots in 2000 and moved to Boston'
        object = 'Tom Brady'
        expected = 'any-wikipedia-nfl-player signed with the any-wikipedia-nfl-team in any-date and moved to any-wikipedia-settlement'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_multiple(self):
        sentence = 'Clinton served as governor of Arkansas from 1979 to 1981 and again from 1983 to 1993'
        object = 'Bill Clinton'
        expected = 'any-wikipedia-president served as governor of any-wikipedia-u.s.-state from any-date-one to any-date-two and again from any-date-three to any-date-four'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_no_dates(self):
        sentence = 'It is split in 3 parts'
        object = 'The Lord of the Rings'
        expected = 'any-wikipedia-novel-series is split in 3 parts'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)


class TestCommaReplacements(unittest.TestCase):
    def test_single(self):
        sentence = 'He was born in Hibbing, Minnesota.'
        object = 'Chi Chi LaRue'
        expected = 'any-wikipedia-adult-biography was born in any-wikipedia-settlement'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)

    def test_multiple(self):
        sentence = 'US Airways runs many flights from Charlotte, North Carolina, Philadelphia, Pennsylvania and Phoenix, Arizona.'
        object = 'US Airways'
        expected = 'any-wikipedia-airline runs many flights from any-wikipedia-settlement-one any-wikipedia-settlement-two and any-wikipedia-settlement-three'
        a = annotation.annotate(sentence, object)
        self.assertEquals(a.join_tokens(), expected)
