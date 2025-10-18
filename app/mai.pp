# # file: app/main.py

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from pydantic import BaseModel
# from typing import List
# import os

# from .utils.vector_db import query_recipes  # Use only Vector DB

# # -----------------------------
# # FastAPI setup
# # -----------------------------
# app = FastAPI(title="Recipe Recommender API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Serve frontend
# frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
# app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

# @app.get("/")
# def index():
#     return FileResponse(os.path.join(frontend_path, "index.html"))

# # -----------------------------
# # Request model
# # -----------------------------
# class RecipeRequest(BaseModel):
#     pantry_items: List[str]
#     diet: str = None
#     cuisine: str = None
#     time_available: int = None
#     servings_required: int = None

# # -----------------------------
# # Health endpoint
# # -----------------------------
# @app.get("/health")
# def health_check():
#     return {"status": "ok", "message": "API is running"}


#     try:
    
#         if not any([
#             request.pantry_items,
#             request.diet,
#             request.cuisine,
#             request.time_available,
#             request.servings_required
#         ]):
#             return {"message": "Please fill at least one field to get recipe suggestions."}

#         # Query top recipes from vector DB (based on pantry items if provided)
#         top_recipes = []
#         if request.pantry_items:
#             top_recipes = query_recipes(request.pantry_items, top_k=10)
#         else:
#             top_recipes = query_recipes([], top_k=50)

#         if not top_recipes:
#             return {"message": "No recipes found for these matches. Try with different inputs."}

#         scored_recipes = []
#         for r in top_recipes:
#             # --- Dynamic filtering based on inputs filled ---
            
#             # Diet filter (only if user filled)
#             if request.diet and request.diet.strip():
#                 if request.diet.lower() not in r.get("tags", "").lower():
#                     continue

#             # Cuisine filter (only if user filled)
#             if request.cuisine and request.cuisine.strip():
#                 if request.cuisine.lower() not in r.get("tags", "").lower():
#                     continue

#             # Max time filter
#             if request.time_available and r.get("time_minutes", 0) > request.time_available:
#                 continue

#             # Servings filter
#             if request.servings_required and r.get("servings", 1) < request.servings_required:
#                 continue

#             # Ingredient matching (only if pantry items provided)
#             match_count = 0
#             if request.pantry_items:
#                 recipe_ingredients = [ing.strip().lower() for ing in r.get("ingredients", "").split(",")]
#                 match_count = sum(1 for item in request.pantry_items if item.lower() in recipe_ingredients)
#                 if match_count == 0:
#                     continue

#             r["match_score"] = match_count
#             scored_recipes.append(r)

#         # Agar filtering ke baad kuch nahi bacha
#         if not scored_recipes:
#             return {"message": "No recipes found for these matches. Try with different inputs."}

#         # Sort by match count
#         scored_recipes.sort(key=lambda x: x["match_score"], reverse=True)

#         # Top 10 results
#         top_recipes_metadata = scored_recipes[:10]

#         # Prepare output
#         final_recipes = []
#         for r in top_recipes_metadata:
#             result = {
#                 "name": r["name"],
#                 "ingredients": r["ingredients"],
#                 "tags": r["tags"],
#                 "time_minutes": r.get("time_minutes", 0),
#                 "servings": r.get("servings", 1),
#                 "instructions": [
#                     f"Use available ingredients: {r['ingredients']}.",
#                     f"Prepare {r['name']} in your preferred cooking style."
#                 ],
#                 "rank": "high"
#             }
#             final_recipes.append(result)

#         return final_recipes

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# 3rd validation with 3 other soft validation





# -----------------------------
# Recipe recommendation endpoint
# -----------------------------
# @app.post("/recommend-recipes")
# def recommend_recipes(request: RecipeRequest):
#     try:
#         # Query top recipes from vector DB
#         top_recipes = query_recipes(request.pantry_items, top_k=50)

#         if not top_recipes:
#             return {"message": "No recipes found for given pantry items."}

#         scored_recipes = []
#         for r in top_recipes:
#             # Diet filter
#             if request.diet and request.diet.strip():
#                 if request.diet.lower() not in r.get("tags", "").lower():
#                     continue

#             # Count matching ingredients
#             recipe_ingredients = [ing.strip().lower() for ing in r.get("ingredients", "").split(",")]
#             match_count = sum(1 for item in request.pantry_items if item.lower() in recipe_ingredients)
#             if match_count == 0:
#                 continue

