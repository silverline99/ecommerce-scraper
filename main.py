import pandas as pd
from bs4 import BeautifulSoup
import requests
from time import sleep
import re


"""
E-commerce web scraping tool
customized for scraping product data from the eshop https://www.online-textil.cz
for the product category of shirts
"""


# Loading the file containing the product urls to be extracted
with open("online_textil_04kosile_2020-09-24.html", "r") as f:
    shirts = f.read()
soup = BeautifulSoup(shirts, 'html.parser')


wanted_list = []
for link in soup.find_all('a'):
    output = str(link.get('class'))
    if output != "None":
        output_clean = str(output[2:-2])
        if output_clean == "item-list__link":
            # "item-list__link" is an unique identifier
            # used on http://online-textil.cz/ website
            # for other sites the identifier will be different
            print(link.get('href'))
            wanted_link = link.get('href')
            wanted_list.append(wanted_link)
print(len(wanted_list))  # Prints the number of relevant product links that are included

urls = []
for path in wanted_list:
    url = "https://online-textil.cz" + path
    urls.append(url)
print(urls)
print(len(urls))  # CHECK that the number of relevant product links remained the same :)


product_names = []
product_categories = []
product_prices = []
product_codes = []
product_colors = []

for product_url in urls:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'
    }
    r = requests.get(product_url, headers=headers)
    product_soup = BeautifulSoup(r.text, 'html.parser')

    # Extraction of product names
    product_name = product_soup.find('h1', {'itemprop': "name"}).text
    product_names.append(product_name)

    # Extraction of product categories
    category_raw = product_soup.find('h1', {'itemprop': "name"}).text
    category_list = re.findall(r'(?:(?<=^)|(?<=[^.]))\s+([A-Z][a-z]+)', category_raw)
    if not category_list:
        # CHECK that no word begins with a capital letter in a product name
        kategorie = "BEZ KATEGORIE"
    else:
        kategorie = str(category_list[0])
    product_categories.append(kategorie)

    # Extraction of product prices
    product_price = product_soup.find('span', {'class': 'price-one__single'}).text[:-9]
    product_prices.append(product_price)

    # Extraction of product codes
    product_code = product_soup.find('span', {'itemprop': 'sku'}).text
    product_codes.append(product_code)

    # Extraction of product codes
    barva_produktu = product_url.rsplit("/", 1)[-1]
    product_colors.append(barva_produktu)

    sleep(0.5)

# Creating a dataframe from lists
shirts_df = pd.DataFrame(
    zip(product_codes, product_names, product_categories, urls, product_prices, product_colors),
    columns=['Kód produktu',
             'Název produktu',
             'Kategorie produktu',
             'URL produktu',
             'Cena produktu bez DPH',
             'Barva produktu'
             ])
print(shirts_df)

# Saving the dataframe into .csv file
shirts_df.to_csv(r'online_textil_01shirts_scrape.csv', index=False, encoding='utf-8-sig')
