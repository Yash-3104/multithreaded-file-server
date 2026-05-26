========================================
Multithreaded File Server
========================================

One-line justification:
"I selected this project to demonstrate concurrency, networking, and OS concepts in a practical multi-client file-sharing application."

----------------------------------------
Overview
----------------------------------------
This project implements a multithreaded file server that allows multiple clients
to upload and download files simultaneously. It uses Python sockets for 
networking, threading for concurrency, and an SQLite database to track uploaded 
files. The client features a Tkinter GUI, making it easy to select files to 
upload and specify filenames for download.

Key features:
- Multiple clients can upload/download concurrently.
- TCP sockets for reliable file transfers.
- Checksum verification (SHA-256) to ensure file integrity.
- Simple GUI using Tkinter for client operations.
- SQLite database stores file metadata (filename, size, checksum).

----------------------------------------
Running from Source
----------------------------------------
1. Make sure you have Python 3 installed.
2. Install required libraries (e.g., Pillow for image handling):
   pip install pillow
3. Run the server:
   python server.py
   - The server will create a "files" folder (if it doesn't exist) to store uploaded files.
   - By default, it listens on port 5000 (configurable in config.ini).

4. Run the client:
   python client.py
   - The client GUI will appear. Enter the server IP (e.g., 127.0.0.1 if local)
     and the server port (e.g., 5000).
   - Click "Upload Files" to select one or more files to upload.
   - Click "Download File" to specify a base filename for downloading.

----------------------------------------
Running from the Compiled EXE
----------------------------------------
1. Navigate to the 'dist' or 'Final_Submission' folder containing:
   - server.exe
   - client.exe
   - icons folder (if onedir) or included in the exe (if onefile).
   - config.ini
2. Start the server by double-clicking "server.exe" (or run in a console to see logs).
3. Start the client by double-clicking "client.exe".
4. In the client GUI, enter "127.0.0.1" for IP (if local) and "5000" for port, 
   then proceed with uploads/downloads.

----------------------------------------
File/Folder Structure
----------------------------------------
- client.py        # Client GUI code
- server.py        # Multithreaded server code
- protocol.py      # Shared protocol helpers 
- config.ini       # Configuration for server/client
- icons/           # Folder containing icon images (save.png, load.png , process.png)
- dist/            # Folder containing compiled .exe files (if onedir mode)
- README.txt       # This file

----------------------------------------
Notes
----------------------------------------
- The server automatically creates a "files" folder to store uploaded files.
- The client creates a "downloads" folder for received files.
- If any folder doesn't exist, it will be created at runtime.
- Ensure you have the correct Python environment or all required libraries 
  installed when running from source.

----------------------------------------
Thank you!
----------------------------------------
