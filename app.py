from flask import Flask, render_template, request, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import json
from urllib.parse import unquote, quote
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

def fetch_data_from_gpt(language, method):
    with open("openai.txt", 'r', encoding='utf-8') as file:
        api_key = file.read().strip()
    
    intent_message = "Generate a programming method description and example code."
    openai_helper = OpenAIHelper(api_key, intent_message)
    
    prompt = f"Provide a detailed description and example for the method '{method}' in {language}. [For examples you must only use python code as value - as it will directly used in code. Each example must include a complete example/clearly defined logic of usage of code]"
    data = ""
    example = '{"method": "", "description": "", "examples": {example_1": "", example_2: "", example_3:""} }'
    
    response = openai_helper.gpt_json(prompt, data, example)

    if response:
        return response
    
    return {
        "method": method,
        "description": "No description available.",
        "example": {
            "example_1": "No example available.",
            "example_2": "No example available.",
            "example_3": "No example available."
        }
    }

def save_data_to_database(day, language, data):
    language = language.capitalize()
    language_mapping = {
        "C#": "csharp",
        "C++": "cplus",
        'C%23' : 'csharp',
        'C%2B%2B': 'cplus'
    }
    safe_language = language_mapping.get(language, language)
    examples_data = json.dumps(data['examples'])
    method = Method(day=day, language=safe_language, method=data["method"], description=data["description"], example=examples_data)
    db.session.add(method)
    db.session.commit()

def get_current_day_of_year():
    now = datetime.utcnow()
    return now.timetuple().tm_yday

def query_database(day, language):
    language = language.capitalize()
    return Method.query.filter_by(day=day, language=language).first()

@app.route('/')
def index():
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "Ruby", "Swift", "Go"]
    return render_template('index.html', languages=languages)

@app.route('/method/<language>/<int:day>', methods=['GET'])
def get_method(language, day):
    language_mapping = {
        "C#": "csharp",
        "C++": "cplus",
        'C%23' : 'csharp',
        'C%2B%2B': 'cplus'
    }
    decoded_language = unquote(language)
    safe_language = language_mapping.get(decoded_language, decoded_language)
    
    query_data = query_database(day, safe_language)
    if not query_data:
        with open('methods_updated.json', 'r', encoding='utf-8') as file:
            method_data = json.load(file)
        json_language = safe_language.lower()
        method_list = method_data[language.lower()]
        method_name = method_list[day - 1]  # Adjusting for 0-based index
        gpt_data = fetch_data_from_gpt(safe_language, method_name)
        save_data_to_database(day, safe_language, gpt_data)
        query_data = query_database(day, safe_language)
    
    if not query_data:
        return render_template('404.html'), 404

    base_date = datetime(datetime.now().year, 1, 1) + timedelta(days=day - 1)
    formatted_date = base_date.strftime('%B %d, %Y')

    data = {
        "method": query_data.method,
        "description": query_data.description,
    }
    examples = json.loads(query_data.example)
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "Ruby", "Swift", "Go"]

    return render_template('method.html', data=data, examples=examples, day=day, language=language, formatted_date=formatted_date, languages=languages)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    language_mapping = {
        "csharp": "C#",
        "cplus": "C++"
    }
    
    methods = Method.query.all()
    urls = []
    
    # Add index page URL
    index_url = "http://www.codingcalendar.com/"
    urls.append(index_url)
    
    for method in methods:
        language_display = language_mapping.get(method.language, method.language)
        language_encoded = quote(language_display)
        url = f"http://www.codingcalendar.com/method/{language_encoded}/{method.day}"
        urls.append(url)
    
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
    for url in urls:
        sitemap_xml += f"""
    <url>
        <loc>{url}</loc>
        <lastmod>{datetime.utcnow().date()}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
"""
    sitemap_xml += "</urlset>"
    return Response(sitemap_xml, mimetype='application/xml')
    
if __name__ == '__main__':
    app.run(debug=True)
