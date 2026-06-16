# 혼밥메이트

Streamlit + FastAPI + Docker 기반 자취생 맞춤 식단 추천 웹 애플리케이션입니다.

사용자가 한 끼 예산, 조리 가능 시간, 냉장고에 있는 재료를 선택하면 Streamlit이 FastAPI에 요청을 보내고, FastAPI가 추천 메뉴 TOP 3를 JSON으로 반환합니다.

## 프로젝트 구조

```text
.
├── back/
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── front/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 실행 방법

```bash
docker compose up -d --build
```

실행 후 브라우저에서 접속합니다.

- Streamlit: http://localhost
- FastAPI: http://localhost:8000
- FastAPI 문서: http://localhost:8000/docs

## 주요 기능

- Streamlit에서 사용자 입력 받기
- FastAPI `/recommend`로 HTTP 요청 보내기
- FastAPI에서 추천 점수 계산
- 추천 메뉴 TOP 3를 JSON으로 반환
- Streamlit에서 카드형 결과 출력

## 추천 점수 기준

- 메뉴 예상 비용이 사용자 예산 이하이면 +2점
- 예산이 상관없음이면 +1점
- 메뉴 조리 시간이 사용자 가능 시간 이하이면 +2점
- 시간이 상관없음이면 +1점
- 보유 재료가 메뉴 재료와 1개 일치할 때마다 +1점

## EC2 배포 확인

AWS EC2에서 Docker 설치 후 아래 명령어로 실행합니다.

```bash
docker compose up -d --build
docker ps
```

보안 그룹에서 80 포트를 열고 `http://EC2_PUBLIC_IP`로 접속하면 Streamlit 앱을 확인할 수 있습니다.
