import selenium
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import ast
import json
import pymysql
from flask import Flask, jsonify, request

products = [] 
keyword = 'hair care'


# Initialize Flask application
app = Flask(__name__)

# Route for the main page of the application
@app.route(rule='/', methods=['GET'])
def main():
    return "Welcome to Scrappy World"

# Route for scraping product information from daraz website
@app.route(rule='/daraz/<string:keyword>/', methods=['GET'])
def call_daraz(keyword):
    get_daraz_product_info(keyword)
    return jsonify(products)


def get_daraz_product_info(keyword):
    date = datetime.now()
    formatdate = date.strftime("%Y-%m-%d")
    session = requests.Session()
    page_no = 1 
    while True:
        url = f"https://www.daraz.pk/catalog/?page={page_no}&q={keyword}"
        response = session.get(url)
        page_source = response.text
        type(page_source)
        if page_source.find(',"listItems":') == -1:
            break
        strlist = page_source.split(',"listItems":')[1].split(',"breadcrumb":[{')[0]
        product_wrapper = json.loads(strlist) #ast.literal_eval(strlist)
        for i, product in enumerate(product_wrapper):
            print(i)
            if(len(products)== 100):
                break
            name = product['name'].strip()
            image_url = product['image'].strip()
            product_url = product['productUrl'].replace('//www','www').strip()
            unit_sale_price = product['priceShow'].replace('Rs. ','').strip()
            try:
                unit_price = product['originalPriceShow'].replace('Rs. ','').strip()
            except:
                unit_price = unit_sale_price
            id = product['nid'].strip()
            products.append({
                    "currency": 'PKR',
                    "Id": id,
                    "Name": name,
                    "image url": image_url,
                    "unit price": unit_price,
                    "unit_sale_price": unit_sale_price,
                    "URL": url,
                    "Data of Extraction": formatdate
                })
        if(len(products) == 100):
            break
        else:
            page_no +=1

    #write_to_db('daraz_products', keyword)
    session.close()   

def write_to_db(table_name, keyword):
    conn = pymysql.connect(
    host="",
    user="",
    password="",
    database=""
    )

    cursor = conn.cursor()
    df = pd.DataFrame(products)
    for index, row in df.iterrows():
        sql = f"INSERT INTO {table_name} (keyword, currency, Id, Name, image_url, unit_price, unit_sale_price, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (keyword, row["currency"], row["Id"], row["Name"],row["image url"], row["unit price"], row["unit_sale_price"], row["URL"]) 
        cursor.execute(sql, values)

    conn.commit()
    cursor.close()
    conn.close()



if __name__=='__main__':
    app.run(host="0.0.0.0", port="8080", debug=True)