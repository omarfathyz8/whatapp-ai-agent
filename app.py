from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import smtplib
import threading
import time
import os

app = Flask(__name__)

# --- Configuration ---
EMAIL = "your_email@gmail.com"
PASSWORD = "your_app_password"
RECEIVER_EMAIL = "receiver_email@example.com"

# --- Global State ---
chat_log = []
last_message_time = time.time()
chat_timeout = 60  # seconds of inactivity before sending email

# --- Rule-Based Bot Function ---
def generate_reply(message):
    message = message.lower()
    if "hello" in message or "hi" in message:
        return "Hi there! How can I help you today?"
    elif "price" in message:
        return "Our product prices vary. Please let me know which item you're interested in."
    elif "thanks" in message or "thank you" in message:
        return "You're welcome! Let me know if you have more questions."
    elif "bye" in message:
        return "Goodbye! Have a great day."
    else:
        return "Thanks for your message! A representative will get back to you soon."

# --- Email Function ---
def send_email(subject, body):
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            msg = f"Subject: {subject}\n\n{body}"
            server.sendmail(EMAIL, RECEIVER_EMAIL, msg)
            print("✅ Email sent.")
    except Exception as e:
        print(f"❌ Email error: {e}")

# --- Chat Monitor ---
def monitor_chat():
    global chat_log
    while True:
        time.sleep(10)
        if chat_log and (time.time() - last_message_time > chat_timeout):
            email_body = "\n".join(chat_log)
            send_email("WhatsApp Chat Summary", email_body)
            chat_log = []  # Reset chat
            print("📧 Chat ended and summary sent.")

# Start monitor in background
threading.Thread(target=monitor_chat, daemon=True).start()

# --- Webhook Endpoint ---
@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    global last_message_time

    incoming_msg = request.form.get("Body")
    from_number = request.form.get("From")

    print(f"📨 Message from {from_number}: {incoming_msg}")
    chat_log.append(f"User: {incoming_msg}")
    last_message_time = time.time()

    reply = generate_reply(incoming_msg)
    chat_log.append(f"Bot: {reply}")

    resp = MessagingResponse()
    msg = resp.message()
    msg.body(reply)
    return str(resp)

# --- Run Server ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
