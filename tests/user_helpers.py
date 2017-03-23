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

def patch(client, url, auth, **kwargs):
    return client.patch(
        url,
        data=json.dumps({k: v for k,v in kwargs.items()}),
        content_type='application/json',
        headers={'Authorization': auth}
        )

def delete(client, url, auth):
    return client.delete(
        url,
        headers={'Authorization': auth}
        )

def patch_user(client, u_id, auth, **kwargs):
    return patch(client, '/api/Users/%d' % u_id, auth, **kwargs)

def delete_user(client, u_id, auth):
    return delete(client, '/api/Users/%d' % u_id, auth)

def get_user(client, u_id, auth):
    return get(client, '/api/Users/%d' % u_id, Authorization=auth)

def logout_user(client, auth):
    return get(client, '/api/Auth/Logout', Authorization=auth)

def get_user_status(client, auth):
    return get(client, '/api/Auth/Status', Authorization=auth)

def register_user(client, email, password):
    return post(client, '/api/Auth/Register', email=email, password=password)

def login_user(client, email, password):
    return post(client, '/api/Auth/Login', email=email, password=password)
    