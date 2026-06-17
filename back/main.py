import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field


app = FastAPI(
    title="Honbab Mate API",
    description="자취생 맞춤 식단 추천 API",
)


class RecommendRequest(BaseModel):
    budget: str = Field(..., description="한 끼 예산")
    max_time: str = Field(..., description="조리 가능 시간")
    ingredients: list[str] = Field(default_factory=list, description="보유 재료")


class Menu(BaseModel):
    name: str
    cost: int
    time: int
    ingredients: list[str]
    difficulty: str
    tip: str


MENU_FILE = Path(__file__).with_name("menus.json")

BUDGET_LIMITS: dict[str, Optional[int]] = {
    "3000원 이하": 3000,
    "5000원 이하": 5000,
    "8000원 이하": 8000,
    "상관없음": None,
}

TIME_LIMITS: dict[str, Optional[int]] = {
    "10분 이내": 10,
    "20분 이내": 20,
    "30분 이내": 30,
    "시간 상관없음": None,
}


def load_menus() -> list[Menu]:
    with MENU_FILE.open("r", encoding="utf-8") as file:
        return [Menu(**menu) for menu in json.load(file)]


def get_recommend_type(menu: Menu, ingredient_score: int) -> dict:
    if ingredient_score >= 2:
        return {"emoji": "🥬", "label": "냉장고 재료 활용형"}
    if menu.time <= 10:
        return {"emoji": "⏱️", "label": "빠른 조리형"}
    if menu.cost <= 4000:
        return {"emoji": "💰", "label": "가성비형"}
    return {"emoji": "🍚", "label": "든든한 한 끼형"}


def score_menu(menu: Menu, request: RecommendRequest) -> dict:
    budget_limit = BUDGET_LIMITS.get(request.budget)
    time_limit = TIME_LIMITS.get(request.max_time)
    selected_ingredients = set(request.ingredients)
    menu_ingredients = set(menu.ingredients)

    if budget_limit is None:
        budget_score = 1
    elif menu.cost <= budget_limit:
        budget_score = 2
    else:
        budget_score = 0

    if time_limit is None:
        time_score = 1
    elif menu.time <= time_limit:
        time_score = 2
    else:
        time_score = 0

    matched_ingredients = sorted(menu_ingredients & selected_ingredients)
    missing_ingredients = sorted(menu_ingredients - selected_ingredients)
    ingredient_score = len(matched_ingredients)
    total_score = budget_score + time_score + ingredient_score

    reason_parts = []
    if budget_limit is None:
        reason_parts.append("예산 제한 없이 고를 수 있어요")
    elif menu.cost <= budget_limit:
        reason_parts.append("예산 안에 들어와요")
    else:
        reason_parts.append("예산은 조금 초과하지만")

    if time_limit is None:
        reason_parts.append("조리 시간 부담이 적어요")
    elif menu.time <= time_limit:
        reason_parts.append("가능한 시간 안에 만들 수 있어요")
    else:
        reason_parts.append("조리 시간이 조금 더 필요해요")

    if matched_ingredients:
        reason_parts.append(f"보유 재료 {len(matched_ingredients)}개를 사용할 수 있어요")
    else:
        reason_parts.append("선택한 재료와 겹치지는 않지만 준비가 간단해요")

    return {
        "name": menu.name,
        "score": total_score,
        "score_detail": {
            "budget_score": budget_score,
            "time_score": time_score,
            "ingredient_score": ingredient_score,
            "total_score": total_score,
        },
        "recommend_type": get_recommend_type(menu, ingredient_score),
        "cost": menu.cost,
        "time": menu.time,
        "difficulty": menu.difficulty,
        "ingredients": menu.ingredients,
        "matched_ingredients": matched_ingredients,
        "missing_ingredients": missing_ingredients,
        "reason": ", ".join(reason_parts) + ".",
        "tip": menu.tip,
        "_matched_count": len(matched_ingredients),
    }


@app.get("/")
async def health_check() -> dict:
    return {"message": "Honbab Mate API is running"}


@app.post("/recommend")
async def recommend(request: RecommendRequest) -> dict:
    scored_menus = [score_menu(menu, request) for menu in load_menus()]
    ranked_menus = sorted(
        scored_menus,
        key=lambda menu: (
            -menu["score"],
            -menu["_matched_count"],
            menu["cost"],
            menu["time"],
        ),
    )

    all_candidates = [
        {key: value for key, value in menu.items() if key != "_matched_count"}
        for menu in ranked_menus
    ]

    return {
        "processed_by": "FastAPI POST /recommend",
        "logic_summary": {
            "candidate_count": len(all_candidates),
            "ranking_rule": "total_score, ingredient_match_count, lower_cost, shorter_time",
            "score_rule": "budget_score + time_score + ingredient_score",
        },
        "request_summary": {
            "budget": request.budget,
            "max_time": request.max_time,
            "ingredients": request.ingredients,
        },
        "all_candidates": all_candidates,
        "recommendations": all_candidates[:3],
    }
