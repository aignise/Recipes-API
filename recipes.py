import requests
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import time
import json

load_dotenv()

url = "https://food-recipes-with-images.p.rapidapi.com/"
headers = {
	"X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"),
	"X-RapidAPI-Host": "food-recipes-with-images.p.rapidapi.com"
}

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

def search_recipes(query):
    """Searches for recipes based on the given query using the Food Recipes with Images API."""
    url = "https://food-recipes-with-images.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": "10293c49f1mshad7aa6bc1165ce9p19aed4jsnb7a764a892f7",
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

def get_response(thread_id, assistant_id):
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

def submit_tool_outputs(thread_id, run_id, run_status, query):
    """Submits tool outputs to the OpenAI API."""
    output = search_recipes(query)
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

if __name__ == "__main__":
    # Take prompt from user
    prompt = input("Enter your recipe query: ")

    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    thread_id = create_thread()
    start(thread_id, prompt)

    print("Waiting for response from OpenAI...")
    response = get_response(thread_id, assistant_id)

    print("Response from OpenAI:")
   

    try:
        data = json.loads(response)
        recipe = data.get('recipes', [])[0]
        
        title, ingredients, image_url, instructions_url = extract_recipe_info(recipe)
        
        print("Recipe Title:", title)
        print("Ingredients:")
        for ingredient in ingredients:
            print("-", ingredient)
        print("Recipe Image URL:", image_url)
        print("Instructions URL:", instructions_url)
    
    except json.decoder.JSONDecodeError:
        print("Error: Unable to decode JSON response from OpenAI API.")
        print("Response:", response)
    
    except IndexError:
        print("Error: No recipe found.")
