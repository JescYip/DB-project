#!/bin/bash

echo "🚀 启动咖啡订购系统..."
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import flask, flask_cors" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 安装依赖..."
    pip3 install flask flask-cors
fi

# 初始化数据库
echo "🗄️  初始化数据库..."
python3 -c "from database import DatabaseManager; DatabaseManager()"

echo "✅ 系统准备就绪！"
echo ""
echo "🌐 启动Web服务器..."
echo "📱 客户端访问地址: http://localhost:5000"
echo "🔧 管理后台地址: http://localhost:5000/admin"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"

# 启动Flask应用
python3 app.py