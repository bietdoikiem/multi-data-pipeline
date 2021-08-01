from calendar import c
import os
import pandas as pd
# pylint: disable=no-name-in-module
from cassandra.cluster import Cluster
# pylint: disable=no-name-in-module
from cassandra.query import ordered_dict_factory
import enum
from abc import ABC
from datetime import datetime

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get(
    "CASSANDRA_HOST") else "localhost"
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get(
    "CASSANDRA_KEYSPACE") else "kafkapipeline"
KRAKEN_TABLE = os.environ.get("KRAKEN_TABLE") if os.environ.get(
    "KRAKEN_TABLE") else "kraken_tick_data"
CRYPTOPANIC_TABLE = os.environ.get("CRYPTOPANIC_TABLE") if os.environ.get(
    "CRYPTOPANIC_TABLE") else "cryptopanic_news"
ANALYSIS_REPORT_TABLE = os.environ.get(
    "ANALYSIS_REPORT_TABLE") if os.environ.get(
        "ANALYSIS_REPORT_TABLE") else "analysis_report"


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
            to_dataframe=False,
            categories=["wordcloud"]):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE kind IN({}) ".format(", ".join([dollar_quote(c) for c in categories])) if cursor == None else ""}    
    {"WHERE kind IN({}) AND {} <= {}".format(", ".join([dollar_quote(c) for c in categories]), col_cursor, cursor) if cursor != None else ""}
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
    # rows = self.session.execute(CQL_QUERY)
    return [dict(row) for row in rows.all()]


class AnalysisQueryUtils(QueryUtils):

  def __init__(self, table: str = ANALYSIS_REPORT_TABLE):
    super().__init__(table)

  def query(self,
            limit=None,
            sort: SortingType = None,
            cursor=None,
            col_cursor=None,
            col_order=None,
            to_dataframe=False,
            categories=["wordcloud"]):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    if (sort != None and col_order == None):
      raise Exception("Column used for sorting order is empty, please specify!")
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    {"WHERE category IN({}) ".format(", ".join([dollar_quote(c) for c in categories])) if cursor == None else ""}    
    {"WHERE category IN({}) AND {} <= {}".format(", ".join([dollar_quote(c) for c in categories]), col_cursor, cursor) if cursor != None else ""}
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
    # rows = self.session.execute(CQL_QUERY)
    return [dict(row) for row in rows.all()]

  def insert_one(self, data: dict = None):
    if (data is None):
      raise "Please provide the insert data for Analysis Report!"
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    CQL_INSERT = """
    INSERT INTO analysis_report(datetime, category, analysis, url)
    VALUES (%(datetime)s, %(category)s, %(analysis)s, %(url)s)
    """
    # Execute
    future = self.session.execute_async(CQL_INSERT, data)
    try:
      result = future.result()
    except Exception as error:
      print("Operation failed!")
      print(error)
      return False
    return True

  def query_one_by_timestamp(self, key, category="wordcloud"):
    # Setup cassandra connection and query type
    self.session.row_factory = ordered_dict_factory
    # Check condition if sort
    # Query statement
    CQL_QUERY = f"""
    SELECT * 
    FROM {self.table}
    WHERE category = '{category}' AND datetime = '{key}'
    ;
    """
    rows = self.session.execute(CQL_QUERY)
    return [dict(row) for row in rows.all()]


def dollar_quote(string):
  return "$${}$$".format(string)

