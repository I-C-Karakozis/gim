import json

def get(client, url, **kwargs):
    return client.get(
        url,
        headers={k: v for k,v in kwargs.items()},
        )

def post(client, url, **kwargs):
    return client.post(
        url,
        data=json.dumps({k: v for k,v in kwargs.items()}),
        content_type='application/json'
        )

def logout_user(client, auth):
    return get(client, '/api/Auth/Logout', Authorization=auth)

def get_user(client, auth):
    return get(client, '/api/Auth/Status', Authorization=auth)

def register_user(client, email, password):
    return post(client, '/api/Auth/Register', email=email, password=password)

def login_user(client, email, password):
    return post(client, '/api/Auth/Login', email=email, password=password)
    
