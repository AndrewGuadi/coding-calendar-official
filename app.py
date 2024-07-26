from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import json
from gpt_helpers import OpenAIHelper
from urllib.parse import unquote


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///methods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=False)

def get_current_day_of_year():
    now = datetime.utcnow()
    return now.timetuple().tm_yday

def query_database(day, language):
    return Method.query.filter_by(day=day, language=language).first()

def fetch_data_from_gpt(language, method):
    with open("openai.txt", 'r', encoding='utf-8') as file:
        api_key = file.read().strip()  # Read the API key from file
    
    intent_message = "Generate a programming method description and example code."
    openai_helper = OpenAIHelper(api_key, intent_message)
    
    prompt = f"Provide a detailed description and example for the method '{method}' in {language}."
    data = ""  # Assuming no additional context needed
    example = '{"method": "", "description": "", "example": ""}'  # Expected JSON format

    response = openai_helper.gpt_json(prompt, data, example)

    if response:
        # Ensure the example is a string
        response['example'] = str(response['example'])
        return response
    
    return {
        "method": method,
        "description": "No description available.",
        "example": "No example available."
    }


def save_data_to_database(day, language, data):
    method = Method(day=day, language=language, method=data["method"], description=data["description"], example=data["example"])
    db.session.add(method)
    db.session.commit()

def remove_method_from_json(language, method):
    with open('methods.json', 'r') as file:
        methods = json.load(file)
    
    # Normalize the language key to match the JSON keys
    language_key = language.lower()

    if method in methods.get(language_key, []):
        methods[language_key].remove(method)
    
    with open('methods.json', 'w') as file:
        json.dump(methods, file)


@app.route('/')
def index():
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "TypeScript", "Ruby", "Swift", "Go"]
    return render_template('index.html', languages=languages)


@app.route('/method/<language>', methods=['GET'])
def get_method(language):
    day = request.args.get('day')
    if day is None:
        day = get_current_day_of_year()
    else:
        day = int(day)

    decoded_language = unquote(language)
    data = query_database(day, decoded_language)
    
    if data is None:
        with open('methods.json', 'r') as file:
            methods = json.load(file)
        
        # Normalize the language key to match the JSON keys
        language_key = decoded_language.lower()
        print(f"Accessing methods for language key: {language_key}")  # Add logging
        
        if language_key in methods and methods[language_key]:
            method_name = methods[language_key][0]
            method_data = fetch_data_from_gpt(decoded_language, method_name)
            save_data_to_database(day, decoded_language, method_data)
            remove_method_from_json(decoded_language, method_name)
            data = method_data
        else:
            print(f"No methods found for language: {language_key}")  # Add logging
            return jsonify({"error": "No more methods available for this language."}), 404
    else:
        data = {
            "method": data.method,
            "description": data.description,
            "example": data.example
        }
    
    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
