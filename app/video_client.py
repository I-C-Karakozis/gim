import ftplib
import StringIO
import hashlib

def get_filepath(vid):
    m = hashlib.md5()
    m.update(vid)
    return m.hexdigest()

def retrieve_videos(videos):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('searcher', 'password') # TODO: move creds to config.py
        res = []
        for video in videos:
            r = StringIO.StringIO()
            ftp.retrbinary('RETR %s' % video, r.write)
            r.seek(0)
            res.append(r)
        return res

def delete_videos(videos):
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('deleter', 'password') # TODO: move creds to config.py
        for video in videos:
            ftp.delete(video)

def upload_video(video, fp):
    fp.seek(0)
    with FTPClient('127.0.0.1', '8888') as ftp: # TODO: move to config.py
        ftp.login('poster', 'password') # TODO: move creds to config.py
        ftp.storbinary('STOR %s' % video, fp)

class FTPClient:
    def __init__(self, host, port):
        self.ftp = ftplib.FTP()
        self.ftp.connect(host, port)

    def __enter__(self):
        return self.ftp

    def __exit__(self, error, value, traceback):
        self.ftp.quit()
