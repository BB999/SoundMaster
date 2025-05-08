from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import sys

def log(message):
    print(f"🔊 {message}")

class VolumeControl:
    def __init__(self):
        log("音量コントロールを初期化中...")
        try:
            devices = AudioUtilities.GetSpeakers()
            log(f"スピーカーデバイス: {devices}")
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            log("✅ 音量コントロールの初期化が完了しました")
        except Exception as e:
            log(f"❌ 初期化エラー: {e}")
            sys.exit(1)
        
    def get_volume(self):
        try:
            volume = round(self.volume.GetMasterVolumeLevelScalar() * 100)
            log(f"📊 現在の音量: {volume}%")
            return volume
        except Exception as e:
            log(f"❌ 音量取得エラー: {e}")
            return 0
    
    def set_volume(self, volume_level):
        try:
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
        try:
            is_muted = self.is_muted()
            log(f"🔇 ミュートを切り替えます: {'ミュート解除' if is_muted else 'ミュート'}")
            result = self.volume.SetMute(not is_muted, None)
            log(f"✅ ミュート切り替え完了 (結果: {result})")
        except Exception as e:
            log(f"❌ ミュート切り替えエラー: {e}")
        
    def is_muted(self):
        try:
            return bool(self.volume.GetMute())
        except Exception as e:
            log(f"❌ ミュート状態取得エラー: {e}")
            return False
        
    def set_mute(self, mute_state):
        try:
            log(f"🔇 ミュートを {'有効' if mute_state else '無効'} に設定します")
            result = self.volume.SetMute(mute_state, None)
            log(f"✅ ミュート設定完了 (結果: {result})")
        except Exception as e:
            log(f"❌ ミュート設定エラー: {e}")