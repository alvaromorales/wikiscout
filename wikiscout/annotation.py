import re
import logging
import wikikb
import tokenize
from nltk.corpus import stopwords
from unidecode import unidecode

logger = logging.getLogger(__name__)


class ObjectNotFoundException(Exception):
    pass


class ObjectSymbolNotFoundException(Exception):
    pass


# Annotation Generation methods

def replace_title(title, symbol, tokenization):
    title_possessive = title + '\'s'
    ok = False

    for i, token in enumerate(tokenization.tokens):
        if token.value == title:
            tokenization.tokens[i] = tokenization.replace_token(token, symbol)
            ok = True
        elif token.value == title_possessive:
            tokenization.tokens[i] = tokenization.replace_token(token,
                                                                symbol + '\'s')
            ok = True

    return ok


def replace_pronoun(object, symbol, tokenization):
    token = tokenization.tokens[0]

    if token.value in ['He', 'She', 'It', 'They']:
        tokenization.tokens[0] = tokenization.replace_token(token, symbol)
        return True

    if token.value in ['His', 'Her', 'Its', 'Their']:
        tokenization.tokens[0] = tokenization.replace_token(token,
                                                            symbol + '\'s')
        return True

    return False


def replace_synonyms(object, symbol, tokenization):
    synonyms = wikikb.get_synonyms(object)

    if len(synonyms) == 0:
        return False

    ok = False
    for i, token in enumerate(tokenization.tokens):
        for s in synonyms:
            if token.value == s:
                tokenization.tokens[i] = tokenization.replace_token(token,
                                                                    symbol)
                ok = True
            elif token.value == s + '\'s':
                tokenization.tokens[i] = tokenization.replace_token(
                    token, '%s\'s' % symbol)
                ok = True

    return ok


def replace_object(object, symbol, tokenization):
    ok = replace_title(object, symbol, tokenization)
    for f in [replace_pronoun, replace_synonyms]:
        if ok:
            break
        ok = f(object, symbol, tokenization)

    return ok


def replace_proper_nouns(object, tokenization):
    ok = False
    for i, t in enumerate(tokenization.tokens):
        if not t.value[0].isupper() or t.value.lower() in \
                stopwords.words('english'):
            continue

        possessive = re.search(r'(.*?)\'s$', t.value)
        if possessive:
            noun = possessive.group(1)
            cls = wikikb.get_class(noun)
            if cls:
                tokenization.tokens[i] = tokenization.replace_token(
                    t, 'any-%s\'s' % cls)
                ok = True
            else:
                title = wikikb.get_synonym_title(noun, object)
                if title:
                    cls = wikikb.get_class(title)
                    if cls:
                        tokenization.tokens[i] = tokenization.replace_token(
                            t, 'any-%s\'s' % cls)
                        ok = True
                    else:
                        logging.debug('Could not find a matching symbol for %s' % t)
                else:
                    logging.debug('Could not find a matching symbol for %s' % t)
        else:
            cls = wikikb.get_class(t.value)
            if cls:
                tokenization.tokens[i] = tokenization.replace_token(
                    t, 'any-%s' % cls)
                ok = True
            else:
                title = wikikb.get_synonym_title(t.value, object)
                if title:
                    cls = wikikb.get_class(title)
                    if cls:
                        tokenization.tokens[i] = tokenization.replace_token(
                            t, 'any-%s' % cls)
                        ok = True
                    else:
                        logging.debug('Could not find a matching symbol for %s' % t)
                else:
                    logging.debug('Could not find a matching symbol for %s' % t)

    return ok


def annotate(sentence, object):
    sentence = unidecode(unicode(sentence))
    object = unidecode(unicode(object))

    cls = wikikb.get_class(object)
    if not cls:
        raise ObjectSymbolNotFoundException(
            "Could not generate a matching symbol for object \"%s\"" % object)

    symbol = 'any-%s' % cls
    tokenization = tokenize.tokenize(sentence)[0]
    logger.info('Tokenized as %s' % [t.value for t in tokenization.tokens])

    if replace_object(object, symbol, tokenization):
        replace_proper_nouns(object, tokenization)
        return tokenization
    else:
        raise ObjectNotFoundException("Could not find object \"%s\" in \"%s\""
                                      % (object, sentence))
