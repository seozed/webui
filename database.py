from pymongo import MongoClient



def get_mongodb(settings=None):
    if settings is None:
        import settings
    client = MongoClient()
    db = client[settings.MONGODB_DB]
    return db