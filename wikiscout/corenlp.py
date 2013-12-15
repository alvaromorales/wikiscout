from string import punctuation
import jsonrpclib
from simplejson import loads
from nltk.corpus import stopwords

class CoreNLP:
    def __init__(self,host='localhost'):
        self.server = jsonrpclib.Server("http://%s:6888"%host)
        self.stopwords = set(stopwords.words('english'))
        self.punctuation = set(punctuation)
        self.tagmap = {'LOCATION': 'any-c-s-c',
                       'TIME': 'any-time',
                       'PERSON': 'any-person',
                       'ORGANIZATION': 'any-wikipedia-organization',
                       'MONEY': 'any-currency',
                       'PERCENT': 'any-percent',
                       'DATE': 'any-date'
                       }
    
    def parse(self,text):
        return loads(self.server.parse(text))

    def normalize(self,word):
        if word == '``' or word == "''":
            return '"'
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

    def ner(self,text):
        parse = self.parse(text)

        if parse is None:
            return

        new_text = []
        
        for sentence in parse['sentences']:
            if 'words' not in sentence:
                continue
            
            for word,attributes in sentence['words']:
                if word in self.stopwords or word.startswith('any-wikipedia-'):
                    new_text.append(word)
                    continue

                if 'NamedEntityTag' in attributes:
                    tag = attributes['NamedEntityTag']
                    if tag in self.tagmap:
                        if len(new_text) > 0:
                            last_word = new_text[-1]
                            if last_word == self.tagmap[tag]:
                                continue
                        new_text.append(self.tagmap[tag])
                    else:
                        word = self.normalize(word)
                        new_text.append(word)
                else:
                    word = self.normalize(word)
                    new_text.append(word)
        
        return ''.join(w if set(w) <= self.punctuation or w == "'s" else ' '+w for w in new_text).lstrip()
