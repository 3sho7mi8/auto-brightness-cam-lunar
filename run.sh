#!/bin/bash

# スクリプトが存在するディレクトリに移動 (これにより config.json が正しく読み込まれる)
cd "$(dirname "$0")"

# 仮想環境の Python を使ってスクリプトを実行
venv/bin/python adjust_brightness.py