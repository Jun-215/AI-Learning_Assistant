@echo off
echo ==========================================
echo     AI Agent 对话系统 - 快速启动脚本
echo ==========================================
echo.

echo [1/3] 启动后端服务...
cd /d "%~dp0backend"
start "AI Agent Backend" cmd /k "python app.py"

echo [2/3] 等待后端启动...
timeout /t 3 /nobreak >nul

echo [3/3] 启动前端服务...
cd /d "%~dp0frontend"
start "AI Agent Frontend" cmd /k "npm start"

echo.
echo ==========================================
echo 系统启动完成！
echo 后端服务: http://localhost:5000
echo 前端界面: http://localhost:3000
echo.
echo 请在 backend\.env 文件中配置您的阿里千问API密钥
echo ==========================================
pause
