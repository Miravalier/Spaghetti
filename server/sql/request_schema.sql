DROP TABLE IF EXISTS requests;
CREATE TABLE requests (
    creation_time       timestamp,
    from_id             integer,
    to_id               integer,
    amount              numeric,

    request_id serial PRIMARY KEY
);
