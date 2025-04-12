"""
カメラモジュールのテスト
"""
import unittest
from unittest.mock import patch, MagicMock, call
import numpy as np
import cv2
from src.camera import AmbientLightSensor, measure_ambient_brightness

class TestAmbientLightSensor(unittest.TestCase):
    """AmbientLightSensorクラスのテスト"""
    
    @patch('cv2.VideoCapture')
    def test_open_success(self, mock_video_capture):
        """カメラが正常に開かれるケースをテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera
        
        # センサーのインスタンス化とメソッド呼び出し
        sensor = AmbientLightSensor(camera_index=0)
        result = sensor.open()
        
        # 検証
        self.assertTrue(result)
        mock_video_capture.assert_called_once_with(0)
        mock_camera.isOpened.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_open_failure(self, mock_video_capture):
        """カメラを開けないケースをテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = False
        mock_video_capture.return_value = mock_camera
        
        # センサーのインスタンス化とメソッド呼び出し
        sensor = AmbientLightSensor(camera_index=1)
        result = sensor.open()
        
        # 検証
        self.assertFalse(result)
        mock_video_capture.assert_called_once_with(1)
        mock_camera.isOpened.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_close(self, mock_video_capture):
        """カメラが正しく閉じられるかテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera
        
        # センサーを開いて閉じる
        sensor = AmbientLightSensor()
        sensor.open()
        sensor.close()
        
        # カメラリソースが解放されたことを確認
        mock_camera.release.assert_called_once()
        self.assertIsNone(sensor.camera)
    
    @patch('cv2.VideoCapture')
    def test_context_manager(self, mock_video_capture):
        """コンテキストマネージャーとして正しく動作するかテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_video_capture.return_value = mock_camera
        
        # コンテキストマネージャーとして使用
        with AmbientLightSensor() as sensor:
            self.assertIsNotNone(sensor.camera)
        
        # 終了時にカメラリソースが解放されたことを確認
        mock_camera.release.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_capture_frame_success(self, mock_video_capture):
        """フレームキャプチャが成功するケースをテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_camera.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_camera
        
        # センサーでフレームをキャプチャ
        sensor = AmbientLightSensor()
        sensor.open()
        frame = sensor.capture_frame()
        
        # 検証
        self.assertIsNotNone(frame)
        mock_camera.read.assert_called_once()
    
    @patch('cv2.VideoCapture')
    def test_capture_frame_failure(self, mock_video_capture):
        """フレームキャプチャが失敗するケースをテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_camera.read.return_value = (False, None)
        mock_video_capture.return_value = mock_camera
        
        # センサーでフレームをキャプチャ
        sensor = AmbientLightSensor()
        sensor.open()
        frame = sensor.capture_frame()
        
        # 検証
        self.assertIsNone(frame)
        mock_camera.read.assert_called_once()
    
    @patch('cv2.VideoCapture')
    @patch('cv2.cvtColor')
    def test_get_frame_brightness(self, mock_cvtcolor, mock_video_capture):
        """フレームの明るさ計算が正しく行われるかテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        
        # グレースケール変換のモック
        gray_frame = np.full((100, 100), 128, dtype=np.uint8)  # 平均値=128のグレースケール画像
        mock_cvtcolor.return_value = gray_frame
        
        # テスト用のフレーム
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # センサーの明るさ計算
        sensor = AmbientLightSensor()
        brightness = sensor.get_frame_brightness(test_frame)
        
        # 検証
        self.assertEqual(brightness, 128.0)
        mock_cvtcolor.assert_called_once_with(test_frame, cv2.COLOR_BGR2GRAY)
    
    @patch('cv2.VideoCapture')
    @patch('time.sleep')
    def test_measure_ambient_light(self, mock_sleep, mock_video_capture):
        """周囲の輝度測定が正しく行われるかテスト"""
        # モックの設定
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        
        # 3つのフレームを読み取り、それぞれの平均輝度が異なる場合
        frames = [
            np.full((100, 100, 3), 100, dtype=np.uint8),  # 輝度=100
            np.full((100, 100, 3), 150, dtype=np.uint8),  # 輝度=150
            np.full((100, 100, 3), 200, dtype=np.uint8)   # 輝度=200
        ]
        
        # read()が呼ばれるたびに異なるフレームを返すようにする
        mock_camera.read.side_effect = [(True, frames[0]), (True, frames[1]), (True, frames[2])]
        mock_video_capture.return_value = mock_camera
        
        # パッチを当てて輝度計算をモックする
        with patch.object(AmbientLightSensor, 'get_frame_brightness') as mock_get_brightness:
            mock_get_brightness.side_effect = [100.0, 150.0, 200.0]
            
            # タイミング制御用のモック
            with patch('time.time') as mock_time:
                # 0秒, 0.2秒, 0.4秒, 0.6秒のタイムスタンプをシミュレート
                mock_time.side_effect = [0, 0.2, 0.4, 0.6]
                
                # センサーで周囲の輝度を測定（0.5秒間）
                sensor = AmbientLightSensor()
                sensor.open()
                brightness = sensor.measure_ambient_light(duration=0.5, sample_interval=0.1)
                
                # 検証（(100 + 150 + 200) / 3 = 150）
                self.assertEqual(brightness, 150.0)
                
                # 3つのフレームがキャプチャされるはず
                self.assertEqual(mock_camera.read.call_count, 3)
                self.assertEqual(mock_get_brightness.call_count, 3)
                
                # sample_intervalごとにsleepするはず
                mock_sleep.assert_has_calls([call(0.1), call(0.1), call(0.1)])


@patch('src.camera.AmbientLightSensor')
def test_measure_ambient_brightness(mock_sensor_class):
    """measure_ambient_brightness関数が正しく動作するかテスト"""
    # モック設定
    mock_sensor_instance = MagicMock()
    mock_sensor_instance.measure_ambient_light.return_value = 175.5
    mock_sensor_class.return_value.__enter__.return_value = mock_sensor_instance
    
    # 関数を呼び出し
    result = measure_ambient_brightness(capture_duration=2.0)
    
    # 検証
    self.assertEqual(result, 175.5)
    mock_sensor_instance.measure_ambient_light.assert_called_once_with(duration=2.0)


if __name__ == '__main__':
    unittest.main()
