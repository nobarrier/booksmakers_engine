import requests
from django.conf import settings

CLIENT_ID = (settings.DIGIKEY_CLIENT_ID or "").strip()
CLIENT_SECRET = (settings.DIGIKEY_CLIENT_SECRET or "").strip()
ENV = (settings.DIGIKEY_ENV or "production").lower().strip()

if ENV == "sandbox":
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"


def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("DIGIKEY_CLIENT_ID / DIGIKEY_CLIENT_SECRET missing")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(
        TOKEN_URL,
        headers=headers,
        data=data,
        timeout=20,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"DigiKey token request failed ({response.status_code}): {response.text}"
        )

    return response.json()["access_token"]
