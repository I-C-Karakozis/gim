import os
import app
import unittest
import tempfile

class GimTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])	
