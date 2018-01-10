import json


# Server Data: Store all info and data when server is running
class ServerCache:
    server = None
    users_db = {} # username : (password, onlinetime)
    login_dict = {} # username : socket
    act_client_dict = {} # socket : active_client
    room_dict = {} # roomname : [user1, user2, user3]
    # Game
    game_start = False
    game_nums = []
    answers_dict = {} # username : (answer, answer_time)


# Config Values
RECEIVE_SIZE = 1024
HOST = "127.0.0.1" # localhost
PORT = 8888
GAME_LENGTH = 40

# DB utilities
def load_users_data():
    with open('users_data.db', 'r') as f:
        try:
            ServerCache.users_db = json.load(f)
        except:
            pass
    f.close()


def save_users_data():
    with open('users_data.db', 'w') as f:
        json.dump(ServerCache.users_db, f)
    f.close()


# Message packing utilities
def unpack(s):
    return json.loads(s)


def enpack(content, code='msg'):
    return json.dumps({'header': code, 'content': content})


# other utilities
def get_time_str(t):
    m, s = divmod(round(t), 60)
    h, m = divmod(m, 60)
    return "%d h %d m %d s " % (h, m, s)


def broadcast_msg(user_lst, msg):
    for user in user_lst:
        temp_skt = ServerCache.login_dict[user]
        temp_skt.send(enpack(msg))


def get_help_menu():
    s = "\n" \
        "1.  [ help ] : get help of the command \n" \
        "2.  [ register username password password ] : register a new account for the game lobby \n" \
        "3.  [ log_in username password ] : log in with an exist account \n" \
        "4.  [ chat_all message ] : chat with all of the users in the lobby\n" \
        "5.  [ online_time ] : get current online time and total online time of the account\n" \
        "6.  [ log_out ] : log out the account but not close the client\n" \
        "7.  [ quit ]: log out the account and close the client \n" \
        "8.  [ create_room roomname ] : create a game room \n" \
        "9.  [ join_room roomname ] : join a game room \n" \
        "10. [ exit_room ] : exit a game room \n" \
        "11. [ get_lobby_user_list ] : get all usernames in the lobby(All active users) \n" \
        "12. [ get_room_list ] : get all roomname list \n" \
        "13. [ get_room_user_list ] : get all usernames in the room \n" \
        "14. [ chat_room message ] : chat with the users in the room \n" \
        "15. [ 21game expression ] : play 21 game\n"
    return s
