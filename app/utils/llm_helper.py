
import ollama
from typing import List, Dict
import json

def generate_recipe_instructions(recipe_metadata: List[Dict], pantry_items: List[str]):
    """
    Generate rank, substitutions, and instructions for recipes using Ollama.
    """
    recipes_info = {}

    for recipe in recipe_metadata:
        prompt = f"""
        You are a strict JSON generator cooking assistant.

        Recipe:
        Name: {recipe['name']}
        Ingredients: {recipe['ingredients']}
        Tags: {recipe['tags']}

        User pantry items: {', '.join(pantry_items)}

        Tasks:
        1. Rank recipe suitability (high/medium/low).
        2. Suggest ingredient substitutions if anything is missing.
        3. Provide step-by-step cooking instructions.

        RULES:
        - Return ONLY valid JSON.
        - Do NOT include extra text, explanation, or markdown formatting.

        JSON format:
        {{
            "rank": "<rank>",
            "substitutions": ["ingredient1->substitute1", ...],
            "instructions": ["Step1", "Step2", ...]
        }}
        """

        try:
            response = ollama.chat(
                model="llama3.2:1b",
                messages=[
                    {"role": "system", "content": "You are a helpful cooking assistant that outputs only JSON."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the model reply
            reply_content = response["message"]["content"].strip()

            # Try to parse JSON
            recipes_info[recipe["name"]] = json.loads(reply_content)

        except (json.JSONDecodeError, KeyError, TypeError):
            # If parsing fails, fallback
            recipes_info[recipe["name"]] = {
                "rank": "unknown",
                "substitutions": [],
                "instructions": ["Could not generate instructions."]
            }

        except Exception as e:
            recipes_info[recipe["name"]] = {
                "rank": "error",
                "substitutions": [],
                "instructions": [f"Error: {str(e)}"]
            }

    return recipes_info
