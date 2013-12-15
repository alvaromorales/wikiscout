from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
from wikiscout.wikikb import WikiKB

def get(wiki_class,title,attribute):
    w = WikiKB('nauru')
    return w.get(wiki_class,title,attribute)

def get_classes(title):
    w = WikiKB('nauru')
    return w.get_classes(title)
    
def get_attributes(wiki_class,title):
    w = WikiKB('nauru')
    return w.get_attributes(wiki_class,title)
    
server = SimpleJSONRPCServer(('localhost', 8029))

server.register_function(get)
server.register_function(get_classes)
server.register_function(get_attributes)
server.serve_forever()
