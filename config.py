import os

class Config(object):
    # Statement for enabling the development environment
    DEBUG = True
    TESTING = False

    # Define the application directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

    # Define the database - we are working with
    # SQLite for this example
    SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(BASE_DIR, 'app.db')
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
    CSRF_SESSION_KEY = "secret" # os.environ['PURVIEW_CSRF_SESSION_KEY']

    # Secret key for signing cookies
    SECRET_KEY = "secret" # os.environ['PURVIEW_SECRET_KEY']
    SECURITY_PASSWORD_SALT = 'my_precious_two' # os.environ['PURVIEW_SECURITY_PASSWORD_SALT']

    # Bcyrpt cryptographic parameters
    BCRYPT_LOG_ROUNDS = 7

    # Minimum password length
    MIN_PASS_LEN = 6

    # main config
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = 'gim04172017@gmail.com' # os.environ['PURVIEW_MAIL_USERNAME']
    MAIL_PASSWORD = 'gordon_ioannis_matthew-333' # os.environ['PURVIEW_MAIL_PASSWORD']

    # mail accounts
    MAIL_DEFAULT_SENDER = 'gim04172017@gmail.com'

# class ProductionConfig(Config):
#     DEBUG = False
#     SQLALCHEMY_DATABASE_URI = os.environ['PURVIEW_MYSQL_URI']
#     CSRF_SESSION_KEY = os.environ['PURVIEW_CSRF_SESSION_KEY']
#     SECRET_KEY = os.environ['PURVIEW_SECRET_KEY']

class TestingConfig(Config):
    # enable testing to block emailing during unit testing
    TESTING = True
    
