from flask import Flask, request, make_response, jsonify, abort
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

# use if not q for 404s (not found - DELETE, GET, PATCH)
# use try/except for 422s (unprocessable entity - POST, PATCH)
class Scientists(Resource):
    def get(self):
        q = Scientist.query.all()
        s_dict = [s.to_dict(only=('id', 'name', 'field_of_study', 'avatar')) for s in q]
        res = make_response(s_dict, 200)
        return res 
    
    def post(self):
        #1. get data
        data = request.get_json()
        try:
            #2. create instance
            sc = Scientist(name=data.get('name'), field_of_study=data.get('field_of_study'), avatar=data.get('avatar'))
            #3. add to db 
            db.session.add(sc)
            db.session.commit()
        except Exception: 
            #422 - UnprocessableEntity
            return make_response({"error": ["validation errors"]}, 422)
            #abort(422, "message")
        return make_response(sc.to_dict(), 201)
api.add_resource(Scientists, '/scientists')

class OneScientist(Resource):
    def get(self, id):
        import ipdb; ipdb.set_trace()
        q = Scientist.query.filter_by(id=id).first()
        #if no corresponding scientist was found
        if not q:
            abort(404, "Scientist not found")
            #return make_response({"error": "not found"}, 404)
        return make_response(q.to_dict(only=('id', 'name', 'avatar', 'field_of_study')), 200)
    def patch(self, id):
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
            #unprocessable entity
            abort(422, {"errors": "validation errors"})
        #q_dict = q.to_dict(only=('id', 'avatar', 'name', 'field_of_study'))
        #res = make_response(q_dict, 200)
        #return res
        return make_response(q.to_dict(only=('id', 'avatar', 'name', 'field_of_study')), 200)
    def delete(self,id):
        q = Scientist.query.filter_by(id=id).first()
        if not q:
            abort(404, "Scientist not found")
        db.session.delete(q)
        db.session.commit()
        return make_response({}, 204)

api.add_resource(OneScientist, '/scientists/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
