import socket
import os
import base64
import json

def parse_response(response_str):
    try:
        header_part, body_part = response_str.split('\r\n\r\n', 1)
        return header_part, body_part
    except ValueError:
        return response_str, ""

def print_response_body(body_str):
    try:
        data = json.loads(body_str)
        print(json.dumps(data, indent=4))
    except json.JSONDecodeError:
        print(body_str)

def send_request(host, port, request_str):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((host, port))
            sock.sendall(request_str.encode('utf-8'))

            response_bytes = b''
            while True:
                try:
                    data = sock.recv(2048)
                    if not data:
                        break
                    response_bytes += data
                except socket.timeout:
                    break

            return response_bytes.decode('utf-8')
    except ConnectionRefusedError:
        return "KONEKSI GAGAL: Pastikan server sudah berjalan."
    except Exception as e:
        return f"Terjadi Error: {str(e)}"

def list_files(host, port):
    print("\n[INFO] Meminta daftar file dari endpoint /list...")
    request = "GET /list HTTP/1.0\r\n\r\n"
    response = send_request(host, port, request)
    header, body = parse_response(response)
    print("Respons dari Server")
    print_response_body(body)

def upload_file(host, port, filepath):
    filename = os.path.basename(filepath)
    print(f"[INFO] Mengirim file '{filename}' ke endpoint /upload...")

    try:
        with open(filepath, 'rb') as f:
            file_content_binary = f.read()

        file_content_base64 = base64.b64encode(file_content_binary).decode('utf-8')

        body = file_content_base64
        headers = [
            "POST /upload HTTP/1.0",
            f"X-Filename: {filename}",
            f"Content-Length: {len(body)}",
        ]
        request = "\r\n".join(headers) + "\r\n\r\n" + body

        response = send_request(host, port, request)
        header, body = parse_response(response)
        print("Respons dari Server")
        print_response_body(body)

    except FileNotFoundError:
        print(f"ERROR: File '{filepath}' tidak ditemukan di client.")

def delete_file(host, port, filename):
    print(f"[INFO] Mengirim permintaan hapus untuk '{filename}'...")
    request = f"DELETE /delete/{filename} HTTP/1.0\r\n\r\n"
    response = send_request(host, port, request)
    header, body = parse_response(response)
    print("Respons dari Server")
    print_response_body(body)

if __name__ == '__main__':
    TARGET_HOST = '172.16.16.101'
    # TARGET_PORT = 8889  # process
    TARGET_PORT = 8885  # thread 

    print(f"\nTerhubung ke SERVER {TARGET_HOST}:{TARGET_PORT}")

    while True:
        print("\nPilih perintah:")
        print("1. list                      - Menampilkan daftar file")
        print("2. upload <nama_file>        - Mengunggah file")
        print("3. delete <nama_file>        - Menghapus file")
        print("4. exit                      - Keluar program")

        command_input = input(">> ").strip()

        if not command_input:
            continue

        tokens = command_input.split(maxsplit=1)
        command = tokens[0].lower()

        if command == 'list' or command == '1':
            list_files(TARGET_HOST, TARGET_PORT)

        elif command == 'upload' or command == '2':
            if len(tokens) < 2:
                print("ERROR: Harap masukkan nama file. Contoh: upload file.txt")
                continue
            filepath = tokens[1]
            if not os.path.exists(filepath):
                print(f"File '{filepath}' tidak ditemukan.")
            else:
                upload_file(TARGET_HOST, TARGET_PORT, filepath)

        elif command == 'delete' or command == '3':
            if len(tokens) < 2:
                print("ERROR: Harap masukkan nama file. Contoh: delete file.txt")
                continue
            filename = tokens[1]
            delete_file(TARGET_HOST, TARGET_PORT, filename)

        elif command == 'exit' or command == '4':
            print("Keluar dari program.")
            break

        else:
            print("Perintah tidak dikenali. Silakan coba lagi.")
