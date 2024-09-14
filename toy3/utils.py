import re
from openai import OpenAI
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

### 새로만든 함수
def get_inquiry_by_user_name_email(db, name, email):
    # user_info에서 id를 먼저 가져옴
    user_query = """
        SELECT userID
        FROM user_info
        WHERE name = :name AND email = :email
    """
    user_result = db.execute(text(user_query), {"name": name, "email": email}).fetchone()
    if user_result:
        user_id = user_result[0]  # 사용자 id를 가져옴 (튜플 인덱스 접근)
        # board 테이블에서 writer가 user_id와 일치하는 content 가져오기
        board_query = """
            SELECT content
            FROM board
            WHERE writer = :user_id
        """
        board_result = db.execute(text(board_query), {"user_id": user_id}).fetchall()
        if board_result:
            return [row[0] for row in board_result]  # 튜플의 첫 번째 값(content)을 리스트로 반환
        else:
            return None  # 글이 없으면 None 반환
    else:
        return None  # 사용자 정보가 없으면 None 반환

# GPT 모델을 이용해 여러 공지사항 요약 생성
def summarize_notice(contents):
    conversation = [
        {"role": "system", "content": "You are a useful assistant to summarize notifications for users in Korean. Your summaries should not exceed 300 characters."}
    ]

    # 각 공지사항에 대해 별도의 message를 추가
    for content in contents:
        conversation.append({"role": "user", "content": content})

    # GPT를 사용해 요약된 응답 생성
    response = client.chat.completions.create(
        model='gpt-4',
        messages=conversation,
        max_tokens=130,  # 필요한 경우, max_tokens 조정 가능
        temperature=0.7
    )

    return response.choices[0].message.content


# 키워드를 사용해 공지사항 검색
def search_notices_by_keyword(db, keyword):
    query = text("""
        SELECT title, content 
        FROM notice 
        WHERE title LIKE :keyword
        OR content LIKE :keyword
    """)
    
    keyword_with_wildcards = f"%{keyword}%"
    results = db.execute(query, {"keyword": keyword_with_wildcards}).fetchall()
    
    # 검색 결과 반환 (딕셔너리 형태로 변환)
    return [dict(row._mapping) for row in results]

# 사용자 입력에서 키워드를 추출하는 함수
def extract_keyword(user_input):
    # 간단한 패턴을 이용해 질문에서 중요한 단어를 추출
    # 예시: "교환 방법이 궁금해"에서 "교환"을 추출
    keyword_pattern = r"\b[가-힣]+\b"  # 한글 단어 패턴 (필요에 따라 영어 등 추가 가능)
    keywords = re.findall(keyword_pattern, user_input)

    # 예시에서는 첫 번째 단어를 키워드로 사용
    if keywords:
        return keywords[0]  # 첫 번째 단어 반환
    return None


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



def search_notices_by_keyword(db, keyword):
    # 키워드가 title 또는 content에 포함된 공지사항을 조회하는 쿼리
    query = text("""
        SELECT title, content 
        FROM Notice
        WHERE title LIKE :keyword
        OR content LIKE :keyword
    """)
    
    # 와일드카드를 추가하여 부분 일치 검색을 위한 설정
    keyword_with_wildcards = f"%{keyword}%"
    
    # 쿼리 실행
    results = db.execute(query, {"keyword": keyword_with_wildcards}).fetchall()
    
    # 결과를 딕셔너리 리스트로 변환
    return [dict(row._mapping) for row in results]

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
    query = "SELECT * FROM member WHERE name = :name AND email = :email"
    print(f"쿼리 실행: {query} | 파라미터: name={name}, email={email}")
    result = db.execute(text(query), {"name": name, "email": email}).fetchone()
    if result:
        print(f"사용자 찾음: {result}")
        return dict(result._mapping)
    print("사용자를 찾지 못했습니다.")
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
