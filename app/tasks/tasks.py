from . import celery
from app import socketio
from app.main.investment import task_callback_invoice
@celery.task(name='task_deposit')
def task_deposit(response):
    print('eeeeeeeeeeeeeeeeee',response)
    # task_key = 'task-%s' %(response['task_id'])
    # task_identity = rsession.get(task_key).decode('utf-8')
    # session_key = 'session-%s' %(task_identity)
    # identity_socket = rsession.get(session_key)
    # if identity_socket:
    #     socketio.emit('emit_result', {'data':response}, room=identity_socket.decode('utf-8'))

@celery.task(name='task_invoice')
def task_deposit(response):
    task_callback_invoice(response)