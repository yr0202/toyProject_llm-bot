# yuram-llm-bot
LLM chat bot to use CrewAI

## 1. 프로젝트 세팅
- VSC
- Github 연동

## 2. 프로젝트 구성
- 가상환경을 설정 => Docker Container 개념 (공간을 분리해서 따로 관리하겠다)
- python 3.8 열심히 개발했어요. 근데 우리가 배포할 서버가 3.3버전의 파이썬이다.
    => 3.8 함수를 썼다면 3.3에는 없는 함수야 => 오류 => 배포하고 나서 알겠죠
    => 로컬에서 작업하는 환경과 호스트 서버에서 작업하는 환경을 일치시켜 주기 위함
    => Docker(Virtual Machine) // venv모듈을 사용해서 환경 설정을 해주도록 하겠음
    => Docker는 환경을 동일하게 만들어줌

> python3.10 -m venv .venv (강사님) => python -m venv .venv (유람컴)
.venv (가상환경) : 실행시켜야함 => .venv/Scripts/activate (windows)

## 3. 프로젝트

### 3-1. Ollama 모델 + CrewAI

(1) ollama 다운로드 : 언어모델을 로컬에서 돌릴 수 있도록 도와주는 프로그램

(2) ollama를 통해서 llm 다운로드
    ollama pull llama3.1 -> 이건 무거워서 가벼운 phi3으로
    ollama pull phi3
    ollama run phi3 -> 올라마 실행시키기, api가 우리 컴터에서 열리는거다

(3) CrewAI 설치
- 언어 모델의 API 관리를 편리하게 도와주는 라이브러리
- 모델 - 클로드, 젬미니, GPT3.5, GPT4o ... -> import OpenAI //언어마다 SDK를 다운받아줘야함
    => CrewAI, LangChain이 이미 다 SDK 구현을 끝내놓음
- CrewAI가 LangChain보다 가벼워서 사용 

> pip install crewai crewai-tools => To install crewAI, you need to have Python >=3.10 and <=3.13 installed on your system:
> pip install langchain-ollama

- pydantic : 파이썬에서 데이터 타입을 명시할 수 있게 해주는 라이브러리

### 3-2. Flask 사용해서 기본적인 챗봇 