from firebase_config import auth

user = auth.create_user(
    email="test@example.com",
    password="mypassword123",
    display_name="John Doe",
)

print("User created:", user.uid)
