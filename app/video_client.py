import ftplib
import StringIO
import hashlib

def get_filepath(vid):
    m = hashlib.md5()
    m.update(vid)
    return m.hexdigest()

def retrieve_videos(videos, is_hof=False):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        if is_hof:
            ftp.login('hof_searcher', 'password')
        else:
            ftp.login('searcher', 'password') # TODO: move creds to config.py
        res = []
        for video in videos:
            r = StringIO.StringIO()
            ftp.retrbinary('RETR %s' % video, r.write)
            r.seek(0)
            res.append(r)
        return res

def delete_videos(videos, is_hof=False):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        if is_hof:
            ftp.login('hof_deleter', 'password')
        else:
            ftp.login('deleter', 'password') # TODO: move creds to config.py
        for video in videos:
            ftp.delete(video)

def upload_video(video, fp, is_hof=False):
    fp.seek(0)
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        if is_hof:
            ftp.login('hof_poster', 'password')
        else:
            ftp.login('poster', 'password') # TODO: move creds to config.py
        ftp.storbinary('STOR %s' % video, fp)



def retrieve_thumbnails(thumbnails):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('thumb_searcher', 'password')
        res = []
        for thumbnail in thumbnails:
            r = StringIO.StringIO()
            try:
                ftp.retrbinary('RETR %s' % thumbnail, r.write)
                r.seek(0)
                res.append(r)
            except:
                res.append(r)
        return res

def delete_thumbnails(thumbnails):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('thumb_deleter', 'password')
        for thumbnail in thumbnails:
            ftp.delete(thumbnail)

def upload_thumbnail(thumbnail, fp):
    fp.seek(0)
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('thumb_poster', 'password')
        ftp.storbinary('STOR %s' % thumbnail, fp)

class FTPClient:
    def __init__(self, host, port):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)

    def __enter__(self):
        return self.ftp

    def __exit__(self, error, value, traceback):
        self.ftp.quit()
