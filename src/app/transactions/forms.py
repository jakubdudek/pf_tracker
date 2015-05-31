from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField, DateField, DecimalField
from wtforms.validators import Required, Length

class UploadForm(Form):
    transactions = FileField(validators=[FileRequired('Please chose a file!'), FileAllowed(['csv', 'CSV'], 'CSV only!')])
    submit = SubmitField('Upload')

#class NewTransaction(Form):


class NewTransaction(Form):
    choices=[("BUY","BUY"), ("SELL", "SELL"), ("SPLIT", "SPLIT"), ("DIVIDEND", "DIVIDEND")]
    date = StringField('Date', validators=[Required()])
    trade = SelectField(u'Trade', choices=choices)
    symbol = StringField('Symbol', validators=[Required()])
    shares = StringField('Shares', validators=[Required()])
    price = StringField('Price', validators=[Required()])
    comission = StringField('Comission', validators=[Required()])
    fee = StringField('Fee', validators=[Required()])
