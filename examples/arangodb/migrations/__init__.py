from arango import ArangoClient
from migrate_anything import configure, ArangoDBStorage

client = ArangoClient(hosts="https://example.com:8529/")
db = client.db(name="my_db", username="root", password="supersecret")

configure(storage=ArangoDBStorage(collection="migrations", db=db))
