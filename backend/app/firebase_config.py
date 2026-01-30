"""
Firebase initialization and configuration.
All credentials are loaded from environment variables.
"""
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

_initialized = False
db = None
bucket = None
firebase_auth = None
fcm = None


def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials from environment."""
    global _initialized, db, bucket, firebase_auth, fcm
    
    if _initialized:
        return
    
    try:
        settings = get_settings()
        
        # Load credentials from environment variable
        creds_dict = settings.get_firebase_credentials()
        cred = credentials.Certificate(creds_dict)
        
        # Initialize Firebase app
        firebase_admin.initialize_app(cred, {
            'storageBucket': "openresq-b4c5f.firebasestorage.app"
        })
        
        # Initialize services
        db = firestore.client()
        bucket = storage.bucket()
        firebase_auth = auth
        fcm = messaging
        
        _initialized = True
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        raise


def get_db():
    """Get Firestore client instance."""
    if not _initialized:
        initialize_firebase()
    return db


def get_auth():
    """Get Firebase Auth instance."""
    if not _initialized:
        initialize_firebase()
    return firebase_auth


def get_storage():
    """Get Firebase Storage bucket."""
    if not _initialized:
        initialize_firebase()
    return bucket


def get_fcm():
    """Get Firebase Cloud Messaging instance."""
    if not _initialized:
        initialize_firebase()
    return fcm
