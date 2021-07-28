from calendar import c
import os
import pandas as pd
# pylint: disable=no-name-in-module
from cassandra.cluster import Cluster
# pylint: disable=no-name-in-module
from cassandra.query import ordered_dict_factory
import enum
from abc import ABC

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get(
    "CASSANDRA_HOST") else "localhost"
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get(
    "CASSANDRA_KEYSPACE") else "kafkapipeline"
KRAKEN_TABLE = os.environ.get("KRAKEN_TABLE") if os.environ.get(
    "KRAKEN_TABLE") else "kraken_tick_data"
CRYPTOPANIC_TABLE = os.environ.get("CRYPTOPANIC_TABLE") if os.environ.get(
    "CRYPTOPANIC_TABLE") else "cryptopanic_news"


class SortingType(str, enum.Enum):
  DESCENDING = "DESC"
  ASCENDING = "ASC"


# TODO: Create cursor pagination for CryptoPanic, Kraken
class QueryUtils(ABC):

  def __init__(self, table: str):
    self.table = table
    self.cluster = Cluster(CASSANDRA_HOST) if (isinstance(
        CASSANDRA_HOST, list)) else Cluster([CASSANDRA_HOST])
    self.session = self.cluster.connect(CASSANDRA_KEYSPACE)

  def query(self,
            limit=None,
            sort: SortingType = SortingType.DESCENDING,
            cursor=None,
            col_cursor=None,
            col_order=None,
            to_dataframe=False):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE '{}' <= {}".format(col_cursor, cursor) if cursor != None else ""}
    {"ORDER BY {} {}".format(col_order, sort) if sort != None else ""}
    {"LIMIT {}".format(limit) if limit != None else ""}
    ;
    """
    # future = self.session.execute_async(CQL_QUERY)
    # try:
    #   rows = future.result()
    # except Exception:
    #   print("Operation failed!")
    # if (to_dataframe == True):
    #   return pd.DataFrame(rows)
    rows = self.session.execute(CQL_QUERY)
    return [dict(row) for row in rows.all()]


class KrakenQueryUtils(QueryUtils):

  def __init__(self, table: str = KRAKEN_TABLE):
    super().__init__(table)

  def queryByPair(self,
                  pair=None,
                  limit=None,
                  sort: SortingType = None,
                  cursor=None,
                  col_cursor=None,
                  col_order=None,
                  to_dataframe=False,
                  to_json=False):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE pair = '{}'".format(pair) if cursor == None else ""}
    {"WHERE pair = '{}' AND {} <= {}".format(pair, col_cursor, cursor) if cursor != None else ""}
    {"ORDER BY {} {}".format(col_order, sort) if col_order != None and sort != None else ""}
    {"LIMIT {}".format(limit) if limit != None else ""}
    ;
    """
    future = self.session.execute_async(CQL_QUERY)
    try:
      rows = future.result()
    except Exception:
      print("Operation failed!")
    if (to_dataframe == True):
      return pd.DataFrame(rows)
    return [dict(row) for row in rows.all()]


# FIXME: Local variable 'rows' return before assignment AND try to optimize cluster connect!
class CryptoPanicQueryUtils(QueryUtils):

  def __init__(self, table: str = CRYPTOPANIC_TABLE):
    super().__init__(table)

  def query(self,
            limit=None,
            sort: SortingType = None,
            cursor=None,
            col_cursor=None,
            col_order=None,
            to_dataframe=False):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE kind IN ('news', 'media')" if cursor == None else ""}    
    {"WHERE kind IN ('news', 'media') AND {} <= {}".format(col_cursor, cursor) if cursor != None else ""}
    {"ORDER BY {} {}".format(col_order, sort) if col_order != None and sort != None else ""}
    {"LIMIT {}".format(limit) if limit != None else ""}
    ;
    """
    # future = self.session.execute_async(CQL_QUERY)
    # try:
    #   rows = future.result()
    # except Exception:
    #   print("Operation failed!")
    # if (to_dataframe == True):
    #   return pd.DataFrame(rows)
    rows = self.session.execute(CQL_QUERY)
    return [dict(row) for row in rows.all()]
