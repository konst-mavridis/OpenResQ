import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

_initialized = False
_db = None
_bucket = None
_firebase_auth = None
_fcm = None

def initialize_firebase():
    global _initialized, _db, _bucket, _firebase_auth, _fcm

    if _initialized:
        return

    settings = get_settings()
    creds_dict = settings.get_firebase_credentials()
    cred = credentials.Certificate(creds_dict)

    firebase_admin.initialize_app(cred, {
        'storageBucket': "openresq-b4c5f.firebasestorage.app"
    })

    _db = firestore.client()
    _bucket = storage.bucket()
    _firebase_auth = auth
    _fcm = messaging

    _initialized = True
    logger.info("Firebase initialized successfully")

def get_db():
    if not _initialized:
        initialize_firebase()
    return _db

def get_auth():
    if not _initialized:
        initialize_firebase()
    return _firebase_auth

def get_storage():
    if not _initialized:
        initialize_firebase()
    return _bucket

# Export db for backward compatibility
db = get_db()

def get_fcm():
    if not _initialized:
        initialize_firebase()
    return _fcm

# Export fcm for backward compatibility
fcm = get_fcm()
