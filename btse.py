import requests

# Telegram bot information
telegram_token = "7873650895:AAFGndHjZQFOjxGKOawDgaUSj8OoryVZuJo"
chat_id = "315381350"

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

# Fetching the list of all futures prices
markets_url = "https://api.btse.com/futures/api/v2.1/price"
market_summary_url = "https://api.btse.com/futures/api/v2.1/market_summary"
response = requests.get(markets_url)
summary_response = requests.get(market_summary_url)

if response.status_code == 200 and summary_response.status_code == 200:
    data = response.json()
    summary_data = summary_response.json()
    print(f"Received price data: {data}")
    print(f"Received summary data: {summary_data}")

    result_table = []

    # Create a dictionary for quick lookup of fundingRate and percentageChange
    summary_dict = {item.get('symbol'): item for item in summary_data if item.get('symbol')}

    if isinstance(data, list):
        for item in data:
            symbol = item.get('symbol')
            last = item.get('lastPrice') or 0
            index = item.get('indexPrice') or 0
            mark = item.get('markPrice') or 0

            # Fetch fundingRate and percentageChange from summary data
            summary_item = summary_dict.get(symbol, {})
            funding = summary_item.get('fundingRate', 0)  # Use actual fundingRate or default to 0
            change_24h = summary_item.get('percentageChange', 0)  # Use actual percentageChange or default to 0

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
            if abs(change_24h) > 50:
                warnings.append("🚨 24h Change > ±50%")
            if idx_diff > 1 or mark_diff > 1:
                warnings.append("⚠️ Large price difference detected (>1%)")

            funding_color = f"{funding * 100:.3f}%"
            change_24h_str = f"{change_24h:.2f}%"

            result_table.append([
                symbol, index, mark, last, funding_color,
                ", ".join(warnings),
                round(abs(last - index), 2),
                round(abs(last - mark), 2),
                round(idx_diff, 2),
                round(mark_diff, 2),
                change_24h_str
            ])

        headers = [
            "Symbol", "Index Price", "Mark Price", "Futures Price",
            "Funding Rate", "Warnings", "Index Diff",
            "Mark Diff", "Index % Diff", "Mark % Diff", "Change 24h"
        ]

        table_text = "BTSE\n\n"  # Adding BTSE at the top
        table_text += "| " + " | ".join(headers) + " |\n"
        table_text += "|--------|-------------|------------|---------------|--------------|----------|------------|-----------|---------------|-------------|-------------|\n"
        
        for row in result_table:
            table_text += "| " + " | ".join([str(cell) for cell in row]) + " |\n"

        print(table_text)
        send_message_to_telegram(table_text, telegram_token, chat_id)

    else:
        print("Invalid response format or empty data.")
else:
    print(f"Price API Error: {response.status_code} - {response.text}")
    print(f"Summary API Error: {summary_response.status_code} - {summary_response.text}")
