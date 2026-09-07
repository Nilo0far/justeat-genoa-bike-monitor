from playwright.sync_api import sync_playwright

URL = "https://www.justeat.it/en/courier/form?city=genoa&page=city"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1440, "height": 1000}
    )

    page.goto(URL, wait_until="networkidle", timeout=60000)

    print("PAGE URL:", page.url)

    print("\nPAGE TEXT:")
    print(page.locator("body").inner_text()[:8000])

    print("\nVEHICLE INPUT COUNT:")
    print(page.locator('input[name="vehicle_type"]').count())

    page.screenshot(
        path="justeat-debug.png",
        full_page=True
    )

    html = page.content()

    with open("justeat-debug.html", "w", encoding="utf-8") as f:
        f.write(html)

    browser.close()
