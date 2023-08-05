"""
Dump a SQL dataset into a sqlite db file.

"""

import sys
import os
import urlparse
import sqlite3

import numpy
from simplejson import dumps

from pydap.model import *
from pydap.lib import walk
from pydap.client import open_url


sqlite3.register_adapter(numpy.float32, float)
sqlite3.register_adapter(numpy.float32, float)
sqlite3.register_adapter(numpy.int32, int)


type_name = {
    Float64: 'NUMBER',
    Float32: 'NUMBER',
    Int32: 'NUMBER',
    Int16: 'NUMBER',
    Byte: 'NUMBER',
    UInt32: 'NUMBER',
    UInt16: 'NUMBER',
    String: 'TEXT',
    Url: 'TEXT',
}


def freeze():
    url = sys.argv[1]
    basename = urlparse.urlsplit(url).path.rsplit('/', 1)[1].rsplit('.', 1)[0]

    # get remote dataset
    dataset = open_url(url)

    # create table for metadata
    connection = sqlite3.connect('%s.db' % basename, detect_types=sqlite3.PARSE_DECLTYPES)
    connection.executescript("""
        CREATE TABLE attributes (
            id VARCHAR(255),
            value TEXT);
        CREATE INDEX id ON attributes (id);
    """)
    connection.commit()

    # insert global attributes
    dataset.attributes['__name__'] = dataset.name
    connection.execute(
        "INSERT INTO attributes (id, value) VALUES (?, ?);",
        ('DATASET', dumps(dataset.attributes)))

    # get our sequence
    n = 0
    for sequence in walk(dataset, SequenceType):
        n += 1
    if n != 1:
        raise Exception("Exactly one sequence must be present in the dataset.")

    # insert sequence attributes
    sequence.attributes['__name__'] = sequence.name
    connection.execute(
        "INSERT INTO attributes (id, value) VALUES (?, ?);",
        ('SEQUENCE', dumps(sequence.attributes)))

    # create table for data
    for i, child in enumerate(sequence.values()):
        if i == 0:
            connection.executescript("CREATE TABLE data (%s %s);" % (child.name, type_name[child.type]))
        else:
            connection.executescript("ALTER TABLE data ADD COLUMN %s %s;" % (child.name, type_name[child.type]))

        # add attributes
        child.attributes['__type__'] = child.type.descriptor
        connection.execute(
            "INSERT INTO attributes (id, value) VALUES (?, ?);",
            (child.name, dumps(child.attributes)))
    connection.commit()

    # add data
    for value in sequence:
        markers = ', '.join([ '?' for var in value.keys() ])
        query = "INSERT INTO data (%s) VALUES (%s)" % (', '.join(value.keys()), markers)
        connection.execute(query, value.data)

    connection.commit()
