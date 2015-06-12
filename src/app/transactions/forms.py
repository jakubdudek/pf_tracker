from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField, DateField, DecimalField
from wtforms.validators import Required, Length, ValidationError

class UploadForm(Form):
    transactions = FileField(validators=[FileRequired('Please chose a file!'), FileAllowed(['csv', 'CSV'], 'CSV only!')])
    submit = SubmitField('Upload')

#class NewTransaction(Form):

def date_check(form, field):
    import datetime
    
    try:
        datetime.datetime.strptime(field.data, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Incorrect data format, should be YYYY-MM-DD")

def ticker_check(form, field):
    import pandas.io.data as web
    
    if(field.data != "MYCASH"):
        try:
            quote=web.DataReader(field.data, 'yahoo', datetime.today())
        except:
            raise ValidationError("Invalid stock ticker")

class NewTransaction(Form):
    choices=[("BUY","BUY"), ("SELL", "SELL"), ("SPLIT", "SPLIT"), ("DIVIDEND", "DIVIDEND") , ("DEPOSIT", "DEPOSIT")]
    date = StringField('Date', validators=[Required(), date_check])
    trade = SelectField(u'Trade', choices=choices)
    symbol = StringField('Symbol', validators=[Required(), ticker_check])
    shares = StringField('Shares', validators=[Required()])
    price = StringField('Price', validators=[Required()])
    comission = StringField('Comission', validators=[Required()])
    fee = StringField('Fee', validators=[Required()])
