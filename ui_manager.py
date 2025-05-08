import pystray
import threading
import time
from PIL import Image
import os
from volume_control import VolumeControl
import tkinter as tk
from tkinter import ttk

class UIManager:
    def __init__(self, volume_control: VolumeControl):
        self.volume_control = volume_control
        self.notification_window = None
        self.is_running = True
        # アイコンパスの設定
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_path, 'resources', 'app_icon.png')
        # システムトレイの設定
        self.icon = Image.open(self.icon_path)
        self.menu = pystray.Menu(
            pystray.MenuItem('終了', self.stop)
        )
        self.tray = pystray.Icon('volume_control', self.icon, '音量コントロール', self.menu)
        threading.Thread(target=self.tray.run, daemon=True).start()

    def show_volume_notification(self, volume_level: int, is_up: bool):
        # tkinterで通知バーを表示
        self._display_notification(volume_level)

    def _display_notification(self, volume_level: int):
        def show():
            root = tk.Tk()
            root.overrideredirect(True)
            root.attributes('-topmost', True)
            root.attributes('-alpha', 0.97)
            # Mac風ダーク背景
            bg_color = '#232323'
            accent_color = '#4cd964'
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            window_width = 220
            window_height = 110
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            root.configure(bg=bg_color)
            # 音量％のみを大きく中央に表示
            percent_label = tk.Label(
                root,
                text=f"{volume_level}%",
                font=("Segoe UI", 48, "bold"),
                fg=accent_color,
                bg=bg_color
            )
            percent_label.place(relx=0.5, rely=0.5, anchor='center')
            root.after(1000, root.destroy)
            root.mainloop()
        threading.Thread(target=show, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.tray.stop()

    def check_events(self):
        return self.is_running

    def close(self):
        self.tray.stop()