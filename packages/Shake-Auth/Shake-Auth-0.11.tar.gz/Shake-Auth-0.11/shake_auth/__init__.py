# -*- coding: utf-8 -*-
"""
# Shake-Auth

Shake's awesome authentication extension.


---------------------------------------
Copyright © 2011 by [Lúcuma labs] (http://lucumalabs.com).  
See `AUTHORS.md` for more details.  
License: [MIT License] (http://www.opensource.org/licenses/mit-license.php).    
"""
from .auth import (Auth, CREDENTIAL_LOGIN, CREDENTIAL_PASSWORD,
    CREDENTIAL_TOKEN, UserExistsError, UserDoesNotExistsError,
    PasswordTooShortError)
from .perms import protected, is_valid, invalid_csrf_secret
from .utils import get_user_model, LazyUser, Token

__version__ = '0.11'