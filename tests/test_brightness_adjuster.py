"""
BrightnessAdjusterモジュールのテスト
"""
import unittest
from unittest.mock import patch, MagicMock
from src.config import BrightnessConfig
from src.brightness_adjuster import BrightnessAdjuster

class TestBrightnessAdjuster(unittest.TestCase):
    """BrightnessAdjusterクラスのテスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        # テスト用の設定
        self.test_config = BrightnessConfig(
            min_brightness=30,
            max_brightness=70,
            capture_duration=0.5
        )
        
        # テスト対象のインスタンス
        self.adjuster = BrightnessAdjuster(self.test_config)
    
    def test_map_brightness_linear_mapping(self):
        """輝度の線形マッピングが正しく行われるかテスト"""
        # 様々な入力値でマッピングをテスト
        test_cases = [
            (0, 30),     # 最小値（暗い環境）
            (127.5, 50), # 中間値
            (255, 70)    # 最大値（明るい環境）
        ]
        
        for input_brightness, expected_output in test_cases:
            mapped_brightness = self.adjuster.map_brightness(input_brightness)
            self.assertAlmostEqual(
                mapped_brightness, 
                expected_output, 
                places=1,
                msg=f"入力値 {input_brightness} の期待出力は {expected_output} ですが、" 
                    f"実際は {mapped_brightness} でした"
            )
    
    def test_map_brightness_same_min_max(self):
        """最小値と最大値が同じ場合のマッピングをテスト"""
        # 最小値と最大値が同じ設定
        config = BrightnessConfig(min_brightness=50, max_brightness=50)
        adjuster = BrightnessAdjuster(config)
        
        # 任意の入力値に対して最小/最大値が返されることを確認
        for input_value in [0, 127, 255]:
            self.assertEqual(adjuster.map_brightness(input_value), 50)
    
    def test_map_brightness_handles_out_of_range(self):
        """範囲外の入力値に対してマッピングが正しく処理されるかテスト"""
        # 範囲外の入力値
        out_of_range_values = [-10, 300]
        
        for value in out_of_range_values:
            # マッピングは内部で入力値を使用して計算するが、
            # 結果は必ず設定された最小値と最大値の間になるはず
            result = self.adjuster.map_brightness(value)
            self.assertTrue(
                self.test_config.min_brightness <= result <= self.test_config.max_brightness,
                f"マッピング結果 {result} が範囲外です"
            )
    
    @patch('src.brightness_adjuster.measure_ambient_brightness')
    @patch('src.brightness_adjuster.set_display_brightness')
    def test_adjust_success(self, mock_set_brightness, mock_measure_brightness):
        """輝度調整が成功するケースをテスト"""
        # モックの戻り値を設定
        mock_measure_brightness.return_value = 100.0  # 中間程度の明るさ
        mock_set_brightness.return_value = True       # 輝度設定成功
        
        # 調整を実行
        result = self.adjuster.adjust()
        
        # 検証
        self.assertTrue(result)
        mock_measure_brightness.assert_called_once_with(capture_duration=0.5)
        
        # マッピングされた輝度値（この場合は100.0の入力に対して計算される値）でset_brightness()が呼ばれること
        expected_brightness = self.adjuster.map_brightness(100.0)
        mock_set_brightness.assert_called_once_with(expected_brightness)
    
    @patch('src.brightness_adjuster.measure_ambient_brightness')
    @patch('src.brightness_adjuster.set_display_brightness')
    def test_adjust_measurement_failure(self, mock_set_brightness, mock_measure_brightness):
        """輝度測定が失敗するケースをテスト"""
        # 輝度測定が失敗
        mock_measure_brightness.return_value = None
        
        # 調整を実行
        result = self.adjuster.adjust()
        
        # 検証
        self.assertFalse(result)
        mock_measure_brightness.assert_called_once()
        # 測定に失敗した場合、輝度設定は呼ばれないはず
        mock_set_brightness.assert_not_called()
    
    @patch('src.brightness_adjuster.measure_ambient_brightness')
    @patch('src.brightness_adjuster.set_display_brightness')
    def test_adjust_setting_failure(self, mock_set_brightness, mock_measure_brightness):
        """輝度設定が失敗するケースをテスト"""
        # モックの戻り値を設定
        mock_measure_brightness.return_value = 150.0  # 中間程度の明るさ
        mock_set_brightness.return_value = False      # 輝度設定失敗
        
        # 調整を実行
        result = self.adjuster.adjust()
        
        # 検証
        self.assertFalse(result)
        mock_measure_brightness.assert_called_once()
        mock_set_brightness.assert_called_once()


if __name__ == '__main__':
    unittest.main()
