from unidecode import unidecode
import json

f = open('wikipedia-dump.json', 'r')
w = open('wikipedia-dump-processed.json', 'w')

for l in f:
    o = json.loads(l)
    if 'title' in o:
        o['title'] = unidecode(unicode(o['title']))

    w.write(json.dumps(o) + "\n")
