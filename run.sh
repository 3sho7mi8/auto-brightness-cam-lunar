#!/bin/bash

# スクリプトが存在するディレクトリに移動
cd "$(dirname "$0")"

# adjust_brightnessスクリプトに実行権限を付与（初回のみ必要）
if [ ! -x ./adjust_brightness ]; then
    chmod +x ./adjust_brightness
fi

# 仮想環境の Python を使ってスクリプトを実行
# 引数をそのまま渡す
./venv/bin/python ./adjust_brightness "$@"
