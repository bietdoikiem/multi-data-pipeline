CREATE TABLE IF NOT EXISTS fakerdata (
  username TEXT,
  name TEXT,
  address TEXT,
  year INT,
  company TEXT,
  email TEXT,
  job TEXT,
  phone_number TEXT,
  license_plate TEXT,
  image_url TEXT,
  PRIMARY KEY (username, email)
);

CREATE TABLE IF NOT EXISTS cryptopanic_news (
  kind TEXT,
  source_title TEXT,
  source_domain TEXT, 
  title TEXT,
  published_at TIMESTAMP,
  url TEXT,
  PRIMARY KEY ((kind), published_at, url)
) WITH CLUSTERING ORDER BY (published_at DESC) ;

CREATE TABLE IF NOT EXISTS kraken_tick_data (
  datetime TIMESTAMP,
  ask_value DOUBLE,
  ask_volume DOUBLE,
  bid_value DOUBLE,
  bid_volume DOUBLE,
  closed_value DOUBLE,
  closed_volume DOUBLE,
  pair TEXT,
  PRIMARY KEY(pair, datetime)
)
WITH CLUSTERING ORDER BY (datetime DESC);