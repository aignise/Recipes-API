import os
from dotenv import load_dotenv
from entity import create_thread, start, get_response, extract_recipe_info
import json

load_dotenv()

def main():
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    thread_id = create_thread()

    while True:
        # Ask the user if they require recipe assistance or general assistance
        assistance_type = input("What kind of assistance do you need? (recipe/general): ").lower()

        if assistance_type == "recipe":
            # Take recipe query from the user
            prompt = input("Enter your recipe query: ")
            start(thread_id, prompt)

            print("Waiting for response from OpenAI...")
            response = get_response(thread_id, assistant_id, prompt)

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

        elif assistance_type == "general":
            # Take general query from the user
            general_query = input("What is your question or query? ")
            start(thread_id, general_query)
            response = get_response(thread_id, assistant_id, general_query)
            print("Response:", response)

        else:
            print("Invalid input. Please enter 'recipe' or 'general'.")

        # Ask if the user needs further assistance or wants to exit
        while True:
            further_assistance = input("Do you need further assistance? (yes/no): ").lower()
            if further_assistance in ["yes", "no"]:
                break
            else:
                print("Please enter 'yes' or 'no'.")

        if further_assistance == "no":
            print("Thank you for using the assistant. Goodbye!")
            break

if __name__ == "__main__":
    main()

