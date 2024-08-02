from flask import Flask, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
import json
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
    language = language.capitalize()
    return Method.query.filter_by(day=day, language=language).first()

@app.route('/')
def index():
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "TypeScript", "Ruby", "Swift", "Go"]
    return render_template('index.html', languages=languages)

@app.route('/method/<language>/<int:day>', methods=['GET'])
def get_method(language, day):
    language_mapping = {
        "C#": "csharp",
        "C++": "cplus"
    }
    decoded_language = unquote(language)
    safe_language = language_mapping.get(decoded_language, decoded_language)
    print(safe_language)
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
    languages = ["Python", "JavaScript", "Java", "C#", "C++", "PHP", "TypeScript", "Ruby", "Swift", "Go"]

    return render_template('method.html', data=data, examples=examples, day=day, language=language, formatted_date=formatted_date, languages=languages)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
