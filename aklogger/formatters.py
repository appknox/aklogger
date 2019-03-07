from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import logging
import traceback
import itertools as it

from builtins import * # noqa
from .utils import CustomEncoder

BASIC_FORMAT = '%(message)s'
CONSOLE_FORMAT = '%(name)-12s: %(levelname)-8s %(message)s'
FIXED_FORMAT = (
    '%(asctime)s.%(msecs)-3d %(name)-12s %(levelname)-8s %(message)s')
CSV_FORMAT = '%(asctime)s.%(msecs)d,%(name)s,%(levelname)s,"%(message)s"'
JSON_FORMAT = (
    '{"time": "%(asctime)s.%(msecs)d", "name": "%(name)s", "level":'
    ' "%(levelname)s", "message": "%(message)s"}')

DATEFMT = '%Y-%m-%d %H:%M:%S'


class StructuredFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        empty_record = logging.makeLogRecord({})
        filterer = lambda k: k not in empty_record.__dict__ and k != 'asctime' # noqa
        self.filterer = filterer
        super(StructuredFormatter, self).__init__(fmt, datefmt)

    def format(self, record):
        extra = {
            'message': record.getMessage(),
            'time': self.formatTime(record, self.datefmt),
            'msecs': record.msecs,
            'name': record.name,
            'level': record.levelname}

        keys = filter(self.filterer, record.__dict__)
        extra.update({k: record.__dict__[k] for k in keys})
        extra.pop('asctime', None)
        return str(CustomEncoder().encode(extra))

    def formatException(self, exc_info):
        keys = ['type', 'value', 'filename', 'lineno', 'function', 'text']
        type_, value, trcbk = exc_info
        stype = str(type_).replace('type', '').strip(" '<>")
        values = it.chain([stype, value], *traceback.extract_tb(trcbk))
        return str(CustomEncoder().encode(dict(zip(keys, values))))


basic_formatter = logging.Formatter(BASIC_FORMAT)
console_formatter = logging.Formatter(CONSOLE_FORMAT)
fixed_formatter = logging.Formatter(FIXED_FORMAT, datefmt=DATEFMT)
csv_formatter = logging.Formatter(CSV_FORMAT, datefmt=DATEFMT)
json_formatter = logging.Formatter(JSON_FORMAT, datefmt=DATEFMT)
structured_formatter = StructuredFormatter(BASIC_FORMAT, datefmt=DATEFMT)
