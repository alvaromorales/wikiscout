import re
from pymongo import MongoClient
import logging
import infobox
import omnibase
import wikipediabase

logger = logging.getLogger(__name__)


def _connect(host='localhost'):
    """Returns a client and db connection to a MongoDB host with WikiKB
    data."""
    client = MongoClient(host, 27017)
    db = client.wiki
    return (client, db)


def get_article(title, fields=None, lang='en'):
    """Gets an article.

    Args:
      title (str): The title of the article.
      fields (dict): A dictionary of which fields to include.
      lang (str): The language of the article. Defaults to 'en'.
    """
    client, db = _connect()

    if fields:
        fields['_id'] = 0
        fields['redirect'] = 1

    if lang == 'en':
        if fields:
            article = db.wikipedia.find_one({'title': title}, fields=fields)
        else:
            article = db.wikipedia.find_one({'title': title})
    elif lang == 'simple':
        if fields:
            article = db.simplewikipedia.find_one({'title': title},
                                                  fields=fields)
        else:
            article = db.simplewikipedia.find_one({'title': title})
    else:
        return None

    while article is not None and 'redirect' in article:
        if fields:
            article = db.wikipedia.find_one({'wikiTitle': article['redirect']},
                                            fields=fields)
        else:
            article = db.wikipedia.find_one({'wikiTitle': article['redirect']})

    return article


def get_infoboxes(title, lang='en'):
    """Gets infoboxes in an article.

    Args:
      title (str): The title of the article.
      lang (str): The language of the article. Defaults to 'en'.
    """
    fields = {'infoboxes': 1}
    article = get_article(title, fields=fields, lang=lang)

    if article is None or 'infoboxes' not in article:
        return None

    infoboxes = [infobox.Infobox(i) for i in article['infoboxes']]
    return infoboxes


def get(cls, title, attribute):
    """Gets the value of an infobox attribute.

    Args:
      cls (str): The WikipediaBase class.
      title (str): The title of the article.
      attribute (str): The infobox attribute.
    """
    article_infoboxes = get_infoboxes(title)
    for article_infobox in article_infoboxes:
        if article_infobox and article_infobox.name == cls:
            items = article_infobox.items
            if attribute in items:
                return items[attribute]
    return None


def get_attributes(cls, title):
    """Gets the attributes in an article's infobox.

    Args:
      cls (str): The WikipediaBase class.
      title (str): The title of the article.
    """
    article_infoboxes = get_infoboxes(title)

    for article_infobox in article_infoboxes:
        if article_infobox and article_infobox.name == cls:
            return article_infobox.get_all_attributes()
    return []


def get_class(title):
    """Gets the WikipediaBase class of an article.
       If an article contains multiple infoboxes,
       its wikipedia class is the class of the infobox
       with the most number of attributes.

    Args:
      title (str): The article title.
    """
    article = get_article(title)

    if article:
        article_infoboxes = get_infoboxes(title)
        if article_infoboxes and len(article_infoboxes) > 0:
            i = sorted(article_infoboxes,
                       key=lambda i: len(i.attributes),
                       reverse=True)[0]
            return i.name
    return None


def get_all_classes(title):
    """Gets all the classes of an article.

    Args:
      title (str): The article title.
    """
    article = get_article(title, fields={'classes': 1})
    if article:
        return article['classes']
    return None


def get_synonyms(title):
    """Gets an article's synonyms.

    Args:
      title (str): The article title.
    """
    client, db = _connect()
    synonyms = db.synonyms.find_one({'title': title})

    if synonyms is not None:
        # TODO remove external calls
        synonyms = synonyms['synonyms']
        classes = wikipediabase.get_classes(title, host='tonga')
        if classes and 'wikipedia-person' in classes:
            synonyms.extend(omnibase.get('nobel-person', title, 'SYNONYMS', host='tonga'))
        return synonyms
    return None


def pick_best_link(matching_links, article_links):
    def clean_id(id):
        if id is None:
            return None
        return re.match(r'^(.+?)(?:#.*)?$', id.lower()).group(1)

    for i, matching_link in enumerate(matching_links):
        for article_link in article_links:
            if i == 0:
                default = matching_link['title']

            if clean_id(article_link['id']) == clean_id(matching_link['wikiTitle']):
                title = matching_link['title']
                logger.debug('Picked "%s" as best link' % title)
                return title

    logger.debug('Could not pick best link. Returned first: "%s"' % default)
    return default


def get_synonym_title(synonym, object):
    """Gets an article's title given a synonym.

    Args:
      synonym (str): A synonym of the article's title.
    """
    client, db = _connect()
    matching_links = db.inverted_synonyms.find({'synonym': synonym})
    article_links = get_article(object, fields={'links': 1})['links']
    if matching_links.count() != 0:
        if matching_links.count() == 1:
            return matching_links[0]['title']

        return pick_best_link(matching_links, article_links)

    return None
