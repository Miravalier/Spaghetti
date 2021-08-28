#!/bin/bash
sudo mkdir -p /var/spaghetti
sudo sqlite3 /var/spaghetti/db ".read sql/account_schema.sql"
sudo sqlite3 /var/spaghetti/db ".read sql/request_schema.sql"
sudo sqlite3 /var/spaghetti/db ".read sql/transaction_schema.sql"
sudo sqlite3 /var/spaghetti/db ".read sql/user_schema.sql"
