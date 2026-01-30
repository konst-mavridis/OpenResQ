import requests

AI_BASE_URL = "http://localhost:8001"  # localhost: AI microservice

def predict_fire(image_url: str) -> float:
    try:
        response = requests.post(f"{AI_BASE_URL}/fire/validate", json={"image_url": image_url})
        response.raise_for_status()
        data = response.json()
        return data.get("fire_probability", 0.0)
    except Exception:
        return 0.0
