"""
設定モジュールのテスト
"""
import os
import json
import tempfile
import unittest
from src.config import BrightnessConfig, load_config

class TestBrightnessConfig(unittest.TestCase):
    """BrightnessConfigクラスのテスト"""
    
    def test_default_values(self):
        """デフォルト値が正しく設定されるかテスト"""
        config = BrightnessConfig()
        self.assertEqual(config.min_brightness, 35)
        self.assertEqual(config.max_brightness, 80)
        self.assertEqual(config.capture_duration, 1)
    
    def test_validation_clamps_values(self):
        """値が範囲内にクランプされるかテスト"""
        # 範囲外の値で初期化
        config = BrightnessConfig(min_brightness=-10, max_brightness=150)
        
        # 検証実行
        config.validate()
        
        # 値がクランプされていることを確認
        self.assertEqual(config.min_brightness, 0)
        self.assertEqual(config.max_brightness, 100)
    
    def test_validation_swaps_min_max_if_needed(self):
        """min > maxの場合、値が交換されるかテスト"""
        # min > maxで初期化
        config = BrightnessConfig(min_brightness=80, max_brightness=30)
        
        # 検証実行
        config.validate()
        
        # 値が交換されていることを確認
        self.assertEqual(config.min_brightness, 30)
        self.assertEqual(config.max_brightness, 80)
    
    def test_validation_ensures_minimum_capture_duration(self):
        """キャプチャ時間が最小値以上になるかテスト"""
        # 短すぎるキャプチャ時間で初期化
        config = BrightnessConfig(capture_duration=0.01)
        
        # 検証実行
        config.validate()
        
        # 最小値に調整されていることを確認
        self.assertEqual(config.capture_duration, 0.1)


class TestLoadConfig(unittest.TestCase):
    """load_config関数のテスト"""
    
    def test_load_config_with_valid_file(self):
        """有効な設定ファイルから正しく読み込めるかテスト"""
        # テスト用の一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            json.dump({
                "min_brightness": 40,
                "max_brightness": 70,
                "capture_duration": 2.5
            }, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # テスト用設定ファイルを読み込む
            config = load_config(temp_file_path)
            
            # 値が正しく読み込まれていることを確認
            self.assertEqual(config.min_brightness, 40)
            self.assertEqual(config.max_brightness, 70)
            self.assertEqual(config.capture_duration, 2.5)
            
        finally:
            # テスト用ファイルを削除
            os.unlink(temp_file_path)
    
    def test_load_config_with_invalid_json(self):
        """不正なJSONファイルの場合にデフォルト値が使用されるかテスト"""
        # 不正なJSON形式のテスト用一時ファイルを作成
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("{invalid json")
            temp_file_path = temp_file.name
        
        try:
            # 不正な形式の設定ファイルを読み込む
            config = load_config(temp_file_path)
            
            # デフォルト値が使用されていることを確認
            self.assertEqual(config.min_brightness, 35)
            self.assertEqual(config.max_brightness, 80)
            self.assertEqual(config.capture_duration, 1)
            
        finally:
            # テスト用ファイルを削除
            os.unlink(temp_file_path)
    
    def test_load_config_with_nonexistent_file(self):
        """存在しないファイルの場合にデフォルト値が使用されるかテスト"""
        # 存在しないファイルパスを指定
        nonexistent_file = "/path/to/nonexistent/config.json"
        
        # 存在しない設定ファイルを読み込む
        config = load_config(nonexistent_file)
        
        # デフォルト値が使用されていることを確認
        self.assertEqual(config.min_brightness, 35)
        self.assertEqual(config.max_brightness, 80)
        self.assertEqual(config.capture_duration, 1)


if __name__ == '__main__':
    unittest.main()
