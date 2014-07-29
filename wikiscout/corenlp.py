import re
from string import punctuation
import jsonrpclib
from simplejson import loads
from nltk.corpus import stopwords

tagmap = {'DATE': 'any-date',
          'NUMBER': 'any-number'}

stopwords = set(stopwords.words('english'))
punctuation = set(punctuation)
numbers = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five',
           6: 'six', 7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten',
           11: 'eleven', 12: 'twelve', 13: 'thirteen', 14: 'fourteen',
           15: 'fifteen', 16: 'sixteen', 17: 'seventeen', 18: 'eighteen',
           19: 'nineteen', 20: 'twenty'}


def _connect(host='localhost'):
    return jsonrpclib.Server("http://%s:6888" % host)


def parse(text):
    server = _connect()
    response = server.parse(text)
    return loads(response)


def index(symbol, i):
    return symbol + '-%s' % numbers[i]


def normalize(word):
    #if word == '``' or word == "''":
    #    return '"'
    if word == '-LRB-':
        return '('
    if word == '-RRB-':
        return ')'
    if word == '-LSB-':
        return '['
    if word == '-RSB':
        return ']'
    if word == '-LCB-':
        return '{'
    if word == '-RCB-':
        return '}'
    return word


def ner(text):
    text_parse = parse(text)

    if text_parse is None:
        return

    new_text = []

    for sentence in text_parse['sentences']:
        if 'words' not in sentence:
            continue

        for word, attributes in sentence['words']:
            if word in stopwords or word.startswith('any-wikipedia-'):
                new_text.append(word)
                continue

            if 'NamedEntityTag' in attributes:
                tag = attributes['NamedEntityTag']
                if tag in tagmap:
                    if len(new_text) > 0:
                        last_word = new_text[-1]
                        if last_word == tagmap[tag]:
                            continue
                    new_text.append(tagmap[tag])
                else:
                    word = normalize(word)
                    new_text.append(word)
            else:
                word = normalize(word)
                new_text.append(word)

    if new_text.count('any-date') > 1:
        count = 1
        for i, w in enumerate(new_text):
            if w == 'any-date':
                new_text[i] = index(w, count)
                count += 1

    sentence = ''.join(w if set(w) <= punctuation or w == "'s" else ' '+w for w in new_text).strip()
    sentence = re.sub(r'(\w)([\({(\[]|``)\s', r'\1 \2', sentence)
    sentence = sentence.replace('``', '"').replace('\'\'', '"')
    return sentence
