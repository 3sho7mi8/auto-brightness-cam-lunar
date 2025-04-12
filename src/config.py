"""
アプリケーション設定の読み込みと検証を行うモジュール
"""
import os
import json
from dataclasses import dataclass
from typing import Optional
from .logger import logger

# --- デフォルト設定値 ---
DEFAULT_MIN_BRIGHTNESS = 35
DEFAULT_MAX_BRIGHTNESS = 80
DEFAULT_CAPTURE_DURATION = 1
CONFIG_FILE = 'config.json'

@dataclass
class BrightnessConfig:
    """輝度設定を保持するデータクラス"""
    min_brightness: int = DEFAULT_MIN_BRIGHTNESS
    max_brightness: int = DEFAULT_MAX_BRIGHTNESS
    capture_duration: float = DEFAULT_CAPTURE_DURATION
    
    def validate(self) -> 'BrightnessConfig':
        """
        設定値の検証と修正を行う
        
        Returns:
            BrightnessConfig: 検証済みの設定
        """
        # 値の範囲を確認（0-100の間にクランプ）
        self.min_brightness = max(0, min(100, self.min_brightness))
        self.max_brightness = max(0, min(100, self.max_brightness))
        
        # min < maxを保証
        if self.min_brightness > self.max_brightness:
            logger.warning(
                f"設定の最小輝度({self.min_brightness})が最大輝度({self.max_brightness})より"
                "大きいため、値を入れ替えます。"
            )
            self.min_brightness, self.max_brightness = self.max_brightness, self.min_brightness
            
        # キャプチャ時間の検証（最小値を保証）
        self.capture_duration = max(0.1, self.capture_duration)
        
        return self

def load_config(config_path: Optional[str] = None) -> BrightnessConfig:
    """
    設定ファイルを読み込み、BrightnessConfigオブジェクトを返す
    
    Args:
        config_path (str, optional): 設定ファイルへのパス
        
    Returns:
        BrightnessConfig: 読み込まれた設定
    """
    # デフォルト設定オブジェクトを作成
    config = BrightnessConfig()
    
    # 設定ファイルのパスを決定
    config_file = config_path or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        CONFIG_FILE
    )
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # 設定ファイルの値でオブジェクトを更新
            if 'min_brightness' in user_config:
                config.min_brightness = int(user_config['min_brightness'])
                
            if 'max_brightness' in user_config:
                config.max_brightness = int(user_config['max_brightness'])
                
            if 'capture_duration' in user_config:
                config.capture_duration = float(user_config['capture_duration'])
                
            logger.info(f"設定ファイル '{config_file}' を読み込みました。")
            
        except json.JSONDecodeError:
            logger.warning(f"設定ファイル '{config_file}' の形式が正しくありません。デフォルト設定を使用します。")
        except Exception as e:
            logger.warning(f"設定ファイル '{config_file}' の読み込み中にエラーが発生しました: {e}")
    else:
        logger.info(f"設定ファイル '{config_file}' が見つかりません。デフォルト設定を使用します。")
    
    # 設定値の検証
    config.validate()
    
    logger.info(f"使用する設定: 最小輝度={config.min_brightness}, 最大輝度={config.max_brightness}, "
               f"キャプチャ時間={config.capture_duration}秒")
    
    return config
