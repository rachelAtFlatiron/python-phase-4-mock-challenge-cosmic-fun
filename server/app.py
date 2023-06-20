from flask import Flask, request, make_response, jsonify, abort
from werkzeug.exceptions import UnprocessableEntity
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource 
from models import db, Scientist, Planet, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def index():
    response = make_response(
        {"message": "Hello Scientists!"}
    )
    return response 

class Scientists(Resource):
    def get(self): 
        q = Scientist.query.all()
        if not q: 
            abort(404, "Scientist not found")
        return make_response([s.to_dict(only=('id', 'name', 'field_of_study', 'avatar')) for s in q], 200)
    
    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(name=data.get('name'), field_of_study=data.get('field_of_study'), avatar=data.get('avatar'))
            #import ipdb; ipdb.set_trace()


            db.session.add(scientist)
            db.session.commit()
        except Exception: 
            #abort(422, "validation errors")
            return make_response({"errors": ["validation errors"]}, 422)
        return make_response(scientist.to_dict(only=('id', 'name', 'field_of_study', 'avatar')), 201)
api.add_resource(Scientists, '/scientists')

class OneScientist(Resource):
    def get(self, id):
        q = Scientist.query.filter_by(id=id).first()
        if not q: 
            abort(404, "Scientist not found")
        return make_response(q.to_dict(), 200) 
    def patch(self , id):
        q = Scientist.query.filter_by(id=id).first()
        if not q: 
            abort(404, "Scientist not found")
        try: 
            data = request.get_json()
            for attr in data: 
                setattr(q, attr, data.get(attr))
            db.session.add(q)
            db.session.commit() 
        except Exception:
            return make_response({"errors": ["validation errors"]}, 422)
        return make_response(q.to_dict(only=("id", "name", "field_of_study", "avatar")), 200)
    def delete(self, id):
        q = Scientist.query.filter_by(id=id).first()
        if not q: 
            abort(404, "Scientist not found")
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)
    
api.add_resource(OneScientist, '/scientists/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
