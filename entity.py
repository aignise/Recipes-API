import requests
import time
import json
from openai import OpenAI
import os

from dotenv import load_dotenv
load_dotenv()

def search_recipes(query):
    """Searches for recipes based on the given query using the Food Recipes with Images API."""
    url = "https://food-recipes-with-images.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "food-recipes-with-images.p.rapidapi.com"
    }
    querystring = {"q": query}
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return data

def create_thread():
    """Creates a thread for conversation."""
    thread = client.beta.threads.create()
    return thread.id

def start(thread_id, prompt):
    """Starts a conversation in the specified thread with the given prompt."""
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

def get_response(thread_id, assistant_id, prompt):
    """Retrieves the response from the OpenAI API."""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="Answer user questions using custom functions available to you."
    )
    
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == 'requires_action':
            submit_tool_outputs(thread_id, run.id, run_status, prompt)
        time.sleep(1)
    
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    response = messages.data[0].content[0].text.value
    return response

def submit_tool_outputs(thread_id, run_id, run_status, prompt):
    """Submits tool outputs to the OpenAI API."""
    output = search_recipes(prompt)
    output_str = json.dumps(output)
    
    tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
    
    # Construct tool outputs for each tool call
    tool_outputs = []
    for tool_call in tool_calls:
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": output_str
        })
    
    # Submit tool outputs to OpenAI API
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )


def extract_recipe_info(recipe):
    """Extracts relevant information from the recipe."""
    title = recipe.get('title', 'N/A')
    ingredients = recipe.get('ingredients', [])
    image_url = recipe.get('image', 'N/A')
    instructions_url = recipe.get('sourceURL', 'N/A')
    
    return title, ingredients, image_url, instructions_url

# Instantiate OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

