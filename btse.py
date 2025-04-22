import requests
import os

telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

def send_message_to_telegram(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, data={'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'})
    if response.status_code != 200:
        print(f"Error sending message to Telegram: {response.status_code} - {response.text}")
    else:
        print("Message sent successfully!")

send_message_to_telegram("Test message", telegram_token, chat_id)
