import os
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import random
import string

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configuration for SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lookless.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def generate_item_number():
    """Generate a random item number."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# Define the LostItem model
class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    lost_date = db.Column(db.Date)
    campus = db.Column(db.String(100))
    floor = db.Column(db.String(100))
    room = db.Column(db.String(100))
    description = db.Column(db.Text)
    item_type = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    distinctive_features = db.Column(db.Text)
    additional_info = db.Column(db.Text)

# Define the FoundItem model
class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_number = db.Column(db.String(8), unique=True, nullable=False)  # Add this line
    first_name = db.Column(db.String(100))
    second_name = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    found_date = db.Column(db.Date)
    campus = db.Column(db.String(100))
    floor = db.Column(db.String(100))
    room = db.Column(db.String(100))
    description = db.Column(db.Text)
    item_type = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    distinctive_features = db.Column(db.Text)
    additional_info = db.Column(db.Text)

# Define the Match model
class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'), nullable=False)
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'), nullable=False)
    match_percentage = db.Column(db.Float, nullable=False)
    is_hidden = db.Column(db.Boolean, default=False)  # New column to indicate hidden status

    lost_item = db.relationship('LostItem', backref=db.backref('matches', cascade="all, delete-orphan"))
    found_item = db.relationship('FoundItem', backref=db.backref('matches', cascade="all, delete-orphan"))



@app.route('/toggle_match_visibility/<int:match_id>', methods=['POST'])
def toggle_match_visibility(match_id):
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to perform this action.')
        return redirect(url_for('admin_login'))

    match = Match.query.get_or_404(match_id)
    match.is_hidden = not match.is_hidden  # Toggle the hidden status
    db.session.commit()
    return redirect(url_for('admin_matches'))


@app.route('/')
def home():
    return render_template('home.html')

# Lost Item Form with two steps
@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        # Handle back action
        if 'back' in request.form:
            session['step'] = 1
            return redirect(url_for('lost'))

        # Handle regular step advancement
        step = session.get('step', 1)

        if step == 1:
            session['lost_item_data'] = request.form.to_dict()
            session['step'] = 2
            return redirect(url_for('lost'))
        elif step == 2:
            lost_item_data = session.get('lost_item_data', {})
            contact_data = request.form.to_dict()
            lost_item_data.update(contact_data)

            lost_date_str = lost_item_data.get("lost-date")
            lost_date = datetime.strptime(lost_date_str, '%Y-%m-%d') if lost_date_str else None

            lost_item = LostItem(
                first_name=lost_item_data.get("first-name"),
                second_name=lost_item_data.get("second-name"),
                email=lost_item_data.get("email"),
                phone_number=lost_item_data.get("phone-number"),
                lost_date=lost_date,
                campus=lost_item_data.get("campus"),
                floor=lost_item_data.get("floor"),
                room=lost_item_data.get("room"),
                description=lost_item_data.get("description"),
                item_type=lost_item_data.get("item-type"),
                brand=lost_item_data.get("brand"),
                color=lost_item_data.get("color"),
                distinctive_features=lost_item_data.get("distinctive-features"),
                additional_info=lost_item_data.get("additional-info")
            )

            db.session.add(lost_item)
            db.session.commit()

            session.pop('lost_item_data', None)
            session.pop('step', None)

            return render_template('thank_you.html')
    else:
        step = session.get('step', 1)
        if step == 1:
            session['step'] = 1
            return render_template('lost_step1.html')
        elif step == 2:
            return render_template('lost_step2.html')

    session['step'] = 1
    return render_template('lost_step1.html')



# Found Item Form with two steps
@app.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        # Handle back action
        if 'back' in request.form:
            session['step'] = 1
            return redirect(url_for('found'))

        # Handle regular step advancement
        step = session.get('step', 1)

        if step == 1:
            session['found_item_data'] = request.form.to_dict()
            session['step'] = 2
            # Generate the item number here and store it in the session
            session['item_number'] = generate_item_number()
            return redirect(url_for('found'))
        elif step == 2:
            found_item_data = session.get('found_item_data', {})
            contact_data = request.form.to_dict()
            found_item_data.update(contact_data)

            found_date_str = found_item_data.get("found-date")
            found_date = datetime.strptime(found_date_str, '%Y-%m-%d') if found_date_str else None

            found_item = FoundItem(
                item_number=session.get('item_number'),  # Save the item number
                first_name=found_item_data.get("first-name"),
                second_name=found_item_data.get("second-name"),
                email=found_item_data.get("email"),
                phone_number=found_item_data.get("phone-number"),
                found_date=found_date,
                campus=found_item_data.get("campus"),
                floor=found_item_data.get("floor"),
                room=found_item_data.get("room"),
                description=found_item_data.get("description"),
                item_type=found_item_data.get("item-type"),
                brand=found_item_data.get("brand"),
                color=found_item_data.get("color"),
                distinctive_features=found_item_data.get("distinctive-features"),
                additional_info=found_item_data.get("additional-info")
            )

            db.session.add(found_item)
            db.session.commit()

            # Clear session data
            session.pop('found_item_data', None)
            session.pop('step', None)
            session.pop('item_number', None)  # Clear item number from session

            return render_template('thank_you.html')
    else:
        step = session.get('step', 1)
        if step == 1:
            session['step'] = 1
            return render_template('found_step1.html')
        elif step == 2:
            item_number = session.get('item_number', generate_item_number())  # Use session item number if exists
            return render_template('found_step2.html', item_number=item_number)

    session['step'] = 1
    return render_template('found_step1.html')




# Admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'LookLess24$':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password. Please try again.')
    return render_template('admin_login.html')

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

# Admin logout route
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

# View and delete lost items
@app.route('/lost_items')
def lost_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    items = LostItem.query.order_by(LostItem.lost_date.desc()).all()
    return render_template('lost_items.html', items=items)

@app.route('/delete_lost_item/<int:item_id>', methods=['GET', 'POST'])
def delete_lost_item(item_id):
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to delete items.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'LookLess24$':
            item = LostItem.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('lost_items'))
        else:
            flash('Incorrect password. Item not deleted.')
            return redirect(url_for('delete_lost_item', item_id=item_id))

    return render_template('delete_confirmation.html', item_type='lost', item_id=item_id)

# View and delete found items
@app.route('/found_items')
def found_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    items = FoundItem.query.order_by(FoundItem.found_date.desc()).all()
    return render_template('found_items.html', items=items)

@app.route('/delete_found_item/<int:item_id>', methods=['GET', 'POST'])
def delete_found_item(item_id):
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to delete items.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'LookLess24$':
            item = FoundItem.query.get_or_404(item_id)
            db.session.delete(item)
            db.session.commit()
            return redirect(url_for('found_items'))
        else:
            flash('Incorrect password. Item not deleted.')
            return redirect(url_for('delete_found_item', item_id=item_id))

    return render_template('delete_confirmation.html', item_type='found', item_id=item_id)

# Calculate match percentage
def calculate_match_percentage(lost_item, found_item):
    score = 0
    total_weight = 100

    if lost_item.item_type == found_item.item_type:
        score += 30
    if lost_item.color == found_item.color:
        score += 20
    if lost_item.brand == found_item.brand:
        score += 15
    if lost_item.distinctive_features == found_item.distinctive_features:
        score += 15
    if lost_item.floor == found_item.floor and lost_item.room == found_item.room:
        score += 10
    if lost_item.campus == found_item.campus:
        score += 10

    return (score / total_weight) * 100

# Admin matches route
@app.route('/admin_matches')
def admin_matches():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # Fetch all Lost and Found items
    lost_items = LostItem.query.all()
    found_items = FoundItem.query.all()
    threshold = 50  # Define your match threshold

    # Clear existing matches if needed
    Match.query.delete()
    db.session.commit()

    # Iterate over lost and found items to create new matches
    for lost_item in lost_items:
        for found_item in found_items:
            match_percentage = calculate_match_percentage(lost_item, found_item)
            if match_percentage >= threshold:
                new_match = Match(
                    lost_item_id=lost_item.id,
                    found_item_id=found_item.id,
                    match_percentage=match_percentage
                )
                db.session.add(new_match)

    db.session.commit()

    # Fetch all matches to display on the admin page
    matches = Match.query.filter_by(is_hidden=False).all()
    return render_template('admin_matches.html', matches=matches)


@app.route('/hide_match/<int:match_id>', methods=['POST'])
def hide_match(match_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    match = Match.query.get_or_404(match_id)
    match.is_hidden = True
    db.session.commit()

    return redirect(url_for('admin_matches'))


# Export lost items to Excel
@app.route('/export_lost_items')
def export_lost_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    lost_items = LostItem.query.all()
    data = [
        {
            'First Name': item.first_name,
            'Second Name': item.second_name,
            'Email': item.email,
            'Phone Number': item.phone_number,
            'Lost Date': item.lost_date.strftime('%Y-%m-%d') if item.lost_date else '',
            'Campus': item.campus,
            'Floor': item.floor,
            'Room': item.room,
            'Description': item.description,
            'Item Type': item.item_type,
            'Brand': item.brand,
            'Color': item.color,
            'Distinctive Features': item.distinctive_features,
            'Additional Info': item.additional_info,
        } for item in lost_items
    ]

    output = io.BytesIO()
    df = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lost Items')

    output.seek(0)
    return send_file(output, attachment_filename='lost_items.xlsx', as_attachment=True)

# Export found items to Excel
@app.route('/export_found_items')
def export_found_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    found_items = FoundItem.query.all()
    data = [
        {
            'First Name': item.first_name,
            'Second Name': item.second_name,
            'Email': item.email,
            'Phone Number': item.phone_number,
            'Found Date': item.found_date.strftime('%Y-%m-%d') if item.found_date else '',
            'Campus': item.campus,
            'Floor': item.floor,
            'Room': item.room,
            'Description': item.description,
            'Item Type': item.item_type,
            'Brand': item.brand,
            'Color': item.color,
            'Distinctive Features': item.distinctive_features,
            'Additional Info': item.additional_info,
        } for item in found_items
    ]

    output = io.BytesIO()
    df = pd.DataFrame(data)
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Found Items')

    output.seek(0)
    return send_file(output, attachment_filename='found_items.xlsx', as_attachment=True)

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
