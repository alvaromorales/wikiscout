import re
from nltk.tokenize import sent_tokenize

def has_value(s,value):
    return re.search(r'\b%s\b'%re.escape(value),s) is not None

def validate(sentence):
    sentence = sentence.strip()
    # valid sentences must contain at least one period
    return sentence.find('.') != -1 and re.match('TEMPLATE\[[iI]nfobox',sentence) is None

def normalize(sentence):
    sentence = re.sub('(?i)TEMPLATE\[.*?\]','',sentence)
    sentence = sentence.strip()
    return sentence

def get(paragraphs):
    paragraphs = filter(lambda p: validate(p), paragraphs)
    paragraphs = [normalize(p) for p in paragraphs]

    text = " ".join(paragraphs)
    sentences = sent_tokenize(text)
    sentences = filter(lambda s: s.find('=') == -1, sentences)
    
    return sentences
