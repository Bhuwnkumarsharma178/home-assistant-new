import tkinter as tk
from tkinter import messagebox, simpledialog
import threading
import speech_recognition as sr
import pyttsx3
import requests
import time

# Simulated IoT endpoints (replace with your actual endpoints)
DEVICE_ENDPOINTS = {
    'light': 'http://192.168.1.100/light',
    'fan': 'http://192.168.1.100/fan',
    'door': 'http://192.168.1.100/door',
    'thermostat': 'http://192.168.1.100/thermostat',
    'curtain': 'http://192.168.1.100/curtain',
}

# Initial device states
DEVICE_STATUS = {
    'light': 'off',
    'fan': 'off',
    'door': 'closed',
    'thermostat': '22°C',
    'curtain': 'closed',
}

class FridayAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title('FRIDAY Smart Home Assistant')
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()
        self.status_labels = {}
        self.create_gui()
        self.update_status_labels()
        self.listening = False
        self.voice_thread = threading.Thread(target=self.voice_command_listener, daemon=True)
        self.voice_thread.start()

    def create_gui(self):
        tk.Label(self.root, text='FRIDAY Smart Home Control', font=('Arial', 18, 'bold')).pack(pady=10)
        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=10)
        for idx, device in enumerate(DEVICE_STATUS):
            frame = tk.Frame(status_frame)
            frame.grid(row=idx, column=0, sticky='w', pady=2)
            tk.Label(frame, text=f'{device.capitalize()}:', width=12, anchor='w').pack(side='left')
            lbl = tk.Label(frame, text='', width=10, anchor='w')
            lbl.pack(side='left')
            self.status_labels[device] = lbl
            if device in ['light', 'fan', 'door', 'curtain']:
                btn_on = tk.Button(frame, text='On/Open', command=lambda d=device: self.control_device(d, 'on' if d != 'door' and d != 'curtain' else 'open'))
                btn_on.pack(side='left', padx=2)
                btn_off = tk.Button(frame, text='Off/Close', command=lambda d=device: self.control_device(d, 'off' if d != 'door' and d != 'curtain' else 'close'))
                btn_off.pack(side='left', padx=2)
        # Thermostat control
        tk.Button(self.root, text='Set Thermostat', command=self.set_thermostat).pack(pady=5)
        # Voice command display
        self.voice_label = tk.Label(self.root, text='Say a command...', font=('Arial', 12), fg='blue')
        self.voice_label.pack(pady=10)
        # Start/Stop listening
        self.listen_btn = tk.Button(self.root, text='Start Listening', command=self.toggle_listening)
        self.listen_btn.pack(pady=5)

    def update_status_labels(self):
        for device, lbl in self.status_labels.items():
            lbl.config(text=DEVICE_STATUS[device])
        self.root.after(2000, self.update_status_labels)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
        self.voice_label.config(text=f'FRIDAY: {text}')

    def control_device(self, device, action):
        # Simulate HTTP request to IoT device
        try:
            # Uncomment below to use real endpoints
            # resp = requests.post(DEVICE_ENDPOINTS[device], json={'action': action}, timeout=2)
            # if resp.status_code == 200:
            #     DEVICE_STATUS[device] = action if device != 'thermostat' else resp.json().get('value', DEVICE_STATUS[device])
            # else:
            #     raise Exception('Device error')
            # Simulate device response
            if device == 'thermostat':
                DEVICE_STATUS[device] = action
            elif device == 'door' or device == 'curtain':
                DEVICE_STATUS[device] = 'open' if action == 'open' else 'closed'
            else:
                DEVICE_STATUS[device] = 'on' if action == 'on' else 'off'
            self.speak(f'{device.capitalize()} {"opened" if action == "open" else "closed" if action == "close" else action}')
        except Exception as e:
            self.speak(f'Failed to control {device}.')

    def set_thermostat(self):
        temp = simpledialog.askstring('Thermostat', 'Set temperature (°C):')
        if temp:
            self.control_device('thermostat', f'{temp}°C')

    def toggle_listening(self):
        self.listening = not self.listening
        self.listen_btn.config(text='Stop Listening' if self.listening else 'Start Listening')
        if self.listening:
            self.voice_label.config(text='Listening...')
        else:
            self.voice_label.config(text='Say a command...')

    def voice_command_listener(self):
        while True:
            if self.listening:
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source)
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        command = self.recognizer.recognize_google(audio)
                        if isinstance(command, str):
                            command = command.lower()
                        self.voice_label.config(text=f'You: {command}')
                        self.handle_voice_command(command)
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        self.speak('Sorry, I did not understand.')
                    except Exception as e:
                        self.speak('Error with microphone.')
            time.sleep(0.5)

    def handle_voice_command(self, command):
        # Basic command parsing
        if 'light' in command:
            if 'on' in command:
                self.control_device('light', 'on')
            elif 'off' in command:
                self.control_device('light', 'off')
        elif 'fan' in command:
            if 'on' in command:
                self.control_device('fan', 'on')
            elif 'off' in command:
                self.control_device('fan', 'off')
        elif 'door' in command:
            if 'open' in command:
                self.control_device('door', 'open')
            elif 'close' in command:
                self.control_device('door', 'close')
        elif 'curtain' in command:
            if 'open' in command:
                self.control_device('curtain', 'open')
            elif 'close' in command:
                self.control_device('curtain', 'close')
        elif 'thermostat' in command or 'temperature' in command:
            import re
            match = re.search(r'(\d+)', command)
            if match:
                temp = match.group(1)
                self.control_device('thermostat', f'{temp}°C')
                self.speak(f'Thermostat set to {temp} degrees Celsius.')
            else:
                self.speak('Please specify the temperature.')
        else:
            self.speak('Command not recognized.')

def main():
    root = tk.Tk()
    app = FridayAssistant(root)
    root.mainloop()

if __name__ == '__main__':
    main() 