# db를 만드는 코드
#python -> DB를 만들 때 SQLAlchemy
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# 테이블 구조
class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    stock = Column(Integer)
    created_at = Column(DateTime)


