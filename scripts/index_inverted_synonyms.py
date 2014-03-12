from pymongo import MongoClient
import json

"""
Given the wikipedia-term synonyms file produced by WikipediaBase,
produces an inverted index of synonyms in JSON format for use
by WikiKB
"""

f = open('wikipedia-term-generated-synonyms')
outf = open('wiki-inverted-synonyms.json', 'w')

client = MongoClient('localhost', 27017)
db = client.wiki

counter = 0
index = {}

for l in f:
    counter += 1
    if counter % 10000 == 0:
        print "Progress: %s" % counter

    try:
        title, synonym = l.strip().split("\t")
    except:
        continue

    if title not in index:
        index[title] = {'synonyms': set([])}
        article = db.wikipedia.find_one({'title': title},
                                        {'wikiTitle': 1, '_id': 0})
        if article:
            wikiTitle = article['wikiTitle']
            index[title]['wikiTitle'] = wikiTitle
        else:
            index[title]['wikiTitle'] = None

    index[title]['synonyms'].add(synonym)

for title in index:
    wikiTitle = index[title]['wikiTitle']
    synonyms = index[title]['synonyms']

    for syn in synonyms:
        o = {'synonym': syn,
             'wikiTitle': wikiTitle,
             'title': title
             }
        outf.write(json.dumps(o) + "\n")
