from flask import Flask, request, render_template, jsonify
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Yummly API URL and headers
url = "https://food-recipes-with-images.p.rapidapi.com/"
headers = {
    "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "food-recipes-with-images.p.rapidapi.com"
}

# Function to search for recipes
def search_recipes(query):
    querystring = {"q": query}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data

# Function to extract recipe information
def extract_recipe_info(recipe):
    title = recipe.get('title', 'N/A')
    ingredients = recipe.get('ingredients', [])
    image_url = recipe.get('image', 'N/A')
    instructions_url = recipe.get('sourceURL', 'N/A')
    return title, ingredients, image_url, instructions_url

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the recipe query
@app.route('/recipe', methods=['POST'])
def get_recipe():
    query = request.form['query']
    data = search_recipes(query)
    try:
        recipe = data.get('recipes', [])[0]
        title, ingredients, image_url, instructions_url = extract_recipe_info(recipe)
        response = {
            "title": title,
            "ingredients": ingredients,
            "image_url": image_url,
            "instructions_url": instructions_url
        }
    except IndexError:
        response = {"error": "No recipe found."}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
