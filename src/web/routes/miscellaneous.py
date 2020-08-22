# -*- coding: utf-8 -*-
from flask import Blueprint, make_response

misc_bp = Blueprint('miscellaneous', __name__)


@misc_bp.errorhandler(404)
def not_found():
    """Serve 404 template."""
    return make_response("Page not found!", 404)
