from app import app, socketio, start_runner
import os
from gevent.pywsgi import WSGIServer
if __name__ == '__main__':
    socketio.run(
        app, 
        host=os.environ.get('IP', '0.0.0.0'),
        port=os.environ.get('PORT', '5889'),
        debug=True
    )
    # start_runner()
    # app.run(host=os.environ.get('IP', '0.0.0.0'),
    #         port=os.environ.get('PORT', '5000'),
    #         debug=True)