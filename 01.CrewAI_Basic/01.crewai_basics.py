from crewai import Crew, Agent, Task 
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model='phi3',
    base_url='http://localhost:11434'
)

# Crew : 러닝크루 => N명 (조직)
# Agent : 요원 => 1명 (조직원) , 여러개 만들 수 있음
# Task : 미션 , 여러개 만들 수 있음

user_question = input('편하게 질문해주세요 :)')

book_agent = Agent(
    role='책 구매 어시스턴트',
    goal='고객이 어떤 상황인지 설명을 하면 해당 상황에 맞는 우리 서점에 있는 책을 소개합니다.',
    backstory='당신은 우리 서점의 모든 책 정보를 알고있으며, 사람들의 상황에 맞는 책을 소개하는데 전문가입니다.',
    llm=llm
)

recommand_book_task =  Task(
    # description='고객의 상황에 맞는 최고의 추천 도서 제안하기',
    description=user_question,
    expected_output='고객의 상황에 맞는 5개의 도서를 추천해주고, 해당 책을 추천한 이유를 알려줘',
    agent=book_agent,
    output_file='recommand_book_task.md'
)

review_agent = Agent(
    role='책 리뷰 어시스턴트',
    goal='추천받은 책들의 도서에 대한 리뷰를 제공하고, 해당 도서에 대한 심도있는 평가를 제공합니다.',
    backstory='당신은 우리 서점의 모든 책 정보를 알고있으며, 추천받은 책에 대한 전문가 수준의 리뷰를 제공합니다.',
    llm=llm
)

review_task =  Task(
    description='고객이 선택한 책에 대한 리뷰를 제공합니다.',
    expected_output='고객이 선택한 책에 대한 리뷰를 제공합니다.',
    agent=review_agent,
    output_file='review_task.md'
)

# 요원과 미션을 관리
crew = Crew(
    agents=[book_agent, review_agent],
    tasks=[recommand_book_task, review_task],
    verbose=True
)

result = crew.kickoff()

print(result)

# python 01.crewai_basics.py 로 실행하기

# 우리가 하려는 것. 배우고 있는 것
# 파이썬을 활용한 LLM - ollma, CrewAI(AI agent-랜딩 페이지 제작)

# 언어모델 핸들링하고나서 결과값을 자바서버에 내려줘야해.
# LLM이 만들어낸 결과값을 어떻게 자바 서버에 내려주지?
# - REST API(Python-FrameWork) => Java서버

# Flask(쉬움,진입장벽 낮음), FastAPI(진입장벽이 있는 편) => (1) 깃헙 스타 (2) 구글 검색량
# - AI기업. 메인 서버. AI 관련 인퍼런스(추론값) 값은 Python 백엔드로 내려주는 형태

# 프론트엔드는 어떻게 개발하고 계세요? java-jinja template