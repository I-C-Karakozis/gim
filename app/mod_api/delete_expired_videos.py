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
    total_expired = len(expired_videos.all())

    for video in expired_videos:
        # delete votes and tag pairings of expired videos; update HoF too
        models.HallOfFame.add_to_hof_or_delete(video)

    return total_expired

# compute threshold datetime
def main():
    now = datetime.datetime.now()
    diff = datetime.timedelta(days = 3)
    threshold_datetime = now - diff

    total_deleted = delete_expired_videos(threshold_datetime)

    # needed for logging
    print 'Success: ' + str(total_deleted) + ' expired videos deleted.'

main()

