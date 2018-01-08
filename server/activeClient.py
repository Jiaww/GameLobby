import sys
import time
from utilities import *


# Store all the info and process all the message of the client who log in
class ActiveClient:
    def __init__(self, skt, addr):
        self.skt = skt
        self.addr = addr
        self.is_log_in = False
        self.header = ""
        self.content = ""
        self.user_name = ""
        self.start_time = 0
        self.history_time = 0
        self.room_name = ""

    def process_msg(self):
        try:
            data = self.skt.recv(RECEIVE_SIZE)
            if data:
                d = unpack(data)
                header = d['header']
                content = d['content']
                # check if log in
                if header not in ["help", "register", "log_in", "quit"] and not self.is_log_in:
                    self.skt.send(enpack("please log in first!"))
                    self.content = ""
                    return True
                # help menu
                if header == "help":
                    help_content = get_help_menu()
                    self.skt.send(enpack(help_content))
                # register
                elif header == "register":
                    # split content into username pwd pwd
                    temp = content.strip().split(' ')
                    if self.user_name:
                        self.skt.send(enpack("you have to log out first"))
                    elif len(temp) != 3:
                        self.skt.send(enpack("%d params, Invalid number of params, expected 3 params: username password password" % len(temp)))
                    else:
                        username, password, repassword = temp
                        if password != repassword:
                            self.skt.send(enpack("password and repassword are not match!"))
                        else:
                            ServerData.users_db[username] = (password, 0)
                            self.skt.send(enpack("create account successfully!"))
                            save_users_data()
                # log in
                elif header == "log_in":
                    temp = content.strip().split(' ')
                    if self.user_name:
                        self.skt.send(enpack("you have to log out first"))
                    elif len(temp) != 2:
                        self.skt.send(enpack("%d params, Invalid number of params, expected 2 params: username password" % len(temp)))
                    else:
                        username, password = temp
                        if username in ServerData.users_db.keys():
                            if password == ServerData.users_db[username][0]:
                                if username in ServerData.login_dict.keys():
                                    temp_skt = ServerData.login_dict[username]
                                    temp_addr = ServerData.act_client_dict[temp_skt].addr
                                    temp_skt.send(enpack("you kick by (%s, %s)" % self.addr))
                                    ServerData.server.delete_client(temp_skt, temp_addr)
                                    ServerData.act_client_dict[self.skt] = self
                                ServerData.login_dict[username] = self.skt
                                self.user_name = username
                                self.start_time = time.time()
                                self.history_time = ServerData.users_db[username][1]
                                self.skt.send(enpack("login successfully"))
                                self.is_log_in = True
                                # broadcast
                                time.sleep(1.0)
                                broadcast_msg(ServerData.login_dict.keys(), "[%s] log in" % self.user_name)
                            else:
                                self.skt.send(enpack("password is incorrect"))
                        else:
                            self.skt.send(enpack("account doesn't exist"))
                # chat all
                elif header == "chat_all":
                    broadcast_msg(ServerData.login_dict.keys(), "(Lobby Message)[%s]: %s" %(self.user_name, content))
                # online time
                elif header == "online_time":
                    current_online_time = time.time() - self.start_time
                    self.skt.send(enpack("current online time: %s, total online time: %s" % (get_time_str(current_online_time), get_time_str(self.history_time + current_online_time))))
                # log out
                elif header == "log_out":
                    if self.is_log_in:
                        if self.room_name:
                            roomname = self.room_name
                            ServerData.room_dict[roomname].remove(self.user_name)
                            # if the room has no user
                            if len(ServerData.room_dict[roomname]) == 0:
                                ServerData.room_dict.pop(roomname)
                                time.sleep(0.1)
                                broadcast_msg(ServerData.login_dict.keys(), "Room '%s' has been removed" % roomname)
                            self.room_name = ""
                        broadcast_msg(ServerData.login_dict.keys(), "[%s] log out" % self.user_name)
                        ServerData.login_dict.pop(self.user_name, None)
                        ServerData.users_db[self.user_name][1] += round(time.time() - self.start_time)
                        save_users_data()
                        self.user_name = ""
                        self.start_time = 0
                        self.history_time = 0
                        self.is_log_in = False
                    else:
                        self.skt.send(enpack("you have to log in first"))
                # quit client
                elif header == "quit":
                    if self.is_log_in:
                        if self.room_name:
                            roomname = self.room_name
                            ServerData.room_dict[roomname].remove(self.user_name)
                            # if the room has no user
                            if len(ServerData.room_dict[roomname]) == 0:
                                ServerData.room_dict.pop(roomname)
                                time.sleep(0.1)
                                broadcast_msg(ServerData.login_dict.keys(), "Room '%s' has been removed" % roomname)
                            self.room_name = ""
                        broadcast_msg(ServerData.login_dict.keys(), "[%s] log out" % self.user_name)
                        ServerData.login_dict.pop(self.user_name, None)
                        self.user_name = ""
                        self.start_time = 0
                        self.history_time = 0
                    self.skt.send(enpack("quit succesfully"))
                    ServerData.server.delete_client(self.skt, self.addr)
                    sys.exit(1)
                # create room
                elif header == "create_room":
                    temp = content.strip().split(' ')
                    if self.room_name:
                        self.skt.send(enpack("you are already in a room, please exit to the lobby and then create a new room"))
                    elif len(temp) > 1:
                        self.skt.send(enpack("please do not add spaces in room's name "))
                    else:
                        roomname = temp[0]
                        if roomname in ServerData.room_dict.keys():
                            self.skt.send(enpack("the name has been used, please try another name for your room"))
                        else:
                            user_lst = []
                            user_lst.append(self.user_name)
                            ServerData.room_dict[roomname] = user_lst
                            self.room_name = roomname
                            self.skt.send(enpack("Your room '%s' is created successfully" % roomname))
                            time.sleep(0.1)
                            broadcast_msg(ServerData.login_dict.keys(), "Room '%s' has been created" % roomname)
                            # broadcast Room
                            time.sleep(0.1)
                            broadcast_msg(user_lst, "[%s] join the room" % self.user_name)
                # join room
                elif header == "join_room":
                    temp = content.strip().split(' ')
                    if self.room_name:
                        self.skt.send(enpack("you are already in a room, please exit to the lobby and then join another room"))
                    elif len(temp) > 1:
                        self.skt.send(enpack("please do not add spaces in room's name "))
                    else:
                        roomname = temp[0]
                        if roomname in ServerData.room_dict.keys():
                            ServerData.room_dict[roomname].append(self.user_name)
                            self.room_name = roomname
                            # broadcast Room
                            time.sleep(0.1)
                            broadcast_msg(ServerData.room_dict[roomname], "[%s] join the room" % self.user_name)
                        else:
                            self.skt.send(enpack("there is no room named %s" % roomname))
                # exit room
                elif header == "exit_room":
                    roomname = self.room_name
                    time.sleep(0.1)
                    broadcast_msg(ServerData.room_dict[roomname], "[%s] exit the room" % self.user_name)
                    ServerData.room_dict[roomname].remove(self.user_name)
                    # if the room has no user
                    if len(ServerData.room_dict[roomname]) == 0:
                        ServerData.room_dict.pop(roomname)
                        time.sleep(0.1)
                        broadcast_msg(ServerData.login_dict.keys(), "Room '%s' has been removed" % roomname)
                    self.room_name = ""
                # get users name in the lobby
                elif header == "get_lobby_user_list":
                    self.skt.send(enpack("The user-list in lobby: " + str(ServerData.login_dict.keys())))
                # get room list
                elif header == "get_room_list":
                    self.skt.send(enpack("The room-list: " + str(ServerData.room_dict.keys())))
                # get users name in the room
                elif header == "get_room_user_list":
                    if self.room_name:
                        self.skt.send(enpack("The user-list in room: " + str(ServerData.room_dict[self.room_name])))
                    else:
                        self.skt.send(enpack("you are not in a room"))
                # chat with users in the room
                elif header == "chat_room":
                    roomname = self.room_name
                    if roomname:
                        time.sleep(0.1)
                        broadcast_msg(ServerData.room_dict[roomname], "(Room Message)[%s]: %s" %(self.user_name, content))
                    else:
                        self.skt.send(enpack("you are not in a room"))
                # chat with the user with name xxx
                elif header == "chat_private":
                    temp = content.strip().split(' ', 1)
                    if len(temp) != 2:
                        self.skt.send(enpack("expected following format: chat_private target_name message"))
                    else:
                        target_name, msg = temp
                        # check if exist
                        if target_name not in ServerData.users_db.keys():
                            self.skt.send(enpack("the target user does not exist"))
                        else:
                            # check if online
                            if target_name not in ServerData.login_dict.keys():
                                self.skt.send(enpack("the target user is not online right now"))
                            else:
                                ServerData.login_dict[target_name].send(enpack("(Private Message)[%s]: %s" % (self.user_name, msg)))
                                self.skt.send(enpack("(Private Message)[%s]: %s" % (self.user_name, msg)))
                else:
                    self.skt.send(enpack("Invalid Input Command"))
                    return False
                return True
            else:
                return False
        except:
            return True
