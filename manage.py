'''
This maintenace script heavily borrows from the Flask-Migrate docs:
https://flask-migrate.readthedocs.io/en/latest
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db
from app.mod_api import models

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
