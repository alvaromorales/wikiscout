from pymongo import MongoClient
import infobox


def _connect(host='localhost'):
    """Returns a client and db connection to a MongoDB host with WikiKB
    data."""
    client = MongoClient(host, 27017)
    db = client.wiki
    return (client, db)


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


def get_synonym_title(synonym):
    """Gets an article's title given a synonym.

    Args:
      synonym (str): A synonym of the article's title.
    """
    client, db = _connect()
    title = db.inverted_synonyms.find_one({'synonym': synonym})
    if title is not None:
        return title['title']
    return None
