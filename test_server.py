import base64
import socket


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


sock.bind(('127.0.0.1', 8085))

sock.listen(1)

conn, addr = sock.accept()
print('connected')

var = ''
iters = 0
# while True:
#     result = base64.b64decode(conn.recv(1024)).decode('utf-8')
#     if result == '':
#         break
#     var += result
#     iters += 1

while True:
    temp = base64.b64decode(conn.recv(1024)).decode().strip('\n')
    if temp == '':
        break
    var += temp
    iters += 1

print(var)
print(iters)
