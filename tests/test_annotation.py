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

    def test_replace_possesive_title(self):
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

    def test_replace_possesive_pronoun(self):
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

    def test_replace_possesive_synonym(self):
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

    def test_replace_possesive(self):
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
        object = 'Bill Gates'
        sentence = 'Bill Gates studied at Harvard'
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
