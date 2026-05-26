import socket
import threading
import sqlite3
import os
import configparser
import logging

# Import shared protocol helpers
from protocol import (
    read_line, send_line, recv_int, send_int, recv_str, send_str,
    recv_exact, normalize_filename, calculate_checksum
)

# ------------------------
# Logging configuration
# ------------------------
logging.basicConfig(
    level=logging.DEBUG,
    filename='server.log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ------------------------
# Database
# ------------------------
thread_local = threading.local()

def get_db_connection(db_path):
    """
    Return a thread-local SQLite connection.
    """
    if not hasattr(thread_local, 'conn'):
        thread_local.conn = sqlite3.connect(db_path)
    return thread_local.conn

def init_db(db_path):
    """
    Create the files table if it doesn't exist.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT UNIQUE,
            file_size INTEGER,
            upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            checksum TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ------------------------
# Handlers
# ------------------------
def handle_upload(sock, directory):
    conn = get_db_connection(os.path.join(directory, "files.db"))
    try:
        # 1) Receive the file name
        file_name = normalize_filename(recv_str(sock))
        logging.info(f"UPLOAD request for file: {file_name}")

        cursor = conn.cursor()
        cursor.execute("SELECT file_name FROM files WHERE file_name = ?", (file_name,))
        if cursor.fetchone():
            send_line(sock, "FILE_EXISTS")
            logging.info(f"File '{file_name}' already exists in database.")
            return
        else:
            send_line(sock, "PROCEED")

        # 2) Receive file size + checksum
        file_size = recv_int(sock)
        checksum = recv_str(sock)

        # 3) Receive the file data
        file_path = os.path.join(directory, file_name)
        logging.info(f"Saving uploaded file to: {file_path}")

        with open(file_path, 'wb') as f:
            received = 0
            while received < file_size:
                chunk = sock.recv(min(4096, file_size - received))
                if not chunk:
                    raise ConnectionError("Client disconnected during upload.")
                f.write(chunk)
                received += len(chunk)

        # 4) Verify checksum
        if calculate_checksum(file_path) == checksum:
            cursor.execute("INSERT INTO files (file_name, file_size, checksum) VALUES (?, ?, ?)",
                           (file_name, file_size, checksum))
            conn.commit()
            send_line(sock, "SUCCESS")
            logging.info(f"File '{file_name}' uploaded successfully.")
        else:
            os.remove(file_path)
            send_line(sock, "FAILURE")
            logging.error(f"Checksum mismatch for file '{file_name}'.")

    except Exception as e:
        logging.error(f"Upload error: {e}")
        send_line(sock, "FAILURE")

def handle_download(sock, directory):
    """
    The client sends a 'base_name' (no extension).
    We do a partial match in the DB (base_name%).
    If exactly one file matches, we send back:
      1) FILE_FOUND
      2) The actual full filename
      3) The file size
      4) The checksum
      5) The file data
    Then we wait for "SUCCESS" or "FAILURE".
    """
    conn = get_db_connection(os.path.join(directory, "files.db"))
    try:
        base_name = normalize_filename(recv_str(sock))
        logging.info(f"DOWNLOAD request for base name: {base_name}")

        cursor = conn.cursor()
        cursor.execute("""
            SELECT file_name, file_size, checksum
            FROM files
            WHERE file_name LIKE ?
        """, (base_name + '%',))
        results = cursor.fetchall()

        if len(results) == 0:
            send_line(sock, "FILE_NOT_FOUND")
            logging.info(f"No file found matching '{base_name}'.")
            return
        elif len(results) > 1:
            send_line(sock, "MULTIPLE_FILES")
            logging.info(f"Multiple files found matching '{base_name}'.")
            return

        actual_file_name, file_size, checksum = results[0]
        send_line(sock, "FILE_FOUND")

        # Send the actual file name so the client can keep extension
        send_str(sock, actual_file_name)
        send_int(sock, file_size)
        send_str(sock, checksum)

        file_path = os.path.join(directory, actual_file_name)
        logging.info(f"Sending file '{actual_file_name}' from: {file_path}")

        with open(file_path, 'rb') as f:
            sent = 0
            while sent < file_size:
                data = f.read(min(4096, file_size - sent))
                if not data:
                    break
                sock.sendall(data)
                sent += len(data)

        # Wait for the client's "SUCCESS" or "FAILURE"
        final_resp = read_line(sock)
        if final_resp != "SUCCESS":
            logging.error(f"Client reported download failure for '{actual_file_name}'.")

    except Exception as e:
        logging.error(f"Download error: {e}")
        send_line(sock, "FILE_NOT_FOUND")

def handle_client(sock, directory):
    """
    Reads the initial command line: "UPLOAD" or "DOWNLOAD",
    then calls the appropriate handler.
    """
    try:
        command = read_line(sock)
        logging.info(f"Received command: {command}")
        if command == "UPLOAD":
            handle_upload(sock, directory)
        elif command == "DOWNLOAD":
            handle_download(sock, directory)
        else:
            logging.error(f"Invalid command received: '{command}'")
            send_line(sock, "INVALID_COMMAND")
    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        sock.close()

# ------------------------
# Main
# ------------------------
def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config.getint('server', 'port', fallback=5000)
    directory = config.get('server', 'directory', fallback='./files')

    if not os.path.exists(directory):
        os.makedirs(directory)

    db_path = os.path.join(directory, "files.db")
    init_db(db_path)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)

    print(f"Server listening on port {port}")
    logging.info(f"Server listening on port {port}")

    while True:
        client_sock, addr = server_socket.accept()
        logging.info(f"Accepted connection from {addr}")
        t = threading.Thread(target=handle_client, args=(client_sock, directory), daemon=True)
        t.start()

if __name__ == "__main__":
    main()
