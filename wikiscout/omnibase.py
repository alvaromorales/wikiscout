import json
import re
from pyparsing import OneOrMore, nestedExpr
import telnetlib


class OmnibaseConnectionException(Exception):
    pass


class OmnibaseParseException(Exception):
    pass


class OmnibaseException(Exception):
    pass


def _connect(host='localhost'):
    try:
        conn = telnetlib.Telnet(host, 8008)
        return conn
    except:
        raise OmnibaseConnectionException('Could not connect to Omnibase host %s' % host)


def get(cls, symbol, attribute, host='localhost'):
    conn = _connect(host)
    conn.write('(get "%s" "%s"  "%s")\n' % (cls, symbol, attribute.upper()))
    response = conn.read_until('\n').strip()
    conn.close()
    response = re.sub(r'\n', '', response)

    if response == '#f':
        return None

    return list(eval(response.replace('" "', '","')))


def get_symbols(s, cls=None, host='localhost'):
    conn = _connect(host)
    s = json.dumps(s)

    if cls:
        conn.write('(get-symbols %s \':class "%s")\n' % (s, cls))
    else:
        print "writing : (get-symbols %s)\n" % s
        conn.write('(get-symbols %s)\n' % s)

    response = conn.read_until('\n').strip()
    conn.close()

    parsed_response = _parse_get_symbols_response(response)
    return parsed_response


def get_known(s, cls=None, host='localhost'):
    conn = _connect(host)
    s = json.dumps(s)

    if cls:
        conn.write('(get-known %s \':class "%s")\n' % (s, cls))
    else:
        conn.write('(get-known %s)\n' % s)

    response = conn.read_until('\n').strip()
    conn.close()

    parsed_response = _parse_get_symbols_response(response)
    return parsed_response


def _parse_get_symbols_response(response):
    if response[:2] == '()':
        return None

    # some responses are HUGE ... we truncate them
    if len(response) > 0 and response[-2:] != "))":
        last_occurence = response.rfind(':priority 0)')
        response = response[:last_occurence + len(':priority 0)')] + ")"

    parsed_response = []

    try:
        data = OneOrMore(nestedExpr()).parseString(response)
    except:
        raise OmnibaseParseException("Could not parse %s" % response)

    if data[0][0] == "error":
        print response
        raise Exception()

    for d in data[0]:
        r = {}
        r['class'] = d[0]
        r['match'] = d[1].replace('"', '')
        r['span'] = (int(d[3][0]), int(d[3][1]))
        r['symbol'] = d[5].replace('"', '')
        parsed_response.append(r)
    return parsed_response
