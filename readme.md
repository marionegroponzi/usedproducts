# README - usedproduct

## Goal
Scan [usedproducts.nl](usedproducts.nl) and collect all products in a local mongodb for fun.

Longer term the idea is to make some analysis, price trends and maybe notifications when sepcific products become cheap.

### venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
deactivate

### Notes
See mongodump and mongorestore to backup the db
E.g.:
`mongodump --archive=usedproducts.mongodb.gz --db=usedproducts --gzip`

### Authentication
With mongosh create admin user 
```
use admin
db.createUser(
  {
    user: "myUserAdmin",
    pwd: passwordPrompt(), // or cleartext password
    roles: [ { role: "userAdminAnyDatabase", db: "admin" }, "readWriteAnyDatabase" ]
  }
)
```

Enable auth in the service
File location: `/opt/homebrew/etc/mongod.conf` (from [here](https://www.mongodb.com/docs/manual/reference/configuration-options/))
Add
```
security:
    authorization: enabled
```

Restart
brew services restart mongodb-community

With mongosh create user (read or read-write)
```
db.createUser({user:"user_name",pwd:"password",roles:[{role:"read", db:"db_name"}]})
db.createUser({user:"user_name",pwd:"password",roles:[{role:"readWrite", db:"db_name"}]})
```


Login via mongosh
mongosh localhost:27017/usedproducts -u usedproducts



