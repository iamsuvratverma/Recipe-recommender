
from vector_db import collection

if __name__ == "__main__":
    # total recipes in DB
    total = collection.count()
    print(f" Total recipes in DB: {total}")

    if total > 0:
        # sample top 2 recipes
        results = collection.get(limit=2)
        print("\n🔎 Sample Recipes:")
        for r in results["metadatas"]:
            print(f"- {r['name']} | Time: {r['time_minutes']} min | Servings: {r['servings']}")
