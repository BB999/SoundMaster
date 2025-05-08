import pystray
import threading
import time
from PIL import Image
import os
from volume_control import VolumeControl
import tkinter as tk
from tkinter import ttk
from queue import Queue, Empty

class UIManager:
    def __init__(self, volume_control: VolumeControl):
        self.volume_control = volume_control
        self.is_running = True
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_path, 'resources', 'app_icon.png')
        self.icon = Image.open(self.icon_path)
        self.menu = pystray.Menu(
            pystray.MenuItem('終了', self.stop)
        )
        self.tray = pystray.Icon('volume_control', self.icon, '音量コントロール', self.menu)
        threading.Thread(target=self.tray.run, daemon=True).start()
        # 通知UI用のキューとスレッド
        self._notify_queue = Queue()
        self._ui_thread = threading.Thread(target=self._notification_ui_loop, daemon=True)
        self._ui_thread.start()

    def show_volume_notification(self, volume_level: int, is_up: bool):
        self._notify_queue.put(volume_level)

    def _notification_ui_loop(self):
        root = tk.Tk()
        root.withdraw()
        self._current_window = None
        self._close_timer = None
        def show_notification(volume_level):
            accent_color = '#ffffff'
            bg_color = '#232323'
            def close_and_reset():
                if self._current_window is not None and self._current_window.winfo_exists():
                    self._current_window.destroy()
                self._current_window = None
            if self._current_window is not None and self._current_window.winfo_exists():
                self._current_window.percent_label.config(text=f"{volume_level}%", fg=accent_color)
                self._current_window.icon_label.config(text="🔊", fg=accent_color)
                if self._close_timer is not None:
                    self._current_window.after_cancel(self._close_timer)
                self._close_timer = self._current_window.after(700, close_and_reset)
                self._current_window.protocol("WM_DELETE_WINDOW", close_and_reset)
            else:
                win = tk.Toplevel(root)
                win.overrideredirect(True)
                win.attributes('-topmost', True)
                win.attributes('-alpha', 0.85)
                window_width = 220
                window_height = 150
                screen_width = win.winfo_screenwidth()
                screen_height = win.winfo_screenheight()
                x = (screen_width - window_width) // 2
                y = (screen_height - window_height) // 2
                win.geometry(f"{window_width}x{window_height}+{x}+{y}")
                win.configure(bg=bg_color)
                icon_label = tk.Label(win, text="🔊", font=("Segoe UI Emoji", 40), fg=accent_color, bg=bg_color)
                icon_label.place(relx=0.5, rely=0.18, anchor='center')
                percent_label = tk.Label(
                    win,
                    text=f"{volume_level}%",
                    font=("Segoe UI", 44, "bold"),
                    fg=accent_color,
                    bg=bg_color
                )
                percent_label.place(relx=0.5, rely=0.62, anchor='center')
                win.percent_label = percent_label
                win.icon_label = icon_label
                self._close_timer = win.after(700, close_and_reset)
                win.protocol("WM_DELETE_WINDOW", close_and_reset)
                self._current_window = win
        def poll_queue():
            try:
                while True:
                    volume_level = self._notify_queue.get_nowait()
                    show_notification(volume_level)
            except Empty:
                pass
            root.after(50, poll_queue)
        poll_queue()
        root.mainloop()

    def stop(self):
        self.is_running = False
        self.tray.stop()

    def check_events(self):
        return self.is_running

    def close(self):
        self.tray.stop()