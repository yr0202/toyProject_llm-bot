from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    created_at = Column(DateTime)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    name = Column(String)
    phone = Column(String)
    created_at = Column(DateTime)

    # 사용자가 구매한 구매이력들에 대한 참조가 가능
    purchase = relationship('Purchase', back_populates='user') # 역참조 (ORM방식) => 부모도 자녀를 찾을 수 있도록..!

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quality = Column(Integer)
    status = Column(String)
    purchase_date = Column(DateTime)

    user = relationship("User", back_populates='purchase')
    item = relationship("Item")


    # FK -> 관계
    # User:Item => 1:Item, Item, Item, Item, Item.... => O 
    # Item:User => 1:User, User ....  => X
    # User(부모):Item(자녀, FK)

    # User(부모):Purchase(자녀, FK) => User:Purchase,Purchase,Purchase,Purchase
    # Purchase:User => Purchase: User, User, User, User, User => 인스타그램(1명+작성자 지정) N:N, 다:다