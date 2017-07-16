import json
import StringIO
import random
import string

import user_helpers as users_api

DELETE_THRESHOLD = -4

def get(client, url, auth):
    return client.get(
        url,
        headers={'Authorization': auth},
        )

def post(client, url, auth, video, filename, **kwargs):
    if video is not None:
        d = {k: v for k,v in kwargs.items()}
        d.update({'file': (video, filename)})
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

def post_video(client, auth, video=None, filename='video.mov', **kwargs):
    return post(client, '/api/Videos', auth, video, filename, **kwargs)

def post_video_quick(client, auth, content='abba', tags=['lately', 'ive']):
    response = post_video(client, auth, video=StringIO.StringIO(content), 
                      tags=tags,
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

def get_banned_video(client, v_id, auth):
    return get(client, '/api/BannedVideos/%d' % v_id, auth)

def get_all_videos(client, auth, tags=[], **kwargs):
    query_string = '&'.join(['%s=%s' % (k, v) for k,v in kwargs.items()]) + '&' + '&'.join(['tag=%s' % t for t in tags])
    return get(client, '/api/Videos?%s' % query_string, auth)

def get_video_file(client, v_id, auth):
    return get(client, '/api/VideoFiles/%d' %v_id, auth)

def get_banned_video_file(client, v_id, auth):
    return get(client, '/api/BannedVideoFiles/%d' %v_id, auth)

def get_thumbnail(client, v_id, auth):
    return get(client, '/api/Thumbnails/%d' %v_id, auth)

def upvote_video(client, v_id, auth):
    return patch_video(client,
                       v_id,
                       auth=auth,
                       upvote=True,
                       flagged=False
                       )

def downvote_video(client, v_id, auth):
    return patch_video(client,
                       v_id,
                       auth=auth,
                       upvote=False,
                       flagged=False
                       )

def flag_video(client, v_id, auth):
    return patch_video(client,
                       v_id,
                       auth=auth,
                       upvote=False,
                       flagged=True
                       )

def ban_videos(client, v_ids):
    count = 0
    for v_id in v_ids:  
        for i in range(abs(DELETE_THRESHOLD) / 2 + 1):
                    email='goofy' + str(count) + '@goober.com'
                    auth, u_id = users_api.register_user_quick(client, email=email)
                    flag_video(client, v_id, auth)
                    count = count + 1

def generate_sample_feed(client, sortBy):
    contents = ['a', 'b', 'c', 'd', 'e']
    net_votes = [0, -1, 1, 2, -2]
    auth1, u_id1 = users_api.register_user_quick(client,
                                                 email='gim@gim.com'
                                                 )
    auth2, u_id2 = users_api.register_user_quick(client,
                                                 email='gim2@gim.com'
                                                 )

    video_ids = []
    for content in contents:
        v_id = post_video_quick(client,
                                 auth=auth1
                                 )
        video_ids.append(v_id)

    # upvote videos according to net_votes
    auths = (auth1, auth2)
    for net_vote, video_id in zip(net_votes, video_ids):
        upvotes = max(net_vote, 0)
        downvotes = abs(min(net_vote, 0))
        for i in range(upvotes):
            upvote_video(client,
                          video_id,
                          auth=auths[i]
                          )
        for j in range(downvotes):
            downvote_video(client,
                            video_id,
                            auth=auths[-(j+1)]
                            )

    if sortBy == 'popularity':
        intended_order = map(lambda x: x[1], 
                                 sorted(zip(net_votes, video_ids),
                                        cmp=lambda x, y: x[0] - y[0],
                                        reverse=True
                                        )
                                 )
    elif sortBy == 'post_recency':
        intended_order = [v_id for v_id in reversed(video_ids)]
    elif sortBy == 'upvote_recency':
        intended_order = [video_ids[3], video_ids[2]]

    return auth1, auth2, intended_order 

                  
