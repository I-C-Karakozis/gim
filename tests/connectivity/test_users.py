from tests import GimTestCase
from tests import http_helpers as http

class TestUsersConnectivity(GimTestCase.GimTestCase):
    
    def test_get(self):
        assert http.response(self.client.get, '/api/User/5').status_code != http.NOT_FOUND

    def test_post(self):
        assert http.response(self.client.post, '/api/Users').status_code != http.NOT_FOUND

    def test_patch(self):
        assert http.response(self.client.patch, '/api/User/5').status_code != http.NOT_FOUND

    def test_delete(self):
        assert http.response(self.client.delete, '/api/User/5').status_code != http.NOT_FOUND
