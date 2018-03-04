"""
PiLock Production Settings

To be used in Production only.

These settings disable debug mode and enable HSTS, SSL redirection and session cookie encryption.

"""

from .base import *

DEBUG = False

# HSTS: Change this to the max age defined by the server.
# Comment it to disable HSTS. (NOT recommended)
SECURE_HSTS_SECONDS = 63072000

# SSL Redirecting
SECURE_SSL_REDIRECT = True

# Secure session cookie
# Encrypts session cookies.
SESSION_COOKIE_SECURE = True