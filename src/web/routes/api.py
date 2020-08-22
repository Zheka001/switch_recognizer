# -*- coding: utf-8 -*-
from pathlib import Path

from flask import Blueprint
from flask_restful import Api, Resource, request

from src.ml.video_processor import VideoProcessor

api_bp = Blueprint('api', __name__)
api = Api(api_bp)


class VersionResource(Resource):
    @staticmethod
    def get():
        data_ = {'version': 0.1}
        return data_, 200


class VideoProcessingResource(Resource):
    def __init__(self, *args, **kwargs):
        super(VideoProcessingResource, self).__init__(*args, **kwargs)
        self._video_processor = VideoProcessor()

    # @login_required
    def post(self):
        path_to_file = Path(request.args.get('filename'))
        if not path_to_file.exists():
            return {'message': 'videofile does not exist'}, 404
        try:
            result = self._video_processor.run(path_to_file)
            return result, 200
        except Exception as e:
            return {'message': e}, 404


api.add_resource(VersionResource, '/version')
api.add_resource(VideoProcessingResource, '/api/1/video_processing')
