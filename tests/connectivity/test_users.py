from tests import GimTestCase
from tests import http_helpers as http

class TestUsersConnectivity(GimTestCase.GimTestCase):
    
    # test Users class: '/api/Users' requests
    def test_get(self):
        assert http.response(self.app.get, '/api/Users').status_code != http.NOT_FOUND

    # test User class: '/api/Users/<int:User_id>' requests
    def test_get(self):
        assert http.response(self.app.get, '/api/Users/5').status_code != http.NOT_FOUND

    def test_post(self):
        data = dict(User=5000)
        assert http.response(self.app.post, '/api/Users/5', data=data).status_code != http.NOT_FOUND

    def test_patch(self):
        data = dict(User=5000)
        assert http.response(self.app.post, '/api/Users/5', data=data).status_code != http.NOT_FOUND

    def test_delete(self):
        assert http.response(self.app.post, '/api/Users/5').status_code != http.NOT_FOUND
