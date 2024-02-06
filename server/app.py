#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ' '


@app.route('/scientists', methods=['GET','POST'])
def get_scientists(): 
    try:
        if request.method == 'GET':
            print("here")
            scientists_dict = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]
            print("got scientists")
            response = make_response(scientists_dict,200)

        elif request.method == 'POST':
            if request.headers.get("Content-Type") == 'application/json':
                form_data = request.get_json()
            else:
                form_data = request.form

            new_scientist = Scientist(
                name = form_data['name'],
                field_of_study = form_data['field_of_study']
                )
            db.session.add(new_scientist)
            db.session.commit()

            response = make_response(new_scientist.to_dict, 201)
    except: 
        response = make_response({"errors" : ["validation errors"]},400)
    return response

@app.route('/scientists/<int:id>', methods=['GET','PATCH','DELETE'])
def scientist_by_id(id):
    try: 
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if request.method == 'GET':
            response = make_response(scientist.to_dict(),200)

        elif request.method == 'PATCH':
            try:
                if request.headers.get("Content-Type") == 'application/json':
                    form_data = request.get_json()
                else:
                    form_data = request.form

                for attr in form_data: 
                    setattr(scientist, attr, form_data[attr])

                db.session.commit()
                response = make_response(scientist.to_dict(), 202)
            except: 
                response = make_response({"errors" : "Scientist not found"}, 404)
        elif request.method == 'DELETE':
            db.session.delete(scientist)
            db.session.commit()
            response = make_response({'error':'Scientist not found'},204)

    except: 
        response = make_response({"error" : "Scientist not found"},404)
    return response

@app.route('/planets/')
def get_planets(): 
    try: 
        print("here")
        planets = [planet.to_dict() for planet in Planet.query.all()]
        print("here-2")
        response = make_response(planets,200)
        print("here-3")

    except: 
        response = make_response({"ERROR" : "BAD REQUEST"},400)
    return response

@app.route('/missions/', methods=['POST'])
def create_mission():
    try: 
        if request.headers.get("Content-Type") == 'application/json':
            form_data = request.get_json()
        else:
            form_data = request.form
        new_mission = Mission(
            name = form_data['name'], 
            scientist_id = form_data['scientist_id'],
            planet_id = form_data['planet_id']
        )

        db.session.add(new_mission)
        db.session.commit()
        
        response = make_response(new_mission.to_dict(), 201)

    except: 
        response = make_response({"errors" : ["validation errors"]},400)
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
