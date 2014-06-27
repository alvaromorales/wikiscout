import re
from wikipediabase import WikipediaBase
from wikidump import WikiDump
from omnibase import Omnibase

### Convert text into annotations

class Annotation:
    def __init__(self,sentence,wiki_title,template,value,highlights=[]):
        self.sentence = sentence
        self.wiki_title = wiki_title
        self.symbol = self.generate_symbol(template)
        self.template = template
        self.value = value
        
        self.wb = WikipediaBase(host='nauru.csail.mit.edu')
        self.ob = Omnibase(host='nauru.csail.mit.edu')
        self.wdump = WikiDump(host='nauru.csail.mit.edu')
        
        self.get_article_data()

        self.highlights.extend(highlights)
        self.highlights = sorted(self.highlights,key=len,reverse=True)        
        self.annotation = None

    def get_article_data(self):
        join_article = self.wdump.get_wiki_title(self.wiki_title,lang='join')
        
        if join_article is not None:
            self.highlights = join_article['en']['highlights']
            self.highlights.extend(join_article['simple']['highlights'])
            
            self.title = join_article['en']['title'].decode('utf8').encode('ascii')
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
        self.ob_symbols = self.ob.get_known(self.sentence,omnibase_class='wikipedia-term')
            
    @staticmethod
    def generate_symbol(s):
        if s.find(' ') != -1:
            # spaces are invalid
            return
        
        if re.match(r'^infobox_',s,flags=re.IGNORECASE):
            symbol = re.sub(r'^infobox_','any-wikipedia-',s,flags=re.IGNORECASE)
            symbol = symbol.lower().replace('_','-')
            return symbol

        if re.match(r'^wikipedia-',s,flags=re.IGNORECASE):
            symbol = re.sub(r'^wikipedia-','any-wikipedia-',s,flags=re.IGNORECASE)
            symbol = symbol.lower().replace('_','-')
            return symbol
    
    def sub_title(self):
        # possesive
        if re.match(r'\b%s\'s\b'%self.title,self.sentence,flags=re.IGNORECASE):
            return re.sub(r'\b%s\'s\b'%self.title,'%s\'s'%self.symbol,self.sentence,flags=re.IGNORECASE)
        
        # subjective
        if re.match(r'\b%s\b'%self.title,self.sentence,flags=re.IGNORECASE):
            return re.sub(r'\b%s\b'%self.title,'%s'%self.symbol,self.sentence,flags=re.IGNORECASE)

    def sub_pronoun(self):
        # possesive
        if re.match(r'^(?:His|Her|Its)\b',self.sentence):
            return re.sub(r'^(?:His|Her|Its)\b','%s\'s'%self.symbol,self.sentence)
        
        # subjective
        if re.match(r'^(?:He|She|It|They)\b',self.sentence):
            return re.sub(r'^(?:He|She|It|They)\b',self.symbol,self.sentence)
        
    def sub_highlights(self):
        for h in self.highlights:
            if re.match(r'\b%s(?:\'s)?\b'%h,self.sentence):
                return re.sub(r'\b%s'%h,self.symbol,self.sentence,count=1)

    @staticmethod
    def get_class(classes):
        ignore = set(['wikipedia-term','wikipedia-paragraphs','wikipedia-paragraph','wikipedia-person'])
        common = set(['wikipedia-person'])

        classes = list(set(classes))

        if len(classes) <= 1:
            return classes[0]

        if set(classes) == set(['wikipedia-term', 'wikipedia-paragraphs']):
            return 'wikipedia-term'

        classes = filter(lambda c: c not in ignore,classes)
        if len(classes) == 0:
            print "No classes left after 'ignore' filter"
            raise

        if len(classes) == 1:
            return classes[0]

        classes = filter(lambda c: c not in common,classes)
        if len(classes) == 1:
            return classes[0]

        base = re.sub(r'^any-wikipedia-','',self.symbol)
        for c in classes:
            if re.sub(r'^wikipedia-','',c) == base:
                return c
        
        print "No classes left after 'common' filter"
        raise

    def sub_wb_subject(self):
        # try to find symbols with the same title
        title_matches = sorted([symbol for symbol in self.ob_symbols if symbol['symbol'] == self.title],key= lambda symbol: symbol['span'][1] - symbol['span'][0],reverse=True)
        
        if len(title_matches) > 0:
            print len(title_matches)

            longest = title_matches[0]
            match = longest['match']
            
            # possesive
            if re.match(r'\b%s\'s\b'%match,self.sentence):
                return re.sub(r'\b%s\'s\b'%match,'%s\'s'%self.symbol,self.sentence)
            # subjective
            if re.match(r'\b%s\b'%match,self.sentence):
                return re.sub(r'\b%s\b'%match,'%s'%self.symbol,self.sentence)
            
        else:
            # try to find an omnibase symbol with the same class as the title
            c = self.get_class(self.wb_classes)

            print "Reached else clause in WB subject"
            raise

            if c is None:
                return

            for o in self.ob_symbols:
                break
    
    def annotate_sentence(self):
        annotation = self.annotation
        subject = self.annotation
        
