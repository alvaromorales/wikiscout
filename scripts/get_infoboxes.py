from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client.wiki

def main():
    outf = open('infoboxes.txt', 'w')

    i = 0
    for article in db.wikipedia.find({}, fields={'classes':1}, timeout=False):
        i += 1
        try:
            if i % 100 == 0:
                print 'Progress: %s' % i

            if 'classes' in article:
                for c in article['classes']:
                    outf.write('%s\n' % c)

        except Exception:
            pass

    outf.close()

if __name__ == "__main__":
        main()
