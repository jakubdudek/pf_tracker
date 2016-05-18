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
    trade = form._fields.get("trade")

    if(field.data != "MYCASH" and trade.data != "DIVIDEND"):
        try:
            quote=web.DataReader(field.data, 'yahoo', date.today())
        except:
            raise ValidationError("Invalid stock ticker")

    

class NewTransactionForm(Form):
    id = StringField('ID')
    date = StringField('Date', validators=[Required(), date_check])
    trade = StringField('Symbol', validators=[Required()])
    symbol = StringField('Symbol', validators=[Required()])
    shares = StringField('Shares', validators=[Required()])
    price = StringField('Price', validators=[Required()])
    commission = StringField('Commission', validators=[Required()])
    fee = StringField('Fee', validators=[Required()])