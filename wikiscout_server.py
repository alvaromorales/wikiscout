import logging
import SocketServer
from pyparsing import OneOrMore, nestedExpr
from wikiscout import annotation

logger = logging.getLogger(__name__)

class WikiScoutHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        self.data = self.rfile.readline().strip()

<<<<<<< HEAD
        logger.info('-----------------------------------')
=======
        print '-----------------------------------\n'
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
        logger.info('%s wrote: %s' % (self.client_address[0], self.data))
        
        data = OneOrMore(nestedExpr()).parseString(self.data)[0]

        if data[0] != 'get-annotation':
            self.wfile.write('ERROR: method "%s" not supported' % data[0])
        elif len(data) != 3:
            self.wfile.write('ERROR: badly formatted request')
        else:
            object = data[1][1:-1]
            sentence = data[2][1:-1]
            try:
<<<<<<< HEAD
                logging.info("Sentence: %s" % sentence)
                a = annotation.annotate(sentence, object)
                logging.info("Annotation: %s" % a.join_tokens())
=======
                a = annotation.annotate(sentence, object)
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
                self.wfile.write(a.join_tokens() + "\n")
            except annotation.ObjectNotFoundException as e:
                logging.exception(e)
                self.wfile.write('ERROR: %s' % e)
            except annotation.ObjectSymbolNotFoundException as e:
                logging.exception(e)
                self.wfile.write('ERROR: %s' % e)

<<<<<<< HEAD
        logger.info('-----------------------------------')


if __name__ == "__main__":
    format="[%(levelname)s %(name)s %(funcName)s:%(lineno)d]\t\t%(message)s"
    logging.basicConfig(filename='/data/infolab/misc/wikiscout/log/server.log', level=logging.DEBUG, format=format)
=======
        print '-----------------------------------\n'

if __name__ == "__main__":
    format="[%(levelname)s %(name)s %(funcName)s:%(lineno)d]\t\t%(message)s"
    logging.basicConfig(level=logging.DEBUG, format=format)
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
    HOST, PORT = "malta.csail.mit.edu", 8088

    server = SocketServer.TCPServer((HOST, PORT), WikiScoutHandler)
    server.serve_forever()
