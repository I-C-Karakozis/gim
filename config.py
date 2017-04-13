
class Config(object):
    # Statement for enabling the development environment
	DEBUG = True
	TESTING = False

	# Define the application directory
	import os
	BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

	# Define the database - we are working with
	# SQLite for this example
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
	DATABASE_CONNECT_OPTIONS = {}
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Application threads. A common general assumption is
	# using 2 per available processor cores - to handle
	# incoming requests using one and performing background
	# operations using the other.
	THREADS_PER_PAGE = 2

	# Enable protection agains *Cross-site Request Forgery (CSRF)*
	CSRF_ENABLED     = True

	# Use a secure, unique and absolutely secret key for
	# signing the data. 
	CSRF_SESSION_KEY = "secret"

	# Secret key for signing cookies
	SECRET_KEY = "secret"

	# Bycrpt cryptographic parameters
	BCRYPT_LOG_ROUNDS = 7

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://yannis:gim-333@localhost/db'

class TestingConfig(Config):
    TESTING = True
