import re
import json

numbers = { 1 : '-one', 2 : '-two', 3 : '-three', 4 : '-four', 5 : '-five', 6 : '-six', 7 : '-seven', 8 : '-eight', 9 : '-nine',
            10 : '-ten', 11 : '-eleven', 12 : '-twelve', 13 : '-thirteen', 14 : '-fourteen', 15 : '-fifteen', 16 : '-sixteen',
            17 : '-seventeen', 18 : '-eighteen', 19 : '-nineteen' , 20 : '-twenty' }

def define(symbol,wiki_class,index=6,already_defined=False):
    definition = ["\n(make-neuter-nouns", "  (%s :prop ((matching-symbol t) (referent-class %s)))"%(symbol,wiki_class)]
    
    for i in range(1,index):
        indexed_symbol = symbol + numbers[i]
        definition.append('  (%s :gens (%s) :prop ((matching-symbol t) (referent-class %s)))'%(indexed_symbol,symbol,wiki_class))
    
    definition.append(')\n')
    
    return '\n'.join(definition)

def generate(annotation,index,wiki_class,attributes):
    annotation = json.dumps(annotation)
    attrs = symbol_list(attributes)

    return """
(def-schema 'wikiscout-%s
  :sentences '(%s)
  :long-text '((show-wikiscout-literal '%s '%s))
  :sons '(*no-db-links*) :liza '() :function-call T)
"""%(index,annotation,wiki_class,attrs)

def symbol_list(l):
    return '(' + ' '.join(l) + ')'
