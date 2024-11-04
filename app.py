import os
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configuration for SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lookless.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

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

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/lost', methods=['GET', 'POST'])
def lost():
    if request.method == 'POST':
        # Determine which step we're on
        step = session.get('step', 1)

        if step == 1:
            # Store item description data in the session
            session['lost_item_data'] = request.form.to_dict()
            session['step'] = 2  # Move to the next step
            return redirect(url_for('lost'))
        elif step == 2:
            # Retrieve item description data from the session
            lost_item_data = session.get('lost_item_data', {})
            contact_data = request.form.to_dict()

            # Combine data from both steps
            lost_item_data.update(contact_data)

            # Parse the lost date
            lost_date_str = lost_item_data.get("lost-date")
            lost_date = datetime.strptime(lost_date_str, '%Y-%m-%d') if lost_date_str else None

            # Create a new LostItem object
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

            # Save to database
            db.session.add(lost_item)
            db.session.commit()

            # Clear the session data
            session.pop('lost_item_data', None)
            session.pop('step', None)

            return render_template('thank_you.html')
    else:
        # GET request
        step = session.get('step', 1)
        if step == 1:
            session['step'] = 1
            return render_template('lost_step1.html')
        elif step == 2:
            return render_template('lost_step2.html')

    # Default to step 1
    session['step'] = 1
    return render_template('lost_step1.html')


@app.route('/found', methods=['GET', 'POST'])
def found():
    if request.method == 'POST':
        # Determine which step we're on
        step = session.get('step', 1)

        if step == 1:
            # Store item description data in the session
            session['found_item_data'] = request.form.to_dict()
            session['step'] = 2  # Move to the next step
            return redirect(url_for('found'))
        elif step == 2:
            # Retrieve item description data from the session
            found_item_data = session.get('found_item_data', {})
            contact_data = request.form.to_dict()

            # Combine data from both steps
            found_item_data.update(contact_data)

            # Parse the found date
            found_date_str = found_item_data.get("found-date")
            found_date = datetime.strptime(found_date_str, '%Y-%m-%d') if found_date_str else None

            # Create a new FoundItem object
            found_item = FoundItem(
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

            # Save to database
            db.session.add(found_item)
            db.session.commit()

            # Clear the session data
            session.pop('found_item_data', None)
            session.pop('step', None)

            return render_template('thank_you.html')
    else:
        # GET request
        step = session.get('step', 1)
        if step == 1:
            session['step'] = 1
            return render_template('found_step1.html')
        elif step == 2:
            return render_template('found_step2.html')

    # Default to step 1
    session['step'] = 1
    return render_template('found_step1.html')



@app.route('/lost_items')
def lost_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    items = LostItem.query.order_by(LostItem.lost_date.desc()).all()
    return render_template('lost_items.html', items=items)

@app.route('/found_items')
def found_items():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    items = FoundItem.query.order_by(FoundItem.found_date.desc()).all()
    return render_template('found_items.html', items=items)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'LookLess24$':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Incorrect password. Please try again.')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

@app.route('/delete_lost_item/<int:item_id>', methods=['POST', 'GET'])
def delete_lost_item(item_id):
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to delete items.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        return redirect(url_for('confirm_delete_lost_item', item_id=item_id))

    # Should not reach here
    return redirect(url_for('lost_items'))


@app.route('/delete_found_item/<int:item_id>', methods=['POST', 'GET'])
def delete_found_item(item_id):
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to delete items.')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        return redirect(url_for('confirm_delete_found_item', item_id=item_id))

    # Should not reach here
    return redirect(url_for('found_items'))


@app.route('/confirm_delete_lost_item/<int:item_id>', methods=['GET', 'POST'])
def confirm_delete_lost_item(item_id):
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
            return redirect(url_for('lost_items'))

    return render_template('delete_confirmation.html', item_type='lost', item_id=item_id)


@app.route('/confirm_delete_found_item/<int:item_id>', methods=['GET', 'POST'])
def confirm_delete_found_item(item_id):
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
            return redirect(url_for('found_items'))

    return render_template('delete_confirmation.html', item_type='found', item_id=item_id)

@app.route('/export_lost_items')
def export_lost_items():
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to export data.')
        return redirect(url_for('admin_login'))

    # Query all lost items from the database
    lost_items = LostItem.query.all()

    # Convert the data to a list of dictionaries
    data = []
    for item in lost_items:
        data.append({
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
            'Submission Date': item.date_submitted.strftime('%Y-%m-%d %H:%M:%S') if item.date_submitted else ''
        })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Create an Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lost Items')

    output.seek(0)

    # Return the Excel file as a response
    return send_file(
        output,
        attachment_filename='lost_items.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@app.route('/export_found_items')
def export_found_items():
    if not session.get('admin_logged_in'):
        flash('You must be logged in as an administrator to export data.')
        return redirect(url_for('admin_login'))

    # Query all found items from the database
    found_items = FoundItem.query.all()

    # Convert the data to a list of dictionaries
    data = []
    for item in found_items:
        data.append({
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
            'Submission Date': item.date_submitted.strftime('%Y-%m-%d %H:%M:%S') if item.date_submitted else ''

        })

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Create an Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Found Items')

    output.seek(0)

    # Return the Excel file as a response
    return send_file(
        output,
        attachment_filename='found_items.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    app.run(debug=True)
