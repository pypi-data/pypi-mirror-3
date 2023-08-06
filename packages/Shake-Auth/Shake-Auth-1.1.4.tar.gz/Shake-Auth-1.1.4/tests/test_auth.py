# -*- coding: utf-8 -*-
"""
"""
import os
from datetime import datetime

import pytest
import shake_auth
from shake import Shake
from solution import SQLAlchemy


app_settings = {
    'SECRET_KEY': 'ee6864874322ff97d0f7380e815ff0a02493783c',
}

auth_settings = {
    'pepper': 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6',
}


def get_user_model():
    db = SQLAlchemy()
    User = shake_auth.get_user_model(db)
    db.create_all()
    return User


def get_auth(hash_alg='sha512', hash_cost=10):
    User = get_user_model()
    settings = auth_settings.copy()
    settings['hash_alg'] = hash_alg
    settings['hash_cost'] = hash_cost
    settings['pepper'] = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    return shake_auth.Auth(User, **settings)


def test_settings():
    pepper = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    User = get_user_model()

    with pytest.raises(AssertionError):
        shake_auth.Auth(User)
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, hash_alg='md5')
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, hash_cost=-1)
    with pytest.raises(AssertionError):
        shake_auth.Auth(User, pepper=pepper, reset_expire=-1)


def test_create_user():
    auth = get_auth()
    user = auth.create_user(u'admin', u'passw')
    assert user.login == u'admin'
    alg, cost, salt, hashed = user.password.split('$')
    assert alg == 'dsha512'
    assert int(cost) == auth.settings['hash_cost']


def test_sign_in():
    auth = get_auth()
    user = auth.create_user(u'admin', u'passw')

    def index(request):
        auth.sign_in(request, user)
        return request.user.login
    
    def get_user(request):
        return request.user.login

    app = Shake(__file__, app_settings)
    auth.init_app(app)
    app.add_url('/', index)
    app.add_url('/user/', get_user)
    c = app.test_client()
    
    resp = c.get('/')
    resp2 = c.get('/user/')

    assert resp.headers.get('Set-Cookie').startswith('shake_session')
    assert resp.data == user.login
    assert resp2.data == resp.data


def test_sign_out():
    auth = get_auth()
    user = auth.create_user(u'admin', u'passw')

    def index(request):
        auth.sign_in(request, user)
        assert request.user
    
    def sign_out(request):
        auth.sign_out(request)
        assert request.user is None

    app = Shake(__file__, app_settings)
    auth.init_app(app)
    app.add_url('/', index)
    app.add_url('/sign_out/', sign_out)
    c = app.test_client()

    resp = c.get('/')
    resp = c.get('/sign_out/')


def test_authenticate_by_password():
    auth = get_auth()
    credentials = {
        'login': u'admin',
        'password': u'passw',
    }
    user = auth.create_user(credentials['login'], credentials['password'])
    auser = auth.authenticate(credentials)

    assert auser
    assert user == auser
    assert not auth.authenticate({'login': credentials['login']})
    assert not auth.authenticate({'password': credentials['password']})

    bad = credentials.copy()
    bad['login'] = 'meh'
    assert not auth.authenticate(bad)

    bad = credentials.copy()
    bad['password'] = 'meh'
    assert not auth.authenticate(bad)


def test_authenticate_by_token():
    auth = get_auth()
    app = Shake(__file__, app_settings)
    auth.init_app(app)

    user = auth.create_user(u'admin', u'passw')
    token = auth.get_reset_token(user)

    auser = auth.authenticate({'token': str(token)})

    assert auser
    assert user == auser
    assert not auth.authenticate({})
    assert not auth.authenticate({'token': u'lalala'})


def test_authenticate_and_update():
    User = get_user_model()

    settings = auth_settings.copy()
    settings['hash_alg'] = 'sha512'
    settings['hash_cost'] = 10
    settings['pepper'] = 'dc47d3062962d5b9f5828dccc47b9d7eda95ecf6'
    auth = shake_auth.Auth(User, **settings)

    settings = settings.copy()
    settings['hash_alg'] = 'bcrypt'
    auth2 = shake_auth.Auth(User, **settings)

    credentials = {
        'login': u'admin',
        'password': u'passw',
    }
    user = auth.create_user(credentials['login'], credentials['password'])
    oldlogin = user.login
    oldpassw = user.password
    auser = auth2.authenticate(credentials, update=True)

    assert auser
    assert auser.login == oldlogin
    assert auser.password != oldpassw
    alg, cost, hashed = user.password.split('$')
    assert alg == 'bcrypt'

