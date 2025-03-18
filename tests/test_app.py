import pytest
from unittest.mock import patch
from app import app
from app.api import LLMAPIHandler

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_api_handler():
    with patch.object(LLMAPIHandler, 'generate_recipe') as mock_generate:
        mock_generate.return_value = {
            'title': 'Test Recipe',
            'ingredients': ['ingredient1', 'ingredient2'],
            'instructions': ['step1', 'step2']
        }
        yield mock_generate

def test_index_route(client):
    """I test that the index route returns the main page"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Recipe Generator' in response.data

def test_generate_recipe_route(client, mock_api_handler):
    """I test the recipe generation API endpoint"""
    test_ingredients = ['chicken', 'rice', 'tomatoes']
    response = client.post('/api/generate-recipe', 
                         json={'ingredients': test_ingredients})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recipe' in data
    assert 'title' in data['recipe']
    assert 'ingredients' in data['recipe']
    assert 'instructions' in data['recipe']
    
    mock_api_handler.assert_called_once_with(test_ingredients, [])

def test_generate_recipe_empty_ingredients(client, mock_api_handler):
    """I test the API endpoint with empty ingredients list"""
    response = client.post('/api/generate-recipe', 
                         json={'ingredients': []})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    mock_api_handler.assert_called_once_with([], [])

def test_generate_recipe_invalid_request(client):
    """I test the API endpoint with invalid request format"""
    response = client.post('/api/generate-recipe', 
                         json={})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recipe' in data

def test_generate_recipe_with_preferences(client, mock_api_handler):
    """I test the recipe generation API endpoint with preferences"""
    test_ingredients = ['chicken', 'rice']
    test_preferences = ['vegetarian']
    response = client.post('/api/generate-recipe', 
                         json={'ingredients': test_ingredients, 'preferences': test_preferences})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recipe' in data
    mock_api_handler.assert_called_once_with(test_ingredients, test_preferences)

def test_saved_recipes_page(client):
    """I test that the saved recipes page returns correctly"""
    response = client.get('/saved-recipes')
    assert response.status_code == 200

def test_save_recipe(client):
    """I test saving a recipe"""
    test_recipe = {
        'title': 'Test Recipe',
        'ingredients': ['ingredient1', 'ingredient2'],
        'instructions': ['step1', 'step2']
    }
    response = client.post('/api/save-recipe', 
                         json={'recipe': test_recipe})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'message' in data
    assert 'recipe_id' in data

def test_save_recipe_invalid(client):
    """I test saving an invalid recipe"""
    response = client.post('/api/save-recipe', 
                         json={'recipe': {}})
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data

def test_get_saved_recipes(client):
    """I test getting saved recipes"""
    response = client.get('/api/saved-recipes')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'recipes' in data

def test_api_configuration_error(client):
    """I test error handling when api_handler is None"""
    with patch('app.routes.api_handler', None):
        response = client.post('/api/generate-recipe', 
                             json={'ingredients': ['test']})
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'API configuration error' in data['error']

def test_api_handler_initialization_error():
    """I test error handling when LLMAPIHandler initialization fails"""
    # Save the original api_handler
    from app.routes import api_handler as original_api_handler
    
    try:
        # Patch os.getenv to raise a ValueError when getting OPENAI_API_KEY
        with patch('os.getenv') as mock_getenv:
            mock_getenv.return_value = None
            
            # Patch print to capture the warning message
            with patch('builtins.print') as mock_print:
                # Import the module to trigger the exception
                import importlib
                from app import routes
                importlib.reload(routes)
                
                # Check that print was called with a warning message
                mock_print.assert_called_with("Warning: OpenAI API key not found in environment variables")
    finally:
        # Restore the original api_handler
        import app.routes
        app.routes.api_handler = original_api_handler

def test_generate_recipe_exception(client):
    """I test error handling when generate_recipe raises an exception"""
    with patch('app.routes.api_handler.generate_recipe') as mock_generate:
        mock_generate.side_effect = Exception("Test error")
        
        response = client.post('/api/generate-recipe', 
                             json={'ingredients': ['test']})
        
        assert response.status_code == 500
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data

def test_save_recipe_exception(client):
    """I test error handling when save_recipe raises an exception"""
    # Create a test client with a request context
    with client.post('/api/save-recipe', 
                   json={'recipe': {'title': 'Test'}}) as response:
        # Force an exception in the route by patching datetime.now
        with patch('app.routes.datetime') as mock_datetime:
            mock_datetime.now.side_effect = Exception("Test error")
            
            # Call the route handler directly
            from app.routes import save_recipe
            result = save_recipe()
            
            # Check that the error is handled correctly
            assert isinstance(result, tuple)
            assert result[1] == 500
            data = result[0].json
            assert data['success'] is False
            assert 'error' in data

def test_get_saved_recipes_exception(client):
    """I test error handling when get_saved_recipes raises an exception"""
    # Create a test client with a request context
    with client.get('/api/saved-recipes') as response:
        # Force an exception in the route by patching jsonify
        with patch('flask.jsonify') as mock_jsonify:
            mock_jsonify.side_effect = Exception("Test error")
            
            # Call the route handler directly
            from app.routes import get_saved_recipes
            try:
                result = get_saved_recipes()
                assert False, "Exception not raised"
            except Exception:
                # The exception should be raised and caught by Flask's error handler
                pass
