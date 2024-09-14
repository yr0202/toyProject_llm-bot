from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()
# Base = declarative_base()

# MySQL 접속 정보 가져오기
# MYSQL_USER = os.getenv("MYSQL_USER")
# MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
# MYSQL_HOST = os.getenv("MYSQL_HOST")
# MYSQL_DB = os.getenv("MYSQL_DB")
# MYSQL_PORT=os.getenv("MYSQL_PORT",3306)


# MySQL용 DATABASE_URL 생성
# DATABASE_URL = f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}'
DATABASE_URL = 'mysql+pymysql://yuram:1234@localhost/toy2'


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 데이터베이스 초기화 함수
def init_db():
    Base.metadata.create_all(bind=engine)

# 데이터베이스 세션을 생성하고 반환하는 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()  # 트랜잭션 중 오류가 발생할 경우 롤백
        raise e
    finally:
        db.close()  # 세션을 안전하게 닫음

# init_db()