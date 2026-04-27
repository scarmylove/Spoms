from pymongo import MongoClient, ASCENDING, DESCENDING  # type: ignore
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure  # type: ignore
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class MongoDatabase:
    _client = None
    _db = None
    
    @classmethod
    def get_connection(cls):
        """Get or create MongoDB connection"""
        if cls._client is None:
            try:
                mongo_uri = os.environ.get('MONGODB_URI')
                if not mongo_uri:
                    raise ValueError("MONGODB_URI environment variable not set")
                
                cls._client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                # Verify connection
                cls._client.admin.command('ping')
                cls._db = cls._client['spoms']
                logger.info("MongoDB connection established")
                cls._create_indexes()
            except (ServerSelectionTimeoutError, ConnectionFailure) as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        
        return cls._db
    
    @classmethod
    def _create_indexes(cls):
        """Create database indexes for better query performance"""
        try:
            db = cls._db
            
            # Users indexes
            db['users'].create_index([('username', ASCENDING)], unique=True)
            db['users'].create_index([('name', ASCENDING)])
            
            # Suppliers indexes
            db['suppliers'].create_index([('name', ASCENDING)])
            db['suppliers'].create_index([('status', ASCENDING)])
            
            # Orders indexes
            db['orders'].create_index([('po_number', ASCENDING)])
            db['orders'].create_index([('status', ASCENDING)])
            db['orders'].create_index([('supplier', ASCENDING)])
            
            # Payments indexes
            db['payments'].create_index([('id', ASCENDING)])
            db['payments'].create_index([('status', ASCENDING)])
            db['payments'].create_index([('po_number', ASCENDING)])
            
            # Feedback indexes
            db['feedback'].create_index([('date', DESCENDING)])
            
            logger.info("Database indexes created")
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")


# Database operation functions
def get_db():
    """Get database instance"""
    return MongoDatabase.get_connection()


def load_collection(collection_name):
    """Load all documents from a collection"""
    try:
        db = get_db()
        return list(db[collection_name].find({}, {'_id': 0}))
    except Exception as e:
        logger.error(f"Error loading {collection_name}: {e}")
        return []


def save_document(collection_name, data):
    """Insert a single document"""
    try:
        db = get_db()
        result = db[collection_name].insert_one(data)
        return result.inserted_id
    except Exception as e:
        logger.error(f"Error saving to {collection_name}: {e}")
        raise


def find_document(collection_name, query):
    """Find a single document"""
    try:
        db = get_db()
        doc = db[collection_name].find_one(query, {'_id': 0})
        return doc
    except Exception as e:
        logger.error(f"Error finding document in {collection_name}: {e}")
        return None


def update_document(collection_name, query, data):
    """Update a single document"""
    try:
        db = get_db()
        result = db[collection_name].update_one(query, {'$set': data})
        return result.modified_count
    except Exception as e:
        logger.error(f"Error updating {collection_name}: {e}")
        raise


def delete_document(collection_name, query):
    """Delete a single document"""
    try:
        db = get_db()
        result = db[collection_name].delete_one(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting from {collection_name}: {e}")
        raise


def delete_document(collection_name, query):
    """Delete a single document"""
    try:
        db = get_db()
        result = db[collection_name].delete_one(query)
        return result.deleted_count
    except Exception as e:
        logger.error(f"Error deleting from {collection_name}: {e}")
        raise


def find_document(collection_name, query):
    """Find a single document"""
    try:
        db = get_db()
        doc = db[collection_name].find_one(query, {'_id': 0})
        return doc
    except Exception as e:
        logger.error(f"Error finding in {collection_name}: {e}")
        return None


def find_documents(collection_name, query):
    """Find multiple documents"""
    try:
        db = get_db()
        return list(db[collection_name].find(query, {'_id': 0}))
    except Exception as e:
        logger.error(f"Error finding in {collection_name}: {e}")
        return []


def collection_exists_and_has_data(collection_name):
    """Check if collection exists and has data"""
    try:
        db = get_db()
        return db[collection_name].count_documents({}) > 0
    except Exception as e:
        logger.error(f"Error checking {collection_name}: {e}")
        return False
