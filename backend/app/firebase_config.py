import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, messaging

cred = credentials.Certificate("C:\\Users\\user\\Desktop\\OpenResQ\\backend\\openresq-b4c5f-firebase-adminsdk-fbsvc-b1b7042cba.json")

firebase_admin.initialize_app(cred, {
    'storageBucket': 'gs://openresq-b4c5f.firebasestorage.app'
})

db = firestore.client()
bucket = storage.bucket()   
firebase_auth = auth
fcm = messaging
