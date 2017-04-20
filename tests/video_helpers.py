import json
import StringIO

def get(client, url, auth):
    return client.get(
        url,
        headers={'Authorization': auth},
        )

def post(client, url, auth, video, **kwargs):
    if video is not None:
        d = {k: v for k,v in kwargs.items()}
        d.update({'file': (video, 'video.mov')})
        return client.post(
            url,
            data=d,
            content_type='multipart/form-data',
            headers={'Authorization': auth}
            )
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

def post_video(client, auth, video=None, **kwargs):
    return post(client, '/api/Videos', auth, video, **kwargs)

def post_video_quick(client, auth):
    response = post_video(client, auth, video=StringIO.StringIO('abba'),
                      tags=['the', 'walking', 'living'],
                      lat=0.0,
                      lon=0.0
                      )
    data = json.loads(response.data.decode())
    return data['data']['video_id']

def patch_video(client, v_id, auth, **kwargs):
    return patch(client, '/api/Videos/%d' % v_id, auth, **kwargs)

def delete_video(client, v_id, auth):
    return delete(client, '/api/Videos/%d' % v_id, auth)

def get_video(client, v_id, auth):
    return get(client, '/api/Videos/%d' % v_id, auth)

def get_all_videos(client, auth, tags=[], **kwargs):
    query_string = '&'.join(['%s=%s' % (k, v) for k,v in kwargs.items()]) + '&' + '&'.join(['tag=%s' % t for t in tags])
    return get(client, '/api/Videos?%s' % query_string, auth)

def get_video_file(client, v_id, auth):
    return get(client, '/api/VideoFiles/%d' %v_id, auth)
