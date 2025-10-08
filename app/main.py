# file: app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
import os

from .utils.vector_db import query_recipes  # your existing vector DB helper
from .utils.llm_helper import generate_recipe_instructions  # updated helper

# -----------------------------
# FastAPI setup
# -----------------------------
app = FastAPI(title="Recipe Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# -----------------------------
# Request model
# -----------------------------
class RecipeRequest(BaseModel):
    pantry_items: List[str]
    diet: str = None
    cuisine: str = None
    time_available: int = None
    servings_required: int = None

# -----------------------------
# Health endpoint
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

# -----------------------------
# Recipe recommendation endpoint
# -----------------------------
@app.post("/recommend-recipes")
def recommend_recipes(request: RecipeRequest):
    try:
        # Query top 50 recipes from vector DB
        top_recipes = query_recipes(request.pantry_items, top_k=50)

        scored_recipes = []
        for r in top_recipes:
            # Diet filter if provided
            if request.diet and request.diet.strip():
                if request.diet.lower() not in r.get("tags", "").lower():
                    continue

            # Count matching ingredients
            recipe_ingredients = [ing.strip().lower() for ing in r.get("ingredients", "").split(",")]
            match_count = sum(1 for item in request.pantry_items if item.lower() in recipe_ingredients)
            if match_count == 0:
                continue
            r["match_score"] = match_count

            # Soft filters
            r["time_ok"] = (not request.time_available) or (r.get("time_minutes", 0) <= request.time_available)
            r["servings_ok"] = (not request.servings_required) or (r.get("servings", 1) >= request.servings_required)
            r["cuisine_ok"] = (not request.cuisine) or (request.cuisine.lower() in r.get("tags", "").lower())

            scored_recipes.append(r)

        # Sort by ingredient match count
        scored_recipes.sort(key=lambda x: x["match_score"], reverse=True)

        # Take top 10 recipes
        top_recipes_metadata = scored_recipes[:10]

        # -----------------------------
        # Call LLM for instructions & substitutions
        # -----------------------------
        llm_results = generate_recipe_instructions(top_recipes_metadata, request.pantry_items)

        # Merge LLM results with recipes
        final_recipes = []
        for r in top_recipes_metadata:
            r["llm"] = llm_results.get(r["name"], {})
            final_recipes.append(r)

        return final_recipes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
