# README - usedproduct

## Goal
Scan [usedproducts.nl](usedproducts.nl) and collect all products in a local mongodb for fun.

Longer term the idea is to make some analysis, price trends and maybe notifications when sepcific products become cheap.

### Notes
See mongodump and mongorestore to backup the db
E.g.:
`mongodump --archive=usedproducts.mongodb.gz --db=usedproducts --gzip`