from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Optional

class LostItemForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    # Add other fields with appropriate validators
    # ...
    submit = SubmitField('Submit')
