import sys
import re
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from collections import Counter

from wikiscout import infobox

class MRTopAttributes(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol       

    def mapper(self, key, article):
        if 'infobox' not in article:
            return

        infobox_template = infobox.normalize_template(article['infobox']['name'])
        description = article['infobox']['description']
            
        if infobox_template != '' and infobox.validate_template(infobox_template) and description != []:
            article_infobox = infobox.parse(infobox_template,description)
            
            if article_infobox is None:
                return
            
            attributes = infobox.get_attributes(article_infobox,raw=True)
            
            for (a,raw) in attributes:
                yield infobox_template, (a,raw,1)
                
    def reducer(self, infobox_template, attribute_counts):
        attributes = {}
        
        for (a,raw,count) in attribute_counts:
            if a in attributes:
                attributes[a]['count'] += count
                attributes[a]['raw'].add(raw)
            else:
                attributes[a] = { 'count': count, 'raw' : set([raw]) }

        total = sum([attributes[a]['count'] for a in attributes])
        t = int(total*0.05)
        
        top_attributes = [{'attribute': a, 'raw': list(attributes[a]['raw'])} for a in attributes if attributes[a]['count'] >= t]
        
        if len(top_attributes) > 0:
            yield None, {'template': infobox_template, 'attributes': top_attributes}

if __name__ == '__main__':
        MRTopAttributes.run()
