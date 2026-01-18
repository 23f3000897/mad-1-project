from flask import Flask,render_template,request,flash,redirect,session,url_for
from model import db,User,Parking_lot,Parking_spot,Reserved_spot
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from sqlalchemy import or_
from datetime import datetime,timedelta
from flask_sqlalchemy import SQLAlchemy
import os
from app import db









app = Flask(__name__)






app.config['SECRET_KEY']='JYOY123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/mad-1 project/setup.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db.init_app(app)
print("Using DB at: C:/mad-1 project/setup.db")







@app.route('/')
def home():
    return render_template('home.html')



@app.route('/user_sign',methods=['POST','GET'])
def user_sign():
    if request.method=='POST':
        username=request.form['username']
        fullname=request.form['fullname']
        email=request.form['email']
        password=request.form['password']
        role=request.form['role']
        
        confirm_password=request.form['confirm_password']
        
        if not username or not password or not confirm_password:
            flash('please fill out all the fields')
            return redirect(url_for('user_sign'))
        if password != confirm_password:
            flash('password does not match')
            return redirect(url_for('user_sign'))
        user = User.query.filter_by(username=username).first()
        
        if user:
            flash('user already exists')
            return redirect(url_for('user_sign'))
        
        password_hash = generate_password_hash(password)
        
        new_user = User(username=username,fullname=fullname,email=email,password=password_hash,role=role)
        db.session.add(new_user) 
        db.session.commit()
        
        print("✅ User committed successfully:", username)

        return redirect(url_for('user_login'))
    return render_template('user_sign.html')
        

    
@app.route('/user_login',methods=['GET','POST'])
def user_login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid email or password')
            return redirect(url_for('user_login'))

        session['user_id'] = user.id
        session['username'] = user.username
        session['fullname'] = user.fullname
        session['email'] = user.email
        session['password'] = user.password
        session['role'] = user.role.lower().strip()
        
        flash('Login successful')
        if user.role.lower().strip() == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
                return redirect(url_for('user_dashboard'))

    return render_template('user_login.html') 

@app.route('/admin_dashboard')
def admin_dashboard():
    # while testing with login, uncomment below lines
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('user_login'))

    user = db.session.get(User, session['user_id'])
    print("Logged in user:", user.username, "Role:", user.role)  #
    if user.role.lower().strip() == 'admin':
        users = User.query.filter_by(role='user').all()
        print(users)
        parking_lots = Parking_lot.query.all()
        print(parking_lots)
        reserved_spots = Parking_spot.query.filter_by(status_text_check='Reserved').count()
        available_spots = Parking_spot.query.filter_by(status_text_check='Available').count()

        return render_template('admin_dashboard.html', users=users,
            parking_lots=parking_lots,
            total_users=len(users),
            total_lots=len(parking_lots),
            reserved_spots=reserved_spots,
            available_spots=available_spots)
              
    else:
        flash("You don't have permission to view this page.", "danger")
        return redirect(url_for('home'))  # or user dashboard







@app.route('/edit/<int:parking_lot_id>', methods=['GET', 'POST'])
def edit_parking_lot(parking_lot_id):
    post = Parking_lot.query.get_or_404(parking_lot_id)
    
    # Check if user is logged in and is either admin or the author
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user or (user.role != 'admin' and post.author_id != user_id):
        flash("You don't have permission to edit this post.", "danger")
        return redirect(url_for('home'))  # or any safe fallback route

    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')

        db.session.commit()
        flash("Post updated successfully", "success")
        return redirect(url_for('edit', parking_lot_id=post.id))  # or redirect to another page

    return render_template('edit.html', post=post)

@app.route('/delete/<int:post_id>',methods=['POST'])
def delete_parking_lot(post_id):
    post=post.query.get_or_404(post_id)
    
    user_id=session.get('user_id')
    user=User.query.get(user_id)
    
    if not user or (user.role!='admin' and post.author_id!=user_id):
        flash("You don't have permission to delete this post.","danger")
        return redirect(url_for('home'))
    if Parking_spot.status_text_check=='O':
        flash("cannot delete this parking spot.it is currently occupied","warning")
        return redirect(url_for('admin_dashboard'))
    db.session.delete(post)
    db.session.commit()
    flash("Spot deleted successfully.","success")
    
    return redirect(url_for('admin_dashboard' if user.role=='admin' else 'user_dashboard'))

