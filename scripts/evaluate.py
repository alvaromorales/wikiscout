import os
import sys
import argparse
import logging
import json
from wikiscout import config, start

def log_responses(questions_file, machine, server):
    f = open(questions_file)
    outf = open('eval_answers.json','w')

    for question in f:
        try:
            question = question.strip()
            if question == '':
                continue
            logging.info('Processing: %s'%question)
            response = start.ask(question, machine=machine, server=server)
            outf.write('%s\n'%json.dumps(response))
        except Exception as e:
            logging.exception(e)

def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)
    log_responses(args.file, 'tonga', 'ailab')

if __name__ == '__main__':
    #os.chdir(config.data_dir())

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
            
