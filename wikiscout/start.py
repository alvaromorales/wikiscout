import logging
import requests
import xmltodict

requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)

class STARTParseResponseException(Exception):
    pass


class STARTServerException(Exception):
    pass


def send_request(query, action, machine='malta.csail.mit.edu', server='guest'):
    params = {'query': query,
              'referrer': 'http://start.csail.mit/wikiscout',
              'server': server,
              'machine': machine,
              'action': action,
              'qe': 'HTML',
              'kb': 'no',
              'te': 'XML',
              'de': 'no',
              'fg': 'yes'
              }

    r = requests.post('http://start.csail.mit.edu/askstart.cgi',
                     data=params)

    if '<h1>Internal Server Error</h1>' in r.text:
        raise STARTServerException(r.text)

    try:
        response = xmltodict.parse(r.text)
    except:
        raise STARTParseResponseException('Could not parse START response.\nAction=%s, Query= "%s".\nResponse: %s' % (action, query, r.text[:250]))

    return response


def parse(sentence, machine='malta.csail.mit.edu', server='guest'):
    response = send_request(sentence, 'parse', machine=machine, server=server)
    return response


def parseable(self, sentence):
    return self.parse(sentence) is not None


def tokenize(sentence, machine='malta.csail.mit.edu', server='guest'):
    response = send_request(sentence, 'tokenize', machine=machine,
                            server=server)
    return response
