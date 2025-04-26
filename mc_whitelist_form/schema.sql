DROP TABLE IF EXISTS requests;

CREATE TABLE requests (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  secret TEXT NOT NULL,
  mail TEXT NOT NULL,
  username TEXT NOT NULL,
  request_date INTEGER NOT NULL,
  accept_date INTEGER
);
