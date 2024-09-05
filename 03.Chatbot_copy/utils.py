import re
from openai import OpenAI
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def make_prompt(conversation):
    res = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=conversation,
        max_tokens=150,
        temperature=0.7,
        top_p=0.9,
        frequency_penalty=0.0,
        presence_penalty=0.6
    )
    return res.choices[0].message.content

def extract_customer_name_email(input_text):
    name_pattern = r"이름:\s*([가-힣]{2,4})"
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    name_match = re.search(name_pattern, input_text)
    email_match = re.search(email_pattern, input_text)

    name = name_match.group(1) if name_match else None
    email = email_match.group(0) if email_match else None

    print('유저정보', name, email)

    return name, email

def get_user_by_name_email(db, name, email):
    query = "SELECT * FROM users WHERE name = :name AND email = :email"
    result = db.execute(text(query), {"name": name, "email": email}).fetchone()
    if result:
        return dict(result._mapping)
    return None

def get_purchases_by_user_id(db, user_id):
    query = text("SELECT * FROM purchases WHERE user_id = :user_id")
    results = db.execute(query, {'user_id': user_id}).fetchall()
    return [dict(row._mapping) for row in results]

def get_purchases_with_items_by_user_id(db, user_id):
    query = text("""
        SELECT p.id AS purchase_id, p.quality, p.status, p.purchase_date, 
               i.name AS item_name, i.price AS item_price, i.stock AS item_stock 
        FROM purchases p
        JOIN items i ON p.item_id = i.id
        WHERE p.user_id = :user_id
    """)
    results = db.execute(query, {"user_id": user_id}).fetchall()
    return [dict(row._mapping) for row in results]

def extract_purchase_id(input_text):
    id_pattern = r"주문\s*ID\s*:\s*(\d+)"
    match = re.search(id_pattern, input_text)
    return int(match.group(1)) if match else None

def update_status_to_canceled(db, purchase_id):
    try:
        query = text("UPDATE purchases SET status = 'canceled' WHERE id = :id")
        db.execute(query, {'id': purchase_id})
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating status to canceled: {e}")
