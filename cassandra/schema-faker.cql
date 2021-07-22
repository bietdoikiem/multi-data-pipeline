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
  PRIMARY KEY (title, source_domain, url)
);