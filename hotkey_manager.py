from pynput import keyboard
from threading import Thread, Event
from typing import Callable, Dict, Optional

def log(message):
    print(f"⌨️ {message}")

class HotkeyManager:
    def __init__(self):
        log("ホットキーマネージャーを初期化中...")
        self._listener: Optional[keyboard.Listener] = None
        self._callbacks: Dict[str, Callable] = {}
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        log("✅ ホットキーマネージャーの初期化が完了しました")

    def start(self):
        if self._thread is not None:
            log("⚠️ ホットキーリスナーは既に実行中です")
            return

        log("▶️ ホットキーリスナーを開始します")
        self._listener = keyboard.Listener(on_press=self._on_key_press)
        self._thread = Thread(target=self._listener.start, daemon=True)
        self._thread.start()
        log("✅ ホットキーリスナーが開始されました")

    def stop(self):
        if self._listener:
            log("🛑 ホットキーリスナーを停止します")
            self._stop_event.set()
            self._listener.stop()
            if self._thread:
                self._thread.join()
            self._listener = None
            self._thread = None
            self._callbacks.clear()
            log("✅ ホットキーリスナーが停止しました")

    def register_hotkey(self, key: str, callback: Callable):
        log(f"🔑 ホットキー '{key}' を登録します")
        self._callbacks[key] = callback
        log(f"✅ ホットキー '{key}' の登録が完了しました")

    def unregister_hotkey(self, key: str):
        if key in self._callbacks:
            log(f"🔑 ホットキー '{key}' を登録解除します")
            del self._callbacks[key]
            log(f"✅ ホットキー '{key}' の登録解除が完了しました")

    def _on_key_press(self, key):
        if self._stop_event.is_set():
            return False

        try:
            # キーの詳細情報をログに出力
            log(f"キーが押されました: {key}")
            
            # キー名で判定
            if hasattr(key, 'name'):
                if key.name == 'f23':
                    log("🔑 F23キーが押されました")
                    if 'F23' in self._callbacks:
                        self._callbacks['F23']()
                elif key.name == 'f24':
                    log("🔑 F24キーが押されました")
                    if 'F24' in self._callbacks:
                        self._callbacks['F24']()
            # 仮想キーコードで判定
            elif hasattr(key, 'vk'):
                log(f"仮想キーコード: 0x{key.vk:02X}")
                if key.vk == 0x86:  # F23
                    log("🔑 F23キーが押されました")
                    if 'F23' in self._callbacks:
                        self._callbacks['F23']()
                elif key.vk == 0x87:  # F24
                    log("🔑 F24キーが押されました")
                    if 'F24' in self._callbacks:
                        self._callbacks['F24']()
        except Exception as e:
            log(f"❌ キー処理中にエラーが発生しました: {e}")

        return True

    def __del__(self):
        self.stop()