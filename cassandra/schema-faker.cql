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