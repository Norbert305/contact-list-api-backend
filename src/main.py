"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact', methods=['GET'])
def get_contact():
    contacts = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts))
    return jsonify(all_contacts), 200

@app.route('/contact', methods=['POST'])
def add_new_contact():
    body = request.json
    new_contact = Contact(full_name= body["full_name"], email=body["email"], address=body["address"], phone=body["phone"])
    db.session.add(new_contact)
    db.session.commit()
    contacts = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts))
    return jsonify(all_contacts), 200

#return jsonify(response_body), 200

@app.route('/contact/<id>', methods=['PUT'])
def update_contact(id):
    body = request.json
    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)

    if "full_name" in body:
        contact.full_name = body["full_name"]
    if "email" in body:
        contact.email = body["email"]
    if "phone" in body:
        contact.phone = body["phone"]
    if "address" in body:
        contact.email = body["address"]
    db.session.commit()
    contacts = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts))
    return jsonify(all_contacts), 200


@app.route('/contact/<id>', methods=['DELETE'])
def delete_contact(id):

    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)
    db.session.delete(contact)
    db.session.commit()
    contacts = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts))
    return jsonify(all_contacts), 200


# return jsonify(response_body), 200



# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
