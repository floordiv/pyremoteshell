import base64
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


print('connecting')
sock.connect(('127.0.0.1', 8085))
print('connected\nsending...', end=' ')


# with open('server.py', 'r') as file:
#     sock.send(file.read().encode('utf-8'))
sock.send(base64.b64encode('hello wrld'.encode('utf-8')))

print('done')
