import socket
import threading
import sys 
import argparse
import select


#TODO: Implement a client that connects to your server to chat with other clients here

# Use sys.stdout.flush() after print statemtents

parser = argparse.ArgumentParser(description="Chat Room Client")
parser.add_argument('-join', action='store_true', help='Join a chat room')
parser.add_argument('-host', type=str, help='Hostname of the chat server')
parser.add_argument('-port', type=int, help='Port number of the chat server')
parser.add_argument('-username', type=str, help='Your username')
parser.add_argument('-passcode', type=str, help='Passcode for the chatroom')
args = parser.parse_args()
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = ":Exit"
HEADER = 100
stop_event = threading.Event()


def receive_messages(client_socket):
    while not stop_event.is_set():
        try:
            message = client_socket.recv(1024).decode(FORMAT)
            if not message:
                stop_event.set()
                break 
            print(message)
            sys.stdout.flush()
        except socket.error as s:
            if not stop_event.is_set():
                print(f"A socket error occurred: {s}")
                sys.stdout.flush() 
            break
        except Exception as e:
            if not stop_event.is_set():
                print(f"An error occurred: {e}")
                sys.stdout.flush() 
            break
    """
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    """
    
def send_messages(client_socket):
    while not stop_event.is_set():
        message = input()
        
        if message == ":Exit":
            stop_event.set()
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            break
        else:
            client_socket.send(message.encode(FORMAT))
            
if __name__ == "__main__":
     
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        try:
            client_sock.connect((args.host, args.port))
            credentials = f"{args.username}:{args.passcode}"
            client_sock.send(credentials.encode('utf-8'))
            response = client_sock.recv(1024).decode('utf-8')
            if response == "Connected":
                print(f"Connected to {args.host} on port {args.port}")
                sys.stdout.flush() 
                thread = threading.Thread(target=receive_messages, args=(client_sock,))
                thread.start()
                send_messages(client_sock)
            else:
                print("Incorrect passcode")
                sys.stdout.flush() 
                stop_event.set()
                client_sock.close()
        except socket.error as e:
            print(f"Connection error: {e}")
            sys.stdout.flush() 
        finally:
            if not stop_event.is_set():
                stop_event.set()
                client_sock.close()
                thread.join()



