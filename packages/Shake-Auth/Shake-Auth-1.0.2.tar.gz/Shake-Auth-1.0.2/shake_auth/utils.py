# -*- coding: utf-8 -*-
"""
    # shake_auth.utils
    
    
    --------    
    Copyright © 2010–2011 by Lúcuma labs (http://lucumalabs.com).

    MIT License. (http://www.opensource.org/licenses/mit-license.php)
    
"""
try:
    import bcrypt
except ImportError:
    bcrypt = None
from datetime import datetime
import hashlib
import os

from jinja2 import PackageLoader
from shake import url_for, Render


DEFAULT_HASH_COST = 10

auth_loader = PackageLoader('shake_auth', 'views')
auth_render = Render(loader=auth_loader)


class LazyUser(object):
    """Loads the current user from the session, but only when needed.
    
    Instead of just storing the user id, we generate a hash from the
    password *salt*. That way, an admin or the user herself can invalidate
    the login in other computers just by changing (or re-saving) her password.
    """

    SESSION_NAME = '_uhm'
    
    def __init__(self, db, User):
        self.db = db
        self.User = User
    
    def __get__(self, request, obj_type=None):
        user = None
        uhmac = request.session.get(self.SESSION_NAME)
        if uhmac:
            try:
                uid, mac = uhmac.split('$')
                user = self.db.query(self.User).get(uid)
                if not user or uhmac != self.get_user_hmac(user):
                    raise ValueError
            except ValueError:
                user = None
                request.session.invalidate()
        request.user = user
        return user
    
    @classmethod
    def get_user_hmac(cls, user):
        # This use as a seed a few chars from the password SALT.
        # NOT from the real password.
        mac = hashlib.sha256(user.password[10:18])
        mac = mac.hexdigest()[:8]
        return '%s$%s' % (user.id, mac)
    
    @classmethod
    def sign_in(cls, request, user):
        request.session[cls.SESSION_NAME] = cls.get_user_hmac(user)
        request.user = user
    
    @classmethod
    def sign_out(cls, request):
        request.session.invalidate()
        request.user = None


class Token(object):
    
    def __init__(self, token, expire_after):
        self.token = token
        self._expire_after = expire_after
    
    @property
    def expire_after(self):
        return self._expire_after
    
    @property
    def link(self):
        return url_for('auth.check_token', external=True, token=self.token)
    
    def __repr__(self):
        return self.token


def split_hash(hashed):
    """Split the password hash into it's components.
    
    Returns a tuple with the hash name, cost and salt.
        
        >>> split_hash('sha512$13$mysalt$myhash')
        ('sha512', 13, 'mysalt')
        >>> split_hash('bcrypt$06$mysaltyhash')
        ('bcrypt', 6, 'mysaltyhash')
    
    """
    lhashed = hashed.split('$')
    if len(lhashed) < 3:
        raise ValueError
    return lhashed[0], int(lhashed[1]), lhashed[2]


def hash_sha256(password, cost=DEFAULT_HASH_COST, salt=None, pepper=''):
    """SHA-256 password hashing."""
    assert cost >= 0
    salt = salt or hashlib.sha256(os.urandom(64)).hexdigest()
    password += pepper
    hashed = hashlib.sha256(salt + password).hexdigest()
    # Key strengthening
    for i in xrange(2 ** cost):
        hashed = hashlib.sha256(hashed + salt).hexdigest()
    return 'sha256$%i$%s$%s' % (cost, salt, hashed)


def hash_sha512(password, cost=DEFAULT_HASH_COST, salt=None, pepper=''):
    """SHA-512 password hashing."""
    assert cost >= 0
    salt = salt or hashlib.sha512(os.urandom(64)).hexdigest()
    password += pepper
    hashed = hashlib.sha512(salt + password).hexdigest()
    # Key strengthening
    for i in xrange(2 ** cost):
        hashed = hashlib.sha512(hashed + salt).hexdigest()
    return 'sha512$%i$%s$%s' % (cost, salt, hashed)


def hash_bcrypt(password, cost=DEFAULT_HASH_COST, hashed=None, pepper=''):
    """OpenBSD Blowfish password hashing.
    
    Requires py-bcrypt <http://pypi.python.org/pypi/py-bcrypt/>
    
    It hashes passwords using a version of Bruce Schneier's Blowfish
    block cipher with modifications designed to raise the cost of
    off-line password cracking, so it can be increased as computers get faster.
    
    Returns a string with the following format (without the spaces):
    "bcrypt $ cost $ salted_hashed_password"
    """
    assert cost >= 4
    # In this implementation of the algorithm, bcrypt hashes
    # starts with '$2a$'. This is replaced with 'bcrypt$' to maintain
    # consistency with the other hash algorithms in the module.
    if hashed:
        salt = hashed.replace('bcrypt$', '$2a$', 1)
    else:
        assert cost >= 0
        salt = bcrypt.gensalt(cost)
    password += pepper
    hashed = bcrypt.hashpw(password, salt)
    return hashed.replace('$2a$', 'bcrypt$', 1)


def get_user_model(db):
    """ """
    
    class User(db.Model):
        
        id = db.Column(db.Integer, primary_key=True)
        login = db.Column(db.Unicode(64),
            unique=True, nullable=False)
        email = db.Column(db.String(64),
            nullable=True)
        password = db.Column(db.String(140), nullable=True)
        date_joined = db.Column(db.DateTime, default=datetime.utcnow,
            nullable=False)
        last_sign_in = db.Column(db.DateTime,
            nullable=True)
        status = db.Column(db.String(1),
            default='A', nullable=False)
        
        def __init__(self, login, password=None, email=None):
            self.login = login
            self.password = password
            self.email = email
        
        def __repr__(self):
            if self.email:
                return '<User %s (%s)>' % (self.login, self.email)
            return '<User %s>' % self.login
        
        @property
        def is_active(self):
            return self.status == 'A'
        
        @property
        def is_suspended(self):
            return self.status == 'S'
    
    return User

