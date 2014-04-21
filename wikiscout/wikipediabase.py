import re
import telnetlib


class WikipediaBaseConnectionException(Exception):
    pass


class WikipediaBaseParseException(Exception):
    pass


class WikipediaBaseException(Exception):
    pass


def _connect(host='localhost'):
    try:
        conn = telnetlib.Telnet(host, 8023)
        return conn
    except:
        raise WikipediaBaseConnectionException(
            'Could not connect to WikipediaBase host %s' % host)


def get_classes(symbol, host='localhost'):
    symbol = unidecode(unicode(symbol)).encode('ascii', 'ignore')
    conn = _connect(host)
    conn.write('(get-classes "%s")\n' % symbol)
    response = conn.read_all()
    conn.close()

    try:
        parsed_response = _parse_get_classes_response(response)
    except:
        raise WikipediaBaseConnectionException(
            'WikipediaBase could not parse: %s' % symbol)

    return parsed_response


def _parse_get_classes_response(response):
    if response.strip() == '#f':
        return []

    response = re.sub(r'<!---.*?\"', '\"', response)
    response = re.sub(r'\n', '', response)

    return map(lambda c: eval(c), response.strip()[1:-1].split(' '))
