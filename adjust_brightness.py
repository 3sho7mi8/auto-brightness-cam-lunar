import cv2
import numpy as np
import subprocess
import time
import sys
import json
import os

# --- デフォルト設定値 ---
DEFAULT_MIN_BRIGHTNESS = 35
DEFAULT_MAX_BRIGHTNESS = 80
CONFIG_FILE = 'config.json'
# --- デフォルト設定値ここまで ---

def load_config():
    """設定ファイル (config.json) を読み込む"""
    config = {
        'min_brightness': DEFAULT_MIN_BRIGHTNESS,
        'max_brightness': DEFAULT_MAX_BRIGHTNESS
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
                # 設定ファイルの値でデフォルト値を上書き
                config['min_brightness'] = int(user_config.get('min_brightness', DEFAULT_MIN_BRIGHTNESS))
                config['max_brightness'] = int(user_config.get('max_brightness', DEFAULT_MAX_BRIGHTNESS))
                # 値のバリデーション (0-100の範囲)
                config['min_brightness'] = max(0, min(100, config['min_brightness']))
                config['max_brightness'] = max(0, min(100, config['max_brightness']))
                # min < max の保証
                if config['min_brightness'] > config['max_brightness']:
                    print(f"警告: 設定ファイルの min_brightness ({config['min_brightness']}) が max_brightness ({config['max_brightness']}) より大きいため、値を入れ替えます。", file=sys.stderr)
                    config['min_brightness'], config['max_brightness'] = config['max_brightness'], config['min_brightness']

        except json.JSONDecodeError:
            print(f"警告: {CONFIG_FILE} の形式が正しくありません。デフォルト設定を使用します。", file=sys.stderr)
        except Exception as e:
            print(f"警告: {CONFIG_FILE} の読み込み中にエラーが発生しました ({e})。デフォルト設定を使用します。", file=sys.stderr)
    else:
        print(f"情報: {CONFIG_FILE} が見つかりません。デフォルト設定を使用します。")

    print(f"使用する設定: 最小輝度={config['min_brightness']}, 最大輝度={config['max_brightness']}")
    return config

def get_ambient_light_from_webcam(capture_duration=1):
    """Webカメラから画像を取得し、平均輝度を計算する"""
    # デフォルトのWebカメラを開く
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("エラー: Webカメラを開けませんでした。", file=sys.stderr)
        return None

    # カメラの準備時間を少し待つ
    time.sleep(2)

    start_time = time.time()
    brightness_readings = []

    while time.time() - start_time < capture_duration:
        # フレームを読み込む
        ret, frame = cap.read()

        if not ret:
            print("エラー: フレームを読み取れませんでした。", file=sys.stderr)
            # 少し待ってリトライするか、ループを抜ける
            time.sleep(0.1)
            continue
            # return None # エラー発生時に即時終了する場合

        # フレームをグレースケールに変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 平均輝度を計算 (0-255)
        avg_brightness = np.mean(gray_frame)
        brightness_readings.append(avg_brightness)

        # 短い間隔でキャプチャ（必要に応じて調整）
        # time.sleep(0.1)

    # カメラリソースを解放
    cap.release()

    if not brightness_readings:
        print("エラー: 有効な輝度データを取得できませんでした。", file=sys.stderr)
        return None

    # 期間中の平均輝度を計算
    final_avg_brightness = np.mean(brightness_readings)
    print(f"Webカメラから計算された平均輝度: {final_avg_brightness:.2f}")
    return final_avg_brightness

def set_display_brightness(brightness_level):
    """Lunar CLI を使用してディスプレイの輝度を設定する"""
    # 輝度レベルを 0-100 の範囲にクランプする
    brightness_level = max(0, min(100, int(brightness_level)))
    print(f"ディスプレイの輝度を {brightness_level} に設定します...")

    try:
        # Lunar CLI コマンドを実行
        # 注意: 'lunar' コマンドがPATHに含まれている必要があります。
        # もし特定のパスにある場合は、フルパスを指定してください。
        # 例: '/usr/local/bin/lunar'
        command = ['lunar', 'set', 'brightness', str(brightness_level)]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Lunar CLI の出力:")
        print(result.stdout)
        print("ディスプレイの輝度を正常に設定しました。")
    except FileNotFoundError:
        print(f"エラー: 'lunar' コマンドが見つかりません。PATHを確認してください。", file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"エラー: Lunar CLI の実行に失敗しました。", file=sys.stderr)
        print(f"コマンド: {' '.join(e.cmd)}", file=sys.stderr)
        print(f"リターンコード: {e.returncode}", file=sys.stderr)
        print(f"エラー出力:\n{e.stderr}", file=sys.stderr)
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)

if __name__ == "__main__":
    # 0. 設定ファイルを読み込む
    config = load_config()
    min_brightness_setting = config['min_brightness']
    max_brightness_setting = config['max_brightness']

    # 1. Webカメラから平均輝度を取得
    #    キャプチャ時間を長くすると、より安定した値が得られる可能性があります。
    avg_camera_brightness = get_ambient_light_from_webcam(capture_duration=1) # 1秒間キャプチャ

    if avg_camera_brightness is not None:
        # 2. 輝度を 0-100 のスケールにマッピング
        #    このマッピングは調整が必要かもしれません。
        #    例えば、暗い環境でも最低限の明るさを保つ、
        #    または非常に明るい環境での最大値を制限するなど。
        #    Webカメラ輝度(0-255)を min_brightness_setting から max_brightness_setting の範囲に線形マッピング
        if max_brightness_setting == min_brightness_setting:
             target_brightness = min_brightness_setting # 範囲が0の場合
        else:
             target_brightness = min_brightness_setting + (avg_camera_brightness / 255) * (max_brightness_setting - min_brightness_setting)


        # 計算結果が設定範囲内に収まるように最終調整 (念のため)
        target_brightness = max(min_brightness_setting, min(max_brightness_setting, target_brightness))

        print(f"計算された目標輝度: {target_brightness:.2f}")

        # 3. Lunar CLI でディスプレイ輝度を設定
        set_display_brightness(target_brightness)
    else:
        print("輝度の取得に失敗したため、ディスプレイ輝度の調整をスキップします。")