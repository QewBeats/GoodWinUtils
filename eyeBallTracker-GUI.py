import sys
import cv2
from time import sleep
from os import system
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class FaceMonitor(QThread):
    face_detected = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.running = False
        self.secwithoutface = 0

    def run(self):
        faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        vs = cv2.VideoCapture(0)

        self.running = True
        while self.running:
            ret, frame = vs.read()
            if frame is None:
                break

            faces = faceCascade.detectMultiScale(frame)
            if len(faces) == 0:
                self.secwithoutface += 1
            else:
                self.secwithoutface = 0

            self.face_detected.emit(len(faces) > 0)

            if self.secwithoutface == 5:
                system('rundll32.exe user32.dll,LockWorkStation')

            sleep(1)

        vs.release()

    def stop(self):
        self.running = False
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Lock Application")
        self.setGeometry(100, 100, 300, 200)

        # Status label
        self.status_label = QLabel("Status: Idle", self)
        self.status_label.setStyleSheet("font-size: 14px;")
        self.status_label.setAlignment(Qt.AlignCenter)

        # Start Button
        self.start_button = QPushButton("Start Eye Tracking", self)
        self.start_button.clicked.connect(self.start_tracking)

        # Stop Button
        self.stop_button = QPushButton("Stop Eye Tracking", self)
        self.stop_button.clicked.connect(self.stop_tracking)
        self.stop_button.setEnabled(False)  # Initially disabled

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Eye Tracker
        self.monitor = FaceMonitor()
        self.monitor.face_detected.connect(self.update_status)

    def start_tracking(self):
        self.monitor.start()
        self.status_label.setText("Status: Tracking Faces...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_tracking(self):
        self.monitor.stop()
        self.status_label.setText("Status: Idle")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_status(self, face_detected):
        if face_detected:
            self.status_label.setText("Status: Face Detected")
        else:
            self.status_label.setText("Status: No Face Detected")

if __name__ == "__main__":
    # Set QT environment variable to avoid warnings
    import os
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
