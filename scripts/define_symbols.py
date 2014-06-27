import re
import sys
import argparse
import logging
import json

from wikiscout.infobox import normalize_class
from wikiscout.annotation import Annotation
from wikiscout import schemata

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
    
    f = open(args.attributes)
    outf = open('wikiscout-matching-symbols.lisp','w')

    symbols = set()

    outf.write("""\n;;;------------------------------------------------------------------- 
;;;
;;; WikiScout Lexical Data
;;;
""")

    for l in f:
        template_attributes = json.loads(l)
        template = template_attributes['template']
        wiki_class = normalize_class(template)
        symbol = Annotation.generate_symbol(template)
        if symbol is None:
            continue

        symbols.add((symbol,wiki_class))

    common = set(['any-wikipedia-term','any-wikipedia-person'])

    for symbol,wiki_class in symbols:
        if symbol in common:
            definition = schemata.define(symbol,wiki_class,index=11)
        else:
            definition = schemata.define(symbol,wiki_class)
    
        outf.write(definition)
    
    f.close()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = "Generates matching symbol definitions for WikiScout annotations",
        epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars = '@' )

    parser.add_argument(
        "attributes",
        help = "pass attributes to the program",
        metavar = "attributes")

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
            
