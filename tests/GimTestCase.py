import os
import unittest
import tempfile

from flask_sqlalchemy import SQLAlchemy

from app import app, db
from app.mod_api import models

class GimTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestingConfig')
        self.client = app.test_client()
        self.db = db

class GimFreshDBTestCase(GimTestCase):
    def setUp(self):
        super(GimFreshDBTestCase, self).setUp()
        self.db.drop_all()
        self.db.create_all()
        models.Permission.initialize_permissions()
        models.Usergroup.initialize_usergroups()
        
    def tearDown(self):
        super(GimFreshDBTestCase, self).tearDown()
        self.db.drop_all()
