import os
import sys


APP_ENV = os.environ.get('APP_ENV', 'development')
API_PREFIX = "/api"
HEALTH_PREFIX = "/health"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = "logs" if APP_ENV == "development" else "/tmp/photobox/logs"
LOG_FILE = f"{LOG_DIR}/log.txt"
DOMAINS_DICT_FILE = os.environ.get('DOMAINS_DICT_PATH', "domains.json")

class BaseConfig:
    API_PREFIX = '/api'
    TESTING = False
    DEBUG = False


class DevConfig(BaseConfig):
    FLASK_ENV = 'development'
    DEBUG = True


class ProductionConfig(BaseConfig):
    FLASK_ENV = 'production'


class TestConfig(BaseConfig):
    FLASK_ENV = 'development'
    TESTING = True
    DEBUG = True
    # make celery execute tasks synchronously in the same process
    CELERY_ALWAYS_EAGER = True
