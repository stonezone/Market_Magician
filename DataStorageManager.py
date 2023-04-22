# DataStorageManager.py

import os
import zlib
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
import redis
from neo4j import GraphDatabase
from jsonschema import validate
from cryptography.fernet import Fernet

# Load API keys and credentials from environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

class DataStorageManager:

    def __init__(self):
        self.mongo_client = MongoClient(MONGO_URI)
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        self.neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.fernet = Fernet(SECRET_KEY)

    def __del__(self):
        self.mongo_client.close()
        self.neo4j_driver.close()

    # MongoDB data operations
    def insert_data_mongo(self, db_name, collection_name, data):
        db = self.mongo_client[db_name]
        collection = db[collection_name]
        result = collection.insert_one(data)
        return result.inserted_id

    def query_data_mongo(self, db_name, collection_name, query):
        db = self.mongo_client[db_name]
        collection = db[collection_name]
        return list(collection.find(query))

    # Redis data operations
    def cache_data_redis(self, key, value, expiration_time=None):
        compressed_value = zlib.compress(value.encode())
        self.redis_client.set(key, compressed_value, ex=expiration_time)

    def get_cached_data_redis(self, key):
        compressed_value = self.redis_client.get(key)
        return zlib.decompress(compressed_value).decode() if compressed_value else None

    # Neo4j data operations
    def insert_data_neo4j(self, query, parameters=None):
        with self.neo4j_driver.session() as session:
            return session.write_transaction(lambda tx: tx.run(query, parameters))

    def query_data_neo4j(self, query, parameters=None):
        with self.neo4j_driver.session() as session:
            return session.read_transaction(lambda tx: list(tx.run(query, parameters)))

    # Data validation and schema enforcement
    def validate_data(self, schema, data):
        try:
            validate(instance=data, schema=schema)
            return True
        except Exception as e:
            print(f"Data validation failed: {e}")
            return False

    # Encryption and decryption
    def encrypt_data(self, data):
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt_data(self, encrypted_data):
        return self.fernet.decrypt(encrypted_data.encode()).decode()

# Example usage
if __name__ == "__main__":
    data_storage_manager = DataStorageManager()
    # Examples of how to use the new features and methods
