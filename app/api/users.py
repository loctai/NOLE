from flask import jsonify, request, url_for, g, abort
from app.api import bp


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify({'user':'werwre'})