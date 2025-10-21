"""
設定ウィンドウモジュール
"""
import tkinter as tk
from tkinter import ttk

class SettingsWindow:
    def __init__(self, parent_app):
        """
        設定ウィンドウを初期化

        Args:
            parent_app: VolumeControlAppのインスタンス
        """
        self.parent_app = parent_app
        self.window = None
        self.audio_devices = []
        self.selected_device_id = None

    def show(self):
        """設定ウィンドウを表示"""
        # 既にウィンドウが開いている場合は前面に表示
        if self.window and self.window.winfo_exists():
            self.window.lift()
            self.window.focus_force()
            return

        # 新しいウィンドウを作成
        self.window = tk.Toplevel()
        self.window.title("設定 - SoundMaster")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        # ウィンドウを中央に配置
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- 音声デバイス設定 ---
        device_frame = ttk.LabelFrame(main_frame, text="音声デバイス設定", padding="10")
        device_frame.pack(fill=tk.X, pady=(0, 15))

        # 音声デバイス選択
        device_select_frame = ttk.Frame(device_frame)
        device_select_frame.pack(fill=tk.X, pady=5)
        ttk.Label(device_select_frame, text="出力デバイス:", width=15).pack(side=tk.LEFT)

        # デバイス一覧を取得
        self.audio_devices = self.parent_app.volume_control.get_audio_devices()

        # 保存されたデバイスIDを取得
        saved_device_id = self.parent_app.config_manager.get("selected_device_id")

        # デバイス名のリストを作成
        device_names = []
        selected_index = 0
        for i, device in enumerate(self.audio_devices):
            name = device["name"]
            if device["is_default"]:
                name += " (デフォルト)"
                if not saved_device_id:  # 保存されたデバイスIDがない場合はデフォルトを選択
                    selected_index = i
            if saved_device_id and device["id"] == saved_device_id:
                selected_index = i
            device_names.append(name)

        # コンボボックスを作成
        self.device_var = tk.StringVar(value=device_names[selected_index] if device_names else "")
        device_combo = ttk.Combobox(
            device_select_frame,
            textvariable=self.device_var,
            values=device_names,
            state="readonly",
            width=40
        )
        device_combo.pack(side=tk.LEFT, padx=5)
        device_combo.current(selected_index)

        # 選択されたデバイスのIDを保存
        if self.audio_devices and len(self.audio_devices) > selected_index:
            self.selected_device_id = self.audio_devices[selected_index]["id"]

        # デバイス選択時のコールバック
        def on_device_select(event):
            selected_index = device_combo.current()
            if 0 <= selected_index < len(self.audio_devices):
                self.selected_device_id = self.audio_devices[selected_index]["id"]

        device_combo.bind("<<ComboboxSelected>>", on_device_select)

        # --- ホットキー設定 ---
        hotkey_frame = ttk.LabelFrame(main_frame, text="ホットキー設定", padding="10")
        hotkey_frame.pack(fill=tk.X, pady=(0, 15))

        # F23キー（音量ダウン）
        f23_frame = ttk.Frame(hotkey_frame)
        f23_frame.pack(fill=tk.X, pady=5)
        ttk.Label(f23_frame, text="音量を下げる:", width=15).pack(side=tk.LEFT)
        ttk.Label(f23_frame, text="F23キー", foreground="gray").pack(side=tk.LEFT)

        # F24キー（音量アップ）
        f24_frame = ttk.Frame(hotkey_frame)
        f24_frame.pack(fill=tk.X, pady=5)
        ttk.Label(f24_frame, text="音量を上げる:", width=15).pack(side=tk.LEFT)
        ttk.Label(f24_frame, text="F24キー", foreground="gray").pack(side=tk.LEFT)

        # --- 音量調整設定 ---
        volume_frame = ttk.LabelFrame(main_frame, text="音量調整", padding="10")
        volume_frame.pack(fill=tk.X, pady=(0, 15))

        # 音量ステップ
        step_frame = ttk.Frame(volume_frame)
        step_frame.pack(fill=tk.X, pady=5)
        ttk.Label(step_frame, text="音量変更ステップ:", width=15).pack(side=tk.LEFT)

        # 保存された設定を読み込む
        saved_volume_step = self.parent_app.config_manager.get("volume_step", 2)
        self.volume_step_var = tk.IntVar(value=saved_volume_step)
        step_spinbox = ttk.Spinbox(
            step_frame,
            from_=1,
            to=10,
            textvariable=self.volume_step_var,
            width=10
        )
        step_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(step_frame, text="%").pack(side=tk.LEFT)

        # --- 通知設定 ---
        notification_frame = ttk.LabelFrame(main_frame, text="通知設定", padding="10")
        notification_frame.pack(fill=tk.X, pady=(0, 15))

        # 通知表示時間
        duration_frame = ttk.Frame(notification_frame)
        duration_frame.pack(fill=tk.X, pady=5)
        ttk.Label(duration_frame, text="通知表示時間:", width=15).pack(side=tk.LEFT)

        # 保存された設定を読み込む
        saved_notification_duration = self.parent_app.config_manager.get("notification_duration", 700)
        self.notification_duration_var = tk.IntVar(value=saved_notification_duration)
        duration_spinbox = ttk.Spinbox(
            duration_frame,
            from_=300,
            to=3000,
            increment=100,
            textvariable=self.notification_duration_var,
            width=10
        )
        duration_spinbox.pack(side=tk.LEFT, padx=5)
        ttk.Label(duration_frame, text="ミリ秒").pack(side=tk.LEFT)

        # --- アプリケーション情報 ---
        info_frame = ttk.LabelFrame(main_frame, text="アプリケーション情報", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))

        info_text = "SoundMaster v1.0\nWindows音量制御ツール"
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # --- ボタン ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        save_button = ttk.Button(
            button_frame,
            text="保存",
            command=self.save_settings
        )
        save_button.pack(side=tk.RIGHT, padx=5)

        cancel_button = ttk.Button(
            button_frame,
            text="キャンセル",
            command=self.window.destroy
        )
        cancel_button.pack(side=tk.RIGHT)

        # ウィンドウを最前面に
        self.window.lift()
        self.window.focus_force()

    def save_settings(self):
        """設定を保存"""
        volume_step = self.volume_step_var.get()
        notification_duration = self.notification_duration_var.get()

        print(f"[設定] 音量ステップ: {volume_step}%")
        print(f"[設定] 通知表示時間: {notification_duration}ms")

        # 音声デバイスの切り替え
        if self.selected_device_id:
            print(f"[設定] 音声デバイス: {self.selected_device_id}")
            self.parent_app.volume_control.set_audio_device(self.selected_device_id)

        # 設定をファイルに保存
        self.parent_app.config_manager.update({
            "volume_step": volume_step,
            "notification_duration": notification_duration,
            "selected_device_id": self.selected_device_id
        })
        self.parent_app.config_manager.save_config()

        # TODO: 設定を実際に適用する処理を追加
        # self.parent_app.volume_control.set_volume_step(volume_step)
        # self.parent_app.ui_manager.set_notification_duration(notification_duration)

        self.window.destroy()
