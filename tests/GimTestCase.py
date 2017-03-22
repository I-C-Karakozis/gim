import os
import unittest
import tempfile

from flask_sqlalchemy import SQLAlchemy
from app import app, db

class GimTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.db = db
        
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

class GimFreshDBTestCase(GimTestCase):
    def setUp(self):
        super(GimFreshDBTestCase, self).setUp()
        self.db.drop_all()
        self.db.create_all()
        
    def tearDown(self):
        super(GimFreshDBTestCase, self).tearDown()
        self.db.drop_all()
