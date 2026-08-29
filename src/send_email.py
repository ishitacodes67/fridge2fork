import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_recipe_email(to_email, recipe_text, query):
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    subject = f"Your Recipe Recommendation: {query}"
    body = f"Here's your Fridge2Fork recommendation:\n\n{recipe_text}\n\nHappy cooking!"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_password)
            server.send_message(msg)
        print(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    test_recipe = "Pork Medallions - garlic, olive oil, rosemary, lemon juice, salt, black pepper"
    send_recipe_email("ishitakhatti5@gmail.com", test_recipe, "garlic, quick dinner")