# --------
import os
from flask_login import UserMixin
from flask import current_app

class User( UserMixin):
    def __init__(self, user_json):
        self.user_json = user_json

    def get_id(self):
        _id = self.user_json.get('_id')
        return str(_id)


 

        
  



