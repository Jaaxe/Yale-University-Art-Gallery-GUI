import argparse
from socket import socket, SOL_SOCKET, SO_REUSEADDR
from sys import exit, argv, stderr
from os import name
from pickle import load, dump
from luxlist import query_database
from luxdetails import query_object_details, display_object_details
import sqlite3
def cli_parser():
    parser = argparse.ArgumentParser(
        prog= "luxserver.py",
        description= "Server for the YUAG application",
        allow_abbrev=False,
    )
    parser.add_argument('port', help='the port at which the server should listen')

    args = parser.parse_args()

    return args


def query_list(cursor, request):

    #query database for list
    results = query_database(cursor, request["date"], request["agent"], request["classifier"], request["label"]) #TODO change args
    
    return results
    # print(f"Sent {len(results)} results to client.")

def query_object(cursor, request):
    #query the database for detailed object info

    summary, label, produced_by, classifications, references = query_object_details(cursor, request)
    results = display_object_details(summary, label, produced_by, classifications, references)
    return results
    # print(f"Sent detailed information about {results} to client.")


def handle_client(sock):
    with sock.makefile(mode='rb') as flo_in, sock.makefile(mode='wb') as flo_out:
        try:
            # Read client's request
            request = load(flo_in)
            
            conn = sqlite3.connect("lux.sqlite")
            cursor = conn.cursor()

            # print("server request", request)
            if 'id' in request:
                object_id = request['id']
                details = query_object(cursor, object_id)
                response = {"details": details}  # Wrap details in a dictionary
            else:
                print(request)
                list = query_list(cursor, request)
                # print("hi")
                response = {"list": list}
            
            #return results to client
            dump(response, flo_out)
            flo_out.flush()

            #closes connection
            conn.close()

        except Exception as ex:
            print(f"Error handling client: {ex}", file=stderr)


def main():
    #parse cli and get the port from it
    args = cli_parser()
    port = int(args.port)

    try:
        server_socket = socket()
        print('Opened server socket')
        if name != 'nt':
            server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', port))
        print('Bound server socket to port')
        server_socket.listen()
        print(f'Listening on port {port}')

        while True:
            try:
                sock, client_addr = server_socket.accept()
                with sock:
                    print('Accepted connection')
                    print('Opened socket')
                    print('Server IP addr and port:',
                        sock.getsockname())
                    print('Client IP addr and port:', client_addr)
                    handle_client(sock)
            except Exception as ex:
                print(ex, file=stderr)
    except Exception as ex:
        print(ex, file=stderr)
        exit(1)

if __name__ == "__main__":
    main()