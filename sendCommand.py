import sys
import serial
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QWidget,
                             QComboBox)
from PyQt5.QtCore import QThread, pyqtSignal


class SerialThread(QThread):
    result_received = pyqtSignal(str)

    def __init__(self, port, command):
        super().__init__()
        self.port = port
        self.command = command
        self.serial_conn = None

    def run(self):
        try:
            self.serial_conn = serial.Serial(self.port, baudrate=115200, timeout=1)
            if not self.serial_conn.is_open:
                self.serial_conn.open()

            # Добавляем \r\n к команде, если их нет
            if not self.command.endswith('\r\n'):
                self.command += '\r\n'

            self.serial_conn.write(self.command.encode('ascii'))
            
            # Читаем ответ
            response = ""
            while True:
                line = self.serial_conn.readline().decode('ascii', errors='ignore').strip()
                if not line:
                    break
                response += line + "\n"

            self.result_received.emit(response)

        except Exception as e:
            self.result_received.emit(f"Error: {str(e)}")
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()


class ATCommandTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AT Command Tool")
        self.setGeometry(100, 100, 600, 400)
        
        self.init_ui()
        self.scan_ports()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        # COM Port selection
        com_layout = QHBoxLayout()
        com_layout.addWidget(QLabel("COM Port:"))
        
        self.port_combo = QComboBox()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.scan_ports)
        
        com_layout.addWidget(self.port_combo)
        com_layout.addWidget(self.refresh_btn)
        layout.addLayout(com_layout)

        # AT Command input
        at_layout = QHBoxLayout()
        at_layout.addWidget(QLabel("AT Command:"))
        
        self.at_input = QLineEdit("AT")
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_command)
        
        at_layout.addWidget(self.at_input)
        at_layout.addWidget(self.send_btn)
        layout.addLayout(at_layout)

        # Response output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def scan_ports(self):
        """Scan for available COM ports"""
        self.port_combo.clear()
        ports = []
        
        # Check common COM ports (Windows)
        for i in range(1, 21):
            port_name = f"COM{i}"
            try:
                s = serial.Serial(port_name)
                s.close()
                ports.append(port_name)
            except (OSError, serial.SerialException):
                pass
        
        # Check common /dev/tty* ports (Linux/Mac)
        for port in ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']:
            try:
                s = serial.Serial(port)
                s.close()
                ports.append(port)
            except (OSError, serial.SerialException):
                pass
        
        if ports:
            self.port_combo.addItems(ports)
        else:
            self.port_combo.addItem("No ports found")

    def send_command(self):
        port = self.port_combo.currentText()
        command = self.at_input.text().strip()
        
        if not port or port == "No ports found":
            self.output.append("Error: No COM port selected")
            return
        
        if not command:
            self.output.append("Error: No AT command entered")
            return
        
        self.output.append(f"> {command}")
        
        self.thread = SerialThread(port, command)
        self.thread.result_received.connect(self.show_result)
        self.thread.start()
        
        # Disable button while command is executing
        self.send_btn.setEnabled(False)
        self.thread.finished.connect(lambda: self.send_btn.setEnabled(True))

    def show_result(self, result):
        self.output.append(result)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ATCommandTool()
    window.show()
    sys.exit(app.exec_())
