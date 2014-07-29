import re
import mwparserfromhell
from dewiki.parser import Parser as DewikiParser
from unidecode import unidecode

ignore_attributes = set(['NAME', 'BIRTH-NAME', 'CAPTION', 'COMMON-NAME', 'WEBSITE', 'NATIVE-NAME'])


class InfoboxParseException(Exception):
    pass


class Infobox:
    def __init__(self, infobox):
        self.attributes = {}
        wiki_class = get_class(infobox['name'])
        description = infobox['description']

        infobox_contents = ''.join(['|', '|'.join(description)])
        infobox_text = ''.join(['{{', wiki_class, infobox_contents, '}}'])
        parsed = mwparserfromhell.parse(infobox_text)

        templates = parsed.filter_templates()

        if len(templates) > 0:
            self.name = wiki_class
            parsed_infobox = templates[0]
            self.build_infobox(parsed_infobox)
        else:
            raise InfoboxParseException()

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value

    def __delitem__(self, key):
        del self.attributes[key]

    def __iter__(self):
        return self.attributes.__iter__()

    def __str__(self):
        return "Infobox(name=%s, attributes=%s)" % (self.name, self.attributes)

    def build_infobox(self, parsed_infobox):
        for p in parsed_infobox.params:
            attribute = normalize_attribute(p.name)
            value = parse_value(p.value.strip())

            if validate_attribute(attribute) and validate_value(value):
                if attribute in self.attributes:
                    self.attributes[attribute].extend(value)
                else:
                    self.__setitem__(attribute, value)

        return None


def get_class(template):
    """Returns a wikipedia class given an infobox template."""
    wiki_class = template.lower().strip()

    if ':' in wiki_class:
        wiki_class = wiki_class.split(':')[0]

    wiki_class = re.sub(r'\([^\)]*\)', '', wiki_class).strip()

    wiki_class = re.sub(r'\n+', '', wiki_class)
    wiki_class = re.sub('_+', '-', wiki_class)
    wiki_class = re.sub('[ ]+', '-', wiki_class)
    wiki_class = re.sub('-+$', '', wiki_class)
    wiki_class = re.sub('\.', '', wiki_class)
    wiki_class = re.sub(r'^infobox-', 'wikipedia-', wiki_class)

    return wiki_class


def validate_class(wiki_class):
    """Checks that a Wikipedia class is valid."""
    return re.match('^wikipedia-[a-z-]+$', wiki_class) is not None


def normalize_attribute(attribute, allow_suffix=False):
    """Normalizes an attribute.

    Args:
      attribute (str): The name of the attribute.
      allow_suffix (bool): Set to True to keep integer suffixes. Defaults to False.
    """
    a = attribute.strip().upper()
    a = re.sub(r'_+', '-', a)
    a = re.sub(r'\n+', '', a)
    a = re.sub(r'[ ]+', '-', a)

    if not allow_suffix and not a.isdigit():
        a = re.sub(r'-*[0-9]+$', '', a)

    return a


def validate_attribute(attribute):
    """Checks if an attribute is valid."""
    valid = attribute not in ignore_attributes
    valid = valid and not attribute.isdigit()
    valid = valid and attribute != ''
    valid = valid and re.match('^[A-Z0-9-/]+$', attribute) is not None
    return valid


def validate_value(value):
    """Checks if a value is valid."""
    if len(value) == 0:
        return False

    for v in value:
        if v is None or v.isdigit() or len(v) <= 1 or v == '(TEMPLATE)':
            return False
    return True


def parse_value(value):
    value = unidecode(unicode(DewikiParser().parse_string(value).strip()))

    value = re.sub(r'\(TEMPLATE\)', '', value)
    value = re.sub(r'<ref>[^<]+?</ref>', '', value)
    value = re.sub(r'<ref name=[^/]+/>', '', value)
    value = re.sub(r'<ref name=[^>]+></ref>', '', value)
    value = re.sub(r'<ref>[^<]*</ref>', '', value)
    value = re.sub(r'<small>[^<]+?</small>', '', value)
    value = re.sub(r'\([^\)]*\)', '', value)

    value = re.split('<br ?/?>', value)
    value = [v.strip() for v in value]
    return value
