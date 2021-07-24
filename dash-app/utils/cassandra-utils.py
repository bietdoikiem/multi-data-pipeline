import os
import re
import sys
import pandas as pd
# pylint: disable=no-name-in-module
from cassandra.cluster import Cluster
# pylint: disable=no-name-in-module
from cassandra.query import dict_factory

CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get(
    "CASSANDRA_HOST") else "cassandradb"
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get(
    "CASSANDRA_KEYSPACE") else "kafkapipeline"
KRAKEN_TABLE = os.environ.get("KRAKEN_TABLE")


def getKrakenData():
  return getDF(KRAKEN_TABLE)


def getDF(source_table):
  if (isinstance(CASSANDRA_HOST, list)):
    cluster = Cluster(CASSANDRA_HOST)
  else:
    cluster = Cluster([CASSANDRA_HOST])

  session = cluster.connect(CASSANDRA_KEYSPACE)
  session.row_factory = dict_factory
  cqlquery = f"SELECT * FROM {source_table};"
  rows = session.execute(cqlquery)
  return pd.DataFrame(rows)
