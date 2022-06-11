from flask import Blueprint
from flask import current_app as app


admin_router = Blueprint('admin' ,__name__)

from . import views, payment