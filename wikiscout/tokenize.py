from collections import namedtuple
import start
import logging

logger = logging.getLogger(__name__)

Token = namedtuple('Token', ['value'])


class Tokenization:
    def __init__(self, start_tokenization):
        self.tokens = [Token(t) for t in start_tokenization['tokens']['token']]
        self.original = self.tokens[:]
        self.unknown_words = []
        if start_tokenization['unknown-words'] is not None:
            self.unknown_words = [Token(t) for t in
                                  start_tokenization['unknown-words']['token']]

    @staticmethod
    def replace_token(token, new_value):
        new_token = Token(new_value)
        logger.debug('Replaced %s with %s' % (token, new_token))
        return new_token

    def join_tokens(self):
        return " ".join([t.value for t in self.tokens])

    def __str__(self):
        return "Tokenization(%s)" % self.tokens


def tokenize(sentence):
    response = start.tokenize(sentence)
    tokenizations = response['tokenizations']['tokenization']
    return [Tokenization(t) for t in tokenizations]
