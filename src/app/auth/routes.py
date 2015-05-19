import os

from flask import render_template, current_app, request, redirect, url_for, flash, session, g, json
from flask.ext.login import login_user, logout_user, login_required, current_user, current_app
from ..models import User
from . import auth
from .forms import LoginForm, RegisterForm
from app import db, cache
from ..lib import pf_utils as utils

import pandas as pd

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if not current_app.config['DEBUG'] and not current_app.config['TESTING'] \
        and not request.is_secure:
        return redirect(url_for('.login', _external=True, _scheme='https'))
    form = LoginForm()
    if form.validate_on_submit():
        print('form is validated')
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid email or password.')
            return redirect(url_for('.login'))
        #user is now logged in, make session permanent and save cvs path in session
        login_user(user, form.remember_me.data)
        session.permanent = True
        session['csv_path'] = os.path.join(current_app.config['UPLOAD_FOLDER'], current_user.get_id() + '.csv')

        #if the csv exists, process it, else redirect to empty portfolio
        if(os.path.isfile(session['csv_path'])):
            return redirect(url_for('.process_csv'))
        return redirect(request.args.get('next') or url_for('portfolio.index'))
    return render_template('auth/login.html', form=form)



@auth.route('/process_csv')
@login_required
def process_csv():
    print('processing'+ session['csv_path'])
    #pf, pfindex, indextickers, piedata, pfmetrics, mastertable] = utils.process_pf_data(csvfile=session['csv_path'])
    #cache.set('portfolio', mastertable)
    
    return redirect(request.args.get('next') or url_for('portfolio.index'))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    session.clear()
    return redirect(url_for('.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        password = form.password.data;
        password2 = form.password2.data;
        if password != password2:
            flash('Passwords did not match.')
            return render_template('auth/register.html', form=form)
        db.create_all()
        user = User(email=form.email.data, username=form.name.data, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)

