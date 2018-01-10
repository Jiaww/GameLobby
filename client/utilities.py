import sys
import json

# Config Values
HOST = "127.0.0.1"
PORT = 8888
RECEIVE_SIZE = 1024


def user_name_tag(username):
    sys.stdout.write("<" + username + "> ")
    sys.stdout.flush()


def unpack(s):
    return json.loads(s)


def enpack(content, code='msg'):
    return json.dumps({'header': code, 'content': content})


def read_command(line):
    command = line.split(' ', 1)
    if len(command) == 1:
        if command[0] in ["help", "log_out", "quit", "online_time", "get_lobby_user_list", "get_room_user_list", "get_room_list", "exit_room"]:
            return command[0], 0
        else:
            return -1, 0
    elif len(command) == 2:
        header, content = command
        if header not in ["register", "log_in", "chat_all", "create_room", "join_room", "chat_room", "chat_private", "21game"]:
            return -1, 0
        return header, content

