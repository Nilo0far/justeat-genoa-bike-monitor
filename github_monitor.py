name: Just Eat Genoa Bike Monitor

on:
  workflow_dispatch:

  schedule:
    - cron: "*/5 * * * *"

jobs:
  check-bike:
    runs-on: ubuntu-latest
    timeout-minutes: 3

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install requests
        run: pip install requests

      - name: Check Genoa bike availability
        env:
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python github_monitor.py
