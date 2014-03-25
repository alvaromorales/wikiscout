import start
import logging
import corenlp

logger = logging.getLogger(__name__)


numbers = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
           6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
           11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
           15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
           19: 'nineteen', 20: 'twenty'}

class Token:
    def __init__(self, value):
        self.value = value
        self.original = value
        self.is_possessive = value.endswith('\'s')

    def noun(self):
        if self.is_possessive:
            return self.value[:-2]
        return self.value

    def index(self, i):
        if self.is_possessive:
            return self.noun() + '-%s' % numbers[i] + '\'s'
        else:
            return self.value + '-%s' % numbers[i]


class Tokenization:
    def __init__(self, start_tokenization):
        self.tokens = [Token(t) for t in start_tokenization['tokens']['token']]
        self.unknown_words = []
        if start_tokenization['unknown-words'] is not None:
            self.unknown_words = [Token(t) for t in
                                  start_tokenization['unknown-words']['token']]

    @staticmethod
    def replace_token(token, new_value):
        token.value = new_value
        logger.debug('Replaced %s with %s' % (token.original, token.value))
        return token

    def join_tokens(self):
        """Join tokens and index multiple occurrences of a matching symbol"""
        normalized = [t.noun() for t in self.tokens]
        tokens = []
        
        index_counts = {}
        indexed_tokens = {}

        for i,t in enumerate(normalized):
            token = self.tokens[i]
            if t.startswith('any-'):
                if normalized.count(t) > 1:
                    if token.original in indexed_tokens:
                        tokens.append(indexed_tokens[token.original])
                    else:
                        if t in index_counts:
                            index_counts[t] += 1
                        else:
                            index_counts[t] = 1
                        i = index_counts[t]
                        indexed = token.index(i)
                        indexed_tokens[token.original] = indexed
                        tokens.append(indexed)
                else:
                    tokens.append(token.value)
            else:
                tokens.append(token.value)

        annotation = " ".join(tokens)
        annotation = corenlp.ner(annotation)
        return annotation

    def __str__(self):
        return "Tokenization(%s)" % ([t.value for t in self.tokens])


def tokenize(sentence):
    response = start.tokenize(sentence)
    tokenizations = response['tokenizations']['tokenization']
    if type(tokenizations) is list:
        return [Tokenization(t) for t in tokenizations]
    else:
        return [Tokenization(tokenizations)]
