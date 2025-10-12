from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, COMObject
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, IMMDeviceEnumerator, IMMNotificationClient, EDataFlow, ERole
import sys
import threading

def log(message):
    print(f"🔊 {message}")

class AudioDeviceNotificationClient(COMObject):
    """デバイス変更通知を受け取るためのクライアント"""
    _com_interfaces_ = [IMMNotificationClient]

    def __init__(self, volume_control_instance):
        super().__init__()
        self.volume_control = volume_control_instance
        log("デバイス通知クライアントを初期化しました")

    def OnDefaultDeviceChanged(self, flow, role, device_id):
        """デフォルトデバイスが変更されたときに呼ばれる"""
        try:
            if flow == EDataFlow.eRender.value:  # 再生デバイスの場合のみ
                log(f"🔄 デフォルト再生デバイスが変更されました: {device_id}")
                self.volume_control._reinitialize_device()
        except Exception as e:
            log(f"❌ デバイス変更通知エラー: {e}")

    def OnDeviceAdded(self, device_id):
        """デバイスが追加されたときに呼ばれる"""
        log(f"➕ デバイスが追加されました: {device_id}")

    def OnDeviceRemoved(self, device_id):
        """デバイスが削除されたときに呼ばれる"""
        log(f"➖ デバイスが削除されました: {device_id}")

    def OnDeviceStateChanged(self, device_id, new_state):
        """デバイスの状態が変更されたときに呼ばれる"""
        log(f"🔄 デバイスの状態が変更されました: {device_id}, 新しい状態: {new_state}")

    def OnPropertyValueChanged(self, device_id, key):
        """デバイスのプロパティが変更されたときに呼ばれる"""
        pass  # 必要に応じて実装

class VolumeControl:
    def __init__(self):
        log("音量コントロールを初期化中...")
        self._lock = threading.Lock()
        self.volume = None
        self.device_enumerator = None
        self.notification_client = None

        try:
            # デバイスの初期化
            self._initialize_device()

            # デバイス変更通知の登録
            self._register_device_notifications()

            log("✅ 音量コントロールの初期化が完了しました")
        except Exception as e:
            log(f"❌ 初期化エラー: {e}")
            sys.exit(1)

    def _initialize_device(self):
        """デバイスを初期化する"""
        try:
            devices = AudioUtilities.GetSpeakers()
            log(f"スピーカーデバイス: {devices}")
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            log("✅ デバイスの初期化が完了しました")
        except Exception as e:
            log(f"❌ デバイス初期化エラー: {e}")
            raise

    def _register_device_notifications(self):
        """デバイス変更通知を登録する"""
        try:
            from comtypes import CoCreateInstance, GUID

            # CLSID_MMDeviceEnumeratorを直接定義
            CLSID_MMDeviceEnumerator = GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')

            # デバイス列挙子を取得
            self.device_enumerator = CoCreateInstance(
                CLSID_MMDeviceEnumerator,
                IMMDeviceEnumerator,
                CLSCTX_ALL
            )

            # 通知クライアントを作成して登録
            self.notification_client = AudioDeviceNotificationClient(self)
            self.device_enumerator.RegisterEndpointNotificationCallback(self.notification_client)
            log("✅ デバイス変更通知の登録が完了しました")
        except Exception as e:
            log(f"❌ 通知登録エラー: {e}")
            # 通知登録が失敗しても動作は継続

    def _reinitialize_device(self):
        """デバイスを再初期化する（デバイス変更時に呼ばれる）"""
        with self._lock:
            try:
                log("🔄 デバイスを再初期化しています...")
                # 別スレッドからの呼び出しの場合、COMを初期化
                import comtypes
                comtypes.CoInitialize()
                try:
                    self._initialize_device()
                    log("✅ デバイスの再初期化が完了しました")
                finally:
                    comtypes.CoUninitialize()
            except Exception as e:
                log(f"❌ デバイス再初期化エラー: {e}")
        
    def get_volume(self):
        with self._lock:
            try:
                if self.volume is None:
                    log("⚠️ デバイスが初期化されていません")
                    return 0
                volume = round(self.volume.GetMasterVolumeLevelScalar() * 100)
                log(f"📊 現在の音量: {volume}%")
                return volume
            except Exception as e:
                log(f"❌ 音量取得エラー: {e}")
                return 0
    
    def set_volume(self, volume_level):
        with self._lock:
            try:
                if self.volume is None:
                    log("⚠️ デバイスが初期化されていません")
                    return
                volume_level = max(0, min(100, volume_level))
                log(f"🔊 音量を {volume_level}% に設定します")
                result = self.volume.SetMasterVolumeLevelScalar(volume_level / 100, None)
                log(f"✅ 音量の設定が完了しました (結果: {result})")
            except Exception as e:
                log(f"❌ 音量設定エラー: {e}")
        
    def volume_up(self, step=2):
        try:
            current_volume = self.get_volume()
            new_volume = current_volume + step
            log(f"🔊 音量を上げます: {current_volume}% → {new_volume}%")
            self.set_volume(new_volume)
        except Exception as e:
            log(f"❌ 音量上げエラー: {e}")
        
    def volume_down(self, step=2):
        try:
            current_volume = self.get_volume()
            new_volume = current_volume - step
            log(f"🔊 音量を下げます: {current_volume}% → {new_volume}%")
            self.set_volume(new_volume)
        except Exception as e:
            log(f"❌ 音量下げエラー: {e}")
        
    def toggle_mute(self):
        with self._lock:
            try:
                if self.volume is None:
                    log("⚠️ デバイスが初期化されていません")
                    return
                is_muted = self._is_muted_unsafe()
                log(f"🔇 ミュートを切り替えます: {'ミュート解除' if is_muted else 'ミュート'}")
                result = self.volume.SetMute(not is_muted, None)
                log(f"✅ ミュート切り替え完了 (結果: {result})")
            except Exception as e:
                log(f"❌ ミュート切り替えエラー: {e}")

    def _is_muted_unsafe(self):
        """ロックなしでミュート状態を取得（内部使用専用）"""
        try:
            if self.volume is None:
                return False
            return bool(self.volume.GetMute())
        except Exception as e:
            log(f"❌ ミュート状態取得エラー: {e}")
            return False

    def is_muted(self):
        with self._lock:
            return self._is_muted_unsafe()

    def set_mute(self, mute_state):
        with self._lock:
            try:
                if self.volume is None:
                    log("⚠️ デバイスが初期化されていません")
                    return
                log(f"🔇 ミュートを {'有効' if mute_state else '無効'} に設定します")
                result = self.volume.SetMute(mute_state, None)
                log(f"✅ ミュート設定完了 (結果: {result})")
            except Exception as e:
                log(f"❌ ミュート設定エラー: {e}")

    def cleanup(self):
        """クリーンアップ処理"""
        try:
            if self.notification_client and self.device_enumerator:
                log("🧹 デバイス変更通知の登録を解除しています...")
                self.device_enumerator.UnregisterEndpointNotificationCallback(self.notification_client)
                log("✅ 通知の登録解除が完了しました")
        except Exception as e:
            log(f"❌ クリーンアップエラー: {e}")