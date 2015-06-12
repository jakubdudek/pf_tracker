import os, csv
from flask import render_template, current_app, request, redirect, url_for, flash, json, jsonify, session, Response
from . import transactions
from .forms import UploadForm, NewTransaction
from werkzeug import secure_filename
from flask_wtf.file import FileField

from flask.ext.login import login_required, current_user
from ..models import User

from ..pf_utils import pf_utils as utils
from ..pf_utils import pf_utils as pf

from app import db

import pandas as pd

from app import cache


@transactions.route('/exit', methods=['GET', 'POST'])
@login_required
def exit():
    print("leaving page")
    
    tr_by_date_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='index')
    symbols=pf.get_symbols(tr_by_date_df)
    
    [worth, cumrates, invalid]=  pf.get_rates_df(pf.get_holdings(tr_by_date_df, symbols), symbols, tr_by_date_df)
    cumrates.to_sql('cumrates'+str(current_user.get_id()), db.engine, if_exists='replace')
    worth.to_sql('worth'+str(current_user.get_id()), db.engine, if_exists='replace')

    return Response("ok")

@transactions.route('/del_trans', methods=['GET', 'POST'])
@login_required
def del_trans():
    print("in del_trans")
    if request.method == "POST":
        print(str(request.form['row_id']))
        transaction_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='index')
        transaction_df.reset_index(inplace='true')
        transaction_df = transaction_df[transaction_df.ID != (int(request.form['row_id']))]
        transaction_df.set_index('index', inplace='true')
        transaction_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')
        cache.clear()
    return Response("ok")

@transactions.route('/new_transaction', methods=['GET', 'POST'])
@login_required
def new_transaction():

    form =UploadForm()

    if request.method == "POST":
        form2 = NewTransaction(request.form)
        print((request.form['symbol']))
        if form2.validate_on_submit():
            transaction_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='index')
            
            date=pd.to_datetime(request.form['date'])
            symbol=(request.form['symbol'])
            trade=(request.form['trade'])
            shares=float(request.form['shares'])
            price=float(request.form['price'])
            comission=float(request.form['comission'])
            fee=float(request.form['fee'])
            
            #add to dataframe
            transaction_df.reset_index(inplace='true')
            s=transaction_df.index.size
            transaction_df.loc[s]=[date, s+1, trade, symbol, shares, price, comission, fee]
            transaction_df.set_index('index', inplace='true')
            transaction_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')
            
            cache.clear()
            
            return redirect(url_for('.transactions'))
        else:
            print("not valid")
            try:
                transaction_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='index')
                transactions_list = pf.df_to_obj_list(transaction_df, 'Date')

                #insert row id
                #for i in range(0, len(transactions_list)):
                #    transactions_list[i]["DT_RowId"]=str(i)
    
                #remove time from timestamp
                for i in range(0, len(transactions_list)):
                    transactions_list[i]['Date']=transactions_list[i]['Date'].split(' ')[0]
            except:
                transactions_list = []
            
            return render_template('transactions/transactions.html', form2=form2, form=form, transactions=transactions_list , show_modal=1)
        
        print("redirecting")
        return redirect(url_for('.transactions'))

    return

@transactions.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = UploadForm()
    form2 = NewTransaction()
    transactions_list=[]
    
    print("now in main view")
   
    if form.validate_on_submit():
        ##todo, secure_filename
        transaction_df = pf.get_trans(form.transactions.data)

        # write transactions to sql
        print("writing to database")
        transaction_df.to_sql('transaction_'+str(current_user.get_id()), db.engine, if_exists='replace')

    else:
        
        try:
            transaction_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='index')
        except:
            transaction_list =[]
            return render_template('transactions/transactions.html', form2=form2, form=form, transactions=transactions_list)

    transactions_list = pf.df_to_obj_list(transaction_df, 'Date')

    #insert row id
    for i in range(0, len(transactions_list)):
        transactions_list[i]["DT_RowId"]=str(i)

    #remove time from timestamp
    for i in range(0, len(transactions_list)):
        transactions_list[i]['Date']=transactions_list[i]['Date'].split(' ')[0]

#print(transactions_list)

    return render_template('transactions/transactions.html', form=form, form2=form2, transactions=transactions_list, show_modal=0)




