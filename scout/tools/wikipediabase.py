from pyparsing import OneOrMore, nestedExpr
import re
import telnetlib

class WikipediaBase:
    def __init__(self,host='localhost'):
        self.host = host
        self.scheme_parser = OneOrMore(nestedExpr())
        self.connect()
    
    def connect(self):
        # open a new telnet connection to WikipediaBase
        try:
            self.telnet = telnetlib.Telnet(self.host,8023)
        except:
            print "Could not connect to WikipediaBase host %s"%self.host
            raise
    
    def get_classes(self,s):
        self.connect()
        self.telnet.write('(get-classes "%s")\n'%s)
        response = self.telnet.read_all()

        try:
            parsed_response = self.parse_get_classes_response(response)
        except:
            raise Exception('WikipediaBase could not parse: %s'%self.sentence)

        self.close()
        return parsed_response
    
    def parse_get_classes_response(self,response):
        if response.strip() == '#f':
            return []

        response = re.sub(r'<!---.*?\"','\"',response)
        response = re.sub(r'\n','',response)

        return map(lambda c: eval(c),response.strip()[1:-1].split(' '))

    def close(self):
        self.telnet.close()

