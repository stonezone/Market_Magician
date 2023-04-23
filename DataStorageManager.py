import pymongo
from pymongo import MongoClient
import logging
import os
import shutil

class DataStorageManager:
    def __init__(self, database_name):
        self.database_name = database_name
        self.backup_path = "database_backup"
        self.logger = self.setup_logger()
        self.setup_backup_folder()

        try:
            self.client = MongoClient()
            self.db = self.client[self.database_name]
            self.logger.info(f"Connected to database: {self.database_name}")
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {self.database_name}. Error: {e}")
            raise

    def setup_logger(self):
        logger = logging.getLogger("DataStorageManager")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Set up file handler for logging
        file_handler = logging.FileHandler("data_storage_manager.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Set up console handler for logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def setup_backup_folder(self):
        if not os.path.exists(self.backup_path):
            os.makedirs(self.backup_path)
            self.logger.info(f"Created backup folder at {self.backup_path}")

    def insert_data(self, collection_name, data):
        try:
            collection = self.db[collection_name]
            result = collection.insert_one(data)
            self.logger.info(f"Inserted data into {collection_name}: {result.inserted_id}")
        except Exception as e:
            self.logger.error(f"Failed to insert data into {collection_name}. Error: {e}")
            raise

    def update_data(self, collection_name, query, new_data):
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": new_data})
            self.logger.info(f"Updated data in {collection_name}: {result.modified_count} document(s) modified")
        except Exception as e:
            self.logger.error(f"Failed to update data in {collection_name}. Error: {e}")
            raise

    def query_data(self, collection_name, query, projection=None):
        try:
            collection = self.db[collection_name]
            result = collection.find(query, projection)
            self.logger.info(f"Queried data from {collection_name}: {result.count()} document(s) returned")
            return list(result)
        except Exception as e:
            self.logger.error(f"Failed to query data from {collection_name}. Error: {e}")
            raise
    def backup_database(self):
        backup_folder = os.path.join(self.backup_path, self.database_name)
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        try:
            os.system(f"mongodump --db {self.database_name} --out {self.backup_path}")
            self.logger.info(f"Successfully backed up {self.database_name} to {self.backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to backup database {self.database_name}. Error: {e}")
            raise
    def delete_data(self, collection_name, query):
        try:
            collection = self.db[collection_name]
            result = collection.delete_one(query)
            self.logger.info(f"Deleted data from {collection_name}: {result.deleted_count} document(s) deleted")
        except Exception as e:
            self.logger.error(f"Failed to delete data from {collection_name}. Error: {e}")
            raise

    def restore_database(self):
        backup_folder = os.path.join(self.backup_path, self.database_name)
        if os.path.exists(backup_folder):
            try:
                os.system(f"mongorestore --db {self.database_name} {backup_folder}")
                self.logger.info(f"Successfully restored {self.database_name} from {self.backup_path}")
            except Exception as e:
                self.logger.error(f"Failed to restore database {self.database_name}. Error: {e}")
                self.logger.error(f"Failed to restore database {self.database_name}. Error: {e}")
            raise
        else:
            self.logger.error(f"Backup folder for {self.database_name} not found in {self.backup_path}")

    def drop_collection(self, collection_name):
        try:
            collection = self.db[collection_name]
            collection.drop()
            self.logger.info(f"Dropped collection {collection_name} from {self.database_name}")
        except Exception as e:
            self.logger.error(f"Failed to drop collection {collection_name} from {self.database_name}. Error: {e}")
            raise

if __name__ == "__main__":
    data_storage_manager = DataStorageManager("test_db")

    # Insert data
    data_storage_manager.insert_data("test_collection", {"symbol": "AAPL", "price": 100})

    # Update data
    data_storage_manager.update_data("test_collection", {"symbol": "AAPL"}, {"price": 101})

    # Query data
    data = data_storage_manager.query_data("test_collection", {"symbol": "AAPL"})
    print(data)

    # Delete data
    data_storage_manager.delete_data("test_collection", {"symbol": "AAPL"})

    # Backup database
    data_storage_manager.backup_database()

    # Restore database
    data_storage_manager.restore_database()

    # Drop collection
    data_storage_manager.drop_collection("test_collection")
                