#             # Soft filters
#             if request.time_available and r.get("time_minutes", 0) > request.time_available:
#                 continue
#             if request.servings_required and r.get("servings", 1) < request.servings_required:
#                 continue
#             if request.cuisine and request.cuisine.lower() not in r.get("tags", "").lower():
#                 continue

#             r["match_score"] = match_count
#             scored_recipes.append(r)

#         # Sort by ingredient match count
#         scored_recipes.sort(key=lambda x: x["match_score"], reverse=True)

#         # Take top 10 recipes
#         top_recipes_metadata = scored_recipes[:10]

#         # -----------------------------
#         # Directly send from Vector DB (no LLM)
#         # -----------------------------
#         final_recipes = []
#         for r in top_recipes_metadata:
#             result = {
#                 "name": r["name"],
#                 "ingredients": r["ingredients"],
#                 "tags": r["tags"],
#                 "time_minutes": r.get("time_minutes", 0),
#                 "servings": r.get("servings", 1),
#                 "instructions": [
#                     f"Use available ingredients: {r['ingredients']}.",
#                     f"Prepare {r['name']} in your preferred cooking style."
#                 ],
#                 "rank": "high"
#             }
#             final_recipes.append(result)

#         return final_recipes

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# 2nd code for stric validation
# @app.post("/recommend-recipes")
# def recommend_recipes(request: RecipeRequest):




# file: app/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os

from .utils.vector_db import query_recipes  # vector DB function

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

# Serve frontend folder
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/frontend", StaticFiles(directory=frontend_path), name="frontend")

@app.get("/")
def index():
    """Serve main frontend page"""
    return FileResponse(os.path.join(frontend_path, "index.html"))

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running fine"}

# -----------------------------
# Request Model
# -----------------------------
class RecipeRequest(BaseModel):
    pantry_items: List[str]
    diet: Optional[str] = None
    cuisine: Optional[str] = None
    time_available: Optional[int] = None
    servings_required: Optional[int] = None

# -----------------------------
# Main Recommendation Endpoint
# -----------------------------
@app.post("/recommend-recipes")
def recommend_recipes(request: RecipeRequest):
    try:
        # Mandatory check: Pantry and Servings must be provided
        if not request.pantry_items or not request.servings_required:
            return {"message": "Please provide at least pantry items and servings."}

        # Query top recipes from DB
        top_recipes = query_recipes(request.pantry_items, top_k=50)
        if not top_recipes:
            return {"message": "No recipes found for these matches. Try with different inputs."}

        # Determine which optional fields are filled
        has_diet = bool(request.diet and request.diet.strip())
        has_cuisine = bool(request.cuisine and request.cuisine.strip())
        has_time = bool(request.time_available)

        scored_recipes = []

        for r in top_recipes:
            # Ingredient match count
            recipe_ingredients = [ing.strip().lower() for ing in r.get("ingredients", "").split(",")]
            match_count = sum(1 for item in request.pantry_items if item.lower() in recipe_ingredients)
            if match_count == 0:
                continue

            # --- Apply strict filtering for each filled field ---
            # Pantry & servings are mandatory
            if r.get("servings", 0) != request.servings_required:
                continue
            # Optional fields (only if filled)
            if has_time and r.get("time_minutes", 0) != request.time_available:
                continue
            if has_diet and request.diet.lower() not in r.get("tags", "").lower():
                continue
            if has_cuisine and request.cuisine.lower() not in r.get("tags", "").lower():
                continue

            # If recipe passes all applicable filters, add it
            r["match_score"] = match_count
            scored_recipes.append(r)

        # If no recipes match
        if not scored_recipes:
            return {"message": "No recipes found for these matches. Try with different inputs."}

        # Sort by number of matched ingredients
        scored_recipes.sort(key=lambda x: x["match_score"], reverse=True)
        top_recipes_metadata = scored_recipes[:10]

        # Prepare final response
        final_recipes = []
        for r in top_recipes_metadata:
            final_recipes.append({
                "name": r["name"],
                "ingredients": r["ingredients"],
                "tags": r["tags"],
                "time_minutes": r.get("time_minutes", 0),
                "servings": r.get("servings", 1),
                "instructions": [
                    f"Use available ingredients: {r['ingredients']}.",
                    f"Prepare {r['name']} in your preferred cooking style."
                ],
                "rank": "high",
                "match_score": r["match_score"]
            })

        # Prepare note for missing fields
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

