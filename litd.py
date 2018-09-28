import json
import os
import operator
import socket
import threading

import commands as np

MAX_CONNECTIONS = 5
socket_path = '/tmp/litd'
queries = {}

def setup():
    queries.update({
        'effects': effects(),
        'colors': colors(),
        'sections': sections(),
        'zones': zones(),
        'speeds': speeds(),
        'sections': sections(),
        'error': error('not a valid query')
    })

def start():
    running = True
    serv = socket.socket(socket.AF_UNIX)
    try:
        os.remove(socket_path)
    except OSError:
        pass
    try:
        # Allow created socket to have non-root read and write permissions
        os.umask(0o1)
        serv.bind(socket_path)
        serv.listen(MAX_CONNECTIONS)
        while running:
           conn, address = serv.accept()
           start_conn_thread(conn)
    except Exception as e:
        print('litd socket error: {}'.format(e))

def start_conn_thread(conn):
    def listener():
        while True:
            try:
                data = conn.recv(4096)
                if not data: break
                resp = handle_command(data.decode()).encode()
                # First 32 bytes is message length
                conn.send(str(len(resp)).zfill(32).encode())
                conn.send(resp)
            except Exception as e:
                print('litd connection error: {}'.format(e))

    thread = threading.Thread(target=listener)
    thread.start()

def handle_command(data):
    msg = json.loads(data)
    type_error = error('type must be specified as "command" or "query"')
    if not 'type' in msg:
        return type_error
    msg_type = msg['type']
    print('processing {}'.format(msg))
    if msg_type == 'command':
        return command(msg)
    elif msg_type == 'query':
        return query(msg)
    else:
        return type_error

def error(msg):
    return json.dumps({'rc': 1, 'result': 'ERROR: {}'.format(msg)})

def result(data):
    data['rc'] = 0
    return json.dumps(data)

def command(msg):
    if 'args' in msg:
        ret, status = np.start(msg['effect'], **msg['args'])
    else:
        ret, status = np.start(msg['effect'])
    return json.dumps({'result': ret, 'rc': status})

def query(msg):
    return queries[msg.get('query', 'error')]

def effects():
    return result({'effects': sorted(np.get_effects(), key=operator.itemgetter('name'))})

def colors():
    return result({'colors': np.get_colors()})

def sections():
    return result({'sections': list(np.get_sections())})

def zones():
    return result({'zones': list(np.get_zones())})

def speeds():
    return result({'rc': 0, 'speeds': np.get_speeds()})

if __name__ == '__main__':
    setup()
    start()