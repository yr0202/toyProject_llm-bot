# 요청이 들어왔을 때 처리하는 곳
# 데이터 받으면 뿌려주는 역할
# routes에서는 디비 연동하는 함수를 호출만 한다.
from flask import Flask, request, abort, jsonify
from database import get_db
import crud

def register_routes(app: Flask):
    @app.route('/items', methods=['POST'])
    def create_item_route():
        db = next(get_db()) # db 연결
        data = request.get_json() # 유저가 보낸 데이터
        print("유저가 보낸 데이터 : ", data)

        new_item = crud.create_item(db, data['name'], data['price'], data['stock']) # circular import
        return jsonify({
            'id':new_item.id,
            'name':new_item.name,
            'price':new_item.price,
            'stock':new_item.stock,
            'created_at':new_item.created_at.isoformat() #isoformat()은 datetime 객체를 ISO 8601 형식의 문자열로 변환하는 메서드
        }), 201 # 201 : 생성 완료 됐다

    # 신입 => REST API => 서비스단 보다는 관리자 페이지단 (6개월 -> 유저 endpoint)
    @app.route('/items/<int:item_id>', methods=['GET'])
    def get_item_route(item_id):
        db = next(get_db())
        item = crud.get_item(db, item_id)

        if item is None:
            abort(404)

        return jsonify({
            'id':item.id,
            'name':item.name,
            'price':item.price,
            'stock':item.stock,
            'created_at':item.created_at.isoformat()
        }), 200
    
    @app.route('/items', methods=['GET'])
    def get_all_items_route():
        db = next(get_db())
        items = crud.get_all_items(db)

        return jsonify([{
            'id':new_item.id,
            'name':new_item.name,
            'price':new_item.price,
            'stock':new_item.stock,
            'created_at':new_item.created_at.isoformat()
        } for new_item in items]), 201

    @app.route('/items/<int:item_id>', methods=['PUT'])
    def update_item_route(item_id):
        db = next(get_db())
        data = request.get_json()

        updated_item = crud.update_item(
            db=db,
            item_id=item_id,
            name=data['name'],
            price=data['price'],
            stock=data['stock']
        )

        if updated_item is None:
            abort(404)

        return {"message":f"Successfully updated item (Item ID: {item_id})"}

    @app.route('/items/<int:item_id>', methods=['DELETE'])
    def delete_item_route(item_id):
        db = next(get_db())
        deleted_item =crud.delete_item(db=db, item_id=item_id)

        if deleted_item is None:
            abort(404)

        return {"message":f"Successfully deleted item (Item ID: {item_id})"}
    

# 프로젝트 : 
# - 챗봇에게 정보를 줄 때 크롤링 + 쇼핑몰 - 마케팅 툴 (카피라이팅 작성해주는)