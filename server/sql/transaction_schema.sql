DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_time    timestamp,
    from_id             integer,
    to_id               integer,
    amount              numeric,

    transaction_id serial PRIMARY KEY
);
