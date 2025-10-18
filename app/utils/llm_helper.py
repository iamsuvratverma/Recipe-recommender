# file: app/utils/llm_helper.py

import ollama
import json

def generate_recipe_details(recipe, pantry_items, diet=None, cuisine=None, time_available=None, servings_required=None):
    """
    Generate instructions, substitutions, and rank using Ollama LLM.
    If LLM is not used or fails, fallback safely handles ingredients.
    """
    prompt = f"""
User Pantry: {', '.join(pantry_items)}
Diet: {diet or 'any'}
Cuisine: {cuisine or 'any'}
Max time: {time_available or 'any'}
Servings: {servings_required or 'any'}

Candidate Recipe:
Name: {recipe['name']}
Ingredients: {', '.join(recipe.get('ingredients', [])) if isinstance(recipe.get('ingredients', []), list) else recipe.get('ingredients', '')}
Tags: {recipe.get('tags', '')}
Time: {recipe.get('time_minutes', 'unknown')} minutes
Servings: {recipe.get('servings', 'unknown')}

Generate:
1. Step-by-step cooking instructions.
2. Ingredient substitutions if something is missing in the pantry.
3. Rank the recipe suitability (high/medium/low).
Output in JSON format only.
"""
    try:
        llm_response = ollama.chat(prompt)  # Call LLM
        data = json.loads(llm_response)
        data["match_score"] = recipe.get("match_score", 0)
        return data
    except Exception:
        # Fallback if LLM fails or not used
        ingredients = recipe.get("ingredients", [])
        if isinstance(ingredients, str):
            # Convert string of ingredients to a proper list by splitting commas
            ingredients = [i.strip() for i in ingredients.split(",") if i.strip()]
        return {
            "name": recipe["name"],
            "rank": "high",
            "instructions": [f"Use available ingredients: {', '.join(ingredients)}"],
            "substitutions": [],
            "match_score": recipe.get("match_score", 0)
        }
