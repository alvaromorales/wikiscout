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
    def __init__(self, start_tokenization, sentence):
        tokens = replace_commas(sentence, start_tokenization['tokens']['token'])
        self.tokens = [Token(t) for t in tokens]
        self.sentence = sentence
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

        for i, t in enumerate(normalized):
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


def tokenize(sentence, machine='malta'):
    response = start.tokenize(sentence, machine=machine)

    if 'tokenizations' not in response:
        return []

    tokenizations = response['tokenizations']['tokenization']
    if type(tokenizations) is list:
        return [Tokenization(t, sentence) for t in tokenizations]
    else:
        return [Tokenization(tokenizations, sentence)]


def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]


def get_surrounding(s, i):
    words = [s[i]]

    before = i-1
    while before > 0 and s[before].isalpha():
        c = s[before]
        words.insert(0, c)
        before -= 1

    after = i + 1
    if after < len(s):
        words.append(s[after])
        after += 1

    while after < len(s) and s[after].isalpha():
        c = s[after]
        words.append(c)
        after += 1

    return "".join(words)


def insert_comma(value, surround):
    without = surround.replace(',', '')
    pos = value.find(without)

    split = [value[:pos], value[pos:pos+len(without)], value[pos+len(without):]]
    split[1] = surround
    return "".join(split)


def replace_commas(sentence, tokens):
    # only add commas in between tokens (such as locations)
    last_token = -1
    for i in find(sentence, ','):
        surrounding = get_surrounding(sentence, i)
        without = surrounding.replace(',', '')
        if len(surrounding) <= 2:
            continue

        for j, t in enumerate(tokens):
            if j < last_token:
                continue

            if t.find(without) != -1:
                tokens[j] = insert_comma(t, surrounding)
                last_token = j
                break

    return tokens
