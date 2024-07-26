from flask import Flask, jsonify, render_template
from datetime import datetime
import sqlite3
import json

app = Flask(__name__)

def get_current_day_of_year():
    now = datetime.utcnow()
    return now.timetuple().tm_yday

def query_database(day, language):
    conn = sqlite3.connect('methods.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM methods WHERE day=? AND language=?", (day, language))
    result = cursor.fetchone()
    conn.close()
    return result

def fetch_data_from_gpt(language):
    # For example purposes, we'll return a mock response
    return {
        "method": "example_method",
        "description": "This is an example method description.",
        "example": "def example_method():\n    pass"
    }

def save_data_to_database(day, language, data):
    conn = sqlite3.connect('methods.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO methods (day, language, method, description, example) VALUES (?, ?, ?, ?, ?)",
                   (day, language, data["method"], data["description"], data["example"]))
    conn.commit()
    conn.close()

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
            "method": data[2],
            "description": data[3],
            "example": data[4]
        }
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
