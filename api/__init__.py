from flask import Blueprint
_api = Blueprint('api', __name__, url_prefix='/api')

from wrmota.api import _api
