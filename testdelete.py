from gpt_helpers import OpenAIHelper
from app import create_static_page


def fetch_data_from_gpt(language, method):
    with open("openai.txt", 'r', encoding='utf-8') as file:
        api_key = file.read().strip()  # Read the API key from file
    
    intent_message = "Generate a programming method description and example code."
    openai_helper = OpenAIHelper(api_key, intent_message)
    
    prompt = f"Provide a detailed description and example for the method '{method}' in {language}. [For examples you must only use python code as value - as it will directly used in code. Each example must include a complete example/clearly defined logic of usage of code]"
    data = ""  # Assuming no additional context needed
    example = '{"method": "", "description": "", "examples": {example_1": "", example_2: "", example_3:""} }'  # Expected JSON format
    
    response = openai_helper.gpt_json(prompt, data, example)

    if response:
        # Ensure the example is a string
        return response
    
    return {
        "method": method,
        "description": "No description available.",
        "example": "No example available."
    }




if __name__ == "__main__":

   result = fetch_data_from_gpt('python', 'upper')
   create_static_page("python", 1, result)