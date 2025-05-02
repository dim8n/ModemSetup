import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports

class ATCommandSender:
    def __init__(self, master):
        self.master = master
        master.title("AT Command Sender")

        self.port = tk.StringVar()
        self.baudrate = tk.IntVar(value=115200)
        self.timeout = tk.DoubleVar(value=1.0)
        self.at_command = tk.StringVar()

        self.create_widgets()
        self.update_com_ports()

    def create_widgets(self):
        # Выбор COM-порта
        ttk.Label(self.master, text="COM порт:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.port_combo = ttk.Combobox(self.master, textvariable=self.port)
        self.port_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.port_combo.bind("<<ComboboxSelected>>", self.on_port_selected) # Добавим обработчик выбора
        ttk.Button(self.master, text="Обновить порты", command=self.update_com_ports).grid(row=0, column=2, padx=5, pady=5)

        # Скорость передачи (baudrate)
        ttk.Label(self.master, text="Скорость (бод):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        baudrate_entry = ttk.Entry(self.master, textvariable=self.baudrate)
        baudrate_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Тайм-аут
        ttk.Label(self.master, text="Тайм-аут (сек):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        timeout_entry = ttk.Entry(self.master, textvariable=self.timeout)
        timeout_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Ввод AT-команды
        ttk.Label(self.master, text="AT команда:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        at_command_entry = ttk.Entry(self.master, textvariable=self.at_command)
        at_command_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        # Кнопки предустановленных команд
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.button1 = ttk.Button(button_frame, text="ATI", command=self.send_command_1).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button2 = ttk.Button(button_frame, text="2", command=self.send_command_2).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button3 = ttk.Button(button_frame, text="3", command=self.send_command_3).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button4 = ttk.Button(button_frame, text="4", command=self.send_command_4).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.button5 = ttk.Button(button_frame, text="5", command=self.send_command_5).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Кнопка отправки произвольной команды
        send_button = ttk.Button(self.master, text="Отправить", command=self.send_at_command)
        send_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

        # Область для отображения ответа
        self.response_text_area = scrolledtext.ScrolledText(self.master, wrap=tk.WORD, height=10)
        self.response_text_area.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        self.response_text_area.config(state=tk.DISABLED) # Сделаем поле только для чтения

        # Кнопка очистки вывода
        clear_button = ttk.Button(self.master, text="Очистить вывод", command=self.clear_output)
        clear_button.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        # Конфигурация сетки для растягивания элементов
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_rowconfigure(6, weight=1)

    def update_com_ports(self):
        ports = serial.tools.list_ports.comports()
        port_names = [f"{port.device} ({port.description})" for port in ports]
        self.port_combo['values'] = port_names
        default_port = "COM13"
        if any(default_port in name for name in port_names):
            self.port.set(default_port)
        elif ports:
            # По умолчанию устанавливаем только имя устройства
            self.port.set(ports[0].device)
        else:
            self.port.set("")

    def on_port_selected(self, event):
        selected_item = self.port_combo.get()
        # Извлекаем только имя устройства (до первой скобки)
        port_name = selected_item.split(' ')[0]
        self.port.set(port_name)

    def send_at_command(self):
        selected_port = self.port.get()
        baud = self.baudrate.get()
        time = self.timeout.get()
        command = self.at_command.get()

        if not selected_port:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт.")
            return

        if not command:
            messagebox.showerror("Ошибка", "Пожалуйста, введите AT команду.")
            return

        self._send_command(command)

    def send_command_1(self):
        command = "ATI"  # Команда для первой кнопки
        self._send_command(command)

    def send_command_2(self):
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_3(self):
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_4(self):
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def send_command_5(self):
        command = "" # Добавьте свою команду здесь
        self._send_command(command)

    def _send_command(self, command):
        selected_port = self.port.get()
        baud = self.baudrate.get()
        time = self.timeout.get()

        if not selected_port:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите COM порт.")
            return

        try:
            ser = serial.Serial(selected_port, baud, timeout=time)
            ser.write(f"{command}\r\n".encode())  # Добавляем \r\n и кодируем в байты
            response = ser.read(1024).decode(errors='ignore').strip() # Читаем ответ и декодируем
            ser.close()
            self.display_response(response)
        except serial.SerialException as e:
            messagebox.showerror("Ошибка порта", f"Ошибка при работе с портом {selected_port}: {e}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

    def display_response(self, response):
        self.response_text_area.config(state=tk.NORMAL) # Включаем редактирование
        self.response_text_area.insert(tk.END, response + "\n")
        self.response_text_area.config(state=tk.DISABLED) # Снова делаем только для чтения
        self.response_text_area.see(tk.END) # Прокручиваем вниз

    def clear_output(self):
        self.response_text_area.config(state=tk.NORMAL)
        self.response_text_area.delete("1.0", tk.END)
        self.response_text_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = ATCommandSender(root)
    root.mainloop()