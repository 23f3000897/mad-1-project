from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False, default='user') 
    

class Parking_lot(db.Model):
    __tablename__ = "Parking_lots"
    
    id = db.Column(db.Integer,primary_key=True)
    prime_location_name = db.Column(db.String,nullable=False)
    price=db.Column(db.Integer,nullable=False)
    Address=db.Column(db.String,nullable=False)
    pincode=db.Column(db.String,nullable=False)
    maximum_number_of_spots=db.Column(db.Integer,nullable=False)
    spot = db.relationship("Parking_spot",backref="Parking_lots")

    
class Parking_spot(db.Model):
    __tablename__="Parking_spots"
    
    
    id=db.Column(db.Integer,primary_key=True)
    lot_id=db.Column(db.Integer,db.ForeignKey("Parking_lots.id"),nullable=False)
    status_text_check=db.Column(db.String,nullable=False,default='Available')
    reserved=db.relationship("Reserved_spot",backref="Parking_spots")
    # customer = db.relationship('User') 
    @property
    def status_text(self):
        return self.status_text_check
    
class Reserved_spot(db.Model):
    __tablename__= "Reserved_spots"
    
    id=db.Column(db.Integer,primary_key=True)
    spot_id =db.Column(db.Integer,db.ForeignKey("Parking_spots.id"),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.id"),nullable=False)
    Parking_timestamp=db.Column(db.DateTime,nullable=True)
    leaving_timestamp=db.Column(db.DateTime,nullable=True)
    total_time=db.Column(db.Integer,nullable=True)
    parking_cost=db.Column(db.Integer,nullable=False)
    status_text_check = db.Column(db.String, nullable=False, default='Reserved') 
    
    # customer = db.relationship('users')
    def __repr__(self):
     return f"<ReservedSpot id={self.id}, user_id={self.user_id}, spot_id={self.spot_id}, status={self.status_text_check}>"

    
    
    
    
    
    
    
    
    
