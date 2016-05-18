import os, csv
import pandas as pd

from flask import render_template, request, redirect, url_for, flash, json, Response, abort
from sqlalchemy.ext.automap import automap_base
from flask.ext.login import login_required, current_user
from werkzeug import secure_filename
from werkzeug.datastructures import MultiDict
from app import db

from . import transactions
from .forms import UploadForm, NewTransactionForm
from ..models import User
from ..pf_utils import pf_utils as pf



@transactions.route('/exit', methods=['GET', 'POST'])
@login_required
def exit():
    print("leaving page")
    
    tr_by_date_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='ID')
    symbols=pf.get_symbols(tr_by_date_df)
    
    [worth, cumrates, invalid]=  pf.get_rates_df(pf.get_holdings(tr_by_date_df, symbols), symbols, tr_by_date_df)
    cumrates.to_sql('cumrates'+str(current_user.get_id()), db.engine, if_exists='replace')
    worth.to_sql('worth'+str(current_user.get_id()), db.engine, if_exists='replace')

    return Response("ok")

@transactions.route('/create', methods=['POST'])
@login_required
def create():
    
    if request.method == 'POST':
        trForm=NewTransactionForm(request.form)
        print(str(request.form))
        if trForm.validate():
            print("validation passed")

            # extract data fields from request
            date=pd.to_datetime(str(trForm.date.data))
            symbol=trForm.symbol.data
            trade=trForm.trade.data
            shares=float(trForm.shares.data)
            price=float(trForm.price.data)
            commission=float(trForm.commission.data)
            fee=float(trForm.fee.data)

            # open database, create one if this is the first transaction
            try:
                tr_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='date')
            except:
                id = 0
            else:
                if request.form['action'] == 'create':
                    # transaction id is largest id + 1
                    id = tr_df['id'].max()+1
                else:
                    id = request.form['id']
                    tr_df = tr_df[tr_df.id != int(id)]

            #new row to add
            add = [date, id, trade, symbol, shares, price, commission, fee]
            row = pd.DataFrame.from_dict({0:dict(zip(tr_df.reset_index().columns,add))}, orient='index')            
            row.set_index('date', inplace='true')

            # append row to database
            row.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='append')
            return redirect(url_for('.get_table'))

        else:
            print("validaton failed")
            print(trForm.errors)
            errors={'fieldErrors':[{'name' : key , 'status' : trForm.errors[key]} for key in trForm.data.keys() if key in trForm.errors]}
            return json.dumps(errors);   
    else:
        # need to return server error 405 (method no allowed)
        abort(405)

# @transactions.route('/edit', methods=['GET', 'POST'])
# @login_required
# def edit():
#     print("Editing transaction...")
#     print(str(request.form))
    
#     ID = request.form['id']
#     #print(ID)

#     # remove empty (non modified) elements of form
#     tmp = MultiDict([(i,j) for i,j in request.form.items() if j != ''])
#     # remove  csrf token
#     #tmp.pop("csrf_token", None)
#     #tmp.pop("ID", None)
#     keys = tmp.keys();
#     trForm=NewTransactionForm(tmp)
    
#     if trForm.validate():
#         tr_df = pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='date')
#         tr_df.reset_index(inplace='true')

#         # get index of row of interest (matching ID)
#         index = (tr_df[tr_df['id'] == int(ID)].index.tolist()[0])

#         for key in keys:
#             if key != 'csrf_token':
#                 tr_df.set_value(index, key, trForm.data[key])    
        
#         tr_df.set_index('date', inplace='true')

#         # write database
#         tr_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')

#         return redirect(url_for('.get_table'))
#     else:
#         print("validaton failed")
#         print(trForm.errors)
#         errors={'fieldErrors':[{'name' : key , 'status' : trForm.errors[key]} for key in trForm.data.keys() if key in trForm.errors]}
#         return json.dumps(errors);   


@transactions.route('/delete', methods='POST')
@login_required
def delete():
    print("Deleting transaction...")
    if request.method == "POST":

        # todo: figure out how to delete row directly in database, rather than read and write back
        id = request.form['id']

        # open database table
        tr_df = pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='date')
   
        # remove entry matching ID
        for i in range(0, len(id)):
            tr_df = tr_df[tr_df.id != int(id[i])]

        # rewrite the table to database
        tr_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')

        # rewrite table
        return redirect(url_for('.get_table'))
    else:
        # need to return server error 405 (method no allowed)
        abort(405)


@transactions.route('/get_table', methods=['GET', 'POST'])
@login_required
def get_table():
    tr_list=[]

    # look for transactions tables in database, if not present empty table
    try:
        tr_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='id')
        tr_list = pf.df_to_obj_list(tr_df, 'date') 
        #remove time stamps from dates
        for i in range(0, len(tr_list)):
            tr_list[i]['date'] = tr_list[i]['date'].split(' ')[0]  
    except:
        tr_list = []
        flash("No data found, please upload a file or add a transaction")

    # turn into json format for ajax

    tr_json = {"data" : tr_list}
    print(tr_json)
    return json.dumps(tr_json)


@transactions.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = UploadForm()
    trForm = NewTransactionForm()

    if form.validate_on_submit():
        ##todo, secure_filename
        tr_df = pf.get_trans(form.transactions.data)

        # write transactions to sql
        print("writing to database")
        tr_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')
    else:
        print("not valid")
        print(form.errors)
    
    return render_template('transactions/transactions.html', form=form, form2=trForm)





