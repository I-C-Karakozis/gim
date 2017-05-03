from app import app
from app.mod_api.delete_expired_videos import delete_expired_videos

from tests import user_helpers as users_api
from tests import video_helpers as videos_api

import math
import datetime
import time

def delete_expired():
    diff = datetime.timedelta(seconds = 1)
    time.sleep(3)
    now = datetime.datetime.now()
    threshold_datetime = now - diff

    delete_expired_videos(threshold_datetime)

def simulate_hof(client, number_of_videos):
    contents = [str(i) for i in range(number_of_videos)]
    net_votes = [(math.pow(-1, i) * i) for i in range(number_of_videos)]
    emails = [('gim' + contents[i] + '@gim.com') for i in range(number_of_videos)]

    auths = []
    for email in emails:
    	auth, u_id = users_api.register_user_quick(client, email=email) 
    	auths.append(auth)

    video_ids = []
    for content in contents:
        v_id = videos_api.post_video_quick(client,
                                           auth=auths[0], 
                                           content=content
                                           )
        video_ids.append(v_id)

    # upvote videos according to net_votes
    for net_vote, video_id in zip(net_votes, video_ids):
        upvotes = max(net_vote, 0)
        downvotes = abs(min(net_vote, 0))
        for i in range(int(upvotes)):
            videos_api.upvote_video(client,
                                    video_id,
                                    auth=auths[i]
                                    )
        for j in range(int(downvotes)):
            videos_api.downvote_video(client,
                                      video_id,
                                      auth=auths[j]
                                      )

    return net_votes, auths

