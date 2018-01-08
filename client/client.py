import select
import socket
import threading
from utilities import *

reload(sys)
sys.setdefaultencoding("utf-8")


class Client(threading.Thread):
    def __init__(self, host, port):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.login_name = ""
        self.user_name = 'offline'
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.skt.connect((host, port))
        except:
            print "Unable to connect (%s: %s)" % (host, port)
            sys.exit()

    def run(self):
        while True:
            user_name_tag(self.user_name)
            connect_list = [sys.stdin, self.skt]
            readable, writable, exceptionals = select.select(connect_list, [], [])
            for r in readable:
                # client socket
                if r == self.skt:
                    data = r.recv(RECEIVE_SIZE)
                    if data:
                        d = unpack(data)
                        print "\n >>> " + d['content'] + " <<< "
                        if d['content'] == "login successfully":
                            self.user_name = self.login_name
                        if d['content'] == "[%s] log out" % self.user_name:
                            self.user_name = "offline"
                        if d['content'] == "quit succesfully":
                            print "disconnected"
                            sys.exit(1)
                    else:
                        print "disconnected"
                        sys.exit(1)
                # sys std input
                else:
                    line = sys.stdin.readline().replace('\n', '')
                    header, content = read_command(line)
                    if header == -1:
                        print "Invalid command, input 'help' for more information"
                        continue
                    elif header == "log_in":
                        self.login_name = content.split(' ')[0]
                    self.skt.send(enpack(content=content, code=header))


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.run()
