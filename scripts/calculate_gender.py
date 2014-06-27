from pymongo import MongoClient
from wikiscout import sentence

"""
Augments articles with a gender attribute, calculated based on the most
popular pronoun
"""

client = MongoClient('localhost', 27017)
db = client.wiki

def main():
    i = 0
    for article in db.wikipedia.find({}, fields={'_id': 1, 'paragraphs': 1}, timeout=False):
        try:
            if i % 100 == 0:
                print 'Progress: %s' % i

            if 'paragraphs' in article:
                gender = sentence.get_gender(article['paragraphs'])
                db.wikipedia.update({'_id': article['_id']}, 
                                          {'$set': {'gender': gender}})
            i += 1
        except Exception as e:
            print article['title'], e
            continue


if __name__ == "__main__":
        main()
