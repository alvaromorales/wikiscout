import mwparserfromhell
from dewiki.parser import Parser as DewikiParser
import re

### Ignore

ignore_attributes = set(['name','caption'])


### Templates

def normalize_template(template):
    t = template.lower().strip()
    t = re.sub('_+','_',t)
    return t

def validate_template(template):
    return re.match('^[a-z_]+$',template) is not None
    
### Attributes

def normalize_attribute(attribute):
    a = attribute.lower().strip()
    a = re.sub('_+','_',a)
    if a.isdigit():
        return a
    a = re.sub('_*[0-9]+$','',a)
    return a

def validate_attribute(attribute):
    return not attribute.isdigit() and attribute != ''

### Values

def validate_value(value):
    # ignore dates?
    return not value.isdigit() and len(value) > 1 and value != '(TEMPLATE)'

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
    
# Returns a list of all valid, normalized infobox attributes
def get_attributes(infobox):
    normalized = [normalize_attribute(a.name) for a in infobox.params]
    return filter(lambda a: validate_attribute(a),normalized)

# Returns a list of all normalized attributes
def get_all_attributes(infobox):
    return [normalize_attribute(a.name) for a in infobox.params]

def get_items(infobox):
    items = []
    for p in infobox.params:
        attribute = normalize_attribute(p.name)
        value = DewikiParser().parse_string(p.value.strip())
        if validate_attribute(attribute) and value != '':
            items.append((attribute,value))
    return items
