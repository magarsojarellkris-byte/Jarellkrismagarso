
import requests

API_URL = "https://jarellkrismagarso.onrender.com"

try:
    response = requests.get(API_URL, timeout=60)
    response.raise_for_status()

    data = response.json()
    print("API Response:", data)
    print("Message:", data["message"])
    print("Status:", data["status"])

except requests.exceptions.RequestException as e:
    print("Request Error:", e)
except ValueError as e:
    print("JSON Error:", e)
