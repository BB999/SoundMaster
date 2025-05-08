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
        self._current_window = None
        self._window_lock = threading.Lock()

    def show_volume_notification(self, volume_level: int, is_up: bool):
        # tkinterで通知バーを表示
        self._display_notification(volume_level)

    def _display_notification(self, volume_level: int):
        def show():
            def close_and_reset(win):
                with self._window_lock:
                    if self._current_window == win:
                        self._current_window = None
                    win.destroy()
            with self._window_lock:
                if self._current_window is not None and self._current_window.winfo_exists():
                    try:
                        self._current_window.percent_label.config(text=f"{volume_level}%")
                        self._current_window.icon_label.config(text="🔊")
                        if hasattr(self._current_window, 'close_timer') and self._current_window.close_timer is not None:
                            self._current_window.after_cancel(self._current_window.close_timer)
                        self._current_window.close_timer = self._current_window.after(700, lambda win=self._current_window: close_and_reset(win))
                    except Exception:
                        pass
                    return
                root = tk.Tk()
                root.overrideredirect(True)
                root.attributes('-topmost', True)
                root.attributes('-alpha', 0.85)
                bg_color = '#232323'
                accent_color = '#4cd964'
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                window_width = 220
                window_height = 150
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                root.geometry(f"{window_width}x{window_height}+{x}+{y}")
                root.configure(bg=bg_color)
                icon_label = tk.Label(root, text="🔊", font=("Segoe UI Emoji", 40), fg=accent_color, bg=bg_color)
                icon_label.place(relx=0.5, rely=0.18, anchor='center')
                percent_label = tk.Label(
                    root,
                    text=f"{volume_level}%",
                    font=("Segoe UI", 44, "bold"),
                    fg=accent_color,
                    bg=bg_color
                )
                percent_label.place(relx=0.5, rely=0.62, anchor='center')
                root.percent_label = percent_label
                root.icon_label = icon_label
                root.close_timer = root.after(700, lambda win=root: close_and_reset(win))
                root.protocol("WM_DELETE_WINDOW", lambda win=root: close_and_reset(win))
                self._current_window = root
            root.mainloop()
        threading.Thread(target=show, daemon=True).start()

    def stop(self):
        self.is_running = False
        self.tray.stop()

    def check_events(self):
        return self.is_running

    def close(self):
        self.tray.stop()