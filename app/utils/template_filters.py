from datetime import datetime, date
import time
from . import helpers
def init_template_filters(app):
    @app.template_filter('uppercase')
    def uppercase(text):
        return text.upper()
        
    @app.template_filter("yes_no")
    def yesno_format(value):
        if value is None:
            return ""
        if value:
            return "Yes"
        else:
            return "No"

    @app.template_filter("datetime_format")
    def datetime_format(value):
        if value:
            return value.strftime("%m-%d-%Y %H:%M")
        else:
            return ""

    @app.template_filter("nbsp")
    def nbsp(value):
        if value:
            return value.replace(' ', '\xa0')
        else:
            return ""

    @app.template_filter("date_format")
    def date_format(value):
        if value is None:
            return ''
        return value.strftime("%b, %d %Y %H:%M")
    @app.template_filter("server_time")
    def server_time(t):
        time_ = time.strftime('%A %B, %d %Y %H:%M:%S')
        
        return time_
    @app.template_filter("blank_if_none")
    def blank_if_none(value):
        return value or ""

    @app.template_filter("default_if_none")
    def default_if_none(value, default):
        return value or default

    @app.template_filter("currency")
    def currency(value):
        if value:
            return "£{:.2f}".format(value)
        else:
            return ""

    @app.template_filter("separated_number")
    def currency(value):
        return F"{value:,}"

    @app.template_filter()
    def format_usd(value):
        return helpers.format_usd(value)
    @app.template_filter()
    def format_satoshi(value):
        value = round(float(value), 0)
        amount_coin = helpers.format_satoshi(value)
        return round(float(amount_coin),4)

    @app.context_processor
    def inject_now():
        return {'current_year': datetime.utcnow().strftime("%Y")}
    @app.template_filter()
    def replace_address(s):
        sequence = '...'
        indicies = (5,len(s)-5)
        return sequence.join([s[:indicies[0]-1], s[indicies[1]:]])