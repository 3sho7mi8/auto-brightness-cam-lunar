"""
Lunar CLIを使用してディスプレイの輝度を制御するモジュール
"""
import subprocess
from typing import Tuple, Optional, Dict, List, Any
from .logger import logger

class LunarController:
    """Lunar CLIを使用してディスプレイの輝度を制御するクラス"""
    
    def __init__(self, command_path: str = 'lunar'):
        """
        LunarControllerを初期化
        
        Args:
            command_path (str): lunar コマンドのパス
        """
        self.command_path = command_path
    
    def set_brightness(self, brightness_level: float) -> bool:
        """
        ディスプレイの輝度を設定する
        
        Args:
            brightness_level (float): 設定する輝度レベル（0-100の範囲）
            
        Returns:
            bool: 操作が成功したかどうか
        """
        # 輝度レベルを 0-100 の整数値にクランプする
        brightness = max(0, min(100, int(brightness_level)))
        
        logger.info(f"ディスプレイの輝度を {brightness}% に設定します...")
        
        try:
            # Lunar CLI コマンドを実行
            command = [self.command_path, 'set', 'brightness', str(brightness)]
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            logger.debug(f"Lunar CLI の出力: {result.stdout.strip()}")
            logger.info(f"ディスプレイの輝度を {brightness}% に正常に設定しました。")
            return True
            
        except FileNotFoundError:
            logger.error(
                f"'{self.command_path}' コマンドが見つかりません。" 
                "Lunar CLIがインストールされているか、またはPATHが正しく設定されているか確認してください。"
            )
            return False
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Lunar CLI の実行に失敗しました。コマンド: {' '.join(e.cmd)}")
            logger.error(f"リターンコード: {e.returncode}")
            if e.stderr:
                logger.error(f"エラー出力: {e.stderr}")
            return False
            
        except Exception as e:
            logger.error(f"予期せぬエラーが発生しました: {e}")
            return False
    
    def get_current_brightness(self) -> Optional[float]:
        """
        現在のディスプレイの輝度を取得する
        
        Returns:
            Optional[float]: 現在の輝度レベル（0-100の範囲）、またはエラー時にNone
        """
        try:
            command = [self.command_path, 'get', 'brightness']
            result = subprocess.run(
                command, 
                check=True, 
                capture_output=True, 
                text=True
            )
            
            brightness_str = result.stdout.strip()
            
            # 出力からパーセンテージ値を抽出
            try:
                # '%'記号がある場合は削除してfloatに変換
                brightness = float(brightness_str.replace('%', '').strip())
                logger.debug(f"現在のディスプレイ輝度: {brightness}%")
                return brightness
            except ValueError:
                logger.error(f"輝度値の解析に失敗しました: '{brightness_str}'")
                return None
                
        except Exception as e:
            logger.error(f"現在の輝度を取得する際にエラーが発生しました: {e}")
            return None


def set_display_brightness(brightness_level: float) -> bool:
    """
    ディスプレイの輝度を設定する便利な関数
    
    Args:
        brightness_level (float): 設定する輝度レベル（0-100の範囲）
        
    Returns:
        bool: 操作が成功したかどうか
    """
    controller = LunarController()
    return controller.set_brightness(brightness_level)
