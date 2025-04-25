import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QComboBox, QLineEdit, 
                             QLabel, QWidget, QGroupBox)
from PyQt5.QtCore import QIODevice
from PyQt5.QtGui import QFont
from serial import Serial
from serial.tools import list_ports


class ATCommandApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AT Command Sender")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        
        # COM port selection
        self.com_group = QGroupBox("COM Port Selection")
        self.com_layout = QHBoxLayout()
        
        self.com_label = QLabel("Select COM Port:")
        self.com_combo = QComboBox()
        self.refresh_com_ports()
        
        self.com_layout.addWidget(self.com_label)
        self.com_layout.addWidget(self.com_combo)
        self.com_group.setLayout(self.com_layout)
        
        # Command section
        self.cmd_group = QGroupBox("Commands")
        self.cmd_layout = QVBoxLayout()
        
        # Standard buttons
        self.btn_layout = QHBoxLayout()
        self.band_query_btn = QPushButton("Send AT!BAND?")
        self.band_query_btn.clicked.connect(lambda: self.send_command("at!band?"))
        
        self.band_equals_query_btn = QPushButton("Send AT!BAND=?")
        self.band_equals_query_btn.clicked.connect(lambda: self.send_command("at!band=?"))
        
        self.btn_layout.addWidget(self.band_query_btn)
        self.btn_layout.addWidget(self.band_equals_query_btn)
        
        # Custom command
        self.custom_cmd_layout = QHBoxLayout()
        self.custom_cmd_label = QLabel("Custom Command:")
        self.custom_cmd_input = QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter AT command here")
        self.custom_cmd_btn = QPushButton("Send")
        self.custom_cmd_btn.clicked.connect(self.send_custom_command)
        
        self.custom_cmd_layout.addWidget(self.custom_cmd_label)
        self.custom_cmd_layout.addWidget(self.custom_cmd_input)
        self.custom_cmd_layout.addWidget(self.custom_cmd_btn)
        
        self.cmd_layout.addLayout(self.btn_layout)
        self.cmd_layout.addLayout(self.custom_cmd_layout)
        self.cmd_group.setLayout(self.cmd_layout)
        
        # Output section
        self.output_group = QGroupBox("Output")
        self.output_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Hack", 10))
        
        self.clear_btn = QPushButton("Clear Output")
        self.clear_btn.clicked.connect(self.clear_output)
        
        self.output_layout.addWidget(self.output_text)
        self.output_layout.addWidget(self.clear_btn)
        self.output_group.setLayout(self.output_layout)
        
        # Add all groups to main layout
        self.main_layout.addWidget(self.com_group)
        self.main_layout.addWidget(self.cmd_group)
        self.main_layout.addWidget(self.output_group)
        
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
        # Serial port
        self.serial_port = None
        
    def refresh_com_ports(self):
        """Refresh the list of available COM ports"""
        self.com_combo.clear()
        ports = list_ports.comports()
        for port in ports:
            display_text = f"{port.device} - {port.description}"
            self.com_combo.addItem(display_text, port.device)
    
    def send_command(self, command):
        """Send AT command to selected COM port"""
        selected_port = self.com_combo.currentData()
        if not selected_port:
            self.output_text.append("No COM port selected!")
            return
            
        try:
            if not self.serial_port or self.serial_port.port != selected_port:
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.close()
                self.serial_port = Serial(selected_port, baudrate=115200, timeout=1)
            
            self.serial_port.write((command + "\r\n").encode())
            self.output_text.append(f"> {command}")
            
            # Read response
            response = ""
            while True:
                line = self.serial_port.readline().decode().strip()
                if not line:
                    break
                response += line + "\n"
            
            if response:
                self.output_text.append(response)
            else:
                self.output_text.append("No response received")
                
        except Exception as e:
            self.output_text.append(f"Error: {str(e)}")
    
    def send_custom_command(self):
        """Send custom command from input field"""
        command = self.custom_cmd_input.text().strip()
        if command:
            self.send_command(command)
            self.custom_cmd_input.clear()
    
    def clear_output(self):
        """Clear the output text area"""
        self.output_text.clear()
    
    def closeEvent(self, event):
        """Close serial port when window is closed"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ATCommandApp()
    window.show()
    sys.exit(app.exec_())