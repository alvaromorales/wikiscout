import logging
import wikikb
from tokenize import tokenize

logger = logging.getLogger(__name__)

# Annotation Generation methods


def replace_title(title, symbol, tokenization):
    title_possesive = title + '\'s'
    ok = False

    for i, token in enumerate(tokenization.tokens):
        if token.value == title:
            tokenization.tokens[i] = tokenization.replace_token(token, symbol)
            ok = True
        elif token.value == title_possesive:
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
        tokenization.tokens[0] = tokenization.replace_token(token, symbol + '\'s')
        return True

    return False


def replace_synonyms(object, symbol, tokenization):
    synonyms = wikikb.get_synonyms(object)
    if synonyms is None:
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
