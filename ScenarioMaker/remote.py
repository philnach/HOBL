"""
Handles receiving screen casts from the DUT.
"""

from PyQt6.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import socket
import pickle
import struct
import numpy as np
from datetime import datetime
import qoi

class RemoteThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, settings):
        super().__init__()
        self.run_flag = True
        self.settings = settings
        self.connected = False


    def recvall(self, n):
        data = bytearray()

        while len(data) < n:
            try:
                packet = self.video_client_socket.recv(n - len(data))
                if not packet:
                    return None
            except:
                return None

            data.extend(packet)

        return bytes(data)


    def connect(self):
        # Create a socket client
        try:
            self.video_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.video_client_socket.connect((self.settings.get("dut_ip"), 8020))
            self.connected = True

            # Expect 8 bytes: 4 bytes for width and 4 bytes for height
            header = self.recvall(8)
            if header is None:
                print("Failed to receive initial dimensions header")
                return False
            height, width = struct.unpack('<II', header)
            self.full_frame = np.zeros((height, width, 4), dtype=np.uint8)

            return True
        except:
            print("Could not connect to ScreenServer")
            return False


    def capture_frame(self):
        # Read 4 bytes for the number of dirty rectangles
        rect_count = self.recvall(4)
        if rect_count is None:
            print("Incomplete rectangle count received")
            return False
        dirty_rect_count = struct.unpack('<I', rect_count)[0]

        for _ in range(dirty_rect_count):
            # Read 16 bytes for the rectangle (left, top, right, bottom)
            rect_data = self.recvall(16)
            if rect_data is None:
                print("Incomplete rectangle data received")
                return False
            left, top, right, bottom = struct.unpack('<iiii', rect_data)

            region_width  = right - left
            region_height = bottom - top

            # Read the region's QOI-encoded size (4 bytes)
            region_size_data = self.recvall(4)
            if region_size_data is None:
                print("Incomplete region size data received")
                return False
            region_encoded_size = struct.unpack('<I', region_size_data)[0]

            # Read the QOI-encoded data for this region
            region_qoi_data = self.recvall(region_encoded_size)
            if region_qoi_data is None:
                print("Incomplete QOI data received")
                return False

            try:
                region_frame = qoi.decode(region_qoi_data)
            except:
                print("QOI decoding failed")
                return False

            if region_frame.shape[0] != region_height or region_frame.shape[1] != region_width:
                print(f"Mismatch in region dimensions: {region_frame.shape}")
                return False

            self.full_frame[top:bottom, left:right, :] = region_frame

        self.change_pixmap_signal.emit(self.full_frame)
        return True


    def run(self):
        fail_count = 0
        while self.run_flag:
            result = self.capture_frame()
            if not result:
                fail_count += 1
                if fail_count >= 10:
                    return


    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.run_flag = False
        if self.connected:
            self.video_client_socket.shutdown(socket.SHUT_RDWR)
            self.video_client_socket.close()
            print("Shutting down socket")
        self.wait()
