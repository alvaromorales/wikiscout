import logging
import json
from tools.annotation import Annotation
from tools.start import START
from tools import schemata
from tools import infobox

class Scout:
    def __init__(self,attributes_file,candidates_file,output_file):
        self.attributes = self.load_attributes(attributes_file)
        self.candidates_file = candidates_file
        self.outf = open(output_file,'w')
        self.start = START('nauru.csail.mit.edu')
    
    def load_attributes(self,attributes_file):
        f = open(attributes_file)
        attributes = {}

        for l in f:
            template_attrs = json.loads(l)
            template = template_attrs['template']
            for d in template_attrs['attributes']:
                attribute = d['attribute']
                raw = d['raw']
                attributes[(template,attribute)] = raw
                
        return attributes

    def eval_candidate(self,template,attribute,sentence,value,wiki_title,index):
        try:
            annotation = Annotation(sentence,wiki_title,template,value).get()
        except Exception as e:
            logging.error('Could not generate annotation for "%s". Exception:\n%s'%(sentence,e))
            return None

        if annotation is None:
            return
        
        try:
            parseable = self.start.parseable(annotation)
        except Exception as e:
            logging.error('START parse error:\n%s'%e)
            return None
        
        if parseable:
            if (template,attribute) not in self.attributes:
                logging.warn('No raw attributes for attribute "%s" of template "%s"'%(attribute,template))
                raw_attributes = [attribute]
            else:
                raw_attributes = self.attributes[(template,attribute)]
            
            wiki_class = infobox.normalize_class(template)
            schema = schemata.generate(annotation,index,wiki_class,raw_attributes)
            
            return schema
    
    def run(self):
        f = open(self.candidates_file)
        index = 0
        total = 0
        
        for l in f:
            template_candidates = json.loads(l)
            template = template_candidates['infobox_type']
            
            for attribute in template_candidates['attributes']:
                candidates = template_candidates['attributes'][attribute]
                for candidate in candidates:
                    sentence = candidate['sentence']
                    value = candidate['value']
                    wiki_title = candidate['wikiTitle']
                    
                    total += 1
                    schema = self.eval_candidate(template,attribute,sentence,value,wiki_title,index)
                    if schema is not None:
                        self.outf.write(schema)
                        index += 1
        return index,total
