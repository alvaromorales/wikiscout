import re
import mwparserfromhell
from dewiki.parser import Parser as DewikiParser
from unidecode import unidecode


class InfoboxParseException(Exception):
    pass


def get_class(template):
    """Returns a wikipedia class given an infobox template."""
    wiki_class = template.lower().strip()
    wiki_class = re.sub(r'\n+', '', wiki_class)
    wiki_class = re.sub('_+', '-', wiki_class)
    wiki_class = re.sub('[ ]+', '-', wiki_class)
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
    ignore_attributes = set(['NAME', 'CAPTION', 'COMMON-NAME'])

    valid = attribute not in ignore_attributes
    valid = valid and not attribute.isdigit()
    valid = valid and attribute != ''
    valid = valid and re.match('^[A-Z0-9-/]+$', attribute) is not None
    return valid


def validate_value(value):
    """Checks if a value is valid."""
    return value is not None and not value.isdigit() and len(value) > 1 and value != '(TEMPLATE)'


class Infobox:
    def __init__(self, infobox):
        wiki_class = get_class(infobox['name'])
        description = infobox['description']

        infobox_contents = ''.join(['|', '|'.join(description)])
        infobox_text = ''.join(['{{', wiki_class, infobox_contents, '}}'])

        infobox = mwparserfromhell.parse(infobox_text)
        templates = infobox.filter_templates()
        self.wiki_class = wiki_class

        if len(templates) > 0:
            self.infobox = templates[0]
            self.name = wiki_class
        else:
            raise InfoboxParseException()

    @property
    def attributes(self):
        return self.get_attributes()

    def get_attributes(self, raw=False, only_valid=True):
        """Get infobox attributes.

        Args:
          raw (bool): Set to True to get a list of (normalized,raw) attribute tuples. Defaults to False.
          only_valid (bool): Set to True to exclude invalid attributes. Defaults to True.
        """
        if raw:
            normalized = [(normalize_attribute(a.name), a.name.strip()) for a in self.infobox.params]
            if only_valid:
                return filter(lambda (norm, raw): validate_attribute(norm), normalized)
            return normalized
        else:
            normalized = [normalize_attribute(a.name) for a in self.infobox.params]
            if only_valid:
                return filter(lambda a: validate_attribute(a), normalized)
            return normalized

    def get_all_attributes(self):
        normalized = [normalize_attribute(a.name, allow_suffix=True) for a in self.infobox.params]
        return normalized

    @property
    def items(self):
        items = {}
        for p in self.infobox.params:
            attribute = normalize_attribute(p.name)
            value = unidecode(unicode(DewikiParser().parse_string(p.value.strip()).strip()))

            if validate_attribute(attribute) and validate_value(value):
                items[attribute] = value
        return items

    def get(self, attribute):
        return self.items()[attribute]
