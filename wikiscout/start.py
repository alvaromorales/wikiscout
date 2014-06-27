import requests
import xmltodict


class STARTParseResponseException(Exception):
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

    r = requests.get('http://start.csail.mit.edu/askstart.cgi',
                     params=params)

    try:
        response = xmltodict.parse(r.text)
    except:
        raise STARTParseResponseException('Could not parse: %s' % r.text)

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
