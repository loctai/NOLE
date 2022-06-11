from flask import Blueprint
from flask import current_app as app


main = Blueprint('main' ,__name__)

from . import views , dashboard, wallet, investment, referral, account, transaction