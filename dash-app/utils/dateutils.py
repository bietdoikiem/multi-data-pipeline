from datetime import datetime


def format_ms_time(dt: datetime):
  s = dt.strftime('%Y-%m-%d %H:%M:%S.%f')
  return s[:-3]