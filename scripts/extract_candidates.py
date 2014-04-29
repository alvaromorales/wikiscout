from collections import namedtuple
from pymongo import MongoClient
from wikiscout import sentence
from wikiscout.infobox_parser import Infobox
from unidecode import unidecode

client = MongoClient('localhost', 27017)
db = client.wiki

Candidate = namedtuple('Candidate', ['cls', 'attribute', 'sentence', 'title', 'value'])


def main():
    f = open('sentences.tsv', 'w')
    i = 0
    for simple_article in db.simplewikipedia.find({}, fields={'_id': 0, 'title': 1, 'paragraphs': 1, 'infoboxes': 1, 'sentences': 1}, timeout=False):
        try:
            if i % 100 == 0:
                print 'Progress: %s' % i
            candidates = process_article(simple_article)
            if candidates:
                write_candidates(candidates, f)
            i += 1
        except Exception as e:
            print e
            continue

    f.close()


def write_candidates(candidates, f):
    for c in candidates:
        str = "\t".join([c.cls, c.attribute, c.sentence, c.title, c.value])
        str = unidecode(unicode(str)).encode('utf8', 'ignore')
        f.write('%s\n' % str)
        f.flush()


def process_article(simple_article):
    if 'sentences' not in simple_article:
        return None

    article_sentences = simple_article['sentences']
    if len(article_sentences) == 0:
        return None

    title = simple_article['title']
    en_article = db.wikipedia.find_one({'title': title}, fields={'_id': 0, 'title': 1, 'paragraphs': 1, 'infoboxes': 1})

    if en_article is None:
        return None

    if 'infoboxes' not in en_article:
        return None

    if len(en_article['infoboxes']) == 0:
        return None

    sentences = set()
    for raw_infobox in en_article['infoboxes']:
        infobox = Infobox(raw_infobox)
        candidates = process_infobox(infobox, title, article_sentences)
        for s in candidates:
            sentences.add(s)

    return sentences


def process_infobox(infobox, title, article_sentences):
    candidates = []
    cls = infobox.name
    for attribute in infobox:
        if ignore_attribute(attribute):
            continue

        for s in article_sentences:
            for value in infobox[attribute]:
                if sentence.contains(s, [value]):
                    c = Candidate(cls, attribute, s, title, value)
                    candidates.append(c)
    return candidates


def ignore_attribute(a):
    a = a.lower()
    if a.find('name') != -1:
        return True
    if a.find('demonym') != -1:
        return True
    return False


if __name__ == "__main__":
        main()
