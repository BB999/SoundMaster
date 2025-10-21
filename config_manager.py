"""
設定管理モジュール
"""
import json
import os

class ConfigManager:
    def __init__(self, config_file="settings.json"):
        """
        設定マネージャーを初期化

        Args:
            config_file: 設定ファイルのパス
        """
        self.config_file = config_file
        self.default_config = {
            "volume_step": 2,
            "notification_duration": 700,
            "selected_device_id": None
        }
        self.config = self.load_config()

    def load_config(self):
        """設定をファイルから読み込む"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"[設定] 設定ファイルを読み込みました: {self.config_file}")
                    return {**self.default_config, **config}  # デフォルト設定とマージ
            except Exception as e:
                print(f"[設定] 設定ファイルの読み込みエラー: {e}")
                return self.default_config.copy()
        else:
            print(f"[設定] 設定ファイルが見つかりません。デフォルト設定を使用します。")
            return self.default_config.copy()

    def save_config(self):
        """設定をファイルに保存する"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
                print(f"[設定] 設定ファイルを保存しました: {self.config_file}")
        except Exception as e:
            print(f"[設定] 設定ファイルの保存エラー: {e}")

    def get(self, key, default=None):
        """設定値を取得する"""
        return self.config.get(key, default)

    def set(self, key, value):
        """設定値を更新する"""
        self.config[key] = value

    def update(self, updates):
        """複数の設定値を一度に更新する"""
        self.config.update(updates)
