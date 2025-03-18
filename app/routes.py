from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from app.api import LLMAPIHandler
import os
import json
from datetime import datetime

load_dotenv()

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
api_handler = None

# I'm using in-memory storage for saved recipes (in a real app, I would use a database)
saved_recipes = []

try:
    api_handler = LLMAPIHandler()
except ValueError as e:
    print(f"Warning: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/saved-recipes')
def saved_recipes_page():
    """I render the saved recipes page"""
    return render_template('saved_recipes.html')

@app.route('/api/generate-recipe', methods=['POST'])
def generate_recipe():
    ingredients = request.json.get('ingredients', [])
    preferences = request.json.get('preferences', [])
    
    if not api_handler:
        return jsonify({
            'success': False,
            'error': 'API configuration error'
        }), 500
        
    try:
        recipe = api_handler.generate_recipe(ingredients, preferences)
        return jsonify({
            'success': True,
            'recipe': recipe
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/save-recipe', methods=['POST'])
def save_recipe():
    """I save a recipe to the user's collection"""
    try:
        recipe = request.json.get('recipe', {})
        if not recipe or 'title' not in recipe:
            return jsonify({
                'success': False,
                'error': 'Invalid recipe data'
            }), 400
            
        # Add timestamp and unique ID
        recipe['saved_at'] = datetime.now().isoformat()
        recipe['id'] = len(saved_recipes) + 1
        
        # Save the recipe
        saved_recipes.append(recipe)
        
        return jsonify({
            'success': True,
            'message': 'Recipe saved successfully',
            'recipe_id': recipe['id']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/saved-recipes', methods=['GET'])
def get_saved_recipes():
    """I get all saved recipes"""
    return jsonify({
        'success': True,
        'recipes': saved_recipes
    })
