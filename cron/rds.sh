#!/bin/bash
PGPASSWORD=asdf1234 pgbench -i -F 90 -s 10000 -h $(aws rds describe-db-instances --db-instance-identifier cw-postgres --region ap-northeast-2 | grep -oP "cw[\w.-]+com") -U master postgres