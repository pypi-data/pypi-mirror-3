import sys
import re 
import os.path
import operator
import itertools
import copy
import sqlite3
import logging
log = logging.getLogger('pydap')

from simplejson import loads

from pydap.model import *
from pydap.model import SequenceData
from pydap.proxy import ConstraintExpression
from pydap.lib import combine_slices, fix_slice
from pydap.util.safeeval import expr_eval
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError, ConstraintExpressionError


class Handler(BaseHandler):

    extensions = re.compile(r"^.*\.db$", re.IGNORECASE)

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_constraints(self, environ):
        try:
            conn = sqlite3.connect(self.filepath, 
                    detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        # Build the dataset object, populating the metadata from the DB. Attributes
        # are stored as JSON objects in the DB.
        curs = conn.execute("SELECT value FROM attributes WHERE id='DATASET';")
        attrs = loads(curs.fetchone()[0])
        name = attrs.pop('__name__', os.path.splitext(os.path.basename(self.filepath))[0])
        dataset = DatasetType(name, attrs)

        # Build the sequence object, and insert it in the dataset.
        curs = conn.execute("SELECT value FROM attributes WHERE id='SEQUENCE';")
        attrs = loads(curs.fetchone()[0])
        name = attrs.pop('__name__', 'sequence')
        seq = SequenceType(name, attrs)
        dataset[seq.name] = seq

        # Parse the constraint expression from ``environ['pydap.ce']``,
        # extracting the requested fields, any filters (queries) and the
        # slice for the sequence.
        fields, queries = environ['pydap.ce']
        queries = filter(bool, queries)  # fix for older version of pydap
        curs = conn.execute("SELECT * FROM data LIMIT 1")
        all_vars = [ t[0] for t in curs.description ]
        slices = [f[0][1] for f in fields if f[0][0] == seq.name]
        if slices:
            slice_ = slices[0]
        else:
            slice_ = None
        # Check that all slices are equal. 
        if [s for s in slices if s != slice_]:
            raise ConstraintExpressionError('Slices are not unique!')
        # If no fields have been explicitly requested, of if the sequence
        # has been requested directly, return all variables.
        if not fields or seq.name in [f[0][0] for f in fields if len(f) == 1]:
            fields = [[(name, ())] for name in all_vars]

        # Add all requested variables to the sequence.
        cols = []
        for var in fields:
            while var:
                name, unused_slice = var.pop(0)
                if name == seq.name:
                    continue
                elif name in all_vars:
                    curs = conn.execute("SELECT value FROM attributes WHERE id=?;", (name,))
                    attrs = loads(curs.fetchone()[0])
                    cols.append(name)
                    type_ = typemap[attrs.pop('__type__', 'Int32').lower()]
                    seq[name] = BaseType(name=name, type=type_)
                else:
                    raise ConstraintExpressionError('Invalid token: "%s"' % name)

        # Add a proxy to the data.
        seq.data = SQLProxy(seq.id, tuple(cols), queries, self.filepath, slice_)
        return dataset


class SQLProxy(SequenceData):
    """
    A ``SequenceData`` object that reads data from a database.

    """
    def __init__(self, id, cols, queries, filepath, slice_=None):
        self.id = id
        self.cols = cols
        self.queries = queries
        self.filepath = filepath
        self._slice = slice_ or (slice(None),)

    def __deepcopy__(self, memo=None, _nil=[]):
        out = self.__class__(self.id, self.cols[:],
                self.queries[:], self.filepath, 
                self._slice)
        return out

    def __getitem__(self, key):
        out = copy.deepcopy(self)
        if isinstance(key, ConstraintExpression):
            out.queries.append(str(key))
        elif isinstance(key, basestring):
            out._slice = (slice(None),)
            out.id = '%s.%s' % (self.id, key)
            out.cols = key
        elif isinstance(key, tuple):
            out.cols = key
        else:
            out._slice = combine_slices(self._slice, fix_slice(key, (sys.maxint,)))
        return out

    def __len__(self):
        conn = sqlite3.connect(self.filepath, 
                detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)

        condition = parse_queries(self.queries, self.cols)
        offset = self._slice[0].start or 0
        limit = (self._slice[0].stop or sys.maxint) - (self._slice[0].start or 0)
        query = """SELECT COUNT(*)
FROM data
%(condition)s
LIMIT %(limit)d
OFFSET %(offset)d""" % locals()
        curs = conn.cursor()
        log.info(query)
        curs.execute(query)
        results = curs.fetchone()[0]
        slice_ = fix_slice(self._slice, (results,))
        return (min(results, slice_[0].stop)-slice_[0].start-1)//slice_[0].step+1

    @property
    def query(self):
        if isinstance(self.cols, tuple):
            cols = ', '.join(self.cols)
        else:
            cols = self.cols
        condition = parse_queries(self.queries, self.cols)
        offset = self._slice[0].start or 0
        limit = (self._slice[0].stop or sys.maxint) - (self._slice[0].start or 0)

        return """SELECT %(cols)s
FROM data
%(condition)s 
LIMIT %(limit)d
OFFSET %(offset)d""" % locals()

    def __iter__(self):
        conn = sqlite3.connect(self.filepath, 
                detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        curs = conn.cursor()
        log.info(self.query)
        curs.execute(self.query)

        # slice and filter data
        data = curs
        data = itertools.islice(data, 0, None, self._slice[0].step)
        if not isinstance(self.cols, tuple):
            data = itertools.imap(operator.itemgetter(0), data)
        return data

    # Comparisons return a ``ConstraintExpression`` object
    def __eq__(self, other): return ConstraintExpression('%s=%s' % (self.id, other))
    def __ne__(self, other): return ConstraintExpression('%s!=%s' % (self.id, other))
    def __ge__(self, other): return ConstraintExpression('%s>=%s' % (self.id, other))
    def __le__(self, other): return ConstraintExpression('%s<=%s' % (self.id, other))
    def __gt__(self, other): return ConstraintExpression('%s>%s' % (self.id, other))
    def __lt__(self, other): return ConstraintExpression('%s<%s' % (self.id, other))


def parse_queries(queries, cols):
    CE = re.compile(r'''^                         # Start of selection
                       (?P<var1>.*?)              # Anything
                       (?P<op><=|>=|!=|=~|>|<|=)  # Operators
                       {?                         # {
                       (?P<var2>.*?)              # Anything
                       }?                         # }
                       $                          # EOL
                    ''', re.VERBOSE)
    out = []
    for query in queries:
        m = CE.match(query)
        if not m:
            raise ConstraintExpressionError('Invalid constraint expression: %s.' % query)
        var1, op, var2 = m.groups()
        if op == '=~':
            raise ConstraintExpressionError('Regular expressions disallowed!')

        # evaluate variables
        if var1 == cols or var1 in cols:
            var2 = expr_eval(var2)

            if isinstance(var2, tuple):
                subsubquery = []
                for var in var2:
                    subsubquery.append('(%s %s %s)' % (var1, op, repr(var)))
                subquery = '(%s)' % ' OR '.join(subsubquery)
            else:
                subquery = '(%s %s %s)' % (var1, op, repr(var2))
            out.append(subquery)
    condition = ' AND '.join(out)
    if condition:
        condition = 'WHERE %s' % condition
    return condition


if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
