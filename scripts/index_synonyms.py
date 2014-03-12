import json

"""
Given the wikipedia-term synonyms file produced by WikipediaBase,
produces a JSON formatted synonyms list for use by WikiKB
"""

f = open('wikipedia-term-generated-synonyms')
outf = open('wiki-synonyms.json', 'w')

index = {}
for l in f:
    try:
        title, synonym = l.strip().split("\t")
    except:
        continue
    if title not in index:
        index[title] = []

    index[title].append(synonym)

for title in index:
    o = {'title': title,
         'synonyms': index[title]
         }
    outf.write(json.dumps(o) + "\n")
