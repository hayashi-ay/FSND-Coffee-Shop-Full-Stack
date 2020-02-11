import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'hayashi-ay.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee_shop_auth'

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError('Authorization header is missing', 401)

    auth_header = request.headers['Authorization']
    header_parts = auth_header.split()

    if len(header_parts) != 2:
        raise AuthError('Authorization header is malformed', 401)
    elif header_parts[0].lower() != 'bearer':
        raise AuthError('Authorization header is malformed', 401)

    token = header_parts[1]
    return token

def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads( jsonurl.read() )

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError('Authorization header is malformed', 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError('Token is expired', 401)
        except Exception:
            raise AuthError('Unbale to parse authentication token', 400)

    raise AuthError('Unable to find the appropriate key', 400)

def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError('Permissions not included in JWT', 400)

    if permission not in payload['permissions']:
        raise AuthError('You don\'t have a permission', 401)

    return True

def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                jwt = get_token_auth_header()
                payload = verify_decode_jwt(jwt)
                check_permissions(permission,payload)
                return f(payload,*args, **kwargs)
            except AuthError as e:
                abort(e.status_code, e.error)
        return wrapper
    return requires_auth_decorator