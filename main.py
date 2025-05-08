import sys
import signal
from volume_control import VolumeControl
from hotkey_manager import HotkeyManager
from ui_manager import UIManager
import time

def log(message):
    print(f"🔍 {message}")

class VolumeControlApp:
    def __init__(self):
        log("🚀 アプリケーションを初期化中...")
        self.volume_control = VolumeControl()
        self.ui_manager = UIManager(self.volume_control)
        self.hotkey_manager = HotkeyManager()
        
        self.setup_hotkeys()
        self.setup_signal_handlers()
        log("✅ アプリケーションの初期化が完了しました")
        
    def setup_hotkeys(self):
        log("⌨️ ホットキーを設定中...")
        self.hotkey_manager.register_hotkey('F23', self.volume_down)
        self.hotkey_manager.register_hotkey('F24', self.volume_up)
        self.hotkey_manager.start()
        log("✅ ホットキーの設定が完了しました")
        
    def setup_signal_handlers(self):
        log("🛡️ シグナルハンドラーを設定中...")
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        log("✅ シグナルハンドラーの設定が完了しました")
        
    def volume_up(self):
        log("🔊 音量を上げます")
        try:
            self.volume_control.volume_up()
            current_volume = self.volume_control.get_volume()
            log(f"📊 現在の音量: {current_volume}%")
            self.ui_manager.show_volume_notification(current_volume, True)
        except Exception as e:
            log(f"❌ 音量上げエラー: {e}")
        
    def volume_down(self):
        log("🔉 音量を下げます")
        try:
            self.volume_control.volume_down()
            current_volume = self.volume_control.get_volume()
            log(f"📊 現在の音量: {current_volume}%")
            self.ui_manager.show_volume_notification(current_volume, False)
        except Exception as e:
            log(f"❌ 音量下げエラー: {e}")
        
    def run(self):
        log("▶️ アプリケーションを開始します")
        try:
            while self.ui_manager.check_events():
                time.sleep(0.1)
        except Exception as e:
            log(f"❌ エラーが発生しました: {e}")
            self.cleanup()
            
    def cleanup(self, *args):
        log("🛑 アプリケーションを終了します")
        self.hotkey_manager.stop()
        self.ui_manager.close()
        sys.exit(0)

if __name__ == '__main__':
    app = VolumeControlApp()
    app.run()