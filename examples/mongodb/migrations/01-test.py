from pymongo import MongoClient

client = MongoClient()
db = client.my_db


def up():
    db.posts.insert_one(
        {
            "id": "post-1",
            "title": "We're live!",
            "content": "This is our first post, yay.",
        }
    )
    db.posts.create_index("id")


def down():
    db.posts.drop()
