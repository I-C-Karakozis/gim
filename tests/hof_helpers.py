def get(client, url, auth):
    return client.get(
        url,
        headers={'Authorization': auth},
        )

def get_all_hof_videos(client, auth):
    return get(client, '/api/HallOfFame', auth)

def get_video_file(client, hof_id, auth):
    return get(client, '/api/HallOfFameFiles/%d' %hof_id, auth)
