import json
import logging

from flask import jsonify, request
from flask_restful import Api, Resource
from photobox import config
from photobox.processing.Render import Render
from photobox.models.ImagePayload import ImagePayload
from photobox.utils import utils
import threading

logger = logging.getLogger()
domains_dict = utils.load_domains_dict()


def process_images(image_payload, image_path):
    Render(image_payload, image_path).start()


class ColorEnhanceAPI(Resource):
    def post(self):
        try:
            image_path, host = utils.get_image_path_from_request(request, domains_dict)
        except Exception as e:
            logger.error(f"Can't get image path from request domain. Error: {e}")
            return {"message": str(e)}, 400
        json_data = request.get_json(force=True)
        image_url = json_data['url']
        logger.info(f"Got request for enhancing color, url: {image_url}, host: {host}")
        try:
            res = Render.enhance_color(image_path, image_url)
            logger.error(f"Image color has been adjusted successfully, original url: {image_url}, final url: {res}")
            return jsonify({"url": res})
        except Exception as e:
            logger.error(f"Exception during enhancing color: {e}")
            return {"message": str(e)}, 400


class PhotoProcessingAPI(Resource):
    def post(self):
        try:
            image_path, host = utils.get_image_path_from_request(request, domains_dict)
        except Exception as e:
            logger.error(f"Can't get path from requested domain. Error: {e}")
            return {"message": str(e)}, 400
        json_data = request.get_json(force=True)
        image_payload: [ImagePayload] = ImagePayload.schema().loads(json.dumps(json_data), many=True)
        logger.info(f"Got request for render images, quantity: {len(image_payload)}, host: {host}")
        #try:
            #Render(image_payload, image_path).start()
        logger.info(f"The job has been scheduled, images are processing in the background")
        thread = threading.Thread(target=process_images, args=[image_payload, image_path])
        thread.daemon = True
        thread.start()
        #except Exception as e:
            #logger.error(f"Exception during rendering images: {e}")
            #return {"message": "Can't finish rendering, the error occurred on server side"}, 400
        return json_data, 200


def register(app):
    api = Api(app, prefix=config.API_PREFIX)
    # photo processing endpoint
    api.add_resource(PhotoProcessingAPI, '/render')

    # task status endpoint
    api.add_resource(ColorEnhanceAPI, '/enhance-color')

