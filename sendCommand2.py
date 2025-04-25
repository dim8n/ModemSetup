import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLineEdit, QLabel, 
                             QComboBox, QWidget, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont


class SerialWorker(QThread):
    result_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, port, command):
        super().__init__()
        self.port = port
        self.command = command
        self.serial_conn = None

    def run(self):
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            
            # Отправка команды
            self.serial_conn.write((self.command + "\r\n").encode('utf-8'))
            
            # Чтение ответа
            response = []
            while True:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if not line:
                    break
                response.append(line)
            
            self.result_received.emit("\n".join(response))
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()


class ATCommandApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AT Command Sender")
        self.setGeometry(100, 100, 600, 500)
        
        self.worker = None
        self.init_ui()
        self.update_com_ports()

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        # COM-порт
        com_layout = QHBoxLayout()
        com_layout.addWidget(QLabel("COM Port:"))
        
        self.com_port_combo = QComboBox()
        self.refresh_ports_btn = QPushButton("Refresh")
        self.refresh_ports_btn.clicked.connect(self.update_com_ports)
        
        com_layout.addWidget(self.com_port_combo, 1)
        com_layout.addWidget(self.refresh_ports_btn)
        layout.addLayout(com_layout)

        # Кнопки команд
        btn_layout = QHBoxLayout()
        
        self.band_query_btn = QPushButton("Режим работы (AT!BAND?)")
        self.band_query_btn.clicked.connect(lambda: self.send_command("at!band?"))
        
        self.band_equals_query_btn = QPushButton("Доступные режимы (AT!BAND=?)")
        self.band_equals_query_btn.clicked.connect(lambda: self.send_command("at!band=?"))
        
        self.command1_btn = QPushButton("AT!BAND=00")
        self.command1_btn.clicked.connect(lambda: self.send_command("at!band=00"))
        self.command2_btn = QPushButton("AT!BAND=01")
        self.command2_btn.clicked.connect(lambda: self.send_command("at!band=01"))
        self.command3_btn = QPushButton("AT!BAND=09")
        self.command3_btn.clicked.connect(lambda: self.send_command("at!band=09"))

        btn_layout.addWidget(self.band_query_btn)
        btn_layout.addWidget(self.band_equals_query_btn)
        btn_layout.addWidget(self.command1_btn)
        btn_layout.addWidget(self.command2_btn)
        btn_layout.addWidget(self.command3_btn)
        layout.addLayout(btn_layout)

        # Пользовательская команда
        custom_layout = QHBoxLayout()
        
        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter custom AT command")
        
        self.send_custom_btn = QPushButton("Send Custom")
        self.send_custom_btn.clicked.connect(self.send_custom_command)
        
        custom_layout.addWidget(self.custom_cmd_input, 1)
        custom_layout.addWidget(self.send_custom_btn)
        layout.addLayout(custom_layout)

        # Вывод результатов
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        hack_font = QFont("Hack", 10)
        self.result_output.setFont(hack_font)
        layout.addWidget(self.result_output)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def update_com_ports(self):
        self.com_port_combo.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.com_port_combo.addItem("No ports found")
            return
        
        for port in ports:
            self.com_port_combo.addItem(port.device, port.device)

    def send_command(self, command):
        if not command:
            return
            
        selected_port = self.com_port_combo.currentData()
        if not selected_port or selected_port == "No ports found":
            QMessageBox.warning(self, "Error", "No COM port selected or available!")
            return
        
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Warning", "Please wait for the current command to finish")
            return
        
        self.result_output.append(f"> {command}")
        
        self.worker = SerialWorker(selected_port, command)
        self.worker.result_received.connect(self.display_result)
        self.worker.error_occurred.connect(self.display_error)
        self.worker.start()

    def send_custom_command(self):
        command = self.custom_cmd_input.text().strip()
        if command:
            self.send_command(command)

    def display_result(self, result):
        self.result_output.append(result)
        self.result_output.append("")  # Пустая строка для разделения

    def display_error(self, error):
        self.result_output.append(f"Error: {error}")
        self.result_output.append("")  # Пустая строка для разделения


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ATCommandApp()
    window.show()
    sys.exit(app.exec_())