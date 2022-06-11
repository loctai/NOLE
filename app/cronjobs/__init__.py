from flask import Blueprint

bp = Blueprint('cron', __name__)

from app.cronjobs import profit_daily, tickers, binary_bonus, auto_trade, auto_mail