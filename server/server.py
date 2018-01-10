import socket
import select
from activeClient import *
from utilities import *
from game21 import Game21

class Server:
    def __init__(self, host=HOST, port=PORT):
        self.listen_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_skt.setblocking(0)
        self.listen_skt.bind((host, port))
        self.listen_skt.listen(5)

        self.receive_size = RECEIVE_SIZE
        print "Server start at: %s:%s" %(host, port)
        print "Waiting for connections..."
        # Game Object
        self.game = Game21()
        self.game.setDaemon(True)
        self.game.start()

        self.skts = []
        self.skts.append(self.listen_skt)
        # loading users data from file
        load_users_data()
        ServerCache.server = self

    def add_client(self, skt, addr):
        # Add active client
        skt.setblocking(0) # Non-blocking
        self.skts.append(skt)
        # Assign proxy for the activated client
        client = ActiveClient(skt, addr)
        ServerCache.act_client_dict[skt] = client

    def delete_client(self, skt, addr):
        # Delete non-active client
        try:
            skt.close()
        except:
            pass
        self.skts.remove(skt)
        client = ServerCache.act_client_dict[skt]
        user_name = client.user_name
        temp_addr = client.addr
        if user_name:
            ServerCache.login_dict.pop(user_name)
            ServerCache.users_db[user_name][1] += round(time.time() - client.start_time)
            save_users_data()
            time.sleep(0.1)
            broadcast_msg(ServerCache.login_dict.keys(), '%s log out' % user_name)
        ServerCache.act_client_dict.pop(skt, None)
        print "Client (%s:%s) disconnected" % temp_addr

    def run(self):
        while True:
            try:
                readable, writable, exceptional = select.select(self.skts, [], [])
                for r in readable:
                    if r == self.listen_skt:
                        # new connection
                        skt, addr = self.listen_skt.accept()
                        self.add_client(skt, addr)
                        print "Client (%s:%s) connected" % addr
                    else:
                        # receive data
                        end = ServerCache.act_client_dict[r].process_msg()
                        # when no longer receive, delete client
                        if not end:
                            self.delete_client(r, ServerCache.act_client_dict[r].addr)
            except:
                pass


if __name__ == "__main__":
    server = Server()
    server.run()


