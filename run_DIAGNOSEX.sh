#!/usr/bin/env bash
# DIAGNOSEX · 中药企业财务健康度诊断 —— macOS / Linux 一键启动脚本
set -e

cd "$(dirname "$0")"

echo "============================================================"
echo "  DIAGNOSEX  中药企业财务健康度诊断"
echo "============================================================"
echo

if [ ! -f "DIAGNOSEX.py" ]; then
    echo "[错误] 当前目录找不到 DIAGNOSEX.py"
    echo "       请将本脚本与 DIAGNOSEX.py、申报数据 CSV 放在同一文件夹。"
    exit 1
fi
if [ ! -f "中药上市公司2023-2025年报财务数据.csv" ]; then
    echo "[错误] 当前目录找不到 中药上市公司2023-2025年报财务数据.csv"
    echo "       请将本脚本与 DIAGNOSEX.py、申报数据 CSV 放在同一文件夹。"
    exit 1
fi

# ---- 1. 检测 Python ----
PYEXE=""
if command -v python3 >/dev/null 2>&1; then
    PYEXE="python3"
elif command -v python >/dev/null 2>&1 && python -c 'import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)'; then
    PYEXE="python"
fi
if [ -z "$PYEXE" ]; then
    echo "[错误] 未检测到 Python 3.9+。请先安装 Python："
    echo "       macOS：brew install python  或到 https://www.python.org/downloads/"
    echo "       Linux：sudo apt install python3 python3-venv python3-pip"
    exit 1
fi

# ---- 2. 创建虚拟环境（仅首次） ----
if [ ! -f ".venv/bin/python" ]; then
    echo "[1/4] 正在创建虚拟环境 .venv ..."
    "$PYEXE" -m venv .venv
else
    echo "[1/4] 已存在虚拟环境 .venv，跳过创建"
fi
VPY=".venv/bin/python"

# ---- 3. 安装依赖（仅首次） ----
if [ ! -f ".venv/.deps_ok" ]; then
    echo "[2/4] 正在安装依赖 streamlit / pandas / plotly（首次运行约 2-5 分钟）..."
    "$VPY" -m pip install -q --upgrade pip
    "$VPY" -m pip install -q -r requirements.txt
    echo ok > ".venv/.deps_ok"
else
    echo "[2/4] 依赖已安装，跳过"
fi

# ---- 4. 释放端口 8502 ----
PORT=8502
echo "[3/4] 检查端口 $PORT ..."
PIDS=$(lsof -ti tcp:"$PORT" 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    echo "      端口 $PORT 被占用，正在释放..."
    echo "$PIDS" | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# ---- 5. 启动 ----
echo "[4/4] 启动服务，稍候 3 秒会自动打开浏览器"
echo "      地址：http://localhost:$PORT"
echo "      关闭本窗口（或按 Ctrl+C）即停止服务"
echo
( sleep 3; open "http://localhost:$PORT" 2>/dev/null || xdg-open "http://localhost:$PORT" 2>/dev/null || true ) &
"$VPY" -m streamlit run DIAGNOSEX.py --server.headless true --server.port "$PORT" --theme.base light --browser.gatherUsageStats false

echo
echo "服务已停止。"
