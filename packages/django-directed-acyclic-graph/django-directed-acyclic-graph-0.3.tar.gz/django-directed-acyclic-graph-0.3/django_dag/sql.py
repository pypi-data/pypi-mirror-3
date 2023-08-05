import os
from django.db import connections, transaction

def sql(obj, params=(), using="default", as_dict=False):
    """
Execute arbitrary SQL, passed either as a filepath or a string.

Filenames should be relative to BRIGHTWAY_ROOT_PATH.

Outputs a cursor object. It is up to the consumer to fetchone(), fetchall(), etc.

.. rubric:: Inputs

* obj: String. Either a filepath or a string for the SQL to execute.
* params: Tuple. Parameters for SQL query
* using: String. Database to use (useful only with multiple databases)

.. rubruc:: Outputs

A python DBABI cursor object.
    """
    # TODO: Pass stringIO object as well?
    try:
        filepath = os.path.join(os.path.dirname(__file__), obj)
        query = open(filepath, "r").read()
    except IOError:
        # Assume query is a string
        query = obj
    cursor = connections[using].cursor()
    cursor.execute(query, params)
    if as_dict:
        return dict_cursor(cursor)
    else:
        return cursor

def dict_cursor(cursor):
    """Turn SQL tuples into dictionaries. Returns generator."""
    description = [x[0] for x in cursor.description]
    for row in cursor:
        yield dict(zip(description, row))

