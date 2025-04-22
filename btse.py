import requests
import os
from tabulate import tabulate

# Telegram bot information (read from environment variables)
telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

def send_message_to_telegram(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    max_length = 4096
    if len(message) > max_length:
        parts = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        for part in parts:
            response = requests.post(url, data={'chat_id': chat_id, 'text': part, 'parse_mode': 'Markdown'})
            if response.status_code != 200:
                print(f"Error sending message to Telegram: {response.status_code}")
    else:
        response = requests.post(url, data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'})
        if response.status_code != 200:
            print(f"Error sending message to Telegram: {response.status_code}")

# Fetching the list of all futures markets
markets_url = "https://api.btse.com/futures/api/v2/market_summary"
response = requests.get(markets_url)

if response.status_code == 200:
    data = response.json()
    print(f"Received data: {data}")

    result_table = []

    if isinstance(data, list):
        for item in data:
            symbol = item.get('symbol')
            last = item.get('last') or 0
            index = item.get('lowestAsk') or 0
            mark = item.get('highestBid') or 0
            funding = item.get('fundingRate') or 0
            volume = item.get('volume') or 0

            def percent_diff(a, b):
                return abs(a - b) / b * 100 if b else 0

            idx_diff = percent_diff(last, index)
            mark_diff = percent_diff(last, mark)

            warnings = []
            if idx_diff > 1:
                warnings.append("⚠️ Index diff > 1%")
            if mark_diff > 1:
                warnings.append("⚠️ Mark diff > 1%")
            if abs(funding) > 0.01:
                warnings.append("⚠️ Funding > ±1%")
            if idx_diff > 1 or mark_diff > 1:
                warnings.append("⚠️ Large price difference detected (>1%)")

            funding_color = f"{funding * 100:.3f}%"

            result_table.append([
                symbol, index, mark, last, funding_color,
                ", ".join(warnings), f"{volume:,.0f}",
                round(abs(last - index), 2),
                round(abs(last - mark), 2),
                round(idx_diff, 2),
                round(mark_diff, 2)
            ])

        headers = [
            "Symbol", "Index Price", "Mark Price", "Futures Price",
            "Funding Rate", "Warnings", "Volume (24h)",
            "Index Diff", "Mark Diff", "Index % Diff", "Mark % Diff"
        ]

        table_text = "| " + " | ".join(headers) + " |\n"
        table_text += "|--------|-------------|------------|---------------|--------------|----------|--------------|------------|-----------|---------------|-------------|\n"

        for row in result_table:
            table_text += "| " + " | ".join([str(cell) for cell in row]) + " |\n"

        print(table_text)
        send_message_to_telegram(table_text, telegram_token, chat_id)

    else:
        print("Invalid response format or empty data.")
else:
    print(f"Error: {response.status_code} - {response.text}")
