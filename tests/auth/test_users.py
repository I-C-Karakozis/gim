from tests import GimTestCase
from tests import user_helpers as api
from tests import http_helpers as http

import json

class TestUsers(GimTestCase.GimFreshDBTestCase):
    def test_get(self):
        with self.client:
            # register a user
            auth, u_id = api.register_user_quick(self.client)

            # GET on the Users endpoint with the user's id
            response = api.get_user(self.client,
                                    u_id=u_id,
                                    auth=auth
                               )
            assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND

    def test_patch(self):
        # register a user
        auth, u_id = api.register_user_quick(self.client)
        
        # PATCH on the Users endpoint with user's id
        response = api.patch_user(self.client,
                                  u_id=u_id,
                                  auth=auth
                                  )
        assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND

    def test_delete(self):
        # register a user
        auth, u_id = api.register_user_quick(self.client)

        # DELETE on the Users endpoint with the user's id
        response = api.delete_user(self.client,
                                   u_id=u_id,
                                   auth=auth
                                   )
        assert response.status_code != http.UNAUTH and response.status_code != http.NOT_FOUND
