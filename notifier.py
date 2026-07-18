import json
import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SEARCH_URL = "https://www.cars24.com/buy-used-skoda-slavia-cars-bangalore/"
SEEN_FILE = "seen.json"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )


def load_seen():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r") as f:
        return set(json.load(f))


def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(sorted(list(seen)), f, indent=2)


def get_listings():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 Chrome/137 Safari/537.36"
        )
    }

    r = requests.get(SEARCH_URL, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    listings = []

    # Collect every Cars24 listing link
    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/buy-used-" not in href:
            continue

        if "slavia" not in href.lower():
            continue

        if href.startswith("/"):
            href = "https://www.cars24.com" + href

        title = a.get_text(" ", strip=True)

        listings.append(
            {
                "id": href,
                "title": title if title else "Skoda Slavia",
                "url": href,
            }
        )

    # Remove duplicates
    unique = {}
    for x in listings:
        unique[x["id"]] = x

    return list(unique.values())


def main():
    seen = load_seen()

    listings = get_listings()

    print(f"Found {len(listings)} listings")

    new = []

    for listing in listings:
        if listing["id"] not in seen:
            new.append(listing)
            seen.add(listing["id"])

    for listing in new:
        send_telegram(
            f"🚗 New Skoda Slavia listed!\n\n"
            f"{listing['title']}\n\n"
            f"{listing['url']}"
        )

    save_seen(seen)

    print(f"New listings: {len(new)}")


if __name__ == "__main__":
    main()