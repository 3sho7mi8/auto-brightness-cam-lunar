# Lunar Brightness Adjuster

自動的にWebカメラから周囲の明るさを検出し、[Lunar CLI](https://lunar.fyi/#cli)を使用して外部ディスプレイの輝度を調整するPythonアプリケーションです。

## 特徴

* Webカメラを使用して周囲の明るさ（平均輝度）を測定
* 測定された輝度に基づいて、設定された最小・最大範囲内でディスプレイの輝度を自動調整
* 設定ファイル（`config.json`）で輝度調整範囲やキャプチャ時間をカスタマイズ可能
* ログ出力機能（デバッグモード対応）

## 必要条件

* Python 3.6 以上
* OpenCV (`opencv-python`)
* NumPy (`numpy`)
* [Lunar CLI](https://lunar.fyi/#cli) がインストールされ、システムのPATHに設定されていること
* macOS（カメラへのアクセス許可が必要）

## セットアップ

1. **リポジトリのクローンまたはダウンロード**:
   ```bash
   # 必要に応じてリポジトリをクローン
   # git clone <リポジトリURL>
   # cd lunar-support
   ```

2. **仮想環境の作成**:
   ```bash
   python3 -m venv venv
   ```

3. **依存パッケージのインストール**:
   ```bash
   venv/bin/pip install opencv-python numpy
   ```

4. **カメラへのアクセス許可**:
   * macOSの「システム設定」→「プライバシーとセキュリティ」→「カメラ」へ移動
   * スクリプトの実行に使用するアプリケーション（例：ターミナル、VS Code）にカメラへのアクセスを許可

## 設定

1. プロジェクトのルートに`config.json`ファイルを作成（既に存在しない場合）
2. 以下の形式で最小輝度（`min_brightness`）、最大輝度（`max_brightness`）、キャプチャ時間（`capture_duration`）を設定:

   ```json
   {
     "min_brightness": 35,
     "max_brightness": 80,
     "capture_duration": 1.0
   }
   ```
   
   設定項目:
   * `min_brightness`: 周囲が最も暗い時のディスプレイ輝度（0-100）
   * `max_brightness`: 周囲が最も明るい時のディスプレイ輝度（0-100）
   * `capture_duration`: カメラが周囲の明るさを測定する時間（秒）

## 使い方

1. **実行スクリプトに実行権限を付与**（初回のみ必要）:
   ```bash
   chmod +x run.sh
   ```

2. **スクリプトの実行**:
   ```bash
   ./run.sh
   ```
   
   オプション:
   * デバッグモード（詳細なログ出力）を有効にする:
     ```bash
     ./run.sh --debug
     ```
   * 別の設定ファイルを指定する:
     ```bash
     ./run.sh --config /path/to/custom_config.json
     ```

   スクリプトは自動的に仮想環境のPythonインタープリタを使用して`adjust_brightness`を実行します。

## 開発者向け情報

### プロジェクト構造

```
lunar-support/
├── adjust_brightness     # メインスクリプト（実行可能）
├── config.json           # 設定ファイル
├── logs/                 # ログ出力ディレクトリ
├── run.sh                # 実行スクリプト
├── src/                  # ソースコードパッケージ
│   ├── __init__.py
│   ├── brightness_adjuster.py  # メインロジック
│   ├── camera.py         # カメラ/輝度測定機能
│   ├── config.py         # 設定管理
│   └── lunar.py          # Lunar CLI操作
└── tests/                # テストパッケージ
    ├── __init__.py
    ├── test_brightness_adjuster.py
    ├── test_camera.py
    ├── test_config.py
    └── test_lunar.py
```

### テストの実行

単体テストを実行するには:

```bash
venv/bin/python -m unittest discover -s tests
```

特定のテストファイルを実行するには:

```bash
venv/bin/python -m unittest tests/test_config.py
```

## ログ

アプリケーションのログは`logs/lunar_brightness.log`に保存されます。デバッグモードを有効にすると、より詳細な情報が記録されます。

## ライセンス

このプロジェクトはオープンソースで提供されています。
