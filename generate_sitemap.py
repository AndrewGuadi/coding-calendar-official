import os
from datetime import datetime

output_dir = 'static_pages'
sitemap_path = 'sitemap.xml'

# Get the list of generated HTML files
pages = [f for f in os.listdir(output_dir) if f.endswith('.html')]

# Generate sitemap content
sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

for page in pages:
    sitemap_content += f"""
    <url>
        <loc>http://www.codingcalendar.com/static_pages/{page}</loc>
        <lastmod>{datetime.utcnow().date()}</lastmod>
    </url>
    """

sitemap_content += "</urlset>"

# Save the sitemap
with open(sitemap_path, 'w') as file:
    file.write(sitemap_content)

print("Sitemap generated successfully.")
