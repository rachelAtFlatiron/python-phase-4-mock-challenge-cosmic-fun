from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Scientist(db.Model, SerializerMixin):
    __tablename__ = "scientists" 

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    name = db.Column(db.String, nullable=False, unique=True)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)

    missions = db.relationship('Mission', back_populates='scientist')
    planets = association_proxy('missions', 'planet')

    serialize_rules = ('-created_at', '-updated_at', '-missions.scientist', '-planets.scientists')

    def __repr__(self):
        return f'<Scientist {self.id} {self.name} />'

class Planet(db.Model, SerializerMixin):
    __tablename__ = "planets" 

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    name = db.Column(db.String) 
    distance_from_earth = db.Column(db.String) 
    nearest_star = db.Column(db.String) 
    image = db.Column(db.String) 

    missions = db.relationship('Mission', back_populates='planet')
    scientists = association_proxy('missions', 'scientist')
    
    serialize_rules = ('-created_at', '-updated_at', '-missions.planet', '-scientists.planets')

    def __repr__(self): 
        f"<Planet {self.id} {self.name} />"

class Mission(db.Model, SerializerMixin):
    __tablename__ = "missions"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)

    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    serialize_rules = ('-created_at', '-updated_at', '-scientist.missions', '-planet.missions')
    
    def __repr__(self):
        return f"<Mission {self.id} {self.name} />"