import os, csv, time
from flask import render_template, current_app, request, redirect, url_for, flash, json, jsonify, make_response, Response
from . import performance
from .forms import UploadForm
from werkzeug import secure_filename
from flask_wtf.file import FileField

import pandas as pd

from flask.ext.login import login_required, current_user, session
from ..models import User
from ..lib import pf_utils as utils
from ..lib import new_utils as pf
from pandas.tseries import offsets
from datetime import date

from app import cache

@performance.route('/get_performance', methods=['GET', 'POST'])
@login_required
def get_performance():
    if request.method == "POST":
        
        cumrates = cache.get('cumrates')
        if(cumrates is None):
            #get portfolio data
            [worth, cumrates, invalid]=pf.get_rates(session['csv_path'])
            cache.set('cumrates', cumrates)
        
        
        idx = cache.get('idx')
        if(idx is None):
            #get index data
            idx = pf.get_index_rates(pf.get_cashflow(pf.get_trans(session['csv_path'])[0]), ['spy', 'iwm'])
            cache.set('idx', idx)

        if ('max' in request.form):
            print('requesting max')
            [dates_l, pf_rates, spy_rates_l, iwm_rates_l] = post_data(cumrates, idx)
        
        elif ('ytd' in request.form):
            print('requesting ytd')
            #get last business day of last year
            last_day_of_last_year = pd.date_range('12/1/'+str(date.today().year-1), periods=1, freq='BM')
            
            #get cumrates from begining of the year and divide by last day of previous year
            ytd_cumrates = cumrates[str(date.today().year)+'-1-1':date.today()]/cumrates[last_day_of_last_year[0]]
            
            #repeat for index
            ytd_idx = idx
                            
            ytd_idx['spy'] = idx['spy'][str(date.today().year)+'-1-1':date.today()]/idx['spy'][last_day_of_last_year[0]]
            ytd_idx['iwm'] = idx['iwm'][str(date.today().year)+'-1-1':date.today()]/idx['iwm'][last_day_of_last_year[0]]
                                    
            [dates_l, pf_rates, spy_rates_l, iwm_rates_l] = post_data(ytd_cumrates, ytd_idx)

        
        elif ('1month' in request.form):
            print('requesting 1month')
            delta = offsets.BDay(20)
            last = offsets.BDay(21)
        
            month_cumrates = cumrates[cumrates.index[-1]-delta:cumrates.index[-1]]/cumrates[cumrates.index[-1]-last]
        
            month_idx = idx
        
            month_idx['spy'] = idx['spy'][idx['spy'].index[-1]-delta:idx['spy'].index[-1]]/idx['spy'][idx['spy'].index[-1]-last]
            month_idx['iwm'] = idx['iwm'][idx['iwm'].index[-1]-delta:idx['iwm'].index[-1]]/idx['iwm'][idx['iwm'].index[-1]-last]
        
        
            [dates_l, pf_rates, spy_rates_l, iwm_rates_l] = post_data(month_cumrates, month_idx)

        elif ('1year' in request.form):
            print('requesting 1year')
            
            delta = offsets.BDay(250)
            last = offsets.BDay(251)
            
            year_cumrates = cumrates[cumrates.index[-1]-delta:cumrates.index[-1]]/cumrates[cumrates.index[-1]-last]
            
            year_idx = idx
            
            year_idx['spy'] = idx['spy'][idx['spy'].index[-1]-delta:idx['spy'].index[-1]]/idx['spy'][idx['spy'].index[-1]-last]
            year_idx['iwm'] = idx['iwm'][idx['iwm'].index[-1]-delta:idx['iwm'].index[-1]]/idx['iwm'][idx['iwm'].index[-1]-last]
            
            [dates_l, pf_rates, spy_rates_l, iwm_rates_l] = post_data(year_cumrates, year_idx)


        #jsonify response
        return jsonify(axis=dates_l, data=pf_rates, spy=spy_rates_l, iwm=iwm_rates_l)

    return Response("ok")

def post_data(cumrates, idx):
    # turn index to strings, remove time
    dates_l=list(str(x) for x in cumrates.index)
    for i in range(0, len(dates_l)):
        dates_l[i]=dates_l[i].split(' ')[0]
    
    #create lists for highcharts
    pf_rates=list((cumrates.values-1)*100)
    spy_rates_l = list(((idx['spy'].values-1)*100))
    iwm_rates_l = list(((idx['iwm'].values-1)*100))

    return dates_l, pf_rates, spy_rates_l, iwm_rates_l


@performance.route('/performance')
@login_required
def performance():
    
    return render_template('performance/performance.html')


