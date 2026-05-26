 Multithreaded File Server

# Overview

This project implements a **multithreaded file server** that allows multiple clients to upload and download files simultaneously. It uses:

- **Python Sockets** for networking
- **Threading** for concurrency
- **SQLite Database** for storing file metadata
- **Tkinter GUI** for user-friendly client interaction

The system supports reliable TCP-based file transfers with checksum verification to ensure data integrity.

---

# Features

- Multiple clients can upload/download files concurrently
- TCP socket-based communication
- SHA-256 checksum verification for file integrity
- Tkinter GUI for client operations
- SQLite database for tracking uploaded files
- Automatic folder creation for uploads/downloads
- Configurable IP and port using `config.ini`

---

# Tech Stack

- Python
- Socket Programming
- Multithreading
- Tkinter
- SQLite
- SHA-256 Hashing

---

# Project Structure

```bash
multithreaded-file-server/
│
├── client.py          # Client GUI application
├── server.py          # Multithreaded server
├── protocol.py        # Shared communication protocol helpers
├── gui.py             # GUI-related components
├── create_icons.py    # Icon generation utility
├── config.ini         # Configuration settings
├── icons/             # Application icons
├── dist/              # Compiled executable files
├── downloads/         # Downloaded files (created automatically)
├── files/             # Uploaded files stored on server
└── README.md
