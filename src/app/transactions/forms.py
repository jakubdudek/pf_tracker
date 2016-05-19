from flask_wtf import Form
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField, DateField, DecimalField
from wtforms.validators import Required, Length, ValidationError

class UploadForm(Form):
    transactions = FileField(validators=[FileRequired('Please chose a file!'), FileAllowed(['csv', 'CSV'], 'CSV only!')])
    submit = SubmitField('Upload')

def date_check(form, field):
    import datetime
    
    try:
        datetime.datetime.strptime(field.data, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Incorrect data format, should be YYYY-MM-DD")

def ticker_check(form, field):
    from datetime import date, timedelta
    import pandas.io.data as web

    trade = form._fields.get("trade")

    if(field.data != "MYCASH" and trade.data != "DIVIDEND"):
        try:
            quote=web.DataReader(field.data, 'yahoo', date.today()-timedelta(days=1))
        except:
            raise ValidationError("Invalid stock ticker")

def float_check(form, field):
    try:
        float(field.data)
    except:
        raise ValidationError("Invalid input, please enter a real number")

class NewTransactionForm(Form):
    id = StringField('ID')
    date = StringField('Date', validators=[Required(), date_check])
    trade = StringField('Symbol', validators=[Required()])
    symbol = StringField('Symbol', validators=[Required(), ticker_check])
    shares = StringField('Shares', validators=[Required(), float_check])
    price = StringField('Price', validators=[Required(), float_check])
    commission = StringField('Commission', validators=[Required(), float_check])
    fee = StringField('Fee', validators=[Required(), float_check])
