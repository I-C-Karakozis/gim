from tests import GimTestCase
from tests import http_helpers as http

class TestVideosConnectivity(GimTestCase.GimTestCase):
    
    # test Videos class: '/api/Videos' requests
    def test_get(self):
        assert http.response(self.app.get, '/api/Videos').status_code != http.NOT_FOUND

    def test_post(self):
        data = dict(video=5000)
        assert http.response(self.app.post, '/api/Videos', data=data).status_code != http.NOT_FOUND



    # test Video class: '/api/Videos/<int:video_id>' requests
    def test_get(self):
        assert http.response(self.app.get, '/api/Videos/5').status_code != http.NOT_FOUND

    def test_patch(self):
        data = dict(video=5000)
        assert http.response(self.app.post, '/api/Videos/5', data=data).status_code != http.NOT_FOUND

    def test_delete(self):
        assert http.response(self.app.post, '/api/Videos/5').status_code != http.NOT_FOUND
