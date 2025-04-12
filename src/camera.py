"""
Webカメラを使用して周囲の輝度を計測するモジュール
"""
import time
import cv2
import numpy as np
from typing import Optional, List, Tuple
from .logger import logger

class AmbientLightSensor:
    """Webカメラを使用して周囲の輝度を検出するクラス"""
    
    def __init__(self, camera_index: int = 0):
        """
        AmbientLightSensorを初期化
        
        Args:
            camera_index (int): 使用するカメラのインデックス（デフォルト=0）
        """
        self.camera_index = camera_index
        self.camera = None
    
    def __enter__(self):
        """コンテキストマネージャーの開始（カメラを開く）"""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャーの終了（カメラを閉じる）"""
        self.close()
    
    def open(self) -> bool:
        """
        カメラデバイスを開く
        
        Returns:
            bool: カメラが正常に開かれたかどうか
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            
            if not self.camera.isOpened():
                logger.error(f"カメラ（インデックス:{self.camera_index}）を開けませんでした。")
                return False
                
            logger.debug(f"カメラ（インデックス:{self.camera_index}）を開きました。")
            # カメラの準備時間を少し待つ
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"カメラ初期化中にエラーが発生しました: {e}")
            return False
    
    def close(self):
        """カメラリソースを解放する"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            logger.debug("カメラリソースを解放しました。")
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        1フレームをキャプチャする
        
        Returns:
            Optional[np.ndarray]: キャプチャされたフレーム、またはエラー時にNone
        """
        if self.camera is None or not self.camera.isOpened():
            logger.error("カメラが開かれていないため、フレームをキャプチャできません。")
            return None
        
        ret, frame = self.camera.read()
        
        if not ret:
            logger.warning("フレームを読み取れませんでした。")
            return None
        
        return frame
    
    def get_frame_brightness(self, frame: np.ndarray) -> float:
        """
        フレームの平均輝度を計算
        
        Args:
            frame (np.ndarray): 分析するフレーム
            
        Returns:
            float: 平均輝度（0-255の範囲）
        """
        # フレームをグレースケールに変換
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 平均輝度を計算 (0-255)
        avg_brightness = float(np.mean(gray_frame))
        
        return avg_brightness
    
    def measure_ambient_light(self, duration: float = 1.0, 
                             sample_interval: float = 0.1) -> Optional[float]:
        """
        指定された時間にわたって周囲の輝度を測定
        
        Args:
            duration (float): 測定時間（秒）
            sample_interval (float): サンプリング間隔（秒）
            
        Returns:
            Optional[float]: 平均輝度（0-255の範囲）、またはエラー時にNone
        """
        if self.camera is None:
            if not self.open():
                return None
        
        start_time = time.time()
        brightness_readings: List[float] = []
        
        logger.debug(f"{duration}秒間の輝度測定を開始します...")
        
        try:
            while time.time() - start_time < duration:
                frame = self.capture_frame()
                
                if frame is not None:
                    brightness = self.get_frame_brightness(frame)
                    brightness_readings.append(brightness)
                    logger.debug(f"フレーム輝度: {brightness:.2f}")
                
                # 短い間隔でキャプチャ
                time.sleep(sample_interval)
        
        except Exception as e:
            logger.error(f"輝度測定中にエラーが発生しました: {e}")
        
        # 測定結果の処理
        if not brightness_readings:
            logger.error("有効な輝度データを取得できませんでした。")
            return None
        
        # 平均輝度を計算
        avg_brightness = float(np.mean(brightness_readings))
        logger.info(f"測定結果: 平均輝度 = {avg_brightness:.2f} (サンプル数: {len(brightness_readings)})")
        
        return avg_brightness


def measure_ambient_brightness(capture_duration: float = 1.0) -> Optional[float]:
    """
    Webカメラを使用して周囲の平均輝度を測定する便利な関数
    
    Args:
        capture_duration (float): 測定時間（秒）
        
    Returns:
        Optional[float]: 平均輝度（0-255の範囲）、またはエラー時にNone
    """
    with AmbientLightSensor() as sensor:
        return sensor.measure_ambient_light(duration=capture_duration)
