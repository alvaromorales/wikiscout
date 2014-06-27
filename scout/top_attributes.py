import sys
import re
from mrjob.protocol import JSONValueProtocol
from mrjob.job import MRJob
from collections import Counter
from tools.infobox import parse_infobox, get_infobox_attributes

# import mwparserfromhell

# # Parses an infobox from the wikipedia dump
# def parse_infobox(infobox_template,description):
#     infobox_contents = ''.join(['|','|'.join(description)])
#     infobox_text = ''.join(['{{',infobox_template.lower(),'\n',infobox_contents,'\n}}'])

#     infobox = mwparserfromhell.parse(infobox_text)
    
#     templates = infobox.filter_templates()
#     if len(templates) > 0:
#         if len(templates) > 1:
#             raise
#         return templates[0]
    
# Returns a list of infobox attributes
def get_infobox_attributes(infobox):
    return [p.name.rstrip() for p in infobox.params]

class MRTopAttributes(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    OUTPUT_PROTOCOL = JSONValueProtocol       

    def validate_attribute(self,a):
        return not a.isdigit()

    def validate_template(self,t):
        return re.match('^[a-z_]+$',t) != None
    
    def mapper(self, key, article):
        if 'infobox' in article:
            infobox_template = article['infobox']['name'].lower()
            description = article['infobox']['description']
            
            if infobox_template != '' and self.validate_template(infobox_template) and description != []:
                infobox = parse_infobox(infobox_template,description)
            
                if infobox != None:
                    attributes = get_infobox_attributes(infobox)
                    
                    for a in attributes:
                        if self.validate_attribute(a):
                            yield infobox_template, (a.lower(),1)
                    
    def reducer(self, infobox_template, attribute_counts):
        attributes = {}
        
        for (a,count) in attribute_counts:
            if a in attributes:
                attributes[a] += count
            else:
                attributes[a] = count

        total = sum(attributes.itervalues())
        t = int(total*0.15)
        
        top_attributes = [a for a in attributes if attributes[a] >= t]
        
        if len(top_attributes) > 0:
            yield None, {'template': infobox_template, 'attributes': top_attributes}

if __name__ == '__main__':
        MRTopAttributes.run()
