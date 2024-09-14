from flask import Flask, request, render_template, session, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI
from database import get_db
from utils import (
    search_notices_by_keyword, summarize_notice,extract_keyword,
    make_prompt,
    extract_customer_name_email,
    get_user_by_name_email,
    get_purchases_by_user_id,
    get_purchases_with_items_by_user_id,
    extract_purchase_id,
    update_status_to_canceled,
)

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

messages = []  # 채팅 내역을 저장하는 리스트


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
    update_status_to_canceled,
    get_inquiry_by_user_name_email  # 추가된 함수
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

messages = []  # 채팅 내역을 저장하는 리스트

from flask import Flask, request, render_template, session, jsonify
from dotenv import load_dotenv
import os
from openai import OpenAI
from database import get_db
from utils import (
    search_notices_by_keyword, summarize_notice, extract_keyword,
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

            elif '1:1문의' in user_input:
                inquiry_link = "http://localhost:8080/toy2/board/list"
                bot_response = f'1:1 문의를 원하시면 다음의 링크를 클릭해주세요: <a href="{inquiry_link}" target="_blank">여기를 클릭</a>'

            elif '내 글 보여줘' in user_input:
                inquiries = get_inquiry_by_user_name_email(db, session['name'], session['email'])
                if inquiries:
                    inquiry_list = "\n".join(inquiries)
                    bot_response = f"{session['name']}님이 작성한 글은 다음과 같습니다:\n{inquiry_list}"
                else:
                    bot_response = f"{session['name']}님이 작성한 글이 없거나, 등록된 사용자가 없습니다."

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
            else:  # 일반 대화 처리 및 공지사항 처리
                # 사용자가 입력한 질문에서 키워드 추출
                keyword = extract_keyword(user_input)

                # 데이터베이스에서 키워드와 일치하는 공지사항 검색
                notices = search_notices_by_keyword(db, keyword)

                if notices:
                    # 모든 공지사항의 내용을 리스트로 모아서 GPT에게 요약 요청
                    notice_contents = [notice['content'] for notice in notices]
                    bot_response = summarize_notice(notice_contents)
                else:
                    # 일반 대화 처리
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
                # 로그인 시 세션을 강제로 초기화
                session.clear()  # 기존 세션 정보 초기화
                user = get_user_by_name_email(db, name, email)
                if user:
                    session['user_id'] = user['userID']
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




# @app.route('/', methods=["GET", "POST"])
# def index():
#     db = next(get_db())
#     bot_response = ""

#     # 초기 환영 메시지 설정
#     if not messages:
#         messages.append({
#             'role': 'assistant',
#             'content': '안녕하세요! CS봇입니다. 궁금하신 사항을 말씀해주세요.'
#         })

#     if request.method == 'POST':
#         user_input = request.form['user_input']
        
#         # 사용자가 입력한 질문에서 키워드 추출
#         keyword = extract_keyword(user_input)

#         # 데이터베이스에서 키워드와 일치하는 공지사항 검색
#         notices = search_notices_by_keyword(db, keyword)

#         if notices:
#             # 모든 공지사항의 내용을 리스트로 모아서 GPT에게 요약 요청
#             notice_contents = [notice['content'] for notice in notices]
#             bot_response = summarize_notice(notice_contents)
#         else:
#             bot_response = "관련된 공지사항을 찾을 수 없습니다."

#         # 대화 내역 업데이트
#         messages.append({'role': 'user', 'content': user_input})
#         messages.append({'role': 'assistant', 'content': bot_response})

#     return render_template('index.html', messages=messages)




# if __name__ == "__main__":
#     app.run(debug=True)




# @app.route('/', methods=["GET", "POST"])
# def index():
#     db = next(get_db())
#     bot_response = ""
    
#     # If the messages list is empty, start with a default greeting
#     if not messages:
#         messages.append({
#             'role': 'assistant',
#             'content': '안녕하세요! CS봇입니다. 필요하신 사항을 말씀해주세요!'
#         })

#     if request.method == 'POST':
#         user_input = request.form['user_input']
        
#         # Handle specific case for '상품' keyword
#         if '상품' == user_input:
#             product = get_product(db)
#             if product:
#                 # Create a table structure for the product list
#                 product_detail = "<table border='1' style='border-collapse: collapse;'>"
#                 product_detail += "<tr><th>상품 ID</th><th>이름</th><th>가격</th></tr>"  # Table headers

#                 # Fill the table with product data
#                 for row in product:
#                     product_detail += (
#                         f"<tr><td>{row['productID']}</td>"
#                         f"<td>{row['productName']}</td>"
#                         f"<td>{row['salePrice']}원</td></tr>"
#                     )
                
#                 product_detail += "</table>"  # Close the table
                
#                 # Create a bot response with the product list table
#                 bot_response = (
#                     "<b>상품 목록은 다음과 같습니다:</b><br><br>"
#                     f"{product_detail}"  # Insert the formatted table
#                 )
#             else:
#                 bot_response = "상품 목록을 불러올 수 없습니다."
#         elif '상품별점' == user_input:
#             product = get_product(db)
#             if product:
#                 # Create a table structure for the product list
#                 product_detail = "<table border='1' style='border-collapse: collapse;'>"
#                 product_detail += "<tr><th>상품 ID</th><th>이름</th><th>가격</th></tr>"  # Table headers

#                 # Fill the table with product data
#                 for row in product:
#                     product_detail += (
#                         f"<tr><td>{row['productID']}</td>"
#                         f"<td>{row['productName']}</td>"
#                         f"<td>{row['salePrice']}원</td></tr>"
#                     )
                
#                 product_detail += "</table>"  # Close the table
                
#                 # Create a bot response with the product list table
#                 bot_response = (
#                     "<b>상품 목록은 다음과 같습니다:</b><br><br>"
#                     f"{product_detail}"  # Insert the formatted table
#                 )
#             else:
#                 bot_response = "상품 목록을 불러올 수 없습니다."
        
#         # Handle '상품목록페이지' keyword
#         elif '상품목록' == user_input:
#             inquiry_link = "http://localhost:8080/toy2/product/list"
#             bot_response = f'상품목록 페이지를 원하시면 다음의 링크를 클릭해주세요: <a href="{inquiry_link}" target="_blank">여기를 클릭</a>'
#         elif '회원가입' == user_input:
#             inquiry_link = "http://localhost:8080/toy2/signup"
#             bot_response = f'회원가입 페이지를 원하시면 다음의 링크를 클릭해주세요: <a href="{inquiry_link}" target="_blank">여기를 클릭</a>'
#         elif '로그인' == user_input:
#             inquiry_link = "http://localhost:8080/toy2/login"
#             bot_response = f'로그인 페이지를 원하시면 다음의 링크를 클릭해주세요: <a href="{inquiry_link}" target="_blank">여기를 클릭</a>'
#         # Handle general conversation
#         else:
#             conversation = [
#                 {"role": "system", "content": "You are a very kind and helpful mall C/S assistant, and additionally a smart assistant who gives you weather information or your fortune for the day."},
#                 {"role": "assistant", "content": "어떻게 도와드릴까요?"}
#             ]
#             # Extend conversation history
#             conversation.extend([{"role": msg['role'], "content": msg['content']} for msg in messages])
#             conversation.append({"role": "user", "content": user_input})

#             # Generate a bot response based on conversation
#             bot_response = make_prompt(conversation)
        
#         # Append the user input and bot response to the message history
#         messages.append({'role': 'user', 'content': user_input})
#         messages.append({'role': 'assistant', 'content': bot_response})    
    
#     # Render the index.html template with messages
#     return render_template('index.html', messages=messages)

# if __name__ == "__main__":
#     app.run(debug=True)



# @app.route('/', methods=["GET", "POST"])
# def index():
#     db = next(get_db())
#     bot_response = "" # 챗봇의 응답을 저장할 변수

#     # 'messages' 리스트가 비어있으면 기본 환영 메시지를 추가
#     if not messages:
#         messages.append({
#             'role': 'assistant', # 어떤 역할을 가질 것인지 정의
#             'content': '안녕하세요! CS봇입니다. 저와 대화를 지속하기 위해서는 로그인이 필요합니다.\n이름: 홍길동, 이메일: inseop@gmail.com\n위와 같은 형식으로 대화를 시작해 주세요!'
#         })

#     # 사용자가 이미 로그인한 상태인지 확인
#     if 'user_id' in session:
#         user_id = session['user_id']
#         user = get_user_by_name_email(db, session['name'], session['email'])
        
#         if request.method == 'POST':
#             user_input = request.form['user_input']

#             if '로그아웃해줘' in user_input:
#                 session.clear()  # 세션 초기화
#                 messages.clear()  # 대화 내역 초기화
#                 bot_response = "로그아웃되었습니다. 다시 로그인하려면 이름과 이메일을 입력해주세요."
#                 messages.append({
#                     'role': 'assistant',
#                     'content': '안녕하세요! CS봇입니다. 저와 대화를 지속하기 위해서는 로그인이 필요합니다.\n이름: 홍길동, 이메일: inseop@gmail.com\n위와 같은 형식으로 대화를 시작해 주세요!'
#                 })
#             elif '구매내역' in user_input:
#                 purchases = get_purchases_with_items_by_user_id(db, user_id)
                
#                 if purchases:
#                     purchase_detail = "\n".join(
#                         [f"주문 ID: {row['purchase_id']}, 수량: {row['quality']}, 상태: {row['status']}, "
#                          f"아이템 이름: {row['item_name']}, 가격: {row['item_price']}, 재고: {row['item_stock']}" 
#                          for row in purchases]
#                     )
#                     bot_response = f"{user['name']}님의 주문 내역은 다음과 같습니다:\n{purchase_detail}"
#                 else:
#                     bot_response = '주문 내역이 확인되지 않습니다.'

#             elif '환불요청' in user_input:
#                 purchase_id = extract_purchase_id(user_input)
#                 purchases = get_purchases_by_user_id(db, user_id)

#                 purchase_to_cancel = None
#                 for p in purchases:
#                     if p['id'] == purchase_id:
#                         purchase_to_cancel = p
#                         break

#                 if purchase_to_cancel:
#                     update_status_to_canceled(db, purchase_id)
#                     bot_response = f"{user['name']}님의 주문 ID {purchase_id}의 환불 요청이 처리되었습니다."
#                 else:
#                     bot_response = '''
#                     환불을 요청하시려면 "환불요청 주문 ID: [주문ID]"와 같은 형식으로 입력해 주세요.
#                     예: 환불요청 주문 ID: 123
#                     '''
#             else: # 로그인을 진행한 사용자를 대상으로 일상 대화 진행이 가능하게끔.
#                 conversation = [
#                     {"role": "system", "content": "You are a very kind and helpful shopping mall C/S assistant."},
#                     {"role": "assistant", "content": "어떻게 도와드릴까요?"}
#                 ]
#                 conversation.extend([{"role": msg['role'], "content": msg['content']} for msg in messages])
#                 conversation.append({"role": "user", "content": user_input})

#                 bot_response = make_prompt(conversation)

#             messages.append({'role': 'user', 'content': user_input})
#             messages.append({'role': 'assistant', 'content': bot_response})
#     else: # 로그인 안함
#         if request.method == 'POST':
#             bot_response = "비회원 관련 채팅만 가능합니다."
#             else:
#                 user = get_user_by_name_email(db, name, email)
#                 if user:
#                     session['user_id'] = user['id']
#                     session['name'] = user['name']
#                     session['email'] = user['email']
#                     bot_response = f"안녕하세요, {user['name']} 고객님! 어떤 도움이 필요하신가요? 제가 도와드릴 수 있는 것이 있으면 언제든지 말씀해주세요."
#                 else:
#                     bot_response = "고객 정보를 찾을 수 없습니다. 올바른 이름과 이메일을 제공해주세요."

#             messages.append({'role': 'user', 'content': user_input})
#             messages.append({'role': 'assistant', 'content': bot_response})

#     return render_template('index.html', messages=messages)


# if __name__ == "__main__":
#     app.run(debug=True)