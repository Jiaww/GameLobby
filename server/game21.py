import threading
import random
import time
from utilities import *


class Game21(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.rnum = []

    # initialize the game state
    def init_game(self):
        # flush the data of last game in Server cache
        ServerCache.game_start = True
        ServerCache.answers_dict = {}
        ServerCache.game_nums = []
        # generate 4 random integer between 1:10
        self.rnum = []
        for i in range(4):
            self.rnum.append(random.randint(1, 10))
        ServerCache.game_nums = self.rnum

        # broadcast the 'Game start' message to all the users
        print "21 Game Start!: the 4 numbers are %d %d %d %d " % (self.rnum[0], self.rnum[1], self.rnum[2], self.rnum[3])
        time.sleep(0.1)
        broadcast_msg(ServerCache.login_dict.keys(), "21 Game Start!: the 4 numbers are %d %d %d %d \n Join the room and Hurry up !!" % (self.rnum[0], self.rnum[1], self.rnum[2], self.rnum[3]))

    # end the game and get the final winner
    def end_game(self):
        winner = ""
        winner_time = 100
        winner_answer = 0
        max_num = 0
        got_21 = False
        # iterate through all the (answer, answer_time) pair stored in server cache
        for user in ServerCache.answers_dict.keys():
            answer, answer_time = ServerCache.answers_dict[user]
            # check if the answer is 21
            if answer == 21:
                # if already got a 21 point
                if got_21:
                    # compare answer time
                    if answer_time < winner_time:
                        winner = user
                        winner_time = answer_time
                        winner_answer = answer
                else:
                    winner = user
                    winner_time = answer_time
                    winner_answer = answer
                    got_21 = True
            elif answer < 21:
                # if already got a 21 point
                if got_21:
                    pass
                else:
                    # compare with max number
                    if answer > max_num:
                        winner = user
                        winner_time = answer_time
                        winner_answer = answer
                        max_num = answer
                    elif answer == max_num:
                        # compare answer time
                        if answer_time < winner_time:
                            winner = user
                            winner_time = answer_time
                            winner_answer = answer

        if winner:
            for room in ServerCache.room_dict.keys():
                time.sleep(0.1)
                broadcast_msg(ServerCache.room_dict[room], "The winner is %s, the answer equals: %d" % (winner, winner_answer))
            print "The winner is %s, the answer equals: %d" % (winner, winner_answer)
        else:
            for room in ServerCache.room_dict.keys():
                time.sleep(0.1)
                broadcast_msg(ServerCache.room_dict[room], "No winner this time, good luck next round")
            print "No winner this time"
        ServerCache.game_start = False

    def run(self):
        while True:
            try:
                if time.localtime(time.time()).tm_sec == 0:
                    self.init_game()
                    time.sleep(GAME_LENGTH)
                    self.end_game()
            except:
                pass