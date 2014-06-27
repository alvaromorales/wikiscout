import json

def generate(annotation,index,attributes):
    annotation = json.dumps(annotation)
    attrs = lisp_list(attributes)

    return """
(def-schema 'wikiscout-%s
  :sentences
    '(%s)
  :long-text '((show-wikiscout-field 'any-wikipedia-person '%s))
  :sons '(*no-db-links*) :liza '() :function-call T)
  """%(index,annotation,attrs)

def lisp_list(l):
    elements = ['"' + e + '"' for e in l]
    return '(' + ' '.join(elements) + ')'
