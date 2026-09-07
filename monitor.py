import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://www.justeat.it/en/courier/form?city=genoa&page=city"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

BIKE_WORDS = [
    "bike",
    "e-bike",
    "bicycle",
    "bicicletta",
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

        vehicle_inputs = page.locator('input[name="vehicle_type"]')

        vehicles = []

        for i in range(vehicle_inputs.count()):
            el = vehicle_inputs.nth(i)

            value = (el.get_attribute("value") or "").strip().lower()

            label_text = el.locator("xpath=ancestor::label").inner_text().strip().lower()

            vehicles.append({
                "value": value,
                "label": label_text
            })

        print("Vehicle options found:")

        for vehicle in vehicles:
            print(
                f"- value={vehicle['value']} | label={vehicle['label']}"
            )

        bike_found = any(
            any(
                word in vehicle["value"]
                or word in vehicle["label"]
                for word in BIKE_WORDS
            )
            for vehicle in vehicles
        )

        browser.close()

        return bike_found


if __name__ == "__main__":
    try:
        available = check_justeat()

        if available:
            send_telegram(
                "🚨 JUST EAT GENOVA ALERT 🚲\n\n"
                "Bike / E-bike option is AVAILABLE!\n\n"
                "Apply now:\n"
                "https://www.justeat.it/en/courier/form?city=genoa&page=city"
            )
        else:
            print("Bike option NOT found.")

    except Exception as e:
        print("ERROR:", e)
        raise
