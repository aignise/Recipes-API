import time
import openai
import os
import json
from function import search_recipes, extract_recipe_info
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=openai_api_key)

def create_thread():
    thread = client.beta.threads.create()
    return thread.id

def start(thread_id, prompt):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt
    )

def get_response(thread_id, assistant_id):
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
    output = search_recipes(query)
    output_str = json.dumps(output)
    
    tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
    
    tool_outputs = []
    for tool_call in tool_calls:
        tool_outputs.append({
            "tool_call_id": tool_call.id,
            "output": output_str
        })
    
    client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs
    )

if __name__ == "__main__":
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
