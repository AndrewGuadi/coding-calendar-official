from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///methods.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

def get_current_day_of_year():
    now = datetime.utcnow()
    return now.timetuple().tm_yday

class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=False)

def query_database(day, language):
    return Method.query.filter_by(day=day, language=language).first()

def fetch_data_from_gpt(language):
    return {
        "method": "example_method",
        "description": "This is an example method description.",
        "example": "def example_method():\n    pass"
    }

def save_data_to_database(day, language, data):
    method = Method(day=day, language=language, method=data["method"], description=data["description"], example=data["example"])
    db.session.add(method)
    db.session.commit()

def remove_method_from_json(language, method):
    with open('methods.json', 'r') as file:
        methods = json.load(file)
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
        data = fetch_data_from_gpt(language)
        save_data_to_database(day, language, data)
        remove_method_from_json(language, data["method"])
    else:
        data = {
            "method": data.method,
            "description": data.description,
            "example": data.example
        }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
