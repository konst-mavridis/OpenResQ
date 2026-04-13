from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import os
import json
import base64

# Load environment variables from .env
load_dotenv()

# On Render, credentials should be in an environment variable
# or the service account file should be path-independent.
cred_json = os.getenv("FIREBASE_CREDENTIALS")
cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "openresq-b4c5f-firebase-adminsdk-fbsvc-b1b7042cba.json")

if cred_json:
    try:
        # Try parsing as JSON directly
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
    except Exception as e:
        try:
            # Try base64 decoding if JSON parsing fails
            decoded = base64.b64decode(cred_json).decode('utf-8')
            cred_dict = json.loads(decoded)
            cred = credentials.Certificate(cred_dict)
        except Exception as e2:
            print(f"Error parsing FIREBASE_CREDENTIALS: {e2}")
            exit(1)
elif os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
else:
    print("Error: No FIREBASE_CREDENTIALS env var or local JSON file found.")
    print(f"Looked for file at: {os.path.abspath(cred_path)}")
    exit(1)

try:
    initialize_app(cred)
except Exception:
    # app already initialized
    pass

db = firestore.client()

# Fetch all pending organizations
try:
    docs = db.collection("pending_organizations").get()
    print(f"\n--- Pending Organizations ({len(docs)} found) ---")
    if len(docs) == 0:
        print("No documents in collection.")
    for doc in docs:
        data = doc.to_dict()
        print(f"ID: {doc.id}")
        print(f"  Org: {data.get('org_name')}")
        print(f"  Email: {data.get('admin_email')}")
        print(f"  Status: {data.get('status')}")
        print("-" * 30)
except Exception as e:
    print(f"Error fetching documents: {e}")
