import socket
import threading
import sys 
import argparse
import select
from datetime import datetime, timedelta
import time


#TODO: Implement all code for your server here

# Use sys.stdout.flush() after print statemtents
DISCONNECT_MESSAGE = ":Exit"
HEADER = 100
FORMAT = 'utf-8' 
parser = argparse.ArgumentParser(description="Chat Room Server")
parser.add_argument('-start', action='store_true', help='Start the server')
parser.add_argument('-port', type=int, help='Listening port for the server')
parser.add_argument('-passcode', type=str, help='Passcode for joining the chatroom')
args = parser.parse_args()

clients = [] 
passcode = args.passcode

def broadcast(message, exclude_socket=None):
    for client in clients:
        if client['socket'] != exclude_socket:
            try:
                client['socket'].send(message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending message to {client['address']}: {e}")
                sys.stdout.flush()

def handle_client(conn, addr):
    incorrect_passcode = False
    try:
        credentials = conn.recv(1024).decode('utf-8')
        username, client_passcode = credentials.split(':')
        
        if client_passcode == args.passcode:
            conn.send("Connected".encode('utf-8'))
            print(f"{username} joined the chatroom")
            sys.stdout.flush()
            broadcast(f"{username} joined the chatroom", exclude_socket=conn)
            clients.append({'socket': conn, 'address': addr, 'username': username})
            while True:
                message = conn.recv(1024).decode(FORMAT)
                if not message:
                    break
                if message == ':)':
                    print(f"{username}: [feeling happy]")
                    sys.stdout.flush()
                    broadcast(f"{username}: [feeling happy]", exclude_socket=conn)
                    sys.stdout.flush()
                    
                elif message == ':(':
                    print(f"{username}: [feeling sad]")
                    sys.stdout.flush()
                    broadcast(f"{username}: [feeling sad]", exclude_socket=conn)
                    sys.stdout.flush()
                elif message == ':mytime':
                    timestamp = datetime.now()
                    formatted_time = timestamp.strftime("%a %b %d %H:%M:%S %Y")
                    print(f"{username}: {formatted_time}")
                    sys.stdout.flush()
                    broadcast(f"{username}: {formatted_time}", exclude_socket=conn)
                    sys.stdout.flush()
                elif message == ':+1hr':
                    current_time = datetime.now()
                    new_time = current_time + timedelta(hours=1)
                    formatted_time = new_time.strftime("%a %b %d %H:%M:%S %Y")
                    print(f"{username}: {formatted_time}")
                    sys.stdout.flush()
                    broadcast(f"{username}: {formatted_time}", exclude_socket=conn)
                    sys.stdout.flush()
                elif message.startswith(':dm'):
                    _, receiver_username, *receiver_message = message.split()
                    private_message = ' '.join(receiver_message)
                    recipient_client = next((client for client in clients if client['username'] == receiver_username), None)
                    if recipient_client is not None:
                        print(f"{username} to {receiver_username}: {private_message}")
                        sys.stdout.flush()
                        recipient_client['socket'].send(f"{username}: {private_message}".encode(FORMAT))
                    else:
                        conn.send(f"User {receiver_username} not found.".encode(FORMAT))
                        sys.stdout.flush()
                    
                elif message == DISCONNECT_MESSAGE:
                    break
                else:
                    print(f"{username}: {message}")
                    sys.stdout.flush()
                    broadcast(f"{username}: {message}", exclude_socket=conn)
                    sys.stdout.flush()
        else:
            conn.send("Incorrect passcode".encode('utf-8'))
            incorrect_passcode = True
            conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.stdout.flush()
    finally:
        for client in clients:
            if client['socket'] == conn:
                clients.remove(client)
                break
        if not incorrect_passcode:
            print(f"{username} left the chatroom")
            sys.stdout.flush()
            broadcast(f"{username} left the chatroom", exclude_socket=conn)
            sys.stdout.flush()
    try:
        conn.close()
    except Exception as e:
        pass
    

def start(server):
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args = (conn, addr))
        thread.start()

if __name__ == "__main__":
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
		server_sock.bind(('127.0.0.1', args.port))
		server_sock.listen()
		print(f"Server started on port {args.port}. Accepting connections")
		sys.stdout.flush()
		start(server_sock)