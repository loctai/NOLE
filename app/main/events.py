from flask import session
from flask_socketio import emit, join_room, leave_room
from app import socketio


@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    room = session.get('team')
    join_room(room)
    emit('status', {'msg': session.get('Your name') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('team')
    emit('message', {'msg': session.get('Your name') + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('team')
    leave_room(room)
    emit('status', {'msg': session.get('Your name') + ' has left the room.'}, room=room)