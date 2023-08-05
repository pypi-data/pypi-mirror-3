#!/usr/bin/env python

import datetime
from types import NoneType

from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy import Boolean, Date, DateTime, Float, Integer, String, Time
from sqlalchemy.schema import CreateTable

DIALECTS = {
    'access': 'access.base',
    'firebird': 'firebird.kinterbasdb',
    'informix': 'informix.informixdb',
    'maxdb': 'maxdb.sapdb',
    'mssql': 'mssql.pyodbc',
    'mysql': 'mysql.mysqlconnector',
    'oracle': 'oracle.cx_oracle',
    'postgresql': 'postgresql.psycopg2',
    'sqlite': 'sqlite.pysqlite',
    'sybase': 'sybase.pyodbc'
}

NULL_COLUMN_MAX_LENGTH = 32

def make_column(column):
    """
    Creates a sqlalchemy column from a csvkit Column.
    """
    sql_column_kwargs = {'nullable': False}
    sql_type_kwargs = {}

    column_types = {
        bool: Boolean,
        int: Integer,
        float: Float,
        datetime.datetime: DateTime,
        datetime.date: Date,
        datetime.time: Time,
        NoneType: String,
        unicode: String
        }

    max_lengths = {
        NoneType: NULL_COLUMN_MAX_LENGTH,
        unicode: column.max_length
        }

    if column.type in column_types:
        sql_column_type = column_types[column.type]
    else:
        raise ValueError('Unexpected normalized column type: %s' % column.type)

    if column.type in max_lengths:
        sql_type_kwargs['length'] = max_lengths[column.type]

    sql_column_kwargs['nullable'] = column.nullable

    return Column(column.name, sql_column_type(**sql_type_kwargs), **sql_column_kwargs)

def get_connection(connection_string):
    engine = create_engine(connection_string)
    metadata = MetaData(engine)

    return engine, metadata

def make_table(csv_table, name='table_name', metadata=None):
    """
    Creates a sqlalchemy table from a csvkit Table.
    """
    if not metadata:
        metadata = MetaData()

    sql_table = Table(csv_table.name, metadata)

    for column in csv_table:
        sql_table.append_column(make_column(column))

    return sql_table

def make_create_table_statement(sql_table, dialect=None):
    """
    Generates a CREATE TABLE statement for a sqlalchemy table.
    """
    if dialect:
        module = __import__('sqlalchemy.dialects.%s' % DIALECTS[dialect], fromlist=['dialect'])
        sql_dialect = module.dialect()
    else:
        sql_dialect = None 

    return unicode(CreateTable(sql_table).compile(dialect=sql_dialect)).strip() + ';'

