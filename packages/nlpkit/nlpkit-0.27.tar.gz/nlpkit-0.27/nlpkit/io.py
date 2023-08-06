import logging
import sys
import codecs
import json

from bson import json_util

def json_load(filename):
    if filename == "-":
        file = sys.stdin
    else:
        file = codecs.open(filename)
    for lineno, line in enumerate(file, 1):
        try:
            yield json.loads(line, object_hook=json_util.object_hook)
        except Exception as e:
            logging.error("JSON error in line {} of file {}".format(lineno, filename))
            raise e

class JSONDumper(object):
    def __init__(self, filename):
        self._filename = filename
        if filename == '-':
            self._file = sys.stdout
        else:
            self._file = codecs.open(filename, 'w', encoding='utf-8')

    def dump(self, doc):
        print >>self._file, json.dumps(doc, default=json_util.default)

    def close(self):
        if self._filename != '-':
            self._file.close()

def json_dump(iterable, fname):
    dumper = JSONDumper(fname)
    for doc in iterable:
        dumper.dump(doc)
    dumper.close()

def json_map(map_func, fname_in, fname_out):
    dumper = JSONDumper(fname_out)
    for doc in json_load(fname_in):
        dumper.dump(map_func(doc))
    dumper.close()

def mongo_checkout(iter, value_fname, key_fname=None):
    pass