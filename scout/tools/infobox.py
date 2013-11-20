import mwparserfromhell
import re

# Parses an infobox from the json-wikipedia dump
def parse(infobox_template,description):
    infobox_contents = ''.join(['|','|'.join(description)])
    infobox_text = ''.join(['{{',infobox_template.lower(),'\n',infobox_contents,'\n}}'])

    infobox = mwparserfromhell.parse(infobox_text)
    
    templates = infobox.filter_templates()
    if len(templates) > 0:
        if len(templates) > 1:
            raise
        return templates[0]
    
# Returns a list of infobox attributes
def get_attributes(infobox):
    return [p.name.strip() for p in infobox.params]

### Templates

def normalize_template(template):
    t = template.lower().strip()
    t = t.replace('__','_')
    return t

def validate_template(template):
    return re.match('^[a-z_]+$',template) is not None
    
### Attributes

def normalize_attribute(attribute):
    a = attribute.lower().strip()
    a = a.replace('__','_')
    a = re.sub('_*[0-9]+$','',a)
    return a

def validate_attribute(attribute):
    return not attribute.isdigit()
