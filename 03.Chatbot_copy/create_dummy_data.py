from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from models import Base, User, Purchase, Item

# ORM 방식 데이터를 처리해주고 있다. => MySQL - SQL로도 가능하다.
engine = create_engine("sqlite:///./test.db")
Session = sessionmaker(bind=engine)
session = Session()

# 예제 데이터 추가
item1 = Item(name="삼성노트북", price=10000, stock=10, created_at=datetime.now())
item2 = Item(name="LG노트북", price=20000, stock=10, created_at=datetime.now())
item3 = Item(name="맥북에어", price=30000, stock=10, created_at=datetime.now())
item4 = Item(name="맥북프로13", price=40000, stock=10, created_at=datetime.now())
item5 = Item(name="맥북프로16", price=50000, stock=10, created_at=datetime.now())

session.add_all([item1, item2, item3, item4, item5])
session.commit()

user1=User(name='김인섭', email='inseop@gmail.com', phone='01012341234', created_at=datetime.now()) # python object
user2=User(name='홍길동', email='gildong@gmail.com', phone='01012341234', created_at=datetime.now())

session.add_all([user1, user2])
session.commit()

purchase1=Purchase(user_id=user1.id, item_id=item4.id, quality=1, status='paid', purchase_date=datetime.now())
purchase2=Purchase(user_id=user1.id, item_id=item5.id, quality=1, status='canceled', purchase_date=datetime.now())

session.add_all([purchase1, purchase2])
session.commit()

# +크롤링 +파이썬 기반의 협업필터로 상품 추천

# 챗복 => LLM => (1) 비용이 아직까지는 비싸다. (2) 보안 때문에. => (유저 데이터를 LLM에게 넘겨줘야 하잖아요?)
# + 가스라이팅 => 고객 데이터 알고있지? 강남구 사는 고객들 리스트 알려줘.

# 2단계
# > python create_dummy_data.py
# - 더미 데이터 생성