import telnetlib
import xmltodict
import socket
import re
import json

_servers = {
    'guest': 8001,
    'ailab': 8002,
}


class STARTConnectionException(Exception):
    pass


def _connect(host='localhost', server='guest'):
    port = _servers[server]
    try:
        telnet = telnetlib.Telnet(host, port)
        remote_address = socket.gethostbyname(socket.gethostname())
        return (telnet, remote_address)
    except:
        raise STARTConnectionException("Could not connect to START host %s" % host)


def _format_request(query, action, remote_address, kb='yes', machine='malta.csail.mit.edu', server='guest'):
    request = '(:REMOTE-ADDRESS "%s" :VB "normal" :QUERY %s :USER_AGENT "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36" :TE "XML" :KB "%s" :REFERRER "http://malta.csail.mit.edu/wikiscout" :DE "no" :ACTION "%s" :FG "yes" :SERVER "%s" :QE "HTML" :EQ "history" :QI "qsymbols" :MACHINE "%s" :HTTP_HOST "groups.csail.mit.edu")' % (remote_address, json.dumps(query), kb, action, server, machine)
    return request


def parse(sentence, host='localhost', server='guest'):
    telnet, remote_address = _connect(host, server)
    request = _format_request(sentence, 'parse', remote_address, kb='no')
    telnet.write(request)
    response = telnet.read_all().strip()
    telnet.close()

    if response.find('===> NULL') != -1:
        return None

    try:
        parsed = xmltodict.parse(response)
    except:
        raise Exception("Could not parse:\n%s" % response)

    if 'interaction' in parsed and 'query' in parsed['interaction']:
        if 'exception' not in parsed['interaction']['query'] and 'reply' in parsed['interaction']['query']:
            return parsed['interaction']['query']

    return None


def parseable(self,sentence):
    return self.parse(sentence) is not None


def ask(question, host='localhost', server='guest'):
    telnet, remote_address = _connect(host, server)
    request = _format_request(question, 'parse', remote_address, kb='no')
    telnet.write(request)
    response = telnet.read_all().strip()
    telnet.close()

    response = response.replace('<EM>', '')
    response = response.replace('</EM>', '')
    response = response.replace('<HR>', '')
    response = response.replace('</HR>', '')
    response = re.sub(r'<img.*?>',  '', response)

    try:
        parsed = xmltodict.parse(response)
    except:
        raise Exception("Could not parse:\n%s" % response)
        if 'interaction' in parsed and 'query' in parsed['interaction']:
            return parsed['interaction']['query']
        return None
