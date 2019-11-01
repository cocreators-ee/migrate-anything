from arango import ArangoClient

client = ArangoClient(hosts="https://example.com:8529/")
db = client.db(name="my_db", username="root", password="supersecret")


def up():
    collection = db.create_collection("test_collection")
    collection.insert({"foo": "bar"})


def down():
    db.delete_collection("test_collection")
