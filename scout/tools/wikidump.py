import re
from pymongo import MongoClient
import infobox

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

    def get_wiki_title(self,wiki_title,lang='en',ignorecase=False):
        if ignorecase:
            wiki_title = re.compile(wiki_title,re.IGNORECASE)

        if lang == 'en':
            return self.wikipedia.find_one({'wikiTitle':wiki_title})
        elif lang == 'simple':
            return self.simplewikipedia.find_one({'wikiTitle':wiki_title})
        elif lang == 'join':
            return self.joined_wikipedia.find_one({'wikiTitle':wiki_title})

    def get_title_template(self,wiki_title,lang='en'):
        article = self.get_wiki_title(wiki_title,lang=lang)

        if article is None:
            article = self.get_wiki_title(wiki_title,lang=lang,ignorecase=True)
        
        if article is not None:
            title = article['title'].decode('utf8').encode('ascii','ignore')
            template = None
            if 'infobox' in article:
                template = infobox.normalize_template(article['infobox']['name']).decode('utf8').encode('ascii','ignore')
            return (title,template)
        
