from flask import Flask, jsonify, render_template, request, send_from_directory, abort, Response
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from datetime import datetime, timedelta
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

def create_static_page(language, day, method_data):
    language_key = language.lower()
    file_name = f"{language_key}_{day}.html"
    output_dir = 'static_pages'
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate the formatted date
    base_date = datetime(datetime.now().year, 1, 1) + timedelta(days=day - 1)
    formatted_date = base_date.strftime('%Y-%m-%d')
    
    # HTML template for the static page
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="description" content="{description}">
        <meta name="keywords" content="{keywords}">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #333;
                color: #00FF00;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: #000000;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }}
            h1 {{
                text-align: center;
            }}
            pre {{
                background: #444444;
                color: #00FF00;
                padding: 10px;
                border-radius: 4px;
                overflow-x: auto;
            }}
            code {{
                color: #00FF00;
            }}
            .date-container {{
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }}
            .date {{
                background: black;
                color: #00FF00; /* Matrix green text */
                font-family: 'Courier New', Courier, monospace;
                font-size: 1.5em;
                padding: 10px 20px;
                border: 2px solid #00FF00;
                border-radius: 8px;
                text-align: center;
                display: inline-block;
            }}
            .arrow {{
                cursor: pointer;
                font-size: 2em;
                margin: 0 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="date-container">
                <div class="arrow" id="left-arrow">&#8592;</div>
                <div class="date" id="date" data-day-of-year="{day}">{formatted_date}</div>
                <div class="arrow" id="right-arrow">&#8594;</div>
            </div>
            <h1>{method_name}</h1>
            <p>{method_description}</p>
            <pre><code>{example}</code></pre>
        </div>
        <script>
            function navigateToDate(language, dayOfYear) {{
                window.location.href = `/?language=${{language}}&day=${{dayOfYear}}`;
            }}

            document.getElementById('left-arrow').addEventListener('click', function() {{
                let currentDayOfYear = parseInt(document.getElementById('date').getAttribute('data-day-of-year'));
                currentDayOfYear = currentDayOfYear > 1 ? currentDayOfYear - 1 : 365;
                navigateToDate('{language}', currentDayOfYear);
            }});

            document.getElementById('right-arrow').addEventListener('click', function() {{
                let currentDayOfYear = parseInt(document.getElementById('date').getAttribute('data-day-of-year'));
                currentDayOfYear = currentDayOfYear < 365 ? currentDayOfYear + 1 : 1;
                navigateToDate('{language}', currentDayOfYear);
            }});
        </script>
    </body>
    </html>
    """
    
    title = f"{method_data['method']} in {language} - Best Coding Practices"
    description = f"Learn how to use the {method_data['method']} method in {language}. Find examples and best practices."
    keywords = f"{method_data['method']}, {language}, Best Coding Practices, Programming Examples"

    # Generate HTML content
    html_content = html_template.format(
        title=title,
        description=description,
        keywords=keywords,
        method_name=method_data['method'],
        method_description=method_data['description'],
        example=method_data['example'],
        formatted_date=formatted_date,
        day=day,
        language=language
    )
    
    # Save the HTML file
    with open(os.path.join(output_dir, file_name), 'w') as output_file:
        output_file.write(html_content)


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
            create_static_page(decoded_language, day, method_data)
            data = method_data
        else:
            print(f"No methods found for language: {language_key}")  # Add logging
            return jsonify({"error": "No more methods available for this language."}), 404
    else:
        static_page_path = f"static_pages/{decoded_language.lower()}_{day}.html"
        if os.path.exists(static_page_path):
            return send_from_directory('static_pages', f"{decoded_language.lower()}_{day}.html")
        else:
            data = {
                "method": data.method,
                "description": data.description,
                "example": data.example
            }
    
    return jsonify(data)

@app.route('/static_pages/<path:filename>')
def serve_static_page(filename):
    try:
        return send_from_directory('static_pages', filename)
    except FileNotFoundError:
        abort(404)

def generate_sitemap():
    pages = []
    static_pages_dir = 'static_pages'
    
    for filename in os.listdir(static_pages_dir):
        if filename.endswith('.html'):
            pages.append(f'http://www.codingcalendar.com/{static_pages_dir}/{filename}')
    
    sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

    for page in pages:
        sitemap_content += f"""
    <url>
        <loc>{page}</loc>
        <lastmod>{datetime.utcnow().date()}</lastmod>
    </url>
"""
    sitemap_content += "</urlset>"
    return sitemap_content

@app.route('/sitemap.xml')
def sitemap():
    sitemap_xml = generate_sitemap()
    return Response(sitemap_xml, mimetype='application/xml')

if __name__ == '__main__':
    app.run(debug=True)