@app.route('/create', methods=['GET', 'POST'])
def create_parking_lot():
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    if not user or user.role != 'admin':
        flash("You don't have permission to create parking lots.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        print("POST received")
        prime_location_name = request.form['prime_location_name']
        Address = request.form['Address']
        pincode = request.form['pincode']
        price = request.form['price']
        maximum_number_of_spots = request.form['maximum_number_of_spots']
        print("Form data:", prime_location_name, Address, pincode, price, maximum_number_of_spots)


        if not prime_location_name  or not Address or not pincode or not price or not maximum_number_of_spots:
            flash("Please fill out all fields.", "warning")
            return redirect(url_for('create'))

        new_lot = Parking_lot(
            prime_location_name=prime_location_name,
            Address=Address,
            pincode=pincode,
            price=float(price),
            maximum_number_of_spots=int(maximum_number_of_spots),
        )

        db.session.add(new_lot)
        db.session.commit()
        print("Parking lot added to DB")
        flash("Parking lot created successfully.", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('create.html')

@app.route('/view_parking_lot/<int:lot_id>')
def view_parking_lot(lot_id):
    lot = Parking_lot.query.get_or_404(lot_id)
    spots = Parking_spot.query.filter_by(lot_id=lot_id).all()
    spots= Parking_spot.query.all()
    return render_template('view.html', spots=spots,lot=lot)






def initialize_admin():
    with app.app_context():
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin',  
                        fullname='admin',
                        email='admin@gmail.com',  
                        password=generate_password_hash('admin'),
                        role='admin'
                        )
                        
            db.session.add(admin)
            db.session.commit()
@app.route('/show_users')
def show_users():
    users = User.query.all()
    return "<br>".join([f"{u.username} - {u.email}" for u in users])

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('user_login'))

@app.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("please log in.","warning")
        return redirect(url_for('user_login'))
    user=db.session.get(User,user_id)
    if user.role.lower().strip() =='admin':
        return redirect(url_for('admin_dashboard'))
    
    
    current_reservation=Reserved_spot.query.filter_by(user_id=user_id,status_text_check='Reserved').first()
    spot_details = None
    lot_details = None
    if current_reservation:
        spot_details = Parking_spot.query.get(current_reservation.spot_id)
        if spot_details:
            lot_details = Parking_lot.query.get(spot_details.lot_id )
            
    
    
    history=Reserved_spot.query.filter(Reserved_spot.user_id==user_id,Reserved_spot.status_text_check!='Reserved').all()
    print(history)
    print("User ID:", user_id)
    print("Current Reservation:", current_reservation)
    print("History:", history)
   
    return render_template('user_dashboard.html',
                            current_reservation=current_reservation,
                            history=history)
    
    

    
@app.route('/reserve_spot',methods=['POST'])
def reserve_spot():
    user_id=session.get('user_id')
    if not user_id:
        flash("Please log in first","warning")
        return redirect(url_for('user_login'))
    spot = Parking_spot.query.filter_by(status_text_check='Available').first()
    if not spot:
        flash("No available spots","warning")
        return redirect(url_for('user_dashboard'))
    
    
        
    spot.status_text_check='Reserved'
    lot = Parking_lot.query.get(spot.lot_id)
    Parking_cost=lot.price if lot else 0
    db.session.add(spot)
    reserved_spot=Reserved_spot(user_id=user_id,spot_id=spot.id,status_text_check='Reserved',Parking_timestamp=datetime.now(),parking_cost=0)
    db.session.add(reserved_spot)
    
    
    try:
        db.session.commit()
        flash("spot reserved successfully","success")
    except Exception as e:
        db.session.rollback()
        print("error during reservation:",e )
        flash("spot reservation failed","danger")
        
    
    
    return redirect(url_for('user_dashboard'))

@app.route('/release_spot',methods=['POST'])
def release_spot():
    user_id=session.get('user_id')
    if not user_id:
        flash("Please log in first","warning")
        return redirect(url_for('user_login'))
    reserved_spot=Reserved_spot.query.filter_by(user_id=user_id,status_text_check='Reserved').first()
    if not reserved_spot:
        flash("No reserved spot found","warning")
        return redirect(url_for('user_dashboard'))
    reserved_spot.leaving_timestamp=datetime.now()
    duration=reserved_spot.leaving_timestamp-reserved_spot.Parking_timestamp 
    total_minutes=duration.total_seconds()/60
    rate_per_minute = 2  # or your fixed rate
    cost = round(total_minutes * rate_per_minute)

    reserved_spot.parking_cost=cost
    reserved_spot.total_time=total_minutes
    reserved_spot.status_text_check = 'Completed' 
    
    spot = Parking_spot.query.get(reserved_spot.spot_id)
    spot.status_text_check = 'Available'

    db.session.commit()
    flash(f"Spot released. Total time: {reserved_spot.total_time} min. Cost: ₹{cost}")
    return redirect(url_for('user_dashboard'))

# Make sure this is inside app.app_con

 # replace with your actual app filename
    for _ in range(10):
        spot = Parking_spot(lot_id=lot.id, status_text_check='Available')
        db.session.add(spot)
    db.session.commit()








            

with app.app_context():
    db.create_all()
    

if __name__ == '__main__':
    with app.app_context():
        initialize_admin()
        app.run(debug=True)
        




