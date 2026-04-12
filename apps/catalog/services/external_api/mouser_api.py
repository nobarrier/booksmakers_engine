import requests
from django.conf import settings

MOUSER_API_KEY = getattr(settings, "MOUSER_API_KEY", "")

BASE_URL = "https://api.mouser.com/api/v1/search/keyword"


def search_mouser_products(keyword="Raspberry Pi"):
    if not MOUSER_API_KEY:
        raise RuntimeError("MOUSER_API_KEY missing")

    url = f"{BASE_URL}?apiKey={MOUSER_API_KEY}"

    payload = {
        "SearchByKeywordRequest": {
            "keyword": keyword,
            "records": 10,
            "startingRecord": 0,
            "searchOptions": "",
            "searchWithYourSignUpLanguage": "false",
        }
    }

    response = requests.post(url, json=payload)

    if response.status_code != 200:
        raise RuntimeError(
            f"Mouser search failed ({response.status_code}): {response.text}"
        )

    return response.json()


def normalize_mouser_products(data):
    products = []

    if not data:
        return products

    results = data.get("SearchResults")

    if not results:
        return products

    parts = results.get("Parts", [])

    for item in parts:
        manufacturer = item.get("Manufacturer")
        mpn = item.get("ManufacturerPartNumber")

        products.append(
            {
                "manufacturer": manufacturer,
                "mpn": mpn,
                "dk_part": mpn,
                "description": item.get("Description"),
                "price": None,
                "image": item.get("ImagePath"),
                "url": item.get("ProductDetailUrl"),
                "stock": None,
                "category_path": [],
            }
        )

    return products
