import unittest
from wikiscout import tokenize


class TestComma(unittest.TestCase):
    def test_within_token(self):
        sentence = 'Osgoode Hall Law School is in Toronto, Ontario Canada.'
        expected = 'Osgoode Hall Law School is in Toronto, Ontario Canada'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)

    def test_multiple_replacements(self):
        sentence = 'Air France Flight 447 was a scheduled commercial flight from Rio De Janeiro, Brazil, to Paris, France.'
        expected = 'Air France Flight any-number was a scheduled commercial flight from Rio De Janeiro, Brazil to Paris, France'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()

        self.assertEquals(actual, expected)

    def test_outside_token(self):
        sentence = 'Ludmilla Radchenko  (, born November 11, 1978 in Omsk, Soviet Union) is a Russian model, artist and actress.'
        expected = 'Ludmilla Radchenko is a Russian model artist and actress'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)


class TestTruecase(unittest.TestCase):
    def test_simple(self):
        sentence = 'They have a varsity team and they compete in the Big East Conference'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, sentence)

    def test_no_capitalization(self):
        sentence = 'Curtin University is the largest university in Australia'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, sentence)

    def test_with_commas(self):
        sentence = 'Charing is a village and civil parish in Kent, England'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, sentence)

    def test_case_with_parens(self):
        sentence = 'Space Shuttle Endeavour (OV-105) is a space shuttle run by NASA.'
        expected = 'Space Shuttle Endeavour is a space shuttle run by NASA'
        tokenization = tokenize.tokenize(sentence)
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)
