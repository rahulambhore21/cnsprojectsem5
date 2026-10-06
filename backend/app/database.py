import logging
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.database import Database
from app.config import settings

logger = logging.getLogger("ulpf.database")

_client: MongoClient | None = None
_db: Database | None = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        try:
            _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=3000)
            # Test connection
            _client.admin.command('ping')
            logger.info("Connected to MongoDB successfully at %s", settings.MONGODB_URI)
        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            raise e
    return _client

def get_database() -> Database:
    global _db
    if _db is None:
        client = get_client()
        _db = client[settings.DATABASE_NAME]
    return _db

def init_indexes():
    """Ensure database collections have optimal indexes."""
    try:
        db = get_database()
        
        # Events indexes
        events = db["events"]
        events.create_index([("event_id", ASCENDING)], unique=True)
        events.create_index([("timestamp", DESCENDING)])
        events.create_index([("source.vendor", ASCENDING)])
        events.create_index([("source.format", ASCENDING)])
        events.create_index([("event.action", ASCENDING)])
        events.create_index([("event.severity", ASCENDING)])
        events.create_index([("integrity.sha256", ASCENDING)])
        events.create_index([("network.source_ip", ASCENDING)])
        events.create_index([("network.destination_ip", ASCENDING)])
        
        # Parsers indexes
        parsers = db["parsers"]
        parsers.create_index([("parser_id", ASCENDING)], unique=True)
        parsers.create_index([("name", ASCENDING)])
        parsers.create_index([("vendor", ASCENDING)])
        
        # Sources indexes
        sources = db["sources"]
        sources.create_index([("source_id", ASCENDING)], unique=True)
        sources.create_index([("vendor", ASCENDING)])
        
        # Audit logs indexes
        audit_logs = db["audit_logs"]
        audit_logs.create_index([("timestamp", DESCENDING)])
        
        logger.info("MongoDB indexes successfully verified.")
    except Exception as e:
        logger.warning("Could not initialize MongoDB indexes (will retry on next request): %s", e)

def close_client():
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed.")
