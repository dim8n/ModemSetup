import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
from tkinter import font

class ATCommandSender:
    def __init__(self, root):
        self.root = root
        self.root.title("Modem Setup")
        self.root.geometry("800x700+100+100")

        self.serial_port = None
        self.baud_rate = 115200

        self.init_ui()

    def init_ui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Port selection
        port_frame = ttk.LabelFrame(main_frame, text="COM Port", padding=5)
        port_frame.pack(fill=tk.X, pady=5)

        ttk.Label(port_frame, text="COM Port:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.port_combo = ttk.Combobox(port_frame)
        ports = serial.tools.list_ports.comports()
        port_list_with_descriptions = [f"{port.device} - {port.description or 'Unknown'}" for port in ports]
        self.port_combo['values'] = port_list_with_descriptions

        default_port = "COM13"
        found_default = False
        port_names = [port.device for port in ports]
        if default_port in port_names:
            self.port_combo.set(default_port)
            found_default = True
        elif port_list_with_descriptions:
            self.port_combo.set(port_list_with_descriptions[0].split(' - ')[0])  # Set default to the first available port

        self.connect_btn = ttk.Button(port_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=2, padx=5, pady=5)

        port_frame.columnconfigure(1, weight=1)

        # Command buttons
        btn_frame = ttk.LabelFrame(main_frame, text="Commands", padding=5)
        btn_frame.pack(fill=tk.X, pady=5)

        self.band_query_btn = ttk.Button(btn_frame, text="Current mode?", command=lambda: self.send_command("at!band?"))
        self.band_query_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.band_equal_query_btn = ttk.Button(btn_frame, text="Mode list", command=lambda: self.send_command("at!band=?"))
        self.band_equal_query_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.command1_btn = ttk.Button(btn_frame, text="AT!BAND=00", command=lambda: self.send_command("at!band=00"))
        self.command1_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.command2_btn = ttk.Button(btn_frame, text="AT!BAND=01", command=lambda: self.send_command("at!band=01"))
        self.command2_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.command3_btn = ttk.Button(btn_frame, text="AT!BAND=09", command=lambda: self.send_command("at!band=09"))
        self.command3_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.command4_btn = ttk.Button(btn_frame, text="AT!LTEINFO", command=lambda: self.send_command("AT!LTEINFO"))
        self.command4_btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.command5_btn = ttk.Button(btn_frame, text="AT!GSTATUS?", command=lambda: self.send_command("AT!GSTATUS?"))
        self.command5_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Custom command
        custom_frame = ttk.LabelFrame(main_frame, text="Custom Command", padding=5)
        custom_frame.pack(fill=tk.X, pady=5)

        self.custom_cmd_input = ttk.Entry(custom_frame)
        self.custom_cmd_input.insert(0, "Enter custom AT command")
        self.custom_cmd_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.custom_cmd_input.bind("<FocusIn>", self.clear_placeholder)

        self.send_custom_btn = ttk.Button(custom_frame, text="Send", command=self.send_custom_command)
        self.send_custom_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Output area
        output_frame = ttk.LabelFrame(main_frame, text="Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_area = tk.Text(output_frame, wrap=tk.WORD, state=tk.DISABLED)
        hack_font = font.Font(family="Hack", size=10)
        self.output_area.config(font=hack_font)
        self.output_area.pack(fill=tk.BOTH, expand=True)

        # Clear button
        self.clear_btn = ttk.Button(main_frame, text="Clear Output", command=self.clear_output)
        self.clear_btn.pack(fill=tk.X, pady=5)

        # Disable buttons initially
        self.set_buttons_enabled(False)

    def clear_placeholder(self, event):
        if self.custom_cmd_input.get() == "Enter custom AT command":
            self.custom_cmd_input.delete(0, tk.END)

    def set_buttons_enabled(self, enabled):
        states = tk.NORMAL if enabled else tk.DISABLED
        self.band_query_btn.config(state=states)
        self.band_equal_query_btn.config(state=states)
        self.command1_btn.config(state=states)
        self.command2_btn.config(state=states)
        self.command3_btn.config(state=states)
        self.command4_btn.config(state=states)
        self.command5_btn.config(state=states)
        self.send_custom_btn.config(state=states)
        self.custom_cmd_input.config(state=states)

    def toggle_connection(self):
        selected_port = self.port_combo.get().split(' - ')[0]
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                self.serial_port = None
                self.connect_btn.config(text="Connect")
                self.set_buttons_enabled(False)
                self.append_output("Disconnected from COM port")
            except serial.SerialException as e:
                self.append_output(f"Error disconnecting: {e}")
        else:
            try:
                self.serial_port = serial.Serial(selected_port, self.baud_rate, timeout=0.1)
                self.connect_btn.config(text="Disconnect")
                self.set_buttons_enabled(True)
                self.append_output(f"Connected to {selected_port}")
                self.root.after(100, self.read_data)  # Start reading data periodically
            except serial.SerialException as e:
                self.append_output(f"Failed to open {selected_port}: {e}")
                self.serial_port = None

    def send_command(self, cmd):
        if self.serial_port and self.serial_port.is_open:
            self.append_output(f"> {cmd}")
            try:
                self.serial_port.write((cmd + "\r\n").encode())
            except serial.SerialException as e:
                self.append_output(f"Error sending command: {e}")
        else:
            self.append_output("Not connected to COM port")

    def send_custom_command(self):
        cmd = self.custom_cmd_input.get().strip()
        if cmd and cmd != "Enter custom AT command":
            self.send_command(cmd)

    def read_data(self):
        if self.serial_port and self.serial_port.is_open:
            try:
                while self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode().strip()
                    if data:
                        self.append_output(f"{data}")
            except serial.SerialException as e:
                self.append_output(f"Error reading data: {e}")
                self.toggle_connection() # Disconnect on error
        self.root.after(100, self.read_data) # Continue checking for data

    def clear_output(self):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.delete(1.0, tk.END)
        self.output_area.config(state=tk.DISABLED)

    def append_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n")
        self.output_area.see(tk.END)  # Autoscroll to the bottom
        self.output_area.config(state=tk.DISABLED)

    def on_closing(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ATCommandSender(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()