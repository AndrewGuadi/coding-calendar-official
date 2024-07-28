import json
from gpt_helpers import OpenAIHelper

# Load existing methods from JSON
with open('methods.json', 'r') as file:
    methods = json.load(file)

# OpenAI API key
with open("openai.txt", 'r', encoding='utf-8') as file:
    api_key = file.read().strip()  # Read the API key from file

intent_message = "Generate unique programming methods."
openai_helper = OpenAIHelper(api_key, intent_message)

for language, method_list in methods.items():
    if len(method_list) < 365:
        # Prepare the prompt
        existing_methods = ", ".join(method_list)
        prompt = f"Generate a list of unique {language} programming methods that are not currently included in the following list: {existing_methods}. Provide only new methods in an array format."

        # Example structure expected from GPT-4
        example = '["new_method1", "new_method2", "new_method3", "..."]'

        # Fetch new methods from GPT-4
        response = openai_helper.gpt_json(prompt, "", example)
        
        if response:
            new_methods = response
            # Ensure there are no duplicates
            unique_new_methods = [method for method in new_methods if method not in method_list]
            # Append new unique methods to the existing list until it reaches 365
            methods[language].extend(unique_new_methods)
            
            # If the count is still less than 365, repeat methods
            while len(methods[language]) < 365:
                methods[language].extend(methods[language][:365 - len(methods[language])])

# Save the updated methods back to JSON
with open('methods_updated.json', 'w') as file:
    json.dump(methods, file, indent=4)

print("Updated methods saved to methods_updated.json")
