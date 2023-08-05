XAUTH_SERVICES = (
    'openid',
    'oauth1',
    'oauth2',
    'simple',
)
XAUTH_HOSTNAME = 'localhost:8000'
XAUTH_SIGNUP_SUCCESS_URL = '/'
XAUTH_SIGNIN_SUCCESS_URL = '/'
XAUTH_LOGOUT_URL = '/'
XAUTH_ACCOUNT_FORM = 'xauth.forms.AccountForm'
XAUTH_PROFILE_FIELDS = ['nickname', 'email']
XAUTH_ACTIVATION_REQUIRED = True

XAUTH_SIMPLE_SIGNUP_METHOD = 'username' # or 'email'
