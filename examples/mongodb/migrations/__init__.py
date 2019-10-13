from migrate_anything import configure, MongoDBStorage
import pymongo

db = pymongo.MongoClient().test_db

configure(storage=MongoDBStorage(db.migrations))
