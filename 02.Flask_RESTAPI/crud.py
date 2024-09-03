# 실제 디비랑 소통하는 역할
from sqlalchemy.orm import Session
from models import Item
from datetime import datetime

def create_item(db: Session, name:str, price:int, stock:int):
    new_item = Item(name=name, price=price, stock=stock, created_at = datetime.now())
    db.add(new_item)
    db.commit()

    return new_item

def get_item(db: Session, item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()

    return item

def get_all_items(db: Session):
    items = db.query(Item).all()

    return items

def update_item(db: Session, item_id: int, name:str=None, price:int=None, stock:int=None):
    item = get_item(db, item_id)

    if item is None:
        return None
    
    if name is not None:
        item.name = name
    if price is not None:
        item.price = price
    if stock is not None:
        item.stock = stock

    db.commit()
    return item
    
def delete_item(db: Session, item_id: int):
    item = get_item(db, item_id)

    db.delete(item)
    db.commit()

    return item

# +Django는 더쉽다.

# + Authentication => JWT Auth
# AWS Lambda (Serverless 백엔드 구축 가능)
# 백엔드에 자바를 왜 써요? 전자정부프레임워크라서?
# - 속도. => 세상의 기기 자체들의 속도는 계속 빨라지고 있습니다.
# 옛날에는 코드를 예술로 짜는게 중요했는데, 지금은 덜 중요 => 기기성능이 좋으니까.
# 파이썬 느린단 말이에요. 컴퓨팅 파워가 좋아지다보니깐 => 쓸만한데?