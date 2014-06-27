from pymongo import MongoClient

class WikiDump:
    def __init__(self,host='localhost'):
        self.client = MongoClient(host, 27017)
        self.db = self.client.wiki
        
        self.wikipedia = self.db.wikipedia
        self.simplewikipedia = self.db.simplewikipedia
        self.joined_wikipedia = self.db.join

    def get_title(self,title,lang='en'):
        if lang == 'en':
            return self.wikipedia.find_one({'title':title})
        elif lang == 'simple':
            return self.simplewikipedia.find_one({'title':title})

    def get_wiki_title(self,wiki_title,lang='en'):
        if lang == 'en':
            return self.wikipedia.find_one({'wikiTitle':wiki_title})
        elif lang == 'simple':
            return self.simplewikipedia.find_one({'wikiTitle':wiki_title})
        elif lang == 'join':
            return self.joined_wikipedia.find_one({'wikiTitle':wiki_title})
