from .base import *

DEBUG = False

# HSTS: Change this to the max age defined by the server.
# Comment it to disable HSTS. (NOT recommended)
SECURE_HSTS_SECONDS = 63072000

# SSL Redirecting
# CAUTION: Needs to be set to True when using SSL. This will redirect all the traffic to HTTPS.
# Set to False when you are not using SSL.
SECURE_SSL_REDIRECT = True

# Secure session cookie
# Encrypts session cookies. Recommended: True
SESSION_COOKIE_SECURE = True