import sys
import argparse
import logging
import json

from wikiscout.annotation import Annotation
from wikiscout.start import START
from wikiscout import infobox
from wikiscout import schemata

start = START('nauru.csail.mit.edu')
attributes = {}

def load_attributes(attributes_file):
    attributes = {}
    
    for l in attributes_file:
        template_attrs = json.loads(l)
        template = template_attrs['template']
        for d in template_attrs['attributes']:
            attribute = d['attribute']
            raw = d['raw']
            attributes[(template,attribute)] = raw
    
    return attributes

def eval_candidate(template,attribute,sentence,value,wiki_title,index):
    try:
        annotation = Annotation(sentence,wiki_title,template,value).get()
    except Exception as e:
        logging.exception('Could not generate annotation for "%s". Exception:\n%s'%(sentence,e))
        return None

    if annotation is None:
        return None
        
    try:
        parseable = start.parseable(annotation)
    except Exception as e:
        logging.error('START parse error:\n%s'%e)
        return None
        
    if parseable:
        wiki_class = infobox.get_class(template)
        return (annotation,wiki_class)

def generate_schema(index,annotation,wiki_class,attribute,template):
    if (template,attribute) not in attributes:
        logging.warn('No raw attributes for attribute "%s" of template "%s"'%(attribute,template))
        raw_attributes = [attribute]
    else:
        raw_attributes = attributes[(template,attribute)]
    
    schema = schemata.generate(annotation,index,wiki_class,raw_attributes)
    return schema
    
def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel, filename='%s/wikiscout.log'%args.output, filemode='w')

    schemata_file = open(args.output + '/wikiscout-schemata.lisp','w')
    log_file = open(args.output + '/wikiscout-output.tsv','w')
    log_file.write('Index\tTitle\tClass\tAttribute\tValue\tAnnotation\tSentence\n')
    candidates_file = open(args.candidates)
    
    global attributes
    attributes = load_attributes(open(args.attributes))
    
    index = 0
    total = 0

    for l in candidates_file:
        template_candidates = json.loads(l)
        template = template_candidates['infobox_type']
        
        for attribute in template_candidates['attributes']:
            if attribute in ['common_name']:
                logging.info('Skipping attribute: %s'%attribute)
                continue
            
            candidates = template_candidates['attributes'][attribute]
            for candidate in candidates:
                sentence = candidate['sentence']
                value = candidate['value']
                wiki_title = candidate['wikiTitle']
                
                total += 1
                result = eval_candidate(template,attribute,sentence,value,wiki_title,index)
                if result is not None:
                    annotation,wiki_class = result
                    schema = generate_schema(index,annotation,wiki_class,attribute,template)
                    
                    try:
                        log_file.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(index,wiki_title,wiki_class,attribute,value,annotation,sentence))
                        schemata_file.write(schema)
                        index += 1
                    except Exception as e:
                        logging.error('Could not write schema for article %s, attribute %s and value %s'%(wiki_title,attribute,value))
        
    print "====\nWikiScout: Generated %s annotations out of %s candidates\n===="%(index,total)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = "Generates a schemata file of Wikiscout annotations",
        epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars = '@' )

    parser.add_argument(
        "attributes",
        help = "the attributes file",
        metavar = "attributes")

    parser.add_argument(
        "candidates",
        help = "the file with extracted sentences",
        metavar = "candidates")

    parser.add_argument(
        "output",
        help = "the destination directory",
        metavar = "output")

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")

    parser.add_argument(
        "-q",
        "--quiet",
        help="decrease output verbosity",
        action="store_true")

    args = parser.parse_args()

    loglevel = logging.INFO
    if args.verbose:
        loglevel = logging.DEBUG
    if args.quiet:
        loglevel = logging.WARN
    
    main(args, loglevel)
            
