import argparse
import json
import requests
import socket
import threading
import os
import hashlib


# Command-line argument parsing
def parse_arguments():
    parser = argparse.ArgumentParser(description="NibbleTorrent Peer")
    parser.add_argument("netid", help="Your NetID")
    parser.add_argument("torrent_file", help="The torrent file for the file you want to download.")
    parser.add_argument("-p", "--port", type=int, default=8088, help="The port to receive peer connections from.")
    parser.add_argument("-d", "--dest", help="The folder to download to and seed from.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Turn on debugging messages.")
    return parser.parse_args()


# Torrent file parsing
def parse_torrent_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# Tracker communication
def contact_tracker(tracker_url, peer_id, ip, port, torrent_id):
    params = {
        "peer_id": peer_id,
        "ip": ip,
        "port": port,
        "torrent_id": torrent_id
    }
    response = requests.get(tracker_url, params=params)
    return response.json()


# Util: Generate peer ID
def generate_peer_id(netid):
    return f"-ECEN426-{netid}"


# Util: Get local IP address
def get_local_ip():
    # This function will need to be adapted to your specific environment
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# Placeholder for download function
def download_file(torrent_info, tracker_info, dest_folder, port):
    # This function will handle the download process
    pass


def handle_upload(client_socket, address, shared_data):
    try:
        while True:
            # Read request from the peer
            request = client_socket.recv(1024)  # Adjust buffer size as needed
            # Parse the request and determine the action (e.g., piece request)
            # Send the requested piece back to the peer
            # Example: client_socket.send(piece_data)
    except Exception as e:
        print(f"Upload error: {e}")
    finally:
        client_socket.close()


def start_upload_server(host, port, shared_data):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()

    while True:
        client_socket, addr = server_socket.accept()
        threading.Thread(target=handle_upload, args=(client_socket, addr, shared_data)).start()


def request_file_piece(peer_info, piece_index, shared_data):
    try:
        peer_ip, peer_port = peer_info.split(":")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((peer_ip, int(peer_port)))
            # Send request for file piece (implement NibbleTorrent request format)
            # Example: s.send(request_data)
            # Receive and process the piece response
            # Example: piece_data = s.recv(4096)
            # Verify and store the received piece
    except Exception as e:
        print(f"Download error: {e}")


def download_from_peers(peer_list, torrent_info, shared_data):
    # Download file pieces from the list of peers
    for peer in peer_list:
        # Logic to determine which piece to download from which peer
        piece_index = determine_piece_index_to_download(shared_data)
        threading.Thread(target=request_file_piece, args=(peer, piece_index, shared_data)).start()


def initialize_shared_data(torrent_info):
    total_pieces = len(torrent_info["pieces"])
    return {
        "pieces_received": [False] * total_pieces,  # Track received pieces
        "file_data": bytearray(torrent_info["file_size"]),  # Buffer for the file
        # Additional shared states as needed
    }


# Main function
def main():
    args = parse_arguments()
    torrent_info = parse_torrent_file(args.torrent_file)
    peer_id = generate_peer_id(args.netid)
    ip = get_local_ip()
    tracker_info = contact_tracker(torrent_info["tracker_url"], peer_id, ip, args.port, torrent_info["torrent_id"])

    # Shared data structure to manage file download/upload state
    shared_data = initialize_shared_data(torrent_info)

    # Start upload server
    threading.Thread(target=start_upload_server, args=(ip, args.port, shared_data)).start()

    # Start downloading from peers
    download_from_peers(tracker_info["peers"], torrent_info, shared_data)


if __name__ == "__main__":
    main()
