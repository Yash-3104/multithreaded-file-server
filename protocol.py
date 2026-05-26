import struct
import hashlib
import os

def read_line(sock):
    """
    Read a line from the socket until newline (\n).
    Returns the line WITHOUT the trailing newline.
    """
    data = b''
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Socket closed unexpectedly.")
        data += chunk
        if chunk == b'\n':
            break
    return data.decode('utf-8').rstrip('\n')

def send_line(sock, text):
    """
    Send a line (text + newline).
    """
    sock.sendall(text.encode('utf-8') + b'\n')

def recv_exact(sock, nbytes):
    """
    Receive exactly nbytes from the socket.
    Raises ConnectionError if the socket closes early.
    """
    data = b''
    while len(data) < nbytes:
        chunk = sock.recv(nbytes - len(data))
        if not chunk:
            raise ConnectionError("Socket closed while reading exact bytes.")
        data += chunk
    return data

def send_int(sock, value):
    """
    Send a 64-bit unsigned integer (network byte order).
    """
    sock.sendall(struct.pack('!Q', value))

def recv_int(sock):
    """
    Receive a 64-bit unsigned integer (network byte order).
    """
    data = recv_exact(sock, 8)
    return struct.unpack('!Q', data)[0]

def send_str(sock, text):
    """
    Send a string with a 64-bit length prefix.
    """
    encoded = text.encode('utf-8')
    send_int(sock, len(encoded))
    sock.sendall(encoded)

def recv_str(sock):
    """
    Receive a string with a 64-bit length prefix.
    """
    length = recv_int(sock)
    data = recv_exact(sock, length)
    return data.decode('utf-8')

def normalize_filename(filename):
    """
    Normalize filename to lowercase to avoid case sensitivity issues.
    """
    return filename.lower()

def calculate_checksum(file_path):
    """
    Calculate SHA-256 checksum of a file.
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()
