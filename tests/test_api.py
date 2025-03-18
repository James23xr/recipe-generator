import pytest
import os
import requests
from unittest.mock import patch, MagicMock
from app.api import LLMAPIHandler

@pytest.fixture
def api_handler():
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        return LLMAPIHandler()

def test_create_recipe_prompt(api_handler):
    """I test recipe prompt creation"""
    ingredients = ['chicken', 'rice', 'tomatoes']
    prompt = api_handler._create_recipe_prompt(ingredients)
    
    assert 'chicken, rice, tomatoes' in prompt
    assert 'Title:' in prompt
    assert 'Ingredients:' in prompt
    assert 'Instructions:' in prompt
    assert 'Dietary requirements' not in prompt

def test_create_recipe_prompt_with_preferences(api_handler):
    """I test recipe prompt creation with dietary preferences"""
    ingredients = ['chicken', 'rice', 'tomatoes']
    preferences = ['vegetarian', 'gluten-free']
    prompt = api_handler._create_recipe_prompt(ingredients, preferences)
    
    assert 'chicken, rice, tomatoes' in prompt
    assert 'Dietary requirements:' in prompt
    assert 'vegetarian' in prompt
    assert 'gluten-free' in prompt
    assert 'Title:' in prompt
    assert 'Ingredients:' in prompt
    assert 'Instructions:' in prompt

def test_parse_recipe_response(api_handler):
    """I test parsing of LLM response"""
    test_response = """Title: Test Recipe
    
Ingredients:
- ingredient 1
- ingredient 2

Instructions:
1. step 1
2. step 2"""

    result = api_handler._parse_recipe_response(test_response)
    
    assert result['title'] == 'Test Recipe'
    assert len(result['ingredients']) == 2
    assert 'ingredient 1' in result['ingredients']
    assert len(result['instructions']) == 2
    assert 'step 1' in result['instructions']

def test_generate_recipe_api_success():
    """I test successful API call"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{
            "message": {
                "content": """Title: Test Recipe

Ingredients:
- ingredient 1
- ingredient 2

Instructions:
1. step 1
2. step 2"""
            }
        }]
    }
    
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        with patch('requests.post') as mock_post:
            mock_post.return_value = mock_response
            mock_response.raise_for_status = MagicMock()
            
            api_handler = LLMAPIHandler()
            result = api_handler.generate_recipe(['test'])
            
            assert result['title'] == 'Test Recipe'
            assert len(result['ingredients']) == 2
            assert len(result['instructions']) == 2

def test_generate_recipe_api_failure():
    """I test API failure fallback"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException('API Error')
            
            api_handler = LLMAPIHandler()
            test_ingredients = ['test1', 'test2']
            result = api_handler.generate_recipe(test_ingredients)
            
            assert result['title'] == 'Simple Mixed Ingredients Recipe'
            assert result['ingredients'] == test_ingredients
            assert len(result['instructions']) == 3
            assert 'Combine all ingredients' in result['instructions'][0]

def test_missing_api_key():
    """I test handling of missing API key"""
    with patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError) as exc_info:
            LLMAPIHandler()
        assert "OpenAI API key not found" in str(exc_info.value)

def test_parse_recipe_response_error():
    """I test error handling in recipe response parsing"""
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
        api_handler = LLMAPIHandler()
        result = api_handler._parse_recipe_response("Invalid response format")
        
        assert result['title'] == 'Simple Mixed Ingredients Recipe'
        assert result['ingredients'] == ['No ingredients provided']
        assert len(result['instructions']) == 3
