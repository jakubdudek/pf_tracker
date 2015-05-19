from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField


class UploadForm(Form):
    transactions = FileField('Upload a CSV file of your transactions', validators=[FileRequired('Please chose a file!'), FileAllowed(['csv', 'CSV'], 'CSV only!')])
    submit = SubmitField('Upload')