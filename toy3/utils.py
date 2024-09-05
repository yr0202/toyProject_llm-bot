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






