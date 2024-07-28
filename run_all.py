from app import create_static_page, fetch_data_from_gpt, save_data_to_database, remove_method_from_json, app, db, Method
import json

def generate_all_pages():
    # Load the methods from methods.json
    with open('methods.json', 'r') as file:
        methods = json.load(file)

    # Loop through all the languages and days
    for language in methods.keys():
        for day in range(1, 366):  # Assuming you want to generate pages for each day of the year
            # Check if the method for this day and language already exists in the database
            with app.app_context():
                data = Method.query.filter_by(day=day, language=language.capitalize()).first()
                if not data:
                    # If not, fetch data from GPT and save it to the database
                    if methods[language]:
                        method_name = methods[language][0]
                        method_data = fetch_data_from_gpt(language, method_name)
                        save_data_to_database(day, language.capitalize(), method_data)
                        remove_method_from_json(language, method_name)
                        create_static_page(language, day, method_data)
                        print(f"Generated page for {language.capitalize()} on day {day}")
                    else:
                        print(f"No more methods available for language: {language.capitalize()}")
                        continue
                else:
                    # If data already exists, create the static page using existing data
                    existing_data = {
                        "method": data.method,
                        "description": data.description,
                        "example": data.example
                    }
                    create_static_page(language, day, existing_data)
                    print(f"Page for {language.capitalize()} on day {day} already exists in the database")

if __name__ == "__main__":
    with app.app_context():
        generate_all_pages()