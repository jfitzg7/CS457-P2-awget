import os, sys
import copy
import json
import socket
import struct
import random
import tempfile
import threading


def handle_client(clientSocket, port):
    try:
        data = receiveUrlAndChainlist(clientSocket)

        recvdJson = json.loads(data)
        url = recvdJson[0]
        print("  Request: " + url)
        chainList = removeEntryFromChainList(recvdJson[1], socket.gethostname() + " " + str(port))
        chainList = removeEntryFromChainList(chainList, socket.gethostbyname(socket.gethostname()) + " " + str(port))
        if chainList:
            print("  chainlist is")
            for steppingStone in chainList:
                ss = steppingStone.split()
                print("  <" + ss[0] + ", " + ss[1] + ">")
            randIndex = generateRandomIndex(len(chainList)-1)
            nextSteppingStone = chainList[randIndex]
            ssInfo = nextSteppingStone.split()
            if len(ssInfo) != 2:
                print("Error: Incorrect stepping stone representation, " + str(ssInfo) + ", found in the provided chainlist")
                sys.exit()
            print("  next SS is " + "<" + ssInfo[0] + ", " + ssInfo[1] + ">")
            print("  waiting for file...")
            steppingStoneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            steppingStoneSocket.settimeout(10)

            steppingStoneSocket.connect((ssInfo[0], int(ssInfo[1])))

            sendUrlAndChainlist(steppingStoneSocket, url, chainList)

            fp = tempfile.NamedTemporaryFile(mode='ab+')

            data = steppingStoneSocket.recv(1024)
            fp.write(data)

            while data:
                data = steppingStoneSocket.recv(1024)
                fp.write(data)

            fp.seek(0) #this is needed to reset the read 'pointer' to the beginning of the file

            print("..\n  Relaying file ...")

            for data in readChunks(fp):
                clientSocket.send(data)
            fp.close()
            print("  Goodbye!\n")
            steppingStoneSocket.close()
        else:
            print("  chainlist is empty\n  issuing wget for file")
            fp = tempfile.NamedTemporaryFile(mode="ab+")
            os.system("wget -q " + "--output-document=" + fp.name + " " + url)
            print("..\n  File received\n  Relaying file ...")
            for data in readChunks(fp):
                clientSocket.send(data)
            fp.close()
            print("  Goodbye!\n")
        clientSocket.close()
    except IOError as e:
        print(e)
        sys.exit()


def receiveUrlAndChainlist(clientSocket):
    buf = b''
    while len(buf) < 4:
        recvd = clientSocket.recv(8)
        if not recvd:
            break
        else:
            buf += recvd

    length = 0
    try:
        length = struct.unpack('!I', buf[:4])[0]
    except struct.error as e:
        print("Error: " + str(e))
        sys.exit()

    clientSocket.send(struct.pack('!I', length)) #Send the length back as an acknowledgement before receiving again

    data = ''
    while len(data) < length:
        recvd = clientSocket.recv(1024)
        if not recvd:
            break
        else:
            data += recvd.decode()

    if len(data) != length:
        print("Error: something went wrong while receiving the url and chainlist, the lengths do not match!")
        sys.exit()
    return data


def sendUrlAndChainlist(steppingStoneSocket, url, chainList):
    urlAndChainlist = json.dumps([url, chainList]).encode()
    length = struct.pack("!I", len(urlAndChainlist))
    steppingStoneSocket.send(length)

    #Handle acknowledgement
    buf = b''
    while len(buf) < 4:
        recvd = steppingStoneSocket.recv(8)
        if not recvd:
            break
        else:
            buf += recvd

    ack = struct.unpack('!I', buf[:4])[0]

    if ack != len(urlAndChainlist):
        print("Protocol error: the length received in the ack does not match, the url and chainlist will not be sent!")
        sys.exit()

    steppingStoneSocket.send(urlAndChainlist)


def generateRandomIndex(length):
    random.seed()
    return random.randint(0, length)


def readChunks(file, chunkSize=1024):
    while True:
        data = file.read(chunkSize)
        if not data:
            break
        yield data


def removeEntryFromChainList(chainList, entry):
    newList = copy.deepcopy(chainList)
    try:
        newList.remove(entry)
    except ValueError as e:
        None
    return newList


def server(port):
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        serverSocket.bind((socket.gethostname(), port))
    except OSError as e:
        print("Error: " + str(e))
        sys.exit()
    serverSocket.listen(5)

    while True:
        (clientSocket, address) = serverSocket.accept()
        clientSocket.settimeout(10)

        clientThread = threading.Thread(target = handle_client, args = (clientSocket, port))
        clientThread.daemon = True
        clientThread.start()

    serverSocket.close()

if __name__ == "__main__":
    port = 8081 #default port number
    if len(sys.argv) > 2:
        print("Error: Incorrect number of arguments provided.")
    elif len(sys.argv) == 2:
        try:
            port = int(sys.argv[1])
            if (port < 1024 or port > 65535):
                print("Error: please enter a port number in the range of 1024-65535.")
                sys.exit()
        except ValueError:
            print("Error: please enter a base 10 integer port number (i.e. no alphabetic or special characters).")
            sys.exit()
    print("ss <" + socket.gethostbyname(socket.gethostname()) + ", " + str(port) + ">:")
    server(port)
