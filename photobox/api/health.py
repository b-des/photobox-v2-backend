from flask_restful import Api, Resource

from photobox import config


class HealthStatus(Resource):
    def get(self):
        json_data = {
            "ready": True
        }
        return json_data, 200


def register(app):
    api = Api(app, prefix=config.HEALTH_PREFIX)
    api.add_resource(HealthStatus, '/status')
