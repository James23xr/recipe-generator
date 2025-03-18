import os
import requests
from typing import List, Dict, Any

class LLMAPIHandler:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate_recipe(self, ingredients: List[str], preferences: List[str] = None) -> Dict[str, Any]:
        """
        I generate a recipe based on the provided ingredients using OpenAI's API.
        
        Args:
            ingredients: List of available ingredients
            preferences: Optional list of dietary preferences (e.g., vegetarian, vegan)
            
        Returns:
            Dictionary containing recipe details (title, ingredients, instructions)
        """
        prompt = self._create_recipe_prompt(ingredients, preferences)
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful chef who creates recipes based on available ingredients."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            
            # Parse the response and extract recipe details
            recipe_text = response.json()["choices"][0]["message"]["content"]
            return self._parse_recipe_response(recipe_text)
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling OpenAI API: {e}")
            return self._get_fallback_recipe(ingredients)

    def _create_recipe_prompt(self, ingredients: List[str], preferences: List[str] = None) -> str:
        """I create a prompt for the LLM to generate a recipe."""
        ingredients_list = ", ".join(ingredients)
        
        dietary_requirements = ""
        if preferences and len(preferences) > 0:
            dietary_requirements = f"\n\nDietary requirements: {', '.join(preferences)}."
        
        return f"""Create a recipe using some or all of these ingredients: {ingredients_list}{dietary_requirements}

Please format the response as follows:
Title: [Recipe Name]
Ingredients:
- [ingredient 1]
- [ingredient 2]
...
Instructions:
1. [step 1]
2. [step 2]
..."""

    def _parse_recipe_response(self, response_text: str) -> Dict[str, Any]:
        """I parse the LLM response into structured recipe data."""
        try:
            # Split the response into sections and clean up
            sections = [s.strip() for s in response_text.split('\n\n') if s.strip()]
            
            # Extract title
            title_line = next(s for s in sections[0].split('\n') if 'Title:' in s)
            title = title_line.replace('Title:', '').strip()
            
            # Extract ingredients
            ingredients_section = next(s for s in sections if 'Ingredients:' in s)
            ingredients = [
                line.strip('- ').strip()
                for line in ingredients_section.split('\n')[1:]
                if line.strip() and not line.strip().startswith('Ingredients:')
            ]
            
            # Extract instructions
            instructions_section = next(s for s in sections if 'Instructions:' in s)
            instructions = []
            for line in instructions_section.split('\n')[1:]:
                line = line.strip()
                if line and not line.startswith('Instructions:'):
                    # Remove any leading numbers and dots
                    instruction = line
                    for i in range(1, 10):
                        instruction = instruction.lstrip(str(i)).lstrip('.')
                    instructions.append(instruction.strip())
            
            return {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions
            }
            
        except Exception as e:
            print(f"Error parsing recipe response: {e}")
            return self._get_fallback_recipe([])

    def _get_fallback_recipe(self, ingredients: List[str]) -> Dict[str, Any]:
        """I return a fallback recipe in case of API failure."""
        return {
            'title': 'Simple Mixed Ingredients Recipe',
            'ingredients': ingredients if ingredients else ['No ingredients provided'],
            'instructions': [
                'Combine all ingredients in a large bowl',
                'Mix well and season to taste',
                'Cook until done'
            ]
        }
