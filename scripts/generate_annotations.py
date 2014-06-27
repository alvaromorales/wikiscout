import datetime
import logging
from wikiscout import annotation
from wikiscout.start import STARTServerException
from unidecode import unidecode
import multiprocessing
from collections import namedtuple
from pymongo.errors import ConnectionFailure

Candidate = namedtuple('Candidate', ['cls', 'attribute', 'sentence', 'object', 'value'])

manager = multiprocessing.Manager()
results = manager.Queue()
failQ = manager.Queue()
dead = manager.Event()
finished = manager.Event()

logger = logging.getLogger(__name__)
handler = logging.FileHandler('/scratch/wikiscout/wikiscout.log')
logger.addHandler(handler)


def process_candidate(c):
    if dead.is_set():
        str = "%s\n" % "\t".join([c.cls, c.attribute, c.sentence, c.object, c.value])
        str = unidecode(unicode(str)).encode('utf8', 'ignore')
        failQ.put(str)
        return

    if c.object == c.value:
        return

    try:
        a = annotation.annotate(c.sentence, c.object).join_tokens()
        str = "%s\n" % "\t".join([c.cls, c.attribute, a, c.object, c.sentence, c.value])
        str = unidecode(unicode(str)).encode('utf8', 'ignore')
        results.put(str)
        return
    except (STARTServerException, ConnectionFailure):
        if not dead.is_set():
            dead.set()
            print "Fatal exception raised while processing:\n%s" % c.__str__()
        str = "%s\n" % "\t".join([c.cls, c.attribute, c.sentence, c.object, c.value])
        str = unidecode(unicode(str)).encode('utf8', 'ignore')
        failQ.put(str)
        return
    except Exception as e:
        logger.exception(e)
        return


def get_candidates(path):
    f = open(path)
    candidates = []
    for l in f:
        cls, attribute, sentence, object, value = l.strip().split('\t')
        candidates.append(Candidate(cls, attribute, sentence, object, value))
    f.close()
    return candidates


def process_results():
    outf = open('annotations.tsv', 'a')
    while True:
        s = results.get(True)
        if s is None:
            break

        outf.write('%s' % s)
        outf.flush()
    outf.close()


def process_fail():
    failf = open('sentences-remaining.tsv', 'w')
    while True:
        s = failQ.get(True)
        if s is None:
            break

        failf.write('%s' % s)
        failf.flush()
    failf.close()


def run():
    print "Getting candidates ..."
    candidates = get_candidates('sentences-todo.tsv')

    resultsd = multiprocessing.Process(target=process_results)
    resultsd.start()
    faild = multiprocessing.Process(target=process_fail)
    faild.start()
    print "Started resultsd and faild"

    start_time = datetime.datetime.now()
    print "Starting map tasks at %s" % start_time
    pool.map_async(process_candidate, candidates)
    pool.close()
    pool.join()

    results.put(None)
    failQ.put(None)

    resultsd.join()
    faild.join()
    print "Total runtime: %s" % (datetime.datetime.now() - start_time)

if __name__ == '__main__':
    pool = multiprocessing.Pool(12)
    run()
