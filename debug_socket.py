import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('94.43.41.14', 8090))

