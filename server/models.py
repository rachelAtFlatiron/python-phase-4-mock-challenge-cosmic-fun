from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):

    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    #associated missions, Planet -> Mission
    missions_of_cur_planet = db.relationship('Mission', back_populates="planet", cascade="all, delete-orphan")
    #associated scientists, Planet -> Mission -> Scientist
    scientists_of_cur_planet = association_proxy('missions_of_cur_planet', 'scientist')
    
    serialize_rules = ('-missions_of_cur_planet.planet', )
    # validates - flask level, will not allow bad data on flask level (flask shell)
    # validates - will allow bad data at table level (sqlite3)

    #constraints - at table and flask level - directly defined in table

class Scientist(db.Model, SerializerMixin):

    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    avatar = db.Column(db.String)
    #nullable, unique are constraints
    field_of_study = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)

    #associated missions, Scientist -> Mission
    missions_of_cur_scientist = db.relationship('Mission', back_populates='scientist', cascade="all, delete-orphan")
    #associated planets, Scientist -> Mission -> Planet
    planets_of_cur_scientist = association_proxy("missions_of_cur_scientist", "planet")
    
    serialize_rules = ("-missions_of_cur_scientist.scientist", "-missions_of_cur_scientist.planet", '-planets_of_cur_scientist.scientists_of_cur_planet')
    #validations
    @validates('name')
    def validates_name(self, key, input_name):
        if not input_name: 
            raise ValueError('scientist needs a name')
        #get all names
        names = db.session.query(Scientist.name).all()
        #check if input_name exists in our list of names
        if input_name in names:
            raise ValueError('scientist needs unique name')
        return input_name 
        

class Mission(db.Model, SerializerMixin):

    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    name = db.Column(db.String, nullable=False)

    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    #associated scienist, Mission -> Scientist
    scientist = db.relationship('Scientist', back_populates="missions_of_cur_scientist")
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    #associated planet, Mission -> Planet
    planet = db.relationship('Planet', back_populates='missions_of_cur_planet')

    serialize_rule = ('-scientist.missions_of_cur_scientist', '-planet.missions_of_cur_planet')

    def __repr__(self):
        return f"<Mission id={self.id} name={self.name} />"
    #if your seed file doesn't run, you might want to set up your relationships first