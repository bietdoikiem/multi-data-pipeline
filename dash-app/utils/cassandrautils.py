from calendar import c
import os
import re
import sys
import pandas as pd
# pylint: disable=no-name-in-module
from cassandra.cluster import Cluster
# pylint: disable=no-name-in-module
from cassandra.query import dict_factory
import enum
from abc import ABC, abstractmethod

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get(
    "CASSANDRA_HOST") else "cassandradb"
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get(
    "CASSANDRA_KEYSPACE") else "kafkapipeline"
KRAKEN_TABLE = os.environ.get("KRAKEN_TABLE")
CRYPTOPANIC_TABLE = os.environ.get("CRYPTOPANIC_TABLE")


class SortingType(enum.Enum):
  DESCENDING = "DESC"
  ASCENDING = "ASC"


# TODO: Create cursor pagination for CryptoPanic, Kraken
class QueryUtils(ABC):

  def __init__(self, table: str):
    self.table = table
    self.cluster = Cluster(CASSANDRA_HOST) if (isinstance(
        CASSANDRA_HOST, list)) else Cluster([CASSANDRA_HOST])

  def query(self,
            limit=None,
            sort: SortingType = SortingType.DESCENDING,
            cursor=None,
            col_cursor=None,
            col_order=None,
            to_dataframe=False):
    if (isinstance(CASSANDRA_HOST, list)):
      cluster = Cluster(CASSANDRA_HOST)
    else:
      cluster = Cluster([CASSANDRA_HOST])
    # Setup cassandra connection and query type
    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    --sql START-highlight

    SELECT * 
    FROM {self.table}
    -- if has cursor
    {"WHERE '{}' <= {}".format(col_cursor, cursor) if cursor != None else ""}
    -- if-has-sort
    {"ORDER BY '{}'".format(col_order) if sort != None else ""}
    -- if-has-limit
    {"LIMIT {}".format(limit) if limit != None else ""}

    -- END-highlight
    ;
    """
    rows = session.execute(CQL_QUERY)
    if (to_dataframe == True):
      return pd.DataFrame(rows)
    return rows


class KrakenQueryUtils(QueryUtils):

  def __init__(self, table: str = KRAKEN_TABLE, pair=None):
    super().__init__(table)
    self.pair = pair

  def queryByPair(self,
                  limit=None,
                  sort: SortingType = SortingType.DESCENDING,
                  cursor=None,
                  col_cursor=None,
                  col_order=None,
                  to_dataframe=False):
    if (isinstance(CASSANDRA_HOST, list)):
      cluster = Cluster(CASSANDRA_HOST)
    else:
      cluster = Cluster([CASSANDRA_HOST])
    # Setup cassandra connection and query type
    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE pair = '{}'".format(self.pair) if cursor == None else ""}
    {"WHERE pair = '{}' AND {} <= {}".format(self.pair, col_cursor, cursor) if cursor != None else ""}
    {"ORDER BY {}".format(col_order) if sort != None else ""}
    {"LIMIT {}".format(limit) if limit != None else ""}
    ;
    """
    print("CQLQUERY")
    print(CQL_QUERY, flush=True)
    rows = session.execute(CQL_QUERY)
    if (to_dataframe == True):
      return pd.DataFrame(rows)
    return rows


class CryptoPanicQueryUtils(QueryUtils):

  def __init__(self, table: str = CRYPTOPANIC_TABLE):
    super().__init__(table)

  def query(self,
            limit=None,
            sort: SortingType = SortingType.DESCENDING,
            cursor=None,
            col_cursor=None,
            col_order=None,
            to_dataframe=False):
    super().query(limit, sort, cursor, col_cursor, col_order, to_dataframe)
