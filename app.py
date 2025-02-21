from flask import Flask
import os

webz = Flask(__name__)

@webz.route('/')
def home():
    return "Telegram File Sharing Bot is Running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Render assigns a PORT variable
    webz.run(host="0.0.0.0", port=port)
