import json

def get(client, url, auth):
    return client.get(
        url,
        headers={'Authorization': auth},
        )

def post(client, url, auth, **kwargs):
    return client.post(
        url,
        data=json.dumps({k: v for k,v in kwargs.items()}),
        content_type='application/json',
        headers={'Authorization': auth}
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

def post_video(client, auth, **kwargs):
    return post(client, '/api/Videos', auth, **kwargs)

def patch_video(client, v_id, auth, **kwargs):
    return patch(client, '/api/Videos/%d' % v_id, auth, **kwargs)

def delete_video(client, v_id, auth):
    return delete(client, '/api/Videos/%d' % v_id, auth)

def get_video(client, v_id, auth):
    return get(client, '/api/Videos/%d' % v_id, auth)

def get_all_videos(client, auth):
    return get(client, '/api/Videos', auth)
