import socket
import threading

s_log = open("TCP_log4server.txt", "w") #Open the .txt

def client_C(client_socket): #Function for each connection
    client_address = client_socket.getpeername()
    s_log.write("Accepted connection from {}: {}\n".format(*client_address))
    s_log.flush()

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            msg = data.decode() #Decode msg

            s_log.write("Received from {}:{}: {}\n".format(*client_address, msg)) #Record msg
            s_log.flush()

            ack = "Received your msg: " + msg #Send ack
            client_socket.sendall(ack.encode())

            s_log.write("Sent to {}:{}: {}\n".format(*client_address, ack)) #Record ack
            s_log.flush()

    except Exception as e:
        s_log.write("Err: {}\n".format(e))
    finally:
        s_log.write("Connection closed by {}:{}\n".format(*client_address))
        s_log.flush()
        client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Server socket

server_address = ('127.0.0.1', 12349) #Bind serv address / port
server_socket.bind(server_address)
server_socket.listen(5)
s_log.write("Server is listening on {}:{}\n".format(*server_address))
s_log.flush()

try:
    while True:
        s_log.write("Waiting for a connection...\n")
        s_log.flush()

        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=client_C, args=(client_socket,))
        client_thread.start()

except KeyboardInterrupt:
    s_log.write("Ctrl+C was pressed - Ending server\n")
finally:
    s_log.close() #Close file