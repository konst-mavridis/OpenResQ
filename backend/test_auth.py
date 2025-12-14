import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# ---------------------------
# 1️⃣ Register User
# ---------------------------
def register_user(email, password, display_name):
    data = {"email": email, "password": password, "display_name": display_name}
    r = requests.post(f"{BASE_URL}/auth/register", json=data)
    print("Register:", r.status_code, r.json())
    return r.json().get("uid")

# ---------------------------
# 2️⃣ Set Role (admin only)
# ---------------------------
def set_role(admin_token, uid, role):
    headers = {"Authorization": f"Bearer {admin_token}"}
    r = requests.post(f"{BASE_URL}/auth/set-role/{uid}/{role}", headers=headers)
    print("Set Role:", r.status_code, r.json())

# ---------------------------
# 3️⃣ Create Report
# ---------------------------
def create_report(token, title, description, lat, lng):
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "title": title,
        "description": description,
        "location": {"lat": lat, "lng": lng},
        "media": []
    }
    r = requests.post(f"{BASE_URL}/reports/", json=data, headers=headers)
    print("Create Report:", r.status_code, r.json())
    return r.json().get("report_id")

# ---------------------------
# 4️⃣ Get Report
# ---------------------------
def get_report(token, report_id):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/reports/{report_id}", headers=headers)
    print("Get Report:", r.status_code, r.json())

# ---------------------------
# 5️⃣ List Reports (Responder/Admin)
# ---------------------------
def list_reports(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{BASE_URL}/reports/", headers=headers)
    print("List Reports:", r.status_code)
    for report in r.json():
        print(report)

# ---------------------------
# Example Usage
# ---------------------------
if __name__ == "__main__":
    # 1. Register a new citizen
    citizen_email = "citizen@example.com"
    citizen_password = "password123"
    citizen_display = "Citizen One"
    citizen_uid = register_user(citizen_email, citizen_password, citizen_display)

    # 2. Register admin manually in Firebase (or use existing) and get ID token
    admin_token = "<ADMIN_FIREBASE_ID_TOKEN>"  # π.χ. από Firebase client SDK ή REST API

    # 3. Promote citizen to responder (test role update)
    # set_role(admin_token, citizen_uid, "responder")

    # 4. Create a report
    # token = "<FIREBASE_ID_TOKEN_OF_CITIZEN>"
    # report_id = create_report(token, "Tree down", "Fallen tree on main road", 37.9838, 23.7275)

    # 5. Get the report
    # get_report(token, report_id)

    # 6. List all reports (responder/admin)
    # list_reports(admin_token)
