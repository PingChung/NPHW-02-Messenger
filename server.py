import sys
import socket
import pickle
import logging
from threading import Thread
import NetworkConnector


BUF_SIZE = 32768
server_addr = ("127.0.0.1", 10067)
accounts = {"Alice": "123", "Bob": "abc", "canny": "ccc"}
offline_msg={'Alice':[], 'Bob':[], 'canny':[]}
hidelist = ["None"]
online_user_connections = {}


def listuser(connection):
    users = []

    for i in online_user_connections:
        if i in hidelist:
            pass
        else:
            users.append(i)
    
    connection.sendall(pickle.dumps(users))

def sendmsg(connection, from_user, to_user, msg):
    msg = from_user + " says: " + msg
    
    if to_user in online_user_connections:
        online_user_connections[to_user].sendall(pickle.dumps(msg))
    else:
        offline_msg[to_user].append(msg)


def broadcast(connection, from_user, msg):
    msg = from_user + " broadcasts: " + msg

    for user in accounts:
        if user in online_user_connections:
            online_user_connections[user].sendall(pickle.dumps(msg))
        else:
            offline_msg[user].append(msg)


def updateCheck(connection, id):
    if id in offline_msg:
        connection.sendall(pickle.dumps(offline_msg[id]))


def loginCheck(connection, id ,pw):
    if id in accounts and accounts[id] == pw:
        print('{} login success'.format(id))
        connection.sendall(b"success")
        online_user_connections[id] = connection
        updateCheck(connection, id)
        return id
    else :
        print("{} login fail!".format(id))
        connection.sendall(b"fail")
        connection.close()

def regist(connection, id, pw):
    if id in accounts:
        connection.sendall(b'unsuccess')
    else:
        connection.sendall(b"success")
        accounts.update({id: pw})
        offline_msg.update({id: []})


def hide(id):
    hidelist.append(id)

def unhide(id):
    hidelist.remove(id)

def logout(connection, id):
    connection.sendall(pickle.dumps("logout"))
    online_user_connections.pop(id)


def handle_request(connection):
    #login_success = False
    #(login_success, id) = loginCheck(connection)
    id = ''

    while True:
        msg = pickle.loads(connection.recv(BUF_SIZE))
        split = msg.split(' ', 2)
        msglen = len(split)
        inst = split[0].lower()
            
        if inst == 'exist' and msglen == 3:
            id = loginCheck(connection, split[1], split[2])
        elif inst == 'regist' and msglen == 3:
            regist(connection, split[1], split[2])
        elif inst == "list":
            listuser(connection)
        elif inst == "send" and msglen == 3:
            sendmsg(connection, id, split[1], split[2])
        elif inst == "broadcast" and msglen == 2:
            broadcast(connection, id, split[1])
        elif inst == "logout" and msglen == 1:
            logout(connection, id)
        elif inst == "hide":
            hide(id)
        elif inst == "unhide":
            unhide(id)
        else:
            connection.sendall(pickle.dumps("Message Error!"))
            print("Message Error!")


def handle_conversation(connection, address):
    try:
        while True:
            handle_request(connection)
    except EOFError:
        print('Client socket to {} has closed'.format(address))
    except Exception as e:
        print('Client {} error: {}'.format(address, e))
    finally:
        connection.close()


def accept_connections(server_socket):
    while True:
        connection, address = server_socket.accept()
        print("Accept connection: {}".format(address))
        Thread(target=handle_conversation, args=(connection, address)).start()


def main():
    server_socket = NetworkConnector.server_init(server_addr)
    accept_connections(server_socket)


if __name__ == '__main__':
    main()

