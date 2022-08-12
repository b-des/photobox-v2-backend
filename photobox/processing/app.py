import logging
import os
from logging.handlers import TimedRotatingFileHandler

from flask_cors import CORS
from photobox import api

from flask import Flask

from photobox import config

# set up logger
isExist = os.path.exists(config.LOG_DIR)
if not isExist:
    os.makedirs(config.LOG_DIR)

handler = TimedRotatingFileHandler(config.LOG_FILE,
                                   when="midnight",
                                   backupCount=5)
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s]: {} %(levelname)s %(message)s'.format(os.getpid()),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    handlers=[handler, logging.StreamHandler()])

logger = logging.getLogger()

logger.info(f'Starting app in {config.APP_ENV} environment')
logger.info(f"DOMAINS_DICT_FILE: {config.DOMAINS_DICT_FILE}")


# set up flask
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# register flask restfull endpoints
api.render.register(app)
api.health.register(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4567)
