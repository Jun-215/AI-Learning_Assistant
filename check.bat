@echo off
REM 快速测试脚本
echo 🧪 AI Agent 系统快速测试
echo ================================

REM 检查Python环境
echo [1/4] 检查Python环境...
python --version
if errorlevel 1 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查Node.js环境
echo.
echo [2/4] 检查Node.js环境...
node --version
if errorlevel 1 (
    echo ❌ Node.js未安装或不在PATH中
    pause
    exit /b 1
)

REM 检查后端依赖
echo.
echo [3/4] 检查后端依赖...
cd /d "%~dp0backend"
python -c "import flask, dashscope; print('✅ 后端依赖正常')"
if errorlevel 1 (
    echo ❌ 后端依赖缺失，请运行: pip install -r requirements.txt
    pause
    exit /b 1
)

REM 检查前端依赖
echo.
echo [4/4] 检查前端依赖...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo ❌ 前端依赖缺失，请运行: npm install
    pause
    exit /b 1
) else (
    echo ✅ 前端依赖正常
)

echo.
echo ================================
echo ✅ 环境检查完成，系统就绪！
echo.
echo 🚀 启动方式:
echo   1. run.bat          - 开发模式
echo   2. run.bat backend  - 仅后端
echo   3. run.bat frontend - 仅前端
echo   4. run.bat prod     - 生产模式
echo.
pause
