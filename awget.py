import os, sys
import argparse
import random
import socket
import json

py3 = sys.version_info[0] >= 3
if py3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


def sendAnonymousWget(url, steppingStones):

    a = urlparse(url)
    print("scheme: " + a.scheme)
    print(a.path)
    print(os.path.basename(a.path))

    random.seed()
    steppingStones = trimWhiteSpaceFromStones(steppingStones)
    randIndex = random.randint(0, len(steppingStones)-1)
    steppingStone = steppingStones[randIndex]
    ssInfo = steppingStone.split()
    if len(ssInfo) != 2:
        print("Error: Incorrect stepping stone representation, " + str(ssInfo) + ", found in the provided chainlist")
        exit()

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect((ssInfo[0], int(ssInfo[1])))

    clientSocket.send(json.dumps([url, steppingStones]).encode())

    data = clientSocket.recv(1024)
    recvd = data

    while data:
        data = clientSocket.recv(1024)
        recvd += data

    clientSocket.close()
    print(recvd)


def trimWhiteSpaceFromStones(steppingStones):
    trimmedStones = []
    for stone in steppingStones:
        trimmedStones.append(stone.strip())
    return trimmedStones


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anonymous wget")
    parser.add_argument("url")
    parser.add_argument("-c", nargs="?", const="chaingang.txt", default="chaingang.txt", metavar="chainfile")
    args = parser.parse_args()

    url = args.url
    chainFile = args.c

    try:
        with open(chainFile) as f:
            try:
                chainSize = int(f.readline())
                steppingStones = f.readlines()
                if len(steppingStones) != chainSize:
                    print("Error: the amount of stepping stones listed does not match the specified size")
                    exit()
            except Exception as e:
                print("Error: problem occurred while reading '" + chainFile + "'")
                exit()
    except Exception as e:
        print("Error: could not open '" + chainFile + "'")
        exit()

    sendAnonymousWget(url, steppingStones)
