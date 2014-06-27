from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.wiki

def main():
    outf = open('simpleinfoboxes.txt', 'w')
    simplef = open('simple_en_infoboxes.txt', 'w')

    i = 0
    for simple_article in db.simplewikipedia.find({}, fields={'classes':1, 'wikiTitle':1}, timeout=False):
        i += 1
        try:
            if i % 100 == 0:
                print 'Progress: %s' % i

            if 'classes' in simple_article and len(simple_article['classes']) > 0:
                for c in simple_article['classes']:
                    outf.write('%s\n' % c)

            article = db.wikipedia.find_one({'wikiTitle': simple_article['wikiTitle']}, fields={'classes':1})
            if article is None:
                continue

            if 'classes' in article:
                for c in article['classes']:
                    simplef.write('%s\n' % c)

        except Exception as e:
            print e
            pass

    outf.close()

if __name__ == "__main__":
        main()
