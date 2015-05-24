import os

from flask import render_template, current_app, request, redirect, url_for, flash, session, g, json
from flask.ext.login import login_user, logout_user, login_required, current_user, current_app
from ..models import User
from . import auth
from .forms import LoginForm, RegisterForm
from app import db, cache
from ..pf_utils import pf_utils as utils
from ..pf_utils import pf_utils as pf

import pandas as pd
from app import db

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
                
        return redirect(request.args.get('next') or url_for('portfolio.index'))

    return render_template('auth/login.html', form=form)

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

