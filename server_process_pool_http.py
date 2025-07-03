from socket import *
import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http import HttpServer

httpserver = HttpServer()

#untuk menggunakan processpoolexecutor, karena tidak mendukung subclassing pada process,
#maka class ProcessTheClient dirubah dulu menjadi function, tanpda memodifikasi behaviour didalamnya

def ProcessTheClient(connection,address):
    try:
        headers = b""
        while not headers.endswith(b'\r\n\r\n'):
            data = connection.recv(1)
            if not data:
                break
            headers += data
        
        if not headers:
            connection.close()
            return
        
        header_str = headers.decode('utf-8')
        
        content_length = 0
        lines = header_str.split('\r\n')
        for line in lines:
            if line.lower().startswith('content-length:'):
                content_length = int(line.split(':')[1].strip())
                break
                
        body = b""
        if content_length > 0:
            body_read = 0
            while body_read < content_length:
                data = connection.recv(min(1024, content_length - body_read))
                if not data:
                    break
                body += data
                body_read += len(data)

        full_request = headers + body
        
        rcv = full_request.decode('utf-8')
        hasil = httpserver.proses(rcv)
        connection.sendall(hasil)

    except Exception as e:
        print(f"Error processing request from {address}: {e}")
    finally:
        connection.close()
    return



def Server():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8889))
    my_socket.listen(50)
    print(f"Process Pool Server running on port 8889...")

    with ProcessPoolExecutor(max_workers=20) as executor:
        while True:
            try:
                connection, client_address = my_socket.accept()
                print(f"Connection from {client_address}")
                executor.submit(ProcessTheClient, connection, client_address)
                
            except Exception as e:
                print(f"Error accepting connections: {e}")
                break

def main():
	Server()

if __name__=="__main__":
	main()

