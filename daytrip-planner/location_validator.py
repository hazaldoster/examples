import requests


def validate_city(city_name):
    """
    Validate that the input is a real city using a geocoding API.
    Returns True if valid, False otherwise.
    """
    try:
        # Using the OpenStreetMap Nominatim API (no API key required)
        # Be sure to add your app name/email for their terms of service
        url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json&limit=1"
        headers = {"User-Agent": "daytrip-planner-app"}

        response = requests.get(url, headers=headers)
        data = response.json()

        # Check if we got results and if the result is a city
        if (
            data
            and "city" in data[0].get("addresstype", "").lower()
            or "town" in data[0].get("addresstype", "").lower()
            and data[0].get("display_name", "").lower() == (city_name.lower())
        ):
            return True
        return False
    except Exception as e:
        print(f"Error validating city: {str(e)}")
        return False
