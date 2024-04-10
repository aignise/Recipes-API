import requests
import os
from dotenv import load_dotenv

load_dotenv()

def search_recipes(query):
    url = "https://food-recipes-with-images.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "food-recipes-with-images.p.rapidapi.com"
    }
    querystring = {"q": query}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data

def extract_recipe_info(recipe):
    title = recipe.get('title', 'N/A')
    ingredients = recipe.get('ingredients', [])
    image_url = recipe.get('image', 'N/A')
    instructions_url = recipe.get('sourceURL', 'N/A')
    
    return title, ingredients, image_url, instructions_url
