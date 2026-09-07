import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.justeat.it/en/courier/form?city=genoa&page=city"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BIKE_WORDS = [
    "bike",
    "bicycle",
    "bicicletta",
    "own bike",
    "own bicycle",
]


def send_telegram(message):
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=20,
    ).raise_for_status()


def check_justeat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            viewport={"width": 1440, "height": 1000}
        )

        page.goto(URL, wait_until="networkidle", timeout=60000)

        body_text = page.locator("body").inner_text().lower()

        print("Current page:")
        print(page.url)
        print("----- PAGE TEXT -----")
        print(body_text[:6000])

        bike_found = any(word in body_text for word in BIKE_WORDS)

        browser.close()

        return bike_found


if __name__ == "__main__":
    try:
        available = check_justeat()

        if available:
            send_telegram(
                "🚨 JUST EAT GENOVA ALERT 🚲\n\n"
                "Bike / Bicycle appears to be available!\n\n"
                "Check the Just Eat rider application NOW:\n"
                "https://www.justeat.it/en/courier/form?city=genoa&page=city"
            )
        else:
            print("Bike option not found.")

    except Exception as e:
        print("ERROR:", e)
        raise
