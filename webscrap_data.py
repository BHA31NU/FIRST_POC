from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)

# Configuring Flask app with PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:8688@localhost/poc'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the table scheme for 'services' table
class Service(db.Model):
    __tablename__ = 'services'
    id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(255),nullable=False)
    service_metadata = db.Column(db.String(255),nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Create the table
with app.app_context():
    db.create_all()
    print("Table created successfully!")

# Function to scrape data from the webpage
def scrape_data(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text,'html.parser')
    
    services = soup.find_all('h2')
    
    # services_list = services[:6]
    
    sibling_divs = []
    
    for service in services:
        
    # Navigate to the parent and find the next sibling div
        sibling_div = service.parent.parent.parent.find_next_sibling('div')
        sibling_divs.append(sibling_div)
        
    span_seen = set()
    services_dict = {}
    for i, div in enumerate(sibling_divs):
        if div:
            spans = div.find_all('span')
            sub_services=[]
            for span in spans:
                span_text = span.text.strip()
                if span_text not in span_seen:
                    span_seen.add(span_text)
                    sub_services.append(span_text)
                services_dict[services[i].text.strip().lower().replace(" ","_")] = sub_services

    del services_dict["let's_build_the_future_together!"]
    # del services_dict["thank_you!"]
    return services_dict

# Function to store scraped data into the `services` table
def store_data_table(data):
    

    for service, sub_services in data.items():
        for sub_service in sub_services:
            new_entry = Service(service_name=sub_service, service_metadata = service)
            db.session.add(new_entry)
        db.session.commit()

#test
@app.route('/deepak')
def test():
    return jsonify({"title":"Hello"})


# API endpoint to trigger web scraping and save data to the `services` table
@app.route('/fetch_services/', methods=['POST'])
def scrape_and_save():

    url = "https://www.gleecus.com/services/"
    
    if not url:
        return jsonify({"error":"URL is required"}), 400

    #Scrape data
    scraped_data = scrape_data(url)

    #Store scraped data in table
    store_data_table(scraped_data)

    return jsonify({"message":"Data scraped and saved to services table succesfully."}),200

# API endpoint to retrieve data from the `services` table
@app.route('/get-service/<service_name>',methods=['GET'])
def get_service(service_name):
    service_name = service_name.strip()

    results = Service.query.filter_by(service_metadata=service_name).all()
    data = [{
                "id":row.id,
                "service_name":row.service_name,
                "meta_data":row.service_metadata,
                "timestamp":row.timestamp
                } for row in results]

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
