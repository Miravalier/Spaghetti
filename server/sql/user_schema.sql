DROP TABLE IF EXISTS users;
CREATE TABLE users (
    google_id   text,
    email       text,
    user_name   text,

    user_id serial PRIMARY KEY
);
