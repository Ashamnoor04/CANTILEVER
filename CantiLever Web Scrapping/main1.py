# main_app.py
import requests
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, request
import os

# --- 1. Web Scraping ---
def scrape_products():
    """
    Scrapes product data from a dummy e-commerce site.
    """
    url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []
    for item in soup.select('.thumbnail'):
        title = item.select_one('.title').get_text(strip=True)
        price = item.select_one('.price').get_text(strip=True)
        # Ratings are not explicitly available on this test site, so we'll generate some dummy data
        rating = round(np.random.uniform(3.5, 5.0), 1)
        description = item.select_one('.description').get_text(strip=True)

        products.append({
            'title': title,
            'price': float(price.replace('$', '')),
            'rating': rating,
            'description': description
        })
    return pd.DataFrame(products)

# --- 2. Data Storage ---
def save_to_excel(df, filename="products.xlsx"):
    """
    Saves the DataFrame to an Excel file.
    """
    df.to_excel(filename, index=False)
    print(f"Data saved to {filename}")

# --- 3. Data Visualization ---
def create_visualizations(df):
    """
    Creates and saves visualizations for product prices and ratings.
    """
    if not os.path.exists('static'):
        os.makedirs('static')

    # Price Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['price'], kde=True)
    plt.title('Product Price Distribution')
    plt.xlabel('Price ($)')
    plt.ylabel('Frequency')
    plt.savefig('static/price_distribution.png')
    plt.close()
    print("Price distribution plot saved.")

    # Rating Distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(df['rating'], kde=True, bins=10)
    plt.title('Product Rating Distribution')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.savefig('static/rating_distribution.png')
    plt.close()
    print("Rating distribution plot saved.")

# --- 4. Flask Web Application ---
app = Flask(__name__)

# Scrape data and create visualizations when the app starts
products_df = scrape_products()
save_to_excel(products_df)
create_visualizations(products_df)

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Renders the main page with product data and search functionality.
    """
    search_query = request.form.get('search', '')
    if search_query:
        filtered_df = products_df[products_df['title'].str.contains(search_query, case=False)]
    else:
        filtered_df = products_df
    return render_template('index.html', products=filtered_df.to_dict('records'))

if __name__ == '__main__':
    # Create a templates folder if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create the index.html file
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>E-commerce Scraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
            }
        </style>
    </head>
    <body class="bg-gray-100 text-gray-800">
        <div class="container mx-auto p-4 md:p-8">
            <h1 class="text-3xl md:text-4xl font-bold text-center mb-8">E-commerce Product Dashboard</h1>

            <!-- Search Form -->
            <div class="mb-8">
                <form method="POST" action="/" class="flex justify-center">
                    <input type="text" name="search" placeholder="Search for a product..." class="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <button type="submit" class="bg-blue-600 text-white px-6 py-2 rounded-r-md hover:bg-blue-700 transition">Search</button>
                </form>
            </div>

            <!-- Data Table -->
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-2xl font-semibold mb-4">Scraped Products</h2>
                <div class="overflow-x-auto">
                    <table class="min-w-full bg-white">
                        <thead class="bg-gray-200">
                            <tr>
                                <th class="py-3 px-4 text-left">Title</th>
                                <th class="py-3 px-4 text-left">Price ($)</th>
                                <th class="py-3 px-4 text-left">Rating</th>
                                <th class="py-3 px-4 text-left">Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for product in products %}
                            <tr class="border-b">
                                <td class="py-3 px-4">{{ product.title }}</td>
                                <td class="py-3 px-4">{{ product.price }}</td>
                                <td class="py-3 px-4">{{ product.rating }}</td>
                                <td class="py-3 px-4">{{ product.description }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Visualizations -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h2 class="text-2xl font-semibold mb-4">Price Distribution</h2>
                    <img src="/static/price_distribution.png" alt="Price Distribution" class="w-full h-auto rounded-md">
                </div>
                <div class="bg-white p-6 rounded-lg shadow-md">
                    <h2 class="text-2xl font-semibold mb-4">Rating Distribution</h2>
                    <img src="/static/rating_distribution.png" alt="Rating Distribution" class="w-full h-auto rounded-md">
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    with open("templates/index.html", "w") as f:
        f.write(html_template)

    app.run(debug=True)
