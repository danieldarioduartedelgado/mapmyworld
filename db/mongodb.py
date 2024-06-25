from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

def get_database():
    
    mongoclient = MongoClient(config["MONGODB_ATLAS_URI"])
    return mongoclient[config["DB_NAME"]]

get_database()
if __name__ == "__main__":
    dbname = get_database()
