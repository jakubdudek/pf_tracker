from flask import render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from .. import db
from ..models import User
from . import portfolio
from .forms import ProfileForm
from ..pf_utils import pf_utils as pf
import pandas as pd

from app import cache

@portfolio.route('/')
@login_required
def index():
    holding_list = [];
    #try:
    tr_by_date_df=pd.read_sql_table('transaction_'+str(current_user.get_id()), db.engine, index_col='date')
    symbols=pf.get_symbols(tr_by_date_df)
        

    holdings_ts_list = pf.get_holdings(tr_by_date_df, symbols)
    holdings_df = pf.get_current_holdings(holdings_ts_list)
        
    cost_basis = pf.get_costbasis(tr_by_date_df)
        
    # add cost basis and realized gains
    holdings_df = holdings_df.join(cost_basis['basis'])
    holdings_df = holdings_df.join(cost_basis['realized'])
        
    #print(holdings_df)

    #    # turn into a list for datatables
    holdings_list = pf.df_to_obj_list(holdings_df, 'ticker')
    #print(holdings_list)

    #except:
    #    holdings_list =[]
    
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







