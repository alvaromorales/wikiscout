from pyparsing import OneOrMore, nestedExpr
import telnetlib
import xmltodict
import socket
import re

class START:
    def __init__(self,host='localhost'):
        self.host = host

    def connect(self):
        # open a new telnet connection to START
        try:
            self.telnet = telnetlib.Telnet(self.host,8002)
            self.remote_address = socket.gethostbyname(socket.gethostname())
        except:
            print "Could not connect to START host %s"%self.host
            raise
    
    def format_request(self,query,action):
        request = '(:REMOTE-ADDRESS "%s" :VB "normal" :QUERY "%s" :USER_AGENT "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.69 Safari/537.36" :TE "XML" :KB "yes" :REFERRER "http://nauru.csail.mit.edu/paraphrase-test" :DE "no" :ACTION "%s" :FG "yes" :SERVER "ailab" :QE "HTML" :EQ "history" :QI "qsymbols" :MACHINE "nauru.csail.mit.edu" :HTTP_HOST "groups.csail.mit.edu")'%(self.remote_address,query,action)
        return request

    def ask(self,question):
        self.connect()
        request = self.format_request(question,'askstart')
        self.telnet.write(request)
        response = self.telnet.read_all().strip()
        self.close()
        response = response.replace('<EM>','')
        response = response.replace('</EM>','')
        response = response.replace('<HR>','')
        response = response.replace('</HR>','')
        response = re.sub(r'<img.*?>', '',response)
        try:
            parsed = xmltodict.parse(response)
        except:
            print "Could not parse:\n%s"%response
            raise
        if 'interaction' in parsed and 'query' in parsed['interaction']:
            return parsed['interaction']['query']
        return None

    def close(self):
        self.telnet.close()

