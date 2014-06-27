from collections import namedtuple
from pymongo import MongoClient
from wikiscout import infobox, sentence, wikikb

client = MongoClient('localhost', 27017)
db = client.wiki

Candidate = namedtuple('Candidate', ['cls', 'attribute', 'sentence', 'title', 'value'])


def main():
    f = open('sentences.tsv', 'w')
    i = 0
    for simple_article in db.simplewikipedia.find({}, fields={'_id': 0, 'title': 1, 'paragraphs': 1, 'infoboxes': 1}):
        try:
            if i % 1000 == 0:
                print 'Progress: %s' % i
            candidates = process_article(simple_article)
            if candidates:
                write_candidates(candidates, f)
            i += 1
        except Exception as e:
            continue

    f.close()


def write_candidates(candidates, f):
    for c in candidates:
        f.write('%s\n' % "\t".join([c.cls, c.attribute, c.sentence, c.title, c.value]))


def process_article(simple_article):
    title = simple_article['title']
    en_article = db.wikipedia.find_one({'title': title}, fields={'_id': 0, 'title': 1, 'paragraphs': 1, 'infoboxes': 1})

    if en_article is None:
        return None

    if len(en_article['infoboxes']) == 0:
        return None

    article_sentences = get_sentences(simple_article['paragraphs'])

    sentences = set()
    for raw_infobox in en_article['infoboxes']:
        ibox = infobox.Infobox(raw_infobox)
        candidates = process_infobox(ibox, title, article_sentences)
        for s in candidates:
            sentences.add(s)

    return sentences


def process_infobox(infobox, title, article_sentences):
    candidates = []
    cls = infobox.wiki_class
    for attribute, value in infobox.items.items():
        if ignore_attribute(attribute):
            continue

        values = set([value])
        for v in wikikb.get_synonyms(value):
            values.add(v)

        for s in article_sentences:
            if sentence.contains(s, values):
                c = Candidate(cls, attribute, s, title, value)
                candidates.append(c)
    return candidates


def ignore_attribute(a):
    if a.lower().find('name') != -1:
        return True
    if a.lower().find('demonym') != -1:
        return True
    return False


def get_sentences(paragraphs):
    return sentence.get(paragraphs)

if __name__ == "__main__":
        main()
