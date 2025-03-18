"""
My Recipe Generator App
I created a Flask application that generates recipes based on available ingredients using LLM API.
"""

from app.api import LLMAPIHandler
from app.routes import app

__version__ = '0.1.0'
__all__ = ['LLMAPIHandler', 'app']
