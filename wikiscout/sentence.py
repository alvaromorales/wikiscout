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


def normalize(text):
    text = unicode(text)
    text = re.sub(r'(\S)http://', r'\1 http://', text) # whitespaces before hyperlinks
    text = re.sub(r'http://[^\s]+', ' ', text)    # hyperlinks
    text = re.sub(r'\([^)]*\)', '', text)       # brackets, removed by START anyway
    text = re.sub(r'(?i)TEMPLATE\[.*?\]','', text)  # template tags
    text = re.sub('&nbsp;', ' ', text)              # common html entity
    text = re.sub(r'\s+', ' ', text)                # multiple whitespace
    text = re.sub(r'([a-zA-Z0-9"\'])[.]([a-zA-Z]{2,})', r'\1. \2', text) # sentences with no <period> <whitespace>
                                                                         # does not match acronyms like U.S.
    text = text.strip()
    if not text.endswith('.'):
        text += '.'
    text = unidecode(text)
    return text


def contains_object(sentence, title, gender, synonyms):
    s = sentence.lower()
    title = title.lower()

    if re.search(r'\b%s\b' % title, s) or re.search(r'\b%s\'s\b' % title, s):
        return True

    synonyms = [syn.lower() for syn in synonyms]
    for syn in synonyms:
        if re.search(r'\b%s\b' % re.escape(syn), s) or re.search(r'\b%s\'s\b' % re.escape(syn), s):
            return True

    if gender == 'masculine':
        if re.search(r'\bhe\b', s) or re.search(r'\bhis\b', s) or re.search(r'\bhim\b', s):
            return True

    if gender == 'femenine':
        if re.search(r'\bshe\b', s) or re.search(r'\bher\b', s) or re.search(r'\bhers\b', s):
            return True

    if gender == 'neuter':
        if sentence.startswith('It '):
            return True

    return False


def get(paragraphs, title, gender, synonyms):
    """Gets valid sentences from paragraphs."""
    paragraphs = filter(lambda p: validate(p), paragraphs)
    paragraphs = [normalize(p) for p in paragraphs]

    text = " ".join(paragraphs)
    sentences = sent_tokenize(text)
    sentences = filter(lambda s: s.find('=') == -1, sentences)
    sentences = filter(lambda s: contains_object(s, title, gender, synonyms), sentences)

    return sentences


def get_gender(paragraphs):
    text = " ".join(paragraphs).lower()

    masculine = len(re.findall(r'\bhe\b', text)) + len(re.findall(r'\bhis\b', text)) + len(re.findall(r'\bhim\b', text))
    femenine = len(re.findall(r'\bshe\b', text)) + len(re.findall(r'\bher\b', text)) + len(re.findall(r'\bhers\b', text))
    neuter = len(re.findall(r'\bit\b', text)) + len(re.findall(r'\bits\b', text))

    if neuter > masculine and neuter > femenine:
        return 'neuter'
    elif masculine >= femenine:
        return 'masculine'
    else:
        return 'femenine'
