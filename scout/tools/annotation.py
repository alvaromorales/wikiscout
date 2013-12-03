import re
from wikipediabase import WikipediaBase
from wikidump import WikiDump
from omnibase import Omnibase
from corenlp import CoreNLP
from nltk.corpus import stopwords
import logging

### Convert text into annotations

class Annotation:
    def __init__(self,sentence,wiki_title,template,value,highlights=[]):
        self.sentence = sentence
        self.wiki_title = wiki_title
        self.symbol = self.generate_symbol(template)
        self.template = template
        self.value = value

        self.stopwords = set(stopwords.words('english'))
        
        self.wb = WikipediaBase(host='nauru.csail.mit.edu')
        self.ob = Omnibase(host='nauru.csail.mit.edu')
        self.wdump = WikiDump(host='nauru.csail.mit.edu')
        self.corenlp = CoreNLP()
        
        self.get_article_data()

        self.highlights.extend(highlights)
        self.highlights = sorted(filter(lambda h: h != '',self.highlights),key=len,reverse=True)
        
        self.annotation = None

    def get_article_data(self):
        join_article = self.wdump.get_wiki_title(self.wiki_title,lang='join')
        
        if join_article is not None:
            self.highlights = join_article['en']['highlights']
            self.highlights.extend(join_article['simple']['highlights'])
            
            self.title = join_article['en']['title'].decode('utf8').encode('ascii','ignore')
            self.links = join_article['en']['links']
            self.links.extend(join_article['simple']['links'])
            
        else:
            en_article = self.wdump.get_wiki_title(self.wiki_title)
            
            if en_article is None:
                raise ValueError('Could not find an article with wiki_title : %s'%self.wiki_title)
            
            self.highlights = en_article['highlights']
            self.title = en_article['title'].decode('utf8').encode('ascii')
            self.links = en_article['links']

        self.wb_classes = self.wb.get_classes(self.title)
        self.ob_symbols = self.filter_symbols(self.ob.get_known(self.sentence,omnibase_class='wikipedia-term'))
        
    @staticmethod
    def generate_symbol(s):
        if s.find(' ') != -1:
            # spaces are invalid
            return
        
        if re.search(r'^infobox_',s,flags=re.IGNORECASE):
            symbol = re.sub(r'^infobox_','any-wikipedia-',s,flags=re.IGNORECASE)
            symbol = symbol.lower().replace('_','-')
            return symbol

        if re.search(r'^wikipedia-',s,flags=re.IGNORECASE):
            symbol = re.sub(r'^wikipedia-','any-wikipedia-',s,flags=re.IGNORECASE)
            symbol = symbol.lower().replace('_','-')
            return symbol
    
    def filter_symbols(self,symbols):
        return filter(lambda s: s['match'].lower() not in self.stopwords,symbols)

    def sub_title(self):
        # possesive
        if re.search(r'\b%s\'s\b'%re.escape(self.title),self.sentence,flags=re.IGNORECASE):
            return re.sub(r'\b%s\'s\b'%re.escape(self.title),'%s\'s'%self.symbol,self.sentence,flags=re.IGNORECASE)
        
        # subjective
        if re.search(r'\b%s\b'%re.escape(self.title),self.sentence,flags=re.IGNORECASE):
            return re.sub(r'\b%s\b'%re.escape(self.title),'%s'%self.symbol,self.sentence,flags=re.IGNORECASE)

    def sub_pronoun(self):
        # possesive
        if re.search(r'^(?:His|Her|Its|Their)\b',self.sentence):
            return re.sub(r'^(?:His|Her|Its|Their)\b','%s\'s'%self.symbol,self.sentence)
        
        # subjective
        if re.search(r'^(?:He|She|It|They)\b',self.sentence):
            return re.sub(r'^(?:He|She|It|They)\b',self.symbol,self.sentence)
        
    def sub_highlights(self):
        for h in self.highlights:
            if re.search(r'\b%s(?:\'s)?\b'%re.escape(h),self.sentence):
                return re.sub(r'\b%s'%re.escape(h),self.symbol,self.sentence,count=1)

    @staticmethod
    def get_class(classes):
        ignore = set(['wikipedia-term','wikipedia-paragraphs','wikipedia-paragraph'])
        common = set(['wikipedia-person'])
        
        classes = list(set(classes))
        
        if len(classes) == 0:
            return None

        if len(classes) == 1:
            return classes[0]

        if set(classes) == set(['wikipedia-term', 'wikipedia-paragraphs']):
            return 'wikipedia-term'

        classes = filter(lambda c: c not in ignore,classes)
        if len(classes) == 0:
            raise Exception("No classes left after 'ignore' filter")

        if len(classes) == 1:
            return classes[0]

        classes = filter(lambda c: c not in common,classes)
        # shortest matching symbol?
        classes = sorted(classes,key=len)
        
        if len(classes) > 0:
            print classes
            return classes[0]
        
        #base = re.sub(r'^any-wikipedia-','',symbol)
        #for c in classes:
        #    if re.sub(r'^wikipedia-','',c) == base:
        #        return c
        
        raise Exception("No classes left after 'common' filter")

    def sub_wb_subject(self):
        # try to find symbols with the same title
        title_matches = sorted([symbol for symbol in self.ob_symbols if symbol['symbol'] == self.title],key= lambda symbol: symbol['span'][1] - symbol['span'][0],reverse=True)
        
        if len(title_matches) > 0:
            longest = title_matches[0]
            match = longest['match']
            
            # possesive
            if re.search(r'\b%s\'s\b'%re.escape(match),self.sentence):
                return re.sub(r'\b%s\'s\b'%re.escape(match),'%s\'s'%self.symbol,self.sentence)
            # subjective
            if re.search(r'\b%s\b'%re.escape(match),self.sentence):
                return re.sub(r'\b%s\b'%re.escape(match),'%s'%self.symbol,self.sentence)
            
        # special case: infobox-person
        if 'wikipedia-person' in self.wb_classes:
            synonyms = filter(lambda s: s is not None and s != '', self.ob.get('nobel-person',self.title,'SYNONYMS'))
            
            for syn in synonyms:
                # possesive
                if re.search(r'\b%s\'s\b'%re.escape(syn),self.sentence):
                    return re.sub(r'\b%s\'s\b'%re.escape(syn),'%s\'s'%self.symbol,self.sentence)

                # subjective
                if re.search(r'\b%s\b'%re.escape(syn),self.sentence):
                    return re.sub(r'\b%s\b'%re.escape(syn),'%s'%self.symbol,self.sentence)

        # try to find an omnibase symbol with the same class as the title
        c = self.get_class(self.wb_classes)
        print "FIND SUBJECT FROM CLASSES: %s"%c

    # assumes annotation contains substring value
    def replace_value(self,annotation,value,wiki_title,prefer_wikibase=True):
        title_template = self.wdump.get_title_template(wiki_title)
        
        if title_template is None:
            return

        title,template = title_template

        if template is not None and not prefer_wikibase:
            return annotation.replace(value,self.generate_symbol(template))
        else:
            c = self.get_class(self.wb.get_classes(title))
            if c is None:
                print "Could not find a matching symbol for \"%s\" (wikiTitle: %s). Using wikipedia-term"%(value,wiki_title)
                return annotation.replace(value,'any-wikipedia-term')
            else:
                symbol = self.generate_symbol(c)
                return annotation.replace(value,symbol)
    
    def sub_links(self):
        annotation = self.annotation

        for l in self.links:
            wiki_title = l['id']
            value = l['description']
                        
            if len(value) == 0 or value == '' or wiki_title == '' or wiki_title is None:
                continue
            
            if annotation.find(value) != -1:
                annotation = self.replace_value(annotation,value,wiki_title)

        self.annotation = annotation

    def sub_subject(self):
        for f in [self.sub_title,self.sub_pronoun,self.sub_highlights,self.sub_wb_subject]:
            annotation = f()
            
            if annotation is not None:
                return annotation

        raise Exception("Could not find subject %s in the annotation."%self.title)

    def sub_value(self):
        # attempt to lookup and replace value
        value_symbols = self.ob.get_known(self.value,omnibase_class='wikipedia-term')
        value_matches = sorted([symbol for symbol in value_symbols if symbol['symbol'] == self.value],key= lambda symbol: symbol['span'][1] - symbol['span'][0],reverse=True)
        
        if len(value_matches) > 0:
            longest = value_matches[0]
            symbol = longest['symbol']
            
            article = self.wdump.get_title(symbol)
            if article is not None:
                wiki_title = article['wikiTitle']
                annotation = self.replace_value(self.annotation,self.value,wiki_title)
                if annotation is not None:
                    self.annotation = annotation
                    return
        
        print "Could not substitute value = \"%s\". Used wikipedia-term."%(self.value)
        self.annotation = self.annotation.replace(self.value,'any-wikipedia-term')

    def sub_ner(self):
        annotation = self.annotation
        annotation = self.corenlp.ner(annotation)
        self.annotation = annotation

    def normalize(self):
        annotation = self.annotation

        annotation = re.sub(r'\(.*?\)','',annotation)
        annotation = re.sub(r'\s+',' ',annotation)

        self.annotation = annotation

    def get(self):
        # subject substitution
        try:
            annotation = self.sub_subject()
        except Exception as e:
            print e
            return None
        
        if annotation is None:
            raise Exception("Could not find a subject in: \"%s\"."%self.sentence)
        self.annotation = annotation
        
        self.sub_value()
        self.sub_links()

        self.normalize()
        self.sub_ner()
        
        self.normalize()
        return self.annotation
