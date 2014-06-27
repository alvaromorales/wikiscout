import re
import mwparserfromhell
import logging
from dewiki.parser import Parser as DewikiParser
from pymongo import MongoClient
import infobox

class WikiKB:
    def __init__(self,host='localhost'):
        self.client = MongoClient(host, 27017)
        self.db = self.client.wiki        
        self.wikipedia = self.db.wikipedia

    def get_article(self,title):
        article = self.wikipedia.find_one({'title':title})
        
        if article is None:
            return None
        
        while article is not None and 'redirect' in article:
            article = self.wikipedia.find_one({'title': article['redirect']})
        
        return article

    def get(self,wiki_class,title,attribute):
        try:
            article = self.wikipedia.find_one({'title':title})
            article_infobox = self.get_infobox(article)
            if article_infobox is not None and article_infobox.name == wiki_class:
                items = article_infobox.items
                if attribute in items:
                    value = items[attribute]
                    return value
                return None
        except Exception as e:
            logging.exception(e)
            return None

    def get_infobox(self,article):
        if article is None or 'infobox' not in article:
            return None
        try:
            infobox_template = infobox.get_class(article['infobox']['name'])
            description = article['infobox']['description']
            
            if infobox_template != '' and description != []:
                article_infobox = infobox.Infobox(article['infobox'])
                return article_infobox
        except Exception as e:
            logging.exception(e)
            return None

    def get_attributes(self,wiki_class,title):
        try:
            article = self.get_article(title)
            article_infobox = self.get_infobox(article)
            if article_infobox is not None and article_infobox.name == wiki_class:
                attributes = article_infobox.get_all_attributes()
                return attributes
            else:
                return []
        except Exception as e:
            logging.exception(e)
            return []

    def get_classes(self,title):
        article = self.get_article(title)

        if article is None:
            return []
        else:
            wiki_classes = ['wikipedia-term','wikipedia-paragraphs']
            if 'infobox' not in article:
                return wiki_classes

            infobox_template = article['infobox']['name']

            if infobox_template is not None and infobox_template != '':
                wiki_class = infobox.get_class(infobox_template)
                wiki_classes.append(wiki_class)
                return wiki_classes
            
            return wiki_classes
