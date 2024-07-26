from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import json
from gpt_helpers import OpenAIHelper

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
        api_key = file.read()  # Replace with your OpenAI API key
    intent_message = "Generate a programming method description and example code."
    openai_helper = OpenAIHelper(api_key, intent_message)
    prompt = f"Provide a detailed description and example for the method '{method}' in {language}."
    response = openai_helper.gpt_4(prompt)
    return {
        "method": method,
        "description": response.split('\n\n')[0],
        "example": '\n'.join(response.split('\n\n')[1:])
    }

def save_data_to_database(day, language, data):
    method = Method(day=day, language=language, method=data["method"], description=data["description"], example=data["example"])
    db.session.add(method)
    db.session.commit()

def remove_method_from_json(language, method):
    with open('methods.json', 'r') as file:
        methods = json.load(file)
    if method in methods[language]:
        methods[language].remove(method)
    with open('methods.json', 'w') as file:
        json.dump(methods, file)

@app.route('/')
def index():
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "TypeScript", "Ruby", "Swift", "Go"]
    return render_template('index.html', languages=languages)

@app.route('/method/<language>', methods=['GET'])
def get_method(language):
    day = get_current_day_of_year()
    data = query_database(day, language)
    
    if data is None:
        with open('methods.json', 'r') as file:
            methods = json.load(file)
        if methods[language]:
            method_name = methods[language][0]
            method_data = fetch_data_from_gpt(language, method_name)
            save_data_to_database(day, language, method_data)
            remove_method_from_json(language, method_name)
            data = method_data
        else:
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
