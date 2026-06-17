# 혼밥메이트

Streamlit + FastAPI + Docker 기반 자취생 맞춤 식단 추천 웹 애플리케이션입니다.

사용자가 한 끼 예산, 조리 가능 시간, 냉장고에 있는 재료를 선택하면 Streamlit이 FastAPI에 요청을 보내고, FastAPI가 추천 메뉴 TOP 3를 JSON으로 반환합니다.

## 서비스 흐름

```text
사용자 입력
  -> Streamlit 추천 요청 버튼 클릭
  -> Streamlit이 FastAPI POST /recommend 호출
  -> FastAPI가 메뉴 점수를 계산하고 JSON 응답 반환
  -> Streamlit이 응답 JSON의 recommendations를 화면에 출력
```

## 프로젝트 구조

```text
.
├── back/
│   ├── main.py
│   ├── menus.json
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

## Streamlit과 FastAPI 연결 구조

Streamlit은 추천 결과를 직접 계산하지 않고, 사용자가 선택한 조건을 JSON payload로 만들어 FastAPI에 전송합니다.

- 프론트엔드 요청 위치: `front/app.py`
- 요청 코드: `requests.post(f"{API_URL}/recommend", json=payload, timeout=5)`
- Docker 실행 시 API 주소: `API_URL=http://back:8000`
- 백엔드 처리 API: `back/main.py`의 `POST /recommend`

FastAPI 응답에는 `processed_by`, `logic_summary`, `request_summary`, `recommendations`가 포함됩니다. 이 중 `recommendations` 목록을 Streamlit이 받아 카드 형태로 출력합니다.

## FastAPI JSON 응답 예시

`POST /recommend` 요청 예시:

```json
{
  "budget": "5000원 이하",
  "max_time": "20분 이내",
  "ingredients": ["밥", "김치", "참치"]
}
```

응답 예시:

```json
{
  "processed_by": "FastAPI POST /recommend",
  "logic_summary": {
    "candidate_count": 10,
    "ranking_rule": "total_score, ingredient_match_count, lower_cost, shorter_time",
    "score_rule": "budget_score + time_score + ingredient_score"
  },
  "request_summary": {
    "budget": "5000원 이하",
    "max_time": "20분 이내",
    "ingredients": ["밥", "김치", "참치"]
  },
  "recommendations": [
    {
      "name": "참치 김치볶음밥",
      "score": 7,
      "cost": 4500,
      "time": 15,
      "difficulty": "쉬움"
    }
  ]
}
```

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

## 데모 영상에서 보여줄 내용

1. EC2 터미널에서 `docker ps`를 실행해 `honbab-front`, `honbab-back` 컨테이너가 실행 중인 장면을 보여줍니다.
2. 브라우저에서 `http://EC2_PUBLIC_IP`로 Streamlit 앱에 접속합니다.
3. 예산, 조리 가능 시간, 보유 재료를 선택합니다.
4. `식단 추천 요청하기!` 버튼을 클릭합니다.
5. 추천 결과 TOP 3가 화면에 표시되는 장면과 하단의 `FastAPI POST /recommend 응답으로 받은 추천 결과입니다.` 문구를 함께 보여줍니다.
6. `FastAPI 통신 JSON 확인` 영역을 열어 Streamlit이 보낸 실제 요청 JSON과 FastAPI가 반환한 실제 응답 JSON을 보여줍니다.
7. FastAPI 연결을 더 확실히 보여주려면 EC2 터미널에서 `curl http://localhost:8000`을 실행해 백엔드 응답을 보여줍니다.
8. 보안 그룹에서 8000 포트를 열어둔 경우에는 브라우저에서 `http://EC2_PUBLIC_IP:8000/docs` 또는 `http://EC2_PUBLIC_IP:8000`에 접속해 백엔드가 별도로 실행 중임을 보여줘도 됩니다.
