import json
import re
from pyparsing import OneOrMore, nestedExpr
import telnetlib

class Omnibase:
    def __init__(self,host='localhost'):
        self.host = host
        self.scheme_parser = OneOrMore(nestedExpr())
        self.connect()
    
    def connect(self):
        # open a new telnet connection to omnibase
        try:
            self.telnet = telnetlib.Telnet(self.host,8008)
        except:
            print "Could not connect to Omnibase host %s"%self.host
            raise
    
    def get(self,omnibase_class,symbol,attribute):
        self.connect()
        
        self.telnet.write('(get "%s" "%s"  "%s")'%(omnibase_class,symbol,attribute.upper()))
        
        response = self.telnet.read_all()
        response = re.sub(r'\n','',response)

        self.close()

        if response.strip() == '#f':
            return None

        return list(eval(response.replace('" "','","')))

    def get_symbols(self,s,omnibase_class=None):
        self.connect()
        s = json.dumps(s)

        if omnibase_class is not None:
            self.telnet.write('(get-symbols %s \':class "%s")'%(s,omnibase_class))
        else:
            self.telnet.write('(get-symbols %s)'%s)

        response = self.telnet.read_all()

        try:
            parsed_response = self.parse_get_symbols_response(response)
        except:
            raise Exception('Omnibase could not parse: %s'%self.sentence)

        self.close()
        return parsed_response

    def get_known(self,s,omnibase_class=None):
        self.connect()
        s = json.dumps(s)

        if omnibase_class is not None:
            self.telnet.write('(get-known %s \':class "%s")'%(s,omnibase_class))
        else:
            self.telnet.write('(get-known %s)'%s)
        
        response = self.telnet.read_all()
        parsed_response = self.parse_get_symbols_response(response)
        
        self.close()
        return parsed_response

    def parse_get_symbols_response(self,response):
        if response[:2] == '()':
            return None

        # some responses are HUGE ... we truncate them
        
        if len(response) > 0 and response[-2:] != "))":
            last_occurence = response.rfind(':priority 0)')
            response = response[:last_occurence + len(':priority 0)')] + ")"
        
        parsed_response = []

        try:
            data = self.scheme_parser.parseString(response)
        except:
            raise Exception("Could not parse %s"%response)

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

    def close(self):
        self.telnet.close()

