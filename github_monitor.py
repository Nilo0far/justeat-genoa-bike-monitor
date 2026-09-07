import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo


URL = "https://www.justeat.it/en/courier/form?city=genoa&page=city"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

# Vehicle types we want to monitor
BIKE_OPTIONS = [
    "Driver Bike",
    "Driver E-Bike",
    "Company Bike",
    "Company E-Bike",
]


def send_telegram(message):
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": message,
        },
        timeout=20,
    )

    response.raise_for_status()


def extract_json_object(text, start_pos):
    depth = 0
    in_string = False
    escaped = False

    for i in range(start_pos, len(text)):
        ch = text[i]

        if in_string:
            if escaped:
                escaped = False

            elif ch == "\\":
                escaped = True

            elif ch == '"':
                in_string = False

            continue

        if ch == '"':
            in_string = True

        elif ch == "{":
            depth += 1

        elif ch == "}":
            depth -= 1

            if depth == 0:
                return text[start_pos:i + 1]

    raise RuntimeError(
        "Could not extract JSON object."
    )


def get_genoa_vehicle_options():

    response = requests.get(
        URL,
        headers={
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 "
                "Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        timeout=30,
    )

    response.raise_for_status()

    html = response.text

    # Find the JSON data inside the page
    marker = "window.language = "

    marker_pos = html.find(marker)

    if marker_pos == -1:
        raise RuntimeError(
            "Could not find window.language."
        )

    json_start = marker_pos + len(marker)

    language_json_text = extract_json_object(
        html,
        json_start
    )

    language_data = json.loads(
        language_json_text
    )

    # Find Genoa
    cities = language_data.get(
        "city_options",
        []
    )

    genoa = next(
        (
            city
            for city in cities
            if city.get("id") == 592
            or city.get("slug") == "genoa"
        ),
        None,
    )

    if genoa is None:
        raise RuntimeError(
            "Could not find Genoa."
        )

    # Find vehicle selection
    vehicle_question = None

    for item in genoa.get(
        "form_questions",
        []
    ):

        form_question = item.get(
            "form_question",
            {}
        )

        if (
            form_question.get("data_key")
            == "vehicle_type"
        ):
            vehicle_question = item
            break

    if vehicle_question is None:
        raise RuntimeError(
            "Could not find Vehicle Selection "
            "for Genoa."
        )

    options = vehicle_question.get(
        "options"
    )

    if not isinstance(options, dict):
        raise RuntimeError(
            "Vehicle options are invalid."
        )

    return options


# ==========================================
# START
# ==========================================

print("======================================")
print("Just Eat Genoa GitHub Monitor")
print("======================================")

# Current time in Italy
rome_now = datetime.now(
    ZoneInfo("Europe/Rome")
)

print(
    f"[{rome_now.strftime('%Y-%m-%d %H:%M:%S')}] "
    "Checking Just Eat..."
)

# ==========================================
# MONITORING HOURS
# 08:00 -> 19:59 Italy time
# ==========================================

if not (8 <= rome_now.hour < 20):

    print()
    print(
        "Outside monitoring hours."
    )

    print(
        "Rome time:",
        rome_now.strftime("%H:%M:%S")
    )

    print(
        "No request sent to Just Eat."
    )

    raise SystemExit(0)


# ==========================================
# CHECK JUST EAT
# ==========================================

options = get_genoa_vehicle_options()

print()
print("Genoa vehicle status:")

for name, enabled in options.items():

    status = (
        "AVAILABLE"
        if enabled
        else "not available"
    )

    print(
        f"- {name}: {status}"
    )


# ==========================================
# CHECK BIKE / E-BIKE
# ==========================================

enabled_bikes = [
    name
    for name in BIKE_OPTIONS
    if options.get(name, False)
]


# ==========================================
# SEND TELEGRAM ALERT
# ==========================================

if enabled_bikes:

    print()
    print("BIKE FOUND!")

    bike_list = "\n".join(
        f"✅ {name}"
        for name in enabled_bikes
    )

    send_telegram(
        "🚨 JUST EAT GENOVA ALERT 🚲\n\n"
        "BIKE / E-BIKE IS AVAILABLE!\n\n"
        f"{bike_list}\n\n"
        "Check Just Eat NOW:\n"
        "https://www.justeat.it/en/courier/"
        "form?city=genoa&page=city"
    )

    print(
        "Telegram alert sent!"
    )

else:

    print()
    print(
        "Bike is currently NOT available."
    )

    print(
        "No Telegram message sent."
    )


print()
print("Check completed.")
