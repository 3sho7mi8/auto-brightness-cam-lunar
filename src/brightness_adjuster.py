"""
メインのアプリケーションロジックを提供するモジュール
Webカメラの輝度測定値に基づいてLunar CLIでディスプレイの輝度を調整する
"""
from typing import Optional
from .config import BrightnessConfig, load_config
from .camera import measure_ambient_brightness
from .lunar import set_display_brightness
from .logger import logger

class BrightnessAdjuster:
    """
    周囲の明るさに基づいてディスプレイの輝度を自動調整するクラス
    """
    
    def __init__(self, config: Optional[BrightnessConfig] = None):
        """
        BrightnessAdjusterを初期化
        
        Args:
            config (BrightnessConfig, optional): 使用する設定
                指定しない場合は、デフォルトの設定が読み込まれる
        """
        self.config = config or load_config()
    
    def map_brightness(self, ambient_brightness: float) -> float:
        """
        環境光の輝度（0-255）を、設定された最小・最大輝度の範囲にマッピング
        
        Args:
            ambient_brightness (float): 環境光の輝度（0-255の範囲）
            
        Returns:
            float: マッピングされたディスプレイ輝度（0-100の範囲）
        """
        # 最小値と最大値が同じ場合は単純に最小値を返す
        if self.config.min_brightness == self.config.max_brightness:
            return float(self.config.min_brightness)
        
        # 環境光の値（0-255）を設定された範囲にマッピング
        target_brightness = (
            self.config.min_brightness + 
            (ambient_brightness / 255) * 
            (self.config.max_brightness - self.config.min_brightness)
        )
        
        # 結果が設定範囲内に収まるように調整（念のため）
        target_brightness = max(
            self.config.min_brightness, 
            min(self.config.max_brightness, target_brightness)
        )
        
        return target_brightness
    
    def adjust(self) -> bool:
        """
        Webカメラで環境光を測定し、それに基づいてディスプレイの輝度を調整
        
        Returns:
            bool: 調整が成功したかどうか
        """
        # 環境光を測定
        ambient_brightness = measure_ambient_brightness(
            capture_duration=self.config.capture_duration
        )
        
        if ambient_brightness is None:
            logger.error("環境光の測定に失敗したため、輝度調整をスキップします。")
            return False
        
        # 測定値を輝度設定にマッピング
        target_brightness = self.map_brightness(ambient_brightness)
        
        logger.info(f"環境光の輝度: {ambient_brightness:.2f} -> ディスプレイ輝度: {target_brightness:.2f}%")
        
        # ディスプレイの輝度を設定
        success = set_display_brightness(target_brightness)
        
        return success


def main():
    """アプリケーションのメインエントリーポイント"""
    logger.info("Lunar Brightness Adjuster を開始します...")
    
    # 設定を読み込む
    config = load_config()
    
    # 輝度調整を実行
    adjuster = BrightnessAdjuster(config)
    result = adjuster.adjust()
    
    if result:
        logger.info("輝度調整が正常に完了しました。")
    else:
        logger.warning("輝度調整中に問題が発生しました。ログを確認してください。")
    
    logger.info("Lunar Brightness Adjuster を終了します。")
    return 0 if result else 1


if __name__ == "__main__":
    exit(main())
