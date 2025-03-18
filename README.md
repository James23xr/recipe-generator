# Recipe Generator

A Flask web application that generates recipes based on available ingredients using OpenAI's GPT API. The application features a modern, responsive UI built with Bootstrap 5.

## Features

- Input available ingredients through a modern, user-friendly interface
- Generate recipes using OpenAI's GPT API
- Professional, responsive design using Bootstrap 5 and Font Awesome
- Interactive UI with real-time ingredient management
- RESTful API endpoints
- Comprehensive test coverage
- CI/CD pipeline with GitHub Actions

## Setup

1. Clone the repository:
```bash
git clone [your-repo-url]
cd recipe-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Testing

Run tests with coverage:
```bash
pytest --cov=.
```

Run linting:
```bash
flake8 .
black . --check
```

## API Endpoints

### Generate Recipe
- **URL**: `/api/generate-recipe`
- **Method**: `POST`
- **Data Params**: 
```json
{
    "ingredients": ["ingredient1", "ingredient2", ...]
}
```
- **Success Response**:
```json
{
    "success": true,
    "recipe": {
        "title": "Recipe Title",
        "ingredients": ["ingredient1", "ingredient2", ...],
        "instructions": ["step1", "step2", ...]
    }
}
```

## Project Structure

```
recipe-generator/
├── app/
│   ├── __init__.py
│   ├── api.py
│   └── routes.py
├── templates/
│   └── index.html
├── tests/
│   ├── test_app.py
│   └── test_api.py
├── .env
├── .gitignore
├── Procfile
├── README.md
├── app.py
├── requirements.txt
└── setup.py
```

## Deployment

The application is configured for deployment on Heroku with the included Procfile. To deploy:

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new Heroku app:
```bash
heroku create your-app-name
```

4. Set your OpenAI API key as a config variable:
```bash
heroku config:set OPENAI_API_KEY=your_api_key_here
```

5. Deploy the application:
```bash
git push heroku main
```

The application will be available at `https://your-app-name.herokuapp.com`

## License

MIT License
