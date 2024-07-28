import os
import json

# Directory to store generated HTML files
output_dir = 'static_pages'
os.makedirs(output_dir, exist_ok=True)

# Load methods from a JSON file (or database)
with open('methods.json', 'r') as file:
    methods = json.load(file)

# HTML template for each page
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
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{method_name}</h1>
        <p>{description}</p>
        <pre><code>{example}</code></pre>
    </div>
</body>
</html>
"""

# Generate HTML files for each method and language
page_names = []
for language, method_list in methods.items():
    for i, method_name in enumerate(method_list):
        title = f"{method_name} in {language} - Best Coding Practices"
        description = f"Learn how to use the {method_name} method in {language}. Find examples and best practices."
        keywords = f"{method_name}, {language}, Best Coding Practices, Programming Examples"

        # Generate HTML content
        html_content = html_template.format(
            title=title,
            description=description,
            keywords=keywords,
            method_name=method_name,
            description=f"Description for {method_name} in {language}.",
            example=f"Example code for {method_name} in {language}."
        )

        # Save the HTML file
        file_name = f"{output_dir}/{language.lower()}_{i+1}.html"
        with open(file_name, 'w') as output_file:
            output_file.write(html_content)
        
        # Append the file name to the list of page names
        page_names.append(file_name)

print("HTML files generated successfully.")
print("Generated page names:")
for page_name in page_names:
    print(page_name)
