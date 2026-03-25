'''
This is a socket client for sending messages to a higher level framework.
Set the hobl callback parameters to call this script followed by the command you want to send.
'''
from builtins import str
from builtins import *
import socket
import sys
import argparse

parser = argparse.ArgumentParser(description='This is a client for testing the callback server. Call this function followed by the command you want to send.')
parser.add_argument('-host', nargs='?', default='localhost', help="The host IP for the server to listen on. Defaults to localhost.")
parser.add_argument('-port', nargs='?', default=9999, help="The port number for the server to listen on. Defaults to 9999.")
parser.add_argument('message', metavar='Message', nargs=argparse.REMAINDER, help='This is the command that you would like to send.')

args = parser.parse_args()
host = args.host
port = int(args.port)

send_msg = " ".join(args.message)

print("\nSending:")
print("\tHost:\t\t" + host)
print("\tPort:\t\t" + str(port))
print("\tCommand:\t" + str(send_msg) + "\n")

# Create a socket (SOCK_STREAM means a TCP socket)
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Connect to server and send send_msg
    skt.connect((host, port))
    # skt.sendall(send_msg + "\n")
    skt.sendall(send_msg.encode() + '\r\n'.encode())

    if ("Get_Data" in send_msg):
        # Receive file from the server and write it to the disk (test.csv in current directory)
        rcvd_msg = "OK"
        with open("test.csv", "wb") as f:
            while True:
                data = skt.recv(1024)
                if not data:
                    break
                f.write(data)
    else:
        # Receive send_msg from the server and shut down
        rcvd_msg = skt.recv(1024).decode()
finally:
    skt.close()

print("Sent:     {}".format(send_msg))
print("Received: {}".format(rcvd_msg))
print("\n")
