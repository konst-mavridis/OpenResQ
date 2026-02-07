class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_user(self, uid):
        doc = self.db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None

    def create_user(self, user_data):
        uid = user_data["uid"]
        self.db.collection("users").document(uid).set(user_data)

    def update_user(self, uid, updates):
        self.db.collection("users").document(uid).update(updates)
