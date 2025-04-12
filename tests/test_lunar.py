"""
Lunar CLI 制御モジュールのテスト
"""
import unittest
from unittest.mock import patch, MagicMock
from src.lunar import LunarController, set_display_brightness

class TestLunarController(unittest.TestCase):
    """LunarControllerクラスのテスト"""
    
    def setUp(self):
        """各テスト前の準備"""
        self.controller = LunarController()
    
    @patch('subprocess.run')
    def test_set_brightness_success(self, mock_run):
        """輝度設定が成功するケースをテスト"""
        # 成功するサブプロセス実行のモック
        mock_result = MagicMock()
        mock_result.stdout = "Brightness set to 65%\n"
        mock_run.return_value = mock_result
        
        # 輝度設定を実行
        result = self.controller.set_brightness(65.4)
        
        # 検証
        self.assertTrue(result)
        mock_run.assert_called_once_with(
            ['lunar', 'set', 'brightness', '65'],
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_set_brightness_clamps_values(self, mock_run):
        """輝度値が範囲内にクランプされるかテスト"""
        # 成功するサブプロセス実行のモック
        mock_result = MagicMock()
        mock_result.stdout = "Brightness set\n"
        mock_run.return_value = mock_result
        
        # 範囲外の値で輝度設定を実行
        self.controller.set_brightness(-10)  # 下限値テスト
        mock_run.assert_called_with(
            ['lunar', 'set', 'brightness', '0'],  # 0%にクランプされるはず
            check=True,
            capture_output=True,
            text=True
        )
        
        self.controller.set_brightness(120)  # 上限値テスト
        mock_run.assert_called_with(
            ['lunar', 'set', 'brightness', '100'],  # 100%にクランプされるはず
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_set_brightness_command_not_found(self, mock_run):
        """lunarコマンドが見つからないケースをテスト"""
        # FileNotFoundエラーを発生させる
        mock_run.side_effect = FileNotFoundError()
        
        # 輝度設定を実行
        result = self.controller.set_brightness(50)
        
        # 検証
        self.assertFalse(result)
        mock_run.assert_called_once_with(
            ['lunar', 'set', 'brightness', '50'],
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_set_brightness_command_failure(self, mock_run):
        """lunarコマンドが失敗するケースをテスト"""
        # CalledProcessErrorを発生させる
        import subprocess
        mock_error = subprocess.CalledProcessError(
            returncode=1,
            cmd=['lunar', 'set', 'brightness', '50'],
            stderr="Failed to set brightness"
        )
        mock_run.side_effect = mock_error
        
        # 輝度設定を実行
        result = self.controller.set_brightness(50)
        
        # 検証
        self.assertFalse(result)
        mock_run.assert_called_once_with(
            ['lunar', 'set', 'brightness', '50'],
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_get_current_brightness_success(self, mock_run):
        """現在の輝度取得が成功するケースをテスト"""
        # 成功するサブプロセス実行のモック
        mock_result = MagicMock()
        mock_result.stdout = "75%\n"
        mock_run.return_value = mock_result
        
        # 現在の輝度を取得
        brightness = self.controller.get_current_brightness()
        
        # 検証
        self.assertEqual(brightness, 75.0)
        mock_run.assert_called_once_with(
            ['lunar', 'get', 'brightness'],
            check=True,
            capture_output=True,
            text=True
        )
    
    @patch('subprocess.run')
    def test_get_current_brightness_parse_failure(self, mock_run):
        """輝度値の解析に失敗するケースをテスト"""
        # 不正な出力を返すモック
        mock_result = MagicMock()
        mock_result.stdout = "Invalid output"
        mock_run.return_value = mock_result
        
        # 現在の輝度を取得
        brightness = self.controller.get_current_brightness()
        
        # 検証
        self.assertIsNone(brightness)
        mock_run.assert_called_once()


@patch('src.lunar.LunarController')
def test_set_display_brightness(mock_controller_class):
    """set_display_brightness関数が正しく動作するかテスト"""
    # モック設定
    mock_instance = MagicMock()
    mock_instance.set_brightness.return_value = True
    mock_controller_class.return_value = mock_instance
    
    # 関数を呼び出し
    result = set_display_brightness(75.5)
    
    # 検証
    self.assertTrue(result)
    mock_instance.set_brightness.assert_called_once_with(75.5)


if __name__ == '__main__':
    unittest.main()
