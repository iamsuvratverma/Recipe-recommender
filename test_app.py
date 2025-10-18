
import pytest
from unittest.mock import patch, MagicMock
from app.utils import llm_helper

# Test: Successful recipe generation
def test_generate_recipe_instructions_success():
    recipe = [{"name": "Test Recipe", "ingredients": "egg, milk", "tags": "vegetarian"}]
    pantry = ["egg", "milk"]

    # Mock Ollama chat response to match new helper format
    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "high", "substitutions": [], "instructions": ["Step1", "Step2"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)

        assert "Test Recipe" in result
        assert result["Test Recipe"]["rank"] == "high"
        assert result["Test Recipe"]["substitutions"] == []
        assert result["Test Recipe"]["instructions"] == ["Step1", "Step2"]

# Test: JSON parsing failure fallback

def test_generate_recipe_instructions_invalid_json():
    recipe = [{"name": "Bad Recipe", "ingredients": "egg", "tags": "vegetarian"}]
    pantry = ["egg"]

    # Return invalid JSON string
    mock_response = {
        "message": {
            "role": "assistant",
            "content": "INVALID JSON"
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)

        assert result["Bad Recipe"]["rank"] == "unknown"
        assert result["Bad Recipe"]["instructions"] == ["Could not generate instructions."]

# -----------------------------
# Test: Ollama throws exception
# -----------------------------
def test_generate_recipe_instructions_exception():
    recipe = [{"name": "Error Recipe", "ingredients": "egg", "tags": "vegetarian"}]
    pantry = ["egg"]

    with patch("app.utils.llm_helper.ollama.chat", side_effect=Exception("Some error")):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)

        assert result["Error Recipe"]["rank"] == "error"
        assert "Some error" in result["Error Recipe"]["instructions"][0]

# -----------------------------
# Additional tests for multiple recipes
# -----------------------------
def test_generate_multiple_recipes():
    recipes = [
        {"name": "Recipe1", "ingredients": "a,b", "tags": "tag1"},
        {"name": "Recipe2", "ingredients": "c,d", "tags": "tag2"}
    ]
    pantry = ["a", "c"]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "medium", "substitutions": [], "instructions": ["Step1"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipes, pantry)

        assert result["Recipe1"]["rank"] == "medium"
        assert result["Recipe2"]["instructions"] == ["Step1"]

# -----------------------------
# Test: Empty recipe list
# -----------------------------
def test_generate_empty_recipe_list():
    result = llm_helper.generate_recipe_instructions([], ["egg"])
    assert result == {}

# -----------------------------
# Test: Empty pantry
# -----------------------------
def test_generate_empty_pantry():
    recipe = [{"name": "Test Recipe", "ingredients": "egg, milk", "tags": "vegetarian"}]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "low", "substitutions": ["milk->soy"], "instructions": ["Step1"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, [])
        assert result["Test Recipe"]["rank"] == "low"
        assert result["Test Recipe"]["substitutions"] == ["milk->soy"]

# -----------------------------
# Test: Long instructions
# -----------------------------
def test_generate_long_instructions():
    recipe = [{"name": "Long Recipe", "ingredients": "x,y", "tags": "tag"}]
    pantry = ["x"]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "high", "substitutions": [], "instructions": ["Step1", "Step2", "Step3", "Step4"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)
        assert len(result["Long Recipe"]["instructions"]) == 4

# -----------------------------
# Test: Multiple ingredients missing
# -----------------------------
def test_missing_ingredients_substitutions():
    recipe = [{"name": "Sub Recipe", "ingredients": "egg, milk, flour", "tags": "veg"}]
    pantry = ["egg"]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "medium", "substitutions": ["milk->soy", "flour->oat"], "instructions": ["Step1"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)
        assert "milk->soy" in result["Sub Recipe"]["substitutions"]
        assert "flour->oat" in result["Sub Recipe"]["substitutions"]

# -----------------------------
# Test: Special characters in recipe
# -----------------------------
def test_special_characters():
    recipe = [{"name": "Spicy & Sweet", "ingredients": "chili, sugar", "tags": "hot"}]
    pantry = ["chili"]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "high", "substitutions": [], "instructions": ["Step1"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipe, pantry)
        assert "Spicy & Sweet" in result
        assert result["Spicy & Sweet"]["rank"] == "high"

# -----------------------------
# Test: Large number of recipes
# -----------------------------
def test_large_recipe_list():
    recipes = [{"name": f"Recipe{i}", "ingredients": "a,b", "tags": "tag"} for i in range(20)]
    pantry = ["a"]

    mock_response = {
        "message": {
            "role": "assistant",
            "content": '{"rank": "medium", "substitutions": [], "instructions": ["Step1"]}'
        }
    }

    with patch("app.utils.llm_helper.ollama.chat", return_value=mock_response):
        result = llm_helper.generate_recipe_instructions(recipes, pantry)
        assert len(result) == 20
        assert all(r["rank"] == "medium" for r in result.values())
