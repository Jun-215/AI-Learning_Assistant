@echo off
setlocal enabledelayedexpansion

REM AI Agent 对话系统 - 命令行启动脚本
echo ==========================================
echo   AI Agent 对话系统 - 命令行启动
echo ==========================================
echo.

REM 检查参数
if "%1"=="--help" goto :show_help
if "%1"=="-h" goto :show_help
if "%1"=="help" goto :show_help

REM 设置项目根目录
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

REM 检查必要文件
if not exist "%BACKEND_DIR%\app.py" (
    echo ❌ 错误: 找不到后端文件 app.py
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo ❌ 错误: 找不到前端文件 package.json
    exit /b 1
)

REM 根据参数决定启动方式
if "%1"=="backend" goto :start_backend
if "%1"=="frontend" goto :start_frontend
if "%1"=="dev" goto :start_dev
if "%1"=="prod" goto :start_prod

REM 默认启动方式
echo 🚀 启动模式: 开发模式 (前后端分离)
echo.
goto :start_dev

:start_backend
echo 🔧 启动后端服务...
cd /d "%BACKEND_DIR%"
python app.py
goto :end

:start_frontend
echo 🌐 启动前端服务...
cd /d "%FRONTEND_DIR%"
npm start
goto :end

:start_dev
echo 📡 启动后端服务 (后台运行)...
cd /d "%BACKEND_DIR%"
start /min "AI Agent Backend" cmd /k "python app.py"

echo ⏳ 等待后端启动...
timeout /t 3 /nobreak >nul

echo 🌐 启动前端服务...
cd /d "%FRONTEND_DIR%"
npm start
goto :end

:start_prod
echo 🚀 生产模式启动...
echo 📡 启动后端服务 (后台运行)...
cd /d "%BACKEND_DIR%"
start /min "AI Agent Backend" cmd /k "python app.py"

echo ⏳ 等待后端启动...
timeout /t 5 /nobreak >nul

echo 🌐 启动前端服务 (后台运行)...
cd /d "%FRONTEND_DIR%"
start /min "AI Agent Frontend" cmd /k "npm start"

echo ✅ 服务启动完成！
echo 📱 前端地址: http://localhost:3000
echo 🔧 后端地址: http://localhost:5000
goto :end

:show_help
echo.
echo 用法: run.bat [选项]
echo.
echo 选项:
echo   无参数      - 开发模式启动 (前端在当前窗口，后端在后台)
echo   backend     - 仅启动后端服务
echo   frontend    - 仅启动前端服务
echo   dev         - 开发模式 (前端在当前窗口，后端在后台)
echo   prod        - 生产模式 (前后端都在后台运行)
echo   help, -h    - 显示此帮助信息
echo.
echo 示例:
echo   run.bat              启动开发环境
echo   run.bat backend      仅启动后端
echo   run.bat frontend     仅启动前端
echo   run.bat prod         生产模式启动
echo.
goto :end

:end
echo.
echo ==========================================
