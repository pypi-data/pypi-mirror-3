# -*- coding: utf-8 -*-
"""
"""
from datetime import datetime
import os

import pytest
from shake import Shake
from shake_auth import Auth, get_user_model
from shake_sqlalchemy import SQLAlchemy


app_settings = {
    'SECRET_KEY': 'ee6864874322ff97d0f7380e815ff0a02493783c',
}

auth_settings = {
    'pepper': 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6',
}

def init_db():
    db = SQLAlchemy()
    User = get_user_model(db)
    db.create_all()
    user = User(login=u'username', password=u'password')
    db.add(user)
    db.commit()
    return db, User, user


def test_sign_in():
    db, User, user = init_db()
    auth = Auth(auth_settings, db, User)

    def index(request):
        auth.sign_in(request, user)
        return request.user.login
    
    def get_user(request):
        return request.user.login

    app = Shake([], app_settings)
    auth.init_app(app)
    app.add_url('/', index)
    app.add_url('/user/', get_user)
    c = app.test_client()
    
    resp = c.get('/')
    resp2 = c.get('/user/')

    assert resp.headers.get('Set-Cookie').startswith('shake_session')
    assert resp.data == 'username'
    assert resp2.data == resp.data


def test_sign_out():
    db, User, user = init_db()
    auth = Auth(auth_settings, db, User)

    def index(request):
        auth.sign_in(request, user)
        assert request.user
    
    def sign_out(request):
        auth.sign_out(request)
        assert request.user is None

    app = Shake([], app_settings)
    auth.init_app(app)
    app.add_url('/', index)
    app.add_url('/sign_out/', sign_out)
    c = app.test_client()

    resp = c.get('/')
    resp = c.get('/sign_out/')

