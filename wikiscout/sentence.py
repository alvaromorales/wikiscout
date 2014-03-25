import re
from nltk.tokenize import sent_tokenize
from unidecode import unidecode


def has_value(sentence, value):
    """Checks if a sentence contains a value."""
    match = re.search(r'\b%s\b' % re.escape(value), sentence)
    if match:
        return True
    else:
        match = re.search(r'\b%s\'s\b' % re.escape(value), sentence)
        return match is not None


def contains(sentence, values):
    """Check if a sentence contains a value in the values iterable."""
    for value in values:
        if has_value(sentence, value):
            return True
    return False


def validate(sentence):
    sentence = sentence.strip()
    # valid sentences must contain at least one period
    return sentence.find('.') != -1 and \
        re.match('TEMPLATE\[[iI]nfobox', sentence) is None


def normalize(sentence):
    sentence = re.sub('(?i)TEMPLATE\[.*?\]','',sentence)
    sentence = unidecode(sentence)
    sentence = sentence.strip()
    return sentence


def get(paragraphs):
    """Gets valid sentences from paragraphs."""

    paragraphs = filter(lambda p: validate(p), paragraphs)
    paragraphs = [normalize(p) for p in paragraphs]

    text = " ".join(paragraphs)
    sentences = sent_tokenize(text)
    sentences = filter(lambda s: s.find('=') == -1, sentences)

    return sentences
