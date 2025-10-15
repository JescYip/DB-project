#!/bin/bash

echo "启动基于 JessDB 的咖啡店管理系统..."
echo "数据库文件: jessdb.db"
echo "端口: 5000"
echo "访问地址: http://localhost:5000"
echo ""

# 检查 Python 依赖
if ! python3 -c "import flask" 2>/dev/null; then
    echo "安装 Flask 依赖..."
    pip3 install flask flask-cors
fi

# 启动应用
python3 app_jessdb.py