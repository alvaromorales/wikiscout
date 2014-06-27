import sys
import argparse
import logging
import json
from annotation import Annotation
from start import START
from scout import Scout

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel, filename='/scratch/wiki/wikiscout/logs/wikiscout.log', filemode='w')
    
    s = Scout(args.attributes,args.candidates,args.output)
    annotations,total = s.run()
    
    print "====\nWikiScout: Generated %s annotations out of %s candidates\n===="%(annotations,total)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description = "Generates a schemata file of Wikiscout annotations",
        epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars = '@' )

    parser.add_argument(
        "attributes",
        help = "pass attributes to the program",
        metavar = "attributes")

    parser.add_argument(
        "candidates",
        help = "pass candidates to the program",
        metavar = "candidates")

    parser.add_argument(
        "output",
        help = "pass output to the program",
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
            
