"""
アプリケーション全体で使用されるロギング機能を提供するモジュール
"""
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# ログ出力先ディレクトリ
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'lunar_brightness.log')

# ログレベルのマッピング
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def setup_logger(name='lunar_brightness', level='INFO'):
    """
    ロガーをセットアップし、ファイルとコンソールに出力するよう設定
    
    Args:
        name (str): ロガーの名前
        level (str): ロギングレベル ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        
    Returns:
        logging.Logger: 設定されたロガーインスタンス
    """
    # ロガーの作成
    logger = logging.getLogger(name)
    
    # すでにハンドラーが設定されている場合は何もしない
    if logger.handlers:
        return logger
        
    # ログレベルの設定
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # ログディレクトリの作成（存在しない場合）
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # ファイル出力用ハンドラー（ローテーション付き）
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=1024 * 1024,  # 1MB
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # コンソール出力用ハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # フォーマッターの作成
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ハンドラーにフォーマッターを設定
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # ロガーにハンドラーを追加
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# デフォルトロガーを作成
logger = setup_logger()
