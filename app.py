from flask import Flask, request, render_template, jsonify
import os
from dotenv import load_dotenv
from function import search_recipes, extract_recipe_info
load_dotenv()

app = Flask(__name__)

# Yummly API URL and headers
url = "https://food-recipes-with-images.p.rapidapi.com/"
headers = {
    "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
    "X-RapidAPI-Host": "food-recipes-with-images.p.rapidapi.com"
}

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
