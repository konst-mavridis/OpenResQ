import firebase_admin
from firebase_admin import credentials, firestore, auth

cred = credentials.Certificate("C:\\users\\biket\\desktop\\OpenResQ\\backend\\openresq-b4c5f-firebase-adminsdk-fbsvc-b1b7042cba.json")

firebase_admin.initialize_app(cred)

db = firestore.client()
