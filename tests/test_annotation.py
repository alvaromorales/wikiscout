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
