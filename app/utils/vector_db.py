
# from typing import List
# import json
# import os
# from sentence_transformers import SentenceTransformer
# import chromadb
# from chromadb.config import Settings

# # -----------------------------
# # Setup absolute paths
# # -----------------------------
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/utils
# APP_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # app
# DB_DIR = os.path.join(APP_DIR, "chroma_db")  # app/chroma_db
# JSON_PATH = os.path.join(APP_DIR, "data", "recipes.json")  #  app/data/recipes.json

# # Ensure DB dir exists
# os.makedirs(DB_DIR, exist_ok=True)

# # -----------------------------
# # 1️⃣ Initialize Persistent Chroma client
# # -----------------------------
# client = chromadb.PersistentClient(path=DB_DIR)

# # Create or get collection
# collection = client.get_or_create_collection(name="recipes")

# # -----------------------------
# # 2️⃣ Load embedding model
# # -----------------------------
# embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# # -----------------------------
# # 3️⃣ Add recipes from JSON
# # -----------------------------
# def add_recipes_from_json(file_path: str = JSON_PATH):
#     if not os.path.exists(file_path):
#         print(f"❌ JSON file not found: {file_path}")
#         return

#     with open(file_path, "r", encoding="utf-8") as f:
#         recipes = json.load(f)

#     for recipe in recipes:
#         text = recipe["name"] + " " + " ".join(recipe["ingredients"]) + " " + " ".join(recipe["tags"])
#         embedding = embed_model.encode(text).tolist()

#         # Ensure numeric fields
#         time_minutes = int(recipe.get("time_required", 0))
#         servings = int(recipe.get("servings", 1))

#         collection.add(
#             documents=[text],
#             metadatas=[{
#                 "id": recipe["id"],
#                 "name": recipe["name"],
#                 "ingredients": ", ".join(recipe["ingredients"]),
#                 "tags": ", ".join(recipe["tags"]),
#                 "time_minutes": time_minutes,
#                 "servings": servings
#             }],
#             embeddings=[embedding],
#             ids=[str(recipe["id"])]
#         )

#     print(f"✅ Added {len(recipes)} recipes to Chroma DB.")

# # -----------------------------
# # 4️⃣ Query recipes
# # -----------------------------
# def query_recipes(pantry_items: List[str], top_k: int = 5):
#     query_text = " ".join(pantry_items)
#     embedding = embed_model.encode(query_text).tolist()
#     results = collection.query(query_embeddings=[embedding], n_results=top_k)
#     return results['metadatas'][0] if results['metadatas'] else []

# # -----------------------------
# # 5️⃣ Optional test run
# # -----------------------------
# if __name__ == "__main__":
#     add_recipes_from_json()
#     sample_pantry = ["chickpeas", "tomato", "garam masala"]
#     top_recipes = query_recipes(sample_pantry, top_k=3)

#     print("\n🔎 Top 3 recipes for pantry items:", sample_pantry)
#     for i, r in enumerate(top_recipes, start=1):
#         print(f"{i}. {r['name']} - Time: {r['time_minutes']} min, Servings: {r['servings']}")



from typing import List
import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

# -----------------------------
# Setup absolute paths
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # app/utils
APP_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))  # app
DB_DIR = os.path.join(APP_DIR, "chroma_db")  # app/chroma_db
JSON_PATH = os.path.join(APP_DIR, "data", "recipes.json")  # app/data/recipes.json

# Ensure DB dir exists
os.makedirs(DB_DIR, exist_ok=True)

# -----------------------------
# 1️⃣ Initialize Persistent Chroma client
# -----------------------------
client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name="recipes")

# -----------------------------
# 2️⃣ Load embedding model
# -----------------------------
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# 3️⃣ Add recipes from JSON
# -----------------------------
def add_recipes_from_json(file_path: str = JSON_PATH):
    """Load all recipes from JSON and add them to ChromaDB."""
    if not os.path.exists(file_path):
        print(f"❌ JSON file not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    print(f"🔄 Adding {len(recipes)} recipes to Chroma DB...")

    for recipe in recipes:
        text = recipe["name"] + " " + " ".join(recipe["ingredients"]) + " " + " ".join(recipe["tags"])
        embedding = embed_model.encode(text).tolist()

        # Safely convert numeric fields
        time_minutes = int(recipe.get("time_required", 0) or 0)
        servings = int(recipe.get("servings", 1) or 1)

        collection.add(
            documents=[text],
            metadatas=[{
                "id": recipe.get("id", ""),
                "name": recipe.get("name", "Unnamed Recipe"),
                "ingredients": ", ".join(recipe.get("ingredients", [])),
                "tags": ", ".join(recipe.get("tags", [])),
                "time_minutes": time_minutes,
                "servings": servings
            }],
            embeddings=[embedding],
            ids=[str(recipe.get("id", ""))]
        )

    print(f"✅ Added {len(recipes)} recipes to Chroma DB.")

# -----------------------------
# 4️⃣ Query recipes by pantry items
# -----------------------------
def query_recipes(pantry_items: List[str], top_k: int = 5):
    """Query top matching recipes based on pantry items."""
    if not pantry_items:
        print("⚠️ No pantry items provided!")
        return []

    query_text = " ".join(pantry_items)
    embedding = embed_model.encode(query_text).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=top_k)

    if not results or not results.get("metadatas") or not results["metadatas"][0]:
        print("❌ No matching recipes found.")
        return []

    recipes = results["metadatas"][0]
    return recipes

# -----------------------------
# 5️⃣ Optional test run
# -----------------------------
if __name__ == "__main__":
    # Uncomment below line for first run to populate DB
    add_recipes_from_json()

    sample_pantry = ["chickpeas", "tomato", "garam masala"]
    top_recipes = query_recipes(sample_pantry, top_k=3)

    print("\n🔎 Top 3 recipes for pantry items:", sample_pantry)
    for i, r in enumerate(top_recipes, start=1):
        print(f"{i}. {r['name']} - Time: {r['time_minutes']} min, Servings: {r['servings']}")
        print(f"   Ingredients: {r['ingredients']}")
