#!/bin/bash
curl -X PUT \
    -H "Content-Type: application/json" \
    -d '{"idtoken": "debug_id_token"}' \
    https://spaghetti.miramontes.dev/authstatus
