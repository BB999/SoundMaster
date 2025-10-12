"""
システムトレイアイコン用のICOファイルを生成するスクリプト
"""
from PIL import Image
import os
import sys
import codecs

# Windows環境で絵文字を表示するためのエンコーディング設定
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_icon():
    # 入力ファイルパス
    input_path = os.path.join('resources', 'keyboard_icon.png')
    output_path = os.path.join('resources', 'app_icon.ico')

    print(f"[入力] {input_path}")
    print(f"[出力] {output_path}")

    # 画像を開く
    img = Image.open(input_path)
    print(f"[OK] 画像を読み込みました: {img.size}")

    # 透過対応のためRGBAに変換
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        print("[OK] RGBAモードに変換しました")

    # 複数サイズのICOファイルを生成
    # Windows システムトレイ用: 16x16, 32x32, 48x48, 64x64
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]

    print(f"[処理中] {len(sizes)}種類のサイズでICOファイルを生成中...")
    print(f"   サイズ: {', '.join([f'{w}x{h}' for w, h in sizes])}")

    # ICOファイルとして保存
    img.save(output_path, format='ICO', sizes=sizes)

    print(f"[OK] ICOファイルを生成しました: {output_path}")

    # ファイルサイズを確認
    file_size = os.path.getsize(output_path)
    print(f"[情報] ファイルサイズ: {file_size / 1024:.2f} KB")

    # 各サイズのプレビューPNGも生成（確認用）
    print("\n[処理中] プレビュー画像を生成中...")
    for size in sizes:
        preview_img = img.resize(size, Image.Resampling.LANCZOS)
        preview_path = os.path.join('resources', f'preview_{size[0]}x{size[1]}.png')
        preview_img.save(preview_path)
        print(f"   [OK] {preview_path}")

    print("\n[完了] アイコンファイルの生成が完了しました!")

if __name__ == '__main__':
    create_icon()
