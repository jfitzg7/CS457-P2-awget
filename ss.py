import os, sys
import copy
import json
import socket
import random
import tempfile
import threading


def handle_client(clientSocket, port):
    try:
        data = clientSocket.recv(4096).decode()
        recvdJson = json.loads(data)
        url = recvdJson[0]
        chainList = removeEntryFromChainList(recvdJson[1], socket.gethostname() + " " + str(port))
        chainList = removeEntryFromChainList(chainList, socket.gethostbyname(socket.gethostname()) + " " + str(port))
        if chainList:
            randIndex = generateRandomIndex(len(chainList)-1)
            nextSteppingStone = chainList[randIndex]
            ssInfo = nextSteppingStone.split()
            if len(ssInfo) != 2:
                print("Error: Incorrect stepping stone representation, " + str(ssInfo) + ", found in the provided chainlist")
                sys.exit()

            steppingStoneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            steppingStoneSocket.connect((ssInfo[0], int(ssInfo[1]))

            steppingStoneSocket.send(json.dumps([url, chainList]).encode())
            fp = tempfile.NamedTemporaryFile(mode='ab+')

            data = steppingStoneSocket.recv(1024)
            fp.write(data)

            while data:
                data = steppingStoneSocket.recv(1024)
                fp.write(data)

            fp.seek(0) #this is needed to reset the read 'pointer' to the beginning of the file

            for data in readChunks(fp):
                clientSocket.send(data)
            fp.close()
            steppingStoneSocket.close()
        else:
            fp = tempfile.NamedTemporaryFile(mode="ab+")
            os.system("wget " + "--output-document=" + fp.name + " " + url)
            for data in readChunks(fp):
                clientSocket.send(data)
            fp.close()
        clientSocket.close()
    except IOError as e:
        print(e)
        sys.exit()


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
    serverSocket.bind((socket.gethostname(), port))
    serverSocket.listen(5)

    while True:
        (clientSocket, address) = serverSocket.accept()
        clientSocket.settimeout(1)

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
