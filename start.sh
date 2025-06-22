#!/bin/bash

# 自动化脚本：一键在 Codespaces 或本地启动 Python 3.11 机器人

# 1. 安装依赖
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  echo "未找到 requirements.txt，请先创建依赖文件！"
  exit 1
fi

# 2. 检查 config.py
if ! grep -q "BOT_TOKEN = " config.py; then
  echo "请先填写 config.py 文件中的 BOT_TOKEN、GROUP_ID 等信息！"
  exit 1
fi

# 3. 启动机器人
echo "正在启动机器人（main.py）..."
python main.py
