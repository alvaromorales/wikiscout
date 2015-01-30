<<<<<<< HEAD
import os
=======
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
import sys
import argparse
import logging
import json
<<<<<<< HEAD
from wikiscout import config, start

def log_responses(questions_file, machine, server):
    f = open(questions_file)
    outf = open('eval_answers.json','w')

=======
from wikiscout.start import START

def log_responses(questions_file):
    f = open(questions_file)
    outf = open('eval_answers.json','w')

    s = START('faroe.csail.mit.edu')

>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
    for question in f:
        try:
            question = question.strip()
            if question == '':
                continue
            logging.info('Processing: %s'%question)
<<<<<<< HEAD
            response = start.ask(question, machine=machine, server=server)
=======
            response = s.ask(question)
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
            outf.write('%s\n'%json.dumps(response))
        except Exception as e:
            logging.exception(e)

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
<<<<<<< HEAD
    log_responses(args.file, 'tonga', 'ailab')

if __name__ == '__main__':
    #os.chdir(config.data_dir())

=======
    log_responses(args.file)

if __name__ == '__main__':
>>>>>>> 7e8fecb47ed018554811213dac196167c98ec94f
    parser = argparse.ArgumentParser(
        description = "<What the script does.>", #TODO
        epilog = "As an alternative to the commandline, params can be placed in a file, one per line, and specified on the commandline like '%(prog)s @params.conf'.",
        fromfile_prefix_chars = '@' )

    # TODO Specify your real parameters here.
    parser.add_argument(
        "file",
        help = "pass file to the program",
        metavar = "file")

    parser.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="store_true")
    args = parser.parse_args()

    if args.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO

    main(args, loglevel)
            
