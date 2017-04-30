# Current server directory: /home/yannis/gim/gim/app/mod_api/delete_videos.py
# Logging at: /home/yannis/gim/cron.log
# Script runs every half an hour
# To see the relevant cronjob, type "crontab -e" at the command line on the server

from app import app, db
from app import video_client
from app.mod_api import models

import datetime
import sys

def delete_expired_videos(threshold_datetime):
    # collect filepaths and video ids
    expired_videos = models.Video.query.filter(models.Video.uploaded_on < threshold_datetime)

    # delete video file 
    video_client.delete_videos([video.filepath for video in expired_videos])

    for video in expired_videos:

        # delete votes and tag pairings of expired videos
        expired_votes = models.Vote.query.filter_by(v_id = video.v_id)
        for vote in expired_votes:
            vote.delete()

        video.delete()

# compute threshold datetime
def main():
    now = datetime.datetime.now()
    diff = datetime.timedelta(days = 3)
    threshold_datetime = now - diff

    delete_expired_videos(threshold_datetime)

if __name__ == 'main':
    main()

