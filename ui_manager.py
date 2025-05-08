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
            root.overrideredirect(True)  # 枠なし
            root.attributes('-topmost', True)
            root.attributes('-alpha', 0.9)
            # 画面中央に表示
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            window_width = 300
            window_height = 80
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            root.geometry(f"{window_width}x{window_height}+{x}+{y}")
            bar = ttk.Progressbar(root, orient="horizontal", length=250, mode="determinate", maximum=100)
            bar.pack(pady=(15, 5), padx=20)
            bar['value'] = volume_level
            # 音量％ラベル
            percent_label = tk.Label(root, text=f"{volume_level}%", font=("Arial", 14), bg="#f0f0f0")
            percent_label.pack(pady=(0, 10))
            # 1秒後に自動で閉じる
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