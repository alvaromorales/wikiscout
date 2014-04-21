from pymongo import MongoClient
from wikiscout import wikikb, sentence

client = MongoClient('localhost', 27017)
db = client.wiki

def main():
    i = 0
    for simple_article in db.simplewikipedia.find({}, fields={'_id': 1, 'title': 1, 'paragraphs': 1}, timeout=False):
        try:
            if i % 100 == 0:
                print 'Progress: %s' % i
            
            if 'paragraphs' in simple_article:
                title = simple_article['title']
                paragraphs = simple_article['paragraphs']
                gender = wikikb.get_gender(title)
                synonyms = wikikb.get_synonyms(title)
                sentences = sentence.get(paragraphs, title, gender, synonyms)
                db.simplewikipedia.update({'_id': simple_article['_id']}, 
                                          {'$set': {'sentences': sentences}})
            i += 1
        except Exception as e:
            print simple_article['title'], e


if __name__ == "__main__":
        main()
