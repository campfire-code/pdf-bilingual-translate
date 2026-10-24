@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
rem ===== 篝火填写：每个工具不同 =====
set "TOOL_NAME=PDF 双语翻译（保版式）"
set "PY_VERSION=3.12"
set "INSTALL_CMD=uv pip install ."
set "RUN_CMD=pdf2zh -i"
set "OPEN_URL="
rem ===================================
title %TOOL_NAME%
echo.
echo   %TOOL_NAME%  ·  篝火出品
echo   第一次运行会自动下载 Python 和依赖，需要几分钟，请保持联网。
echo   第一次翻译时还会下载版面识别模型，请耐心等待。
echo.
where uv >nul 2>nul || (
  echo 正在安装 uv（Python 环境管理工具）...
  powershell -NoProfile -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex" || goto :fail
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
if exist ".venv\campfire-ready" goto :ready
set "USE_MIRROR="
set /p USE_MIRROR=使用国内镜像加速下载依赖吗？直接回车表示使用 [Y/n]：
if /i not "%USE_MIRROR%"=="n" set "UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple"
uv venv --python %PY_VERSION% .venv || goto :fail
call .venv\Scripts\activate.bat
%INSTALL_CMD% || goto :fail
echo ok> ".venv\campfire-ready"
goto :start
:ready
call .venv\Scripts\activate.bat
:start
if not "%OPEN_URL%"=="" start "" cmd /c "timeout /t 6 >nul & start %OPEN_URL%"
echo 正在启动，浏览器会自动打开中文网页界面（没打开请访问 http://localhost:7860/），关闭这个窗口即可退出。
%RUN_CMD%
goto :eof
:fail
echo.
echo 启动失败：请截图这个窗口，到 GitHub 仓库的 Issues 反馈。
pause
