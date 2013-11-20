import sys
import re
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from collections import Counter
from tools import infobox

class MRTopAttributes(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol       

    def mapper(self, key, article):
        if 'infobox' not in article:
            return

        infobox_template = infobox.normalize_template(article['infobox']['name'])
        description = article['infobox']['description']
            
        if infobox_template != '' and infobox.validate_template(infobox_template) and description != []:
            i = infobox.parse(infobox_template,description)
            
            if i is None:
                return
            
            attributes = [infobox.normalize_attribute(a) for a in infobox.get_attributes(i) if infobox.validate_attribute(a)]
            
            for a in attributes:
                yield infobox_template, (a,1)
                
    def reducer(self, infobox_template, attribute_counts):
        attributes = {}
        
        for (a,count) in attribute_counts:
            if a in attributes:
                attributes[a] += count
            else:
                attributes[a] = count

        total = sum(attributes.itervalues())
        t = int(total*0.05)
        
        top_attributes = [a for a in attributes if attributes[a] >= t]
        
        if len(top_attributes) > 0:
            yield None, {'template': infobox_template, 'attributes': top_attributes}

if __name__ == '__main__':
        MRTopAttributes.run()
