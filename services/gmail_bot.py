# import yagmail
# import imaplib
# import email
# import requests

# # ====== Gmail credentials ======
# GMAIL_USER = "rajatgoswami7333@gmail.com"
# GMAIL_APP_PASSWORD = "ktrl ffpx nemb jybr"

# # ====== LLM endpoint ======
# FASTAPI_URL = "http://127.0.0.1:8000/generate/text"

# # ====== Initialize yagmail client ======
# yag = yagmail.SMTP(user=GMAIL_USER, password=GMAIL_APP_PASSWORD)


# # ---------- Send email ----------
# def send_email(to_email: str, subject: str, body: str):
#     try:
#         yag.send(to=to_email, subject=subject, contents=body)
#         print(f"✅ Email sent to {to_email}")
#         return True
#     except Exception as e:
#         print("❌ Error sending email:", e)
#         return False


# # ---------- Read unread emails ----------
# # ---------- Read unread emails (limit 50) ----------
# # ---------- Read unread emails (limit 50) ----------
# def read_unread_emails(limit=2):
#     import imaplib
#     import email

#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(GMAIL_USER, GMAIL_APP_PASSWORD)
#     mail.select("inbox")

#     status, response = mail.search(None, 'UNSEEN')
#     email_ids = response[0].split()

#     # Limit number of emails
#     email_ids = email_ids[:limit]

#     emails = []

#     for e_id in email_ids:
#         status, msg_data = mail.fetch(e_id, "(RFC822)")
#         for response_part in msg_data:
#             if isinstance(response_part, tuple):
#                 msg = email.message_from_bytes(response_part[1])
#                 subject = msg["subject"]
#                 from_email = msg["from"]
#                 body = ""

#                 if msg.is_multipart():
#                     for part in msg.walk():
#                         if part.get_content_type() == "text/plain":
#                             raw_bytes = part.get_payload(decode=True)
#                             body = raw_bytes.decode('utf-8', errors='replace')
#                             break  # take first text/plain part
#                 else:
#                     raw_bytes = msg.get_payload(decode=True)
#                     body = raw_bytes.decode('utf-8', errors='replace')

#                 emails.append({
#                     "id": e_id,  # keep ID if needed later
#                     "from": from_email,
#                     "subject": subject,
#                     "body": body
#                 })

#         # Mark email as read
#         mail.store(e_id, '+FLAGS', '\\Seen')

#     mail.logout()
#     return emails

# # ---------- Summarize email using PulseNova LLM ----------
# def summarize_email(email_body: str):
#     try:
#         response = requests.post(
#             FASTAPI_URL,
#             json={"prompt": f"Summarize this email in a concise, friendly way:\n\n{email_body}"}
#         )
#         assistant_text = response.json()["response"]
#         return assistant_text
#     except Exception as e:
#         print("❌ Error summarizing email:", e)
#         return None


# # ---------- Quick test ----------
# if __name__ == "__main__":
#     # Read unread emails
#     unread = read_unread_emails(limit=2)
#     print(f"Found {len(unread)} unread emails.")

#     for e in unread:
#         print("From:", e["from"])
#         print("Subject:", e["subject"])
#         print("Original Body:", e["body"])
#         summary = summarize_email(e["body"])
#         print("PulseNova Summary:", summary)
#         print("-" * 50)






        # gmail_bot_clean.py
import imaplib
import email
from email.header import decode_header
import html2text
import requests
import os
from dotenv import load_dotenv
import yagmail


load_dotenv()

USERNAME = os.getenv("GMAIL_USER")
PASSWORD = os.getenv("GMAIL_APP_PASSWORD")



IMAP_SERVER = "imap.gmail.com"
EMAIL_LIMIT = 2

def clean_subject(subject):
    decoded = decode_header(subject)
    subject_str = ""
    for part, enc in decoded:
        if isinstance(part, bytes):
            subject_str += part.decode(enc if enc else "utf-8", errors='replace')
        else:
            subject_str += part
    return subject_str

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body = part.get_payload(decode=True).decode(errors='replace')
                break
        if not body:
            for part in msg.walk():
                if part.get_content_type() == "text/html":
                    html_body = part.get_payload(decode=True).decode(errors='replace')
                    body = html2text.html2text(html_body)
                    break
    else:
        if msg.get_content_type() == "text/plain":
            body = msg.get_payload(decode=True).decode(errors='replace')
        elif msg.get_content_type() == "text/html":
            html_body = msg.get_payload(decode=True).decode(errors='replace')
            body = html2text.html2text(html_body)
    return body.strip()

# ✅ Real summarizer using PulseNova LLM
def summarize_email(body: str):
    response = requests.post(
        "http://127.0.0.1:8000/generate/text",
        json={"prompt": f"Summarize this email concisely and friendly:\n\n{body}"}
    )
    return response.json()["response"]

def read_unread_emails(limit=EMAIL_LIMIT):
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(USERNAME, PASSWORD)
    mail.select("inbox")
    status, messages = mail.search(None, '(UNSEEN)')
    email_ids = messages[0].split()[:limit]

    results = []
    for e_id in email_ids:
        _, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                sender = msg.get("From")
                subject = clean_subject(msg.get("Subject"))
                body = get_email_body(msg)
                summary = summarize_email(body)  # ✅ LLM summarizes here
                results.append({
                    "from": sender,
                    "subject": subject,
                    "body": body[:500],
                    "summary": summary
                })

    mail.logout()
    return results

def compose_email_with_llm(intention: str):
    response = requests.post(
        "http://127.0.0.1:8000/generate/text",
        json={"prompt": f"""Write an email based on this instruction:
'{intention}'

Rules:
- Match the tone exactly
- Do NOT add anything not mentioned
- Do NOT invent content, links, or signatures
- If instruction is empty or unclear, return empty string
- Return ONLY the email body, nothing else"""}
    )
    return response.json()["response"]



def send_email(to: str, subject: str, body_intention: str):
    
    # ✅ If body is empty, don't call LLM — send empty email
    if not body_intention or body_intention.strip() == "":
        professional_body = ""
    else:
        professional_body = compose_email_with_llm(body_intention)
    
    yag = yagmail.SMTP(user=USERNAME, password=PASSWORD)
    yag.send(to=to, subject=subject, contents=professional_body)
    
    return {
        "status": "sent",
        "to": to,
        "subject": subject,
        "body_sent": professional_body
    }