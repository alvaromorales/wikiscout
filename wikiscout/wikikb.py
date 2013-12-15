import re
import mwparserfromhell
import logging
from dewiki.parser import Parser as DewikiParser
from pymongo import MongoClient

class Infobox:
    def __init__(self,infobox):
        infobox_template = self.get_cls(infobox['name'])
        description = infobox['description']
        
        infobox_contents = ''.join(['|','|'.join(description)])
        infobox_text = ''.join(['{{',infobox_template,infobox_contents,'}}'])

        infobox = mwparserfromhell.parse(infobox_text)
        templates = infobox.filter_templates()
        if len(templates) > 0:
            self.infobox = templates[0]
            self.name = self.infobox.name
        else:
            raise Exception('Could not generate Infobox')

        self.dw = DewikiParser()

    @staticmethod
    def get_cls(template):
        cls = template.lower().strip()
        cls = re.sub(r'\n+','',cls)
        cls = re.sub('_+','-',cls)
        cls = re.sub('[ ]+','-',cls)
        cls = re.sub(r'^infobox-','wikipedia-',cls)
        return cls

    @staticmethod
    def normalize_attribute(attribute):
        a = attribute.strip().upper()
        a = re.sub('_+','-',a)
        a = re.sub(r'\n+','',a)
        a = re.sub('[ ]+','-',a)
        return a

    @staticmethod
    def validate_attribute(attribute):
        return re.match('^[A-Z0-9-]+$',attribute) is not None

    @staticmethod
    def validate_value(value):
        return value is not None and value != '' and value != '(TEMPLATE)'

    def get_attributes(self):
        attributes = [self.normalize_attribute(a.name) for a in self.infobox.params]
        return filter(lambda a: self.validate_attribute(a),attributes)

    def get_items(self):
        items = {}
        for p in self.infobox.params:
            attribute = self.normalize_attribute(p.name)
            value = self.dw.parse_string(p.value.strip())
            if self.validate_attribute(attribute) and self.validate_value(value):
                items[attribute] = value
        return items
        
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
            infobox = self.get_infobox(article)
            if infobox is not None and infobox.name == wiki_class:
                items = infobox.get_items()
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
            infobox_template = Infobox.get_cls(article['infobox']['name'])
            description = article['infobox']['description']
            
            if infobox_template != '' and description != []:
                infobox = Infobox(article['infobox'])
                return infobox
        except Exception as e:
            logging.exception(e)
            return None

    def get_attributes(self,wiki_class,title):
        try:
            article = self.get_article(title)
            infobox = self.get_infobox(article)
            if infobox is not None and infobox.name == wiki_class:
                attributes = infobox.get_attributes()
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
                wiki_class = Infobox.get_cls(infobox_template)
                wiki_classes.append(wiki_class)
                return wiki_classes
            
            return wiki_classes
