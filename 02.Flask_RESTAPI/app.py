from flask import Flask, request
from routes import register_routes

app = Flask(__name__) # 서버 구축
register_routes(app)

@app.route('/')
def index():
    return {"Hello":"Flask!"}

# 간단한 API 만들기
@app.route('/api/v1/feeds', methods=['GET']) # REST API : [GET] /api/v1/feeds
def show_all_feeds():
    data = {'result':'success','data':{'feed1':'data1','feed2':'data2'}}
    # 데이터 타입 : 파이썬 Dict => 브라우저가 이해할 수 없다

    return data # jsonify : dictionary 타입을 json으로 바꿔주는 로직이 숨어있다

@app.route('/api/v1/feeds/<int:feed_id>', methods=['GET'])
def show_one_feed(feed_id):
    data = {'result':'success','data':f'feed ID: {feed_id}'}
    return data


# java : request(요청) => flask python 
@app.route('/api/v1/feeds', methods=['POST'])
def create_feed():
    email = request.form['email']
    content = request.form['content']

    data = {'result':'success', 'data':{'email':email,'content':content}}

    return data


if __name__ == "__main__":
    app.run()