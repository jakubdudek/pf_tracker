import os
from flask import render_template, flash, redirect, url_for, session, g
from flask.ext.login import login_required, current_user
from .. import db
from ..models import User
from . import portfolio
from .forms import ProfileForm
from ..lib import pf_utils
from ..lib import new_utils as pf
import pandas as pd
from pandas import DataFrame


from app import cache


@portfolio.route('/')
@login_required
def index():
    mastertable = []
    if(os.path.isfile(session['csv_path'])):
        #[pf, pfindex, indextickers, piedata, pfmetrics, mastertable] = pf_utils.process_pf_data(csvfile=session['csv_path'])
        holdings_ts_list = pf.get_holdings(session['csv_path'])[0]
        
        holdings_ts_list = {i:j.cumsum() for i,j in holdings_ts_list.items()}
        holdings_ts_list = {i:j[-1] for i,j in holdings_ts_list.items()}
        holdings_ts_list = {i:round(j, 2) for i,j in holdings_ts_list.items()}
        holdings_dict = {i:j for i,j in holdings_ts_list.items() if j != 0.0}
        
        holdings_df=DataFrame(0.0, index=holdings_dict.keys(), columns=['Shares', 'Price', 'Market Value'])
        holdings_df['Shares']=holdings_dict.values()
        
        holdings_list = pf.df_to_obj_list(holdings_df, 'Ticker')
        
        print(holdings_list)
    return render_template('portfolio/portfolio.html', holdings=holdings_list)


@portfolio.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    talk_list = user.talks.order_by(Talk.date.desc()).all()
    return render_template('talks/user.html', user=user, talks=talk_list)


@portfolio.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('portfolio.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('talks/profile.html', form=form)







