@echo off
chcp 936 >nul
title DIAGNOSEX - 中药企业财务健康度诊断
cd /d "%~dp0"

echo ============================================================
echo   DIAGNOSEX  中药企业财务健康度诊断
echo ============================================================
echo.

if not exist "DIAGNOSEX.py" (
    echo [错误] 当前目录找不到 DIAGNOSEX.py
    echo        请把本文件与 DIAGNOSEX.py、年报数据 CSV 放在同一文件夹。
    echo.
    pause
    exit /b 1
)
if not exist "中药上市公司2023-2025年报财务数据.csv" (
    echo [错误] 当前目录找不到 中药上市公司2023-2025年报财务数据.csv
    echo        请把本文件与 DIAGNOSEX.py、年报数据 CSV 放在同一文件夹。
    echo.
    pause
    exit /b 1
)

rem ---- 1. 检测 Python ----
set "PYEXE="
where python >nul 2>nul && set "PYEXE=python"
if not defined PYEXE (
    where py >nul 2>nul && set "PYEXE=py"
)
if not defined PYEXE (
    echo [错误] 未检测到 Python，请先安装 Python 3.9 及以上版本，并勾选 "Add Python to PATH"。
    echo        下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

rem ---- 2. 创建虚拟环境（仅首次） ----
if not exist ".venv\Scripts\python.exe" (
    echo [1/4] 正在创建虚拟环境 .venv ...
    %PYEXE% -m venv .venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败，请检查 Python 安装。
        pause
        exit /b 1
    )
) else (
    echo [1/4] 已存在虚拟环境 .venv，跳过创建。
)

set "VPY=.venv\Scripts\python.exe"

rem ---- 3. 安装依赖（仅首次） ----
if not exist ".venv\.deps_ok" (
    echo [2/4] 正在安装依赖 streamlit / pandas / plotly（首次较慢，约 2-5 分钟）...
    "%VPY%" -m pip install -q --upgrade pip
    "%VPY%" -m pip install -q -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请检查网络连接后重试。
        pause
        exit /b 1
    )
    echo ok> ".venv\.deps_ok"
) else (
    echo [2/4] 依赖已安装，跳过。
)

rem ---- 4. 释放端口 8502 ----
set "PORT=8502"
echo [3/4] 检查端口 %PORT% ...
netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
if not errorlevel 1 (
    echo       端口 %PORT% 被占用，正在释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
        taskkill /F /PID %%a >nul 2>nul
    )
    timeout /t 2 /nobreak >nul
)

rem ---- 5. 启动 ----
echo [4/4] 正在启动，稍等 3 秒后自动打开浏览器。
echo       地址：http://localhost:%PORT%
echo       （关闭此窗口即可停止服务）
echo.
start "" http://localhost:%PORT%
timeout /t 3 /nobreak >nul
"%VPY%" -m streamlit run DIAGNOSEX.py --server.headless true --server.port %PORT% --theme.base light --browser.gatherUsageStats false

echo.
echo 服务已停止。
pause
