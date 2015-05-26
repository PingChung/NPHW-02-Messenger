import sys
import os
import socket
import pickle
from threading import Thread
from getpass import getpass
import NetworkConnector


BUF_SIZE = 32768
blacklist = []


def updateCheck(client_socket):
    msg = pickle.loads(client_socket.recv(BUF_SIZE))
    if msg == []:
        pass
    else:
        print(msg)


def regist(client_socket):
    while True:
        print('n')
        id = input("New ID: ")
        pw = getpass("Password: ")

        msg = 'regist ' + id + ' ' + pw
        client_socket.sendall(pickle.dumps(msg))

        if client_socket.recv(BUF_SIZE) == b"success":
            break
        else:
            print('regist error')

def login(client_socket):
    id = getpass(prompt="Login: ")
    if id == 'new':
        regist(client_socket)
        id = getpass(prompt="Login: ")
    pw = getpass(prompt="Password: ")
    msg = "exist " + id + ' ' + pw
    client_socket.sendall(pickle.dumps(msg))
    
    if client_socket.recv(BUF_SIZE) == b"success":
        updateCheck(client_socket)
        return (True, id)
    else:
        return (False, None)

def talkMode(client_socket, to_user):
    while True:
        msg = input()
        
        if msg == "exit":
            break
        else:
            msg = "send" + " " + to_user + " " + msg
            client_socket.sendall(pickle.dumps(msg))

def black(id):
    blacklist.append(id)

def unblack(id):
    blacklist.remove(id)


def handle_send(client_socket, id):
    while True:
        msg = input()
        msg_split = msg.split(' ')
        inst = msg_split[0]


        if inst == "talk" and len(msg_split) == 2:
            talkMode(client_socket, msg_split[1])

        elif inst == "logout" and len(msg_split) == 1:
            client_socket.sendall(pickle.dumps(msg))
            sys.exit()

        elif inst == "black" and len(msg_split) == 2:
            black(msg_split[1])
        elif inst == "unblack" and len(msg_split) == 2:
            unblack(msg_split[1])

        else:
            client_socket.sendall(pickle.dumps(msg))


def handle_recv(client_socket):
    while True:
        msg = pickle.loads(client_socket.recv(BUF_SIZE))

        if msg == 'logout':
            sys.exit()
        elif 'says' in msg or 'broadcasts' in msg:
            msgsplit = msg.split(' ', 1)
            user = msgsplit[0]
            if user in blacklist:
                pass
            else:
                print(msg)
        else:    
            print(msg)


def main():
    client_socket = NetworkConnector.client_init("127.0.0.1", 10067)
    
    (login_success, id) = login(client_socket)
    if login_success: 
        print("I'm {}".format(id))
        Thread(target=handle_recv, args=(client_socket, )).start()
        Thread(target=handle_send, args=(client_socket, id)).start()
    else:   
        print("You are under permission")

if __name__ == '__main__':
    main()