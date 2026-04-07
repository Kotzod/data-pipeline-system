import requests
from pathlib import Path

URL = 'https://www.tampere.fi/ajankohtaista/uutiset.xml'

BASE_DIR = Path(__file__).resolve().parent
FILE = BASE_DIR / "data.xml"

def fetch_url(URL):
        response = requests.get(URL)
        response.raise_for_status()  # Raise an error for bad responses

        with open(FILE, "wb") as f:
            f.write(response.content)

        print(f"RSS feed downloaded and saved to {FILE}")

if __name__ == "__main__":
    fetch_url(URL)