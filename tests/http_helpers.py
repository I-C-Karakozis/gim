OK = 200
CREATED = 201
ACCEPTED = 202
MOVED_PERM = 301
BAD_REQ = 400
UNAUTH = 401
FORBIDDEN = 403
NOT_FOUND = 404

def response(method, url, data=None):
    return method(url) if data is None else method(url, data, follow_redirects=True)
