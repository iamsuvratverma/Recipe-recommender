# file: app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

from .utils.vector_db import query_recipes  # Vector DB

# Optional: Ollama LLM helper
try:
    from .utils.llm_helper import generate_recipe_details
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

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

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

# -----------------------------
# Request model
# -----------------------------
class RecipeRequest(BaseModel):
    pantry_items: Optional[List[str]] = []
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    time_available: Optional[int] = None
    servings_required: Optional[int] = None

# -----------------------------
# Recipe recommender endpoint
# -----------------------------
@app.post("/recommend-recipes")
def recommend_recipes(request: RecipeRequest):
    try:
        # Validate mandatory fields
        if not request.pantry_items or not request.servings_required:
            return {"message": "Please provide at least pantry items and servings."}

        # Query recipes from vector DB
        top_recipes = query_recipes(request.pantry_items, top_k=50)
        if not top_recipes:
            return {"message": "No recipes found for these matches. Try with different inputs."}

        # Optional fields flags
        has_diet = bool(request.diet and request.diet.strip())
        has_cuisine = bool(request.cuisine and request.cuisine.strip())
        has_time = bool(request.time_available)

        scored_recipes = []

        for r in top_recipes:
            # Ingredient match
            recipe_ingredients = [ing.strip().lower() for ing in r.get("ingredients", "").split(",")]
            match_count = sum(1 for item in request.pantry_items if item.lower() in recipe_ingredients)
            if match_count == 0:
                continue

            # --- Apply strict filtering for filled fields only ---
            if request.servings_required and r.get("servings", 0) != request.servings_required:
                continue
            if has_time and r.get("time_minutes", 0) != request.time_available:
                continue
            if has_diet and request.diet.lower() not in r.get("tags", "").lower():
                continue
            if has_cuisine and request.cuisine.lower() not in r.get("tags", "").lower():
                continue

            r["match_score"] = match_count
            scored_recipes.append(r)

        if not scored_recipes:
            return {"message": "No recipes found for these matches. Try with different inputs."}

        # Sort by ingredient match
        scored_recipes.sort(key=lambda x: x["match_score"], reverse=True)
        top_recipes_metadata = scored_recipes[:10]

        # Prepare final output with optional LLM
        final_recipes = []
        for r in top_recipes_metadata:
            recipe_detail = {
                "name": r["name"],
                "ingredients": r["ingredients"],
                "tags": r["tags"],
                "time_minutes": r.get("time_minutes", 0),
                "servings": r.get("servings", 1),
                "rank": "high",
                "match_score": r["match_score"]
            }

            if LLM_AVAILABLE:
                try:
                    llm_result = generate_recipe_details(
                        r,
                        request.pantry_items,
                        diet=request.diet,
                        cuisine=request.cuisine,
                        time_available=request.time_available,
                        servings_required=request.servings_required
                    )
                    recipe_detail.update({
                        "instructions": llm_result.get("instructions", []),
                        "substitutions": llm_result.get("substitutions", [])
                    })
                except Exception:
                    # Fallback if LLM fails
                    recipe_detail["instructions"] = [
                        f"Use available ingredients: {r['ingredients']}.",
                        f"Prepare {r['name']} in your preferred cooking style."
                    ]
                    recipe_detail["substitutions"] = []
            else:
                # Fallback if LLM not installed
                recipe_detail["instructions"] = [
                    f"Use available ingredients: {r['ingredients']}.",
                    f"Prepare {r['name']} in your preferred cooking style."
                ]
                recipe_detail["substitutions"] = []

            final_recipes.append(recipe_detail)

        # Note if optional fields missing
        missing_fields = []
        if not has_diet: missing_fields.append("diet")
        if not has_cuisine: missing_fields.append("cuisine")
        if not has_time: missing_fields.append("max time")

        note = ""
        if missing_fields:
            note = "Note: You have not provided " + ", ".join(missing_fields) + \
                   ", so recipes are shown based on the remaining inputs."

        return {"note": note, "recipes": final_recipes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
