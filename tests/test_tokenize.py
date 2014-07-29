import unittest
from wikiscout import tokenize


class TestComma(unittest.TestCase):
    def test_within_token(self):
        sentence = 'Osgoode Hall Law School is in Toronto, Ontario Canada.'
        expected = 'Osgoode Hall Law School is in Toronto, Ontario Canada'
        tokenization = tokenize.tokenize(sentence)[0]
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)

    def test_multiple_replacements(self):
        sentence = 'Air France Flight 447 was a scheduled commercial flight from Rio De Janeiro, Brazil, to Paris, France.'
        expected = 'Air France Flight any-number was a scheduled commercial flight from Rio De Janeiro, Brazil to Paris, France'
        tokenization = tokenize.tokenize(sentence)[0]
        actual = tokenization.join_tokens()

        self.assertEquals(actual, expected)

    def test_outside_token(self):
        sentence = 'Ludmilla Radchenko  (, born November 11, 1978 in Omsk, Soviet Union) is a Russian model, artist and actress.'
        expected = 'Ludmilla Radchenko is a Russian model artist and actress'
        tokenization = tokenize.tokenize(sentence)[0]
        actual = tokenization.join_tokens()
        self.assertEquals(actual, expected)
