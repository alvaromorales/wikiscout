from py2neo import neo4j
from pymongo import MongoClient
import logging
import infobox

logger = logging.getLogger(__name__)

py2neo_log = logging.getLogger('py2neo')
py2neo_log.setLevel(logging.WARNING)


def _connect(host='localhost'):
    """Returns a client and db connection to a MongoDB host with WikiKB
    data."""
    client = MongoClient(host, 27017)
    db = client.wiki
    return (client, db)


def _connect_wikigraph():
    return neo4j.GraphDatabaseService()


def get_article(title, lang='en'):
    """Gets an article.

    Args:
      title (str): The title of the article.
      lang (str): The language of the article. Defaults to 'en'
    """
    client, db = _connect()

    if lang == 'en':
        article = db.wikipedia.find_one({'title': title})
    elif lang == 'simple':
        article = db.simplewikipedia.find_one({'title': title})
    else:
        return None

    while article is not None and 'redirect' in article:
        article = db.wikipedia.find_one({'title': article['redirect']})

    return article


def get_infobox(title, lang='en'):
    """Gets an article's infobox.

    Args:
      title (str): The title of the article.
      lang (str): The language of the article. Defaults to 'en'.
    """
    article = get_article(title, lang)

    if article is None or 'infobox' not in article:
        return None

    article_infobox = infobox.Infobox(article['infobox'])
    return article_infobox


def get(cls, title, attribute):
    """Gets the value of an infobox attribute.

    Args:
      cls (str): The WikipediaBase class.
      title (str): The title of the article.
      attribute (str): The infobox attribute.
    """
    article_infobox = get_infobox(title)
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
    article_infobox = get_infobox(title)
    if article_infobox and article_infobox.name == cls:
        return article_infobox.get_all_attributes()
    return []


def get_class(title):
    """Gets the WikipediaBase class of an article.

    Args:
      title (str): The article title.
    """
    article = get_article(title)

    if article:
        article_infobox = get_infobox(title)
        if article_infobox:
            return article_infobox.name
    return None


def get_synonyms(title):
    """Gets an article's synonyms.

    Args:
      title (str): The article title.
    """
    client, db = _connect()
    synonyms = db.synonyms.find_one({'title': title})
    if synonyms is not None:
        return synonyms['synonyms']
    return None


def shortest_path_length(t1, t2):
    graph_db = _connect_wikigraph()

    query_string = """MATCH (p0:Page {title:'%s'}), (p1:Page {title:'%s'}),
                        p = shortestPath((p0)-[*..6]-(p1))
                      RETURN p""" % (t1, t2)

    result = neo4j.CypherQuery(graph_db, query_string).execute()
    path_lengths = [len(r.p) for r in result]
    if len(path_lengths) > 0:
        return min(path_lengths)
    else:
        return float('inf')


def pick_best_link(links, object):
    spaths = []
    for l in links:
        spaths.append((l['title'], shortest_path_length(object, l['title'])))

    link = min(spaths, key=lambda x: x[1])[0]
    logger.debug("Picked %s out of %s" % (link, spaths))
    return link


def get_synonym_title(synonym, object):
    """Gets an article's title given a synonym.

    Args:
      synonym (str): A synonym of the article's title.
    """
    client, db = _connect()
    titles = db.inverted_synonyms.find({'synonym': synonym})
    if titles.count() != 0:
        if titles.count() == 1:
            return titles[0]['title']

        return pick_best_link(titles, object)

    return None
