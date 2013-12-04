import re
import logging
from wikipediabase import WikipediaBase
from wikidump import WikiDump
from omnibase import Omnibase
from corenlp import CoreNLP
from nltk.corpus import stopwords

### Convert text into annotations

class Annotation:
    def __init__(self,sentence,wiki_title,template,value,highlights=[]):
        logging.info('Creating Annotation instance for sentence: %s'%sentence)
        self.sentence = sentence.decode('unicode-escape').encode('ascii','ignore')

        self.wiki_title = wiki_title

        self.template = template
        self.value = value.decode('unicode-escape').encode('ascii','ignore')

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
            
            self.title = join_article['en']['title'].decode('utf-8').encode('ascii','ignore')
            self.links = join_article['en']['links']
            self.links.extend(join_article['simple']['links'])
            
        else:
            logging.info('Using en_article for %s'%self.wiki_title)
            en_article = self.wdump.get_wiki_title(self.wiki_title)
            
            if en_article is None:
                raise ValueError('Could not find an article with wiki_title : %s'%self.wiki_title)
            
            self.highlights = en_article['highlights']
            self.title = en_article['title'].decode('utf-8').encode('ascii')
            self.links = en_article['links']

        self.wb_classes = self.wb.get_classes(self.title)
        self.symbol = self.generate_symbol(self.get_class(self.wb_classes))
        self.ob_symbols = self.filter_symbols(self.ob.get_known(self.sentence,omnibase_class='wikipedia-term'))
        
    @staticmethod
    def generate_symbol(s):
        if s.find(' ') != -1:
            logging.info('Found spaces in generate_symbol for symbol "%s"'%s)
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
            annotation = re.sub(r'\b%s\'s\b'%re.escape(self.title),'%s\'s'%self.symbol,self.sentence,flags=re.IGNORECASE)

            logging.info('Found possesive title subject: %s.'%self.title)
            logging.debug('sub_title: %s'%annotation)
            return annotation
        
        # subjective
        if re.search(r'\b%s\b'%re.escape(self.title),self.sentence,flags=re.IGNORECASE):
            annotation = re.sub(r'\b%s\b'%re.escape(self.title),'%s'%self.symbol,self.sentence,flags=re.IGNORECASE)

            logging.info('Found title subject: %s.'%self.title)
            logging.debug('sub_title: %s'%annotation)
            return annotation

    def sub_pronoun(self):
        # possesive
        if re.search(r'^(?:His|Her|Its|Their)\b',self.sentence):
            annotation = re.sub(r'^(?:His|Her|Its|Their)\b','%s\'s'%self.symbol,self.sentence)

            logging.info('Found possesive pronoun subject.')
            logging.debug('sub_pronoun: %s'%annotation)
            return annotation
        
        # subjective
        if re.search(r'^(?:He|She|It|They)\b',self.sentence):
            annotation = re.sub(r'^(?:He|She|It|They)\b',self.symbol,self.sentence)
            
            logging.info('Found pronoun subject.')
            logging.debug('sub_pronoun: %s'%annotation)
            return annotation
        
    def find_subsumed(self,span,value):
        start,end = span
        subsumed = value

        for symbol in self.ob_symbols:
            symbol_start, symbol_end = symbol['span']
            if start >= symbol_start and end <= symbol_end and (end-start) < (symbol_start - symbol_end):
                if len(symbol['symbol']) > len(subsumed):
                    subsumed = symbol['symbol']

        if len(subsumed) != len(value):
            logging.info('find_subsumed: Replaced %s %s with %s'%(value,span,subsumed))
        return subsumed

    def sub_highlights(self):
        for h in self.highlights:
            match = re.search(r'\b%s(?:\'s)?\b'%re.escape(h),self.sentence)
            if match:
                span = match.span()
                h = self.find_subsumed(span,h)
                annotation = re.sub(r'\b%s'%re.escape(h),self.symbol,self.sentence,count=1)

                logging.info('Found highlight subject: %s'%h)
                logging.debug('sub_highlights: %s'%annotation)
                return annotation
    
    @staticmethod
    def get_class(classes):
        logging.debug('get_class called with %s'%str(classes))
        
        ignore = set(['wikipedia-term','wikipedia-paragraphs','wikipedia-paragraph','wikipedia-stack'])
        common = set(['wikipedia-person'])
        
        classes = list(set(classes))
        
        if len(classes) == 0:
            logging.info('get_class received an empty classes list')
            return None

        if len(classes) == 1:
            logging.debug('get_class: %s'%classes[0])
            return classes[0]

        if set(classes) == set(['wikipedia-term', 'wikipedia-paragraphs']):
            logging.debug('get_class: wikipedia-term')
            return 'wikipedia-term'

        classes = filter(lambda c: c not in ignore,classes)
        if len(classes) == 0:
            raise Exception("No classes left after 'ignore' filter")

        if len(classes) == 1:
            logging.debug('get_class: %s'%classes[0])
            return classes[0]

        classes = filter(lambda c: c not in common,classes)
        # shortest matching symbol?
        classes = sorted(classes,key=len)
        
        if len(classes) > 0:
            logging.debug('get_class: picked %s from %s.'%(classes[0],classes))
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
                annotation = re.sub(r'\b%s\'s\b'%re.escape(match),'%s\'s'%self.symbol,self.sentence)
                
                logging.info('Found possesive WB subject from title_matches: %s.'%match)
                logging.debug('sub_wb_subject: %s.'%annotation)
                return annotation

            # subjective
            if re.search(r'\b%s\b'%re.escape(match),self.sentence):
                annotation = re.sub(r'\b%s\b'%re.escape(match),'%s'%self.symbol,self.sentence)

                logging.info('Found WB subject from title_matches: %s.'%match)
                logging.debug('sub_wb_subject: %s.'%annotation)
                return annotation
            
        # special case: infobox-person
        if 'wikipedia-person' in self.wb_classes:
            synonyms = filter(lambda s: s is not None and s != '', self.ob.get('nobel-person',self.title,'SYNONYMS'))
            
            for syn in synonyms:
                # possesive
                if re.search(r'\b%s\'s\b'%re.escape(syn),self.sentence):
                    annotation = re.sub(r'\b%s\'s\b'%re.escape(syn),'%s\'s'%self.symbol,self.sentence)

                    logging.info('Found possesive WB subject from wikipedia-person synonyms: %s.'%syn)
                    logging.debug('sub_wb_subject: %s'%annotation)
                    return annotation

                # subjective
                if re.search(r'\b%s\b'%re.escape(syn),self.sentence):
                    annotation = re.sub(r'\b%s\b'%re.escape(syn),'%s'%self.symbol,self.sentence)
                    
                    logging.info('Found WB subject from wikipedia-person synonyms: %s.'%syn)
                    logging.debug('sub_wb_subject: %s'%annotation)
                    return annotation

        # try to find an omnibase symbol with the same class as the title
        c = self.get_class(self.wb_classes)
        logging.info('TODO: reached end of sub_wb_subject')
        print "FIND SUBJECT FROM CLASSES: %s"%c

    # assumes annotation contains substring value
    def replace_value(self,annotation,value,wiki_title,prefer_wikibase=True):
        title_template = self.wdump.get_title_template(wiki_title)
        
        if title_template is None:
            return

        title,template = title_template

        if template is not None and not prefer_wikibase:
            symbol = self.generate_symbol(template)
            result = annotation.replace(value,symbol)
            
            logging.info('Replaced value "%s" with infobox template symbol "%s".'%(value,symbol))
            logging.debug('replace_value: %s'%result)
            return result
        else:
            c = self.get_class(self.wb.get_classes(title))
            if c is None:
                result = annotation.replace(value,'any-wikipedia-term')

                logging.info("Could not find a matching symbol for \"%s\" (wikiTitle: %s). Using wikipedia-term"%(value,wiki_title))
                logging.debug('replace_value: %s'%result)
                return result
            else:
                symbol = self.generate_symbol(c)
                result = annotation.replace(value,symbol)

                logging.info('Replaced value "%s" with WikipediaBase class "%s"'%(value,symbol))
                logging.debug('replace_value: %s'%result)
                return result

        logging.debug('Could not replace value "%s"'%value)
    
    def sub_links(self):
        logging.debug('In sub_links')
        annotation = self.annotation

        for l in self.links:
            wiki_title = l['id']
            value = l['description']
                        
            if len(value) == 0 or value == '' or wiki_title == '' or wiki_title is None:
                continue

            if annotation.find(value) != -1:

                # only care about proper nouns
                if not value[0].isupper():
                    logging.info('Skipping link "%s" because it is not a proper noun.'%value)
                    continue

                match = re.search(r'\b(%s)\b'%re.escape(value),self.sentence)
                if match:
                    span = match.span()
                    value = self.find_subsumed(span,value)
                    
                logging.debug('Found link: %s'%value)

                result = self.replace_value(annotation,value,wiki_title)
                if result is not None:
                    annotation = result
                    logging.debug('%s'%annotation)

        logging.debug('sub_links: %s'%annotation)
        self.annotation = annotation

    def sub_subject(self):
        for f in [self.sub_title,self.sub_pronoun,self.sub_highlights,self.sub_wb_subject]:
            logging.info('sub_subject trying: %s'%f.__name__)
            annotation = f()
            
            if annotation is not None:
                return annotation

        raise Exception("Could not find subject %s in the annotation."%self.title)

    def sub_value(self):
        logging.debug('In sub_value')
        # attempt to lookup and replace value
        #value_symbols = self.ob.get_known(self.value,omnibase_class='wikipedia-term')
        value_symbols = filter(lambda symbol: symbol['match'].find(self.value) != -1, self.ob_symbols)
        value_matches = sorted([symbol for symbol in value_symbols if self.value == symbol['symbol']],key= lambda symbol: symbol['span'][1] - symbol['span'][0],reverse=True)

        if len(value_matches) > 0:
            longest = value_matches[0]
            symbol = longest['symbol']
            match = longest['match']
            
            if match != self.value:
                logging.info('sub_value: replaced subsumed "%s" with "%s"'%(self.value,match))

            article = self.wdump.get_title(symbol)
            if article is not None:
                wiki_title = article['wikiTitle']
                annotation = self.replace_value(self.annotation,match,wiki_title)
                if annotation is not None:
                    logging.debug('sub_value: %s'%annotation)
                    self.annotation = annotation
                    return
        
        self.annotation = self.annotation.replace(self.value,'any-wikipedia-term')
        logging.info('Could not substitute attribite value "%s". Used wikipedia-term.'%(self.value))
        logging.debug('sub_value: %s'%self.annotation)

    def sub_ner(self):
        annotation = self.annotation
        annotation = self.corenlp.ner(annotation)
        self.annotation = annotation
        logging.debug('sub_ner: %s'%self.annotation)

    def normalize(self):
        annotation = self.annotation

        annotation = re.sub(r'\(.*?\)','',annotation)
        annotation = re.sub(r'\s+',' ',annotation)

        self.annotation = annotation
        logging.debug('normalize: %s'%self.annotation)

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
