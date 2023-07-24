import requests
from bs4 import BeautifulSoup
import csv

def scrape_product_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Scrape Description
        description_element = soup.find('meta', {'name': 'description'})
        description = description_element['content'] if description_element else "N/A"

        # Scrape ASIN
        asin_element = soup.find('th', string='ASIN')
        asin = asin_element.find_next_sibling('td').text.strip() if asin_element else "N/A"

        # Scrape Product Description
        product_description_element = soup.find('div', {'id': 'productDescription'})
        product_description = product_description_element.get_text().strip() if product_description_element else "N/A"

        # Scrape Manufacturer
        manufacturer_element = soup.find('a', {'id': 'bylineInfo'})
        manufacturer = manufacturer_element.text.strip() if manufacturer_element else "N/A"

        return {
            "Description": description,
            "ASIN": asin,
            "Product Description": product_description,
            "Manufacturer": manufacturer
        }

    return None

def scrape_products(url):
    data_list = []
    while url:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('div', {'data-component-type': 's-search-result'})
            for product in products:
                product_url = "https://www.amazon.in" + product.find('a', class_='a-link-normal')['href']
                product_name = product.find('span', class_='a-text-normal').text
            
                product_price_element = product.find('span', class_='a-offscreen')
                product_price = product_price_element.text if product_price_element else "N/A"

                rating_element = product.find('span', class_='a-icon-alt')
                rating = rating_element.text.split()[0] if rating_element else "N/A"

                num_reviews_element = product.find('span', {'class': 'a-size-base', 'dir': 'auto'})
                num_reviews = num_reviews_element.text.split()[0] if num_reviews_element else "N/A"

                # Scrape additional details from the product page
                product_details = scrape_product_details(product_url)
                if product_details:
                    data_list.append({
                        "Product URL": product_url,
                        "Product Name": product_name,
                        "Product Price": product_price,
                        "Rating": rating,
                        "Number of Reviews": num_reviews,
                        "Description": product_details["Description"],
                        "ASIN": product_details["ASIN"],
                        "Product Description": product_details["Product Description"],
                        "Manufacturer": product_details["Manufacturer"]
                    })
            # Check if there is a next page
            next_page_element = soup.find('li', {'class': 'a-last'})
            next_page_url = "https://www.amazon.in" + next_page_element.find('a')['href'] if next_page_element else None
            url = next_page_url

    return data_list

# Scrape 200 pages of product listing
all_data = []
for page_num in range(1, 201):
    page_url = f"https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1&page={page_num}"
    data = scrape_products(page_url)
    all_data.extend(data)

# Export the data to a CSV file
csv_file = "amazon_products.csv"
csv_columns = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", 
               "Description", "ASIN", "Product Description", "Manufacturer"]

try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in all_data:
            writer.writerow(data)
    print("Data exported to", csv_file)
except IOError:
    print("I/O error occurred while writing to the CSV file.")
