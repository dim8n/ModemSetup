import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time

class ATCommandSender:
    def __init__(self, master):
        self.master = master
        master.title("AT Command Sender")

        self.port = tk.StringVar()
        self.at_command = tk.StringVar()
        self.serial_connection = None
        self.is_connected = tk.BooleanVar(value=False)
        self.baudrate = 115200
        self.timeout = 1.0
        self.receive_thread = None
        self.stop_reading = threading.Event()

        self.create_widgets()
        self.update_com_ports()

    def create_widgets(self):
        # Выбор COM-порта
        ttk.Label(self.master, text="COM порт:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.port_combo = ttk.Combobox(self.master, textvariable=self.port)
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.port_combo.bind("<<ComboboxSelected>>", self.on_port_selected)
        ttk.Button(self.master, text="Обновить порты", command=self.update_com_ports).grid(row=0, column=2, padx=5, pady=5)
        # Кнопка подключения/отключения
        self.connect_button = ttk.Button(self.master, text="Подключиться", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=5, pady=5) # Размещаем справа

        # Ввод AT-команды
        ttk.Label(self.master, text="AT команда:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        at_command_entry = ttk.Entry(self.master, textvariable=self.at_command)
        at_command_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")

        # Кнопки предустановленных команд
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="ew")
        self.button1 = ttk.Button(button_frame, text="ATI", command=self.send_command_1)
        self.button1.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button2 = ttk.Button(button_frame, text="2", command=self.send_command_2)
        self.button2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button3 = ttk.Button(button_frame, text="3", command=self.send_command_3)
        self.button3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button4 = ttk.Button(button_frame, text="4", command=self.send_command_4)
        self.button4.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button5 = ttk.Button(button_frame, text="5", command=self.send_command_5)
        self.button5.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Кнопка отправки произвольной команды
        self.send_button = ttk.Button(self.master, text="Отправить", command=self.send_at_command)
        self.send_button.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

        # Область для отображения ответа
        self.response_text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=10)
        self.response_text_area.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.response_text_area.config(state=tk.DISABLED) # Сделаем поле только для чтения

        # Кнопка очистки вывода
        clear_button = ttk.Button(self.master, text="Очистить вывод", command=self.clear_output)
        clear_button.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        # Конфигурация сетки для растягивания элементов
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=0)
        self.master.grid_columnconfigure(3, weight=0)
        self.master.grid_rowconfigure(4, weight=1)

        # Изначально делаем кнопки команд и "Отправить" неактивными
        self.disable_command_buttons()

    def disable_command_buttons(self):
        self.button1.config(state='disabled')
        self.button2.config(state='disabled')
        self.button3.config(state='disabled')
        self.button4.config(state='disabled')
        self.button5.config(state='disabled')
        self.send_button.config(state='disabled')

    def enable_command_buttons(self):
        self.button1.config(state='normal')
        self.button2.config(state='normal')
        self.button3.config(state='normal')
        self.button4.config(state='normal')
        self.button5.config(state='normal')
        self.send_button.config(state='normal')

    def display_system_message(self, message):
        self.response_text_area.config(state=tk.NORMAL)
        self.response_text_area.insert(tk.END, f"[Системное сообщение]: {message}\n")
        self.response_text_area.config(state=tk.DISABLED)
        self.response_text_area.see(tk.END)

    def update_com_ports(self):
        ports = serial.tools.list_ports.comports()
        port_names = [f"{port.device} ({port.description})" for port in ports]
        self.port_combo['values'] = port_names
        default_port = "COM13"
        if any(default_port in name for name in port_names):
            self.port.set(default_port)
        elif ports:
            self.port.set(ports[0].device)
        else:
            self.port.set("")
        if self.is_connected.get():
            self.disconnect_port()
            self.connect_button.config(text="Подключиться", command=self.toggle_connection)
            self.is_connected.set(False)
            self.disable_command_buttons()

    def on_port_selected(self, event):
        selected_item = self.port_combo.get()
        port_name = selected_item.split(' ')[0]
        self.port.set(port_name)
        if self.is_connected.get():
            self.disconnect_port()
            self.connect_button.config(text="Подключиться", command=self.toggle_connection)
            self.is_connected.set(False)
            self.disable_command_buttons()

    def toggle_connection(self):
        if self.is_connected.get():
            self.disconnect_port()
        else:
            self.connect_port()

    def connect_port(self):
        selected_port = self.port.get()
        baud = self.baudrate
        time = self.timeout
        if not selected_port:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт.")
            return

        try:
            self.serial_connection = serial.Serial(selected_port, baud, timeout=time)
            self.connect_button.config(text="Отключиться", command=self.toggle_connection)
            self.is_connected.set(True)
            self.enable_command_buttons()
            self.display_system_message(f"Успешно подключено к {selected_port} на скорости {baud} бод")
            self.start_receive_thread() # Запускаем поток для чтения данных
        except serial.SerialException as e:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к {selected_port}: {e}")
            self.serial_connection = None
            self.is_connected.set(False)
            self.disable_command_buttons()

    def disconnect_port(self):
        if self.is_connected.get():
            self.stop_receive_thread() # Останавливаем поток чтения
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    self.serial_connection.close()
                    self.serial_connection = None
                    self.connect_button.config(text="Подключиться", command=self.toggle_connection)
                    self.is_connected.set(False)
                    self.disable_command_buttons()
                    self.display_system_message(f"Успешно отключено от {self.port.get()}")
                except Exception as e:
                    messagebox.showerror("Ошибка отключения", f"Ошибка при отключении от порта: {e}")
            else:
                self.connect_button.config(text="Подключиться", command=self.toggle_connection)
                self.is_connected.set(False)
                self.disable_command_buttons()

    def start_receive_thread(self):
        self.stop_reading.clear()
        self.receive_thread = threading.Thread(target=self.read_serial_data, daemon=True)
        self.receive_thread.start()

    def stop_receive_thread(self):
        self.stop_reading.set()
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0) # Даем потоку время на завершение

    def read_serial_data(self):
        if self.serial_connection:
            while not self.stop_reading.is_set() and self.serial_connection.is_open:
                try:
                    if self.serial_connection.in_waiting > 0:
                        data = self.serial_connection.read(self.serial_connection.in_waiting)
                        decoded_data = data.decode(errors='ignore')
                        self.display_received_data(decoded_data)
                    time.sleep(0.1) # Небольшая задержка, чтобы не загружать процессор
                except serial.SerialException as e:
                    self.display_system_message(f"Ошибка при чтении данных с порта: {e}")
                    self.disconnect_port()
                    break
                except Exception as e:
                    self.display_system_message(f"Неожиданная ошибка в потоке чтения: {e}")
                    self.disconnect_port()
                    break

    def display_received_data(self, data):
        self.response_text_area.config(state=tk.NORMAL)
        self.response_text_area.insert(tk.END, f"[Получено]: {data}")
        self.response_text_area.config(state=tk.DISABLED)
        self.response_text_area.see(tk.END)

    def send_at_command(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return

        command = self.at_command.get()
        if not command:
            messagebox.showerror("Ошибка", "Пожалуйста, введите AT команду.")
            return

        self._send_command(command)

    def send_command_1(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return
        command = "ATI"
        self._send_command(command)

    def send_command_2(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_3(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_4(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_5(self):
        if not self.is_connected.get() or not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Ошибка", "Порт не подключен.")
            return
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def _send_command(self, command):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(f"{command}\r\n".encode())
                response = self.serial_connection.read(1024).decode(errors='ignore').strip()
                self.display_response(response)
            except serial.SerialException as e:
                messagebox.showerror("Ошибка записи/чтения", f"Ошибка при отправке/получении данных: {e}")
                self.disconnect_port()
        else:
            messagebox.showerror("Ошибка", "Порт не подключен.")

    def display_response(self, response):
        self.response_text_area.config(state=tk.NORMAL)
        self.response_text_area.insert(tk.END, f"[Ответ]: {response}\n")
        self.response_text_area.config(state=tk.DISABLED)
        self.response_text_area.see(tk.END)

    def clear_output(self):
        self.response_text_area.config(state=tk.NORMAL)
        self.response_text_area.delete("1.0", tk.END)
        self.response_text_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ATCommandSender(root)
    root.mainloop()