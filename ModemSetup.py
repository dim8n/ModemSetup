import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLineEdit, QLabel, QWidget, QGroupBox)
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
from PyQt5.QtGui import QFont

class ATCommandSender(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AT Command Sender")
        self.setGeometry(100, 100, 600, 700)
        
        # Serial port setup
        self.serial = QSerialPort()
        self.serial.setBaudRate(115200)
        self.serial.readyRead.connect(self.read_data)
        
        # UI setup
        self.init_ui()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("COM Port:"))
        
        self.port_combo = QComboBox()
        ports = QSerialPortInfo.availablePorts()
        for port in ports:
            #self.port_combo.addItem(port.portName())
            port_name = port.portName()
            port_description = port.description() or "Unknown"
            self.port_combo.addItem(f"{port_name} - {port_description}", port_name)
        port_layout.addWidget(self.port_combo)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        port_layout.addWidget(self.connect_btn)
        
        main_layout.addLayout(port_layout)
        
        # Command buttons
        btn_layout = QHBoxLayout()
        
        self.band_query_btn = QPushButton("Current mode?")
        self.band_query_btn.clicked.connect(lambda: self.send_command("at!band?"))
        btn_layout.addWidget(self.band_query_btn)
        
        self.band_equal_query_btn = QPushButton("Mode list")
        self.band_equal_query_btn.clicked.connect(lambda: self.send_command("at!band=?"))
        btn_layout.addWidget(self.band_equal_query_btn)

        self.command1_btn = QPushButton("AT!BAND=00")
        self.command1_btn.clicked.connect(lambda: self.send_command("at!band=00"))
        btn_layout.addWidget(self.command1_btn)
        
        self.command2_btn = QPushButton("AT!BAND=01")
        self.command2_btn.clicked.connect(lambda: self.send_command("at!band=01"))
        btn_layout.addWidget(self.command2_btn)
        
        self.command3_btn = QPushButton("AT!BAND=09")
        self.command3_btn.clicked.connect(lambda: self.send_command("at!band=09"))
        btn_layout.addWidget(self.command3_btn)

        self.command4_btn = QPushButton("AT!LTEINFO")
        self.command4_btn.clicked.connect(lambda: self.send_command("AT!LTEINFO"))
        btn_layout.addWidget(self.command4_btn)

        self.command5_btn = QPushButton("AT!GSTATUS?")
        self.command5_btn.clicked.connect(lambda: self.send_command("AAT!GSTATUS?"))
        btn_layout.addWidget(self.command5_btn)
       
        main_layout.addLayout(btn_layout)
        
        # Custom command
        custom_layout = QHBoxLayout()
        
        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter custom AT command")
        custom_layout.addWidget(self.custom_cmd_input)
        
        self.send_custom_btn = QPushButton("Send")
        self.send_custom_btn.clicked.connect(self.send_custom_command)
        custom_layout.addWidget(self.send_custom_btn)
        
        main_layout.addLayout(custom_layout)
        
        # Output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        
        # Set Hack font
        hack_font = QFont("Hack", 10)
        self.output_area.setFont(hack_font)

        main_layout.addWidget(self.output_area)
        
        self.clear_btn = QPushButton("Clear Output")
        self.clear_btn.clicked.connect(self.clear_output)
        main_layout.addWidget(self.clear_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Disable buttons until connected
        self.set_buttons_enabled(False)
        
    def set_buttons_enabled(self, enabled):
        self.band_query_btn.setEnabled(enabled)
        self.band_equal_query_btn.setEnabled(enabled)
        self.command1_btn.setEnabled(enabled)
        self.command2_btn.setEnabled(enabled)
        self.command3_btn.setEnabled(enabled)
        self.command4_btn.setEnabled(enabled)
        self.command5_btn.setEnabled(enabled)
        self.send_custom_btn.setEnabled(enabled)
        self.custom_cmd_input.setEnabled(enabled)
        
    def toggle_connection(self):
        if self.serial.isOpen():
            self.serial.close()
            self.connect_btn.setText("Connect")
            self.set_buttons_enabled(False)
            self.append_output("Disconnected from COM port")
        else:
            #port_name = self.port_combo.currentText()
            port_name = self.port_combo.currentData()
            self.serial.setPortName(port_name)
            if self.serial.open(QIODevice.ReadWrite):
                self.connect_btn.setText("Disconnect")
                self.set_buttons_enabled(True)
                self.append_output(f"Connected to {port_name}")
            else:
                self.append_output(f"Failed to open {port_name}")
                
    def send_command(self, cmd):
        if self.serial.isOpen():
            self.append_output(f"> {cmd}")
            self.serial.write((cmd + "\r\n").encode())
        else:
            self.append_output("Not connected to COM port")
            
    def send_custom_command(self):
        cmd = self.custom_cmd_input.text().strip()
        if cmd:
            self.send_command(cmd)
            
    def read_data(self):
        while self.serial.canReadLine():
            data = self.serial.readLine().data().decode().strip()
            self.append_output(f"{data}")
            
    def clear_output(self):
        """Clear the output text area"""
        self.output_area.clear()

    def append_output(self, text):
        self.output_area.append(text)
        
    def closeEvent(self, event):
        if self.serial.isOpen():
            self.serial.close()
        event.accept()

# QComboBox wasn't imported in the original code, so we need to add it
from PyQt5.QtWidgets import QComboBox

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ATCommandSender()
    window.show()
    sys.exit(app.exec_())