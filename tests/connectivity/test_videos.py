from tests import GimTestCase
from tests import http_helpers as http

class TestVideosConnectivity(GimTestCase.GimTestCase):
    def test_get(self):
        assert http.response(self.app.get, '/api/Videos').status_code != http.NOT_FOUND

    def test_post(self):
        data = dict(video=5000)
        assert http.response(self.app.post, '/api/Videos', data=data).status_code != http.NOT_FOUND
