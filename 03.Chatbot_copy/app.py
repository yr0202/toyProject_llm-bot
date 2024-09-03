from flask import Flask, request, render_template, session
from dotenv import load_dotenv
import os
from openai import OpenAI
from database import get_db
from utils import (  # 유틸리티 함수들을 가져옵니다.
    make_prompt,
    extract_customer_name_email,
    get_user_by_name_email,
    get_purchases_by_user_id,
    get_purchases_with_items_by_user_id,
    extract_purchase_id,
    update_status_to_canceled
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

messages = []  # 채팅 내역을 저장하는 리스트

@app.route('/', methods=["GET", "POST"])
def index():
    db = next(get_db())
    bot_response = ""

    # 'messages' 리스트가 비어있으면 기본 환영 메시지를 추가
    if not messages:
        messages.append({
            'role': 'assistant',
            'content': '안녕하세요! CS봇입니다. 저와 대화를 지속하기 위해서는 로그인이 필요합니다.\n이름: 홍길동, 이메일: inseop@gmail.com\n위와 같은 형식으로 대화를 시작해 주세요!'
        })

    # 사용자가 이미 로그인한 상태인지 확인
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user_by_name_email(db, session['name'], session['email'])
        
        if request.method == 'POST':
            user_input = request.form['user_input']

            if '로그아웃해줘' in user_input:
                session.clear()  # 세션 초기화
                messages.clear()  # 대화 내역 초기화
                bot_response = "로그아웃되었습니다. 다시 로그인하려면 이름과 이메일을 입력해주세요."
                messages.append({
                    'role': 'assistant',
                    'content': '안녕하세요! CS봇입니다. 저와 대화를 지속하기 위해서는 로그인이 필요합니다.\n이름: 홍길동, 이메일: inseop@gmail.com\n위와 같은 형식으로 대화를 시작해 주세요!'
                })
            elif '구매내역' in user_input:
                purchases = get_purchases_with_items_by_user_id(db, user_id)
                
                if purchases:
                    purchase_detail = "\n".join(
                        [f"주문 ID: {row['purchase_id']}, 수량: {row['quality']}, 상태: {row['status']}, "
                         f"아이템 이름: {row['item_name']}, 가격: {row['item_price']}, 재고: {row['item_stock']}" 
                         for row in purchases]
                    )
                    bot_response = f"{user['name']}님의 주문 내역은 다음과 같습니다:\n{purchase_detail}"
                else:
                    bot_response = '주문 내역이 확인되지 않습니다.'

            elif '환불요청' in user_input:
                purchase_id = extract_purchase_id(user_input)
                purchases = get_purchases_by_user_id(db, user_id)

                purchase_to_cancel = None
                for p in purchases:
                    if p['id'] == purchase_id:
                        purchase_to_cancel = p
                        break

                if purchase_to_cancel:
                    update_status_to_canceled(db, purchase_id)
                    bot_response = f"{user['name']}님의 주문 ID {purchase_id}의 환불 요청이 처리되었습니다."
                else:
                    bot_response = '''
                    환불을 요청하시려면 "환불요청 주문 ID: [주문ID]"와 같은 형식으로 입력해 주세요.
                    예: 환불요청 주문 ID: 123
                    '''
            else: # 로그인을 진행한 사용자를 대상으로 일상 대화 진행이 가능하게끔.
                conversation = [
                    {"role": "system", "content": "You are a very kind and helpful shopping mall C/S assistant."},
                    {"role": "assistant", "content": "어떻게 도와드릴까요?"}
                ]
                conversation.extend([{"role": msg['role'], "content": msg['content']} for msg in messages])
                conversation.append({"role": "user", "content": user_input})

                bot_response = make_prompt(conversation)

            messages.append({'role': 'user', 'content': user_input})
            messages.append({'role': 'assistant', 'content': bot_response})
    else:
        if request.method == 'POST':
            user_input = request.form['user_input']
            name, email = extract_customer_name_email(user_input)
            
            if not name or not email:
                bot_response = "올바른 이름과 이메일을 제공해주세요."
            else:
                user = get_user_by_name_email(db, name, email)
                if user:
                    session['user_id'] = user['id']
                    session['name'] = user['name']
                    session['email'] = user['email']
                    bot_response = f"안녕하세요, {user['name']} 고객님! 어떤 도움이 필요하신가요? 제가 도와드릴 수 있는 것이 있으면 언제든지 말씀해주세요."
                else:
                    bot_response = "고객 정보를 찾을 수 없습니다. 올바른 이름과 이메일을 제공해주세요."

            messages.append({'role': 'user', 'content': user_input})
            messages.append({'role': 'assistant', 'content': bot_response})

    return render_template('index.html', messages=messages)

if __name__ == "__main__":
    app.run(debug=True)
