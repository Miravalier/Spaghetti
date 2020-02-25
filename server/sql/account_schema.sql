DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    account_uuid    text,
    account_name    text,
    account_balance numeric,
    account_type    integer,
    user_id         integer,
    update_time     timestamp,

    account_id serial PRIMARY KEY
);
