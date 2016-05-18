import os, csv, time
from flask import render_template, current_app, request, redirect, url_for, flash, json, jsonify, make_response, Response
from . import performance
from .forms import UploadForm
from werkzeug import secure_filename
from flask_wtf.file import FileField

import pandas as pd

from flask.ext.login import login_required, current_user, session
from ..models import User
from ..pf_utils import pf_utils as utils
from ..pf_utils import pf_utils as pf
from pandas.tseries import offsets
from pandas import datetime
from pandas import Series
from pandas.tseries.offsets import Week, BDay
from datetime import date

from app import cache
from app import db

@performance.route('/get_performance', methods=['GET', 'POST'])
@login_required
def get_performance():
    if request.method == "POST":
        print(str(request.form))
        keys = list(request.form.keys())
        print(keys)
        keys.remove('src')
        print(keys)
        
        idx = [];
        for key in keys:
            idx.append(request.form[key])
        
        print(idx)
        
     
        tr_by_date_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='date')
        symbols=pf.get_symbols(tr_by_date_df)

# try getting rates from sql and check that they are up to date
        try:
            cumrates=pd.read_sql_table('cumrates'+str(current_user.get_id()), db.engine, index_col='date')
            cumrates = Series(cumrates['0'], index=cumrates.index)
            
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            last_b_day = pd.date_range(start=today-Week(), end=today, freq=BDay())[-1]-BDay(1)
            last_day = cumrates.index[-1].to_datetime()
            
            print(today)
            print(last_day)
            print(last_b_day)

            if (last_day != last_b_day):
                [worth, cumrates, invalid]=  pf.get_rates_df(pf.get_holdings(tr_by_date_df, symbols), symbols, tr_by_date_df)
                cumrates.to_sql('cumrates'+str(current_user.get_id()), db.engine, if_exists='replace')
                worth.to_sql('worth'+str(current_user.get_id()), db.engine, if_exists='replace')
    
        except:
            [worth, cumrates, invalid]=  pf.get_rates_df(pf.get_holdings(tr_by_date_df, symbols), symbols, tr_by_date_df)
            cumrates.to_sql('cumrates'+str(current_user.get_id()), db.engine, if_exists='replace')
            worth.to_sql('worth'+str(current_user.get_id()), db.engine, if_exists='replace')
        


        [idx_rates, invalid] = pf.get_index_rates(pf.get_cashflow(tr_by_date_df), idx)
        if len(invalid)>0:
            err = "Invalid simbols: "+str(invalid)
        else:
            err = ""

        if (request.form['src'] == 'max'):
            print('requesting max')
            return jsonify(post_data(cumrates, idx_rates))
        
        elif (request.form['src'] == 'ytd'):
            print('requesting ytd')
            #get last business day of last year
            last_day_of_last_year = pd.date_range('12/1/'+str(date.today().year-1), periods=1, freq='BM')
            
            #get cumrates from begining of the year and divide by last day of previous year
            ytd_cumrates = cumrates[str(date.today().year)+'-1-1':date.today()]/cumrates[last_day_of_last_year[0]]
            
            #repeat for index
            ytd_idx = idx_rates
            for i in idx:
                ytd_idx[i] = idx_rates[i][str(date.today().year)+'-1-1':date.today()]/idx_rates[i][last_day_of_last_year[0]]

            return jsonify(post_data(ytd_cumrates, ytd_idx))

        
        elif (request.form['src'] == '1month'):
            print('requesting 1month')
            delta = BDay(20)
            last = BDay(21)
        
            month_cumrates = cumrates[cumrates.index[-1]-delta:cumrates.index[-1]]/cumrates[cumrates.index[-1]-last]
        
            month_idx = idx_rates
            for i in idx:
                month_idx[i] = idx_rates[i][idx_rates[i].index[-1]-delta:idx_rates[i].index[-1]]/idx_rates[i][idx_rates[i].index[-1]-last]
        
            return jsonify(post_data(month_cumrates, month_idx))

        elif (request.form['src'] == '1year'):
            print('requesting 1year')
            
            delta = BDay(250)
            last = BDay(251)
            
            year_cumrates = cumrates[cumrates.index[-1]-delta:cumrates.index[-1]]/cumrates[cumrates.index[-1]-last]
            
            year_idx = idx_rates
            
            for i in idx:
                year_idx[i] = idx_rates[i][idx_rates[i].index[-1]-delta:idx_rates[i].index[-1]]/idx_rates[i][idx_rates[i].index[-1]-last]
           
            return jsonify(post_data(year_cumrates, year_idx))

    return Response("ok")

def post_data(cumrates, idx_rates):
    # turn index to strings, remove time
    dates_l=list(str(x) for x in cumrates.index)
    for i in range(0, len(dates_l)):
        dates_l[i]=dates_l[i].split(' ')[0]
   
    #create lists for highcharts
    pf_rates=list((cumrates.values-1)*100)

    json_data = {}
    json_data["axis"]=dates_l
    json_data["data"]=pf_rates
    for key in idx_rates.keys():
        json_data[key]=list((idx_rates[key].values-1)*100)

    return json_data


@performance.route('/performance')
@login_required
def performance():
    
    return render_template('performance/performance.html')


