import os, csv
from flask import render_template, current_app, request, redirect, url_for, flash, json, jsonify, session, Response
from . import transactions
from .forms import UploadForm
from werkzeug import secure_filename
from flask_wtf.file import FileField

from flask.ext.login import login_required, current_user
from ..models import User

from ..lib import pf_utils as utils
from ..lib import new_utils as pf

from app import db

import pandas as pd

from app import cache


@transactions.route('/del_trans', methods=['GET', 'POST'])
@login_required
def del_trans():
    print("in del_trans")
    if request.method == "POST":
        print(str(request.form))

    return Response("ok")

@transactions.route('/newval', methods=['GET', 'POST'])
@login_required
def newval():
    if request.method == "POST":
        print(str(request.form))
        return Response(value)
    return

@transactions.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    form = UploadForm()

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
            return render_template('transactions/transactions.html', form=form, transactions=transactions_list)

    transactions_list = pf.df_to_obj_list(transaction_df, 'Date')

    #insert row id
    for i in range(0, len(transactions_list)):
        transactions_list[i]["DT_RowId"]=str(i)

    #remove time from timestamp
    for i in range(0, len(transactions_list)):
        transactions_list[i]['Date']=transactions_list[i]['Date'].split(' ')[0]

    return render_template('transactions/transactions.html', form=form, transactions=transactions_list)



