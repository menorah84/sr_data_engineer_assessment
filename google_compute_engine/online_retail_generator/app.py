from faker import Faker
from random import randint
from datetime import datetime
import json, requests, time


def init():
    
    with open('countries.json') as countries_file:
        countries = json.load(countries_file)
        
    with open('items.json') as items_file:
        items = json.load(items_file)
        
    fake = Faker()
    
    return fake, countries, items


def generate(fake, countries, items):
        
    x_invoice_no = fake.bothify(text='######')
    x_stock_code = fake.bothify(text='#####?')

    item = items[randint(0, len(items)-1)]
    x_description = item['Description']
    x_quantity = randint(1, 10)
    x_invoice_date = datetime.now().strftime("%Y-%m-%d %H:%M:00.000")
    x_unit_price = item['UnitPrice']
    x_customer_id = fake.bothify(text='#####')

    country = countries[randint(0, len(countries)-1)]
    x_country = country['name']
    geo = fake.local_latlng(country_code=country['code'])
    x_geolocation = f'POINT({geo[1]} {geo[0]})'
    # alternatively, using GeoJSON
    # x_geolocation = json.dumps({ "type": "Point", "coordinates": [ float(geo[1]), float(geo[0]) ]) })

    x_time_spent_seconds = randint(30, 900)
    x_sat_score = randint(1, 5)
    
    data = [{
        "InvoiceNo": x_invoice_no,
        "StockCode": x_stock_code,
        "Description": x_description,
        "Quantity": x_quantity,
        "InvoiceDate": x_invoice_date,
        "UnitPrice": x_unit_price,
        "CustomerID": x_customer_id,
        "Country": x_country,
        "Geolocation": x_geolocation,            
        "TimeSpentSeconds": x_time_spent_seconds,
        "SatScore": x_sat_score
    }]
    
    return data


if __name__ == "__main__":
    
    url = "https://us-central1-fl-uw-03.cloudfunctions.net/online-retail"
    
    payload = { 
        "data-source": "json-payload",
        "project": "fl-uw-03",
        "dataset": "avaloq",
        "table": "online_retail"
    }
    
    fake, countries, items = init()
    
    while(True):
        data = generate(fake, countries, items)
        payload['data'] = data
        resp = requests.post(url, json=payload)
        if resp.status_code == 200:
            print(data)
            print(resp.text)
        else:
            print(f'HTTP Response Code {resp.status_code}')
        time.sleep(randint(180, 900))
