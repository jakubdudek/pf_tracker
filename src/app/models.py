from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request
from flask.ext.login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64),
                      nullable=False, unique=True, index=True)
    username = db.Column(db.String(64),
                         nullable=False, unique=True, index=True)
    is_admin = db.Column(db.Boolean)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    avatar_hash = db.Column(db.String(32))
    portfolio = db.relationship('Portfolio', lazy='dynamic', backref='owner')
    transactions = db.relationship('Transactions', lazy='dynamic', backref='owner')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or \
               hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    id = db.Column(db.Integer, primary_key=True)
    holdings = db.Column(db.PickleType)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Transactions(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)

    Trade = db.Column(db.String(64))
    Symbol = db.Column(db.String(64))
    Shares = db.Column(db.Float)
    Price = db.Column(db.Float)
    Comission = db.Column(db.Float)
    Fee = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))




